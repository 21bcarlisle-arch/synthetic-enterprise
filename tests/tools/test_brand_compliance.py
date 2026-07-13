"""Brand-compliance harness (BRAND1_identity_system / BRAND_CONSTITUTION.md §5.4).

Enforces the two testable properties the constitution requires:
  (a) no raw colour value appears on a consuming surface outside the token source;
  (b) soft-colour-as-text is detectable/blocked (law 3).

Plus the structural guarantees that make (a) meaningful: the token JSON is the sole colour
home, the CSS mirror is a provable projection of it (never an independent home), and the
ratified §7 exemplar is preserved verbatim.
"""
import re
from pathlib import Path

import pytest

from tools.brand_compliance import (
    BRAND_DIR,
    CSS_PATH,
    TOKENS_PATH,
    color_values,
    find_raw_hex,
    find_soft_as_text,
    generate_css,
    load_tokens,
    soft_color_hexes,
    soft_color_names,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
EXEMPLAR_PATH = BRAND_DIR / "exemplar.html"
PROOF_PATH = BRAND_DIR / "proof.html"
CONSTITUTION_PATH = REPO_ROOT / "docs" / "design" / "BRAND_CONSTITUTION.md"

# Files under site/brand/ that are NOT plain consuming surfaces, with the reason each is exempt
# from the "no raw hex" rule:
#   tokens.json  -- the token source itself (the one sanctioned home of colour values);
#   tokens.css   -- a GENERATED, byte-pinned projection of tokens.json (see test below), not an
#                   independently authored colour home;
#   exemplar.html-- the ratified §7 reference, preserved VERBATIM and self-contained by mandate.
_NON_CONSUMING = {"tokens.json", "tokens.css", "exemplar.html"}


def _consuming_surfaces():
    return [
        p
        for p in sorted(BRAND_DIR.glob("*"))
        if p.suffix in {".html", ".css"} and p.name not in _NON_CONSUMING
    ]


# ---- token source: sole colour home ---------------------------------------------------------

def test_token_source_exists_and_parses():
    tokens = load_tokens()
    assert tokens["$schema"], "tokens.json must declare the W3C design-tokens schema"


def test_brag_palette_is_complete():
    """12 status values (blue/red/amber/green x bright/soft) + black + white + 3 greys."""
    values = color_values(load_tokens())
    for role in ("blue", "red", "amber", "green"):
        assert f"{role}-bright" in values, f"missing {role}-bright"
        assert f"{role}-soft" in values, f"missing {role}-soft"
    for base in ("black", "white", "grey-40", "grey-15", "grey-05"):
        assert base in values, f"missing {base}"
    assert len([k for k in values if k.endswith(("-bright", "-soft"))]) == 8
    # Every colour value is a well-formed hex literal.
    for name, hexval in values.items():
        assert re.fullmatch(r"#[0-9A-Fa-f]{6}", hexval), f"{name} = {hexval!r} not a 6-digit hex"


def test_palette_values_match_ratified_constitution():
    """Guards against silent drift of a director-ratified brand value away from §3/§7."""
    values = color_values(load_tokens())
    ratified = {
        "blue-bright": "#0047FF", "blue-soft": "#DCE7FF",
        "red-bright": "#E11900", "red-soft": "#FFDDD6",
        "amber-bright": "#F5A600", "amber-soft": "#FFF0C9",
        "green-bright": "#00873C", "green-soft": "#D6F2E0",
        "black": "#0A0A0A", "white": "#FFFFFF",
    }
    for name, expected in ratified.items():
        assert values[name] == expected, f"{name} drifted: {values[name]} != {expected}"


# ---- (a) no raw hex on a consuming surface --------------------------------------------------

def test_no_raw_hex_on_consuming_surfaces():
    surfaces = _consuming_surfaces()
    assert surfaces, "expected at least one token-consuming surface under site/brand/"
    for surface in surfaces:
        raw = find_raw_hex(surface.read_text())
        assert raw == [], f"{surface.name} hardcodes colour value(s) {raw}; consume tokens instead"


def test_css_mirror_is_a_pinned_projection_of_the_source():
    """tokens.css must be exactly generate_css(tokens.json) -- so it is never an independent
    colour home, and every hex it carries is provably drawn from the source."""
    assert CSS_PATH.read_text() == generate_css(load_tokens()), (
        "site/brand/tokens.css is stale/hand-edited; regenerate with "
        "`python3 -m tools.brand_compliance --write-css`"
    )
    source_hexes = set(color_values(load_tokens()).values())
    for hexval in find_raw_hex(CSS_PATH.read_text()):
        assert hexval in source_hexes, f"tokens.css introduced a novel colour {hexval}"


# ---- (b) soft-colour-as-text is detectable / blocked (law 3) --------------------------------

def test_soft_as_text_detector_flags_var_and_hex():
    tokens = load_tokens()
    names, hexes = soft_color_names(tokens), soft_color_hexes(tokens)
    assert find_soft_as_text("a{color:var(--blue-soft);}", names, hexes)
    assert find_soft_as_text("a{border-color:var(--amber-soft);}", names, hexes)
    assert find_soft_as_text("a{color:#DCE7FF;}", names, hexes)
    assert find_soft_as_text("hr{border:1px solid var(--red-soft);}", names, hexes)


def test_soft_as_fill_behind_black_text_is_allowed():
    tokens = load_tokens()
    names, hexes = soft_color_names(tokens), soft_color_hexes(tokens)
    ok = ".chip{background:var(--green-soft);color:var(--black);}"
    assert find_soft_as_text(ok, names, hexes) == []


def test_consuming_surfaces_have_no_soft_as_text():
    tokens = load_tokens()
    names, hexes = soft_color_names(tokens), soft_color_hexes(tokens)
    for surface in _consuming_surfaces():
        hits = find_soft_as_text(surface.read_text(), names, hexes)
        assert hits == [], f"{surface.name} uses a soft colour as text/thin-line: {hits}"


# ---- exemplar preserved verbatim ------------------------------------------------------------

def test_exemplar_preserved_verbatim_from_constitution():
    """site/brand/exemplar.html must equal the §7 ```html fence in BRAND_CONSTITUTION.md."""
    m = re.search(r"```html\n(.*?)\n```", CONSTITUTION_PATH.read_text(), re.S)
    assert m, "no ```html fence found in BRAND_CONSTITUTION.md"
    ratified = m.group(1)
    on_disk = EXEMPLAR_PATH.read_text()
    assert on_disk.rstrip("\n") == ratified.rstrip("\n"), (
        "exemplar.html has diverged from the ratified §7 reference"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
