import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv
import asyncio

# Загружаем .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

print("BOT_TOKEN:", BOT_TOKEN)

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found! Check your .env file.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("✅ Bot is running correctly!")

async def main():
    print(f"Bot started... Admin ID: {ADMIN_ID}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())























