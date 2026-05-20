print("MAIN GUI STARTED")

import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os

from config import EYE_MISSING_LIMIT, FACE_MISSING_LIMIT, SESSION_FILE
from face_eye_detector import count_faces, detect_eye_status, detect_head_position
from audio_detector import detect_audio
from logger import create_log_file, save_log
from mouth_detector import detect_mouth_movement
from control_manager import get_exam_status, set_exam_status

LIVE_IMAGE = "live_student_frame.jpg"

create_log_file()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Camera not detected")
    exit()

print("Camera opened successfully")


def get_student_name():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as file:
            name = file.read().strip()
            if name:
                return name
    return "Unknown Student"


student_name = get_student_name()

eye_missing_count = 0
face_missing_count = 0
frame_count = 0
audio = False
last_alert = ""


def update_frame():
    global eye_missing_count, face_missing_count, frame_count, audio, last_alert

    ret, frame = cap.read()

    if ret:
        frame = cv2.flip(frame, 1)

        exam_status = get_exam_status()

        if exam_status == "STARTED":
            cv2.imwrite(LIVE_IMAGE, frame)

        cv2.putText(frame, f"Student: {student_name}", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        if exam_status == "STOPPED":
            cv2.putText(frame, "WAITING FOR ADMIN TO START EXAM", (30, 250),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)

            root.after(10, update_frame)
            return

        faces = count_faces(frame)
        eye = detect_eye_status(frame)
        head = detect_head_position(frame)

        frame_count += 1
        if frame_count % 15 == 0:
            audio = detect_audio()

        mouth = detect_mouth_movement(audio)

        status = "SAFE"
        message = "All good"

        if faces == 0:
            face_missing_count += 1
        else:
            face_missing_count = 0

        if eye == "NO_EYE":
            eye_missing_count += 1
        else:
            eye_missing_count = 0

        if face_missing_count > FACE_MISSING_LIMIT:
            status = "ALERT"
            message = "No face detected"

        elif faces > 1:
            status = "ALERT"
            message = "Multiple faces detected"

        elif eye_missing_count > EYE_MISSING_LIMIT:
            status = "ALERT"
            message = "Eyes not visible"

        elif head != "CENTER":
            status = "WARNING"
            message = "Head turned"

        elif mouth:
            status = "ALERT"
            message = "Mouth movement / speaking detected"

        if message != last_alert and status != "SAFE":
            save_log(f"{student_name}: {message}")
            last_alert = message

        if status == "SAFE":
            color = (0, 255, 0)
        elif status == "WARNING":
            color = (0, 255, 255)
        else:
            color = (0, 0, 255)

        cv2.putText(frame, f"STATUS: {status}", (30, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)

        cv2.putText(frame, message, (30, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.putText(frame, f"Faces: {faces}", (30, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.putText(frame, f"Eye: {eye}", (30, 210),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.putText(frame, f"Head: {head}", (30, 250),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.putText(frame, f"Audio: {'YES' if audio else 'NO'}", (30, 290),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.putText(frame, f"Mouth: {'MOVING' if mouth else 'NORMAL'}", (30, 330),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    root.after(10, update_frame)


def stop_app():
    print("Stopping GUI")

    set_exam_status("STOPPED")

    cap.release()

    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

    if os.path.exists(LIVE_IMAGE):
        os.remove(LIVE_IMAGE)

    root.destroy()

    print("Exam stopped by student")


root = tk.Tk()
root.title("Student Exam Dashboard")
root.geometry("900x720")
root.configure(bg="#101820")

title = tk.Label(root, text=f"Student Dashboard - {student_name}",
                 font=("Arial", 22, "bold"),
                 fg="white", bg="#101820")
title.pack(pady=10)

video_label = tk.Label(root, bg="black")
video_label.pack()

stop_btn = tk.Button(root,
                     text="Stop Exam",
                     font=("Arial", 15),
                     bg="red",
                     fg="white",
                     command=stop_app)
stop_btn.pack(pady=15)

root.protocol("WM_DELETE_WINDOW", stop_app)

update_frame()
root.mainloop()