#!/usr/bin/env python3
"""
Microphone and API Diagnostic Tool
Tests microphone access and API connectivity
"""

import os
import sys
from dotenv import load_dotenv

def test_microphone():
    """Test microphone access"""
    print("🎤 Testing Microphone Access...")
    
    try:
        import speech_recognition as sr
        import pyaudio
        
        # Test PyAudio
        p = pyaudio.PyAudio()
        
        # List available audio devices
        print("📋 Available Audio Devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  {i}: {info['name']} (Input channels: {info['maxInputChannels']})")
        
        # Test default microphone
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("🎤 Testing default microphone...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Microphone access successful!")
        p.terminate()
        return True
        
    except ImportError as e:
        print(f"❌ Missing audio library: {e}")
        return False
    except Exception as e:
        print(f"❌ Microphone error: {e}")
        return False

def test_api_keys():
    """Test API key validity"""
    print("\n🔑 Testing API Keys...")
    
    # Force reload environment
    load_dotenv(override=True)
    
    openai_key = os.getenv('OPENAI_API_KEY')
    deepgram_key = os.getenv('DEEPGRAM_API_KEY')
    
    print(f"📊 OpenAI Key: {len(openai_key) if openai_key else 0} characters")
    print(f"📊 Deepgram Key: {len(deepgram_key) if deepgram_key else 0} characters")
    
    # Test OpenAI
    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        
        # Simple test
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        print("✅ OpenAI API key working!")
        
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False
    
    # Test Deepgram
    try:
        import requests
        
        url = 'https://api.deepgram.com/v1/speak?model=aura-helios-en'
        headers = {
            "Authorization": f"Token {deepgram_key}",
            "Content-Type": "application/json"
        }
        payload = {"text": "API test"}
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("✅ Deepgram API key working!")
        else:
            print(f"❌ Deepgram API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Deepgram API error: {e}")
        return False
    
    return True

def test_environment():
    """Test system environment"""
    print("\n🖥️ Testing System Environment...")
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check working directory
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check .env file
    env_file = os.path.join(os.getcwd(), '.env')
    if os.path.exists(env_file):
        print(f"✅ .env file found: {env_file}")
        with open(env_file, 'r') as f:
            lines = f.readlines()
            print(f"📄 .env file has {len(lines)} lines")
    else:
        print("❌ .env file not found!")
        return False
    
    return True

def main():
    """Run all diagnostics"""
    print("🔧 AI Voice Agent Diagnostic Tool")
    print("=" * 50)
    
    # Test environment
    if not test_environment():
        print("\n❌ Environment test failed!")
        return
    
    # Test microphone
    if not test_microphone():
        print("\n❌ Microphone test failed!")
        print("💡 Try: pip install pyaudio SpeechRecognition")
        return
    
    # Test API keys
    if not test_api_keys():
        print("\n❌ API key test failed!")
        print("💡 Check your .env file and API keys")
        return
    
    print("\n🎉 All diagnostics passed!")
    print("✅ Your AI Voice Agent should work properly now.")
    print("\n🚀 Try running: python app.py")

if __name__ == "__main__":
    main()
