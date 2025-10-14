import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import json

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- Load texts ----------
def load_texts():
    with open("texts.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_texts(data):
    with open("texts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

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

    # save previous answer
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
        f"Username: {username}\n\n"
        f"Gender: {data.get('Gender')}\n"
        f"Age: {data.get('Age')}\n"
        f"Country: {data.get('Country')}\n"
        f"Registered before: {data.get('RegisteredBefore')}\n"
        f"Purpose: {data.get('Purpose')}"
    )

    await bot.send_message(ADMIN_ID, text)

# ---------- Admin panel ----------
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    builder = InlineKeyboardBuilder()
    for key in texts.keys():
        builder.button(text=f"Edit {key}", callback_data=f"edit_{key}")
    builder.adjust(1)
    await message.answer("🛠 Select text to edit:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("edit_"))
async def edit_text(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    key = callback.data.replace("edit_", "")
    await callback.message.answer(f"Send new text for *{key}*:", parse_mode="Markdown")
    user_data[callback.from_user.id] = {"edit_key": key}
    await callback.answer()

@dp.message(F.text)
async def update_text(message: types.Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID and "edit_key" in user_data.get(user_id, {}):
        key = user_data[user_id]["edit_key"]
        texts[key] = message.text
        save_texts(texts)
        del user_data[user_id]
        await message.answer(f"✅ Text for *{key}* updated.", parse_mode="Markdown")

# ---------- Run ----------
async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

