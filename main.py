from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI
import os
from dotenv import load_dotenv
import time
from db import init_db, log_ticket

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
init_db() # Создаем БД при запуске

# Простейший rate limiter (словарь: client_id -> время последнего запроса)
RATE_LIMIT_STORE = {}

# Валидация входных данных
class TriageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    channel: str
    client_id: str

@app.post("/triage")
def triage_ticket(req: TriageRequest):
    # 1. Лимитирование запросов (не чаще 1 раза в минуту для client_id)
    current_time = time.time()
    last_request_time = RATE_LIMIT_STORE.get(req.client_id, 0)
    if current_time - last_request_time < 60:
        raise HTTPException(status_code=429, detail="Слишком много запросов. Подождите минуту.")
    RATE_LIMIT_STORE[req.client_id] = current_time

    # Дефолтные значения на случай сбоя
    category, draft_reply, confidence, escalate, error = "other", "Передано оператору.", "low", True, ""

    # 2. LLM обработка
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2, # Строгий режим по заданию
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Ты ассистент поддержки. Верни JSON с ключами: 'category' (billing/support/complaint/other), 'draft_reply' (1-6 предложений), 'confidence' (high/medium/low), 'escalate' (boolean). Если информации мало, ставь escalate: true."},
                {"role": "user", "content": f"Обращение: {req.text}"}
            ]
        )
        import json
        ai_data = json.loads(response.choices[0].message.content)
        category = ai_data.get("category", "other")
        draft_reply = ai_data.get("draft_reply", "Передано оператору.")
        confidence = ai_data.get("confidence", "low")
        escalate = ai_data.get("escalate", True)

    except Exception as e:
        error = str(e) # Сценарий "если все сломалось" отработал, переменные остались дефолтными

    # 3. Сохранение в БД
    log_ticket(req.client_id, req.channel, req.text, category, draft_reply, confidence, escalate, error)

    return {
        "category": category,
        "draft_reply": draft_reply,
        "confidence": confidence,
        "escalate": escalate
    }