import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio

# === CONFIG ===
TOKEN = "твой_токен_сюда"
ADMIN_ID = 5123692910
TEXTS_FILE = "texts.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# === LOAD TEXTS ===
def load_texts():
    try:
        with open(TEXTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading texts: {e}")
        return {}

texts = load_texts()

# === START ===
@dp.message(Command("start"))
async def start(message: types.Message):
    logging.info(f"User {message.from_user.id} started the bot")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ENGLISH"), KeyboardButton(text="РУССКИЙ")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "👋 Please select your language / Пожалуйста, выберите язык:",
        reply_markup=keyboard
    )

# === LANGUAGE CHOICE ===
@dp.message(lambda msg: msg.text in ["ENGLISH", "РУССКИЙ"])
async def choose_language(message: types.Message):
    lang = "en" if message.text == "ENGLISH" else "ru"
    await start_survey(message, lang)

async def start_survey(message, lang):
    t = texts.get(lang, {})
    if not t:
        await message.answer("Texts not loaded. Please contact admin.")
        return

    gender_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Man" if lang == "en" else "Мужчина"),
             KeyboardButton(text="Woman" if lang == "en" else "Женщина")]
        ],
        resize_keyboard=True
    )
    await message.answer(t["greeting"], reply_markup=gender_kb)

# === GENDER QUESTION ===
@dp.message(lambda msg: msg.text in ["Man", "Woman", "Мужчина", "Женщина"])
async def ask_age(message: types.Message):
    lang = "en" if message.text in ["Man", "Woman"] else "ru"
    t = texts[lang]
    await message.answer(t["age_question"])

# === OTHER QUESTIONS ===
@dp.message(lambda msg: msg.text.isdigit())
async def ask_country(message: types.Message):
    user_data = {"age": message.text}
    lang = "en" if message.text.isascii() else "ru"
    t = texts[lang]
    await message.answer(t["country_question"])

# === ADMIN COMMAND ===
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Access denied.")
        return
    await message.answer("✅ Admin panel loaded. Texts ready for editing.")

# === MAIN LOOP ===
async def main():
    logging.info(f"Bot started... Admin ID: {ADMIN_ID}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())










