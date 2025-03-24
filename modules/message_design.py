"""
    name: message_design
    once: false
    origin: tgpy://module/message_design
    priority: 3
"""
import tgpy._core.message_design as md

md.TITLE = '$>'
# md.RUNNING_TITLE = 'TGPy running>'
# md.FORMATTED_ERROR_HEADER = f'<b><a href="{md.TITLE_URL}">TGPy error&gt;</a></b>'    # do not change url! (tgpy will break)

__all__ = []
