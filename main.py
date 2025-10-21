import os
import logging
import re
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ChatType
from aiogram import F

# 🔑 Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "8234719124:AAF1F24fR1fkdzrEaELm4Bnsyc0iFgvkxyE")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# --- Список мата ---
BAD_WORDS = [
    "блять", "бля", "блядь", "бляд", "сука", "ссука", "сцука", "суки",
    "пизд", "пизде", "пиздец", "пизда", "пиздуй", "ебать", "ебал", "ебан",
    "ебло", "ебля", "хуй", "хуя", "хуе", "хуем", "хуев", "хуевый", "ебл",
    "поеб", "наеб", "уеб", "проеб", "заеб", "отеб", "въеб", "выеб",
    "долбоеб", "долбаеб", "ебанат", "ебанутый", "мудак", "мудил", "мудень",
    "мудачье", "мудила", "хер", "херн", "херов", "херня", "охуе", "охере",
    "охуенно", "охуеть", "пидар", "пидор", "пидр", "педик", "педрила",
    "гандон", "гандошить", "шлюх", "шлюха", "шалава"
]

# --- Проверка мата ---
def check_bad_words(text: str) -> bool:
    text_lower = text.lower()
    text_clean = re.sub(r"\s+|[.*_\-]", "", text_lower)  # убираем пробелы и символы
    for word in BAD_WORDS:
        if word in text_clean or re.search(rf"\b{word}", text_lower):
            return True
    return False

# --- /start ---
@dp.message(CommandStart())
async def start(msg: Message):
    if msg.chat.type == ChatType.PRIVATE:
        await msg.answer("❌ Добавь меня в группу и сделай администратором!")
    else:
        await msg.answer("✅ Антимат-бот включён! 👮‍♂️")

# --- Проверка сообщений ---
@dp.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}) & F.text)
async def detect_bad_words(msg: Message):
    if msg.from_user.is_bot or msg.text.startswith("/"):
        return

    logging.info(f"Сообщение: '{msg.text}' от {msg.from_user.first_name}")

    if check_bad_words(msg.text):
        logging.warning(f"Обнаружен мат: '{msg.text}'")

        try:
            await msg.delete()
            warning = await msg.answer(
                f"⚠️ {msg.from_user.first_name}, не матерись!\n"
                f"Сообщение удалено."
            )

            await asyncio.sleep(5)
            try:
                await warning.delete()
            except Exception as e:
                logging.error(f"Не удалось удалить предупреждение: {e}")

        except Exception as e:
            logging.error(f"❌ Ошибка удаления: {e}")
            await msg.reply(
                "⚠️ Не могу удалить сообщение!\n\n"
                "Возможные причины:\n"
                "1. Бот не администратор\n"
                "2. Нет права 'Удаление сообщений'\n"
                "3. Privacy Mode включён в @BotFather"
            )

# --- Личные сообщения ---
@dp.message(F.chat.type == ChatType.PRIVATE)
async def private_message(msg: Message):
    await msg.answer("❌ Я работаю только в группах!")

# --- Запуск ---
async def main():
    logging.info("🚀 Бот запущен на Bothost.ru!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
