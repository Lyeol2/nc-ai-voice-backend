from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

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


# ===== Gemini 호출 =====
async def call_gemini(user_message: str) -> str:
    response = await model.generate_content(user_message)
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


# ===== Unity에서 호출하는 API =====
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    print("Reply!")
    reply = call_gemini(req.message)
    return ChatResponse(reply=reply)