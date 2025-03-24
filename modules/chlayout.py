"""
    name: chlayout
    once: false
    origin: tgpy://module/chlayout
    priority: 1700000002
"""
logger = ConsoleLogger(f"{__name__.split('/')[-1]}\t| ")

en_layout = '`1234567890-=qwertyuiop[]asdfghjkl;\'\\zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?'
ru_layout = 'ё1234567890-=йцукенгшщзхъфывапролджэ\\ячсмитьбю.Ё!"№;%:?*()_+ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,'
translation_en_to_ru = str.maketrans(dict(zip(en_layout, ru_layout)))
translation_ru_to_en = str.maketrans(dict(zip(ru_layout, en_layout)))
en_layout_set = set(en_layout)
ru_layout_set = set(ru_layout)


@dot('chlayout')
async def chlayout(target=None):
    orig = await ctx.msg.get_reply_message()
    text = orig.text
    logger.print(text)
    if target is None:
        cnt_ru_not_en = sum(c in ru_layout_set and c not in en_layout_set for c in text)
        cnt_en_not_ru = sum(c in en_layout_set and c not in ru_layout_set for c in text)
        target = 'ru' if cnt_ru_not_en <= cnt_en_not_ru else 'en'
    if target.lower() == 'ru':
        return text.translate(translation_en_to_ru)
    elif target.lower() == 'en':
        return text.translate(translation_ru_to_en)
    else:
        return 'Error: `target` argument must be "ru" or "en"'


__all__ = ["chlayout"]
