from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class BookingStates(StatesGroup):
    action = State()       # Ищу перевозчика или предлагаю услугу
    date = State()         # Дата поездки
    route = State()        # Маршрут
    contacts = State()     # Контакты

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Что вы хотите?\n1. Ищу перевозчика\n2. Предлагаю услугу\n\nНапишите 1 или 2.")
    await state.set_state(BookingStates.action)

@dp.message(BookingStates.action)
async def process_action(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text == "1":
        await state.update_data(action="Ищу перевозчика")
    elif text == "2":
        await state.update_data(action="Предлагаю услугу")
    else:
        await message.answer("Пожалуйста, введите 1 или 2.")
        return
    await message.answer("Введите дату поездки (например, 2025-06-01):")
    await state.set_state(BookingStates.date)

@dp.message(BookingStates.date)
async def process_date(message: types.Message, state: FSMContext):
    date = message.text.strip()
    # Тут можно добавить валидацию даты при желании
    await state.update_data(date=date)
    await message.answer("Введите маршрут поездки:")
    await state.set_state(BookingStates.route)

@dp.message(BookingStates.route)
async def process_route(message: types.Message, state: FSMContext):
    route = message.text.strip()
    await state.update_data(route=route)
    await message.answer("Введите ваши контакты для связи:")
    await state.set_state(BookingStates.contacts)

@dp.message(BookingStates.contacts)
async def process_contacts(message: types.Message, state: FSMContext):
    contacts = message.text.strip()
    data = await state.get_data()
    action = data.get("action")
    date = data.get("date")
    route = data.get("route")

    text_to_channel = (
        f"🚍 {action}\n"
        f"📅 Дата: {date}\n"
        f"📍 Маршрут: {route}\n"
        f"📞 Контакты: {contacts}\n"
        f"👤 От @{message.from_user.username or message.from_user.full_name} (ID: {message.from_user.id})"
    )

    try:
        await bot.send_message(CHANNEL_ID, text_to_channel)
        await message.answer("✅ Ваше сообщение отправлено в канал. Спасибо!")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке сообщения в канал: {e}")

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
