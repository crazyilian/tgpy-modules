"""
    description: apply tex automatically and via .tex
    name: tex
    version: 0.3.0
    needs_pip:
      unicodeit: unicodeit
"""
import tgpy.api
import unicodeit

AUTOACTIVATE = ['^', r'\Alpha', r'\alpha', r'\Beta', r'\beta', r'\Gamma', r'\gamma', r'\Delta', r'\delta', r'\Epsiolon',
                r'\epsilon', r'\varepsilon', r'\Zeta', r'\zeta', r'\Eta', r'\eta', r'\Theta', r'\theta', r'\Iota',
                r'\iota', r'\Kappa', r'\kappa', r'\Lambda', r'\lambda', r'\Mu', r'\mu', r'\Nu', r'\nu', r'\Xi', r'\xi',
                r'\Omicron', r'\omicron', r'\Pi', r'\pi', r'\Rho', r'\rho', r'\Sigma', r'\sigma', r'\varsigma', r'\Tau',
                r'\tau', r'\Upsilon', r'\upsilon', r'\Phi', r'\phi', r'\varphi', r'\Chi', r'\chi', r'\Psi', r'\psi',
                r'\Omega', r'\omega', r'\mathbb', r'\mathcal', r'\ne', r'\approx', r'\le', r'\ge', r'\leqslant',
                r'\geqslant', r'\pm', r'\mp', r'\times', r'\cdot', r'\div', r'\sqrt', r'\angle', r'\perp', r'\parallel',
                r'\cong', r'\sim', r'\triangle', r'\equiv', r'\triangleq', r'\propto', r'\infty', r'\ll', r'\gg',
                r'\lfloor', r'\rfloor', r'\lceil', r'\rceil', r'\circ', r'\cap', r'\cup', r'\subseteq', r'\subset',
                r'\not', r'\superseteq', r'\superset', r'\in', r'\emptyset', r'\lor', r'\land', r'\neg', r'\oplus',
                r'\implies', r'\iff', r'\forall', r'\exists', r'\nexists', r'\therefore', r'\because', r'\int',
                r'\oint', r'\del', r'\preceq', r'\prec', r'\succeq', r'\succ', r'\d', r'\dots', r'\vdots', r'\cdots',
                r'\ddots', r'\qed', r'\sum', r'\prod', r'\leftarrow', r'\rightarrow', r'\uparrow', r'\downarrow',
                r'\leftrightarrow', r'\updownarrow', r'\Leftarrow', r'\Rightarrow', r'\Uparrow', r'\Downarrow',
                r'\Leftrightarrow', r'\Updownarrow', r'\to', r'\mapsto', r'\nearrow', r'\searrow', r'\swarrow',
                r'\nwarrow', r'\hookleftarrow', r'\hookrightarrow', r'\leftharpoonup', r'\rightharpoonup',
                r'\leftharpoondown', r'\rightharpoondown', r'\AA', r'\BB', r'\CC', r'\DD', r'\EE', r'\FF', r'\GG',
                r'\HH', r'\II', r'\JJ', r'\KK', r'\LL', r'\MM', r'\NN', r'\OO', r'\PP', r'\QQ', r'\RR', r'\SS', r'\TT',
                r'\UU', r'\VV', r'\WW', r'\XX', r'\YY', r'\ZZ']

ALIAS = {'\\' + c * 2: f'\\mathbb{{{c}}}' for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}


async def tex_hook(message=None, is_edit=None):
    text = message.text
    if text.startswith(".tex ") or text.startswith(".tex\n"):
        text = text[5:]
    elif text.startswith(".ntex ") or text.startswith(".ntex\n"):
        return await message.edit(text[6:])
    else:
        is_tex_text = is_autotex() and any(c in text for c in AUTOACTIVATE)
        if not is_tex_text:
            return message

    for f, t in ALIAS.items():
        text = text.replace(f, t)
    text = unicodeit.replace(text)
    if text != message.text:
        return await message.edit(text)
    else:
        return


def autotex(flag=True):
    """set auto activation of .tex to `flag`"""
    tgpy.api.config.set('tex.auto_activate', flag)


def is_autotex():
    """get if auto activation of .tex is true"""
    return tgpy.api.config.get('tex.auto_activate', True)


tgpy.api.exec_hooks.add('tex', tex_hook)

__all__ = ['autotex', 'is_autotex']
