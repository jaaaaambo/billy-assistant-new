import telebot
from datetime import datetime
from google_sheets_helper import append_task_to_sheet
import os

API_TOKEN = os.getenv("API_TOKEN")  # Читаем из переменной среды
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "Привет! Я — Билли Миллиган 🤖\n"
        "Просто отправь мне задачу, и я её сохраню.\n"
        "Команда /summary покажет список задач.")

@bot.message_handler(commands=['summary'])
def send_summary(message):
    bot.reply_to(message, "Все задачи теперь хранятся в Google Sheets. Скоро добавим вывод!")

@bot.message_handler(commands=['clear'])
def clear_tasks(message):
    bot.reply_to(message, "Очистка доступна будет позже (Google Sheets) 🧹")

@bot.message_handler(func=lambda message: True)
def save_task(message):
    now = datetime.now()
    row = [
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        message.from_user.username or "",
        message.text,
        "новая"
    ]
    try:
        append_task_to_sheet(row)
        bot.reply_to(message, "Задача сохранена в таблице ✅")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при сохранении: {e}")

bot.polling(none_stop=True)
