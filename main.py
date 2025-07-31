import os
import base64
import json
import gspread
import telebot
import threading
from flask import Flask
from datetime import datetime
from openai import OpenAI
from oauth2client.service_account import ServiceAccountCredentials

print("=== Запуск main.py ===")

# Получение переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CREDS_B64 = os.getenv("GOOGLE_CREDS_B64")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

print("BOT_TOKEN:", "✅" if BOT_TOKEN else "❌")
print("OPENAI_API_KEY:", "✅" if OPENAI_API_KEY else "❌")
print("GOOGLE_CREDS_B64 получено:", "✅" if GOOGLE_CREDS_B64 else "❌")
print("SPREADSHEET_ID:", SPREADSHEET_ID or "❌")

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)
print("✅ Telegram bot initialized")

# Сохранение Google credentials в файл
with open("creds.json", "w") as f:
    f.write(base64.b64decode(GOOGLE_CREDS_B64).decode("utf-8"))
print("✅ Google credentials decoded and saved")

# Подключение к Google Таблице
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client_gs = gspread.authorize(creds)
spreadsheet = client_gs.open_by_key(SPREADSHEET_ID)
print("✅ Connected to Google Sheets")

# OpenAI клиент
client = OpenAI(api_key=OPENAI_API_KEY)
print("✅ OpenAI key set")

# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — ИИ-ассистент. Помогаешь вести задачи и мысли, работаешь с Google Таблицей и дедлайнами."},
                {"role": "user", "content": text}
            ]
        )
        gpt_response = response.choices[0].message.content.strip()
    except Exception as e:
        gpt_response = f"Ошибка при запросе к OpenAI: {e}"

    bot.send_message(message.chat.id, gpt_response)

# Запуск бота в отдельном потоке
threading.Thread(target=lambda: bot.polling(none_stop=True)).start()

# Фейковый сервер Flask для Render Web Service
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот Billy работает ✅"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
