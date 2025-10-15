import logging
import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

# load .env
load_dotenv()

# Use the same env var name you already have: BOT_TOKEN
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not found in .env. Please set BOT_TOKEN in .env and restart.")
    raise SystemExit(1)

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
if not ADMIN_ID:
    print("ERROR: ADMIN_ID not found or invalid in .env.")
    raise SystemExit(1)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM states (same as before)
class Form(StatesGroup):
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()

# load texts.json (must exist)
with open("texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)

# start
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    # use texts key as you have (adjust if different)
    start_text = texts.get("start_en") or texts.get("greeting") or "👋 Good afternoon! Please answer a few questions."
    await message.answer(
        start_text + "\n\nPlease select your gender:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💬 Man", callback_data="Man"),
                 InlineKeyboardButton(text="💬 Woman", callback_data="Woman")]
            ]
        )
    )
    await state.set_state(Form.gender)

# gender
@dp.callback_query(F.data.in_({"Man", "Woman"}))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)
    await callback.message.edit_text("🎂 How old are you?")
    await state.set_state(Form.age)
    await callback.answer()

# age
@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text.strip())
    await message.answer("🌍 Which country do you currently live in?")
    await state.set_state(Form.country)

# country
@dp.message(Form.country)
async def process_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text.strip())
    await message.answer(
        "💻 Have you ever registered on international dating sites before?\n"
        "If yes, please mention which ones.\n"
        "If no, simply write “No”."
    )
    await state.set_state(Form.registered)

# registered
@dp.message(Form.registered)
async def process_registered(message: types.Message, state: FSMContext):
    await state.update_data(registered=message.text.strip())
    await message.answer("🎯 What is your purpose for joining?\n(For example: serious relationship, marriage, friendship, etc.)")
    await state.set_state(Form.purpose)

# purpose -> final
@dp.message(Form.purpose)
async def process_purpose(message: types.Message, state: FSMContext):
    await state.update_data(purpose=message.text.strip())
    data = await state.get_data()
    await state.clear()

    # Prefer Telegram full_name if present, else fall back to collected name or first_name, else dash
    full_name = (message.from_user.full_name or "").strip() or data.get("name") or (message.from_user.first_name or "—")
    username = f"@{message.from_user.username}" if message.from_user.username else f"tg://user?id={message.from_user.id}"
    user_id = message.from_user.id

    report = (
        f"📝 New form received:\n\n"
        f"👤 Name: {full_name}\n"
        f"👤 Gender: {data.get('gender','')}\n"
        f"📅 Age: {data.get('age','')}\n"
        f"🌍 Country: {data.get('country','')}\n"
        f"💻 Registered before: {data.get('registered','')}\n"
        f"🎯 Purpose: {data.get('purpose','')}\n\n"
        f"{('Username: ' + username) if message.from_user.username else ('User: ' + username)}"
    )

    # send single aggregated report to admin
    try:
        await bot.send_message(ADMIN_ID, report)
    except Exception as e:
        # don't crash; log and continue
        logging.exception("Failed to send report to admin: %s", e)

    # final message with contact button
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
        ]
    )
    final_text = texts.get("final_en") or texts.get("thank_you") or "❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you."
    await message.answer(final_text, reply_markup=keyboard)

# run
async def main():
    logging.info("Bot started... Admin ID: %s", ADMIN_ID)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

































