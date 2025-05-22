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
    action = State()       # Шукаю перевізника або надаю послуги пасажирських перевезень
    date = State()         # Дата поїздки
    route = State()        # Маршрут
    contacts = State()     # Контакти

start_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="/start")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привіт! Виберіть ?\n1. Шукаю перевізника\n2. Пропоную послугу\n\nНапишіть 1 або 2.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(BookingStates.action)

@dp.message(BookingStates.action)
async def process_action(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if text == "1":
        await state.update_data(action="Шукаю перевізника")
    elif text == "2":
        await state.update_data(action="Пропоную послугу")
    else:
        await message.answer("Будь-ласка, Напишіть 1 або 2.")
        return
    await message.answer("Вкажіть дату поїздки (наприклад, 2025-06-01):")
    await state.set_state(BookingStates.date)

@dp.message(BookingStates.date)
async def process_date(message: types.Message, state: FSMContext):
    date = message.text.strip()
    # Тут можна додати валідацію дати при бажанні
    await state.update_data(date=date)
    await message.answer("Напишіть маршрут поїздки:")
    await state.set_state(BookingStates.route)

@dp.message(BookingStates.route)
async def process_route(message: types.Message, state: FSMContext):
    route = message.text.strip()
    await state.update_data(route=route)
    await message.answer("Вкажіть ваші контакти для зв'язку")
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
        f"📞 Контакти: {contacts}\n"
        f"👤 Від @{message.from_user.username or message.from_user.full_name} (ID: {message.from_user.id})"
    )

    try:
        await bot.send_message(CHANNEL_ID, text_to_channel)
        await message.answer(
            "✅ Ваше повідомлення надіслано в канал. Дякуємо!",
            reply_markup=start_kb
        )
    except Exception as e:
        await message.answer(f"❌ Помилка при надсиланні повідомлення в канал: {e}")

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
   
