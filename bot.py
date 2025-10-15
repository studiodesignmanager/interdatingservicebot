import logging
import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

# Logging
logging.basicConfig(level=logging.INFO)

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Load texts
with open("texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)


# FSM States
class Form(StatesGroup):
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()


# /start handler
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="Man"), types.KeyboardButton(text="Woman")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        texts["greeting"] + "\n\n" + texts["choose_gender"],
        reply_markup=keyboard
    )
    await state.set_state(Form.gender)


# Gender handler
@dp.message(lambda m: m.text in ["Man", "Woman"])
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(Gender=message.text)
    await message.answer(texts["age_question"], reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.age)


# Age handler
@dp.message()
async def process_age(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != Form.age:
        return
    await state.update_data(Age=message.text)
    await message.answer(texts["country_question"])
    await state.set_state(Form.country)


# Country handler
@dp.message()
async def process_country(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != Form.country:
        return
    await state.update_data(Country=message.text)
    await message.answer(texts["registered_question"])
    await state.set_state(Form.registered)


# Registered before handler
@dp.message()
async def process_registered(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != Form.registered:
        return
    await state.update_data(RegisteredBefore=message.text)
    await message.answer(texts["purpose_question"])
    await state.set_state(Form.purpose)


# Purpose handler and finish
@dp.message()
async def process_purpose(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != Form.purpose:
        return
    await state.update_data(Purpose=message.text)

    data = await state.get_data()

    # Contact button
    contact_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
        ]
    )

    await message.answer(texts["thank_you"], reply_markup=contact_button)

    # Send results to admin
    await send_results_to_admin(message.from_user, data)

    await state.clear()


async def send_results_to_admin(user: types.User, data: dict):
    username = f"@{user.username}" if user.username else "Anonymous"
    user_fullname = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name

    text = (
        f"📝 User: {user_fullname}\n\n"
        f"👤 Gender: {data.get('Gender')}\n"
        f"📅 Age: {data.get('Age')}\n"
        f"🌍 Country: {data.get('Country')}\n"
        f"💻 Registered before: {data.get('RegisteredBefore')}\n"
        f"🎯 Purpose: {data.get('Purpose')}\n\n"
        f"From: {username} (ID: {user.id})"
    )
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=text)
        print("✅ Message sent to admin")
    except Exception as e:
        print("❌ Failed to send message to admin:", e)


# Run bot
if __name__ == "__main__":
    import asyncio
    print(f"Bot started... Admin ID: {ADMIN_ID}")
    asyncio.run(dp.start_polling(bot))





















