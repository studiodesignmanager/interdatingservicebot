import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния
class Form(StatesGroup):
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await message.answer(
        "👋 Good afternoon! Please answer a few questions.\n\n"
        "✍️ This will help us better understand why you are contacting us and assist you more efficiently."
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Man", callback_data="Man"),
            InlineKeyboardButton(text="Woman", callback_data="Woman")
        ]
    ])

    await message.answer("Please select your gender:", reply_markup=keyboard)
    await state.set_state(Form.gender)

@dp.callback_query(F.data.in_(["Man", "Woman"]))
async def gender_chosen(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback_query.data)
    await callback_query.message.answer("How old are you?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Which country do you currently live in?")
    await state.set_state(Form.country)

@dp.message(Form.country)
async def process_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer(
        "Have you ever registered on international dating sites before?\n"
        "If yes, please mention which ones.\nIf no, simply write “No”."
    )
    await state.set_state(Form.registered)

@dp.message(Form.registered)
async def process_registered(message: types.Message, state: FSMContext):
    await state.update_data(registered=message.text)
    await message.answer(
        "What is your purpose for joining?\n"
        "(For example: serious relationship, marriage, friendship, etc.)"
    )
    await state.set_state(Form.purpose)

@dp.message(Form.purpose)
async def process_purpose(message: types.Message, state: FSMContext):
    await state.update_data(purpose=message.text)
    data = await state.get_data()

    text = (
        f"📝 New form received:\n\n"
        f"👤 Gender: {data.get('gender')}\n"
        f"🎂 Age: {data.get('age')}\n"
        f"🌍 Country: {data.get('country')}\n"
        f"💻 Registered before: {data.get('registered')}\n"
        f"🎯 Purpose: {data.get('purpose')}\n\n"
        f"From: @{message.from_user.username or 'No username'} (ID: {message.from_user.id})"
    )

    await bot.send_message(ADMIN_ID, text)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Contact us", url="https://t.me/interdatingservice")]
        ]
    )

    await message.answer(
        "❤️ Thank you for your answers!\n"
        "Click the button below and send us a message so we can get in touch with you.",
        reply_markup=keyboard
    )

    await state.clear()

if __name__ == "__main__":
    import asyncio
    from aiogram import Dispatcher

    async def main():
        print("Bot started... Admin ID:", ADMIN_ID)
        await dp.start_polling(bot)

    asyncio.run(main())
































