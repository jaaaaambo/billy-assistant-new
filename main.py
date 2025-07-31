import os
import json
import base64
import telebot
import openai
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Восстанавливаем credentials.json из переменной окружения
creds_b64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
creds_path = "credentials.json"
with open(creds_path, "w") as f:
    f.write(base64.b64decode(creds_b64).decode("utf-8"))

# Авторизация в Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key("1AbCDEFGHIJKLmnOPqrSTuvWXYZ1234567890abcD3F")  # название таблицы

# OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Хендлер сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text

    # Запрос к OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты — ИИ-ассистент пользователя, помогаешь с задачами, идеями и дедлайнами."},
            {"role": "user", "content": user_input},
        ]
    )
    reply = response["choices"][0]["message"]["content"]

    bot.send_message(message.chat.id, reply)

    # Пример записи в таблицу
    sheet = spreadsheet.worksheet("Задачи")  # Название листа
    sheet.append_row([datetime.now().isoformat(), user_input, "from Telegram"])

bot.polling()
