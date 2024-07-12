from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
import os
from uuid import uuid4

app = FastAPI()

# List of languages supported by gTTS
SUPPORTED_LANGUAGES = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'ar': 'Arabic', 'hy': 'Armenian',
    'ca': 'Catalan', 'zh': 'Chinese', 'zh-cn': 'Chinese (Mandarin/China)',
    'zh-tw': 'Chinese (Mandarin/Taiwan)', 'zh-yue': 'Chinese (Cantonese)',
    'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch', 'en': 'English',
    'en-au': 'English (Australia)', 'en-uk': 'English (United Kingdom)',
    'en-us': 'English (United States)', 'eo': 'Esperanto', 'fi': 'Finnish',
    'fr': 'French', 'de': 'German', 'el': 'Greek', 'ht': 'Haitian Creole',
    'hi': 'Hindi', 'hu': 'Hungarian', 'is': 'Icelandic', 'id': 'Indonesian',
    'it': 'Italian', 'ja': 'Japanese', 'ko': 'Korean', 'la': 'Latin', 'lv': 'Latvian',
    'mk': 'Macedonian', 'no': 'Norwegian', 'pl': 'Polish', 'pt': 'Portuguese',
    'pt-br': 'Portuguese (Brazil)', 'ro': 'Romanian', 'ru': 'Russian', 'sr': 'Serbian',
    'sk': 'Slovak', 'es': 'Spanish', 'es-es': 'Spanish (Spain)', 'es-us': 'Spanish (United States)',
    'sw': 'Swahili', 'sv': 'Swedish', 'ta': 'Tamil', 'th': 'Thai', 'tr': 'Turkish',
    'vi': 'Vietnamese', 'cy': 'Welsh'
}

# Reverse mapping for converting language names to codes
LANG_NAME_TO_CODE = {v.upper(): k for k, v in SUPPORTED_LANGUAGES.items()}

# CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.post("/convert")
async def convert_text_to_speech(request: Request):
    data = await request.json()
    text = data.get("text")
    lang = data.get("lang")

    if not text or not lang:
        raise HTTPException(status_code=400, detail="Text and language must be provided")

    # Check if lang is a supported language name and convert it to code if necessary
    if lang.upper() in LANG_NAME_TO_CODE:
        lang = LANG_NAME_TO_CODE[lang.upper()]

    # Validate if the resulting language code is supported
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Language '{lang}' is not supported")

    tts = gTTS(text=text, lang=lang)
    filename = f"{uuid4()}.mp3"
    tts.save(filename)
    
    return FileResponse(filename, media_type="audio/mpeg", filename=filename)

@app.on_event("shutdown")
def cleanup_files():
    for file in os.listdir('.'):
        if file.endswith(".mp3"):
            os.remove(file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
