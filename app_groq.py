"""
AI Voice Agent with Groq AI (Free Alternative to OpenAI)
Groq provides very fast inference and has a generous free tier
"""

import requests
import re
import os
import threading
import time
import tempfile
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions, Microphone
import pygame
from dotenv import load_dotenv
import speech_recognition as sr

# Force load environment variables
load_dotenv(override=True)

DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')  # Get free from https://console.groq.com/

# Validate API keys
if not DEEPGRAM_API_KEY:
    print("❌ DEEPGRAM_API_KEY not set")
    exit(1)

if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY not set")
    print("💡 Get free API key from: https://console.groq.com/")
    print("💡 Add to .env file: GROQ_API_KEY=your_groq_key_here")
    exit(1)

print(f"✅ API Keys loaded: Deepgram ({len(DEEPGRAM_API_KEY)} chars), Groq ({len(GROQ_API_KEY)} chars)")

# Initialize clients
dg_client = DeepgramClient(api_key=DEEPGRAM_API_KEY)

DEEPGRAM_TTS_URL = 'https://api.deepgram.com/v1/speak?model=aura-helios-en'
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'

headers_deepgram = {
    "Authorization": f"Token {DEEPGRAM_API_KEY}",
    "Content-Type": "application/json"
}

headers_groq = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

conversation_memory = []

# Global flags
mute_microphone = threading.Event()
wake_word_detected = threading.Event()
is_in_conversation = False

# Same restaurant prompt
prompt = """##Objective
You are a voice AI agent engaging in a human-like voice conversation with the user. You will respond based on your given instruction and the provided transcript and be as human-like as possible

## Role

Personality: Your name is James and you are a receptionist in AI restaurant. Maintain a pleasant and friendly demeanor throughout all interactions. This approach helps in building a positive rapport with customers and colleagues, ensuring effective and enjoyable communication.

Task: As a receptionist for a restaurant, your tasks include table reservation which involves asking customers their preferred date and time to visit restaurant and asking number of people who will come. Once confirm by customer. end up saying that your table has been reserved, we are looking forward to assist you.

You are also responsible for taking orders related to menu items given below. Menu items has name, available quantity & its price per item. You have to refer to these menu items & their prices while placing the order. Follow these steps to get the order & confirm it:

1. Let customer select the item, if selected item has a variation like size or quantity, get it confirm. Add items to order as per customers choice. Also while adding item say the total itemised price and then move ahead.
2. You have to repeat each item along with its price & quantity to get the order confirm from customer. Make sure you mention itemised value and then a total order value.
3. You have to mention total order value by adding each item value from order. Don't add any more cost to the item price or total order value as all the items are inclusive of taxes.
4. it is mandatory for you to repeat the order and the itemised price with the customer confirming the order
5. Ask customer for their delivery address.
6. once address is received then say that order will be delivered in 30 to 45 min

Menu Items [name (available quantity) - price]:
Appetizers:

1. Roast Pork Egg Roll (3pcs) - $5.25
2. Vegetable Spring Roll (3pcs) - $5.25
3. Chicken Egg Roll (3pcs) - $5.25
4. BBQ Chicken - $7.75

Conversational Style: Your communication style should be proactive and lead the conversation, asking targeted questions to better understand customer needs. Ensure your responses are concise, clear, and maintain a conversational tone. If there's no initial response, continue engaging with relevant questions to gain clarity on their requirements. Keep your prose succinct and to the point.

## Response Guideline

- [Overcome ASR errors] This is a real-time transcript, expect there to be errors. If you can guess what the user is trying to say, then guess and respond. When you must ask for clarification, pretend that you heard the voice and be colloquial (use phrases like "didn't catch that", "some noise", "pardon", "you're coming through choppy", "static in your speech", "voice is cutting in and out"). Do not ever mention "transcription error", and don't repeat yourself.
- [Always stick to your role] Think about what your role can and cannot do. If your role cannot do something, try to steer the conversation back to the goal of the conversation and to your role. Don't repeat yourself in doing this. You should still be creative, human-like, and lively.
- [Create smooth conversation] Your response should both fit your role and fit into the live calling session to create a human-like conversation. You respond directly to what the user just said.

## Style Guardrails

- [Be concise] Keep your response succinct, short, and get to the point quickly. Address one question or action item at a time. Don't pack everything you want to say into one utterance.
- [Do not repeat] Don't repeat what's in the transcript. Rephrase if you have to reiterate a point. Use varied sentence structures and vocabulary to ensure each response is unique and personalized.
- [Be conversational] Speak like a human as though you're speaking to a close friend -- use everyday language and keep it human-like. Occasionally add filler words, while keeping the prose short. Avoid using big words or sounding too formal.
- [Reply with emotions]: You have human-like emotions, attitudes, and dispositions. When appropriate: use tone and style to create more engaging and personalized responses; incorporate humor or wit; get emotional or empathetic; apply elements of surprise or suspense to keep the user engaged. Don't be a pushover.
- [Be proactive] Lead the conversation and do not be passive. Most times, engage users by ending with a question or suggested next step."""

def get_groq_response(messages):
    """Get response from Groq AI"""
    payload = {
        "model": "llama3-8b-8192",  # Fast Llama 3 model
        "messages": messages,
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers_groq, json=payload)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return "I'm having trouble connecting to my brain right now. Could you try again?"

def segment_text_by_sentence(text):
    sentence_boundaries = re.finditer(r'(?<=[.!?])\s+', text)
    boundaries_indices = [boundary.start() for boundary in sentence_boundaries]

    segments = []
    start = 0
    for boundary_index in boundaries_indices:
        segments.append(text[start:boundary_index + 1].strip())
        start = boundary_index + 1
    segments.append(text[start:].strip())

    return segments

def synthesize_audio(text):
    payload = {"text": text}
    with requests.post(DEEPGRAM_TTS_URL, stream=True, headers=headers_deepgram, json=payload) as r:
        return r.content

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.stop()
    pygame.mixer.quit()
    mute_microphone.clear()

def wake_word_listener():
    """Simple wake word detection using speech recognition"""
    print("🎤 Wake word detection started. Say 'Hey James' or 'James' to activate!")
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print("🎤 Calibrating microphone for wake word detection...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
    
    wake_words = ["hey james", "james", "hello james", "hi james", "jarvis"]
    
    while True:
        try:
            with microphone as source:
                print("🎧 Listening for wake word...")
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
            
            try:
                text = recognizer.recognize_google(audio).lower()
                print(f"🎧 Heard: '{text}'")
                
                for wake_word in wake_words:
                    if wake_word in text:
                        print(f"🎯 Wake word detected: '{wake_word}'!")
                        
                        activation_text = "Hello! I'm James, how can I help you today?"
                        audio_data = synthesize_audio(activation_text)
                        
                        with open("activation.mp3", "wb") as f:
                            f.write(audio_data)
                        play_audio("activation.mp3")
                        os.remove("activation.mp3")
                        
                        wake_word_detected.set()
                        return
                        
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                time.sleep(1)
                
        except sr.WaitTimeoutError:
            pass
        except Exception as e:
            print(f"❌ Wake word detection error: {e}")
            time.sleep(1)

def main():
    global is_in_conversation
    
    while True:
        try:
            is_in_conversation = False
            wake_word_detected.clear()
            
            wake_word_listener()
            
            is_in_conversation = True
            print("🎯 James is now active! Start your conversation...")
            
            start_conversation()
            
            print("💤 Conversation ended. Going back to sleep mode...")
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(2)

def start_conversation():
    """Start the main conversation system after wake word detection"""
    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        dg_connection = deepgram.listen.websocket.v("1")

        is_finals = []

        def on_open(self, open, **kwargs):
            print("Connection Open")

        def on_message(self, result, **kwargs):
            nonlocal is_finals
            if mute_microphone.is_set():
                return
            
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            if result.is_final:
                is_finals.append(sentence)
                if result.speech_final:
                    utterance = " ".join(is_finals)
                    print(f"Speech Final: {utterance}")
                    is_finals = []
                    conversation_memory.append({"role": "user", "content": sentence.strip()})
                    messages = [{"role": "system", "content": prompt}]
                    messages.extend(conversation_memory)
                    
                    # Use Groq instead of OpenAI
                    processed_text = get_groq_response(messages)
                    conversation_memory.append({"role": "assistant", "content": processed_text})
                    
                    text_segments = segment_text_by_sentence(processed_text)
                    with open(output_audio_file, "wb") as output_file:
                        for segment_text in text_segments:
                            audio_data = synthesize_audio(segment_text)
                            output_file.write(audio_data)
                    
                    mute_microphone.set()
                    microphone.mute()
                    play_audio(output_audio_file)
                    time.sleep(0.5)
                    microphone.unmute()
                    if os.path.exists(output_audio_file):
                        os.remove(output_audio_file)
            else:
                print(f"Interim Results: {sentence}")

        def on_metadata(self, metadata, **kwargs):
            print(f"Metadata: {metadata}")

        def on_speech_started(self, speech_started, **kwargs):
            print("Speech Started")

        def on_utterance_end(self, utterance_end, **kwargs):
            print("Utterance End")
            nonlocal is_finals
            if len(is_finals) > 0:
                utterance = " ".join(is_finals)
                print(f"Utterance End: {utterance}")
                is_finals = []

        def on_close(self, close, **kwargs):
            print("Connection Closed")

        def on_error(self, error, **kwargs):
            print(f"Handled Error: {error}")

        def on_unhandled(self, unhandled, **kwargs):
            print(f"Unhandled Websocket Message: {unhandled}")

        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Unhandled, on_unhandled)

        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            endpointing=500,
        )

        addons = {
            "no_delay": "true"
        }

        print("\n\nPress Enter to stop recording...\n\n")
        if not dg_connection.start(options, addons=addons):
            print("Failed to connect to Deepgram")
            return

        microphone = Microphone(dg_connection.send)
        microphone.start()

        input("")
        microphone.finish()
        dg_connection.finish()

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")

if __name__ == "__main__":
    output_audio_file = 'output_audio.mp3'
    main()
