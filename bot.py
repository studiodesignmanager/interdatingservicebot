import logging
import os
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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

# Load texts
with open("texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)


@dp.message(CommandStart())
async def start(message: types.Message):
    logging.info(f"User {message.from_user.id} started the bot.")
    user_data[message.from_user.id] = {"step": "gender", "answers": {}}
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Man"), KeyboardButton(text="Woman")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(texts["intro"], reply_markup=keyboard)
    await message.answer("1️⃣ Please select your gender:")


@dp.message(F.text.in_(["Man", "Woman"]))
async def ask_age(message: types.Message):
    uid = message.from_user.id
    user_data.setdefault(uid, {"answers": {}})
    user_data[uid]["answers"]["Gender"] = message.text
    user_data[uid]["step"] = "age"
    await message.answer("2️⃣ How old are you?", reply_markup=ReplyKeyboardRemove())


@dp.message(F.text.regexp(r"^\d{1,2}$"))
async def ask_country(message: types.Message):
    uid = message.from_user.id
    if user_data.get(uid, {}).get("step") != "age":
        return
    user_data[uid]["answers"]["Age"] = message.text
    user_data[uid]["step"] = "country"
    await message.answer("3️⃣ Which country do you currently live in?")


@dp.message(F.text)
async def ask_registration(message: types.Message):
    uid = message.from_user.id
    step = user_data.get(uid, {}).get("step")

    if step == "country":
        user_data[uid]["answers"]["Country"] = message.text
        user_data[uid]["step"] = "registered"
        await message.answer(
            "4️⃣ Have you ever registered on international dating sites before?\n"
            "If yes, please mention which ones.\n"
            "If no, simply write “No”."
        )

    elif step == "registered":
        user_data[uid]["answers"]["RegisteredBefore"] = message.text
        user_data[uid]["step"] = "purpose"
        await message.answer(
            "5️⃣ What is your purpose for joining?\n"
            "(For example: serious relationship, marriage, friendship, etc.)"
        )

    elif step == "purpose":
        user_data[uid]["answers"]["Purpose"] = message.text
        user_data[uid]["step"] = "done"

        contact_button = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]],
            resize_keyboard=True
        )
        await message.answer(
            "❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you.",
            reply_markup=contact_button
        )

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
        logging.info(f"✅ Message sent to admin ({ADMIN_ID})")
    except Exception as e:
        logging.error(f"❌ Failed to send message to admin: {e}")


async def main():
    print(f"Bot started... Admin ID: {ADMIN_ID}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())






