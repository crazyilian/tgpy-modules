"""
    name: macro_hook
    once: false
    origin: tgpy://module/macro_hook
    priority: 5
"""
logger = ConsoleLogger(__name__.split('/')[-1] + '\t| ')

import regex
import tgpy.api

macros = {}

def add_macro(name):
    def macro_adder(f):
        macros[name] = f

    return macro_adder


# match `name!(code)` where `code` is smth with correct parentheses. `code` may contain macros inside.
macro_re = regex.compile(r"(\w+)!\(([^()]*(\((?2)\)(?2)|[^()]*))\)")

def applier(match):
    try:
        logger.print(match.group(0))
        return macros[match.group(1)](apply_macros(match.group(2)))
    except:
        return match.group(0)


def apply_macros(txt):
    return regex.sub(macro_re, applier, txt)


async def macros_handler(msg, _):
    text = apply_macros(msg.text)
    if text != msg.text:
        return await msg.edit(text)


tgpy.api.exec_hooks.add("macros_handler", macros_handler)

__all__ = ["add_macro"]
