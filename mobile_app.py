"""
Mobile Web Interface for AI Voice Agent
This creates a web-based version that works on mobile browsers
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import base64
import io
import wave
import openai
import os
from dotenv import load_dotenv
import requests
import threading
import time

# Force load environment variables from .env file, overriding system variables
load_dotenv(override=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize OpenAI with proper API key validation
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

if not OPENAI_API_KEY or len(OPENAI_API_KEY) < 40:
    print("❌ OPENAI_API_KEY not set properly in .env file")
    exit(1)

if not DEEPGRAM_API_KEY:
    print("❌ DEEPGRAM_API_KEY not set properly in .env file") 
    exit(1)

client = openai.OpenAI(api_key=OPENAI_API_KEY)
print(f"✅ Mobile API Keys loaded: Deepgram ({len(DEEPGRAM_API_KEY)} chars), OpenAI ({len(OPENAI_API_KEY)} chars)")

# Same conversation memory and prompt from your original app
conversation_memory = []
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

def transcribe_audio_deepgram(audio_data):
    """Transcribe audio using Deepgram"""
    url = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/wav"
    }
    
    response = requests.post(url, headers=headers, data=audio_data)
    result = response.json()
    
    if 'results' in result and result['results']['channels']:
        transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript
    return ""

def synthesize_audio_deepgram(text):
    """Generate speech using Deepgram TTS"""
    url = 'https://api.deepgram.com/v1/speak?model=aura-helios-en'
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    
    response = requests.post(url, stream=True, headers=headers, json=payload)
    return response.content

@app.route('/')
def index():
    return render_template('simple_voice.html')

@socketio.on('wake_word_check')
def handle_wake_word(data):
    try:
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio'].split(',')[1])
        
        # Transcribe the audio
        transcript = transcribe_audio_deepgram(audio_data)
        
        if transcript.strip():
            text = transcript.lower()
            print(f"🎧 Wake word check: '{text}'")
            
            # Check for wake words
            wake_words = ["hey james", "james", "hello james", "hi james", "jarvis"]
            
            for wake_word in wake_words:
                if wake_word in text:
                    print(f"🎯 Wake word detected: '{wake_word}'!")
                    
                    # Generate activation response
                    activation_text = "Hello! I heard you call me. How can I assist you today?"
                    audio_response = synthesize_audio_deepgram(activation_text)
                    audio_b64 = base64.b64encode(audio_response).decode('utf-8')
                    
                    # Send wake word detected event
                    emit('wake_word_detected', {
                        'wake_word': wake_word,
                        'audio': f"data:audio/mp3;base64,{audio_b64}"
                    })
                    break
    
    except Exception as e:
        print(f"Wake word detection error: {e}")

@socketio.on('james_activated')
def handle_james_activation():
    """Handle manual James activation"""
    print("🎯 James manually activated via mobile interface")
    
    # Generate activation response
    activation_text = "Hello! How can I assist you today?"
    audio_response = synthesize_audio_deepgram(activation_text)
    audio_b64 = base64.b64encode(audio_response).decode('utf-8')
    
    # Send activation confirmation
    emit('wake_word_detected', {
        'wake_word': 'manual_activation',
        'audio': f"data:audio/mp3;base64,{audio_b64}"
    })

@socketio.on('audio_data')
def handle_audio(data):
    try:
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio'].split(',')[1])
        
        # Transcribe the audio
        transcript = transcribe_audio_deepgram(audio_data)
        
        if transcript.strip():
            # Add to conversation memory
            conversation_memory.append({"role": "user", "content": transcript.strip()})
            
            # Generate response using OpenAI
            messages = [{"role": "system", "content": prompt}]
            messages.extend(conversation_memory)
            
            chat_completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            response_text = chat_completion.choices[0].message.content.strip()
            conversation_memory.append({"role": "assistant", "content": response_text})
            
            # Generate speech
            audio_response = synthesize_audio_deepgram(response_text)
            audio_b64 = base64.b64encode(audio_response).decode('utf-8')
            
            # Send response back to client
            emit('ai_response', {
                'transcript': transcript,
                'response_text': response_text,
                'audio': f"data:audio/mp3;base64,{audio_b64}"
            })
    
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
