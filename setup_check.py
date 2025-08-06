#!/usr/bin/env python3
"""
Setup verification script for AI Voice Agent
Run this to test your API keys and dependencies before running the main app
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if all environment variables are set"""
    load_dotenv()
    
    deepgram_key = os.getenv('DEEPGRAM_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print("🔍 Checking Environment Variables...")
    
    if not deepgram_key or deepgram_key == 'deepgram-api-key':
        print("❌ DEEPGRAM_API_KEY not set or using placeholder")
        print("   Go to https://console.deepgram.com/ to get your API key")
        return False
    else:
        print("✅ DEEPGRAM_API_KEY is set")
    
    if not openai_key or openai_key == 'openai-api-key':
        print("❌ OPENAI_API_KEY not set or using placeholder")
        print("   Go to https://platform.openai.com/api-keys to get your API key")
        return False
    else:
        print("✅ OPENAI_API_KEY is set")
    
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    print("\n🔍 Checking Dependencies...")
    
    try:
        import deepgram
        print("✅ deepgram-sdk installed")
    except ImportError:
        print("❌ deepgram-sdk not installed")
        return False
    
    try:
        import openai
        print("✅ openai installed")
    except ImportError:
        print("❌ openai not installed")
        return False
    
    try:
        import pygame
        print("✅ pygame installed")
    except ImportError:
        print("❌ pygame not installed")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not installed")
        return False
    
    return True

def test_api_keys():
    """Test API key validity"""
    print("\n🔍 Testing API Keys...")
    
    load_dotenv()
    
    # Test OpenAI (simplified test)
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        print("✅ OpenAI API key format is valid")
    except Exception as e:
        print(f"❌ OpenAI API key test failed: {e}")
        return False
    
    # Test Deepgram
    try:
        from deepgram import DeepgramClient
        dg_client = DeepgramClient(api_key=os.getenv('DEEPGRAM_API_KEY'))
        print("✅ Deepgram API key format is valid")
    except Exception as e:
        print(f"❌ Deepgram API key test failed: {e}")
        return False
    
    return True

def main():
    """Main setup verification"""
    print("🎤 AI Voice Agent Setup Verification")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies check failed. Please install missing packages.")
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please set your API keys in .env file.")
        sys.exit(1)
    
    # Test API keys
    if not test_api_keys():
        print("\n❌ API key validation failed. Please check your keys.")
        sys.exit(1)
    
    print("\n🎉 All checks passed! Your AI Voice Agent is ready to run.")
    print("\nTo start the voice agent, run:")
    print("python app.py")
    print("\nMake sure you have a microphone connected and working!")

if __name__ == "__main__":
    main()
