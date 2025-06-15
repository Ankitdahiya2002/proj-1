from gtts import gTTS
import pygame
import os
import uuid
import streamlit as st

AUDIO_DIR = "temp_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def speak_text(text, lang="en"):
    st.session_state["audio_playing"] = True

    filename = os.path.join(AUDIO_DIR, f"{uuid.uuid4().hex}.mp3")

    tts = gTTS(text=text, lang=lang)
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Keep checking for cancel flag
    while pygame.mixer.music.get_busy():
        if st.session_state.get("cancel_tts", False):
            pygame.mixer.music.stop()
            break
