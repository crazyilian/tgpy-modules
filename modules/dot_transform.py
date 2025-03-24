"""
    name: dot_transform
    once: false
    origin: tgpy://module/dot_transform
    priority: 1
"""
logger = ConsoleLogger(f"{__name__.split('/')[-1]}\t| ")

import tgpy.api

DOT_HANDLERS = dict()


def get_dot_handler(prx):
    return DOT_HANDLERS.get(prx, lambda *_: None)


def dot(prx):
    def prx_decorator(f):
        logger.print(f"Registering .{prx}")

        DOT_HANDLERS[prx] = f

        def prx_trans(txt):
            if txt.lower().startswith(f".{prx} ") or txt.lower().startswith(f".{prx}\n"):
                txt = txt[len(prx) + 2:]
                return f"get_dot_handler({repr(prx)})({repr(txt)})"
            elif txt.lower() == f".{prx}":
                return f"get_dot_handler({repr(prx)})()"
            else:
                return txt

        tgpy.api.code_transformers.add(prx, prx_trans)
        return f

    return prx_decorator


__all__ = ["dot", "get_dot_handler"]
