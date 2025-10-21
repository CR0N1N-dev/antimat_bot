import os
import logging
import re
import requests
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ChatType
from aiogram import F

# 🔑 Загружаем ключи из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Список матерных слов (базовый, можно расширить) ---
BAD_WORDS = [
    "блять", "бля", "блядь", "сука", "пизд", "ебать", "ебан", "хуй", "хуе", "хуя",
    "ебал", "ебл", "поеб", "наеб", "уеб", "проеб", "заеб", "отеб", "въеб", "выеб",
    "долбоеб", "мудак", "мудил", "мудень", "хер", "херн", "херов", "охуе", "охере",
    "пидар", "пидор", "пидр", "педик", "гандон", "шлюх", "бляд", "ссука", "сцука"
]

# --- Быстрая проверка мата (регулярки) ---
def quick_check_bad_words(text):
    text_lower = text.lower()
    # Убираем пробелы между буквами (обход: "б л я т ь")
    text_clean = re.sub(r'\s+', '', text_lower)
    
    for word in BAD_WORDS:
        # Проверяем целые слова и части слов
        if word in text_clean or re.search(rf'\b{word}', text_lower):
            return True
    return False

# --- Проверка через Gemini (если быстрая проверка не сработала) ---
def gemini_check_bad_words(text):
    if not GEMINI_API_KEY:
        return False
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""Есть ли в этом тексте русский мат или нецензурная лексика?
Текст: "{text}"

Ответь ТОЛЬКО: ДА или НЕТ"""

    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 5}
    }

    try:
        response = requests.post(url, json=data, timeout=5)
        response.raise_for_status()
        result = response.json()
        output = result["candidates"][0]["content"]["parts"][0]["text"].strip().lower()
        return "да" in output
    except Exception as e:
        logging.error(f"Gemini ошибка: {e}")
        return False

# --- Основная проверка ---
def check_bad_words(text):
    # Сначала быстрая проверка
    if quick_check_bad_words(text):
        return True
    # Если не уверены - проверяем через Gemini (опционально)
    # return gemini_check_bad_words(text)
    return False

# --- Команда /start ---
@dp.message(CommandStart())
async def start(msg: Message):
    if msg.chat.type == ChatType.PRIVATE:
        await msg.answer("❌ Добавь меня в группу и сделай администратором!")
    else:
        await msg.answer("✅ Антимат-бот включён! 👮‍♂️")

# --- Проверка сообщений в группе ---
@dp.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}) & F.text)
async def detect_bad_words(msg: Message):
    # Пропускаем ботов и команды
    if msg.from_user.is_bot or msg.text.startswith("/"):
        return
    
    logging.info(f"Проверяю: '{msg.text}' от {msg.from_user.first_name}")
    
    if check_bad_words(msg.text):
        try:
            await msg.delete()
            logging.info(f"❌ Удалено сообщение с матом от {msg.from_user.first_name}")
            
            warning = await msg.answer(
                f"⚠️ {msg.from_user.first_name}, не матерись!\n"
                f"Сообщение удалено."
            )
            
            import asyncio
            await asyncio.sleep(5)
            try:
                await warning.delete()
            except:
                pass
                
        except Exception as e:
            logging.error(f"Ошибка удаления: {e}")
            await msg.answer("⚠️ Не могу удалить сообщение! Сделай меня администратором с правом удаления сообщений.")

# --- Личка ---
@dp.message(F.chat.type == ChatType.PRIVATE)
async def private_message(msg: Message):
    await msg.answer("❌ Я работаю только в группах!")

# --- Запуск ---
if __name__ == "__main__":
    import asyncio
    logging.info("🚀 Антимат-бот запущен!")
    asyncio.run(dp.start_polling(bot))
