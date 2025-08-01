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

# --- Тексты для всех услуг ---
service_texts = {
    "Зняти з Розшуку": {
        "text": """✅ <b>Зняття з РОЗШУКУ на 1 рік</b>
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
👉 /military - зняття СЗЧ""",
        "image": "rozshuk.jpg"
    },
    "Бронювання": {
        "text": """✅ <b>БРОНЮВАННЯ і відстрочка на 1 рік</b>
- для тих, хто на обліку
💰 <i>Вартість:</i> <b>3000 $</b>

✅ <b>БРОНЮВАННЯ і відстрочка на 1 рік</b>
- для тих, хто в РОЗШУКУ
- з виключенням розшуку
💰 <i>Вартість:</i> <b>5500 $</b>

📌 <b>Процедура:</b>
1. Перевірка клієнта за паспортними даними та PDF з резерв
2. Часткова оплата 50% + активація послуги
3. Перевірка оновлення в базі (Резерв+, Оберіг/Армор)
4. Оплата другої частини
5. Відправка документів кур'єром/поштою

⏳ <b>Таймінг:</b>
▪ Миттєва консультація та скрінінг
▪ Бронювання: 3-10 робочих днів
▪ Комплекс: 5-12 робочих днів

💳 <b>Оплата:</b>
USDT | BTC | XMR | Карта України

🔒 <b>Гарантії:</b>
Всі підтвердження, відгуки та гарантії надаються після перевірки клієнта у приватному порядку!

🛡 <b>ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ПОВНА БЕЗПЕКА!</b>

👉 /start - головне меню
👉 /rozshuk - зняття з розшуку""",
        "image": "bron.jpg"
    },
    "Виїзд за кордон": {
        "text": """✅ <b>Виїзд за кордон</b>
- Виключення з обліку на 5 років
- Можливість перетину кордону ("Білий квиток")
💰 <i>Вартість:</i> <b>від 8000 $</b>

📌 <b>Процедура:</b>
1. Перевірка клієнта за паспортними даними та PDF з резерв
2. Часткова оплата 50% + активація послуги
3. Перевірка документів, підтвердження по базам
4. Оплата другої частини
5. Відправка документів кур'єром/поштою

⏳ <b>Таймінг:</b>
▪ Миттєва консультація та скрінінг
▪ Підготовка: 2-5 робочих днів
▪ Документація: 10-20 робочих днів

💳 <b>Оплата:</b>
USDT | BTC | XMR | Карта України

🔒 <b>Гарантії:</b>
Всі підтвердження, відгуки та гарантії надаються після перевірки клієнта у приватному порядку!

🛡 <b>ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ПОВНА БЕЗПЕКА!</b>

👉 /start - головне меню
👉 /military - виведення з ЗС""",
        "image": "vyezd.jpg"
    },
    "СЗЧ/Коміс": {
        "text": """✅ <b>Зняття СЗЧ</b>
- на гарантований 1 рік
💰 <i>Вартість:</i> <b>5000 $</b>

✅ <b>Звільнення зі служби</b>
- за станом здоров'я
💰 <i>Вартість:</i> <b>від 8000 $</b>

📌 <b>Процедура:</b>
1. Перевірка клієнта за паспортними даними та PDF з резерв
2. Часткова оплата 50% + активація послуги
3. Перевірка документів, підтвердження по базам
4. Оплата другої частини
5. Відправка документів кур'єром/поштою

⏳ <b>Таймінг:</b>
▪ Миттєва консультація та скрінінг
▪ Підготовка: 2-5 робочих днів
▪ Документація: 10-20 робочих днів

💳 <b>Оплата:</b>
USDT | BTC | XMR | Карта України

🔒 <b>Гарантії:</b>
Всі підтвердження, відгуки та гарантії надаються після перевірки клієнта у приватному порядку!

🛡 <b>ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ПОВНА БЕЗПЕКА!</b>

👉 /start - головне меню
👉 /rozshuk - зняття з розшуку""",
        "image": "szch.jpg"
    }
}

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

async def send_service_info(message: types.Message, service_name: str):
    service = service_texts[service_name]
    photo_path = images[service_name]
    
    # Отправляем текст сразу
    text_message = await message.answer(
        service["text"],
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    
    if photo_path.exists():
        try:
            # Отправляем фото
            photo = FSInputFile(photo_path)
            sent_photo = await message.answer_photo(
                photo, 
                caption="🔍 Детальна інформація вище 👆",
                parse_mode="HTML"
            )
            
            # Удаляем фото через 7 секунд
            await asyncio.sleep(7)
            await bot.delete_message(chat_id=message.chat.id, message_id=sent_photo.message_id)
            
        except Exception as e:
            logging.error(f"Error sending photo for {service_name}: {e}")
    
    # Отправляем кнопку консультации
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

@dp.message(F.text == "Зняти з Розшуку")
async def handle_rozshuk(message: types.Message):
    await send_service_info(message, "Зняти з Розшуку")

@dp.message(F.text == "Бронювання")
async def handle_bron(message: types.Message):
    await send_service_info(message, "Бронювання")

@dp.message(F.text == "Виїзд за кордон")
async def handle_vyezd(message: types.Message):
    await send_service_info(message, "Виїзд за кордон")

@dp.message(F.text == "СЗЧ/Коміс")
async def handle_szch(message: types.Message):
    await send_service_info(message, "СЗЧ/Коміс")

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
