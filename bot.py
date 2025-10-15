import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import json
import os

TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_ID = 486225736

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Загружаем тексты
with open("texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)

user_data = {}
admin_mode = {}

# --- Старт ---
@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text="РУССКИЙ")
    keyboard.button(text="ENGLISH")
    await message.answer(
        "👋 Добрый день!\n\nПожалуйста, выберите язык / Please choose your language:",
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )


# --- Выбор языка ---
@dp.message(lambda message: message.text in ["РУССКИЙ", "ENGLISH"])
async def select_language(message: types.Message):
    lang = "ru" if message.text == "РУССКИЙ" else "en"
    user_data[message.from_user.id] = {"lang": lang, "answers": {}}

    keyboard = ReplyKeyboardBuilder()
    if lang == "ru":
        keyboard.button(text="Мужчина")
        keyboard.button(text="Женщина")
        text = "👋 Добрый день! Ответьте, пожалуйста, на несколько вопросов.\n\nЭто поможет нам лучше понять цель вашего обращения и помочь вам быстрее.\n\nВыберите ваш пол:"
    else:
        keyboard.button(text="Man")
        keyboard.button(text="Woman")
        text = "👋 Good afternoon! Please answer a few questions.\n\n✍️ This will help us better understand why you are contacting us and assist you more efficiently.\n\nSelect your gender:"

    await message.answer(text, reply_markup=keyboard.as_markup(resize_keyboard=True))


# --- Ответ: пол ---
@dp.message(lambda message: message.text in ["Мужчина", "Женщина", "Man", "Woman"])
async def gender_answer(message: types.Message):
    uid = message.from_user.id
    lang = user_data[uid]["lang"]
    user_data[uid]["answers"]["gender"] = message.text

    if lang == "ru":
        await message.answer("Сколько вам полных лет?")
    else:
        await message.answer("How old are you?")


# --- Возраст ---
@dp.message(lambda message: message.text.isdigit())
async def age_answer(message: types.Message):
    uid = message.from_user.id
    lang = user_data[uid]["lang"]
    user_data[uid]["answers"]["age"] = message.text

    if lang == "ru":
        await message.answer("В какой стране вы проживаете постоянно?")
    else:
        await message.answer("In which country do you permanently live?")


# --- Страна ---
@dp.message(lambda message: message.from_user.id in user_data and "country" not in user_data[message.from_user.id]["answers"])
async def country_answer(message: types.Message):
    uid = message.from_user.id
    lang = user_data[uid]["lang"]
    user_data[uid]["answers"]["country"] = message.text

    if lang == "ru":
        await message.answer("Где вы были зарегистрированы ранее (например, Tinder, Badoo и т.д.)?")
    else:
        await message.answer("Where were you registered before (for example, Tinder, Badoo, etc.)?")


# --- Регистрация ---
@dp.message(lambda message: message.from_user.id in user_data and "registered_before" not in user_data[message.from_user.id]["answers"])
async def registered_before_answer(message: types.Message):
    uid = message.from_user.id
    lang = user_data[uid]["lang"]
    user_data[uid]["answers"]["registered_before"] = message.text

    if lang == "ru":
        await message.answer("Какова ваша цель знакомства?")
    else:
        await message.answer("What is your purpose of dating?")


# --- Цель знакомства ---
@dp.message(lambda message: message.from_user.id in user_data and "purpose" not in user_data[message.from_user.id]["answers"])
async def purpose_answer(message: types.Message):
    uid = message.from_user.id
    lang = user_data[uid]["lang"]
    user_data[uid]["answers"]["purpose"] = message.text

    # Формируем отчет для админа
    answers = user_data[uid]["answers"]
    name = message.from_user.full_name or "No name"
    username = f"@{message.from_user.username}" if message.from_user.username else "No username"

    report = (
        f"📝 New form received:\n\n"
        f"👤 User: {name}\n"
        f"⚧ Gender: {answers.get('gender')}\n"
        f"📅 Age: {answers.get('age')}\n"
        f"🌍 Country: {answers.get('country')}\n"
        f"💻 Registered before: {answers.get('registered_before')}\n"
        f"🎯 Purpose: {answers.get('purpose')}\n\n"
        f"From: {username} (ID: {uid})"
    )

    await bot.send_message(ADMIN_ID, report)

    if lang == "ru":
        await message.answer("✅ Спасибо! Мы получили ваши ответы. Скоро с вами свяжется наш менеджер.")
    else:
        await message.answer("✅ Thank you! We have received your answers. Our manager will contact you soon.")

    del user_data[uid]


# --- Запуск ---
async def main():
    print("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())









































