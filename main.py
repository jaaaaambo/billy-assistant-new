import os
import base64
import json
import gspread
import telebot
import threading
from flask import Flask
from datetime import datetime
import openai
from oauth2client.service_account import ServiceAccountCredentials

# Проверка переменных окружения
print("=== Запуск main.py ===")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CREDS_B64 = os.getenv("GOOGLE_CREDS_B64")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

if BOT_TOKEN: print("BOT_TOKEN: ✅")
if OPENAI_API_KEY: print("OPENAI_API_KEY: ✅")
if GOOGLE_CREDS_B64: print("GOOGLE_CREDS_B64 получено: ✅")
if SPREADSHEET_ID: print("SPREADSHEET_ID:", SPREADSHEET_ID)

# Инициализация Telegram-бота
bot = telebot.TeleBot(BOT_TOKEN)
print("✅ Telegram bot initialized")

# Декодирование и сохранение Google credentials в файл
with open("creds.json", "w") as f:
    f.write(base64.b64decode(GOOGLE_CREDS_B64).decode("utf-8"))
print("✅ Google credentials decoded and saved")

# Авторизация Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client_gs = gspread.authorize(creds)
spreadsheet = client_gs.open_by_key(SPREADSHEET_ID)
print("✅ Connected to Google Sheets")

# Подключение к OpenAI
openai.api_key = OPENAI_API_KEY
print("✅ OpenAI key set")

# Обработка входящих сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip()

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — ассистент по задачам и дедлайнам, работаешь с Google Таблицей, структурируешь мысли и задачи."},
                {"role": "user", "content": text}
            ]
        )
        gpt_response = response.choices[0].message["content"].strip()
    except Exception as e:
        gpt_response = f"Ошибка при запросе к OpenAI: {e}"

    bot.send_message(message.chat.id, gpt_response)

# Фоновый запуск Telegram-бота
threading.Thread(target=lambda: bot.polling(none_stop=True)).start()

# Flask-сервер для Render (если используется как Web Service)
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
