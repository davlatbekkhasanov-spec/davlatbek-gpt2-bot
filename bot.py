# bot.py
# 1) Shu fayl bilan bir papkada stock.csv tursin
# 2) TOKEN ni yoz
# 3) pip install aiogram
# 4) python bot.py

import asyncio
import csv
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

# ===================== CONFIG =====================
TOKEN = os.getenv("BOT_TOKEN", "8305656664:AAHbnnCLmR1-szaCgrt3E5z8quaSWtumdRU")  # Railway'da env: BOT_TOKEN
CSV_PATH = os.getenv("STOCK_CSV_PATH", "stock.csv")         # stock.csv yo'li
# ==================================================

router = Router()
STOCK: Dict[str, float] = {}  # name_lower -> qty


def load_stock(path: str = CSV_PATH) -> int:
    """
    stock.csv format:
    code,name,qty
    729686,Forest clean...,4.000
    """
    STOCK.clear()
    p = Path(path)

    if not p.exists():
        return 0

    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # kerakli headerlar: code, name, qty
        for row in reader:
            if not row:
                continue
            name = (row.get("name") or "").strip()
            qty_raw = (row.get("qty") or "").strip()

            if not name or not qty_raw:
                continue

            # "4,000" yoki "4.000" bo'lishi mumkin
            qty = float(qty_raw.replace(" ", "").replace(",", "."))
            STOCK[name.lower()] = qty

    return len(STOCK)


def find_product(query: str) -> Optional[Tuple[str, float]]:
    q = query.lower().strip()
    if not q:
        return None

    # 1) eng tez: ichida q bo'lsa birinchi topilganini qaytaradi
    for name_l, qty in STOCK.items():
        if q in name_l:
            return name_l, qty
    return None


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🤖 Sklad bot ishladi.\n\n"
        "✅ Qidirish: /check товар\n"
        "🔄 CSV qayta yuklash: /reload\n\n"
        "Misol: /check forest"
    )


@router.message(Command("reload"))
async def cmd_reload(message: Message):
    n = load_stock()
    if n == 0:
        await message.answer("❌ stock.csv topilmadi yoki bo‘sh.\nFayl shu papkada turganini tekshir.")
        return
    await message.answer(f"✅ Yangilandi. {n} ta товар yuklandi.")


@router.message(Command("check"))
async def cmd_check(message: Message):
    q = message.text.replace("/check", "", 1).strip()
    if not q:
        await message.answer("Товар номини ёз:\n/check шакар")
        return

    res = find_product(q)
    if not res:
        await message.answer("❌ Товар топилмади")
        return

    name_l, qty = res
    # name_l lowercase bo'lgani uchun chiroyli ko'rsatamiz:
    # (agar xohlasang original case saqlash ham mumkin, hozir soddaroq)
    await message.answer(f"📦 {name_l}\nОстаток: {qty}")


async def main():
    # Bot start paytida 1 marta yuklaymiz
    n = load_stock()
    print(f"✅ Stock loaded: {n}")

    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
