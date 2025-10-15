import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

# Хранилище данных пользователей
user_data = {}


class Form(StatesGroup):
    gender = State()
    age = State()
    country = State()
    registered_before = State()
    purpose = State()


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_data[message.from_user.id] = {"answers": {}}

    await message.answer(
        "👋 Good afternoon! Please answer a few questions.\n\n"
        "✍️ This will help us better understand why you are contacting us and assist you more efficiently.\n\n"
        "Please select your gender:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Man"), types.KeyboardButton(text="Woman")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        ),
    )
    await state.set_state(Form.gender)


@dp.message(Form.gender)
async def ask_age(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["Gender"] = message.text
    await message.answer("How old are you?")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def ask_country(message: types.Message, state: FSMContext):
    user_data.setdefault(message.from_user.id, {"answers": {}})
    user_data[message.from_user.id]["answers"]["Age"] = message.text
    await message.answer("Which country do you currently live in?")
    await state.set_state(Form.country)


@dp.message(Form.country)
async def ask_registered_before(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["Country"] = message.text
    await message.answer(
        "Have you ever registered on international dating sites before?\n"
        "If yes, please mention which ones.\n"
        "If no, simply write “No”."
    )
    await state.set_state(Form.registered_before)


@dp.message(Form.registered_before)
async def ask_purpose(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["RegisteredBefore"] = message.text
    await message.answer(
        "What is your purpose for joining?\n"
        "(For example: serious relationship, marriage, friendship, etc.)"
    )
    await state.set_state(Form.purpose)


@dp.message(Form.purpose)
async def finish_form(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["Purpose"] = message.text

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
        ]
    )

    await message.answer(
        "❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you.",
        reply_markup=keyboard
    )

    answers = user_data[message.from_user.id]["answers"]

    admin_message = (
        "📝 <b>New form received:</b>\n\n"
        f"👤 <b>User:</b> {answers.get('Name', 'Anonymous')}\n"
        f"🚹 <b>Gender:</b> {answers.get('Gender', '-')}\n"
        f"📅 <b>Age:</b> {answers.get('Age', '-')}\n"
        f"🌍 <b>Country:</b> {answers.get('Country', '-')}\n"
        f"💻 <b>Registered before:</b> {answers.get('RegisteredBefore', '-')}\n"
        f"🎯 <b>Purpose:</b> {answers.get('Purpose', '-')}\n\n"
        f"From: @{message.from_user.username or '—'} (ID: {message.from_user.id})"
    )

    await bot.send_message(ADMIN_ID, admin_message, parse_mode="HTML")

    await state.clear()


async def main():
    logging.info("Bot started... Admin ID: %s", ADMIN_ID)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")






































