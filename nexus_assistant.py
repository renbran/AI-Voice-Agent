import speech_recognition as sr
import sqlite3
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set your OpenAI API key (for Whisper)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Database setup
DB_NAME = "nexus_knowledge.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# Add knowledge to the database
def add_knowledge(question, answer):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO knowledge (question, answer) VALUES (?, ?)", (question, answer))
    conn.commit()
    conn.close()

# Query knowledge from the database
def get_answer(question):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT answer FROM knowledge WHERE question LIKE ?", (f"%{question}%",))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Wake word and personalization
WAKE_WORDS = ["nexus"]
USER_NAMES = ["Renbran", "Sir Renbran", "Bro Renbran"]

# Recognize speech using microphone
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
    return ""

# Use OpenAI Whisper for advanced transcription (optional)
def whisper_transcribe(audio_file_path):
    if not OPENAI_API_KEY:
        print("OpenAI API key not set. Skipping Whisper transcription.")
        return None
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        return transcript["text"]

def main():
    init_db()
    print("Nexus AI Personal Assistant is running.")
    print(f"Say '{WAKE_WORDS[0]}' to activate.")
    while True:
        text = recognize_speech()
        if any(wake in text for wake in WAKE_WORDS):
            print(f"Hello, {USER_NAMES[0]}! How can I assist you today?")
            print("Ask a question or say 'add knowledge' to teach me.")
            command = recognize_speech()
            if "add knowledge" in command:
                print("What is the question?")
                q = recognize_speech()
                print("What is the answer?")
                a = recognize_speech()
                add_knowledge(q, a)
                print("Knowledge added!")
            else:
                answer = get_answer(command)
                if answer:
                    print(f"{USER_NAMES[0]}, the answer is: {answer}")
                else:
                    print(f"Sorry {USER_NAMES[0]}, I don't know the answer yet.")

if __name__ == "__main__":
    main()
