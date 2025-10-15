import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

print("BOT_TOKEN:", BOT_TOKEN)  # проверка, что токен загрузился

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found! Check your .env file.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("✅ Bot is running correctly!")

if __name__ == "__main__":
    print(f"Bot started... Admin ID: {ADMIN_ID}")
    executor.start_polling(dp, skip_updates=True)





















