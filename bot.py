import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import json

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # личный ID администратора

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- Load texts ----------
def load_texts():
    with open("texts.json", "r", encoding="utf-8") as f:
        return json.load(f)

texts = load_texts()

# ---------- User states ----------
user_data = {}

# ---------- Start command ----------
@dp.message(Command("start"))
async def start(message: types.Message):
    user_data[message.from_user.id] = {"step": 0, "answers": {}}

    builder = InlineKeyboardBuilder()
    builder.button(text="Man", callback_data="gender_man")
    builder.button(text="Woman", callback_data="gender_woman")
    builder.adjust(2)

    await message.answer(
        f"{texts['greeting']}\n\n{texts['choose_gender']}",
        reply_markup=builder.as_markup()
    )

# ---------- Gender choice ----------
@dp.callback_query(F.data.startswith("gender_"))
async def choose_gender(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    gender = "Man" if callback.data == "gender_man" else "Woman"
    user_data[user_id]["answers"]["Gender"] = gender
    user_data[user_id]["step"] = 1
    await callback.message.answer(texts["age_question"])
    await callback.answer()

# ---------- Answers flow ----------
@dp.message()
async def handle_answers(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        await message.answer("Please start again with /start")
        return

    step = user_data[user_id]["step"]
    answer = message.text.strip()
    # Сохраняем ответ в зависимости от шага
    if step == 1:
        user_data[user_id]["answers"]["Age"] = answer
        user_data[user_id]["step"] = 2
        await message.answer(texts["country_question"])
    elif step == 2:
        user_data[user_id]["answers"]["Country"] = answer
        user_data[user_id]["step"] = 3
        await message.answer(texts["registered_question"])
    elif step == 3:
        user_data[user_id]["answers"]["RegisteredBefore"] = answer
        user_data[user_id]["step"] = 4
        await message.answer(texts["purpose_question"])
    elif step == 4:
        user_data[user_id]["answers"]["Purpose"] = answer
        await message.answer(texts["thank_you"], reply_markup=contact_button())
        await send_results_to_admin(message.from_user)
        del user_data[user_id]

# ---------- Contact button ----------
def contact_button():
    builder = InlineKeyboardBuilder()
    builder.button(text="📩 CONTACT US", url="https://t.me/interdatingservice")
    return builder.as_markup()

# ---------- Send results to admin ----------
async def send_results_to_admin(user: types.User):
    data = user_data.get(user.id, {}).get("answers", {})
    if not data:
        return

    username = f"@{user.username}" if user.username else f"tg://user?id={user.id}"

    text = (
        f"📨 New user completed the survey!\n\n"
        f"User: {username}\n"
        f"Gender: {data.get('Gender')}\n"
        f"Age: {data.get('Age')}\n"
        f"Country: {data.get('Country')}\n"
        f"Registered before: {data.get('RegisteredBefore')}\n"
        f"Purpose: {data.get('Purpose')}"
    )

    await bot.send_message(ADMIN_ID, text)

# ---------- Run ----------
async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



