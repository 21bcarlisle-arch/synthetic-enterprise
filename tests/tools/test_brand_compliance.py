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
    base_surface_is_dark,
    color_values,
    contrast_ratio,
    find_raw_hex,
    find_soft_as_text,
    generate_css,
    linked_css_text,
    load_tokens,
    page_style_css,
    resolve_var,
    resolved_page_css,
    soft_color_hexes,
    soft_color_names,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
EXEMPLAR_PATH = BRAND_DIR / "exemplar.html"
PROOF_PATH = BRAND_DIR / "proof.html"
BRAND_CSS_PATH = BRAND_DIR / "brand.css"
CONSTITUTION_PATH = REPO_ROOT / "docs" / "design" / "BRAND_CONSTITUTION.md"

# Live production pages that have ADOPTED the brand: they link site/brand/brand.css, carry no
# raw colour in their <style>, and render the wordmark. This list is the enforced adoption
# frontier -- it GROWS as the rollout proceeds (charts/PDFs/remaining pages are declared
# follow-up atoms; a page joins here only once its CSS surface is genuinely token-only).
_ADOPTED_LIVE_SURFACES = [
    REPO_ROOT / "site" / "index.html",          # the front door (BRAND_CONSTITUTION.md DoD)
    REPO_ROOT / "site" / "method" / "index.html",
    REPO_ROOT / "site" / "project" / "index.html",
    REPO_ROOT / "site" / "simplified" / "index.html",
    REPO_ROOT / "site" / "world" / "index.html",   # (2026-07-20) adopted the brand
    # (2026-07-20 v4 site rebuild) platform/ and sim/ were retired -- removed from the adoption
    # frontier. The remaining un-adopted kept doors (company/world/proof) join here as the BRAND1
    # L2->L3 rollout reaches them (each once its CSS is genuinely token-only + wordmark).
]

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
        # amber-bright re-tuned #F5A600 -> #AA6700 for WCAG AA on the light ground
        # (BRAND_LIGHT_MODE_DEFAULT.md, director-ratified 2026-07-13).
        "amber-bright": "#AA6700", "amber-soft": "#FFF0C9",
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


# ---- light-default ground: semantic surface/ink tokens + WCAG AA on white (§3a) -------------

def test_semantic_surface_and_ink_tokens_codify_light_default():
    """The light-default constitution (§3a) must be codified in tokens, not just prose:
    a light base + sunken surface, dark ink, and dark as a NAMED accent surface."""
    values = color_values(load_tokens())
    assert values["surface-base"] == "#FFFFFF", "base ground must be light (white)"
    assert values["surface-sunken"] == "#F4F4F4", "sunken backdrop must be light (grey-05)"
    assert values["surface-accent-dark"] == "#0A0A0A", "dark must be a NAMED accent surface"
    assert values["ink-base"] == "#0A0A0A", "default ink is structural black on the light ground"
    assert values["ink-on-accent"] == "#FFFFFF", "ink on the dark accent is white"
    # The default ground pairs light surface with dark ink (black-on-white), not the reverse.
    assert contrast_ratio(values["surface-base"], values["ink-base"]) >= 4.5


def test_brag_brights_meet_wcag_aa_on_white():
    """Every bright status must read as information on the white ground -- WCAG AA (>=4.5:1).
    Guards the re-tune: the old amber #F5A600 was 2.03:1 and would fail this."""
    values = color_values(load_tokens())
    white = values["white"]
    for role in ("blue", "red", "amber", "green"):
        ratio = contrast_ratio(values[f"{role}-bright"], white)
        assert ratio >= 4.5, f"{role}-bright {values[f'{role}-bright']} = {ratio:.2f}:1 on white, below AA"


# ---- dark-as-base FAILS; light + sparing dark accent PASSES (§3a, mutation-tested) ----------

def test_base_surface_is_dark_mutation_check():
    """R15 mutation check: the control must FIRE on its named defect (a dark base surface) and
    PASS the intended-good case (a light page carrying a sparing dark accent panel)."""
    tokens = load_tokens()
    # MUTANT 1: dark base via the named accent token used (wrongly) as the page ground -> FAIL.
    dark_token = "<style>body{background:var(--surface-accent-dark);color:var(--ink-on-accent);}</style>"
    assert base_surface_is_dark(dark_token, tokens) is True
    # MUTANT 2: dark base via a raw dark hex (the GitHub-dark #0d1117 the director objected to) -> FAIL.
    dark_hex = "<style>body{background:#0d1117;color:#e6edf3;}</style>"
    assert base_surface_is_dark(dark_hex, tokens) is True
    # GOOD 1: light base with a SPARING dark accent on a child panel -> PASS (accent != base).
    light_accent = (
        "<style>body{background:var(--surface-base);color:var(--ink-base);}"
        ".hero{background:var(--surface-accent-dark);color:var(--ink-on-accent);}</style>"
    )
    assert base_surface_is_dark(light_accent, tokens) is False
    # GOOD 2: plain white page -> PASS.
    assert base_surface_is_dark("<style>body{background:#FFFFFF;color:#0A0A0A;}</style>", tokens) is False
    # GOOD 3: light base declared via the page's own :root custom property -> resolved + PASS.
    page_root = "<style>:root{--bg:#f9f9f7;}body{background:var(--bg);}</style>"
    assert base_surface_is_dark(page_root, tokens) is False
    # An unresolved base reference is indeterminate (None), which callers treat as a failure.
    assert base_surface_is_dark("<style>body{background:var(--nope);}</style>", tokens) is None


def test_consuming_surfaces_have_a_light_base():
    """Every token-consuming brand surface must have a LIGHT base (dark is a sparing accent
    only, never the page ground). Fail-closed: None (unresolvable) also fails."""
    tokens = load_tokens()
    for surface in _consuming_surfaces():
        verdict = base_surface_is_dark(surface.read_text(), tokens)
        assert verdict is False, (
            f"{surface.name}: base surface is dark or unresolvable ({verdict!r}); "
            "dark is an accent, not the page ground (BRAND_CONSTITUTION.md §3a)"
        )


# ---- shared brand stylesheet: the single linkable brand surface (no raw hex) ----------------

def test_shared_brand_css_exists_and_imports_the_token_projection():
    css = BRAND_CSS_PATH.read_text()
    assert '@import "tokens.css"' in css, "brand.css must consume the token projection, not re-home colour"


def test_shared_brand_css_has_no_raw_hex():
    """brand.css maps the site's semantic vars + components onto tokens ONLY -- a raw hex here
    would make it a second, independent colour home (the exact defect the token source prevents)."""
    raw = find_raw_hex(BRAND_CSS_PATH.read_text())
    assert raw == [], f"brand.css hardcodes colour value(s) {raw}; reference tokens via var()"


def test_shared_brand_css_has_no_soft_as_text():
    tokens = load_tokens()
    hits = find_soft_as_text(BRAND_CSS_PATH.read_text(), soft_color_names(tokens), soft_color_hexes(tokens))
    assert hits == [], f"brand.css uses a soft colour as text/thin-line: {hits}"


# ---- live-site adoption: the production pages consume tokens end-to-end (L3 DoD) -------------

def test_adopted_pages_link_the_shared_brand_stylesheet():
    for page in _ADOPTED_LIVE_SURFACES:
        assert page.exists(), f"{page} missing"
        assert "brand/brand.css" in page.read_text(), f"{page.name} does not link the brand stylesheet"


def test_adopted_pages_css_surface_is_token_only():
    """Each adopted page's <style> must carry NO raw colour -- it consumes the linked tokens.
    (Chart.js palettes in <script> are a declared follow-up atom and are out of this scope.)"""
    for page in _ADOPTED_LIVE_SURFACES:
        raw = find_raw_hex(page_style_css(page.read_text()))
        assert raw == [], f"{page.name} <style> hardcodes colour(s) {raw}; consume brand tokens"


def test_adopted_pages_have_no_soft_as_text():
    tokens = load_tokens()
    names, hexes = soft_color_names(tokens), soft_color_hexes(tokens)
    for page in _ADOPTED_LIVE_SURFACES:
        hits = find_soft_as_text(page_style_css(page.read_text()), names, hexes)
        assert hits == [], f"{page.name} uses a soft colour as text/thin-line: {hits}"


def test_adopted_pages_have_a_light_base_through_the_linked_cascade():
    """Resolve each page the way a browser would (its <style> + the CSS it links, following
    @import) and assert the BASE surface is light -- dark is a sparing accent, never the ground
    (§3a). Fail-closed: None (unresolvable) fails too."""
    tokens = load_tokens()
    for page in _ADOPTED_LIVE_SURFACES:
        verdict = base_surface_is_dark(resolved_page_css(page), tokens)
        assert verdict is False, (
            f"{page.name}: base surface is dark or unresolvable ({verdict!r}) through its linked CSS"
        )


def test_adopted_pages_carry_the_wordmark_not_the_legacy_symbol():
    """Type-only identity (law 6): the nav shows lowercase `poesys.` with the full stop, and the
    legacy zap-symbol logo (&#9889;) is gone."""
    for page in _ADOPTED_LIVE_SURFACES:
        html = page.read_text()
        assert "nav-logo wordmark" in html, f"{page.name} missing the wordmark class"
        assert "poesys." in html, f"{page.name} missing the poesys. wordmark"
        assert "&#9889;" not in html, f"{page.name} still renders the legacy zap symbol"


def test_adopted_pages_resolve_brag_status_colours_end_to_end():
    """R11 value-level: the live cascade must resolve the site's semantic colours to the
    ratified BRAG tokens -- ground light/ink black, and the four status colours exact. (The
    live-pixel-with-director's-eyes check is the declared residual; this proves the value chain.)"""
    tokens = load_tokens()
    expected = {
        "--bg": "#F4F4F4", "--text": "#0A0A0A",
        "--green": "#00873C", "--red": "#E11900",
        "--amber": "#AA6700", "--blue": "#0047FF",
    }
    for page in _ADOPTED_LIVE_SURFACES:
        css = resolved_page_css(page)
        for var, hexval in expected.items():
            got = resolve_var(var, css, tokens)
            assert got is not None and got.upper() == hexval, (
                f"{page.name}: {var} resolved to {got!r}, expected {hexval} (BRAG token)"
            )


# ---- R15 mutation checks: the new live-site controls must FIRE on their named defects --------

def test_css_token_consumption_control_mutation_check():
    """The 'CSS surface is token-only' control must PASS a token-only style and FIRE on a raw
    hex reintroduced into a page's <style>."""
    good = "<style>body{background:var(--bg);color:var(--text);}</style>"
    assert find_raw_hex(page_style_css(good)) == []          # PASS: token-only
    mutant = "<style>body{background:#0d1117;color:var(--text);}</style>"
    assert find_raw_hex(page_style_css(mutant)) == ["#0d1117"]  # FIRE: raw hex reintroduced


def test_linked_cascade_light_base_control_mutation_check(tmp_path):
    """The linked-cascade light-base control must PASS a page linking a stylesheet that maps the
    ground to a light token, and FIRE when a linked stylesheet maps the ground to the dark
    accent token (dark-as-base -- the §3a defect), proving the resolver follows the <link>."""
    tokens = load_tokens()
    (tmp_path / "light.css").write_text(":root{--bg:var(--surface-sunken);}")
    (tmp_path / "dark.css").write_text(":root{--bg:var(--surface-accent-dark);}")
    body = "<style>body{background:var(--bg);}</style>"
    page = tmp_path / "page.html"

    page.write_text(body + '<link rel="stylesheet" href="light.css">')
    assert base_surface_is_dark(resolved_page_css(page), tokens) is False   # GOOD

    page.write_text(body + '<link rel="stylesheet" href="dark.css">')
    assert base_surface_is_dark(resolved_page_css(page), tokens) is True    # MUTANT fires


def test_linked_css_follows_import_chain():
    """brand.css @imports tokens.css; a page linking brand.css must therefore see the token
    custom properties (else the whole adoption cascade is hollow)."""
    front_door = REPO_ROOT / "site" / "index.html"
    linked = linked_css_text(front_door)
    assert "--surface-sunken" in linked, "token projection not reached through brand.css @import"
    assert "--bg:" in linked, "brand.css semantic mapping not reached via the <link>"


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
