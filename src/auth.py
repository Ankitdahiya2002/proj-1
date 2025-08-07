import streamlit as st
import hashlib
import uuid
from datetime import datetime, timedelta

from src.db import (
    create_user, get_user, is_user_verified, update_reset_token,
    verify_user_credentials, reset_user_password_by_token,
    block_user, count_registered_users,
    verify_user_token, reset_password
)
from src.email_utils import send_verification_email, send_reset_email

# Set default auth mode
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

def auth_page():
    st.title("🔐 OMNISNT AI Assistant - Login")

    # Handle reset token in URL using st.query_params (Streamlit v1.35+)
    reset_token = st.query_params.get("reset_token")
    if reset_token:
        st.session_state.auth_mode = "reset"
        st.session_state.reset_token = reset_token

        # Clean URL by removing query param (not supported directly yet)
        st.query_params.clear()

    # Determine which page to show
    mode = st.session_state.get("auth_mode", "login")

    if mode == "login":
        login_form()
    elif mode == "signup":
        signup_form()
    elif mode == "forgot":
        forgot_password_form()
    elif mode == "reset":
        reset_password_form()


# ✅ LOGIN
def login_form():
    st.subheader("🔑 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email and password:
            if verify_user_credentials(email, password):
                st.session_state.user = email
                st.success("✅ Logged in successfully.")
                st.rerun()
            else:
                st.error("❌ Invalid email or password.")
        else:
            st.warning("Please enter both email and password.")

    st.text("Don't have an account?")
    if st.button("👉 Sign Up"):
        st.session_state.auth_mode = "signup"

    st.text("Forgot password?")
    if st.button("🔁 Reset Password"):
        st.session_state.auth_mode = "forgot"


# ✅ SIGN UP
def signup_form():
    st.subheader("📝 Create Account")
    name = st.text_input("Name")
    profession = st.text_input("Profession")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if name and email and password:
            token = str(uuid.uuid4())
            success = create_user(email, password, name, profession, token)
            if success:
                send_verification_email(email, token)
                st.success("✅ Account created! Check your email to verify.")
                st.session_state.auth_mode = "login"
            else:
                st.error("❌ User already exists or error occurred.")
        else:
            st.warning("Please fill all fields.")

    if st.button("🔙 Back to Login"):
        st.session_state.auth_mode = "login"


# ✅ FORGOT PASSWORD
def forgot_password_form():
    st.subheader("🔁 Forgot Password")
    email = st.text_input("Enter your registered email")

    if st.button("Send Reset Link"):
        user = get_user(email)
        if user:
            token = str(uuid.uuid4())
            expiry = datetime.now() + timedelta(hours=1)
            update_reset_token(email, token, expiry)
            send_reset_email(email, token)
            st.success("📧 Reset link sent to your email.")
            st.session_state.auth_mode = "login"
        else:
            st.error("❌ Email not found.")

    if st.button("🔙 Back to Login"):
        st.session_state.auth_mode = "login"


# ✅ RESET PASSWORD
def reset_password_form():
    st.subheader("🔑 Set New Password")

    token = st.session_state.get("reset_token", None)
    if not token:
        st.error("❌ Invalid or missing reset token.")
        return

    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Reset Password"):
        if new_password != confirm_password:
            st.error("❌ Passwords do not match.")
            return

        hashed = hashlib.sha256(new_password.encode()).hexdigest()
        if reset_user_password_by_token(token, hashed):
            st.success("✅ Password reset successfully. You can now log in.")
            st.session_state.auth_mode = "login"
            st.session_state.pop("reset_token", None)
            st.rerun()

        else:
            st.error("❌ Invalid or expired token.")

    if st.button("🔙 Back to Login"):
        st.session_state.auth_mode = "login"
