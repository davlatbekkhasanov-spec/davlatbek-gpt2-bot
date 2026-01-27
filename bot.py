import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import Message

API_TOKEN = "BOT_TOKENINGNI_BU_YERGA_QO‘YASAN"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


# /start komandasi
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "🤖 <b>Davlatbek GPT-2 bot ishga tushdi!</b>\n\n"
        "Bu bot xodimlarga topshiriqlar berish va nazorat qilish uchun yaratiladi.\n\n"
        "👉 Keyingi bosqichlarda:\n"
        "• topshiriq berish\n"
        "• status tekshirish\n"
        "• eslatmalar\n"
        "• baholash\n\n"
        "Boshlaymiz 🚀"
    )


# Bot ishga tushishi
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
