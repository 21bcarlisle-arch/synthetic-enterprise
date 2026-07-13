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
