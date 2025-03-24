"""
    name: tex
    once: false
    origin: tgpy://modules/tex
    priority: 1700000007
"""
logger = ConsoleLogger(f"{__name__.split('/')[-1]}\t| ")

import tgpy.api
import unicodeit.data
import regex as re


def replace(f: str):  # modified unicodeit.replace
    # modifications begin
    for r in NOTALIAS:
        f = f.replace(r[0], r[1])
        if r[0].endswith('{}'):
            f = f.replace('\\ ' + r[0][1:], r[1])
    # modifications end

    f = re.sub(r'\\not(\\[A-z]+)', r'\\slash{\1}', f)
    for c in unicodeit.data.COMBININGMARKS:
        f = f.replace(c[0] + '{', '\\ ' + c[0][1:] + '{')
    for r in unicodeit.data.REPLACEMENTS:
        f = f.replace(r[0], r[1])
        if r[0].endswith('{}'):
            f = f.replace('\\ ' + r[0][1:], r[1])

    # modifications begin
    supsript_orig = '|'.join(re.escape(key[1:]) for key, val in unicodeit.data.SUBSUPERSCRIPTS if key[0] == '_')
    subsript_orig = '|'.join(re.escape(key[1:]) for key, val in unicodeit.data.SUBSUPERSCRIPTS if key[0] == '^')
    for prefix, orig in [('_', supsript_orig), ('^', subsript_orig)]:
        offset = 0
        for s in re.finditer(fr"{re.escape(prefix)}\{{({orig})+\}}", f):
            newstring, n = re.subn(fr"({orig})", fr"{prefix}\1", s.group(0)[2:-1])
            f = f[:s.start() + offset] + newstring + f[s.end() + offset:]
            offset += n * 2 - (n + 3)
    # modifications end

    for r in unicodeit.data.SUBSUPERSCRIPTS:
        f = f.replace(r[0], r[1])
    for c in unicodeit.data.COMBININGMARKS:
        escaped_latex = f'\\ {c[0][1:]}{{'
        while escaped_latex in f:
            i = f.index(escaped_latex)
            if len(f) <= i + len(escaped_latex):
                f = f[:i] + c[0] + '{'
                continue
            combined_char = f[i + len(escaped_latex)]
            remainder = ''
            if len(f) >= i + len(escaped_latex) + 2:
                remainder = f[i + len(escaped_latex) + 2:]
            f = f[:i] + combined_char + c[1] + remainder
    return f


ALIAS = [('\\' + c * 2, fr'\mathbb{{{c}}}') for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
ALIAS += [
    (r'\Alpha', 'A'), (r'\Beta', 'B'), (r'\Epsilon', 'E'), (r'\Zeta', 'Z'), (r'\Eta', 'H'), (r'\Iota', 'I'),
    (r'\Kappa', 'K'), (r'\Mu', 'M'), (r'\Nu', 'N'), (r'\Omicron', 'O'), (r'\Rho', 'P'), (r'\Tau', 'T'), (r'\Chi', 'X')
]
ALIAS += [
    (r'\omicron', r'\mitomicron'),
    # (r'\epsilon', r'\varepsilon'),
    (r'\superseteq', r'\supseteq'),
    (r'\superset', r'\supset'),
    (r'\nsuperseteq', r'\nsupseteq'),
    (r'\nsuperset', r'\nsupset'),
    (r'\dots', r'\ldots'),
    (r'\qed', r'\blacksquare'),
    (r'\divby', r'\vdots'),
]
ALIAS += [(r'\not', r'\not')]  # disable replacing
NOTALIAS = [
    (r'\not\in', r'\notin'),
    (r'\not\supseteq', r'\nsupseteq'),
    (r'\not\supset', r'\nsupset'),
    (r'\not\superseteq', r'\nsuperseteq'),
    (r'\not\superset', r'\nsuperset'),
    (r'\not\subseteq', r'\nsubseteq'),
    (r'\not\subset', r'\nsubset'),
    (r'\not\exists', r'\nexists')
]


def modify_replacements(repls, positive=()):
    repls_dict = dict(repls)
    repls_dict |= {key: replace(val) for key, val in positive}
    repls.clear()
    repls += repls_dict.items()
    repls.sort(key=lambda el: -len(el[0]))


modify_replacements(unicodeit.data.REPLACEMENTS, ALIAS)
modify_replacements(unicodeit.data.SUBSUPERSCRIPTS, [
    ('^/', '⸍'),
    ('_/', '⸝'),
    ('^\\', '⸌'),
    ('_\\', '⸜'),
    ('_ ', ' '),  # thin space
    ('^ ', ' '),  # thin space
    ('^\'', '\''),

    # ('^q', '𐞥'), # no font in mobile tg

    # ('^C', 'ꟲ'), # no font in mobile tg
    ('^C', 'ᶜ'),  # = lower c

    # ('^F', 'ꟳ'), # no font in mobile tg
    ('^F', 'ᶠ'),  # = lower f

    # ('^Q', 'ꟴ'), # no font in mobile tg

    ('^S', 'ˢ'),  # = lower s

    ('^V', 'ⱽ'),

    ('^X', 'ˣ'),  # = lower x

    # ('^Y', '𐞲'), # no font in mobile tg
    ('^Y', 'ʸ'),  # = lower y

    ('^Z', 'ᙆ'),
])  # no supscript for all upper letters and lower bcdfgqwyz

autotex = {key: set(value) for key, value in tgpy.api.config.get('tex', {}).items()}


def save_config():
    data = {key: list(value) for key, value in autotex.items()}
    tgpy.api.config.set('tex', data)


async def tex_edit(message=None, is_edit=None):
    text = message.text
    chat_id = str(message.chat_id)
    msg_id = message.id
    new_text = text

    if text.startswith('.tex ') or text.startswith('.tex\n'):
        if chat_id not in autotex:
            autotex[chat_id] = set()
        if msg_id not in autotex[chat_id]:
            autotex[chat_id].add(msg_id)
            save_config()
        new_text = text[5:]

    elif text.startswith('.ntex ') or text.startswith('.ntex\n'):
        if chat_id in autotex and msg_id in autotex[chat_id]:
            autotex[chat_id].remove(msg_id)
            save_config()
        new_text = text[6:]

    if message.id in autotex.get(str(message.chat_id), {}):
        new_text = replace(new_text)

    if new_text != text:
        logger.print(text)
        logger.print(new_text)
        return await message.edit(new_text)


tgpy.api.exec_hooks.add('tex_edit', tex_edit)

__all__ = []
