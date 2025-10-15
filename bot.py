import logging
import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

# --- LOAD ENV ---
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

# --- INIT ---
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- STATES ---
class Form(StatesGroup):
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()

# --- LOAD TEXTS ---
with open("texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)["en"]

# --- START HANDLER ---
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    # Сначала приветствие
    await message.answer(
        texts["en"]["greeting"]
    )
    # Затем вопрос про пол с кнопками
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Man", callback_data="Man"),
                InlineKeyboardButton(text="Woman", callback_data="Woman")
            ]
        ]
    )
    await message.answer(
        texts["en"]["gender_question"],
        reply_markup=keyboard
    )
    await state.set_state(Form.gender)


# --- GENDER HANDLER ---
@dp.callback_query(F.data.in_({"Man", "Woman"}))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)
    await callback.message.edit_text(texts["age_question"].replace("📅 ", ""))
    await state.set_state(Form.age)

# --- AGE HANDLER ---
@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer(texts["country_question"].replace("🌍 ", ""))
    await state.set_state(Form.country)

# --- COUNTRY HANDLER ---
@dp.message(Form.country)
async def process_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer(texts["sites_question"].replace("💌 ", ""))
    await state.set_state(Form.registered)

# --- REGISTERED HANDLER ---
@dp.message(Form.registered)
async def process_registered(message: types.Message, state: FSMContext):
    await state.update_data(registered=message.text)
    await message.answer(texts["purpose_question"].replace("🎯 ", ""))
    await state.set_state(Form.purpose)

# --- PURPOSE HANDLER ---
@dp.message(Form.purpose)
async def process_purpose(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    full_name = message.from_user.first_name or "Anonymous"
    username = f"@{message.from_user.username}" if message.from_user.username else "—"
    user_id = message.from_user.id

    report = (
        f"📝 New form received:\n\n"
        f"👤 User: {full_name}\n"
        f"⚥ Gender: {data.get('gender')}\n"
        f"📅 Age: {data.get('age')}\n"
        f"🌍 Country: {data.get('country')}\n"
        f"💻 Registered before: {data.get('registered')}\n"
        f"🎯 Purpose: {message.text}\n\n"
        f"From: {username} (ID: {user_id})"
    )

    await bot.send_message(ADMIN_ID, report)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=texts["contact_button"], url="https://t.me/interdatingservice")]
        ]
    )

    await message.answer(texts["final_message"], reply_markup=keyboard)

# --- RUN ---
async def main():
    print("Bot started... Admin ID:", ADMIN_ID)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())








































