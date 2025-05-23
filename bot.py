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

# Кнопка для отправки контакта (номер телефона)
contact_kb = types.ReplyKeyboardMarkup(
    keyboard=[[types.KeyboardButton(text="Поділитися контактом", request_contact=True)],
              [types.KeyboardButton(text="🔙 Назад")]],
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
        await message.answer("Вкажіть дату поїздки (наприклад, 2025-06-01):", reply_markup=back_kb)
        await state.set_state(BookingStates.date)
        return
    await state.update_data(route=message.text.strip())
    await message.answer(
        "Вкажіть ваші контакти для зв'язку або поділіться контактом через кнопку нижче:",
        reply_markup=contact_kb,
    )
    await state.set_state(BookingStates.contacts)

@dp.message(BookingStates.contacts, F.content_type == "text")
async def process_contacts_text(message: types.Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await message.answer("Напишіть маршрут поїздки:", reply_markup=back_kb)
        await state.set_state(BookingStates.route)
        return
    # Просто текстовый ввод контактов (если не поделились контактом через кнопку)
    await state.update_data(contacts=message.text.strip())
    await send_summary_and_finish(message, state)

@dp.message(BookingStates.contacts, F.content_type == "contact")
async def process_contacts_contact(message: types.Message, state: FSMContext):
    contact = message.contact
    # Берём номер телефона из контакта
    phone_number = contact.phone_number
    # Можно дополнительно получить имя контакта из message.contact.first_name и last_name
    contact_info = f"{phone_number} (ім'я: {contact.first_name or 'Н/Д'})"
    await state.update_data(contacts=contact_info)
    await send_summary_and_finish(message, state)

async def send_summary_and_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()

    text_to_channel = (
        f"🚍 {data.get('action')}\n"
        f"📅 Дата: {data.get('date')}\n"
        f"📍 Маршрут: {data.get('route')}\n"
        f"📞 Контакти: {data.get('contacts')}\n"
        f"👤 Від @{message.from_user.username or message.from_user.full_name} (ID: {message.from_user.id})"
    )

    try:
        await bot.send_message(CHANNEL_ID, text_to_channel)
        await message.answer("✅ Ваше повідомлення надіслано в канал. Дякуємо!", reply_markup=start_kb)
    except Exception as e:
        await message.answer(f"❌ Помилка при надсиланні повідомлення в канал: {e}", reply_markup=start_kb)

    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
