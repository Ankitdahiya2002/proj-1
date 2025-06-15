import os
import smtplib
import streamlit as st
import google.generativeai as genai
from email.mime.text import MIMEText


# Gemini AI Setup
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
print("GEMINI_API_KEY Loaded:", bool(GEMINI_API_KEY))

try:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in Streamlit secrets.")
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print("❌ Failed to configure Gemini:", e)
    genai = None


def gemini_model_object(user_input):
    if not genai:
        return "Gemini is not properly configured. Check API key or SDK."
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content({
            "parts": [
                {"text": user_input}
            ]
        })
        return response.text
    except Exception as e:
        return f"Error from Gemini API: {str(e)}"



def ai_chat_response(prompt: str) -> str:
    """
    Send the full prompt including conversation history to Gemini model.
    """
    if not genai:
        return "Gemini is not properly configured. Check API key or SDK."
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content({
            "parts": [
                {"text": prompt}
            ]
        })
        return response.text.strip()
    except Exception as e:
        return f"Error from Gemini API: {str(e)}"


def send_email(to_email, subject, body):
    """
    Send an email using SMTP credentials.
    """
    EMAIL_HOST = st.secrets["EMAIL_HOST"]
    EMAIL_PORT = int(st.secrets.get("EMAIL_PORT", 587))
    EMAIL_USER = st.secrets["EMAIL_USER"]
    EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]


    if not all([EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD]):
        print("Email credentials are not fully set.")
        return False

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = to_email

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, [to_email], msg.as_string())
        server.quit()
        print("✅ Email sent successfully.")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


if __name__ == "__main__":
    test_input = "Hello, how are you?"
    print("AI Response:", ai_chat_response(test_input))
