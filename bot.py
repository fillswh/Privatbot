from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import os
from dotenv import load_dotenv

# Завантажуємо змінні з .env або Railway
load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Клавіатура з кнопкою /start
start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Напиши мені повідомлення — я надішлю його до каналу.", reply_markup=start_kb)

@dp.message(F.text)
async def forward_to_channel(message: types.Message):
    user = message.from_user
    text = (
        f"✉️ Повідомлення від @{user.username or user.full_name} (ID: {user.id}):\n\n"
        f"{message.text}"
    )
    try:
        await bot.send_message(CHANNEL_ID, text)
        await message.answer("✅ Повідомлення надіслано до каналу.", reply_markup=start_kb)
    except Exception as e:
        await message.answer(f"❌ Помилка при надсиланні повідомлення до каналу: {e}", reply_markup=start_kb)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
