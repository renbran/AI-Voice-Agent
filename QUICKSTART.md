# 🎤 AI Voice Agent - Quick Start Guide

## Current Status ✅
- ✅ Virtual environment created and activated
- ✅ All dependencies installed
- ✅ OpenAI API key configured
- ⏳ **Need Deepgram API key**

## Next Steps

### 1. Get Deepgram API Key
1. Go to https://console.deepgram.com/
2. Sign up for a free account (you get $200 in free credits!)
3. Navigate to "API Keys" in the dashboard
4. Create a new API key
5. Copy the key

### 2. Update .env File
Replace the placeholder in your `.env` file:
```
DEEPGRAM_API_KEY=your-actual-deepgram-key-here
OPENAI_API_KEY=your-actual-openai-key-here
```

### 3. Verify Setup
Run the setup verification script:
```bash
python setup_check.py
```

### 4. Start the AI Voice Agent
Once everything is verified:
```bash
python app.py
```

## How It Works

Your AI Voice Agent "James" is a restaurant receptionist that can:
- **Take Table Reservations**: Ask for date, time, and number of people
- **Process Food Orders**: Help customers order from the menu
- **Handle Delivery**: Get delivery address and confirm timing

## Using the Voice Agent

1. **Start the app**: `python app.py`
2. **Speak naturally**: The agent will respond in real-time
3. **Press Enter**: To stop the recording and exit

## Menu Items Available
- Roast Pork Egg Roll (3pcs) - $5.25
- Vegetable Spring Roll (3pcs) - $5.25  
- Chicken Egg Roll (3pcs) - $5.25
- BBQ Chicken - $7.75

## Technical Details
- **Speech Recognition**: Deepgram Nova-2 model
- **AI Conversation**: OpenAI GPT-3.5-turbo
- **Text-to-Speech**: Deepgram Aura Helios voice
- **Audio**: Pygame for playback

## Troubleshooting

### Common Issues:
- **Microphone not working**: Check Windows microphone permissions
- **Audio playback issues**: Ensure speakers/headphones are working
- **API key errors**: Verify keys are correctly set in .env file
- **Network issues**: Check internet connection for API calls

### Need Help?
- Run `python setup_check.py` to diagnose issues
- Check the console output for error messages
- Ensure your microphone has proper permissions in Windows

## Ready to Test?
Once you have your Deepgram API key, you'll be ready to have voice conversations with your AI restaurant assistant! 🎉
