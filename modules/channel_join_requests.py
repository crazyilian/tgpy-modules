"""
    description: track pending join requests in target channels
    name: channel_join_requests
    needs:
      config_loader: 0.0.0
      cron: 0.0.0
      pet_bot: 0.0.0
      tg_name: 0.0.0
    version: 0.0.0
"""
import telethon


class OneChannelJoinRequests:
    def __init__(self, channel_id, module):
        self.module = module
        self.id = channel_id
        self.name = None

    def get_requesters(self):
        return self.module.config.requesters[self.id]

    async def get_updates(self):
        full_channel = await client(telethon.functions.channels.GetFullChannelRequest(self.id))
        self.name = full_channel.chats[0].title

        new_users = []
        requesters = self.get_requesters().copy()
        for user in full_channel.users:
            if user.is_self:
                continue
            if user.id not in requesters:
                new_users.append(user)
            else:
                requesters.remove(user.id)
        joined_users_id = requesters
        return new_users, joined_users_id

    async def save_updates(self, new_users, joined_users_id):
        for user in new_users:
            self.module.config.requesters[self.id].append(user.id)
        for user_id in joined_users_id:
            self.module.config.requesters[self.id].remove(user_id)
        self.module.config.save()

    async def update_name(self):
        full_channel = await client(telethon.functions.channels.GetFullChannelRequest(self.id))
        self.name = full_channel.chats[0].title
        return self.name


class ChannelJoinRequestsModule:
    def __init__(self):
        self.config = ModuleConfig('channel_join_requests',
                                   default_dict={'channel_ids': [], 'requesters': {}})
        self.channels = [OneChannelJoinRequests(id, self) for id in self.config.channel_ids]
        cron_add_job(self.update, "0 * * * *")

    def get_requesters(self):
        result = {}
        for channel in self.channels:
            result[channel.id] = channel.get_requesters()
        return result

    def add_channel(self, channel_id):
        self.config.channel_ids.append(channel_id)
        self.config.requesters[channel_id] = []
        self.config.save()
        self.channels.append(OneChannelJoinRequests(channel_id, self))

    def remove_channel(self, channel_id):
        if channel_id not in self.config.channel_ids:
            return
        self.config.channel_ids.remove(channel_id)
        self.config.requesters.pop(channel_id)
        self.config.save()
        for ind, channel in enumerate(self.channels, 0):
            if channel.id == channel_id:
                self.channels.pop(ind)
                break

    async def get_channels(self):
        res = {}
        for channel in self.channels:
            if channel.name is None:
                await channel.update_name()
            res[channel.id] = channel.name
        return res

    async def update(self):
        for channel in self.channels:
            new_users, joined_users_id = await channel.get_updates()
            await channel.save_updates(new_users, joined_users_id)

            if new_users:
                notify_message = f'New joining requests in channel "{channel.name}"'
                for user in new_users:
                    user = await client.get_entity(user)  # fix user.username == None
                    notify_message += f'\n' + get_name(user)
                await pet_bot.notify(notify_message)


channel_join_requests = ChannelJoinRequestsModule()

__all__ = ['channel_join_requests']
