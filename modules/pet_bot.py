"""
    name: pet_bot
    once: false
    origin: tgpy://module/pet_bot
    priority: 4
"""
logger = ConsoleLogger(f"{__name__.split('/')[-1]}\t| ")

import telethon
import tgpy.api
from tgpy.utils import DATA_DIR
import tgpy
import asyncio


class PetBot:
    def __init__(self, name=None):
        if name:
            self.name = f'pet_bot_{name}'
            self.session_filename = str(DATA_DIR / f'PetBot_{name}.session')
        else:
            self.name = f'pet_bot'
            self.session_filename = str(DATA_DIR / f'PetBot.session')

        logger.print(f"Starting {self.name}")

        self.bot_token = tgpy.api.config.get(f'{self.name}.token', default=None)
        if self.bot_token is None:
            self.bot_token = logger.input(f'Please enter your {self.name} token: ')
            tgpy.api.config.set(f'{self.name}.token', self.bot_token)

        self.bot = telethon.TelegramClient(self.session_filename, tgpy.app.client.api_id, tgpy.app.client.api_hash)
        self.bot.parse_mode = 'html'
        asyncio.create_task(self.bot.start(bot_token=self.bot_token))

    async def send(self, text="Something happened", chat_id=None, **kwargs):
        if chat_id is None:
            me = await client.get_me()
            chat_id = me.id
        await self.bot.send_message(chat_id, text, **kwargs)

    def __getattr__(self, item):
        return getattr(self.bot, item)


pet_bot = PetBot()


__all__ = ['pet_bot', 'PetBot']
