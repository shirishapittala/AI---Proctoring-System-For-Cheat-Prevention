from flask import Flask, redirect, url_for, render_template_string, send_file
from control_manager import set_exam_status, get_exam_status, init_control
import os
import time
import csv

app = Flask(__name__)

SESSION_FILE = "session.txt"
LIVE_IMAGE = "live_student_frame.jpg"
LOG_FILE = "proctor_logs.csv"

HTML = """
<html>
<head>
<title>Admin Dashboard</title>
<meta http-equiv="refresh" content="2">

<style>
body {
    font-family: Arial;
    background:#101820;
    color:white;
    text-align:center;
    padding:30px;
}
button {
    padding:15px 35px;
    font-size:20px;
    margin:15px;
    border:none;
    border-radius:10px;
    color:white;
}
.start { background:green; }
.stop { background:red; }
.card {
    background:#1f2d3d;
    padding:20px;
    border-radius:15px;
    margin:15px;
    display:inline-block;
    min-width:180px;
}
img {
    width:800px;
    border:5px solid #00a86b;
    border-radius:10px;
}
table {
    width:90%;
    margin:auto;
    border-collapse:collapse;
    background:white;
    color:black;
}
th, td {
    border:1px solid #333;
    padding:10px;
}
th {
    background:#00a86b;
    color:white;
}
</style>
</head>

<body>

<h1>Admin Exam Control Dashboard</h1>

<div>
    <div class="card">
        <h2>Status</h2>
        <p>{{ status }}</p>
    </div>

    <div class="card">
        <h2>Student</h2>
        <p>{{ student }}</p>
    </div>

    <div class="card">
        <h2>Total Alerts</h2>
        <p>{{ total }}</p>
    </div>

    <div class="card">
        <h2>Cheating Score</h2>
        <p>{{ score }}%</p>
    </div>
</div>

<a href="/start"><button class="start">Start Exam</button></a>
<a href="/stop"><button class="stop">Stop Exam</button></a>

<h2>Live Student Exam View</h2>

{% if live %}
    <img src="/live?time={{ timestamp }}">
{% else %}
    <h3>No live frame available / Student stopped exam</h3>
{% endif %}

<h2>Alert Logs</h2>

<table>
<tr>
    <th>Time</th>
    <th>Alert</th>
</tr>

{% for row in rows %}
<tr>
    <td>{{ row[0] }}</td>
    <td>{{ row[1] }}</td>
</tr>
{% endfor %}
</table>

</body>
</html>
"""


def get_student_name():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as file:
            name = file.read().strip()
            if name:
                return name
    return "No student logged in"


def read_logs():
    rows = []

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            rows = list(reader)

    return rows


def calculate_score(total):
    if total == 0:
        return 0
    elif total <= 3:
        return 25
    elif total <= 6:
        return 50
    elif total <= 10:
        return 75
    else:
        return 100


@app.route("/")
def home():
    status = get_exam_status()
    student = get_student_name()

    live = os.path.exists(LIVE_IMAGE) and os.path.exists(SESSION_FILE)

    rows = read_logs()
    total = len(rows)
    score = calculate_score(total)

    return render_template_string(
        HTML,
        status=status,
        student=student,
        live=live,
        timestamp=time.time(),
        rows=rows,
        total=total,
        score=score
    )


@app.route("/live")
def live_image():
    if os.path.exists(LIVE_IMAGE) and os.path.exists(SESSION_FILE):
        return send_file(LIVE_IMAGE, mimetype="image/jpeg")
    return "No live image"


@app.route("/start")
def start_exam():
    set_exam_status("STARTED")
    return redirect(url_for("home"))


@app.route("/stop")
def stop_exam():
    set_exam_status("STOPPED")

    if os.path.exists(LIVE_IMAGE):
        os.remove(LIVE_IMAGE)

    return redirect(url_for("home"))


if __name__ == "__main__":
    init_control()
    app.run(debug=True, port=5001)