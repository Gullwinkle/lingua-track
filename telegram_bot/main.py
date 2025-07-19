import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.filters.command import CommandObject
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, API_URL


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_URL}/register/",
            json={"telegram_id": message.from_user.id}
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                print("Ошибка при регистрации:", resp.status, text)
                await message.answer("Ошибка при регистрации. Попробуйте позже.")
                return
            result = await resp.json()

    await message.answer("Привет! Я помогу тебе учить слова 💬")

# telegram_bot/main.py
@dp.message(CommandStart(deep_link=True))
async def start_with_token(message: Message, command: CommandObject):
    token = command.args

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/link-telegram/", json={
            "telegram_id": message.from_user.id,
            "token": token
        }) as resp:
            if resp.status == 200:
                await message.answer("✅ Telegram успешно привязан!")
            else:
                await message.answer("❌ Не удалось привязать аккаунт. Возможно, неверная ссылка.")


@dp.message(F.text == "/today")
async def cmd_today(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/today/{message.from_user.id}/") as resp:
            if resp.status == 404:
                await message.answer("Сначала отправь /start для регистрации.")
                return
            cards = await resp.json()

    if not cards:
        await message.answer("Сегодня нет слов для повторения ✅")
        return

    text = "\n".join([f"📌 <b>{c['word']}</b> — {c['translation']}" for c in cards])
    await message.answer(text)

@dp.message(F.text == "/progress")
async def cmd_progress(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/progress/{message.from_user.id}/") as resp:
            if resp.status == 404:
                await message.answer("Сначала отправь /start для регистрации.")
                return
            stats = await resp.json()

    await message.answer(f"🧠 Всего слов: {stats['total']}\n🔁 К повторению: {stats['due']}")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
