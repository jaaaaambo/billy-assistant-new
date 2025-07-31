import logging
import os
import telebot
from datetime import datetime
from google_sheets_helper import append_task_to_sheet

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

tasks = []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "Привет! Я — Билли Миллиган 🤖\n"
        "Просто отправь мне задачу, и я её сохраню в Google Таблицу.\n"
        "Команда /summary покажет список задач.\n"
        "Команда /clear удалит все задачи (локально).")

@bot.message_handler(commands=['summary'])
def send_summary(message):
    if not tasks:
        bot.reply_to(message, "Пока задач нет (локально). Отправь мне что-нибудь.")
    else:
        response = "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks)])
        bot.reply_to(message, f"📝 Вот твои задачи (локально):\n{response}")

@bot.message_handler(commands=['clear'])
def clear_tasks(message):
    tasks.clear()
    bot.reply_to(message, "Локальные задачи очищены. В таблице они остаются.")

@bot.message_handler(func=lambda message: True)
def handle_task(message):
    tasks.append(message.text)
    now = datetime.now()
    date = now.strftime("%d.%m.%Y")
    time = now.strftime("%H:%M")
    username = message.from_user.username or f"id:{message.from_user.id}"
    task_text = message.text
    status = "активная"

    append_task_to_sheet([date, time, username, task_text, status])
    bot.reply_to(message, "Задача сохранена в Google Таблицу ✅")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot.infinity_polling()
