"""
    name: gachi
    needs:
        dot_hook: 0.0.1
    version: 0.0.1
"""


@dot_hook('gachi')
async def gachi(text="", message=None, is_edit=None):
    if message is None:
        return
    await message.edit("♂️" + text + "♂️")
