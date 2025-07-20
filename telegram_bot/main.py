import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, API_URL
from aiogram.types import FSInputFile
import tempfile


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start_command(message: Message):
    text = (
        "👋 *Добро пожаловать в LinguaTrack Bot!*\n\n"
        "Вот список доступных команд:\n"
        "📌 /start — показать это сообщение\n"
        "📅 /today — слова для повторения на сегодня\n"
        "📈 /progress — ваш прогресс в изучении\n"
        "🧠 /test — тест с вариантами перевода\n"
        "🔊 /say <слово> — озвучить слово\n\n"
        "Успехов в обучении! 💪"
    )
    await message.answer(text, parse_mode="Markdown")

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
                await message.answer("✅ Telegram успешно привязан! Начните с команды /start.")
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


@dp.message(F.text.startswith("/say"))
async def say_word(message: Message):
    word = message.text[5:].strip()
    if not word:
        await message.answer("Пожалуйста, укажи слово: /say apple")
        return

    url = f"{API_URL}/say/{word}/"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                audio_bytes = await resp.read()

                # Сохраняем временный файл
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name

                voice = FSInputFile(tmp_path)
                await message.answer_voice(voice=voice)

            else:
                await message.answer("Не удалось озвучить слово 😕")


class TestState(StatesGroup):
    waiting_for_answer = State()



@dp.message(F.text == "/test")
async def start_test(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/test-question/{message.from_user.id}/") as resp:
            if resp.status != 200:
                await message.answer("Не удалось загрузить тест 😕")
                return
            data = await resp.json()

    word = data["word"]
    options = data["options"]
    question_id = data["question_id"]

    buttons = []
    for option in options:
        callback_data = f"answer:{question_id}:{option['id']}"
        button = InlineKeyboardButton(text=option['translation'], callback_data=callback_data)
        buttons.append([button])  # каждая кнопка — в отдельной строке

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(f"🔤 Как переводится слово: *{word}*?", parse_mode="Markdown", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("answer:"))
async def handle_answer(callback: CallbackQuery):
    _, correct_id, chosen_id = callback.data.split(":")
    correct = correct_id == chosen_id

    if correct:
        text = "✅ Правильно!"
    else:
        text = "❌ Неправильно."

    await callback.answer()
    await callback.message.edit_reply_markup()
    await callback.message.answer(text)


async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
