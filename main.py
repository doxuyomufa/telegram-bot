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
    FSInputFile,
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

# --- Краткие тексты ---
intro_texts = {
    "Зняти з Розшуку": "✅ Зняття з розшуку на 1 рік з гарантією недоторканості",
    "Бронювання": "✅ Бронювання та відстрочка на 1 рік для тих, хто на обліку",
    "Виїзд за кордон": "✅ Виключення з обліку на 5 років та можливість виїзду",
    "СЗЧ/Коміс": "✅ Зняття СЗЧ на 1 рік або звільнення зі служби",
}

# --- Полные тексты ---
full_texts = {
    "Зняти з Розшуку": """**Послуги:**
- Зняття з розшуку на 1 рік з гарантією недоторканості
- Оновлення дати ВЛК

**Вартість:** від 4000 $

**Етапи:**
1. Перевірка даних
2. Передоплата 50%
3. Зняття з розшуку, підтвердження в базах
4. Доставка документів

**Таймінг:** 3–10 днів

**Оплата:** Криптовалюта або карта

**Гарантії та відгуки:** надаються після перевірки клієнта""",

    "Бронювання": """**Послуги:**
- Бронювання та відстрочка на 1 рік
- Можливість для тих, хто у розшуку

**Вартість:** від 3000 $

**Етапи:**
1. Перевірка даних
2. Передоплата 50%
3. Підтвердження в базах
4. Відправка документів

**Таймінг:** 3–10 днів

**Оплата:** Криптовалюта або карта""",

    "Виїзд за кордон": """**Послуги:**
- Виключення з обліку на 5 років
- Отримання білого квитка

**Вартість:** від 8000 $

**Етапи:**
1. Перевірка даних
2. Передоплата 50%
3. Зняття з обліку, перевірка в базах
4. Відправка документів

**Таймінг:** 10–20 днів

**Оплата:** Криптовалюта або карта""",

    "СЗЧ/Коміс": """**Послуги:**
- Зняття СЗЧ на 1 рік
- Звільнення зі служби за станом здоров’я

**Вартість:** від 5000 $

**Етапи:**
1. Перевірка даних
2. Передоплата 50%
3. Підтвердження в базах
4. Доставка документів

**Таймінг:** 10–20 днів

**Оплата:** Криптовалюта або карта""",
}

# --- Изображения ---
images = {
    "Зняти з Розшуку": IMAGES_DIR / "rozshuk.jpg",
    "Бронювання": IMAGES_DIR / "bron.jpg",
    "Виїзд за кордон": IMAGES_DIR / "vyezd.jpg",
    "СЗЧ/Коміс": IMAGES_DIR / "szch.jpg",
}

# --- Проверка наличия фото при старте ---
def check_images():
    for name, path in images.items():
        if not path.exists():
            logging.warning(f"⚠ Фото для '{name}' не найдено: {path}")
        else:
            logging.info(f"Фото для '{name}' найдено: {path}")

# --- Обработчик для кнопки "Зняти з Розшуку" с фото + текст и кнопкой ---
@dp.message(F.text == "Зняти з Розшуку")
async def send_znyat_rozshuk(message: types.Message):
    photo_path = images.get("Зняти з Розшуку")
    if photo_path and photo_path.exists():
        photo = FSInputFile(photo_path)
        sent_photo = await message.answer_photo(photo, caption="⏳ Завантаження інформації...")
        # Удаляем фото через 5 секунд
        await asyncio.sleep(5)
        await sent_photo.delete()
    else:
        logging.warning("Фото для 'Зняти з Розшуку' не найдено")

    # Текст с эмодзи и форматированием Markdown
    text = (
        "✅ *Зняття з РОЗШУКУ* на 1 рік - з повною гарантією недоторканості та оновленою датою пройденого ВЛК - *4000 $*\n\n"
        "✅ *БРОНЮВАННЯ* і відстрочка на 1 рік для тих, хто в РОЗШУКУ з виключенням розшуку і гарантією недоторканості на 1 рік - *5500 $*\n\n"
        "*Процедура:*\n"
        "1. Перевірка клієнта за паспортними даними та PDF з резерву\n"
        "2. Часткова оплата в розмірі 50% і активація послуги\n"
        "3. Перевірка оновлення в базі Резерв+, Оберіг/Армор та оплата другої частини\n"
        "4. Відправка паперових документів бронювання, якщо була вибрана дана опція\n\n"
        "⌛️ *Таймінг:*\n"
        "- Миттєва консультація та скрінінг клієнта\n"
        "- Зняття з розшуку або бронювання від 3 до 10 робочих днів\n"
        "- Зняття з розшуку та бронювання - від 5 до 12 робочих днів\n\n"
        "💲 *Оплата:* Крипто USDT, BTC, XMR або карта\n\n"
        "💬 *ВІДГУКИ ТА ГАРАНТІЇ:*\n"
        "Відгуки, гарантії та підтвердження - інформація конфіденційна, "
        "тому видається у приватному спілкуванні після перевірки клієнта та погодження замовлення!\n\n"
        "🔒 *ГАРАНТОВАНИЙ РЕЗУЛЬТАТ ТА ВАША БЕЗПЕКА!*\n"
        "ЗВЕРТАЙТЕСЯ!!!\n\n"
        "на головну - /start\n"
        "зняття СЗЧ - /military"
    )

    # Кнопка консультации (широкая под всем текстом)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Консультація", url="https://t.me/robic33ai")]
        ]
    )

    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

# --- Обработчики для остальных кнопок оставляем прежними (как в вашем коде) ---

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

@dp.message(F.text.in_(intro_texts.keys()))
async def send_intro(message: types.Message):
    choice = message.text
    photo_path = images.get(choice)

    if photo_path and photo_path.exists():
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo, caption=intro_texts[choice])
    else:
        await message.answer(intro_texts[choice])

    details_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Детальніше", callback_data=f"details_{choice}"),
                InlineKeyboardButton(text="Консультація", url="https://t.me/robic33ai"),
            ]
        ]
    )
    await message.answer("Оберіть дію:", reply_markup=details_keyboard)

@dp.callback_query(F.data.startswith("details_"))
async def send_details(callback: types.CallbackQuery):
    choice = callback.data.replace("details_", "")
    await callback.message.answer(full_texts[choice])

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
    check_images()  # проверяем наличие всех картинок при запуске
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
