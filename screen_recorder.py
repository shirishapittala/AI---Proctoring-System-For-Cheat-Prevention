import cv2
import numpy as np
import mss
import threading
import time
import os

recording = False

def start_screen_recording():
    global recording
    recording = True

    os.makedirs("recordings", exist_ok=True)

    file_name = f"recordings/screen_record_{int(time.time())}.avi"

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        width = monitor["width"]
        height = monitor["height"]

        writer = cv2.VideoWriter(
            file_name,
            cv2.VideoWriter_fourcc(*"XVID"),
            10,
            (width, height)
        )

        while recording:
            img = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            writer.write(frame)

        writer.release()

def run_screen_recorder():
    thread = threading.Thread(target=start_screen_recording, daemon=True)
    thread.start()

def stop_screen_recording():
    global recording
    recording = False