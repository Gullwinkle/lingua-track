import aiohttp
import asyncio
from config import BOT_TOKEN


def send_telegram_message(chat_id, text):
    async def send():
        async with aiohttp.ClientSession() as session:
            await session.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                json={'chat_id': chat_id, 'text': text}
            )
    asyncio.run(send())
