import cv2

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)

def count_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)
    return len(faces)

def detect_eye_status(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    if len(faces) == 0:
        return "NO_EYE"

    x, y, w, h = faces[0]
    face_gray = gray[y:y+h, x:x+w]

    eyes = eye_cascade.detectMultiScale(face_gray, 1.1, 5)

    if len(eyes) >= 1:
        return "EYES_ON_SCREEN"
    return "NO_EYE"

def detect_head_position(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5)

    if len(faces) == 0:
        return "NO_FACE"

    x, y, w, h = faces[0]
    center_x = x + w // 2
    frame_center = frame.shape[1] // 2

    if center_x < frame_center - 100:
        return "LEFT"
    elif center_x > frame_center + 100:
        return "RIGHT"
    return "CENTER"