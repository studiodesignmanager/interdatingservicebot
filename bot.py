import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram import F
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Храним ответы пользователей
user_data = {}

# --- Этап 1 ---
@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Man"), KeyboardButton(text="Woman")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "👋 Good afternoon! Please answer a few questions.\n\n"
        "✍️ This will help us better understand why you are contacting us and assist you more efficiently.\n\n"
        "Please select your gender:",
        reply_markup=keyboard
    )
    user_data[message.from_user.id] = {"step": 1}

# --- Этап 2: пол ---
@dp.message(F.text.in_(["Man", "Woman"]))
async def gender_chosen(message: types.Message):
    user_data[message.from_user.id]["gender"] = message.text
    user_data[message.from_user.id]["step"] = 2
    await message.answer("How old are you?", reply_markup=types.ReplyKeyboardRemove())

# --- Этап 3: возраст ---
@dp.message(F.text.regexp(r"^\d{1,2}$"))
async def age_received(message: types.Message):
    user_data[message.from_user.id]["age"] = message.text
    user_data[message.from_user.id]["step"] = 3
    await message.answer("Which country do you currently live in?")

# --- Этап 4: страна ---
@dp.message(F.text, lambda msg: user_data.get(msg.from_user.id, {}).get("step") == 3)
async def country_received(message: types.Message):
    user_data[message.from_user.id]["country"] = message.text
    user_data[message.from_user.id]["step"] = 4
    await message.answer(
        "Have you ever registered on international dating sites before?\n"
        "If yes, please mention which ones.\n"
        "If no, simply write “No”."
    )

# --- Этап 5: опыт регистрации ---
@dp.message(F.text, lambda msg: user_data.get(msg.from_user.id, {}).get("step") == 4)
async def sites_received(message: types.Message):
    user_data[message.from_user.id]["sites"] = message.text
    user_data[message.from_user.id]["step"] = 5
    await message.answer(
        "What is your purpose for joining?\n"
        "(For example: serious relationship, marriage, friendship, etc.)"
    )

# --- Этап 6: цель ---
@dp.message(F.text, lambda msg: user_data.get(msg.from_user.id, {}).get("step") == 5)
async def purpose_received(message: types.Message):
    user_data[message.from_user.id]["purpose"] = message.text
    user_data[message.from_user.id]["step"] = 6

    # Кнопка для связи
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Send us a message", url="https://t.me/interdatingservice")]
        ]
    )

    await message.answer(
        "❤️ Thank you for your answers!\n"
        "Click the button below and send us a message so we can get in touch with you.",
        reply_markup=keyboard
    )

    # Отправляем админу ответы
    data = user_data[message.from_user.id]
    text = (
        f"📩 New submission from @{message.from_user.username or 'NoUsername'}\n\n"
        f"👤 Gender: {data.get('gender')}\n"
        f"🎂 Age: {data.get('age')}\n"
        f"🌍 Country: {data.get('country')}\n"
        f"💻 Registered on dating sites before: {data.get('sites')}\n"
        f"🎯 Purpose: {data.get('purpose')}"
    )
    await bot.send_message(ADMIN_ID, text)

    # очищаем после отправки
    del user_data[message.from_user.id]

# --- Запуск ---
if __name__ == "__main__":
    print






























