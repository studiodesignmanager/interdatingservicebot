import logging
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Store answers temporarily
user_data = {}

# Load texts from texts.json
with open("texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)


@dp.message(CommandStart())
async def start(message: types.Message):
    # Инициализация данных
    user_data[message.from_user.id] = {"answers": {}, "name": message.from_user.full_name}

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Man"), KeyboardButton(text="Woman")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        texts["greeting"] + "\n\n" + texts["choose_gender"],
        reply_markup=keyboard
    )


@dp.message(lambda m: m.text in ["Man", "Woman"])
async def ask_age(message: types.Message):
    user_data[message.from_user.id]["answers"]["Gender"] = message.text
    await message.answer(texts["age_question"], reply_markup=types.ReplyKeyboardRemove())


@dp.message(lambda m: "Age" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_country(message: types.Message):
    user_data[message.from_user.id]["answers"]["Age"] = message.text
    await message.answer(texts["country_question"])


@dp.message(lambda m: "Country" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_registered(message: types.Message):
    user_data[message.from_user.id]["answers"]["Country"] = message.text
    await message.answer(texts["registered_question"])


@dp.message(lambda m: "RegisteredBefore" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_purpose(message: types.Message):
    user_data[message.from_user.id]["answers"]["RegisteredBefore"] = message.text
    await message.answer(texts["purpose_question"])


@dp.message(lambda m: "Purpose" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def finish(message: types.Message):
    user_data[message.from_user.id]["answers"]["Purpose"] = message.text

    contact_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
        ]
    )

    await message.answer(
        texts["thank_you"],
        reply_markup=contact_button
    )

    await send_results_to_admin(message.from_user)


async def send_results_to_admin(user: types.User):
    data = user_data.get(user.id, {})
    answers = data.get("answers", {})
    name = data.get("name", "Anonymous")  # Имя пользователя из анкеты или Anonymous

    # Проверка всех полей перед формированием отчета
    gender = answers.get("Gender", "N/A")
    age = answers.get("Age", "N/A")
    country = answers.get("Country", "N/A")
    registered = answers.get("RegisteredBefore", "N/A")
    purpose = answers.get("Purpose", "N/A")

    text = (
        f"📝 User: {name}\n\n"
        f"👤 Gender: {gender}\n"
        f"📅 Age: {age}\n"
        f"🌍 Country: {country}\n"
        f"💻 Registered before: {registered}\n"
        f"🎯 Purpose: {purpose}\n\n"
        f"From: @{user.username if user.username else 'NoUsername'} (ID: {user.id})"
    )

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=text)
        print("✅ Message sent to admin")
    except Exception as e:
        print("❌ Failed to send message to admin:", e)


async def main():
    print(f"Bot started... Admin ID: {ADMIN_ID}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())












































