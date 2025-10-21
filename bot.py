import os
import logging
import requests
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
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

# --- Проверка текста через Gemini ---
def check_bad_words(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": f"Определи, содержит ли это сообщение нецензурную лексику (мат): '{text}'. Ответь только 'да' или 'нет'."}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        output = result["candidates"][0]["content"]["parts"][0]["text"].lower()
        return "да" in output
    except Exception as e:
        print("Ошибка Gemini API:", e)
        return False

# --- Команда /start ---
@dp.message(CommandStart())
async def start(msg: Message):
    if msg.chat.type == ChatType.PRIVATE:
        await msg.answer("Я работаю только в группе, пожалуйста перейди в группу!")
    else:
        await msg.answer("Привет! Я слежу за порядком 👀")

# --- Проверка сообщений в группе ---
@dp.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def detect_bad_words(msg: Message):
    if msg.text and check_bad_words(msg.text):
        try:
            await bot.delete_message(msg.chat.id, msg.message_id)
            await msg.answer(
                f"{msg.from_user.first_name}, ты сказал плохое слово! 😡\n"
                "Не говори больше плохие слова, иначе будет плохо."
            )
        except Exception as e:
            print("Ошибка при удалении:", e)

# --- Сообщения в личке ---
@dp.message(F.chat.type == ChatType.PRIVATE)
async def private_message(msg: Message):
    await msg.answer("Я работаю только в группе, пожалуйста перейди в группу!")

# --- Запуск бота ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
