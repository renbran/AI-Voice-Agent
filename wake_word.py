"""
Wake Word Detection for AI Voice Agent
Adds "Hey James" wake word functionality
"""

import pvporcupine
import pyaudio
import struct
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

class WakeWordDetector:
    def __init__(self, wake_word_callback, access_key=None):
        """
        Initialize wake word detector
        wake_word_callback: Function to call when wake word is detected
        access_key: Picovoice access key (get free from https://console.picovoice.ai/)
        """
        self.wake_word_callback = wake_word_callback
        self.access_key = access_key or os.getenv('PICOVOICE_ACCESS_KEY')
        self.is_listening = False
        self.audio_stream = None
        self.porcupine = None
        
        # Wake words available: "hey google", "hey siri", "jarvis", "computer", "americano"
        # We'll use "jarvis" as it's closest to "James" and freely available
        self.wake_words = ["jarvis"]  # You can add more wake words here
        
    def start_listening(self):
        """Start listening for wake words"""
        if self.is_listening:
            return
            
        try:
            # Initialize Porcupine wake word engine
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=self.wake_words
            )
            
            # Initialize audio stream
            self.audio_stream = pyaudio.PyAudio().open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            
            self.is_listening = True
            print("🎤 Wake word detection started. Say 'Jarvis' to activate James!")
            
            # Start listening thread
            threading.Thread(target=self._listen_for_wake_word, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Wake word detection failed to start: {e}")
            print("💡 Install Picovoice: pip install pvporcupine")
            print("💡 Get free access key: https://console.picovoice.ai/")
    
    def stop_listening(self):
        """Stop listening for wake words"""
        self.is_listening = False
        if self.audio_stream:
            self.audio_stream.close()
        if self.porcupine:
            self.porcupine.delete()
        print("🔇 Wake word detection stopped")
    
    def _listen_for_wake_word(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                # Check for wake word
                wake_word_index = self.porcupine.process(pcm)
                
                if wake_word_index >= 0:
                    print(f"🎯 Wake word detected: {self.wake_words[wake_word_index]}")
                    self.wake_word_callback()
                    # Brief pause after detection
                    time.sleep(1)
                    
            except Exception as e:
                if self.is_listening:
                    print(f"❌ Wake word detection error: {e}")
                break

# Alternative: Simple keyword detection using speech recognition
class SimpleWakeWordDetector:
    def __init__(self, wake_word_callback, wake_words=None):
        """
        Simple wake word detector using continuous speech recognition
        wake_words: List of wake words (default: ["hey james", "james", "hello james"])
        """
        self.wake_word_callback = wake_word_callback
        self.wake_words = wake_words or ["hey james", "james", "hello james", "jarvis"]
        self.is_listening = False
        
    def start_listening(self):
        """Start simple wake word detection"""
        if self.is_listening:
            return
            
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            print("🎤 Calibrating microphone for wake word detection...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            
            self.is_listening = True
            print(f"🎤 Simple wake word detection started. Say: {', '.join(self.wake_words)}")
            
            # Start listening thread
            threading.Thread(target=self._listen_for_wake_word_simple, daemon=True).start()
            
        except ImportError:
            print("❌ speech_recognition not installed. Install with: pip install SpeechRecognition")
        except Exception as e:
            print(f"❌ Simple wake word detection failed: {e}")
    
    def stop_listening(self):
        """Stop wake word detection"""
        self.is_listening = False
        print("🔇 Simple wake word detection stopped")
    
    def _listen_for_wake_word_simple(self):
        """Simple wake word detection loop"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for 2 seconds, then process
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                try:
                    # Use Google's free speech recognition
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"🎧 Heard: {text}")
                    
                    # Check if any wake word is in the recognized text
                    for wake_word in self.wake_words:
                        if wake_word.lower() in text:
                            print(f"🎯 Wake word detected: {wake_word}")
                            self.wake_word_callback()
                            time.sleep(2)  # Pause after activation
                            break
                            
                except sr.UnknownValueError:
                    # Speech not recognized, continue listening
                    pass
                except sr.RequestError as e:
                    print(f"❌ Speech recognition error: {e}")
                    time.sleep(1)
                    
            except sr.WaitTimeoutError:
                # Timeout, continue listening
                pass
            except Exception as e:
                if self.is_listening:
                    print(f"❌ Wake word error: {e}")
                time.sleep(1)
