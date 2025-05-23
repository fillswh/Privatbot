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
    action = State()
    date = State()
    route = State()
    contacts = State()

start_kb = types.ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton(text="/start")]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

back_kb = types.ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton(text="🔙 Назад")]],
    resize_keyboard=True,
)

contact_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="Поділитися контактом", request_contact=True)],
        [types.KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True,
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привіт! Виберіть:\n1. Шукаю перевізника\n2. Пропоную послугу\n\nНапишіть 1 або 2."
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
        await message.answer("Будь ласка, напишіть 1 або 2.")
        return
    await message.answer("Вкажіть дату поїздки (наприклад, 2025-06-01):", reply_markup=back_kb)
    await state.set_state(BookingStates.date)

@dp.message(BookingStates.date)
async def process_date(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await message.answer(
            "Привіт! Виберіть:\n1. Шукаю перевізника\n2. Пропоную послугу\n\nНапишіть 1 або 2."
        )
        await state.set_state(BookingStates.action)
        return
    await state.update_data(date=message.text.strip())
    await message.answer("Напишіть маршрут поїздки:", reply_markup=back_kb)
    await state.set_state(BookingStates.route)

@dp.message(BookingStates.route)
async def process_route(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await message.answer(
            "Вкажіть дату поїздки (наприклад, 06-01-2025):", reply_markup=back_kb
        )
        await state.set_state(BookingStates.date)
        return
    await state.update_data(route=message.text.strip())
    await message.answer(
        "Будь ласка, поділіться вашим контактом або напишіть його вручну:",
        reply_markup=contact_kb,
    )
    await state.set_state(BookingStates.contacts)

@dp.message(BookingStates.contacts)
async def process_contacts(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await message.answer("Напишіть маршрут поїздки:", reply_markup=back_kb)
        await state.set_state(BookingStates.route)
        return

    # Если пользователь отправил контакт через кнопку
    if message.contact:
        contact_info = f"{message.contact.first_name or ''} {message.contact.last_name or ''}".strip()
        contact_phone = message.contact.phone_number
        contact = f"{contact_info} Телефон: {contact_phone}"
    else:
        # Если пользователь просто ввел текст с контактами
        contact = message.text.strip()

    await state.update_data(contacts=contact)
    data = await state.get_data()

    text_to_channel = (
        f"🚍 {data.get('action')}\n"
        f"📅 Дата: {data.get('date')}\n"
        f"📍 Маршрут: {data.get('route')}\n"
        f"📞 Контакти: {data.get('contacts')}\n"
    )

    try:
        await bot.send_message(CHANNEL_ID, text_to_channel)
        await message.answer("✅ Ваше повідомлення надіслано в канал. Дякуємо!", reply_markup=start_kb)
    except Exception as e:
        await message.answer(
            f"❌ Помилка при надсиланні повідомлення в канал: {e}", reply_markup=start_kb
        )

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
