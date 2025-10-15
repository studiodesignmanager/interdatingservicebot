import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Загрузка токенов
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Тексты
texts = {
    "greeting": "👋 Good afternoon! Please answer a few questions.\n\n✍️ This will help us better understand why you are contacting us and assist you more efficiently.",
    "choose_gender": "Please select your gender:",
    "age_question": "How old are you?",
    "country_question": "Which country do you currently live in?",
    "registered_question": "Have you ever registered on international dating sites before?\nIf yes, please mention which ones.\nIf no, simply write “No”.",
    "purpose_question": "What is your purpose for joining?\n(For example: serious relationship, marriage, friendship, etc.)",
    "thank_you": "❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you."
}

# Кнопка CONTACT US
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
    ]
)

# Хранение ответов пользователей
user_data = {}

# Старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"answers": {}, "name": message.from_user.first_name}
    await message.answer(texts["greeting"])
    
    gender_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Man", callback_data="gender_Man"),
         InlineKeyboardButton(text="Woman", callback_data="gender_Woman")]
    ])
    await message.answer(texts["choose_gender"], reply_markup=gender_kb)

# Выбор пола
@dp.callback_query_handler(lambda c: c.data.startswith("gender_"))
async def process_gender(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data[user_id]["answers"]["Gender"] = callback_query.data.split("_")[1]
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, texts["age_question"])

# Возраст
@dp.message_handler(lambda m: "Gender" in user_data.get(m.from_user.id, {}).get("answers", {}) and
                                   "Age" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_age(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["answers"]["Age"] = message.text
    await message.answer(texts["country_question"])

# Страна
@dp.message_handler(lambda m: "Age" in user_data.get(m.from_user.id, {}).get("answers", {}) and
                                   "Country" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_country(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["answers"]["Country"] = message.text
    await message.answer(texts["registered_question"])

# Зарегистрирован ли ранее
@dp.message_handler(lambda m: "Country" in user_data.get(m.from_user.id, {}).get("answers", {}) and
                                   "RegisteredBefore" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_registered(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["answers"]["RegisteredBefore"] = message.text
    await message.answer(texts["purpose_question"])

# Цель
@dp.message_handler(lambda m: "RegisteredBefore" in user_data.get(m.from_user.id, {}).get("answers", {}) and
                                   "Purpose" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_purpose(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]["answers"]["Purpose"] = message.text

    # Отправка отчёта админу
    answers = user_data[user_id]["answers"]
    report_text = (
        f"📝 User: {user_data[user_id]['name']}\n\n"
        f"👤 Gender: {answers.get('Gender', 'N/A')}\n"
        f"🎂 Age: {answers.get('Age', 'N/A')}\n"
        f"🌍 Country: {answers.get('Country', 'N/A')}\n"
        f"💻 Registered before: {answers.get('RegisteredBefore', 'N/A')}\n"
        f"🎯 Purpose: {answers.get('Purpose', 'N/A')}\n\n"
        f"From: @{message.from_user.username} (ID: {user_id})"
    )
    await bot.send_message(ADMIN_ID, report_text, reply_markup=keyboard)
    
    # Финальное сообщение пользователю
    await message.answer(texts["thank_you"], reply_markup=keyboard)

if __name__ == "__main__":
    import asyncio
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)














































