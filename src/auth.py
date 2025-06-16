import streamlit as st
import uuid
from datetime import datetime, timedelta
from src.db import (
    create_user, get_user, update_reset_token,
    reset_password, verify_user_token, is_user_verified
)
from src.security import hash_password, verify_password
from src.email_utils import send_email
from src.db import get_connection


def auth_page():
    st.sidebar.title("🔐 Authentication")
    mode = st.sidebar.radio("Choose mode", ["Login", "Sign Up", "Reset Password"], key="auth_mode")

    # --- Handle verification from token in URL
    query_params = st.query_params
    token = query_params.get("verify_token", None)


    if token:
        if verify_user_token(token):
            st.sidebar.success("✅ Email verified. Please log in.")
        else:
            st.sidebar.error("❌ Invalid or expired verification link.")

    if mode == "Login":
        login_ui()
    elif mode == "Sign Up":
        signup_ui()
    else:
        reset_ui()


def login_ui():
    st.sidebar.subheader("Login to your account")

    email = st.sidebar.text_input("📧 Email")
    password = st.sidebar.text_input("🔒 Password", type="password")

    if st.sidebar.button("Login"):
        user = get_user(email)
        if user and verify_password(password, user["password"]):
            if not user.get("verified", 0):
                st.sidebar.warning("Please verify your email before logging in.")
            elif user.get("blocked", 0):
                st.sidebar.error("🚫 Your account has been blocked.")
            else:
                st.session_state["user"] = user["email"]
                st.sidebar.success(f"✅ Logged in as {user.get('name', email)}")
                st.rerun()

        else:
            st.sidebar.error("Invalid email or password")


def signup_ui():
    st.sidebar.subheader("Create an account")

    name = st.sidebar.text_input("🧑 Full Name")
    profession = st.sidebar.text_input("💼 Profession")
    email = st.sidebar.text_input("📧 Email")
    password = st.sidebar.text_input("🔒 Password", type="password")
    confirm = st.sidebar.text_input("🔒 Confirm Password", type="password")

    if st.sidebar.button("Sign Up"):
        if password != confirm:
            st.sidebar.warning("Passwords do not match.")
            return

        hashed = hash_password(password)
        token = str(uuid.uuid4())

        if create_user(email, hashed, name=name, profession=profession, verification_token=token):
            verify_link = f"{st.secrets['APP_BASE_URL']}/?verify_token={token}"
            # Send verification email
            send_email(
                email,
                "Verify your OMNISNT Account",
                f"<p>Hi {name},</p><p>Click the link to verify your account:</p><a href='{verify_link}'>{verify_link}</a>"
            )
            st.sidebar.success("Account created! Please verify your email.")
        else:
            st.sidebar.error("Email already registered.")


def reset_ui():
    st.sidebar.subheader("Reset your password")

    email = st.sidebar.text_input("📧 Enter your email")

    if st.sidebar.button("Send Reset Link"):
        user = get_user(email)
        if not user:
            st.sidebar.warning("Email not found.")
            return

        token = str(uuid.uuid4())
        expiry = datetime.now() + timedelta(minutes=30)
        update_reset_token(email, token, expiry)

        reset_link = f"{st.secrets['APP_BASE_URL']}/?reset_token={token}"
        # Send reset email
        send_email(
            email,
            "Password Reset - OMNISNT",
            f"<p>Click below to reset your password:</p><a href='{reset_link}'>{reset_link}</a>"
        )
        st.sidebar.success("Check your email for a reset link.")

    # If token in query params
    reset_token = st.query_params.get("reset_token", None)

    if reset_token:
        new_pass = st.sidebar.text_input("🔐 New Password", type="password")
        confirm_pass = st.sidebar.text_input("🔁 Confirm Password", type="password")

        if st.sidebar.button("Reset Password"):
            if new_pass != confirm_pass:
                st.sidebar.error("Passwords don't match.")
                return

            hashed = hash_password(new_pass)
            # Fetch user by token
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT email, reset_token_expiry FROM users WHERE reset_token = ?", (reset_token,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                st.sidebar.error("Invalid or expired reset link.")
                return

            email = row["email"]
            expiry = datetime.strptime(row["reset_token_expiry"], "%Y-%m-%d %H:%M:%S")

            if datetime.now() > expiry:
                st.sidebar.error("Reset link has expired.")
                return

            reset_password(email, hashed)
            st.sidebar.success("Password updated! You can now log in.")


# Optional helper for token-based logic in `db.py`
def get_connection():
    import sqlite3
    conn = sqlite3.connect("omnisicient.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
