# bot.py  (Bitta fayl, /check yozmasa ham ishlaydi)
# 1) stock.csv shu fayl yonida tursin (header: code,name,qty)
# 2) TOKEN ni qo'y (yoki env: BOT_TOKEN)
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
CSV_PATH = os.getenv("STOCK_CSV_PATH", "stock.csv")

router = Router()

# key: normalized name -> (original_name, qty)
STOCK: Dict[str, Tuple[str, float]] = {}

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
    "menga", "bizga", "meni", "mni",
}


def normalize(text: str) -> str:
    text = (text or "").lower().strip()

    # Uz/Ru kirill farqlarini bir xilga keltiramiz
    replace_map = {
        "ў": "у",
        "қ": "к",
        "ғ": "г",
        "ҳ": "х",
        "ё": "е",
        "’": "'",
    }
    for k, v in replace_map.items():
        text = text.replace(k, v)

    # Ortiqcha bo'shliqlar
    text = " ".join(text.split())
    return text


def clean_query(text: str) -> str:
    t = normalize(text)

    # /check yozilgan bo'lsa olib tashlaymiz
    if t.startswith("/check"):
        t = t.replace("/check", "", 1).strip()

    # aliaslar (latin -> ruscha so'z)
    for k, v in ALIASES.items():
        t = t.replace(k, v)

    parts = [p for p in t.split() if p and p not in STOP_WORDS]
    return " ".join(parts).strip()


def load_stock(path: str = CSV_PATH) -> int:
    STOCK.clear()

    if not os.path.exists(path):
        print("❌ stock.csv topilmadi:", path)
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


def find_product(text_query: str) -> Optional[Tuple[str, float]]:
    q = clean_query(text_query)
    if not q:
        return None

    # 1) aniq moslik
    if q in STOCK:
        return STOCK[q]

    # 2) ichidan qidirish
    for key, (orig, qty) in STOCK.items():
        if q in key:
            return orig, qty

    return None


@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "🤖 Склад бот тайёр.\n"
        "1) /check товар\n"
        "2) Оддий ёз: 'ручка борми' ёки 'шакар топиб бер'\n"
        "CSV янгиланса: /reload"
    )


@router.message(Command("reload"))
async def reload_cmd(message: Message):
    n = load_stock()
    await message.answer(f"✅ Янгиланди: {n} та товар")


@router.message(Command("check"))
async def check_cmd(message: Message):
    res = find_product(message.text)
    if not res:
        await message.answer("❌ Товар топилмади")
        return
    name, qty = res
    await message.answer(f"📦 {name}\nОстаток: {qty}")


# /check yozilmasa ham qidiradi
@router.message(F.text)
async def any_text_search(message: Message):
    text = (message.text or "").strip()
    if not text or text.startswith("/"):
        return

    # juda qisqa bo'lsa javob bermaymiz
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
