import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
#from src.db import log_email_status


def send_email(to, subject, html_content):
    """
    Send an HTML email via Gmail SMTP using Streamlit secrets.
    """
    try:
        # Load sensitive info from Streamlit secrets
        SENDER = st.secrets["EMAIL_USER"]
        APP_PASSWORD = st.secrets["EMAIL_PASSWORD"]

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

        print(f"✅ Email sent to {to}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email to {to}: {e}")
        return False
