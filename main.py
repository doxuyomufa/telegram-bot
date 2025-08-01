import asyncio
import logging
import os
import aiosqlite
from pathlib import Path
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# --- Конфигурация ---
API_TOKEN = os.getenv("API_TOKEN", "PUT-YOUR-TOKEN-HERE")
DB_PATH = "db.sqlite3"
IMAGES_DIR = Path("images")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Меню ---
interest_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зняти з Розшуку"), KeyboardButton(text="Бронювання")],
        [KeyboardButton(text="Виїзд за кордон"), KeyboardButton(text="СЗЧ/Коміс")],
    ],
    resize_keyboard=True,
)

# Тексты для первого сообщения
intro_texts = {
    "Зняти з Розшуку": "✅ Зняття з РОЗШУКУ на 1 рік - з повною гарантією недоторканості",
    "Бронювання": "✅ БРОНЮВАННЯ і відстрочка на 1 рік для тих, хто на обліку",
    "Виїзд за кордон": "✅ Виключення з обліку на 5 років та можливість перетину кордону",
    "СЗЧ/Коміс": "✅ Зняття СЗЧ на гарантований 1 рік",
}

# Полные тексты
full_texts = {
    "Зняти з Розшуку": """✅ Зняття з РОЗШУКУ на 1 рік - з повною гарантією недоторканості та оновленою датою пройденого ВЛК - 4000 дол

✅ БРОНЮВАННЯ і відстрочка на 1 рік для тих, хто в РОЗШУКУ з виключенням розшуку і гарантією недоторканості на 1 рік - 5500 дол

Процедура:
1. Перевірка клієнта за паспортними даними та пдф з резерв
2. Часткова оплата в розмірі 50% і активація послуги
3. Перевірка оновлення в базі Резерв+, Оберіг/Армор та оплата другої частини
4. Відправка паперових документів бронювання, якщо була вибрана дана опція

⌛️ Таймінг:
Миттєва консультація та скрінінг клієнта
Зняття з розшуку або бронювання від 3 до 10 робочих днів
Зняття з розшуку та бронювання - від 5 до 12 робочих днів

💲 Оплата:
Крипто USDT, BTC, XMR або карта

💬 ВІДГУКИ ТА ГАРАНТІЇ:
Відгуки, гарантії та підтвердження - інформація конфіденційна, тому видається у приватному спілкуванні після перевірки клієнта та попереднього погодження на замовлення послуги!

ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ВАША БЕЗПЕКА!
ЗВЕРТАЙТЕСЯ!!!""",

    "Бронювання": """✅ БРОНЮВАННЯ і відстрочка на 1 рік для тих, хто на обліку - 3000 дол
✅ БРОНЮВАННЯ і відстрочка на 1 рік для тих, хто в РОЗШУКУ з виключенням розшуку - 5500 дол

Процедура:
1. Перевірка клієнта за паспортними даними та пдф з резерв
2. Часткова оплата в розмірі 50% і активація послуги
3. Перевірка оновлення в базі Резерв+, Оберіг/Армор та оплата другої частини
4. Відправка паперових документів кур'єром або поштою

⌛️ Таймінг:
Миттєва консультація та скрінінг клієнта
Бронювання від 3 до 10 робочих днів
Зняття з розшуку та бронювання - від 5 до 12 робочих днів

💲 Оплата:
Крипто USDT, BTC, XMR або карта

💬 ВІДГУКИ ТА ГАРАНТІЇ:
Відгуки, гарантії та підтвердження - інформація конфіденційна, тому видається у приватному спілкуванні після перевірки клієнта та попереднього погодження на замовлення послуги!

ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ВАША БЕЗПЕКА!
ЗВЕРТАЙТЕСЯ!!!""",

    "Виїзд за кордон": """✅ Виключення з обліку на 5 років та можливість перетину кордону "Білий квиток" - від 8000*

Процедура:
1. Перевірка клієнта за паспортними даними та пдф з резерв
2. Часткова оплата в розмірі 50% і активація послуги
3. Перевірка документів, підтвердження по базам та оплата другої частини
4. Відправка документів кур'єром або поштою

⌛️ Таймінг:
Миттєва консультація та скрінінг клієнта
Уточнення ситуації та підготовчий процес від 2 до 5 робочих днів
Документація, зняття з обліку та перевірка по базам - від 10 до 20 робочих днів

💲 Оплата:
Крипто USDT, BTC, XMR або карта

💬 ВІДГУКИ ТА ГАРАНТІЇ:
Відгуки, гарантії та підтвердження - інформація конфіденційна, тому видається у приватному спілкуванні після перевірки клієнта та попереднього погодження на замовлення послуги!

ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ВАША БЕЗПЕКА!
ЗВЕРТАЙТЕСЯ!!!""",

    "СЗЧ/Коміс": """✅ Зняття СЗЧ на гарантований 1 рік - 5000 дол

✅ Звільнення зі служби за станом здоров'я від 8000 дол

Процедура:
1. Перевірка клієнта за паспортними даними та пдф з резерв
2. Часткова оплата в розмірі 50% і активація послуги
3. Перевірка документів, підтвердження по базам та оплата другої частини
4. Відправка документів кур'єром або поштою

⌛️ Таймінг:
Миттєва консультація та скрінінг клієнта
Уточнення ситуації та підготовчий процес від 2 до 5 робочих днів
Документація, зняття з обліку та перевірка по базам - від 10 до 20 робочих днів

💲 Оплата:
Крипто USDT, BTC, XMR або карта

💬 ВІДГУКИ ТА ГАРАНТІЇ:
Відгуки, гарантії та підтвердження - інформація конфіденційна, тому видається у приватному спілкуванні після перевірки клієнта та попереднього погодження на замовлення послуги!

ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ВАША БЕЗПЕКА!
ЗВЕРТАЙТЕСЯ!!!"""
}

images = {
    "Зняти з Розшуку": IMAGES_DIR / "rozshuk.jpg",
    "Бронювання": IMAGES_DIR / "bron.jpg",
    "Виїзд за кордон": IMAGES_DIR / "vyezd.jpg",
    "СЗЧ/Коміс": IMAGES_DIR / "szch.jpg",
}

# --- Хендлеры ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Аби продовжити напиши число 5 + 3 = ?")

@dp.message(F.text == "8")
async def after_captcha(message: types.Message):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)",
            (message.from_user.id, message.from_user.username),
        )
        await db.commit()
    await message.answer("Чудово, Ви пройшли перевірку! Що Вас цікавить?", reply_markup=interest_menu)

@dp.message(F.text.in_(intro_texts.keys()))
async def send_intro(message: types.Message):
    choice = message.text
    photo_path = images.get(choice)
    
    # Отправляем краткое вступление с фото
    if photo_path and photo_path.exists():
        with open(photo_path, "rb") as photo:
            await message.answer_photo(photo, caption=intro_texts[choice])
    else:
        await message.answer(intro_texts[choice])
    
    # Создаем кнопки для деталей
    details_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Детальніше", callback_data=f"details_{choice}"),
                InlineKeyboardButton(text="Консультація", url="https://t.me/robic33ai")
            ]
        ]
    )
    
    await message.answer("Оберіть дію:", reply_markup=details_keyboard)

@dp.callback_query(F.data.startswith("details_"))
async def send_details(callback: types.CallbackQuery):
    choice = callback.data.replace("details_", "")
    
    # Отправляем полный текст
    await callback.message.answer(full_texts[choice])
    
    # Предлагаем консультацию
    consultation_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Консультація", url="https://t.me/robic33ai")]
        ]
    )
    await callback.message.answer("Зв'яжіться з нами для консультації:", reply_markup=consultation_button)
    await callback.answer()

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)"
        )
        await db.commit()

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
