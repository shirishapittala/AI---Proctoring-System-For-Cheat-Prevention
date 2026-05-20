import cv2
import os
import numpy as np
from attendence import mark_attendance
from config import SESSION_FILE
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
if face_cascade.empty():
    print("Error loading Haar cascade file")
recognizer = cv2.face.LBPHFaceRecognizer_create()
FACE_DIR = "faces"
MODEL_FILE = "face_model.yml"
LABEL_FILE = "labels.txt"
MATCH_THRESHOLD = 35

from control_manager import set_exam_status
import subprocess

def open_exam():
    set_exam_status("STARTED")
    print("Exam started...")

    subprocess.run(["python", "main_gui.py"])

def train_model():
    faces_data = []
    labels = []
    label_map = {}
    current_label = 0

    for name in os.listdir(FACE_DIR):
        user_dir = os.path.join(FACE_DIR, name)

        if not os.path.isdir(user_dir):
            continue

        label_map[current_label] = name

        for img_name in os.listdir(user_dir):
            img_path = os.path.join(user_dir, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            if img is not None:
                img = cv2.resize(img, (200, 200))
                faces_data.append(img)
                labels.append(current_label)

        current_label += 1

    if len(faces_data) == 0:
        print("No face data found")
        return

    recognizer.train(faces_data, np.array(labels))
    recognizer.save(MODEL_FILE)

    with open(LABEL_FILE, "w") as file:
        for label, name in label_map.items():
            file.write(f"{label},{name}\n")


def register_face():
    name = input("Enter student name: ")

    user_dir = os.path.join(FACE_DIR, name)
    os.makedirs(user_dir, exist_ok=True)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    count = 0

    print("Capturing 30 face samples...")

    while count < 30:
        ret, frame = cap.read()

        if not ret:
            print("Camera error")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (200, 200))

            count += 1
            cv2.imwrite(os.path.join(user_dir, f"{count}.jpg"), face_img)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"Samples: {count}/30", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Register Face", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    train_model()
    print("Face registered and trained successfully")


def load_labels():
    labels = {}

    if not os.path.exists(LABEL_FILE):
        return labels

    with open(LABEL_FILE, "r") as file:
        for line in file:
            label, name = line.strip().split(",")
            labels[int(label)] = name

    return labels


def login_face():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

    if not os.path.exists(MODEL_FILE):
        print("No trained model found. Register first.")
        return

    recognizer.read(MODEL_FILE)
    labels = load_labels()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    print("Face Login Started...")

    success_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Camera error")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        status_text = "Show registered face"

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (200, 200))

            label, confidence = recognizer.predict(face_img)

            if confidence < MATCH_THRESHOLD:
                success_count += 1
                status_text = f"Matching... {success_count}/5"

                if success_count >= 5:
                    name = labels.get(label, "Student")
                    print(f"Login success: {name}")

                    with open(SESSION_FILE, "w") as file:
                        file.write(name)

                    mark_attendance(name)

                    cap.release()
                    cv2.destroyAllWindows()

                    open_exam()
                    return

            else:
                success_count = 0
                status_text = "Face not matched"

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, f"Confidence: {int(confidence)}", (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.putText(frame, status_text, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.imshow("Face Login", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


while True:
    print("\n===== AI Iris Proctoring Login =====")
    print("1. Register Face")
    print("2. Login with Face")
    print("3. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        register_face()

    elif choice == "2":
        login_face()
        break

    elif choice == "3":
        break



