import csv
import time
import os

FILE = "attendance.csv"

def mark_attendance(name):
    exists = os.path.exists(FILE)

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not exists:
            writer.writerow(["Name", "Time", "Status"])

        writer.writerow([name, time.strftime("%H:%M:%S"), "Present"])