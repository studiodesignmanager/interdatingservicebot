import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    name = State()
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()

contact_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
    ]
)

# Start command
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "👋 Good afternoon! Please answer a few questions.\n\n"
        "✍️ This will help us better understand why you are contacting us and assist you more efficiently."
    )
    await message.answer("Please enter your full name:")
    await state.set_state(Form.name)

# Name
@dp.message(Form.name)
async def ask_gender(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip() or "Anonymous")
    await message.answer("Please select your gender:")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Man", callback_data="gender_man"),
                InlineKeyboardButton(text="Woman", callback_data="gender_woman")
            ]
        ]
    )
    await state.set_state(Form.gender)
    await message.answer("Choose:", reply_markup=keyboard)

# Gender
@dp.callback_query(Form.gender)
async def ask_age(callback: types.CallbackQuery, state: FSMContext):
    gender = "Man" if callback.data == "gender_man" else "Woman"
    await state.update_data(gender=gender)
    await callback.message.answer("🎂 How old are you?")
    await state.set_state(Form.age)
    await callback.answer()

# Age
@dp.message(Form.age)
async def ask_country(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text.strip())
    await message.answer("🌍 Which country do you currently live in?")
    await state.set_state(Form.country)

# Country
@dp.message(Form.country)
async def ask_registered(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text.strip() or "Anonymous")
    await message.answer(
        "💻 Have you ever registered on international dating sites before?\n"
        "If yes, please mention which ones.\nIf no, simply write “No”."
    )
    await state.set_state(Form.registered)

# Registered
@dp.message(Form.registered)
async def ask_purpose(message: types.Message, state: FSMContext):
    await state.update_data(registered=message.text.strip())
    await message.answer(
        "🎯 What is your purpose for joining?\n"
        "(For example: serious relationship, marriage, friendship, etc.)"
    )
    await state.set_state(Form.purpose)

# Purpose
@dp.message(Form.purpose)
async def final_thank_you(message: types.Message, state: FSMContext):
    await state.update_data(purpose=message.text.strip())

    data = await state.get_data()
    name = data.get("name", "Anonymous")
    gender = data.get("gender", "")
    age = data.get("age", "")
    country = data.get("country", "")
    registered = data.get("registered", "")
    purpose = data.get("purpose", "")

    report = (
        f"📝 User: {name}\n"
        f"👤 Gender: {gender}\n"
        f"🎂 Age: {age}\n"
        f"🌍 Country: {country}\n"
        f"💻 Registered before: {registered}\n"
        f"🎯 Purpose: {purpose}\n\n"
        f"From: @{message.from_user.username} (ID: {message.from_user.id})"
    )

    await bot.send_message(ADMIN_ID, report)
    await message.answer(
        "❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you.",
        reply_markup=contact_button
    )
    await state.clear()

if __name__ == "__main__":
    import asyncio
    from aiogram import Router
    from aiogram.client.session.aiohttp import AiohttpSession

    dp.include_router(Router())

    async def main():
        async with Bot(token=BOT_TOKEN, session=AiohttpSession()) as b:
            await dp.start_polling(b)

    asyncio.run(main())





























