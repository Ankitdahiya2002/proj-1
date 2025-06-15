import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ✅ Replace with your actual Gmail and App Password
SENDER = "dahiyaankit38@gmail.com"
APP_PASSWORD = "bqvmuoktepzzhjcd"

def send_email(to, subject, html_content):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = to

    part = MIMEText(html_content, "html")
    msg.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER, APP_PASSWORD)
        server.sendmail(SENDER, to, msg.as_string())
