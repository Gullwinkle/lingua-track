import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Токен бота и URL API
TELEGRAM_BOT_TOKEN = BOT_TOKEN  # Замените на ваш токен
API_BASE_URL = 'http://localhost:8000/api'  # URL вашего Django API

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.reply('Привет! Я бот LinguaTrack. Используй команды:\n/today - слова на сегодня\n/test - пройти тест\n/progress - твой прогресс\n/say <слово> - озвучить слово\n/cards - список карточек')

@dp.message(Command('today'))
async def today(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'{API_BASE_URL}/today/?telegram_id={telegram_id}') as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        response_text = '\n'.join([f"{card['word']}: {card['translation']}" for card in data])
                        await message.reply(f'Карточки на сегодня:\n{response_text}')
                    else:
                        await message.reply('На сегодня нет карточек для повторения.')
                else:
                    await message.reply(f'Привяжите ваш Telegram ID на сайте. Код ошибки: {response.status}')
        except Exception as e:
            logging.error(f'Ошибка в /today: {str(e)}')
            await message.reply('Ошибка при получении карточек.')

@dp.message(Command('cards'))
async def cards(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'{API_BASE_URL}/cards/?telegram_id={telegram_id}') as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        response_text = '\n'.join([f"{card['word']}: {card['translation']}" for card in data])
                        await message.reply(f'Ваши карточки:\n{response_text}')
                    else:
                        await message.reply('У вас пока нет карточек.')
                else:
                    await message.reply(f'Привяжите ваш Telegram ID на сайте. Код ошибки: {response.status}')
        except Exception as e:
            logging.error(f'Ошибка в /cards: {str(e)}')
            await message.reply('Ошибка при получении карточек.')

@dp.message(Command('progress'))
async def progress(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'{API_BASE_URL}/progress/?telegram_id={telegram_id}') as response:
                if response.status == 200:
                    data = await response.json()
                    await message.reply(
                        f'Ваш прогресс:\n'
                        f'Всего карточек: {data["total_cards"]}\n'
                        f'Выучено: {data["learned_cards"]}\n'
                        f'Повторений: {data["total_reviews"]}'
                    )
                else:
                    await message.reply(f'Привяжите ваш Telegram ID на сайте. Код ошибки: {response.status}')
        except Exception as e:
            logging.error(f'Ошибка в /progress: {str(e)}')
            await message.reply('Ошибка при получении прогресса.')

@dp.message(Command('say'))
async def say(message: types.Message):
    word = message.text.replace('/say ', '').strip()
    if not word:
        await message.reply('Укажите слово после /say, например: /say hello')
        return
    telegram_id = str(message.from_user.id)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'{API_BASE_URL}/say/{word}/?telegram_id={telegram_id}') as response:
                if response.status == 200:
                    data = await response.json()
                    audio_url = data.get('audio_url')
                    await message.reply_audio(audio=audio_url, title=word)
                else:
                    await message.reply(f'Привяжите ваш Telegram ID на сайте. Код ошибки: {response.status}')
        except Exception as e:
            logging.error(f'Ошибка при озвучивании слова "{word}": {str(e)}')
            await message.reply('Ошибка при озвучивании слова.')

@dp.message(Command('test'))
async def test(message: types.Message):
    telegram_id = str(message.from_user.id)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f'{API_BASE_URL}/test/?telegram_id={telegram_id}') as response:
                if response.status == 200:
                    data = await response.json()
                    if 'error' in data:
                        await message.reply(data['error'])
                        return
                    card = data['card']
                    choices = data['choices']
                    keyboard = ReplyKeyboardMarkup(
                        keyboard=[[KeyboardButton(text=choice['translation'])] for choice in choices],
                        resize_keyboard=True,
                        one_time_keyboard=True
                    )
                    await message.reply(
                        f'Слово: {card["word"]}\nВыберите правильный перевод:',
                        reply_markup=keyboard
                    )
                else:
                    await message.reply(f'Привяжите ваш Telegram ID на сайте. Код ошибки: {response.status}')
        except Exception as e:
            logging.error(f'Ошибка в /test: {str(e)}')
            await message.reply('Ошибка при запуске теста.')

@dp.message(F.text)
async def handle_test_answer(message: types.Message):
    telegram_id = str(message.from_user.id)
    answer = message.text
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f'{API_BASE_URL}/test/submit/',
                json={'telegram_id': telegram_id, 'answer': answer}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['correct']:
                        await message.reply('Правильно! 🎉', reply_markup=types.ReplyKeyboardRemove())
                    else:
                        await message.reply(
                            f'Неправильно. Правильный перевод: {data["correct_translation"]}',
                            reply_markup=types.ReplyKeyboardRemove()
                        )
                    await message.reply('Используйте /test для следующего вопроса.')
                else:
                    error_text = await response.text()
                    logging.error(f'Ошибка API /test/submit/: Код {response.status}, Ответ: {error_text}')
                    await message.reply(f'Ошибка при отправке ответа. Код: {response.status}')
        except Exception as e:
            logging.error(f'Ошибка при обработке ответа теста: {str(e)}')
            await message.reply('Ошибка при обработке ответа.')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())