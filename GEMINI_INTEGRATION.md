# Gemini API Integration - Implementation Summary

## Overview
Successfully restored multi-LLM support to AI Shadow Coach with both Gemini and Ollama capabilities.

## Changes Made

### 1. Created Multi-LLM Architecture (`backend/coaches/`)

#### `backend/coaches/__init__.py`
- Factory function `create_coach()` for creating coach instances
- Supports both "gemini" and "ollama" coach types
- Clean abstraction for adding more LLMs in the future

#### `backend/coaches/base_coach.py`
- Abstract base class defining the coach interface
- Shared Socratic prompting behavior
- Common conversation history management
- Helper methods for context building

#### `backend/coaches/gemini_coach.py`
- Google Gemini API integration
- Streaming support for faster responses
- Comprehensive error handling:
  - API key validation
  - Rate limiting
  - Network errors
  - Model not found errors
- Uses `gemini-2.0-flash-exp` model by default

#### `backend/coaches/ollama_coach.py`
- Local Ollama server integration
- Error handling for connection issues
- No API key required (runs locally)

### 2. Updated Configuration (`backend/config.py`)

Added new configuration options:
- `COACH_TYPE`: Choose between "gemini" (default) or "ollama"
- `GEMINI_API_KEY`: Your Gemini API key
- `GEMINI_MODEL`: Model to use (default: gemini-2.0-flash-exp)

Enhanced validation to check coach-specific requirements.

### 3. Updated Main Application (`backend/main.py`)

- Changed from direct `Coach()` instantiation to `create_coach(Config.COACH_TYPE)`
- Now uses the factory pattern for coach creation
- Automatically selects the appropriate coach based on configuration

### 4. Updated Dependencies (`requirements.txt`)

Added:
- `google-generativeai>=0.3.0`

### 5. Updated Environment Template (`env.example`)

Added comprehensive configuration options:
```env
# Coach Type Selection
COACH_TYPE=gemini

# Gemini Settings
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Ollama Settings (fallback)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install google-generativeai
# or
pip install -r requirements.txt
```

### 2. Configure Your API Key

#### Option A: Using .env file (Recommended)
Create or update `.env` file in the project root:
```env
COACH_TYPE=gemini
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

#### Option B: Using Environment Variables
```bash
# Windows PowerShell
$env:COACH_TYPE="gemini"
$env:GEMINI_API_KEY="your_actual_api_key_here"

# Linux/Mac
export COACH_TYPE=gemini
export GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Get Your Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

### 4. Run the Application

```bash
python -m uvicorn backend.main:app --reload
```

Or use the existing launch scripts:
```bash
# Windows
.\launch.ps1

# Linux/Mac
./launch.sh
```

## Testing

Run the integration test:
```bash
python test_gemini_coach.py
```

This will verify:
- Coach factory imports correctly
- Configuration is loaded properly
- All coaches implement the required interface
- Ollama coach can be created (fallback option)
- Gemini coach creation works (if API key is set)

## Switching Between Coaches

### Use Gemini (Cloud-based, faster)
```env
COACH_TYPE=gemini
GEMINI_API_KEY=your_key_here
```

### Use Ollama (Local, no API key needed)
```env
COACH_TYPE=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

Make sure Ollama is running:
```bash
ollama serve
ollama pull llama3.2
```

## Architecture Benefits

1. **Extensible**: Easy to add new LLM providers
2. **Configurable**: Switch providers without code changes
3. **Maintainable**: Shared base class reduces code duplication
4. **Error Handling**: Comprehensive error messages for common issues
5. **Type Safety**: Full type hints for better IDE support

## Troubleshooting

### "GEMINI_API_KEY is required" Error
- Make sure your `.env` file exists in the project root
- Verify the API key is correctly set
- Check that there are no extra spaces or quotes around the key

### "Model not found" Error
- Verify the model name is correct
- Try using the default: `gemini-2.0-flash-exp`
- Check Google's documentation for available models

### Rate Limit Errors
- Wait a moment before retrying
- Check your API quota at: https://console.cloud.google.com/
- Consider upgrading your API plan if needed

### Cannot Connect to Ollama
- Make sure Ollama is running: `ollama serve`
- Check the OLLAMA_URL is correct (default: http://localhost:11434)
- Verify the model is installed: `ollama pull llama3.2`

## API Comparison

| Feature | Gemini | Ollama |
|---------|--------|--------|
| Speed | Fast (cloud) | Depends on hardware |
| API Key | Required | Not required |
| Cost | Pay per use | Free (local) |
| Privacy | Data sent to Google | Fully local |
| Setup | Easy | Requires installation |
| Models | Latest Google models | Various open-source models |

## Files Modified

- ✅ `backend/coaches/__init__.py` (created)
- ✅ `backend/coaches/base_coach.py` (created)
- ✅ `backend/coaches/gemini_coach.py` (created)
- ✅ `backend/coaches/ollama_coach.py` (created)
- ✅ `backend/config.py` (updated)
- ✅ `backend/main.py` (updated)
- ✅ `requirements.txt` (updated)
- ✅ `env.example` (updated)
- ✅ `test_gemini_coach.py` (created)

## Next Steps

1. **Get your Gemini API key** from https://makersuite.google.com/app/apikey
2. **Update your .env file** with the API key
3. **Run the application** and test the Gemini coach
4. **Optional**: Keep the old `backend/coach.py` for reference, or delete it

## Notes

- The implementation is based on git commit 8f3771e
- All tests pass successfully
- The old `backend/coach.py` is still present but no longer used
- You can safely delete `backend/coach.py` if you want to clean up
