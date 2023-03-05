"""
    description: factorize numbers asynchronously
    name: factor_async
    needs:
      shell: 0.1.0
      await_utils: 0.0.0
    needs_pip:
      sympy: sympy
    version: 0.1.0
"""
from collections import defaultdict
import sympy


async def factor_rho(n):
    res = (await run_shell(f"factor {n}"))[0]
    return list(map(int, res.partition(":")[2].split()))


async def factor_ecm(n):
    res = (await run_shell(f"echo {n} | ecm -q 3000000"))[0]
    prefactors = list(map(int, res.split()))
    factors = []
    for prefactor in prefactors:
        factors += await factor(prefactor)
    return factors


async def _factor(n):
    if await await_sync(sympy.isprime, n):
        return [n]
    if n < 10 ** 38:
        return await factor_rho(n)
    return await factor_ecm(n)


async def factor(n):
    return sorted(await _factor(int(n)))


@dot('factor')
async def factor_text(n=None):
    if n is None:
        return "No number to factor"
    n = int(n)
    if n == 1:
        return "1"
    by_power = defaultdict(int)
    for x in await factor(n):
        by_power[x] += 1
    return " × ".join(str(k) if v == 1 else str(k) + superscript(v) for k, v in by_power.items())


def superscript(n):
    return ("⁻" if n < 0 else "") + "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(c)] for c in str(abs(n)))


__all__ = ['factor', 'factor_text']
