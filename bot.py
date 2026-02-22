# bot.py
# 1) stock.csv shu fayl yonida tursin (code,name,qty)
# 2) TOKEN ni qo'y
# 3) pip install aiogram
# 4) python bot.py

import asyncio
import csv
import os
from typing import Dict, Tuple, Optional

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN", "8305656664:AAHbnnCLmR1-szaCgrt3E5z8quaSWtumdRU")

router = Router()

# key: normalized name -> (original_name, qty)
STOCK: Dict[str, Tuple[str, float]] = {}

# ====== sozlarni "yumshatish" (ruscha/uzcha aralash) ======
ALIASES = {
    "shakar": "сахар",
    "saxar": "сахар",
    "ruchka": "ручка",
    "qalam": "ручка",
}

STOP_WORDS = {
    "topib", "ber", "berchi", "bering", "beringchi", "bervor", "bervoring",
    "desa", "de", "deb", "shuni", "shu", "mana", "ilimos", "iltimos",
    "top", "topibber", "topibberchi", "kerak", "bormi",
    "bor", "yoqmi", "yo'qmi", "yoq", "yo'q",
    "menga", "bizga", "meni", "mni", "menga",
}

def normalize(text: str) -> str:
    return (
        text.lower()
        .replace("ё", "е")
        .replace("’", "'")
        .strip()
    )

def clean_query(text: str) -> str:
    t = normalize(text)

    # "/check" yozilsa olib tashlaymiz
    if t.startswith("/check"):
        t = t.replace("/check", "", 1).strip()

    # aliaslarni almashtiramiz
    for k, v in ALIASES.items():
        t = t.replace(k, v)

    # stop so'zlarni olib tashlaymiz
    parts = [p for p in t.split() if p and p not in STOP_WORDS]

    return " ".join(parts).strip()

def load_stock(path: str = "stock.csv") -> int:
    STOCK.clear()
    if not os.path.exists(path):
        print("❌ stock.csv topilmadi")
        return 0

    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or "").strip()
            qty_raw = (row.get("qty") or "").strip()
            if not name or not qty_raw:
                continue
            qty = float(qty_raw.replace(" ", "").replace(",", "."))
            STOCK[normalize(name)] = (name, qty)

    print(f"✅ Yuklandi: {len(STOCK)} ta товар")
    return len(STOCK)

def find_product(query: str) -> Optional[Tuple[str, float]]:
    q = clean_query(query)
    if not q:
        return None

    # aniq moslik
    if q in STOCK:
        return STOCK[q]

    # ichidan qidirish
    for key, (orig, qty) in STOCK.items():
        if q in key:
            return orig, qty

    return None


# ====== handlers ======
@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "🤖 Склад бот тайёр.\n"
        "Иккала усул ишлайди:\n"
        "1) /check товар\n"
        "2) Оддий ёз: 'ручка борми' ёки 'шакар топиб бер'\n\n"
        "CSV янгиланса: /reload"
    )

@router.message(Command("reload"))
async def reload_cmd(message: Message):
    n = load_stock()
    await message.answer(f"✅ Янгиланди: {n} та товар")

@router.message(Command("check"))
async def check_cmd(message: Message):
    q = message.text
    res = find_product(q)
    if not res:
        await message.answer("❌ Товар топилмади")
        return
    name, qty = res
    await message.answer(f"📦 {name}\nОстаток: {qty}")

# /check yozmasa ham tutib oladi:
# F.text bo'lsa va command bo'lmasa
@router.message(F.text)
async def any_text_search(message: Message):
    text = message.text.strip()

    # command bo'lsa tegmaymiz
    if text.startswith("/"):
        return

    # juda qisqa bo'lsa javob bermaymiz (spam bo'lmasin)
    if len(text) < 3:
        return

    res = find_product(text)
    if not res:
        await message.answer("❌ Товар топилмади")
        return

    name, qty = res
    await message.answer(f"📦 {name}\nОстаток: {qty}")


async def main():
    load_stock()
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
