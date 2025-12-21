from fastapi import FastAPI
from pydantic import BaseModel
import os
import google.generativeai as genai
import asyncio
import base64
import requests
import io
import json
import IPython.display as ipd
import IPython
import httpx
import soundfile as sf
import wave
import numpy as np

from dotenv import load_dotenv

load_dotenv()

OPENAPI_KEY = os.getenv("OPENAPI_KEY")
header = {'OPENAPI_KEY': OPENAPI_KEY} 
response = requests.get("https://openapi.ai.nc.com/tts/standard/v1/api/voices/varco",headers=header)
print("/api/voices/varco 보이스 화자 수: ",len(response.json()))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)


# API 키 설정
genai.configure(api_key=GEMINI_API_KEY)
# Gemini 모델 로드
model = genai.GenerativeModel('gemini-2.5-flash')


app = FastAPI()

# ===== 요청/응답 모델 =====
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

class SoundRequest(BaseModel):
    voice : str
    language : str 
    text : str   

class SoundResponse(BaseModel):
    soundWAV : str

# ===== VARCO VOICE 호출 ====
async def call_voice(soundData : SoundRequest) -> str:
    data = {
        "text": soundData.text,
        "language": soundData.language,
        "voice": soundData.voice,
        "properties": {
            "speed": 1,
            "pitch": 1
    },
        "n_fm_steps": 8,
        "seed": -1,
        "return_metadata": False
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openapi.ai.nc.com/tts/standard/v1/api/synthesize",
            headers=header,
            json=data
    )

    print("/api/synthesize 응답 상태 코드:", response.status_code)
    audio = response.json().get("audio")
    return audio


# ===== Gemini 호출 =====
async def call_gemini(user_message: str) -> str:
    response = await asyncio.to_thread(
        model.generate_content, user_message
    )
    return response.text


def float_wav_to_pcm16_base64(wav_bytes: bytes) -> str:
    # ✅ float32 WAV 읽기 (format 3 지원)
    audio, sample_rate = sf.read(
        io.BytesIO(wav_bytes),
        dtype="float32"
    )

    print(sample_rate)
    # mono 보장
    if audio.ndim > 1:
        audio = audio[:, 0]

    # float → int16
    audio = np.clip(audio, -1.0, 1.0)
    audio_int16 = (audio * 32767).astype(np.int16)

    # PCM16 WAV로 다시 쓰기
    out = io.BytesIO()
    sf.write(
        out,
        audio_int16,
        sample_rate,
        subtype="PCM_16",
        format="WAV"
    )

    return base64.b64encode(out.getvalue()).decode("utf-8")

@app.post("/api/voice", response_model=SoundResponse)
async def chat(req: SoundRequest):
    print("sound request")
    reply = await call_voice(req)

    wav_bytes = base64.b64decode(reply)
    result = float_wav_to_pcm16_base64(wav_bytes)

    return SoundResponse(soundWAV=result )

# ===== Unity에서 호출하는 API =====
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    print("Reply!")
    reply = await call_gemini(req.message)
    print(reply)
    return ChatResponse(reply=reply)