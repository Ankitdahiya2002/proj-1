import streamlit as st
from src.voice_input import get_voice_input
from src.translation import to_english, to_hindi
from src.helper import ai_chat_response

# Optional: user preference stored in session
language = st.selectbox("🌐 Language", ["English", "Hindi"])
voice_enabled = st.checkbox("🎤 Enable Voice Input")

# Set language code
lang_code = "hi-IN" if language == "Hindi" else "en-US"

# Combine text + voice input
text_input = st.text_area("💬 Type your message")

if voice_enabled:
    voice_text = get_voice_input(language=lang_code)
    if voice_text:
        text_input = voice_text

# Translation
if text_input:
    st.markdown(f"📝 Your message: `{text_input}`")

    # Translate to English if input is in Hindi
    query = to_english(text_input, src_lang="hi") if language == "Hindi" else text_input

    # Replace with your chatbot logic
    ai_response = ai_chat_response(query)

    # Translate back to Hindi if needed
    if language == "Hindi":
        ai_response = to_hindi(ai_response)

    st.markdown("🤖 **AI Response:**")
    st.success(ai_response)
