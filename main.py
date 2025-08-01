import asyncio
import logging
import os
from pathlib import Path
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile
)

# --- Конфигурация ---
API_TOKEN = os.getenv("API_TOKEN", "PUT-YOUR-TOKEN-HERE")
DB_PATH = "db.sqlite3"
IMAGES_DIR = Path("images")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Главное меню ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Зняти з Розшуку"), KeyboardButton(text="Бронювання")],
        [KeyboardButton(text="Виїзд за кордон"), KeyboardButton(text="СЗЧ/Коміс")],
    ],
    resize_keyboard=True,
)

# --- Тексты для "Зняти з Розшуку" ---
rozshuk_text = """✅ <b>Зняття з РОЗШУКУ на 1 рік</b> 
- з повною гарантією недоторканості 
- оновленою датою пройденого ВЛК 
💰 <i>Вартість:</i> <b>4000 $</b>

✅ <b>БРОНЮВАННЯ і відстрочка на 1 рік</b>
- для тих, хто в РОЗШУКУ 
- з виключенням розшуку 
- гарантія недоторканості на 1 рік 
💰 <i>Вартість:</i> <b>5500 $</b>

📌 <b>Процедура:</b>
1. Перевірка клієнта за паспортними даними та PDF з резерв
2. Часткова оплата 50% + активація послуги
3. Перевірка оновлення в базі (Резерв+, Оберіг/Армор)
4. Оплата другої частини
5. Відправка паперових документів (за бажанням)

⏳ <b>Таймінг:</b>
▪ Миттєва консультація та скрінінг
▪ Зняття з розшуку: 3-10 робочих днів
▪ Бронювання: 3-10 робочих днів
▪ Комплекс: 5-12 робочих днів

💳 <b>Оплата:</b>
USDT | BTC | XMR | Карта України

🔒 <b>Гарантії:</b>
Всі підтвердження, відгуки та гарантії надаються після перевірки клієнта у приватному порядку!

🛡 <b>ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ПОВНА БЕЗПЕКА!</b>

👉 /start - головне меню
👉 /military - зняття СЗЧ"""

# --- Изображения ---
images = {
    "Зняти з Розшуку": IMAGES_DIR / "rozshuk.jpg",
    "Бронювання": IMAGES_DIR / "bron.jpg",
    "Виїзд за кордон": IMAGES_DIR / "vyezd.jpg",
    "СЗЧ/Коміс": IMAGES_DIR / "szch.jpg",
}

# --- Обработчики ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Щоб продовжити, напиши результат: 5 + 3 = ?")

@dp.message(F.text == "8")
async def after_captcha(message: types.Message):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (id, username, interactions) VALUES (?, ?, 0)",
            (message.from_user.id, message.from_user.username),
        )
        await db.commit()
    await message.answer("Чудово, ви пройшли перевірку! Оберіть послугу:", reply_markup=main_menu)

@dp.message(F.text == "Зняти з Розшуку")
async def handle_rozshuk(message: types.Message):
    photo_path = images["Зняти з Розшуку"]
    
    if photo_path.exists():
        try:
            # Отправляем фото с подписью (исчезнет через 5 сек)
            photo = FSInputFile(photo_path)
            sent_photo = await message.answer_photo(
                photo, 
                caption="🔄 Інформація завантажується...",
                parse_mode="HTML"
            )
            
            # Удаляем фото через 5 секунд
            await asyncio.sleep(5)
            await bot.delete_message(chat_id=message.chat.id, message_id=sent_photo.message_id)
            
        except Exception as e:
            logging.error(f"Error sending photo: {e}")
    
    # Отправляем основной текст
    await message.answer(
        rozshuk_text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    
    # Отправляем кнопку консультации (на всю ширину)
    consultation_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🔷 ОТРИМАТИ КОНСУЛЬТАЦІЮ 🔷", 
                url="https://t.me/robic33ai"
            )]
        ]
    )
    await message.answer(
        "Натисніть кнопку нижче для зв'язку з фахівцем:",
        reply_markup=consultation_button
    )

# ... остальные обработчики (для других кнопок) остаются без изменений ...

# --- База данных ---
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, interactions INT)"
        )
        await db.commit()

# --- Главный запуск ---
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
