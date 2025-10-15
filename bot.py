import logging
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Logging setup
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Temporary storage for user answers
user_data = {}

# Load texts
texts = {
    "intro": "👋 Good afternoon! Please answer a few questions.\n\n✍️ This will help us better understand why you are contacting us and assist you more efficiently.",
    "choose_gender": "Please select your gender:",
    "age_question": "How old are you?",
    "country_question": "Which country do you currently live in?",
    "registered_question": "Have you ever registered on international dating sites before?\nIf yes, please mention which ones.\nIf no, simply write “No”.",
    "purpose_question": "What is your purpose for joining?\n(For example: serious relationship, marriage, friendship, etc.)",
    "thank_you": "❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you."
}

# Start command
@dp.message(CommandStart())
async def start(message: types.Message):
    user_data[message.from_user.id] = {"answers": {}}

    # Send greeting
    await message.answer(texts["intro"])

    # Ask gender with buttons
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Man"), KeyboardButton(text="Woman")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(texts["choose_gender"], reply_markup=keyboard)


# Gender selection
@dp.message(lambda m: m.text in ["Man", "Woman"])
async def ask_age(message: types.Message):
    user_data[message.from_user.id]["answers"]["Gender"] = message.text
    await message.answer(texts["age_question"], reply_markup=types.ReplyKeyboardRemove())


# Age
@dp.message(lambda m: "Age" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_country(message: types.Message):
    user_data[message.from_user.id]["answers"]["Age"] = message.text
    await message.answer(texts["country_question"])


# Country
@dp.message(lambda m: "Country" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_registered(message: types.Message):
    user_data[message.from_user.id]["answers"]["Country"] = message.text
    await message.answer(texts["registered_question"])


# Registered before
@dp.message(lambda m: "RegisteredBefore" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_purpose(message: types.Message):
    user_data[message.from_user.id]["answers"]["RegisteredBefore"] = message.text
    await message.answer(texts["purpose_question"])


# Purpose
@dp.message(lambda m: "Purpose" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def finish(message: types.Message):
    user_data[message.from_user.id]["answers"]["Purpose"] = message.text

    # Inline button with emoji
    contact_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
        ]
    )

    await message.answer(texts["thank_you"], reply_markup=contact_button)

    # Send results to admin
    await send_results_to_admin(message.from_user)


# Send results to admin
async def send_results_to_admin(user: types.User):
    data = user_data.get(user.id, {}).get("answers", {})
    if not data:
        return

    full_name = f"{user.full_name}" if user.full_name else "Anonymous"
    username = f"@{user.username}" if user.username else f"tg://user?id={user.id}"

    text = (
        f"📝 User: {full_name}\n\n"
        f"👤 Gender: {data.get('Gender')}\n"
        f"📅 Age: {data.get('Age')}\n"
        f"🌍 Country: {data.get('Country')}\n"
        f"💻 Registered before: {data.get('RegisteredBefore')}\n"
        f"🎯 Purpose: {data.get('Purpose')}\n\n"
        f"From: {username} (ID: {user.id})"
    )

    try:
        await bot.send_message(chat_id=ADMIN_ID, text=text)
        print("✅ Message sent to admin")
    except Exception as e:
        print("❌ Failed to send message to admin:", e)


# Run bot
async def main():
    print(f"Bot started... Admin ID: {ADMIN_ID}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())










































