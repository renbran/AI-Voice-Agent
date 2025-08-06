# 📱 Mobile AI Voice Agent Setup Guide

## Overview
This guide shows you how to run your AI Voice Agent on mobile devices with **voice wake-up functionality** that works on any smartphone or tablet.

## 🚀 Quick Mobile Setup

### Option 1: HTTPS Mobile App (Recommended - Full Voice Wake-Up)

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install cryptography  # For HTTPS certificates
```

#### 2. Run the HTTPS Mobile Server
```bash
python simple_https_app.py
```

#### 3. Access on Mobile with HTTPS
- **HTTPS URL**: `https://192.168.0.161:5443`
- **Accept security warning** (self-signed certificate)
- **Enable microphone** when prompted
- **Say "Hey James"** for voice wake-up!

### Option 2: Basic HTTP Mobile App

#### 1. Run the Basic Mobile Server
```bash
python mobile_app.py
```

#### 2. Access on Mobile
- **HTTP URL**: `http://192.168.0.161:5000`
- **Limited microphone support** on some browsers

## 🌐 Mobile Voice Wake-Up Features

### ✅ What Works on Mobile (HTTPS)

- **🎤 Voice Wake-Up**: Say "Hey James" to activate automatically
- **👂 Always Listening**: Continuous wake word detection
- **🗣️ Full Conversation**: James responds with voice
- **📱 Touch-Friendly**: Large buttons, mobile-optimized interface
- **🔒 Secure**: HTTPS required for microphone access
- **🌍 Universal**: Works on iPhone Safari, Android Chrome, tablets

### 🎯 Mobile Voice Experience

1. **Open HTTPS URL** in mobile browser
2. **Accept security warning** (self-signed certificate)
3. **Enable microphone access** when prompted
4. **Say "Hey James"** - automatic wake word detection
5. **Have conversation** - James responds with voice
6. **Automatic return** to wake word mode after each chat

## 📱 Other Mobile Options

### Option 2: Progressive Web App (PWA)
Make it installable on mobile home screen:

```bash
# Add to mobile_app.py for PWA support
@app.route('/manifest.json')
def manifest():
    return {
        "name": "AI Voice Agent - James",
        "short_name": "Voice Agent",
        "description": "Talk to James, your AI restaurant assistant",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#667eea",
        "theme_color": "#667eea",
        "icons": [
            {
                "src": "/static/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            }
        ]
    }
```

### Option 3: Native Mobile App (Advanced)
For a full native app experience:

#### React Native + Expo:
```bash
# Create React Native app
npx create-expo-app VoiceAgent
cd VoiceAgent

# Install voice libraries
expo install expo-av expo-speech
npm install socket.io-client
```

#### Flutter (Cross-platform):
```dart
// Add to pubspec.yaml
dependencies:
  speech_to_text: ^6.6.0
  flutter_tts: ^3.8.5
  socket_io_client: ^2.0.3+1
```

## 🔧 Network Setup for Mobile Access

### Find Your Computer's IP Address:
```bash
# Windows
ipconfig
# Look for "IPv4 Address" (e.g., 192.168.1.100)

# Mac/Linux  
ifconfig
# Look for inet address
```

### Allow Mobile Access:
1. **Run mobile app**: `python mobile_app.py`
2. **Note the IP**: Your computer shows IP like `192.168.1.100`
3. **On mobile**: Open browser, go to `http://192.168.1.100:5000`
4. **Grant microphone permission** when prompted

## 🌟 Mobile Demo Instructions

### What to Try on Mobile:
1. **"Hi James, I'd like to make a reservation for 4 people tonight at 7 PM"**
2. **"What's on your menu today?"**
3. **"I want to order 2 chicken egg rolls for delivery"**
4. **"Can you help me place an order?"**

### Expected Mobile Experience:
- ✅ **Tap to talk** - Large, responsive button
- ✅ **Clear audio** - James responds through phone speakers
- ✅ **Visual feedback** - See conversation and status
- ✅ **Menu display** - Quick reference to available items
- ✅ **Responsive design** - Works on any screen size

## 🔥 Production Mobile Deployment

### For Public Mobile Access:

#### 1. Deploy to Cloud (Heroku/Railway/Render):
```bash
# Create Procfile
echo "web: python mobile_app.py" > Procfile

# Deploy to Heroku
heroku create your-voice-agent
git push heroku main
```

#### 2. Add HTTPS for Mobile:
Mobile browsers require HTTPS for microphone access in production.

#### 3. Set Environment Variables:
```bash
# Set in production
DEEPGRAM_API_KEY=your_key
OPENAI_API_KEY=your_key
```

## 📊 Mobile vs Desktop Comparison

| Feature | Desktop App | Mobile Web | Native App |
|---------|-------------|------------|------------|
| Setup | ✅ Easy | ✅ Easy | ⚠️ Complex |
| Voice Quality | ✅ Excellent | ✅ Good | ✅ Excellent |
| Portability | ❌ No | ✅ Yes | ✅ Yes |
| App Store | ❌ No | ❌ No | ✅ Yes |
| Installation | ✅ Local | 🌐 Browser | 📱 Store |

## 🎉 Ready to Test Mobile?

Your mobile voice agent is ready! The web version gives you:
- **No installation required** on mobile
- **Works on any smartphone/tablet**
- **Same AI personality (James)**
- **Full voice conversation capability**
- **Touch-optimized interface**

Start the mobile server and try it on your phone! 📱🎤
