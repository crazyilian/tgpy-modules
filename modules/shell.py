"""
    description: run and use shell via .sh & run shell functions
    name: shell
    needs:
      dot: 0.1.0
    version: 0.1.0
"""
import asyncio
import subprocess


async def run_shell(code, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, **kwargs):
    proc = await asyncio.create_subprocess_shell(code, stdout=stdout, stderr=stderr, **kwargs)
    stdout, _ = await proc.communicate()
    return stdout.decode(), proc.returncode


def run_sync_shell(arguments, capture_output=True, check=True, encoding='utf-8', **kwargs):
    proc = subprocess.run(arguments, capture_output=capture_output, check=check, encoding=encoding, **kwargs)
    return proc.stdout, proc.returncode


@dot('sh')
async def sh(code=''):
    text, returncode = await run_shell(code)
    return text + (f"\n\nReturn code: {returncode}" if returncode != 0 else "")
