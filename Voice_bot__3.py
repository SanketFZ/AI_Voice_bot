import streamlit as st
import speech_recognition as sr

import google.generativeai as genai
import time
import pygame
from datetime import datetime,date
from openai import OpenAI
from elevenlabs import ElevenLabs , play 
from dotenv import load_dotenv
import os

load_dotenv()
openaitts = False

st.set_page_config(page_title="AI Voice Assistant", layout="wide")

try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash')
except ImportError:
    st.error("Error: Google Generative AI module not found. Please install it using 'pip install google-generativeai'.")

client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

try:
    pygame.mixer.init()
except Exception as e:
    st.error(f"Error initializing pygame mixer: {e}")


client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY") ,
)


def speak_text(text):
    global openaitts

    if openaitts:
        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text
            )
            fname = 'output.mp3'
            with open(fname, 'wb') as mp3file:
                response.stream_to_file(fname)

            pygame.mixer.music.load(fname)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.25)
            pygame.mixer.music.stop()
        except Exception as e:
            st.error(f"Error in OpenAI TTS: {e}")
    else:
        try:
            audio = client.text_to_speech.convert(
                    text=text,
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_64",
)
            play(audio)
            append_to_log(f"AI: {text}") 
        except Exception as e:
            st.error(f"Error in ElevenLabs TTS: {e}")



st.markdown(
    """
    <style>
        body {
            background: linear-gradient(to right, #2c3e50, #4ca1af);
            font-family: 'Arial', sans-serif;
            color: white;
        }
        .chat-container {
            max-width: 700px;
            margin: auto;
            background: rgba(255, 255, 255, 0.2);
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        }
        .user-message {
            background: #0084ff;
            color: white;
            padding: 10px;
            border-radius: 15px;
            margin-bottom: 10px;
            text-align: right;
        }
        .bot-message {
            background: #f1f0f0;
            color: black;
            padding: 10px;
            border-radius: 15px;
            margin-bottom: 10px;
            text-align: left;
        }
        @keyframes listening {
            0% { opacity: 0.3; }
            50% { opacity: 1; }
            100% { opacity: 0.3; }
        }
        .listening {
            animation: listening 1.5s infinite;
            color: #ffcc00;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔊 AI Voice Assistant")
st.subheader("Talk to me like Google Assistant or Siri!")


def append_to_log(text):
    today = date.today().strftime("%Y-%m-%d")
    filename = f'chatlog-{today}.txt'
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")


# Speech recognition function
def listen():
    rec = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        rec.adjust_for_ambient_noise(source, duration=0.5)
        st.info("Listening...")
        with st.spinner("🎤 AI is Listening..."):
            try:
                audio = rec.listen(source, timeout=5)
                text = rec.recognize_google(audio)
                append_to_log(f"User: {text}")
                return text
            except Exception as e:
                st.warning(f"Could not recognize speech: {e}")
                return ""

# Chat function
def chat_with_ai(user_input):
    try:
        prompt = f"In a technical interview, answer this precisely and concisely: {user_input}."
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating AI response: {e}")
        return "I'm sorry, I couldn't process that request."

# Chat history
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

# Voice input button
if st.button("🎙️ Click to Speak"):
    user_input = listen()
    if user_input:
        st.session_state.chat_log.append(("user", user_input))
        response = chat_with_ai(user_input)
        st.session_state.chat_log.append(("bot", response))
        speak_text(response)

# Display chat history

for role, text in st.session_state.chat_log:
    if role == "user":
        st.markdown(f'<div class="user-message">{text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{text}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
