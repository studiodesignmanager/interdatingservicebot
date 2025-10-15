import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

# Загружаем токены
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO)

# FSM состояния
class Form(StatesGroup):
    name = State()
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()

# Кнопка CONTACT US
contact_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📩CONTACT US", url="https://t.me/interdatingservice")]
    ]
)

# Хранение данных пользователей
user_data = {}

# Команда /start
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_data[message.from_user.id] = {"answers": {}}
    await message.answer("👋 Good afternoon! Please answer a few questions.\n\n✍️ This will help us better understand why you are contacting us and assist you more efficiently.")
    await message.answer("Please enter your name:")
    await state.set_state(Form.name)

# Name
@dp.message(Form.name)
async def ask_gender(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["User"] = message.text.strip() or "Anonymous"
    await message.answer("👤 Please select your gender:")
    gender_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Man", callback_data="gender_man"),
             InlineKeyboardButton(text="Woman", callback_data="gender_woman")]
        ]
    )
    await message.answer("Select:", reply_markup=gender_keyboard)
    await state.set_state(Form.gender)

# Gender
@dp.callback_query(Form.gender)
async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[1].capitalize()
    user_data[callback.from_user.id]["answers"]["Gender"] = choice
    await callback.message.answer("🎂 How old are you?")
    await state.set_state(Form.age)

# Age
@dp.message(Form.age)
async def ask_country(message: types.Message, state: FSMContext):
    age_text = message.text.strip()
    if not age_text.isdigit():
        await message.answer("🎂 Please enter your age using numbers only (e.g., 36).")
        return
    user_data[message.from_user.id]["answers"]["Age"] = age_text
    await message.answer("🌍 Which country do you currently live in?")
    await state.set_state(Form.country)

# Country
@dp.message(Form.country)
async def ask_registered(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["Country"] = message.text.strip() or "Anonymous"
    await message.answer("💻 Have you ever registered on international dating sites before?\nIf yes, please mention which ones.\nIf no, simply write “No”.")
    await state.set_state(Form.registered)

# Registered
@dp.message(Form.registered)
async def ask_purpose(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["Registered before"] = message.text.strip() or "No"
    await message.answer("🎯 What is your purpose for joining?\n(For example: serious relationship, marriage, friendship, etc.)")
    await state.set_state(Form.purpose)

# Purpose
@dp.message(Form.purpose)
async def final_step(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["Purpose"] = message.text.strip() or "Anonymous"

    # Формируем отчет админу
    data = user_data[message.from_user.id]["answers"]
    report = (
        f"📝 User: {data.get('User', 'Anonymous')}\n\n"
        f"👤 Gender: {data.get('Gender', 'N/A')}\n"
        f"🎂 Age: {data.get('Age', 'N/A')}\n"
        f"🌍 Country: {data.get('Country', 'N/A')}\n"
        f"💻 Registered before: {data.get('Registered before', 'N/A')}\n"
        f"🎯 Purpose: {data.get('Purpose', 'N/A')}\n\n"
        f"From: @{message.from_user.username or 'Anonymous'} (ID: {message.from_user.id})"
    )
    await bot.send_message(chat_id=ADMIN_ID, text=report)
    await message.answer("❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you.", reply_markup=contact_keyboard)
    await state.clear()

if __name__ == "__main__":
    import asyncio
    from aiogram import F

    async def main():
        await dp.start_polling(bot)

    asyncio.run(main())


























