
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
API_TOKEN = os.getenv("7984024778:AAGUXeHYYu5c_dVmYX5tdJ3vbt-6YLfoYEc")
CHANNEL_ID = os.getenv("@htokudy")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Напиши мне сообщение — я отправлю его в канал.")

@dp.message(F.text)
async def forward_to_channel(message: types.Message):
    user = message.from_user
    text = (
        f"✉️ Сообщение от @{user.username or user.full_name} (ID: {user.id}):\n\n"
        f"{message.text}"
    )
    try:
        await bot.send_message(CHANNEL_ID, text)
        await message.answer("✅ Сообщение отправлено в канал.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке сообщения в канал: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
