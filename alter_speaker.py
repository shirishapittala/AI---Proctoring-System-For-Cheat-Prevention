import pyttsx3
import time

engine = pyttsx3.init()
last_alert_time = 0

def speak_alert(message):
    global last_alert_time

    current_time = time.time()

    if current_time - last_alert_time > 8:
        engine.say(message)
        engine.runAndWait()
        last_alert_time = current_time