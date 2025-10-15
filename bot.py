import logging
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import asyncio

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
    user_data[message.from_user.id] = {"answers": {}}
    # Gender selection buttons
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Man", callback_data="gender_Man"),
             InlineKeyboardButton(text="Woman", callback_data="gender_Woman")]
        ]
    )
    await message.answer(texts["greeting"], reply_markup=keyboard)


@dp.callback_query(lambda c: c.data and c.data.startswith("gender_"))
async def ask_age(callback_query: types.CallbackQuery):
    gender = callback_query.data.split("_")[1]
    user_data[callback_query.from_user.id]["answers"]["Gender"] = gender
    await bot.send_message(callback_query.from_user.id, texts["age_question"])


@dp.message(lambda m: "Gender" in user_data.get(m.from_user.id, {}).get("answers", {}) and
            "Age" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_country(message: types.Message):
    user_data[message.from_user.id]["answers"]["Age"] = message.text
    await message.answer(texts["country_question"])


@dp.message(lambda m: "Age" in user_data.get(m.from_user.id, {}).get("answers", {}) and
            "Country" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_registered(message: types.Message):
    user_data[message.from_user.id]["answers"]["Country"] = message.text
    await message.answer(texts["registered_question"])


@dp.message(lambda m: "Country" in user_data.get(m.from_user.id, {}).get("answers", {}) and
            "RegisteredBefore" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def ask_purpose(message: types.Message):
    user_data[message.from_user.id]["answers"]["RegisteredBefore"] = message.text
    await message.answer(texts["purpose_question"])


@dp.message(lambda m: "RegisteredBefore" in user_data.get(m.from_user.id, {}).get("answers", {}) and
            "Purpose" not in user_data.get(m.from_user.id, {}).get("answers", {}))
async def finish(message: types.Message):
    user_data[message.from_user.id]["answers"]["Purpose"] = message.text

    contact_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
        ]
    )

    await message.answer(texts["thank_you"], reply_markup=contact_button)

    # Send results to admin
    await send_results_to_admin(message.from_user)


async def send_results_to_admin(user: types.User):
    data = user_data.get(user.id, {}).get("answers", {})
    if not data:
        return

    username = f"@{user.username}" if user.username else f"tg://user?id={user.id}"

    text = (
        f"📩 **New user response!**\n\n"
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
    asyncio.run(main())


































