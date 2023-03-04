"""
    description: decorator dot to make function usable through .{prx}, but run it as hook
    name: dot_hook
    needs:
      await_utils: 0.0.0
    version: 0.0.1
"""
import tgpy.api


def dot_hook(prx, prevent=True):
    """decorator to make function usable through .{prx}, but run it as hook"""

    def prx_decorator(f):
        async def prx_hook(message, is_edit):
            txt = message.raw_text
            if txt.lower().startswith(f".{prx} ") or txt.lower().startswith(f".{prx}\n"):
                txt = txt[len(prx) + 2:]
                res = await await_if_awaitable(f(txt, message=message, is_edit=is_edit))
            elif txt.lower() == f".{prx}":
                res = await await_if_awaitable(f(message=message, is_edit=is_edit))
            else:
                return True

            if prevent:
                return False
            return res

        tgpy.api.exec_hooks.add(prx, prx_hook)
        return f

    return prx_decorator
