import logging
import requests
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ChatType
from aiogram import F

# 🔑 Замени на свои ключи
load_dotenv()
GEMINI_API_KEY = "AIzaSyBHD3ls9mIPw2poqtaS4aNRJJfjs6j0Ico"

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Проверка текста через Gemini API
def check_bad_words(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": f"Определи, содержит ли это сообщение нецензурную лексику (мат): '{text}'. Ответь только 'да' или 'нет'."}]
        }]
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    try:
        output = result["candidates"][0]["content"]["parts"][0]["text"].lower()
        return "да" in output
    except Exception:
        return False

# Реакция на старт
@dp.message(CommandStart())
async def start(msg: Message):
    if msg.chat.type == ChatType.PRIVATE:
        await msg.answer("Я работаю только в группе, пожалуйста перейди в группу!")
    else:
        await msg.answer("Привет! Я слежу за порядком 👀")

# Обработка сообщений в группе
@dp.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def detect_bad_words(msg: Message):
    if msg.text:
        if check_bad_words(msg.text):
            try:
                await bot.delete_message(msg.chat.id, msg.message_id)
                await msg.answer(f"{msg.from_user.first_name}, ты сказал плохое слово! 😡\nНе говори больше плохие слова, иначе будет плохо.")
            except Exception as e:
                print("Ошибка при удалении:", e)

# Обработка сообщений в личке
@dp.message(F.chat.type == ChatType.PRIVATE)
async def private_message(msg: Message):
    await msg.answer("Я работаю только в группе, пожалуйста перейди в группу!")

# Запуск
if name == "main":
    import asyncio
    asyncio.run(dp.start_polling(bot))