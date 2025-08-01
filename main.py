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
    WebhookInfo
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# --- Конфигурация ---
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("Не указан API_TOKEN в переменных окружения")

DB_PATH = "db.sqlite3"
IMAGES_DIR = Path("images")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", 8000))

if not WEBHOOK_URL:
    raise ValueError("Не указан WEBHOOK_URL в переменных окружения")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Создаем директорию для изображений, если ее нет
IMAGES_DIR.mkdir(exist_ok=True)

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
    photo_path = IMAGES_DIR / service["image"]
    
    # Отправляем текст
    await message.answer(
        service["text"],
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    
    # Отправляем фото, если оно существует
    if photo_path.exists():
        try:
            photo = FSInputFile(photo_path)
            await message.answer_photo(
                photo, 
                caption="🔍 Детальна інформація вище 👆",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
    else:
        logger.warning(f"Image not found: {photo_path}")
    
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

# --- Webhook настройки ---
async def on_startup(bot: Bot) -> None:
    await init_db()
    
    # Проверяем текущий webhook
    webhook_info = await bot.get_webhook_info()
    logger.info(f"Current webhook info: {webhook_info}")
    
    # Устанавливаем новый webhook
    webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    logger.info(f"Setting webhook to: {webhook_url}")
    
    try:
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        logger.info("Webhook successfully set")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        raise

async def on_shutdown(bot: Bot) -> None:
    logger.warning("Shutting down...")
    await bot.delete_webhook(drop_pending_updates=True)
    logger.warning("Bot stopped")

# --- Главный запуск ---
async def main() -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    try:
        await web._run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
