# src/voice_input.py
import openai
import streamlit as st
import tempfile

def get_voice_input():
    st.info("📤 Upload an audio file (WAV, MP3, M4A,txt,pdf)")
    audio_file = st.file_uploader("Upload your voice input", type=["wav", "mp3", "m4a","txt","pdf","xlsx"])
    
    if audio_file is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3",prefix = ".txt") as tmp_file:
                tmp_file.write(audio_file.read())
                tmp_path = tmp_file.name

            with open(tmp_path, "rb") as f:
                transcription = openai.Audio.transcribe(f)
                return transcription["text"]
        except Exception as e:
            st.error(f"❌ API error: {e}")
    return None
