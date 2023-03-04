"""
    description: react when someone answers to "yes", "no", etc. with rhyme in target
      chats
    name: yes_no_answers
    needs:
      config_loader: 0.0.0
      tg_name: 0.0.0
    version: 0.1.1
"""
import telethon

handle_yes_no_chats = set()
really_handling_yes_no_chats = set()


class YesNoAnswers:
    def __init__(self):
        self.config = ModuleConfig('yes_no_answers', default_dict={'chats': [], 'suffixes': {
            "да": "да",
            "нет": "ет",
            "ладно": "дно"
        }})
        self.telethon_handlers = set()
        self.chats = set()
        self.add_chat(*self.config.chats)

    def __save_chats(self):
        self.config.chats = list(self.chats)

    def add_chat(self, *chats):
        """add new chats to handle yes no answers"""
        self.chats.update(chats)
        self.__save_chats()
        new_chats = [chat for chat in chats if chat not in self.telethon_handlers]
        if not new_chats:
            return
        self.telethon_handlers.update(new_chats)

        @client.on(telethon.events.NewMessage(chats=new_chats))
        async def handle_yes_no_answer(event):
            if event.chat_id not in self.chats:
                return
            for word, suffix in self.config.suffixes.items():
                if not event.text.lower().endswith(suffix):
                    continue
                orig = await event.get_reply_message()
                if orig and orig.text.lower().split()[-1:] == [word]:
                    await event.reply("Ловко парировал(а) " + get_name(event.sender))
                    break

    def remove_chat(self, *chats):
        """remove chat handlers"""
        self.chats.difference_update(chats)
        self.__save_chats()

    async def get_chats(self):
        """get current handling chats"""
        for chat in self.chats:
            print(chat, ':', get_name(await client.get_entity(chat)))

    def add_word(self, word: str, suffix: str):
        """associate word with suffix"""
        self.config.suffixes[word] = suffix
        self.config.save()

    def remove_word(self, word):
        """remove word association"""
        self.config.suffixes.pop(word)
        self.config.save()

    def get_words(self):
        """get word and suffix associations"""
        for (word, suf) in self.config.suffixes.items():
            print(word, ':', suf)


yes_no_answers = YesNoAnswers()

__all__ = ['yes_no_answers']
