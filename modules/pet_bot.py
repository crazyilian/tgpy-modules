"""
    description: telethon bot with Bot API
    name: pet_bot
    needs:
      config_loader: 0.0.0
    version: 0.0.0
"""
import telethon
from tgpy.utils import DATA_DIR
from tgpy import app
import asyncio


class PetBot:
    def __init__(self, name=None):
        if name:
            self.name = f'pet_bot_{name}'
            self.session_name = f'PetBot_{name}.session'
        else:
            self.name = f'pet_bot'
            self.session_name = f'PetBot.session'

        self.config = ModuleConfig(self.name, ['bot_token'], [str],
                                   default_dict={'session_filename': str(DATA_DIR / self.session_name)})

        self.bot = telethon.TelegramClient(
            self.config.session_filename, app.client.api_id, app.client.api_hash
        )
        self.bot.parse_mode = 'html'
        asyncio.create_task(self.bot.start(bot_token=self.config.bot_token))

    async def notify(self, text, chat_id=None, **kwargs):
        if not text:
            text = "Something happened"
        if chat_id is None:
            me = await client.get_me()
            chat_id = me.id
        await self.bot.send_message(chat_id, text, **kwargs)

    def __getattr__(self, item):
        return self.bot.item


pet_bot = PetBot()


@dot('notify')
async def notify_me(text=None):
    return await pet_bot.notify(text)


__all__ = ['pet_bot', 'PetBot', 'notify_me']
