import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

API_TOKEN = "BOT_TOKENINGNI_BU_YERGA_QO‘YASAN"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Xodimlar (hozircha xotirada)
employees = {}  # user_id: full_name


@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "🤖 <b>Davlatbek GPT-2 bot ishga tushdi!</b>\n\n"
        "👤 Xodim bo‘lsangiz /register buyrug‘ini yozing.\n"
        "📋 Ro‘yxatni ko‘rish: /employees"
    )


@dp.message(Command("register"))
async def register_handler(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name

    if user_id in employees:
        await message.answer("⚠️ Siz allaqachon ro‘yxatdan o‘tgansiz.")
        return

    employees[user_id] = full_name
    await message.answer(
        f"✅ <b>Ro‘yxatdan o‘tdingiz!</b>\n"
        f"👤 Ism: {full_name}"
    )


@dp.message(Command("employees"))
async def employees_handler(message: Message):
    if not employees:
        await message.answer("📭 Hozircha hech kim ro‘yxatdan o‘tmagan.")
        return

    text = "👥 <b>Ro‘yxatdan o‘tgan xodimlar:</b>\n\n"
    for i, name in enumerate(employees.values(), start=1):
        text += f"{i}. {name}\n"

    await message.answer(text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
