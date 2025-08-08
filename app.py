import streamlit as st

# Set page config as the very first Streamlit call
st.set_page_config(page_title="Assistant", page_icon="👨🏼‍⚖️", layout="wide")

from src.auth import auth_page
from src.db import (
    create_user, get_user, is_user_verified, update_reset_token, get_all_users,
    block_user, count_registered_users, verify_user_token, reset_password,
    get_uploaded_files, save_uploaded_file, get_user_chats, save_chat
)
from src.admin import show_admin_panel
from src.helper import ai_chat_response
from src.voice_input import get_voice_input
from src.file_reader import extract_file
from src.translation import to_english, to_hindi


def show_user_panel():
    if "user" not in st.session_state:
        st.warning("Please log in.")
        st.stop()

    user_email = st.session_state["user"]
    user = get_user(user_email)
    user_name = user.get("name", "User")

    # Sidebar
    with st.sidebar:
        st.markdown(f"👋 Hi, **{user_name}**", unsafe_allow_html=True)
        if st.button("🔒 Logout"):
            del st.session_state["user"]
            st.success("You have been logged out.")
            st.rerun()

        st.title("⚙️ Settings")
        language = st.selectbox("🌐 Language", ["English 🇺🇸", "Hindi🇮🇳"], index=0, disabled=True)

    # Upload Section
    st.markdown("## 📁 Upload a File")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "xlsx", "csv"])
    if uploaded_file:
        progress_bar = st.progress(0, text="Uploading and extracting...")
        file_type = uploaded_file.type
        file_name = uploaded_file.name

        try:
            progress_bar.progress(30, "Reading file...")
            extracted_text = extract_file(uploaded_file)

            progress_bar.progress(60, "Saving to database...")
            save_uploaded_file(user_email, file_name, file_type, extracted_text)

            progress_bar.progress(100, "Done!")
            st.success(f"✅ File `{file_name}` processed and saved.")

            with st.expander("📄 Extracted Text Preview"):
                st.text_area("Content", extracted_text[:2000], height=300)

        except Exception as e:
            st.error(f"❌ Error: {e}")
            progress_bar.empty()

    # Uploaded Files
    st.markdown("## 🗂️ Your Uploaded Files")
    uploaded_files = get_uploaded_files(user_email)
    if uploaded_files:
        for file in uploaded_files:
            with st.expander(f"{file['file_name']} ({file['file_type']}) - {file['timestamp']}"):
                st.markdown(f"**File Name:** {file['file_name']}")
                st.markdown(f"**Type:** {file['file_type']}")
                st.markdown(f"**Uploaded on:** {file['timestamp']}")
    else:
        st.info("You haven't uploaded any files yet.")

    # Chat Input
    with st.form("chat_form"):
        manual_input = st.text_input("Type your message here:")
        submitted = st.form_submit_button("Send")

    if submitted and manual_input.strip():
        user_input = manual_input.strip()
        translated_input = to_english(user_input) if language == "Hindi" else user_input

        past_chats = get_user_chats(user_email)[-5:]
        history = ""
        for chat in past_chats:
            history += f"User: {chat['user_input'][:500]}\nAI: {chat['ai_response'][:500]}\n\n"

        prompt = history + f"User: {translated_input}\nAI:"
        with st.spinner("Thinking... 🤖"):
            response = ai_chat_response(prompt)

        if language == "Hindi":
            response = to_hindi(response)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        st.session_state.chat_history.append({"user": user_input, "ai": response})
        save_chat(user_email, user_input, response, thread_id=None)
        st.success(f"🤖 {response}")

    # Chat History
    with st.expander("🕘 Conversation History", expanded=True):
        for chat in st.session_state.get("chat_history", []):
            st.markdown(f"**🧑 You:** {chat['user']}")
            st.markdown(f"**🤖 AI:** {chat['ai']}")
            st.markdown("---")


def main():
    query_params = st.query_params
    verify_token = query_params.get("verify_token")

    if verify_token:
        from src.auth import verify_user_token
        if verify_user_token(verify_token):
            st.sidebar.success("✅ Email verified. Please log in.")
        else:
            st.sidebar.error("❌ Invalid or expired verification link.")
        return

    if "user" not in st.session_state:
        # Hide sidebar until user logs in (mobile friendly)
        st.markdown(
            "<style>[data-testid='stSidebar'] {display: none;}</style>",
            unsafe_allow_html=True
        )
        auth_page()
    else:
        user_email = st.session_state["user"]
        user = get_user(user_email)
        if user.get("role") == "admin":
            show_admin_panel()
        else:
            show_user_panel()


if __name__ == "__main__":
    main()
