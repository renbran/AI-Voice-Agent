"""
HTTPS Mobile Web Interface for AI Voice Agent
Mobile browsers require HTTPS for microphone access
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
import ssl

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
print(f"✅ HTTPS Mobile API Keys loaded: Deepgram ({len(DEEPGRAM_API_KEY)} chars), OpenAI ({len(OPENAI_API_KEY)} chars)")

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

# Deepgram configuration
DEEPGRAM_TTS_URL = 'https://api.deepgram.com/v1/speak?model=aura-helios-en'
DEEPGRAM_STT_URL = 'https://api.deepgram.com/v1/listen'

def get_deepgram_response(audio_data):
    """Send audio to Deepgram for speech-to-text"""
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/wav"
    }
    
    params = {
        "model": "nova-2",
        "smart_format": "true"
    }
    
    try:
        response = requests.post(DEEPGRAM_STT_URL, headers=headers, params=params, data=audio_data)
        response.raise_for_status()
        result = response.json()
        transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript
    except Exception as e:
        print(f"❌ Deepgram STT error: {e}")
        return None

def get_openai_response(messages):
    """Get response from OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return "I'm having trouble connecting right now. Could you try again?"

def synthesize_audio(text):
    """Convert text to speech using Deepgram"""
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {"text": text}
    
    try:
        response = requests.post(DEEPGRAM_TTS_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"❌ Deepgram TTS error: {e}")
        return None

@app.route('/')
def index():
    return render_template('simple_voice.html')

@socketio.on('wake_word_check')
def handle_wake_word(data):
    try:
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio'].split(',')[1])
        
        # Get transcription from Deepgram
        transcript = get_deepgram_response(audio_data)
        
        if transcript:
            transcript_lower = transcript.lower()
            wake_words = ['hey james', 'james', 'hello james', 'hi james', 'jarvis']
            
            for wake_word in wake_words:
                if wake_word in transcript_lower:
                    print(f"🎯 Wake word detected: '{wake_word}' in '{transcript}'")
                    emit('wake_word_detected', {'detected': True, 'transcript': transcript})
                    return
        
        emit('wake_word_detected', {'detected': False})
        
    except Exception as e:
        print(f"❌ Wake word check error: {e}")
        emit('error', {'message': 'Wake word detection failed'})

@socketio.on('james_activation')
def handle_james_activation(data):
    try:
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio'].split(',')[1])
        
        # Get transcription from Deepgram
        transcript = get_deepgram_response(audio_data)
        
        if not transcript:
            emit('error', {'message': 'Could not understand audio'})
            return
            
        emit('transcription', {'text': transcript})
        
        # Add to conversation memory
        conversation_memory.append({"role": "user", "content": transcript})
        
        # Get AI response
        messages = [{"role": "system", "content": prompt}]
        messages.extend(conversation_memory[-10:])  # Keep last 10 messages
        
        ai_response = get_openai_response(messages)
        conversation_memory.append({"role": "assistant", "content": ai_response})
        
        # Convert response to speech
        audio_content = synthesize_audio(ai_response)
        
        if audio_content:
            # Convert to base64 for transmission
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            emit('ai_response', {
                'message': ai_response,
                'audio': f"data:audio/mp3;base64,{audio_base64}"
            })
        else:
            emit('ai_response', {'message': ai_response})
        
    except Exception as e:
        print(f"❌ James activation error: {e}")
        emit('error', {'message': 'Processing failed'})

if __name__ == '__main__':
    print("🚀 Starting HTTPS James Voice Agent...")
    print("📱 Access on mobile: https://192.168.0.161:5443")
    print("⚠️  You'll see a security warning - click 'Advanced' → 'Proceed'")
    
    # Create SSL context for HTTPS
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    socketio.run(app, host='0.0.0.0', port=5443, debug=True, ssl_context=context)
