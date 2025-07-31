import os
import telebot
import openai
import gspread
import base64
import json

from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Фиктивный web server для Render
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Running..."

# Переменные окружения
TELEGRAM_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CREDS_B64 = os.getenv("GOOGLE_CREDS_B64")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Декодируем Google credentials
creds_json_path = "google_creds.json"
with open(creds_json_path, "w") as f:
    f.write(base64.b64decode(GOOGLE_CREDS_B64).decode("utf-8"))

# Подключаемся к таблице
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json_path, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)
sheet = spreadsheet.sheet1

# OpenAI
openai.api_key = OPENAI_API_KEY

# Telegram bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я твой ассистент. Напиши мне задачу или мысль.")

@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    text = message.text.strip()

    # Отправка в GPT
    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": text}]
    )

    reply = gpt_response.choices[0].message.content.strip()
    bot.send_message(message.chat.id, reply)

    # Сохраняем в Google Таблицу
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, message.chat.username or "", text, reply])

# Запуск Telegram-бота
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host="0.0.0.0", port=10000)
