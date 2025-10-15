import logging
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

# ----------------- Logging -----------------
logging.basicConfig(level=logging.INFO)

# ----------------- Load .env -----------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

print("BOT_TOKEN loaded:", BOT_TOKEN)  # убедимся, что токен корректный

# ----------------- Bot & Dispatcher -----------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------------- User data -----------------
user_data = {}

# ----------------- Load texts -----------------
with open("texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)

# ----------------- Handlers -----------------
@dp.message(CommandStart())
async def start(message: types.Message):
    user_data[message.from_user.id] = {"answers": {}}

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Man"), KeyboardButton(text="Woman")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(texts["greeting"], reply_markup=keyboard)
    await message.answer(texts["choose_gender"])


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

    contact_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]],
        resize_keyboard=True
    )

    await message.answer(texts["thank_you"], reply_markup=contact_keyboard)
    await send_results_to_admin(message.from_user)


# ----------------- Send to admin -----------------
async def send_results_to_admin(user: types.User):
    data = user_data.get(user.id, {}).get("answers", {})
    if not data:
        return

    username = f"@{user.username}" if user.username else f"tg://user?id={user.id}"

    text = (
        f"📨 New user completed the survey!\n\n"
        f"User: {username}\n"
        f"Gender: {data.get('Gender')}\n"
        f"Age: {data.get('Age')}\n"
        f"Country: {data.get('Country')}\n"
        f"Registered before: {data.get('RegisteredBefore')}\n"
        f"Purpose: {data.get('Purpose')}"
    )

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=text)
        print("✅ Message sent to admin")
    except Exception as e:
        print("❌ Failed to send message to admin:", e)


# ----------------- Main -----------------
async def main():
    print(f"Bot started... Admin ID: {ADMIN_ID}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())



















