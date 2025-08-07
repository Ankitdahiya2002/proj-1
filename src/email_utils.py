import smtplib
from email.mime.text import MIMEText
import streamlit as st

from src.db import log_email_status, get_connection


def send_email(to_email, subject, body):
    """
    Send an HTML email using SMTP credentials from Streamlit secrets.
    Logs success or failure in the email_logs table.
    """
    EMAIL_HOST = st.secrets.get("EMAIL_HOST")
    EMAIL_PORT = int(st.secrets.get("EMAIL_PORT", 587))
    EMAIL_USER = st.secrets.get("EMAIL_USER")
    EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD")

    if not all([EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD]):
        print("❌ Email credentials are not fully set.")
        log_email_status(to_email, subject, "failed", "Missing SMTP credentials")
        return False

    try:
        msg = MIMEText(f"<html><body>{body}</body></html>", "html")
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = to_email

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, [to_email], msg.as_string())
        server.quit()

        print(f"✅ Email sent to {to_email}.")
        log_email_status(to_email, subject, "sent")
        return True

    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        log_email_status(to_email, subject, "failed", str(e))
        return False


def send_verification_email(to_email, verification_token):
    """
    Sends an account verification email with a unique tokenized link.
    """
    base_url = st.secrets.get("BASE_URL", "http://localhost:8501")
    verification_link = f"{base_url}/?verify_token={verification_token}"

    subject = "Verify your email - OMNISNT AI Assistant"
    body = f"""
        <h3>Welcome to OMNISNT AI Assistant 👋</h3>
        <p>To activate your account, please click the link below:</p>
        <p><a href="{verification_link}">{verification_link}</a></p>
        <p>If you didn’t request this, feel free to ignore it.</p>
    """
    return send_email(to_email, subject, body)


def send_reset_email(to_email, reset_token):
    """
    Sends a password reset email with a secure reset token link.
    """
    base_url = st.secrets.get("BASE_URL", "http://localhost:8501")
    reset_link = f"{base_url}/?reset_token={reset_token}"

    subject = "Reset Your Password - OMNISNT AI Assistant"
    body = f"""
        <h3>Forgot your password?</h3>
        <p>Click the link below to reset it. This link expires in 30 minutes:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
    """
    return send_email(to_email, subject, body)
