import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# FSM
class Form(StatesGroup):
    name = State()
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()

# Inline keyboard for Contact
contact_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
    ]
)

# /start handler
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Good afternoon! Please answer a few questions.\n\n"
        "✍️ This will help us better understand why you are contacting us and assist you more efficiently."
    )
    await message.answer("Please enter your full name:")
    await state.set_state(Form.name)

# Name handler
@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Man", callback_data="gender_man"),
                InlineKeyboardButton(text="Woman", callback_data="gender_woman"),
            ]
        ]
    )
    await message.answer("Please select your gender:", reply_markup=keyboard)
    await state.set_state(Form.gender)

# Gender handler
@dp.callback_query(lambda c: c.data and c.data.startswith("gender_"))
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    gender = "Man" if callback.data == "gender_man" else "Woman"
    await state.update_data(gender=gender)
    await callback.message.answer("🎂 How old are you?")
    await state.set_state(Form.age)
    await callback.answer()

# Age handler
@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("🌍 Which country do you currently live in?")
    await state.set_state(Form.country)

# Country handler
@dp.message(Form.country)
async def process_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer(
        "💻 Have you ever registered on international dating sites before?\n"
        "If yes, please mention which ones.\n"
        "If no, simply write “No”."
    )
    await state.set_state(Form.registered)

# Registered handler
@dp.message(Form.registered)
async def process_registered(message: types.Message, state: FSMContext):
    await state.update_data(registered=message.text)
    await message.answer(
        "🎯 What is your purpose for joining?\n"
        "(For example: serious relationship, marriage, friendship, etc.)"
    )
    await state.set_state(Form.purpose)

# Purpose handler
@dp.message(Form.purpose)
async def process_purpose(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    # Send final thank you with contact button
    await message.answer(
        "❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you.",
        reply_markup=contact_keyboard
    )

    # Send report to admin
    name = data.get("name", "Anonymous")
    gender = data.get("gender", "N/A")
    age = data.get("age", "N/A")
    country = data.get("country", "N/A")
    registered = data.get("registered", "N/A")
    purpose = data.get("purpose", "N/A")
    username = message.from_user.username or "N/A"
    user_id = message.from_user.id

    report = (
        f"📝 {name} - New form received:\n\n"
        f"👤 Gender: {gender}\n"
        f"🎂 Age: {age}\n"
        f"🌍 Country: {country}\n"
        f"💻 Registered before: {registered}\n"
        f"🎯 Purpose: {purpose}\n\n"
        f"From: @{username} (ID: {user_id})"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=report)

if __name__ == "__main__":
    print(f"Bot started... Admin ID: {ADMIN_ID}")
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)























