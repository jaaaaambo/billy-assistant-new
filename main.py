import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# --- Конфигурация ---
API_TOKEN = 'ТВОЙ_ТОКЕН_БОТА'
GOOGLE_SHEET_NAME = 'billy-assistant'

bot = telebot.TeleBot(API_TOKEN)
user_states = {}
pending_data = {}

# --- Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("billy-assistant.json", scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME)
sheet_tasks = sheet.worksheet("Задачи")
sheet_thoughts = sheet.worksheet("Мысли")

# --- Команды ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Я Билли Миллиган 🤖\n\nНапиши мне мысль или задачу — и я помогу с этим разобраться!")

@bot.message_handler(commands=['summary'])
def send_summary(message):
    rows = sheet_tasks.get_all_values()[1:]
    if not rows:
        bot.send_message(message.chat.id, "Пока нет задач.")
        return
    text = "\n".join([f"{i+1}. {row[0]} — до {row[2]} ({row[3]})" for i, row in enumerate(rows)])
    bot.send_message(message.chat.id, f"📝 Список задач:\n{text}")

# --- Обработка входящего текста ---
@bot.message_handler(func=lambda message: True)
def handle_input(message):
    user_id = message.from_user.id
    user_states[user_id] = 'awaiting_type'
    pending_data[user_id] = {'description': message.text}
    bot.send_message(user_id, "Это задача или мысль? Напиши `задача` или `мысль`.")

# --- Основная логика диалога ---
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'awaiting_type')
def handle_type(message):
    user_id = message.from_user.id
    msg_type = message.text.strip().lower()
    
    if msg_type not in ['задача', 'мысль']:
        bot.send_message(user_id, "Пожалуйста, напиши `задача` или `мысль`.")
        return

    pending_data[user_id]['type'] = msg_type
    if msg_type == 'мысль':
        save_thought(user_id)
    else:
        user_states[user_id] = 'awaiting_deadline'
        bot.send_message(user_id, "Когда дедлайн? Напиши в формате `ДД.ММ.ГГ` или `нет дедлайна`.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'awaiting_deadline')
def handle_deadline(message):
    user_id = message.from_user.id
    text = message.text.strip().lower()

    if text == 'нет дедлайна':
        deadline = ''
        days_left = ''
    else:
        try:
            deadline_date = datetime.strptime(text, "%d.%m.%y").date()
            deadline = deadline_date.strftime("%d.%m.%Y")
            days_left = (deadline_date - datetime.today().date()).days
        except ValueError:
            bot.send_message(user_id, "Не понял формат даты. Попробуй `31.08.25` или `нет дедлайна`.")
            return

    pending_data[user_id]['deadline'] = deadline
    pending_data[user_id]['days_left'] = days_left
    user_states[user_id] = 'awaiting_status'
    bot.send_message(user_id, "Какой статус задачи? Например: `в работе`, `ожидает`, `в планах`.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'awaiting_status')
def handle_status(message):
    user_id = message.from_user.id
    pending_data[user_id]['status'] = message.text.strip()
    save_task(user_id)

# --- Сохранение данных ---
def save_task(user_id):
    data = pending_data.pop(user_id)
    user_states.pop(user_id)
    row = [
        data['description'],
        data['type'],
        data['deadline'],
        data['status'],
        str(data['days_left']),
        datetime.now().strftime("%d.%m.%Y")
    ]
    sheet_tasks.append_row(row)
    bot.send_message(user_id, "✅ Задача сохранена в таблицу!")

def save_thought(user_id):
    data = pending_data.pop(user_id)
    user_states.pop(user_id)
    row = [data['description'], datetime.now().strftime("%d.%m.%Y")]
    sheet_thoughts.append_row(row)
    bot.send_message(user_id, "💭 Мысль сохранена!")

# --- Запуск ---
bot.polling(none_stop=True)
