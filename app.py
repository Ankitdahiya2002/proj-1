import streamlit as st
from src.auth import auth_page
from src.db import (
    create_tables, save_chat, get_user_chats, get_user,
    save_uploaded_file, get_uploaded_files
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

    # Sidebar: Welcome + Logout
    with st.sidebar:
        st.markdown(
            f"""
            <div style='
                background-color: #e0f7fa;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 10px;
                color: #333;
                font-weight: bold;
            '>
                👋 Hi, {user_name}
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🔒 Logout"):
            del st.session_state["user"]
            st.success("You have been logged out.")
            st.rerun()

    # ⚙️ Settings
    st.sidebar.title("⚙️ Settings")
    language = st.sidebar.selectbox("🌐 Language", ["English 🇺🇸", "Hindi🇮🇳"], index=0, disabled=True)

    # Chat history setup
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = ""
    response = None
    auto_trigger = False

    # 📂 File Upload Section
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

    # 🗂️ User Upload History
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

    # ✍️ Manual input form
    with st.form("chat_form"):
        manual_input = st.text_input("Type your message here:")
        submitted = st.form_submit_button("Send")

    if submitted and manual_input.strip():
        user_input = manual_input.strip()
        auto_trigger = True

    # 🤖 Process chat input
    if auto_trigger and user_input.strip():
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

        st.session_state.chat_history.append({"user": user_input, "ai": response})
        save_chat(user_email, user_input, response, thread_id=None)
        st.success(f"🤖 {response}")

    # 🕘 Chat History
    with st.expander("🕘 Conversation History", expanded=True):
        for chat in st.session_state.chat_history:
            st.markdown(f"**🧑 You:** {chat['user']}")
            st.markdown(f"**🤖 AI:** {chat['ai']}")
            st.markdown("---")


def main():
    st.set_page_config(page_title="OMNISNT AI Assistant", page_icon="🤖")
    create_tables()

    if "user" not in st.session_state:
        auth_page()
        return

    user = get_user(st.session_state["user"])
    if not user:
        st.error("User not found.")
        del st.session_state["user"]
        st.rerun()
        return

    if user.get("blocked"):
        st.error("Your account is blocked. Contact the administrator.")
        del st.session_state["user"]
        return

    if user.get("role") == "admin":
        show_admin_panel()
    else:
        show_user_panel()


if __name__ == "__main__":
    main()
