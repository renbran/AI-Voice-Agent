#!/usr/bin/env python3
"""
Test script for wake word functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_wake_word():
    """Test the wake word detection"""
    print("🎤 Testing Wake Word Detection for AI Voice Agent")
    print("=" * 50)
    
    try:
        # Test speech recognition import
        import speech_recognition as sr
        print("✅ SpeechRecognition library installed")
        
        # Test microphone access
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        print("✅ Microphone access available")
        
        # Test ambient noise adjustment
        print("🎤 Testing microphone calibration...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
        print("✅ Microphone calibration successful")
        
        # Test wake word detection
        print("\n🎯 Wake Word Test")
        print("Say one of these wake words:")
        print("- 'Hey James'")
        print("- 'James'") 
        print("- 'Hello James'")
        print("- 'Hi James'")
        print("\nListening for 10 seconds...")
        
        wake_words = ["hey james", "james", "hello james", "hi james"]
        
        with microphone as source:
            try:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                text = recognizer.recognize_google(audio).lower()
                print(f"🎧 You said: '{text}'")
                
                # Check for wake words
                wake_word_detected = False
                for wake_word in wake_words:
                    if wake_word in text:
                        print(f"🎯 ✅ Wake word detected: '{wake_word}'!")
                        wake_word_detected = True
                        break
                
                if not wake_word_detected:
                    print("❌ No wake word detected in your speech")
                    
            except sr.WaitTimeoutError:
                print("⏰ No speech detected within 10 seconds")
            except sr.UnknownValueError:
                print("❌ Could not understand the speech")
            except sr.RequestError as e:
                print(f"❌ Speech recognition service error: {e}")
        
        print("\n🎉 Wake word detection test completed!")
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install SpeechRecognition")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_wake_word()
