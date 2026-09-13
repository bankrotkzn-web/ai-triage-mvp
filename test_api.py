import requests

url = "http://localhost:8000/triage"
data = {
    "text": "У меня списали деньги за подписку дважды! Верните средства.",
    "channel": "email",
    "client_id": "user_123"
}

print("Отправляем запрос к ИИ...")
response = requests.post(url, json=data)
print("Ответ сервера:")
print(response.json())