from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)

app = FastAPI()

# ===== 요청/응답 모델 =====
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


# ===== Gemini 호출 =====
async def call_gemini(user_message: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    system_prompt = (
        "너는 판타지 RPG 게임의 NPC다. "
        "대답은 1~2문장으로 간결하게 한다."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {"text": user_message}
                ]
            }
        ]
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            GEMINI_URL,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]


# ===== Unity에서 호출하는 API =====
@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply = await call_gemini(req.message)
    return ChatResponse(reply=reply)