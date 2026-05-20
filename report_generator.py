import csv
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from config import LOG_FILE

def generate_pdf_report():
    if not os.path.exists(LOG_FILE):
        return

    os.makedirs("reports", exist_ok=True)

    pdf_path = "reports/proctor_report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, 750, "AI Iris Proctoring Report")

    c.setFont("Helvetica", 11)
    y = 700

    with open(LOG_FILE, "r") as file:
        reader = csv.reader(file)

        for row in reader:
            if y < 50:
                c.showPage()
                y = 750

            c.drawString(50, y, " | ".join(row))
            y -= 20

    c.save()
    print("PDF report generated")

def generate_html_report():
    if not os.path.exists(LOG_FILE):
        return

    os.makedirs("reports", exist_ok=True)

    html_path = "reports/proctor_report.html"

    html = """
    <html>
    <head>
    <title>AI Proctoring Report</title>
    <style>
    body { font-family: Arial; background:#f4f4f4; padding:20px; }
    table { width:100%; border-collapse:collapse; background:white; }
    th, td { border:1px solid #333; padding:10px; text-align:left; }
    th { background:#101820; color:white; }
    </style>
    </head>
    <body>
    <h1>AI Iris Proctoring Report</h1>
    <table>
    """

    with open(LOG_FILE, "r") as file:
        reader = csv.reader(file)

        for i, row in enumerate(reader):
            html += "<tr>"
            for col in row:
                tag = "th" if i == 0 else "td"
                html += f"<{tag}>{col}</{tag}>"
            html += "</tr>"

    html += "</table></body></html>"

    with open(html_path, "w") as file:
        file.write(html)

    print("HTML report generated")