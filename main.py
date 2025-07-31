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

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CREDS_B64 = os.getenv("GOOGLE_CREDS_B64")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Инициализация Telegram-бота
bot = telebot.TeleBot(BOT_TOKEN)

# Декодирование и сохранение Google credentials в файл
with open("creds.json", "w") as f:
    f.write(base64.b64decode(GOOGLE_CREDS_B64).decode("utf-8"))

# Авторизация Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client_gs = gspread.authorize(creds)
spreadsheet = client_gs.open_by_key(SPREADSHEET_ID)

# Подключение к OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Обработка входящих сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip()

    # Отправка запроса в OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — ассистент по задачам и дедлайнам, работаешь с Google Таблицей, структурируешь мысли и задачи."},
                {"role": "user", "content": text}
            ]
        )
        gpt_response = response.choices[0].message.content.strip()
    except Exception as e:
        gpt_response = f"Ошибка при запросе к OpenAI: {e}"

    bot.send_message(message.chat.id, gpt_response)

# Фоновый запуск бота
threading.Thread(target=lambda: bot.polling(none_stop=True)).start()

# Flask-сервер для Render (если Web Service)
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
