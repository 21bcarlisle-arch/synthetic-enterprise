"""BRAND1 token adoption, enforced as a CLASS over the canonical door set (R10).

WHY THIS EXISTS
---------------
`tests/tools/test_brand_compliance.py` already enforces brand law beautifully --
but only over `_ADOPTED_LIVE_SURFACES`, a HAND-MAINTAINED allowlist. That makes
the failure mode silent in exactly the direction that matters: a door that has
never been adopted is not "failing", it is simply absent from the list, and a
door added to the public IA tomorrow is unguarded by default. Four of the eight
canonical doors were in that blind spot when this file was written.

R10 says an absurdity-class defect may not be closed with an instance fix: fixing
one door's palette closes one door. This control inverts the default instead. The
enforced set is DERIVED from `site/sitemap.xml` -- the same published list
`site/live_pixel_verify.py` uses -- so:

    every canonical door is either TOKEN-ADOPTED or explicitly REGISTERED as
    unadopted with a reason, and a door that is neither FAILS.

Adding a door to the public IA now forces a decision. That is the whole point;
the allowlist could never do it.

WHAT "ADOPTED" MEANS  (BRAND_CONSTITUTION.md §5, §10, §3a)
----------------------------------------------------------
  A1  links the shared stylesheet `../brand/brand.css`
  A2  no raw colour hex anywhere in its own CSS -- tokens are "the ONLY place a
      colour value ever lives" (§5)
  A3  does not redefine the brand semantic variables in its own `:root` -- a page
      that re-declares `--text`/`--blue` has taken the palette back off the token
      source even if it links the stylesheet (§10, "delete their own :root")
  A4  light base surface -- "a page whose base surface is dark FAILS brand
      compliance" (§3a, the director's own niggle, verbatim in the constitution)
  A5  type-only identity: the lowercase `poesys.` wordmark, not the legacy
      `⚡ Poesys` symbol lockup (§4 law 6)

THE REGISTER IS NOT AN ESCAPE HATCH
-----------------------------------
`UNADOPTED` entries need a non-empty reason, and a registered door that has since
been adopted fails too -- so the register cannot quietly rot into a permanent
exemption list that describes a world that no longer exists.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
REPO = SITE.parent
sys.path.insert(0, str(REPO))

from tools.brand_compliance import (  # noqa: E402
    base_surface_is_dark,
    find_raw_hex,
    load_tokens,
    page_style_css,
    resolved_page_css,
)

sys.path.insert(0, str(SITE))
from live_pixel_verify import canonical_doors  # noqa: E402

# ---------------------------------------------------------------------------
# The register of canonical doors NOT yet token-adopted.
#
# Each entry is a debt with a name, not a permission. Reasons are load-bearing:
# they say what has to happen for the entry to be deleted.
# ---------------------------------------------------------------------------
UNADOPTED: dict[str, str] = {
    "/customers/": (
        "2026-08-03 SITE1_expert_doors fork: 50 raw hex + own :root palette. Outside "
        "this fork's file_scope (concurrent sibling forks hold site/customers/**). "
        "Delete this entry when the door links ../brand/brand.css and drops its palette."
    ),
    "/now/": (
        "2026-08-03 SITE1_expert_doors fork: 76 raw hex, a full independent light+dark "
        "theme whose dark variant sets a DARK BASE SURFACE -- a §3a compliance defect in "
        "its own right, not merely unadopted. Outside this fork's file_scope."
    ),
    "/privacy/": (
        "2026-08-03 SITE1_expert_doors fork: 48 raw hex + 4 :root blocks incl. a dark "
        "base, and still ships the legacy '⚡ Poesys' symbol lockup against §4 law 6. "
        "Outside this fork's file_scope."
    ),
}


_BRAND_LINK_RE = re.compile(
    r"""<link\b[^>]*\bhref\s*=\s*["'][^"']*brand/brand\.css["'][^>]*>""", re.I
)


def links_brand_css(text: str) -> bool:
    """True only if the page carries a real <link> ELEMENT to the shared brand
    stylesheet.

    Deliberately not `"brand/brand.css" in text`. That was the first version, and
    an R15 mutation killed it: deleting the <link> tag left the door still passing,
    because every adopted door also carries a CSS COMMENT naming
    `../brand/brand.css` to explain where its palette went. The control was reading
    its own documentation and calling it compliance -- a fail-open, and the exact
    TAUTOLOGY shape R15 names (the evidence came from the same prose it checked).
    """
    return bool(_BRAND_LINK_RE.search(text))


def door_path(door: str) -> Path:
    """Map a sitemap door URL path to the file that serves it."""
    return SITE / door.strip("/") / "index.html" if door.strip("/") else SITE / "index.html"


def doors() -> list[str]:
    return canonical_doors()


def adopted_doors() -> list[str]:
    return [d for d in doors() if d not in UNADOPTED]


# ---------------------------------------------------------------------------
# The class property: the door set and the register partition each other.
# ---------------------------------------------------------------------------
def test_every_canonical_door_is_adopted_or_registered():
    """A door in the public IA that is neither adopted nor registered FAILS.

    This is the control the hand-maintained allowlist could not express: a new
    door is guarded on the day it is published, not on the day someone remembers
    to add it to a list.
    """
    unknown = [d for d in doors() if d not in UNADOPTED and not door_path(d).exists()]
    assert not unknown, f"sitemap advertises doors with no file: {unknown}"
    # Every door is in exactly one of the two buckets by construction; what can
    # actually break is a registered door that no longer exists.
    stale = [d for d in UNADOPTED if d not in doors()]
    assert not stale, (
        f"UNADOPTED registers doors that are not in the sitemap: {stale}. "
        "A register describing a world that no longer exists is worse than none."
    )


def test_register_entries_carry_a_real_reason():
    """An exemption without a reason is an escape hatch. These must state what
    unblocks them, so the register is a to-do list rather than a silence."""
    for door, reason in UNADOPTED.items():
        assert reason and len(reason.strip()) > 40, (
            f"{door} is registered unadopted with no substantive reason"
        )


def test_registered_doors_are_genuinely_unadopted():
    """R15 anti-rot: a door that HAS been adopted must be removed from the
    register. Without this the register would silently outlive the debt and
    permanently exempt a compliant door."""
    wrongly_registered = []
    for door in UNADOPTED:
        text = door_path(door).read_text(encoding="utf-8")
        if links_brand_css(text) and not find_raw_hex(page_style_css(text)):
            wrongly_registered.append(door)
    assert not wrongly_registered, (
        f"these doors are token-adopted but still registered as unadopted: "
        f"{wrongly_registered} -- delete their UNADOPTED entries"
    )


# ---------------------------------------------------------------------------
# A1-A5 over every adopted door.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("door", adopted_doors())
def test_adopted_door_links_the_shared_stylesheet(door):
    """A1."""
    text = door_path(door).read_text(encoding="utf-8")
    assert links_brand_css(text), f"{door} does not link the shared brand stylesheet"


@pytest.mark.parametrize("door", adopted_doors())
def test_adopted_door_has_no_raw_hex(door):
    """A2 -- THE guard the task names: a hardcoded hex reappearing in a
    token-adopted surface must fail. Scoped to the page's own CSS so HTML numeric
    entities in prose (`&#8322;` for the CO2 subscript) are not mistaken for
    colours."""
    text = door_path(door).read_text(encoding="utf-8")
    raw = find_raw_hex(page_style_css(text))
    assert not raw, (
        f"{door} carries raw colour hex in its own CSS: {sorted(set(raw))}. "
        "The token source is the only place a colour value may live "
        "(BRAND_CONSTITUTION §5)."
    )


@pytest.mark.parametrize("door", adopted_doors())
def test_adopted_door_does_not_redefine_the_brand_palette(door):
    """A3 -- linking brand.css while re-declaring `--text`/`--blue` in a local
    `:root` takes the palette straight back off the token source."""
    css = page_style_css(door_path(door).read_text(encoding="utf-8"))
    roots = re.findall(r":root[^{]*\{([^}]*)\}", css)
    redefined = set()
    for block in roots:
        for name in re.findall(r"(--[a-z0-9-]+)\s*:", block):
            if name in {"--bg", "--surface", "--surface2", "--border", "--text",
                        "--muted", "--green", "--red", "--amber", "--blue",
                        "--teal", "--purple"}:
                redefined.add(name)
    assert not redefined, (
        f"{door} re-declares brand semantic vars in its own :root: {sorted(redefined)}"
    )


@pytest.mark.parametrize("door", adopted_doors())
def test_adopted_door_has_a_light_base_surface(door):
    """A4 -- §3a, the director's verbatim niggle. Dark is punctuation, not paper."""
    path = door_path(door)
    dark = base_surface_is_dark(resolved_page_css(path), load_tokens())
    assert dark is not True, f"{door} resolves to a DARK base surface (§3a defect)"


@pytest.mark.parametrize("door", adopted_doors())
def test_adopted_door_uses_the_type_only_wordmark(door):
    """A5 -- §4 law 6: lowercase `poesys.` with the full stop, no symbol lockup."""
    text = door_path(door).read_text(encoding="utf-8")
    assert "&#9889;" not in text and "⚡" not in text, (
        f"{door} still ships the legacy symbol lockup; identity is type-only (§4 law 6)"
    )


# ---------------------------------------------------------------------------
# R15: the controls above must be able to FAIL. These prove it in-process, so the
# proof travels with the control instead of living in a commit message.
# ---------------------------------------------------------------------------
def test_mutation_raw_hex_control_fires():
    """Inject a raw hex into an adopted door's CSS -- the A2 control must see it."""
    door = adopted_doors()[0]
    clean = door_path(door).read_text(encoding="utf-8")
    assert not find_raw_hex(page_style_css(clean)), "precondition: door starts clean"
    mutated = clean.replace("<style>", "<style>\n.mutant { color: #ff0000; }", 1)
    assert find_raw_hex(page_style_css(mutated)), (
        "MUTATION SURVIVED: the raw-hex control cannot see a hardcoded colour"
    )


def test_mutation_stylesheet_link_control_is_not_satisfied_by_a_comment():
    """R15, and a real fail-open this control shipped with for one iteration.

    The first version asserted `"brand/brand.css" in text`. Deleting the <link>
    tag from an adopted door did NOT turn it red, because the door also carries a
    CSS comment naming the stylesheet to explain where its palette went -- the
    control was reading its own documentation. This pins the fix: prose mentioning
    the stylesheet is not adoption; a <link> element is.
    """
    # Synthetic, so the proof does not depend on which real door happens to carry
    # an explanatory comment today.
    with_link = (
        '<link rel="stylesheet" href="../brand/brand.css">\n'
        "<style>/* palette from ../brand/brand.css; :root deleted */</style>"
    )
    comment_only = "<style>/* palette from ../brand/brand.css; :root deleted */</style>"

    assert links_brand_css(with_link), "a real <link> element must count as adoption"
    assert "brand/brand.css" in comment_only, (
        "precondition: the comment alone satisfies a naive substring check -- "
        "this is exactly what made the first version fail open"
    )
    assert not links_brand_css(comment_only), (
        "MUTATION SURVIVED: a page with no <link> to brand.css still counts as "
        "adopted because a comment mentions the file"
    )

    # And the same on the real artefact: strip the tag, the door stops qualifying.
    door = adopted_doors()[0]
    real = door_path(door).read_text(encoding="utf-8")
    assert links_brand_css(real), "precondition: the door really does link it"
    assert not links_brand_css(_BRAND_LINK_RE.sub("", real)), (
        "MUTATION SURVIVED: removing the <link> tag left the door 'adopted'"
    )


def test_mutation_palette_redefinition_control_fires():
    """A page that links brand.css but re-declares --text must be caught."""
    css = ":root { --text: var(--ink-base); --blue: var(--blue-bright); }"
    roots = re.findall(r":root[^{]*\{([^}]*)\}", css)
    found = {n for b in roots for n in re.findall(r"(--[a-z0-9-]+)\s*:", b)}
    assert "--text" in found and "--blue" in found, (
        "MUTATION SURVIVED: the palette-redefinition control cannot see a local :root"
    )


def test_mutation_unregistered_door_is_caught():
    """R15 for the class property itself: a door published in the sitemap with no
    file and no register entry must fail. Proven against a synthetic door list so
    the real sitemap is never touched."""
    fake = "/a-door-that-does-not-exist/"
    unknown = [d for d in [fake] if d not in UNADOPTED and not door_path(d).exists()]
    assert unknown == [fake], (
        "MUTATION SURVIVED: an unregistered, non-existent door was not caught"
    )
