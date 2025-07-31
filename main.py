import telebot
import os
from gpt import ask_gpt

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    response = ask_gpt(message.text)
    bot.send_message(message.chat.id, response)

bot.polling()
