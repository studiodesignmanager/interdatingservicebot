import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

print("BOT_TOKEN:", TOKEN)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Старт
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

# Обработка выбора пола
@dp.message(F.text.in_(["Man", "Woman"]))
async def get_gender(message: Message):
    await message.answer("How old are you?")

async def main():
    print(f"Bot started... Admin ID: {ADMIN_ID}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
EOF

























