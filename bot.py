import os
import logging
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

logging.basicConfig(level=logging.INFO)

# --- Проверка мата через Gemini ---
def check_bad_words(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""Проверь текст на наличие мата, нецензурной лексики, оскорблений.
Текст: "{text}"

Ответь ТОЛЬКО одним словом: ДА или НЕТ
ДА - если есть мат
НЕТ - если мата нет"""

    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 10
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        output = result["candidates"][0]["content"]["parts"][0]["text"].strip().lower()
        logging.info(f"Проверка '{text[:50]}...' -> Gemini: {output}")
        
        return "да" in output or "yes" in output
    except Exception as e:
        logging.error(f"Ошибка Gemini API: {e}")
        return False

# --- Команда /start ---
@dp.message(CommandStart())
async def start(msg: Message):
    if msg.chat.type == ChatType.PRIVATE:
        await msg.answer("❌ Я работаю только в группах!")
    else:
        await msg.answer("✅ Антимат-бот активирован! Слежу за порядком 👮")

# --- Проверка сообщений в группе ---
@dp.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}) & F.text)
async def detect_bad_words(msg: Message):
    # Пропускаем ботов и команды
    if msg.from_user.is_bot or (msg.text and msg.text.startswith("/")):
        return
    
    logging.info(f"Проверяю: {msg.text}")
    
    if check_bad_words(msg.text):
        try:
            # Удаляем сообщение с матом
            await msg.delete()
            
            # Отправляем предупреждение
            warning = await msg.answer(
                f"⚠️ {msg.from_user.first_name}, не матерись!\n"
                f"Твоё сообщение удалено."
            )
            
            # Удаляем предупреждение через 5 секунд
            import asyncio
            await asyncio.sleep(5)
            try:
                await warning.delete()
            except:
                pass
                
        except Exception as e:
            logging.error(f"Не могу удалить сообщение: {e}")
            logging.error("Проверь права бота: он должен быть админом с правом удаления сообщений!")

# --- Сообщения в личке ---
@dp.message(F.chat.type == ChatType.PRIVATE)
async def private_message(msg: Message):
    await msg.answer("❌ Я работаю только в группах! Добавь меня в группу и сделай администратором.")

# --- Запуск бота ---
if __name__ == "__main__":
    import asyncio
    logging.info("🚀 Бот запущен!")
    asyncio.run(dp.start_polling(bot))
