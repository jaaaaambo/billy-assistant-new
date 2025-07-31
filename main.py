import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Простой список задач в оперативной памяти
tasks = []

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я — Билли Миллиган 🤖
Просто отправь мне задачу, и я её сохраню.
Команда /summary покажет список задач.")

@dp.message_handler(commands=['summary'])
async def send_summary(message: types.Message):
    if not tasks:
        await message.reply("Пока задач нет. Отправь мне что-нибудь.")
    else:
        response = "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks)])
        await message.reply(f"📝 Вот твои задачи:\n{response}")

@dp.message_handler(commands=['clear'])
async def clear_tasks(message: types.Message):
    tasks.clear()
    await message.reply("Все задачи удалены.")

@dp.message_handler()
async def handle_task(message: types.Message):
    tasks.append(message.text)
    await message.reply("Задача сохранена ✅")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)