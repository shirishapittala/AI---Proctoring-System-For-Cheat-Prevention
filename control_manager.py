import json
import os

CONTROL_FILE = "control.json"

def init_control():
    if not os.path.exists(CONTROL_FILE):
        set_exam_status("STOPPED")

def set_exam_status(status):
    with open(CONTROL_FILE, "w") as file:
        json.dump({"exam_status": status}, file)

def get_exam_status():
    init_control()

    with open(CONTROL_FILE, "r") as file:
        data = json.load(file)

    return data.get("exam_status", "STOPPED")