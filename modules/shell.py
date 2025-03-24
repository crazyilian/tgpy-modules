"""
    name: shell
    once: false
    origin: tgpy://module/shell
    priority: 1700000001
"""
logger = ConsoleLogger(f"{__name__.split('/')[-1]}\t| ")

import asyncio


@dot('sh')
async def run_sh(cmd=""):
    logger.print(cmd)
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    stdout, _ = await proc.communicate()
    text, returncode = stdout.decode(), proc.returncode
    return text + (f"\n\nReturn code: {returncode}" if returncode != 0 else "")

__all__ = []
