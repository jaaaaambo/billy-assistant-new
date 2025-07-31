import telebot
import os
from gpt import ask_gpt

TOKENN = os.getenv("TELEGRAM_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    response = ask_gpt(message.text)
    bot.send_message(message.chat.id, response)

bot.polling()
