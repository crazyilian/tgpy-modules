"""
    description: replace default "TGPy>" prefix
    name: message_design
    version: 1.0.0
"""
import tgpy._core.message_design as message_design
import tgpy.api

DEFAULT_TITLE = message_design.TITLE
message_design.TITLE = tgpy.api.config.get('message_design.prefix', DEFAULT_TITLE)


def set_tgpy_prefix(prefix=DEFAULT_TITLE):
    message_design.TITLE = prefix
    tgpy.api.config.set('message_design.prefix', prefix)


__all__ = [set_tgpy_prefix]
