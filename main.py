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

# Декодирование Google credentials
with open("creds.json", "w") as f:
    f.write(base64.b64decode(GOOGLE_CREDS_B64).decode("utf-8"))

# Авторизация Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
gs_client = gspread.authorize(creds)
spreadsheet = gs_client.open_by_key(SPREADSHEET_ID)
sheet = spreadsheet.sheet1  # первая вкладка

# Подключение к OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Функция для добавления задачи в таблицу
def add_task_to_sheet(text):
    today = datetime.today().strftime("%Y-%m-%d")
    row = [text, "🟡 В работе", today, ""]
    sheet.append_row(row)

# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip()

    # Отправка в OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — ассистент по задачам. Определи, является ли сообщение задачей. Если да — добавь в таблицу."},
                {"role": "user", "content": text}
            ]
        )
        gpt_response = response.choices[0].message.content.strip()
    except Exception as e:
        gpt_response = f"❌ Ошибка при запросе к OpenAI: {e}"
        bot.send_message(message.chat.id, gpt_response)
        return

    # Попробуем понять, нужно ли добавить в таблицу
    if "добавь в таблицу" in gpt_response.lower() or "я добавил" in gpt_response.lower():
        try:
            add_task_to_sheet(text)
            gpt_response += "\n✅ Задача добавлена в таблицу."
        except Exception as e:
            gpt_response += f"\n❌ Не удалось добавить в таблицу: {e}"

    bot.send_message(message.chat.id, gpt_response)

# Flask для Render (Web Service)
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Бот работает."

# Запуск
if __name__ == "__main__":
    print("=== Запуск main.py ===")
    print("BOT_TOKEN:", "✅" if BOT_TOKEN else "❌")
    print("OPENAI_API_KEY:", "✅" if OPENAI_API_KEY else "❌")
    print("GOOGLE_CREDS_B64 получено:", "✅" if GOOGLE_CREDS_B64 else "❌")
    print("SPREADSHEET_ID:", SPREADSHEET_ID)

    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
