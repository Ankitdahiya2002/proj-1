import streamlit as st
from src.db import (
    get_all_users, block_user, export_chats_to_csv,
    count_registered_users
)
from src.email_utils import send_email


def show_admin_panel():
    st.set_page_config(page_title="Admin Dashboard", page_icon="👑")
    st.title("👑 OMNISCENT Admin Dashboard")

    # --- Metrics Section
    col1, col2 = st.columns(2)
    with col1:
        total_users = count_registered_users()
        st.metric("Total Registered Users", total_users)

    with col2:
        st.metric("Admin Access", "✔️ Active")

    st.markdown("---")

    # --- Search & Filter Users
    st.subheader("📋 User Accounts")
    search_term = st.text_input("🔍 Search user by email or name")

    users = get_all_users()
    users = sorted(users, key=lambda u: u.get("blocked", 0), reverse=True)

    if search_term:
        users = [
            u for u in users
            if search_term.lower() in u["email"].lower()
            or search_term.lower() in u.get("name", "").lower()
        ]

    if not users:
        st.info("No users found.")
    else:
        for i, user in enumerate(users):
            col1, col2, col3 = st.columns([3, 1.2, 1])
            with col1:
                st.markdown(f"""
                    **{user.get("name", "Unnamed")}**  
                    📧 `{user['email']}`  
                    🧑‍💼 *{user.get("profession", "Unknown")}*  
                    🛡️ Role: `{user.get("role", "user")}`
                """)
            with col2:
                blocked = bool(user.get("blocked", 0))
                btn_label = "🔓 Unblock" if blocked else "🔒 Block"
                if st.button(btn_label, key=f"block_btn_{i}"):
                    block_user(user["email"], not blocked)
                    st.success(f"{'Unblocked' if blocked else 'Blocked'} {user['email']}")
                    st.experimental_rerun()

            with col3:
                pass  # Reserved for future actions (e.g., promote/delete user)

    st.markdown("---")

    # --- Export Chat Logs
    st.subheader("📤 Export All Chat Logs")
    if st.button("📥 Generate CSV"):
        csv_data = export_chats_to_csv()
        st.download_button(
            label="📄 Download chat_history.csv",
            data=csv_data,
            file_name="chat_history.csv",
            mime="text/csv"
        )

    st.markdown("---")

    # --- Email Testing Utility
    st.subheader("📧 Send Test Email")
    email_tester()


def email_tester():
    test_email = st.text_input("📨 Send Test Email To")
    if st.button("✉️ Send Test Email"):
        if test_email:
            success = send_email(test_email, "Test Email from OMNISNT", "<p>This is a test email from the admin panel.</p>")
            if success:
                st.success("✅ Test email sent successfully!")
            else:
                st.error("❌ Failed to send test email.")
        else:
            st.warning("Please enter a valid email address.")
