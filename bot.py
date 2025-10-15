import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils import executor
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
import json
with open("texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)


@dp.message(CommandStart())
async def start(message: types.Message):
    user_data[message.from_user.id] = {"answers": {}}
    await message.answer(
        texts["intro"],
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Man"), KeyboardButton(text="Woman")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await message.answer("1️⃣ Please select your gender:")


@dp.message(lambda m: m.text in ["Man", "Woman"])
async def ask_age(message: types.Message):
    user_data[message.from_user.id]["answers"]["Gender"] = message.text
    await message.answer("2️⃣ How old are you?", reply_markup=types.ReplyKeyboardRemove())


@dp.message(lambda m: "How old" in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_country(message: types.Message):
    user_data[message.from_user.id]["answers"]["Age"] = message.text
    await message.answer("3️⃣ Which country do you currently live in?")


@dp.message(lambda m: "Country" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_registration(message: types.Message):
    if "Age" not in user_data.get(message.from_user.id, {}).get("answers", {}):
        user_data[message.from_user.id]["answers"]["Age"] = message.text
    user_data[message.from_user.id]["answers"]["Country"] = message.text
    await message.answer(
        "4️⃣ Have you ever registered on international dating sites before?\n"
        "If yes, please mention which ones.\n"
        "If no, simply write “No”."
    )


@dp.message(lambda m: "RegisteredBefore" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_purpose(message: types.Message):
    user_data[message.from_user.id]["answers"]["RegisteredBefore"] = message.text
    await message.answer(
        "5️⃣ What is your purpose for joining?\n"
        "(For example: serious relationship, marriage, friendship, etc.)"
    )


@dp.message(lambda m: "Purpose" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def finish(message: types.Message):
    user_data[message.from_user.id]["answers"]["Purpose"] = message.text

    contact_button = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]],
        resize_keyboard=True
    )

    await message.answer(
        "❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you.",
        reply_markup=contact_button
    )

    # Send results to admin
    await send_results_to_admin(message.from_user)


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


async def main():
    print(f"Bot started... Admin ID: {ADMIN_ID}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())




