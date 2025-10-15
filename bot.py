import os
import json
import asyncio
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import Router

# ---------- logging ----------
logging.basicConfig(level=logging.INFO)

# ---------- load env ----------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment (.env)")

# ---------- bot / dispatcher ----------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# ---------- FSM ----------
class Form(StatesGroup):
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()

# ---------- START ----------
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    greeting_text = (
        "👋 Good afternoon! Please answer a few questions.\n\n"
        "✍️ This will help us better understand why you are contacting us and assist you more efficiently.\n\n"
        "Please select your gender:"
    )

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Man"), KeyboardButton(text="Woman")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(greeting_text, reply_markup=kb)
    await state.set_state(Form.gender)

# ---------- GENDER ----------
@router.message(Form.gender)
async def process_gender(message: Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer("How old are you?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.age)

# ---------- AGE ----------
@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Which country do you currently live in?")
    await state.set_state(Form.country)

# ---------- COUNTRY ----------
@router.message(Form.country)
async def process_country(message: Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer(
        "Have you ever registered on international dating sites before?\n"
        "If yes, please mention which ones.\n"
        "If no, simply write “No”."
    )
    await state.set_state(Form.registered)

# ---------- REGISTERED ----------
@router.message(Form.registered)
async def process_registered(message: Message, state: FSMContext):
    await state.update_data(registered=message.text)
    await message.answer(
        "What is your purpose for joining?\n"
        "(For example: serious relationship, marriage, friendship, etc.)"
    )
    await state.set_state(Form.purpose)

# ---------- PURPOSE ----------
@router.message(Form.purpose)
async def process_purpose(message: Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    data = await state.get_data()

    username = message.from_user.username
    if username:
        user_field = f"@{username}"
    else:
        user_field = f"tg://user?id={message.from_user.id}"

    admin_text = (
        "📨 New user completed the survey!\n\n"
        f"User: {user_field}\n"
        f"Gender: {data.get('gender')}\n"
        f"Age: {data.get('age')}\n"
        f"Country: {data.get('country')}\n"
        f"Registered before: {data.get('registered')}\n"
        f"Purpose: {data.get('purpose')}"
    )

    # ✅ кнопка со ссылкой (та же, что раньше)
    contact_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]],
        resize_keyboard=True
    )

    await message.answer(
        "❤️ Thank you for your answers!\n"
        "Click the button below and send us a message so we can get in touch with you.",
        reply_markup=contact_kb
    )

    # отправляем админу
    try:
        await bot.send_message(ADMIN_ID, admin_text)
        logging.info("✅ Sent survey results to admin.")
    except Exception as e:
        logging.error(f"Failed to send to admin: {e}")

    await state.clear()

# ---------- fallback ----------
@router.message(F.text)
async def catch_all(message: Message):
    pass

# ---------- run ----------
async def main():
    logging.info("Bot started... Admin ID: %s", ADMIN_ID)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




























