"""
    description: apply tex automatically and via .tex
    name: tex
    version: 0.1.0
"""
import re
import tgpy.api

ALPHABET = {
    # Greek letters
    "\\Alpha": "Α",
    "\\alpha": "α",
    "\\Beta": "Β",
    "\\beta": "β",
    "\\Gamma": "Γ",
    "\\gamma": "γ",
    "\\Delta": "Δ",
    "\\delta": "δ",
    "\\Epsiolon": "Ε",
    "\\epsilon": "ϵ",
    "\\varepsilon": "ε",
    "\\Zeta": "Ζ",
    "\\zeta": "ζ",
    "\\Eta": "Η",
    "\\eta": "η",
    "\\Theta": "Θ",
    "\\theta": "θ",
    "\\Iota": "Ι",
    "\\iota": "ι",
    "\\Kappa": "Κ",
    "\\kappa": "κ",
    "\\Lambda": "Λ",
    "\\lambda": "λ",
    "\\Mu": "Μ",
    "\\mu": "μ",
    "\\Nu": "Ν",
    "\\nu": "ν",
    "\\Xi": "Ξ",
    "\\xi": "ξ",
    "\\Omicron": "Ο",
    "\\omicron": "ο",
    "\\Pi": "Π",
    "\\pi": "π",
    "\\Rho": "Ρ",
    "\\rho": "ρ",
    "\\Sigma": "Σ",
    "\\sigma": "σ",
    "\\varsigma": "ς",
    "\\Tau": "Τ",
    "\\tau": "τ",
    "\\Upsilon": "Υ",
    "\\upsilon": "υ",
    "\\Phi": "Φ",
    "\\phi": "ϕ",
    "\\varphi": "φ",
    "\\Chi": "Χ",
    "\\chi": "χ",
    "\\Psi": "Ψ",
    "\\psi": "ψ",
    "\\Omega": "Ω",
    "\\omega": "ω",

    # Blackboard bold
    "\\mathbb{A}": "𝔸",
    "\\mathbb{a}": "𝕒",
    "\\mathbb{B}": "𝔹",
    "\\mathbb{b}": "𝕓",
    "\\mathbb{C}": "ℂ",
    "\\mathbb{c}": "𝕔",
    "\\mathbb{D}": "𝔻",
    "\\mathbb{d}": "𝕕",
    "\\mathbb{E}": "𝔼",
    "\\mathbb{e}": "𝕖",
    "\\mathbb{F}": "𝔽",
    "\\mathbb{f}": "𝕗",
    "\\mathbb{G}": "𝔾",
    "\\mathbb{g}": "𝕘",
    "\\mathbb{H}": "ℍ",
    "\\mathbb{h}": "𝕙",
    "\\mathbb{I}": "𝕀",
    "\\mathbb{i}": "𝕚",
    "\\mathbb{J}": "𝕁",
    "\\mathbb{j}": "𝕛",
    "\\mathbb{K}": "𝕂",
    "\\mathbb{k}": "𝕜",
    "\\mathbb{L}": "𝕃",
    "\\mathbb{l}": "𝕝",
    "\\mathbb{M}": "𝕄",
    "\\mathbb{m}": "𝕞",
    "\\mathbb{N}": "ℕ",
    "\\mathbb{n}": "𝕟",
    "\\mathbb{O}": "𝕆",
    "\\mathbb{o}": "𝕠",
    "\\mathbb{P}": "ℙ",
    "\\mathbb{p}": "𝕡",
    "\\mathbb{Q}": "ℚ",
    "\\mathbb{q}": "𝕢",
    "\\mathbb{R}": "ℝ",
    "\\mathbb{r}": "𝕣",
    "\\mathbb{S}": "𝕊",
    "\\mathbb{s}": "𝕤",
    "\\mathbb{T}": "𝕋",
    "\\mathbb{t}": "𝕥",
    "\\mathbb{U}": "𝕌",
    "\\mathbb{u}": "𝕦",
    "\\mathbb{V}": "𝕍",
    "\\mathbb{v}": "𝕧",
    "\\mathbb{W}": "𝕎",
    "\\mathbb{w}": "𝕨",
    "\\mathbb{X}": "𝕏",
    "\\mathbb{x}": "𝕩",
    "\\mathbb{Y}": "𝕐",
    "\\mathbb{y}": "𝕪",
    "\\mathbb{Z}": "ℤ",
    "\\mathbb{z}": "𝕫",
    "\\mathbb{0}": "𝟘",
    "\\mathbb{1}": "𝟙",
    "\\mathbb{2}": "𝟚",
    "\\mathbb{3}": "𝟛",
    "\\mathbb{4}": "𝟜",
    "\\mathbb{5}": "𝟝",
    "\\mathbb{6}": "𝟞",
    "\\mathbb{7}": "𝟟",
    "\\mathbb{8}": "𝟠",
    "\\mathbb{9}": "𝟡",

    # Basic math
    "\\ne": "≠",
    "\\approx": "≈",
    "\\le": "≤",
    "\\ge": "≥",
    "\\leqslant": "⩽",
    "\\geqslant": "⩾",
    "\\pm": "±",
    "\\mp": "∓",
    "\\times": "×",
    "\\cdot": "⋅",
    "\\div": "÷",
    "\\sqrt": "√",

    # Geometry
    "\\angle": "∠",
    "\\perp": "⊥",
    "\\parallel": "∥",
    "\\cong": "≅",
    "\\sim": "~",
    "\\triangle": "Δ",

    # Algebra
    "\\equiv": "≡",
    "\\triangleq": "≜",
    "\\propto": "∝",
    "\\infty": "∞",
    "\\ll": "≪",
    "\\gg": "≫",
    "\\lfloor": "⌊",
    "\\rfloor": "⌋",
    "\\lceil": "⌈",
    "\\rceil": "⌉",
    "\\circ": "∘",

    # Set theory
    "\\cap": "∩",
    "\\cup": "∪",
    "\\not\\subset": "⊄",
    "\\subseteq": "⊆",
    "\\subset": "⊂",
    "\\not\\superset": "⊅",
    "\\superseteq": "⊇",
    "\\superset": "⊃",
    "\\not\\in": "∉",
    "\\in": "∈",
    "\\emptyset": "Ø",

    # Logic
    "\\lor": "∨",
    "\\land": "∧",
    "\\neg": "¬",
    "\\oplus": "⊕",
    "\\implies": "⇒",
    "\\iff": "⇔",
    "\\forall": "∀",
    "\\exists": "∃",
    "\\nexists": "∄",
    "\\therefore": "∴",
    "\\because": "∵",

    # Calculus
    "\\int": "∫",
    "\\oint": "∮",
    "\\del": "∇",
    "\\preceq": "≼",
    "\\prec": "≺",
    "\\succeq": "≽",
    "\\succ": "≻",
    "\\d": "∂",

    # Superscript
    "^0": "⁰",
    "^1": "¹",
    "^2": "²",
    "^3": "³",
    "^4": "⁴",
    "^5": "⁵",
    "^6": "⁶",
    "^7": "⁷",
    "^8": "⁸",
    "^9": "⁹",

    # Misc
    "\\dots": "…",
    "\\vdots": "⋮",
    "\\cdots": "⋯",
    "\\ddots": "⋱",
    "^\\circ": "°",
    "\\qed": "□",
    "\\sum": "∑",
    "\\prod": "∏",

    # Arrows
    "\\leftarrow": "←",
    "\\rightarrow": "→",
    "\\uparrow": "↑",
    "\\downarrow": "↓",
    "\\leftrightarrow": "↔",
    "\\updownarrow": "↕",
    "\\Leftarrow": "⇐",
    "\\Rightarrow": "⇒",
    "\\Uparrow": "⇑",
    "\\Downarrow": "⇓",
    "\\Leftrightarrow": "⇔",
    "\\Updownarrow": "⇕",
    "\\to": "→",
    "\\mapsto": "↦",
    "\\nearrow": "↗",
    "\\searrow": "↘",
    "\\swarrow": "↙",
    "\\nwarrow": "↖",
    "\\hookleftarrow": "↩",
    "\\hookrightarrow": "↪",
    "\\leftharpoonup": "↼",
    "\\rightharpoonup": "⇀",
    "\\leftharpoondown": "↽",
    "\\rightharpoondown": "⇁",
}

ALPHABET = {k: v for (k, v) in sorted(ALPHABET.items(), reverse=True)}


def apply_tex(text):
    text = text.replace("\\\\", "\x00")
    text = re.sub(r"\^\{([0-9]+)\}", lambda m: "".join("^" + c for c in m.group(1)), text)
    for from_, to in ALPHABET.items():
        text = text.replace(from_, to)
    text = text.replace("\x00", "\\")
    return text


async def tex_hook(message=None, is_edit=None):
    text = message.text
    if text.startswith(".tex ") or text.startswith(".tex\n"):
        text = text[6:]
    else:
        is_tex_text = any(from_ in text for from_ in ALPHABET) or "^" in text
        if not is_tex_text:
            return

    text = apply_tex(text)
    if text != message.text:
        await message.edit(text)


tgpy.api.exec_hooks.add('tex', tex_hook)

__all__ = ['apply_tex']
