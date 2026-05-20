from flask import Flask, render_template_string
import csv
import os
from collections import Counter

app = Flask(__name__)

LOG_FILE = "proctor_logs.csv"

HTML = """
<html>
<head>
<title>AI Proctoring Dashboard</title>

<meta http-equiv="refresh" content="3">

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body {
    font-family: Arial;
    background:#101820;
    color:white;
    padding:20px;
}

h1 {
    text-align:center;
}

.cards {
    display:flex;
    justify-content:space-around;
    margin-bottom:20px;
}

.card {
    background:#00a86b;
    padding:20px;
    border-radius:10px;
    width:200px;
    text-align:center;
}

table {
    width:100%;
    border-collapse:collapse;
    background:white;
    color:black;
}

th, td {
    border:1px solid #333;
    padding:10px;
    text-align:left;
}

th {
    background:#00a86b;
    color:white;
}
</style>
</head>

<body>

<h1>AI Iris Proctoring Dashboard</h1>

<div class="cards">
    <div class="card">
        <h2>Total Alerts</h2>
        <p>{{ total }}</p>
    </div>
    <div class="card">
        <h2>Face Alerts</h2>
        <p>{{ face }}</p>
    </div>
    <div class="card">
        <h2>Audio Alerts</h2>
        <p>{{ audio }}</p>
    </div>
    <div class="card">
        <h2>Eye Alerts</h2>
        <p>{{ eye }}</p>
    </div>
</div>

<canvas id="chart" height="100"></canvas>

<br><br>

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

<script>
var ctx = document.getElementById('chart').getContext('2d');

var chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Face', 'Audio', 'Eye'],
        datasets: [{
            label: 'Alerts Count',
            data: [{{ face }}, {{ audio }}, {{ eye }}],
        }]
    }
});
</script>

</body>
</html>
"""

@app.route("/")
def dashboard():
    rows = []
    alerts = []

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            rows = list(reader)

            for r in rows:
                alerts.append(r[1])

    total = len(alerts)

    counter = Counter()

    for a in alerts:
        if "face" in a.lower():
            counter["face"] += 1
        elif "eye" in a.lower():
            counter["eye"] += 1
        elif "speaking" in a.lower() or "audio" in a.lower():
            counter["audio"] += 1

    return render_template_string(
        HTML,
        rows=rows,
        total=total,
        face=counter["face"],
        audio=counter["audio"],
        eye=counter["eye"]
    )

if __name__ == "__main__":
    app.run(debug=True)