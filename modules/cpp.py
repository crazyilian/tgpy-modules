"""
    name: cpp
    once: false
    origin: tgpy://module/cpp
    priority: 1700000003
"""
logger = ConsoleLogger(f"{__name__.split('/')[-1]}\t| ")

import asyncio


@dot('cpp')
async def run_cpp(cmd=''):
    logger.print(cmd)
    with open("/tmp/tmp.cpp", "w") as out:
        out.write(cmd)

    proc = await asyncio.create_subprocess_exec(
        "g++", "-std=c++20", "/tmp/tmp.cpp", "-o", "/tmp/cpp_res",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    if proc.returncode != 0:
        return stdout.decode()

    proc = await asyncio.create_subprocess_exec(
        "/tmp/cpp_res",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    stdout, _ = await proc.communicate()
    text, returncode = stdout.decode(), proc.returncode
    return text + (f"\n\nReturn code: {returncode}" if returncode != 0 else "")

__all__ = []
