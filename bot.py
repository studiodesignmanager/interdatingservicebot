import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio
import json

# --- LOAD ENV ---
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")        # <-- имя переменной должно совпадать с .env
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env!")

logging.basicConfig(level=logging.INFO)

# --- INIT BOT ---
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- LOAD TEXTS ---
with open("texts.json", "r", encoding="utf-8") as f:
    texts = json.load(f)

# --- STATES ---
class Form(StatesGroup):
    gender = State()
    age = State()
    country = State()
    registered = State()
    purpose = State()

# --- START HANDLER ---
@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        texts["en"]["greeting"],
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Man", callback_data="Man"),
                    InlineKeyboardButton(text="Woman", callback_data="Woman")
                ]
            ]
        )
    )
    await state.set_state(Form.gender)





































