"""
    description: send random file on `ladno()`'
    name: ladno
    needs_pip:
        zstd: zstd
        base65536: base65536
    version: 0.0.1
"""
import telethon
import random
import tgpy.api
import zstd
import base65536


def compress(text):
    return 'zstd:' + base65536.encode(zstd.compress(text.encode(), 22))


def decompress(text):
    return zstd.decompress(base65536.decode(text[5:])).decode()


class Ladno:
    """
        Concept: automatic send random sticker reaction instead of ладно (ok)
        Add few stickers (or images/gifs/videos) and send `ladno()`
    """

    def _get_files(self):
        return tgpy.api.config.get('ladno_files.files', [])

    def number(self):
        """number of files in list"""
        return len(self._get_files())

    def _add_files(self, *f):
        fs = self._get_files()
        fs.extend(f)
        tgpy.api.config.save()

    def _remove_files(self, *f):
        fs = self._get_files()
        cnt = 0
        for file in f:
            for added in fs:
                if added['id'] == file['id'] and added['access_hash'] == added['access_hash']:
                    fs.remove(added)
                    cnt += 1
                    break
        tgpy.api.config.save()
        return cnt

    def _to_tg_file(self, f):
        return telethon.types.InputDocument(
            id=f['id'],
            access_hash=f['access_hash'],
            file_reference=bytes.fromhex(f['file_reference'])
        )

    def _from_tg_file(self, tgf):
        try:
            return {
                'id': tgf.media.id,
                'access_hash': tgf.media.access_hash,
                'file_reference': tgf.media.file_reference.hex()
            }
        except:
            return None

    async def __call__(self, ind=None):
        """`send(ind)` but removes call message"""
        await ctx.msg.delete()
        return await self.send(ind)

    async def send(self, ind=None):
        """Send file with index `ind`. If `ind` is None, choose random one."""
        files = self._get_files()
        if len(files) == 0:
            return 'No files'
        if ind is None:
            file = random.choice(files)
        else:
            file = files[ind]
        await ctx.msg.respond(file=self._to_tg_file(file))
        return 'Done'

    async def send_all(self):
        """send all files"""
        files = self._get_files()
        if len(files) == 0:
            return 'No files'
        for file in files:
            await ctx.msg.respond(file=self._to_tg_file(file))
        return 'Done'

    async def share_compressed(self):
        """share compressed python list of files"""
        arr = [repr((f['id'], f['access_hash'], f['file_reference'])) for f in self._get_files()]
        await ctx.msg.respond(f'<code>{compress(repr(arr))}</code>')
        return f'Shared {len(arr)} files'

    async def _get_from_raw_reply(self):
        orig = await ctx.msg.get_reply_message()
        try:
            arr = eval(decompress(orig.raw_text))
            return [{'id': f[0], 'access_hash': f[1], 'file_reference': f[2]} for f in arr]
        except:
            return None

    async def _get_file_from_reply(self):
        orig = await ctx.msg.get_reply_message()
        file = None
        if orig is not None and orig.file is not None:
            file = self._from_tg_file(orig.file)
        return file

    async def _get_files_since_reply(self):
        orig = await ctx.msg.get_reply_message()
        if orig is None:
            return 'Reply to message to add all files after it'
        files = []
        async for mess in client.iter_messages(orig.chat_id):
            if mess.file is not None:
                f = self._from_tg_file(mess.file)
                if f is not None:
                    files.append(f)
            if mess.id == orig.id:
                break
        return list(reversed(files))

    async def add(self):
        """add one file from reply"""
        file = await self._get_file_from_reply()
        if file is None:
            return 'No files in reply'
        self._add_files(file)
        return 'Done'

    async def add_compressed_list(self):
        """add all files in compressed list from reply"""
        files = await self._get_from_raw_reply()
        if files is None:
            return 'Reply to shared files list'
        self._add_files(*files)
        return f'Added {len(files)} files'

    async def add_since(self):
        """add all files in all messages from reply to current"""
        files = await self._get_files_since_reply()
        self._add_files(*files)
        return f'Added {len(files)} files'

    async def remove(self, ind=None):
        """remove one file from reply (or with index `ind` if not None)"""
        if ind is None:
            file = await self._get_file_from_reply()
        else:
            file = self._get_files()[ind]
        if file is None:
            return 'No files in reply'
        if self._remove_files(file):
            return 'Done'
        else:
            return 'No such file'

    async def remove_compressed_list(self):
        """remove all files in compressed list from reply"""
        files = await self._get_from_raw_reply()
        if files is None:
            return 'Reply to shared files list'
        cnt = self._remove_files(*files)
        return f'Removed {cnt} files'

    async def remove_since(self):
        """remove all files in all messages from reply to current"""
        files = await self._get_files_since_reply()
        cnt = self._remove_files(*files)
        return f'Removed {cnt} files'

    async def remove_all(self):
        """remove all files"""
        files = self._get_files()
        cnt = self._remove_files(*files)
        return f'Removed {cnt} files'


ladno = Ladno()

__all__ = ['ladno']
