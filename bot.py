import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router
from dotenv import load_dotenv
import asyncio

# Load .env variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


# Define states
class Form(StatesGroup):
    gender = State()
    age = State()
    country = State()


# Start command
@router.message(F.text == "/start")
async def start_handler(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Man"), KeyboardButton(text="Woman")]
        ],
        resize_keyboard=True
    )
    await message.answer("👋 Good afternoon! Please answer a few questions.\n\n✍️ This will help us better understand why you are contacting us and assist you more efficiently.\n\nSelect your gender:", reply_markup=keyboard)
    await state.set_state(Form.gender)


# Gender handler
@router.message(Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await message.answer("How old are you?", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.age)


# Age handler
@router.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Which country do you live in?")
    await state.set_state(Form.country)


# Country handler
@router.message(Form.country)
async def process_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    data = await state.get_data()

    gender = data.get("gender")
    age = data.get("age")
    country = data.get("country")
    username = message.from_user.username or "No username"
    user_id = message.from_user.id

    # Send confirmation to user
    await message.answer("✅ Thank you! Our team will contact you soon.")

    # Send data to admin
    admin_text = (
        f"📩 New submission:\n\n"
        f"👤 User: @{username} (ID: {user_id})\n"
        f"🚻 Gender: {gender}\n"
        f"🎂 Age: {age}\n"
        f"🌍 Country: {country}"
    )

    try:
        await bot.send_message(ADMIN_ID, admin_text)
    except Exception as e:
        print(f"Failed to send message to admin: {e}")

    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


























