"""
    description: apply tex automatically and via .tex
    name: tex
    version: 0.2.0
    needs_pip:
      unicodeit: unicodeit
"""
import tgpy.api
import unicodeit


async def tex_hook(message=None, is_edit=None):
    text = message.text
    if text.startswith(".tex ") or text.startswith(".tex\n"):
        text = text[5:]
    else:
        is_tex_text = any(c in text for c in ['\\', '{', '}'])
        if not is_tex_text:
            return

    text = unicodeit.replace(text)
    if text != message.text:
        await message.edit(text)


tgpy.api.exec_hooks.add('tex', tex_hook)

__all__ = []
