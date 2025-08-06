"""
Simple HTTPS Mobile Voice Interface without SocketIO
Uses regular HTTPS with fetch API for better mobile compatibility
"""

from flask import Flask, render_template, request, jsonify
import base64
import openai
import os
from dotenv import load_dotenv
import requests
import ssl

# Force load environment variables
load_dotenv(override=True)

app = Flask(__name__)

# Initialize API keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')

if not OPENAI_API_KEY or not DEEPGRAM_API_KEY:
    print("❌ Missing API keys")
    exit(1)

client = openai.OpenAI(api_key=OPENAI_API_KEY)
print(f"✅ HTTPS API Keys loaded: Deepgram ({len(DEEPGRAM_API_KEY)} chars), OpenAI ({len(OPENAI_API_KEY)} chars)")

# Restaurant prompt
prompt = """You are James, a friendly AI restaurant assistant. Keep responses short and conversational.

Menu Items:
- Roast Pork Egg Roll (3pcs) - $5.25
- Vegetable Spring Roll (3pcs) - $5.25  
- Chicken Egg Roll (3pcs) - $5.25
- BBQ Chicken - $7.75

Help with reservations and orders. Be friendly and proactive."""

conversation_memory = []

# Deepgram URLs
DEEPGRAM_STT_URL = 'https://api.deepgram.com/v1/listen'
DEEPGRAM_TTS_URL = 'https://api.deepgram.com/v1/speak?model=aura-helios-en'

def get_deepgram_response(audio_data):
    """Send audio to Deepgram for speech-to-text"""
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/webm"  # Explicitly set WebM for browser compatibility
    }
    
    params = {
        "model": "nova-2",
        "smart_format": "true",
        "punctuate": "true",
        "interim_results": "false"
    }
    
    try:
        print(f"📤 Sending {len(audio_data)} bytes to Deepgram...")
        response = requests.post(DEEPGRAM_STT_URL, headers=headers, params=params, data=audio_data)
        
        if response.status_code != 200:
            print(f"❌ Deepgram HTTP {response.status_code}: {response.text}")
            print(f"📋 Request headers: {headers}")
            print(f"📋 Request params: {params}")
            return None
            
        result = response.json()
        if 'results' in result and result['results']['channels']:
            transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
            print(f"✅ Deepgram transcript: '{transcript}'")
            return transcript
        else:
            print(f"❌ Unexpected Deepgram response structure: {result}")
            return None
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
        return "I'm having trouble right now. Could you try again?"

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
    return render_template('https_voice.html')

@app.route('/wake_word_check', methods=['POST'])
def wake_word_check():
    try:
        data = request.json
        audio_data = base64.b64decode(data['audio'].split(',')[1])
        
        transcript = get_deepgram_response(audio_data)
        
        if transcript:
            transcript_lower = transcript.lower()
            wake_words = ['hey james', 'james', 'hello james', 'hi james']
            
            for wake_word in wake_words:
                if wake_word in transcript_lower:
                    print(f"🎯 Wake word detected: '{wake_word}' in '{transcript}'")
                    return jsonify({'detected': True, 'transcript': transcript})
        
        return jsonify({'detected': False})
        
    except Exception as e:
        print(f"❌ Wake word check error: {e}")
        return jsonify({'error': 'Wake word detection failed'}), 500

@app.route('/voice_chat', methods=['POST'])
def voice_chat():
    try:
        data = request.json
        audio_data = base64.b64decode(data['audio'].split(',')[1])
        
        transcript = get_deepgram_response(audio_data)
        
        if not transcript:
            return jsonify({'error': 'Could not understand audio'}), 400
        
        # Add to conversation memory
        conversation_memory.append({"role": "user", "content": transcript})
        
        # Get AI response
        messages = [{"role": "system", "content": prompt}]
        messages.extend(conversation_memory[-10:])
        
        ai_response = get_openai_response(messages)
        conversation_memory.append({"role": "assistant", "content": ai_response})
        
        # Convert response to speech
        audio_content = synthesize_audio(ai_response)
        
        result = {
            'transcript': transcript,
            'response': ai_response
        }
        
        if audio_content:
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            result['audio'] = f"data:audio/mp3;base64,{audio_base64}"
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Voice chat error: {e}")
        return jsonify({'error': 'Processing failed'}), 500

if __name__ == '__main__':
    print("🚀 Starting HTTPS James Voice Agent...")
    print("📱 Access on mobile: https://192.168.0.161:5443")
    print("⚠️  Accept security warning to enable microphone")
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('cert.pem', 'key.pem')
    
    app.run(host='0.0.0.0', port=5443, debug=True, ssl_context=context)
