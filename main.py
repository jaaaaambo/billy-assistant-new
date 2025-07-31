import os
import json
import base64
import gspread
import telebot
import threading
from flask import Flask
from openai import OpenAI

# Распаковка Google credentials
creds_b64 = os.getenv("GOOGLE_CREDS_B64")
with open("credentials.json", "w") as f:
    f.write(base64.b64decode(creds_b64).decode("utf-8"))

# Подключение к Google Sheets
gc = gspread.service_account(filename="credentials.json")
spreadsheet_id = os.getenv("SPREADSHEET_ID")
spreadsheet = gc.open_by_key(spreadsheet_id)
sheet_tasks = spreadsheet.worksheet("Задачи")
sheet_thoughts = spreadsheet.worksheet("Мысли")

# Инициализация Telegram-бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Инициализация OpenAI клиента
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_input = message.text

    # Обращение к OpenAI
    chat_response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_input}]
    )
    reply = chat_response.choices[0].message.content.strip()
    bot.send_message(message.chat.id, reply)

# Flask-приложение для фиктивного порта
app = Flask(__name__)

@app.route("/")
def index():
    return "Billy Assistant is running."

# Запуск
if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
