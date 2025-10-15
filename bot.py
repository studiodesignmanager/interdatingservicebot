import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загрузка токена и admin_id
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FSM
class Form(StatesGroup):
    name = State()
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()
    done = State()

# Кнопка CONTACT US
contact_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
    ]
)

# Start
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.update_data(user_name=message.from_user.full_name, username=message.from_user.username)
    await message.answer(
        "👋 Good afternoon! Please answer a few questions.\n\n"
        "✍️ This will help us better understand why you are contacting us and assist you more efficiently.\n\n"
        "Please select your gender:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Man", callback_data="gender_Man"),
                    InlineKeyboardButton(text="Woman", callback_data="gender_Woman"),
                ]
            ]
        )
    )
    await state.set_state(Form.gender)

# Gender
@dp.callback_query(lambda c: c.data.startswith("gender_"), state=Form.gender)
async def gender_callback(c: types.CallbackQuery, state: FSMContext):
    gender = c.data.split("_")[1]
    await state.update_data(gender=gender)
    await c.message.edit_text(f"👤 Gender: {gender}\n\nHow old are you?")
    await state.set_state(Form.age)

# Age
@dp.message(Form.age)
async def ask_age(message: types.Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("🎂 Please enter a valid age (numbers only).")
        return
    await state.update_data(age=message.text.strip())
    await message.answer("🌍 Which country do you currently live in?")
    await state.set_state(Form.country)

# Country
@dp.message(Form.country)
async def ask_country(message: types.Message, state: FSMContext):
    if not message.text.strip():
        await message.answer("🌍 Please enter a valid country.")
        return
    await state.update_data(country=message.text.strip())
    await message.answer(
        "💻 Have you ever registered on international dating sites before?\n"
        "If yes, please mention which ones.\n"
        "If no, simply write “No”."
    )
    await state.set_state(Form.registered)

# Registered
@dp.message(Form.registered)
async def ask_registered(message: types.Message, state: FSMContext):
    await state.update_data(registered=message.text.strip())
    await message.answer(
        "🎯 What is your purpose for joining?\n"
        "(For example: serious relationship, marriage, friendship, etc.)"
    )
    await state.set_state(Form.purpose)

# Purpose
@dp.message(Form.purpose)
async def ask_purpose(message: types.Message, state: FSMContext):
    await state.update_data(purpose=message.text.strip())
    data = await state.get_data()

    report = (
        f"📝 User: {data.get('user_name', 'Anonymous')}\n"
        f"👤 Gender: {data.get('gender')}\n"
        f"🎂 Age: {data.get('age')}\n"
        f"🌍 Country: {data.get('country')}\n"
        f"💻 Registered before: {data.get('registered')}\n"
        f"🎯 Purpose: {data.get('purpose')}\n\n"
        f"From: @{data.get('username', 'unknown')} (ID: {message.from_user.id})"
    )

    await bot.send_message(chat_id=ADMIN_ID, text=report)
    await message.answer(
        "❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you.",
        reply_markup=contact_button
    )
    await state.clear()

if __name__ == "__main__":
    import asyncio
    from aiogram import executor
    logging.info("Bot started... Admin ID: %s", ADMIN_ID)
    executor.start_polling(dp, skip_updates=True)
























