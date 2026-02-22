import asyncio
import csv
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command

TOKEN = "8305656664:AAHbnnCLmR1-szaCgrt3E5z8quaSWtumdRU"

router = Router()
STOCK = {}


# -------- TEXT NORMALIZE --------
def normalize(text: str) -> str:
    text = text.lower()

    replace_map = {
        "ў": "у",
        "қ": "к",
        "ғ": "г",
        "ҳ": "х",
        "ё": "е",
    }

    for k, v in replace_map.items():
        text = text.replace(k, v)

    return text.strip()


# -------- LOAD CSV (AUTO ENCODING FIX) --------
def load_stock():
    STOCK.clear()

    if not os.path.exists("stock.csv"):
        print("stock.csv yo'q")
        return

    # UTF-8 ishlamasa CP1251 o'qiydi
    try:
        f = open("stock.csv", encoding="utf-8")
        f.read(100)
        f.close()
        encoding = "utf-8"
    except:
        encoding = "cp1251"

    with open("stock.csv", encoding=encoding) as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row["name"]
            qty = float(row["qty"].replace(",", "."))

            STOCK[normalize(name)] = (name, qty)

    print("✅ Yuklandi:", len(STOCK))


# -------- SEARCH --------
def find_product(query: str):
    q = normalize(query)

    for key, value in STOCK.items():
        if q in key:
            return value

    return None


# -------- COMMANDS --------
@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "🤖 Склад бот тайёр\n"
        "Оддий ёз: ручка борми\n"
        "ёки /check ручка"
    )


@router.message(Command("check"))
async def check_cmd(message: Message):
    result = find_product(message.text)

    if not result:
        await message.answer("❌ Товар топилмади")
        return

    name, qty = result
    await message.answer(f"📦 {name}\nОстаток: {qty}")


# /check yozmasdan ham ishlaydi
@router.message(F.text)
async def any_text(message: Message):
    if message.text.startswith("/"):
        return

    result = find_product(message.text)

    if not result:
        await message.answer("❌ Товар топилмади")
        return

    name, qty = result
    await message.answer(f"📦 {name}\nОстаток: {qty}")


# -------- START --------
async def main():
    load_stock()

    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
