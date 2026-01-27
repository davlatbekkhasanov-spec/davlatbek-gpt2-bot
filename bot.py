import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

TOKEN = os.getenv("8305656664:AAHbnnCLmR1-szaCgrt3E5z8quaSWtumdRU")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_handler(message):
    await message.answer("✅ Davlatbek GPT-2 bot ishlayapti")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
