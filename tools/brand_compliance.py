"""Brand-compliance logic for Poesys surfaces (BRAND_CONSTITUTION.md / BRAND_RULES.md).

The token source (`site/brand/tokens.json`) is the SOLE home of every colour value. This
module gives the harness (and any surface linter) the primitives to enforce that:

  * `find_raw_hex(text)`          -- law: surfaces consume tokens, never raw hex values.
  * `find_soft_as_text(css)`      -- law 3: soft colours are fills behind black text only,
                                     never `color:`, border, outline or stroke.
  * `generate_css(tokens)`        -- deterministic `:root{ --token: value }` projection of the
                                     JSON source, so the CSS mirror is provably not an
                                     independent colour home.

Nothing here mutates files. `tests/tools/test_brand_compliance.py` wires it as a real test.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
BRAND_DIR = REPO_ROOT / "site" / "brand"
TOKENS_PATH = BRAND_DIR / "tokens.json"
CSS_PATH = BRAND_DIR / "tokens.css"

# A hex colour literal: #RGB, #RRGGBB, #RRGGBBAA (word-bounded so we don't match "#" anchors).
HEX_RE = re.compile(r"#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{1}|[0-9A-Fa-f]{3}|[0-9A-Fa-f]{5})?\b")

# Properties whose value is text-coloured or a thin line: soft may never appear here (law 3).
_TEXT_OR_LINE_PROP = (
    r"(?:color|border(?:-(?:top|right|bottom|left))?(?:-color)?|outline(?:-color)?"
    r"|text-decoration(?:-color)?|stroke|column-rule(?:-color)?|caret-color)"
)


def load_tokens(path: Path | None = None) -> dict:
    """Parse the W3C design-tokens JSON source."""
    path = path or TOKENS_PATH
    return json.loads(path.read_text())


def _walk_colors(node, prefix: str = "") -> Iterable[tuple[str, str]]:
    """Yield (dashed-name, hex-value) for every ``$type: color`` leaf under a tokens subtree."""
    if not isinstance(node, dict):
        return
    if node.get("$type") == "color" and isinstance(node.get("$value"), str):
        yield prefix, node["$value"]
        return
    for key, child in node.items():
        if key.startswith("$"):
            continue
        child_prefix = f"{prefix}-{key}" if prefix else key
        yield from _walk_colors(child, child_prefix)


def color_values(tokens: dict) -> dict[str, str]:
    """Map of dashed token name -> hex value, e.g. ``{'blue-bright': '#0047FF', ...}``."""
    return dict(_walk_colors(tokens.get("color", {})))


def soft_color_names(tokens: dict) -> list[str]:
    return [name for name in color_values(tokens) if name.endswith("-soft")]


def soft_color_hexes(tokens: dict) -> set[str]:
    return {v.upper() for k, v in color_values(tokens).items() if k.endswith("-soft")}


def find_raw_hex(text: str) -> list[str]:
    """Every raw hex colour literal in a surface. Consuming surfaces must return []."""
    return HEX_RE.findall(text)


def find_soft_as_text(css_text: str, soft_names: Iterable[str], soft_hexes: Iterable[str]) -> list[str]:
    """Flag any soft colour (by ``--*-soft`` var or by soft hex) used as text/thin-line colour.

    Matches declarations like ``color: var(--blue-soft)`` or ``border-color:#DCE7FF``. A soft
    colour used as ``background``/``fill`` behind black text is legitimate and is NOT flagged.
    Returns the offending declaration substrings.
    """
    names = [re.escape(n) for n in soft_names]
    hexes = [re.escape(h) for h in soft_hexes]
    alts = []
    if names:
        alts.append(r"var\(\s*--(?:%s)\s*\)" % "|".join(names))
    if hexes:
        alts.append(r"(?:%s)" % "|".join(hexes))
    if not alts:
        return []
    value = r"(?:%s)" % "|".join(alts)
    pat = re.compile(rf"{_TEXT_OR_LINE_PROP}\s*:\s*[^;{{}}]*?{value}", re.IGNORECASE)
    return [m.group(0).strip() for m in pat.finditer(css_text)]


# ---- light-default / dark-as-accent (BRAND_CONSTITUTION.md §3a) ------------------------------
# The base (body/html) surface of a page must be light; dark is a sparing ACCENT applied to a
# child element (hero/panel), never the page ground. `base_surface_is_dark` resolves the base
# background through the page's own :root custom properties AND the brand tokens, then judges it
# by WCAG relative luminance. It looks ONLY at the base surface, so a light page carrying a
# sparing dark accent panel passes, while a dark-ground page fails.

# A CSS named colour we may meet as a bare background keyword (minimal set that actually occurs).
_NAMED_COLORS = {"white": "#FFFFFF", "black": "#000000", "transparent": None}

# body/html rule -> its background(-color) value (first background declaration in the rule body).
_BASE_BG_RE = re.compile(
    r"(?:^|[^A-Za-z-])(?:body|html)\b[^{}]*\{[^{}]*?\bbackground(?:-color)?\s*:\s*([^;}]+)",
    re.IGNORECASE,
)
_VAR_REF_RE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,([^)]*))?\)")
_CUSTOM_PROP_RE = re.compile(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]+)")
_HEX_ANY_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")

# Threshold: WCAG relative luminance below which a surface needs light text (the standard
# ~0.18 crossover where black vs white text give roughly equal contrast). Below it = "dark".
_DARK_LUMINANCE_MAX = 0.18


def _srgb_to_linear(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """WCAG relative luminance of a #RGB / #RRGGBB colour."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.2126 * _srgb_to_linear(r) + 0.7152 * _srgb_to_linear(g) + 0.0722 * _srgb_to_linear(b)


def contrast_ratio(a: str, b: str) -> float:
    """WCAG contrast ratio between two colours (>=1)."""
    la, lb = relative_luminance(a), relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _var_map(text: str, tokens: dict | None) -> dict[str, str]:
    """Custom-property name -> value, from the brand tokens plus the page's own :root."""
    m: dict[str, str] = {}
    if tokens is not None:
        for name, val in color_values(tokens).items():
            m[f"--{name}"] = val
    for name, val in _CUSTOM_PROP_RE.findall(text):
        m[name] = val.strip()
    return m


def _resolve_color(value: str, var_map: dict[str, str], _depth: int = 0) -> str | None:
    """Resolve a CSS background value to a #hex, following var(--x[, fallback]) and named colours.

    Returns None if it cannot be resolved (an unresolved reference is treated as indeterminate,
    NOT as light -- callers fail closed)."""
    value = value.strip()
    if _depth > 12 or not value:
        return None
    var_m = _VAR_REF_RE.search(value)
    if var_m:
        ref = var_map.get(var_m.group(1))
        if ref is not None:
            resolved = _resolve_color(ref, var_map, _depth + 1)
            if resolved is not None:
                return resolved
        if var_m.group(2):  # var() fallback
            return _resolve_color(var_m.group(2), var_map, _depth + 1)
        return None
    hex_m = _HEX_ANY_RE.search(value)
    if hex_m:
        return hex_m.group(0)
    for name, hx in _NAMED_COLORS.items():
        if re.search(rf"\b{name}\b", value, re.IGNORECASE):
            return hx
    return None


def base_surface_is_dark(text: str, tokens: dict | None = None) -> bool | None:
    """Judge a page's BASE surface (body/html background) against the light-default law.

    Returns True if the base surface is dark (a brand-compliance defect -- dark must be a
    sparing accent, never the page ground), False if it is light, and None if the base
    background references something that cannot be resolved to a colour (indeterminate --
    callers should treat None as a failure, fail-closed, per R15). A page with no explicit
    base background renders on the browser default (white) and is therefore light -> False.
    """
    var_map = _var_map(text, tokens)
    m = _BASE_BG_RE.search(text)
    if not m:
        return False  # no explicit base surface -> default white -> light
    resolved = _resolve_color(m.group(1), var_map)
    if resolved is None:
        return None  # unresolved reference -> indeterminate (fail closed at the call site)
    return relative_luminance(resolved) < _DARK_LUMINANCE_MAX


# ---- live-site adoption: follow a page's linked stylesheets (+ @import) ----------------------
# A production page consumes the brand by LINKING site/brand/brand.css (which @imports the
# token projection). To judge such a page the way a browser resolves it, we concatenate the
# page's own <style> blocks with the CSS it links, following one level of @import. This is what
# makes "the live site consumes tokens end-to-end" testable rather than asserted.

_STYLESHEET_LINK_RE = re.compile(r"<link\b[^>]*\brel\s*=\s*[\"']stylesheet[\"'][^>]*>", re.IGNORECASE)
_HREF_RE = re.compile(r"href\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
_IMPORT_RE = re.compile(r"@import\s+(?:url\()?\s*[\"']([^\"')]+)[\"']")
_STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)


def page_style_css(html_text: str) -> str:
    """Concatenated contents of every ``<style>`` block in a page (the CSS surface itself)."""
    return "\n".join(_STYLE_BLOCK_RE.findall(html_text))


def linked_css_text(page_path: Path) -> str:
    """CSS a page links via ``<link rel=stylesheet>``, following one+ levels of ``@import``.

    Local (relative) hrefs only; remote stylesheets are skipped (the brand is self-hosted).
    Missing files are skipped rather than raising, so the caller sees whatever resolves.
    """
    page_path = Path(page_path)
    html = page_path.read_text()
    parts: list[str] = []
    seen: set[Path] = set()

    def _add(css_path: Path) -> None:
        css_path = css_path.resolve()
        if css_path in seen or not css_path.exists():
            return
        seen.add(css_path)
        css = css_path.read_text()
        for imp in _IMPORT_RE.findall(css):
            _add(css_path.parent / imp)
        parts.append(css)

    for link in _STYLESHEET_LINK_RE.findall(html):
        href_m = _HREF_RE.search(link)
        if not href_m:
            continue
        href = href_m.group(1)
        if href.startswith(("http://", "https://", "//", "data:")):
            continue
        _add(page_path.parent / href)
    return "\n".join(parts)


def resolved_page_css(page_path: Path) -> str:
    """A page's own ``<style>`` CSS plus the CSS it links -- the cascade a browser would see."""
    page_path = Path(page_path)
    return page_style_css(page_path.read_text()) + "\n" + linked_css_text(page_path)


def resolve_var(var_name: str, css_text: str, tokens: dict | None = None) -> str | None:
    """Resolve ``var(--name)`` to a ``#hex`` through the given CSS's custom properties + tokens.

    Returns None if the chain cannot be resolved to a colour (an unresolved reference)."""
    if not var_name.startswith("--"):
        var_name = f"--{var_name.lstrip('-')}"
    return _resolve_color(f"var({var_name})", _var_map(css_text, tokens))


def generate_css(tokens: dict) -> str:
    """Deterministic ``:root`` CSS custom-property projection of the token source.

    This is the ONLY sanctioned way a hex value reaches CSS; the emitted file is byte-checked
    against this function by the harness so it can never drift into an independent colour home.
    """
    lines = [
        "/* GENERATED from site/brand/tokens.json by tools/brand_compliance.generate_css.",
        " * Do not edit by hand. Colour values live in tokens.json only (BRAND_CONSTITUTION.md).",
        " * Regenerate: python3 -m tools.brand_compliance --write-css */",
        ":root {",
    ]
    for name, value in color_values(tokens).items():
        lines.append(f"  --{name}: {value};")

    # Font family (house stack) + weights + type scale + spacing, so surfaces reference tokens only.
    fam = tokens["font"]["family"]["house"]["$value"]
    fam_css = ", ".join(f'"{f}"' if " " in f else f for f in fam)
    lines.append(f"  --font-house: {fam_css};")
    for wname, wnode in tokens["font"]["weight"].items():
        if wname.startswith("$"):
            continue
        lines.append(f"  --font-weight-{wname}: {wnode['$value']};")
    for sname, snode in tokens["font"]["size"].items():
        if sname.startswith("$"):
            continue
        lines.append(f"  --font-size-{sname}: {snode['$value']};")
    for sp, spnode in tokens["spacing"].items():
        if sp.startswith("$"):
            continue
        lines.append(f"  --space-{sp}: {spnode['$value']};")
    lines.append(f"  --border-hairline: {tokens['border']['hairline']['$value']};")
    lines.append("}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    import sys

    toks = load_tokens()
    if "--write-css" in sys.argv:
        CSS_PATH.write_text(generate_css(toks))
        print(f"wrote {CSS_PATH.relative_to(REPO_ROOT)}")
    else:
        print(generate_css(toks))
