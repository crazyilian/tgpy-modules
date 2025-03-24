"""
    name: py_macro
    once: false
    origin: tgpy://modules/py_macro
    priority: 1700000006
"""
logger = ConsoleLogger(__name__.split('/')[-1] + '\t| ')

from unsync import unsync
import tgpy.api


@unsync
async def py_macro_applier(code):
    return (await tgpy.api.tgpy_eval(code)).result


@add_macro("py")
def py_macro(code):
    logger.print(code)
    return str(py_macro_applier(code).result())


__all__ = []
