import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

API_TOKEN = "8305656664:AAHbnnCLmR1-szaCgrt3E5z8quaSWtumdRU"

# ===== ADMIN ID =====
ADMINS = {5732350707}

logging.basicConfig(level=logging.INFO)

bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ===== DATA (hozircha RAM) =====
employees = {}   # user_id: full_name
tasks = []       # list of dicts


# ===== START =====
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🤖 <b>Aqlli topshiriqlar boti</b>\n\n"
        "👤 Xodimlar: /register\n"
        "🧑‍💼 Adminlar: /task\n"
        "📋 Ro‘yxat: /employees"
    )


# ===== REGISTER =====
@dp.message(Command("register"))
async def register(message: Message):
    uid = message.from_user.id
    name = message.from_user.full_name

    if uid in employees:
        await message.answer("⚠️ Siz allaqachon ro‘yxatdan o‘tgansiz.")
        return

    employees[uid] = name
    await message.answer(f"✅ Ro‘yxatdan o‘tdingiz: <b>{name}</b>")


# ===== EMPLOYEES =====
@dp.message(Command("employees"))
async def list_employees(message: Message):
    if not employees:
        await message.answer("📭 Xodimlar yo‘q.")
        return

    text = "👥 <b>Xodimlar:</b>\n\n"
    for i, name in enumerate(employees.values(), 1):
        text += f"{i}. {name}\n"

    await message.answer(text)


# ===== CREATE TASK =====
@dp.message(Command("task"))
async def create_task(message: Message):
    if message.from_user.id not in ADMINS:
        await message.answer("⛔ Siz admin emassiz.")
        return

    if not employees:
        await message.answer("⚠️ Avval xodimlar ro‘yxatdan o‘tsin.")
        return

    message.bot['awaiting_task'] = message.from_user.id
    await message.answer("📝 Topshiriq matnini yozing:")


@dp.message(lambda m: m.bot.get('awaiting_task') == m.from_user.id)
async def task_text(message: Message):
    message.bot.pop('awaiting_task')

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"emp_{uid}")]
            for uid, name in employees.items()
        ]
    )

    message.bot['task_text'] = message.text
    await message.answer("👤 Xodimni tanlang:", reply_markup=kb)


# ===== ASSIGN TASK =====
@dp.callback_query(lambda c: c.data.startswith("emp_"))
async def assign_task(callback):
    uid = int(callback.data.split("_")[1])
    task_text = callback.bot['task_text']

    task = {
        "employee_id": uid,
        "employee_name": employees[uid],
        "text": task_text,
        "status": "jarayonda",
        "created": datetime.now(),
        "last_remind": None
    }

    tasks.append(task)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"done_{len(tasks)-1}"),
            InlineKeyboardButton(text="❌ Bajarilmadi", callback_data=f"fail_{len(tasks)-1}")
        ]
    ])

    await bot.send_message(
        uid,
        f"📌 <b>Yangi topshiriq:</b>\n\n{task_text}",
        reply_markup=kb
    )

    await callback.message.answer("✅ Topshiriq biriktirildi.")
    await callback.answer()


# ===== STATUS BUTTONS =====
@dp.callback_query(lambda c: c.data.startswith(("done_", "fail_")))
async def update_status(callback):
    action, idx = callback.data.split("_")
    idx = int(idx)

    if idx >= len(tasks):
        await callback.answer("Xatolik")
        return

    tasks[idx]["status"] = "bajarildi" if action == "done" else "bajarilmadi"

    await callback.message.edit_text(
        f"📌 {tasks[idx]['text']}\n\n"
        f"📊 Status: <b>{tasks[idx]['status'].upper()}</b>"
    )
    await callback.answer("Saqlandi")


# ===== REMINDER LOOP =====
async def reminder_loop():
    while True:
        now = datetime.now()
        for task in tasks:
            if task["status"] == "jarayonda":
                last = task["last_remind"]
                if not last or now - last >= timedelta(minutes=30):
                    try:
                        await bot.send_message(
                            task["employee_id"],
                            f"⏰ <b>Eslatma!</b>\n\nTopshiriq hali bajarilmadi:\n{task['text']}"
                        )
                        task["last_remind"] = now
                    except:
                        pass
        await asyncio.sleep(60)


# ===== MAIN =====
async def main():
    asyncio.create_task(reminder_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
