import logging
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
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
    user_data[message.from_user.id] = {"answers": {}}
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(types.KeyboardButton(text="Man"))
    keyboard.add(types.KeyboardButton(text="Woman"))
    await message.answer(
        texts["greeting"],
        reply_markup=keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )
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

    contact_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
        ]
    )

    await message.answer(
        texts["thank_you"],
        reply_markup=contact_button
    )

    # Send results to admin
    await send_results_to_admin(message.from_user)


async def send_results_to_admin(user: types.User):
    data = user_data.get(user.id, {}).get("answers", {})
    if not data:
        return

    username_display = data.get("Name") or f"User {user.id}"  # Если есть поле Name в анкете
    tg_username = f"@{user.username}" if user.username else f"tg://user?id={user.id}"

    text = (
        f"📝 User: {username_display}\n\n"
        f"👤 Gender: {data.get('Gender')}\n"
        f"📅 Age: {data.get('Age')}\n"
        f"🌍 Country: {data.get('Country')}\n"
        f"💻 Registered before: {data.get('RegisteredBefore')}\n"
        f"🎯 Purpose: {data.get('Purpose')}\n\n"
        f"From: {tg_username} (ID: {user.id})"
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




































