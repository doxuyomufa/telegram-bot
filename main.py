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
    InputFile
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

# --- Тексты и изображения ---
service_data = {
    "Зняти з Розшуку": {
        "intro": "✅ Зняття з розшуку на 1 рік з гарантією недоторканості",
        "full": """**Послуги:**\n- Зняття з розшуку на 1 рік з гарантією\n- Оновлення дати ВЛК\n\n**Вартість:** від 4000 $\n\n**Етапи:**\n1. Перевірка даних\n2. Передоплата 50%\n3. Підтвердження в базах\n4. Доставка документів\n\n**Таймінг:** 3–10 днів\n\n**Оплата:** Криптовалюта або карта""",
        "image": "rozshuk.jpg"
    },
    "Бронювання": {
        "intro": "✅ Бронювання та відстрочка на 1 рік для тих, хто на обліку",
        "full": """**Послуги:**\n- Бронювання та відстрочка на 1 рік\n- Можливість для тих, хто у розшуку\n\n**Вартість:** від 3000 $\n\n**Етапи:**\n1. Перевірка даних\n2. Передоплата 50%\n3. Підтвердження в базах\n4. Відправка документів\n\n**Таймінг:** 3–10 днів\n\n**Оплата:** Криптовалюта або карта""",
        "image": "bron.jpg"
    },
    "Виїзд за кордон": {
        "intro": "✅ Виключення з обліку на 5 років та можливість виїзду",
        "full": """**Послуги:**\n- Виключення з обліку на 5 років\n- Отримання білого квитка\n\n**Вартість:** від 8000 $\n\n**Етапи:**\n1. Перевірка даних\n2. Передоплата 50%\n3. Зняття з обліку\n4. Відправка документів\n\n**Таймінг:** 10–20 днів\n\n**Оплата:** Криптовалюта або карта""",
        "image": "vyezd.jpg"
    },
    "СЗЧ/Коміс": {
        "intro": "✅ Зняття СЗЧ на 1 рік або звільнення зі служби",
        "full": """**Послуги:**\n- Зняття СЗЧ на 1 рік\n- Звільнення за станом здоров'я\n\n**Вартість:** від 5000 $\n\n**Етапи:**\n1. Перевірка даних\n2. Передоплата 50%\n3. Підтвердження в базах\n4. Доставка документів\n\n**Таймінг:** 10–20 днів\n\n**Оплата:** Криптовалюта або карта""",
        "image": "szch.jpg"
    }
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

@dp.message(F.text.in_(service_data.keys()))
async def send_intro(message: types.Message):
    service = message.text
    data = service_data[service]
    image_path = IMAGES_DIR / data["image"]
    
    try:
        if image_path.exists():
            photo = InputFile(image_path)
            await message.answer_photo(photo, caption=data["intro"])
        else:
            await message.answer(data["intro"])
    except Exception as e:
        logging.error(f"Error sending photo: {e}")
        await message.answer(data["intro"])
    
    details_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Детальніше", callback_data=f"details_{service}"),
                InlineKeyboardButton(text="Консультація", url="https://t.me/robic33ai"),
            ]
        ]
    )
    await message.answer("Оберіть дію:", reply_markup=details_keyboard)

@dp.callback_query(F.data.startswith("details_"))
async def send_details(callback: types.CallbackQuery):
    service = callback.data.replace("details_", "")
    data = service_data.get(service)
    
    if data:
        await callback.message.answer(data["full"], parse_mode="Markdown")
        
        consultation_button = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Консультація", url="https://t.me/robic33ai")]
            ]
        )
        await callback.message.answer("Зв'яжіться з нами для консультації:", reply_markup=consultation_button)
    
    await callback.answer()

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
