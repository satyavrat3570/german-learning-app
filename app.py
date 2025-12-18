import streamlit as st
import pandas as pd
import speech_recognition as sr
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import os
import tempfile
import io

# --- CONFIGURATION ---
CSV_FILE = "german_vocab.csv"

# --- FUNCTIONS ---
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame({'German': ['Hallo'], 'English': ['Hello']})

def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='de')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except:
        return None

def check_audio_bytes(audio_bytes, target_word):
    r = sr.Recognizer()
    # Convert raw bytes to a file-like object
    audio_file = io.BytesIO(audio_bytes)
    
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="de-DE")
            return text
    except sr.UnknownValueError:
        return "???"
    except sr.RequestError:
        return "Error"
    except Exception as e:
        return "???"

# --- APP LAYOUT ---
st.set_page_config(page_title="German Mobile", layout="centered")

# Initialize Session
if 'index' not in st.session_state:
    st.session_state.index = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""

df = load_data()
if st.session_state.index >= len(df):
    st.session_state.index = 0

row = df.iloc[st.session_state.index]
german = row['German']
english = row['English']

# --- MOBILE UI ---
st.markdown(f"""
<div style="text-align: center; margin-top: 20px;">
    <h1 style="font-size: 60px; margin-bottom: 0;">{german}</h1>
    <p style="font-size: 24px; color: #555;">{english}</p>
</div>
""", unsafe_allow_html=True)

# Audio Player (Listen)
st.write("### 1. Listen")
audio_path = text_to_speech(german)
if audio_path:
    st.audio(audio_path, format="audio/mp3")

# Recorder (Speak)
st.write("### 2. Speak")
st.caption("Tap 'Start', speak the word, then tap 'Stop'.")

# This is the special mobile button
audio = mic_recorder(
    start_prompt="🔴 Start Recording",
    stop_prompt="⏹ Stop & Check",
    key='recorder'
)

if audio:
    user_text = check_audio_bytes(audio['bytes'], german)
    
    if user_text.lower() == german.lower():
        st.success(f"✅ Perfect! You said: {user_text}")
        st.balloons()
    elif user_text == "???":
        st.warning("⚠️ Didn't catch that. Try closer to the mic.")
    else:
        st.error(f"❌ Heard: '{user_text}'")

st.markdown("---")
# Next Button (Big for fingers)
if st.button("NEXT WORD ➡️", use_container_width=True):
    st.session_state.index += 1
    st.session_state.feedback = ""
    st.rerun()