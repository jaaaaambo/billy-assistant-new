import telebot
import os

API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

tasks = []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "Привет! Я — Билли Миллиган 🤖\n"
        "Просто отправь мне задачу, и я её сохраню.\n"
        "Команда /summary покажет список задач.\n"
        "Команда /clear удалит все задачи.")

@bot.message_handler(commands=['summary'])
def send_summary(message):
    if not tasks:
        bot.reply_to(message, "Пока задач нет. Отправь мне что-нибудь.")
    else:
        response = "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks)])
        bot.reply_to(message, f"📝 Вот твои задачи:\n{response}")

@bot.message_handler(commands=['clear'])
def clear_tasks(message):
    tasks.clear()
    bot.reply_to(message, "Все задачи удалены.")

@bot.message_handler(func=lambda message: True)
def handle_task(message):
    tasks.append(message.text)
    bot.reply_to(message, "Задача сохранена ✅")

if __name__ == "__main__":
    bot.infinity_polling()
