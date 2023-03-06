"""
    name: gachi
    needs:
        dot_hook: 0.0.1
"""


@dot_hook('gachi')
async def gachi(text, message, is_edit):
    await message.edit("♂️" + text + "♂️")
