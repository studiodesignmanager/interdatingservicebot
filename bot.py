import json
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import asyncio

TOKEN = "твой_токен"
ADMIN_ID = 5123692910
TEXTS_FILE = "texts.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# ===== FSM =====
class Form(StatesGroup):
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()


# ===== LOAD TEXTS =====
def load_texts():
    try:
        with open(TEXTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading texts: {e}")
        return {}

texts = load_texts()


# ===== START =====
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="ENGLISH"), KeyboardButton(text="РУССКИЙ")]],
        resize_keyboard=True
    )
    await message.answer("👋 Please select your language / Пожалуйста, выберите язык:", reply_markup=keyboard)
    await state.clear()


# ===== LANGUAGE CHOICE =====
@dp.message(F.text.in_(["ENGLISH", "РУССКИЙ"]))
async def choose_language(message: types.Message, state: FSMContext):
    lang = "en" if message.text == "ENGLISH" else "ru"
    await state.update_data(lang=lang)
    t = texts[lang]

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Man" if lang == "en" else "Мужчина"),
             KeyboardButton(text="Woman" if lang == "en" else "Женщина")]
        ],
        resize_keyboard=True
    )

    await message.answer(t["greeting"], reply_markup=keyboard)
    await state.set_state(Form.gender)


# ===== GENDER =====
@dp.message(Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    t = texts[lang]

    await state.update_data(gender=message.text)
    await message.answer(t["age_question"], reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.age)


# ===== AGE =====
@dp.message(Form.age)
async def process_age(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    t = texts[lang]

    await state.update_data(age=message.text)
    await message.answer(t["country_question"])
    await state.set_state(Form.country)


# ===== COUNTRY =====
@dp.message(Form.country)
async def process_country(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    t = texts[lang]

    await state.update_data(country=message.text)
    await message.answer(t["registered_question"])
    await state.set_state(Form.registered)


# ===== REGISTERED =====
@dp.message(Form.registered)
async def process_registered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    t = texts[lang]

    await state.update_data(registered=message.text)
    await message.answer(t["purpose_question"])
    await state.set_state(Form.purpose)


# ===== PURPOSE =====
@dp.message(Form.purpose)
async def process_purpose(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    t = texts[lang]

    await state.update_data(purpose=message.text)
    user_data = await state.get_data()

    # Send to admin
    info = (
        f"📩 New response from @{message.from_user.username or 'NoUsername'}\n\n"
        f"Gender: {user_data['gender']}\n"
        f"Age: {user_data['age']}\n"
        f"Country: {user_data['country']}\n"
        f"Registered before: {user_data['registered']}\n"
        f"Purpose: {user_data['purpose']}"
    )
    await bot.send_message(ADMIN_ID, info)

    # Thank user
    await message.answer(t["thank_you"])
    await state.clear()


# ===== MAIN =====
async def main():
    logging.info("Bot started...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())












