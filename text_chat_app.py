"""
Simple Text-Based Mobile Chat Interface for James AI
No microphone required - type to chat with James
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import openai
import os
from dotenv import load_dotenv

# Force load environment variables
load_dotenv(override=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'james-text-chat-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY not set")
    exit(1)

print(f"✅ Text Chat API Key loaded: OpenAI ({len(OPENAI_API_KEY)} chars)")

openai.api_key = OPENAI_API_KEY

# Restaurant prompt
prompt = """You are James, a friendly AI restaurant assistant. You help customers with:
1. Table reservations (ask for date, time, and number of people)
2. Taking food orders from our menu
3. Providing information about our restaurant

Menu Items:
- Roast Pork Egg Roll (3pcs) - $5.25
- Vegetable Spring Roll (3pcs) - $5.25  
- Chicken Egg Roll (3pcs) - $5.25
- BBQ Chicken - $7.75

Keep responses short, friendly, and conversational. Always be helpful and proactive."""

conversation_memory = []

@app.route('/')
def text_chat():
    return render_template('text_chat.html')

@socketio.on('send_message')
def handle_message(data):
    user_message = data['message']
    
    # Add to conversation memory
    conversation_memory.append({"role": "user", "content": user_message})
    
    try:
        # Get AI response
        messages = [{"role": "system", "content": prompt}]
        messages.extend(conversation_memory[-10:])  # Keep last 10 messages
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        conversation_memory.append({"role": "assistant", "content": ai_response})
        
        emit('ai_response', {'message': ai_response})
        
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        emit('ai_response', {'message': "I'm having trouble right now. Could you try again?"})

if __name__ == '__main__':
    print("🚀 Starting James Text Chat Server...")
    print("📱 Access on mobile: http://192.168.0.161:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
