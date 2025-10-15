









import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Text
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

# Загрузка токенов
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Класс состояний
class Form(StatesGroup):
    Gender = State()
    Age = State()
    Country = State()
    Registered = State()
    Purpose = State()

# Словарь для хранения ответов пользователей
user_data = {}

# Клавиатура для Contact Us
contact_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📩 CONTACT US", url="https://t.me/interdatingservice")]
    ]
)

# /start
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_data.setdefault(message.from_user.id, {"answers": {}, "name": message.from_user.full_name})
    await message.answer(
        "👋 Good afternoon! Please answer a few questions.\n\n✍️ This will help us better understand why you are contacting us and assist you more efficiently."
    )
    # Выбор пола
    gender_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Man", callback_data="gender_man"),
                InlineKeyboardButton(text="Woman", callback_data="gender_woman")
            ]
        ]
    )
    await message.answer("Please select your gender:", reply_markup=gender_keyboard)
    await state.set_state(Form.Gender)

# Обработка пола
@dp.callback_query(Text(startswith="gender_"))
async def gender_choice(callback: types.CallbackQuery, state: FSMContext):
    gender = callback.data.split("_")[1].capitalize()
    user_data[callback.from_user.id]["answers"]["Gender"] = gender
    await callback.message.edit_reply_markup()
    await callback.message.answer("🎂 How old are you?")
    await state.set_state(Form.Age)

# Возраст
@dp.message(Form.Age)
async def ask_age(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["Age"] = message.text
    await message.answer("🌍 Which country do you currently live in?")
    await state.set_state(Form.Country)

# Страна
@dp.message(Form.Country)
async def ask_country(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["Country"] = message.text
    await message.answer(
        "💻 Have you ever registered on international dating sites before?\n"
        "If yes, please mention which ones.\nIf no, simply write “No”."
    )
    await state.set_state(Form.Registered)

# Зарегистрирован ли
@dp.message(Form.Registered)
async def ask_registered(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["Registered"] = message.text
    await message.answer(
        "🎯 What is your purpose for joining?\n(For example: serious relationship, marriage, friendship, etc.)"
    )
    await state.set_state(Form.Purpose)

# Цель
@dp.message(Form.Purpose)
async def ask_purpose(message: types.Message, state: FSMContext):
    user_data[message.from_user.id]["answers"]["Purpose"] = message.text

    # Формируем отчёт для админа
    data = user_data[message.from_user.id]["answers"]
    full_name = user_data[message.from_user.id]["name"]
    username = message.from_user.username or "N/A"
    report = (
        f"📝 User: {full_name}\n"
        f"👤 Gender: {data.get('Gender','')}\n"
        f"🎂 Age: {data.get('Age','')}\n"
        f"🌍 Country: {data.get('Country','')}\n"
        f"💻 Registered before: {data.get('Registered','')}\n"
        f"🎯 Purpose: {data.get('Purpose','')}\n"
        f"\nFrom: @{username} (ID: {message.from_user.id})"
    )

    await bot.send_message(chat_id=ADMIN_ID, text=report)

    # Финальное сообщение пользователю с кнопкой
    await message.answer(
        "❤️ Thank you for your answers!\nClick the button below and send us a message so we can get in touch with you.",
        reply_markup=contact_keyboard
    )
    await state.clear()

# Запуск бота
if __name__ == "__main__":
    import asyncio
    from aiogram import F
    from aiogram.types import CallbackQuery

    async def main():
        from aiogram import Router

        router = Router()
        dp.include_router(router)
        await dp.start_polling(bot)

    asyncio.run(main())


































