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

# Проверка
print("=== Запуск main.py ===")
print(f"BOT_TOKEN: {'✅' if BOT_TOKEN else '❌'}")
print(f"OPENAI_API_KEY: {'✅' if OPENAI_API_KEY else '❌'}")
print(f"GOOGLE_CREDS_B64 получено: {'✅' if GOOGLE_CREDS_B64 else '❌'}")
print(f"SPREADSHEET_ID: {SPREADSHEET_ID}")

# Telegram-бот
bot = telebot.TeleBot(BOT_TOKEN)
print("✅ Telegram bot initialized")

# Декодируем Google credentials
with open("creds.json", "w") as f:
    f.write(base64.b64decode(GOOGLE_CREDS_B64).decode("utf-8"))
print("✅ Google credentials decoded and saved")

# Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client_gs = gspread.authorize(creds)
spreadsheet = client_gs.open_by_key(SPREADSHEET_ID)
print("✅ Connected to Google Sheets")

# OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)
print("✅ OpenAI key set")


def calculate_days_left(deadline_str: str) -> int:
    """Возвращает количество дней до дедлайна (включительно)"""
    deadline = datetime.strptime(deadline_str, "%d.%m.%Y").date()
    today = datetime.today().date()
    delta = (deadline - today).days
    return delta


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip()

    if "дедлайн" in text and any(char.isdigit() for char in text):
        try:
            # Пример: "сделать задачу дедлайн 12.08.2025"
            parts = text.split("дедлайн")
            task_text = parts[0].strip()
            deadline_str = parts[1].strip().split()[0]
            days_left = calculate_days_left(deadline_str)

            sheet = spreadsheet.worksheet("Задачи")
            sheet.append_row([task_text, deadline_str, "Не начато", days_left])
            bot.send_message(message.chat.id, f"📝 Задача добавлена: «{task_text}» до {deadline_str} ({days_left} дн.)")
            return
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Не удалось распознать или записать задачу. Ошибка: {e}")
            return

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты — ассистент по задачам и дедлайнам, работаешь с Google Таблицей, структурируешь мысли и задачи."},
                {"role": "user", "content": text}
            ]
        )
        reply = response.choices[0].message.content.strip()
        bot.send_message(message.chat.id, reply)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при запросе к OpenAI: {e}")


# Бот в фоне
threading.Thread(target=lambda: bot.polling(none_stop=True)).start()

# Flask-сервер
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
