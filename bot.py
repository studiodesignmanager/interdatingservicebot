import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# --- Bot initialization ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Start command handler ---
@dp.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Man"), KeyboardButton(text="Woman")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "👋 Good afternoon! Please answer a few questions.\n\n"
        "✍️ This will help us better understand why you are contacting us and assist you more efficiently.\n\n"
        "Please select your gender:",
        reply_markup=keyboard
    )

# --- Gender selection handler ---
@dp.message(F.text.in_(["Man", "Woman"]))
async def gender_chosen(message: Message):
    await message.answer("How old are you?")

# --- Main loop ---
async def main():
    print(f"✅ Bot started successfully.\nAdmin ID: {ADMIN_ID}\nToken: {BOT_TOKEN[:10]}...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



























