from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Определяем шаги диалога
class Form(StatesGroup):
    role = State()
    date = State()
    route = State()
    contact = State()

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("Привет! Выберите одну из опций:\n1. Ищу перевозчика\n2. Предлагаю услугу перевозки")
    await state.set_state(Form.role)

@dp.message(Form.role)
async def process_role(message: types.Message, state: FSMContext):
    role_text = message.text.strip().lower()
    if "ищу" in role_text:
        await state.update_data(role="Ищу перевозчика")
    elif "предлагаю" in role_text or "услуга" in role_text:
        await state.update_data(role="Предлагаю услугу перевозки")
    else:
        await message.answer("Пожалуйста, выберите 'Ищу перевозчика' или 'Предлагаю услугу перевозки'.")
        return
    await message.answer("Укажите дату поездки (например, 25.05.2025):")
    await state.set_state(Form.date)

@dp.message(Form.date)
async def process_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text.strip())
    await message.answer("Укажите маршрут (например, Киев — Львов):")
    await state.set_state(Form.route)

@dp.message(Form.route)
async def process_route(message: types.Message, state: FSMContext):
    await state.update_data(route=message.text.strip())
    await message.answer("Оставьте контактную информацию (телефон, Telegram и т.д.):")
    await state.set_state(Form.contact)

@dp.message(Form.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text.strip())
    data = await state.get_data()
    
    text = (
        f"📝 Новое объявление:\n"
        f"Тип: {data['role']}\n"
        f"Дата: {data['date']}\n"
        f"Маршрут: {data['route']}\n"
        f"Контакты: {data['contact']}\n"
        f"От: @{message.from_user.username or message.from_user.full_name} (ID: {message.from_user.id})"
    )

    try:
        await bot.send_message(CHANNEL_ID, text)
        await message.answer("✅ Объявление отправлено в канал.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке: {e}")

    await state.clear()

async def main():
    from aiogram.fsm.storage.memory import MemoryStorage
    dp.storage = MemoryStorage()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
