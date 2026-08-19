#!/usr/bin/env python3
"""R15 proof for the evidence page's reader-ready flag (director ruling, 2026-08-19).

The ruling: "Any live page showing wrong figures, internal vocabulary, or machine records a
reader can't use gets replaced with an honest placeholder until it's right."

A boolean that switches a page between "honest hole" and "machine dump" is exactly the kind of
flag that gets flipped during a tidy-up by someone who reads it as a feature toggle. So the
control is not "is the flag False" -- that would pin today's state and go red the day the work
is finished, which is the pinned-literal defect this project keeps finding in its own controls.
It is CONDITIONAL: whatever the flag says, the page a reader meets must match the claim the flag
makes about it.
"""
from __future__ import annotations

import html
import re

from tools import generate_evidence_data as gen

# Written as a pattern, not a list of today's ids: the point is that NO internal identifier
# reaches a reader, including ones minted after this test was written.
ATOM_ID = re.compile(r"\b(?:EP|SITE|OPS|KNIFE|H|D|W\d|G|B|C|AO|HX|CA|SP)\d+[a-z]?_[a-z0-9_]+")
REPO_PATH = re.compile(r"\b(?:docs|site|tools|background|tests)/[a-z0-9_./]+\.(?:json|yaml|jsonl|py)")


def _visible_text(markup: str) -> str:
    t = re.sub(r"<script.*?</script>", " ", markup, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def _page() -> str:
    payload = gen.build_payload(
        map_path=gen.MAP_PATH, mapping_path=gen.MAPPING_PATH,
        ledger_path=gen.LEDGER_PATH, suite_log_path=gen.SUITE_LOG_PATH,
    )
    return (gen.render_html(payload) if gen.EVIDENCE_READER_READY
            else gen.render_placeholder(payload))


def test_MUTATION_the_flag_cannot_be_flipped_without_the_page_becoming_readable():
    """THE control. If someone sets EVIDENCE_READER_READY = True as a tidy-up, the page they
    publish must actually be free of the vocabulary the ruling names. This fails on that flip
    and passes on a genuine rewrite, which is the only difference that matters."""
    text = _visible_text(_page())
    if not gen.EVIDENCE_READER_READY:
        return  # the placeholder's own obligations are asserted below
    ids = sorted(set(ATOM_ID.findall(text)))
    paths = sorted(set(REPO_PATH.findall(text)))
    assert not ids, (
        f"EVIDENCE_READER_READY is True but the page still shows raw atom ids to a reader: "
        f"{ids[:6]}. The flag claims this page is written for a reader; it is not."
    )
    assert not paths, (
        f"EVIDENCE_READER_READY is True but the page still cites repository paths: {paths[:4]}. "
        "A reader cannot open those."
    )


def test_the_placeholder_shows_no_internal_identifier_at_all():
    """The state today. Measured on the RENDERED TEXT a reader sees, not on the template --
    the old page's 19 atom ids were all generated, so a template check would have missed
    every one of them."""
    assert not gen.EVIDENCE_READER_READY, (
        "the flag is True -- if the reader-facing page has shipped, delete this test and keep "
        "the mutation above, which is the one that guards the flip"
    )
    text = _visible_text(_page())
    assert not ATOM_ID.findall(text), ATOM_ID.findall(text)[:6]


def test_the_placeholder_says_what_it_will_show_and_roughly_when():
    """The ruling's actual requirement: not a blank, but a hole that tells you what belongs in
    it. A placeholder without these is the 'unintelligible content' problem with fewer words."""
    text = _visible_text(_page())
    assert "This page is being built" in text, "the shared reader-facing marker is missing"
    lowered = text.lower()
    assert "what this page will show" in lowered
    assert "roughly when" in lowered
    assert len(text) > 800, "the placeholder is too thin to tell a reader anything useful"


def test_MUTATION_the_DATA_is_still_generated_while_the_rendering_is_held_back():
    """The half that stops this being a retreat. If the payload were switched off with the
    page, the rebuilt page would come back six months stale -- so the derivation must keep
    running and keep being checked every publish."""
    payload = gen.build_payload(
        map_path=gen.MAP_PATH, mapping_path=gen.MAPPING_PATH,
        ledger_path=gen.LEDGER_PATH, suite_log_path=gen.SUITE_LOG_PATH,
    )
    assert payload.get("nodes"), "the evidence payload is empty -- the derivation stopped"
    assert payload.get("totals"), "the evidence totals are gone"


def test_the_placeholder_still_carries_the_site_nav():
    """A hole that drops you out of the site is a worse hole. The nav renders from the IA
    register, so the page keeps every door the rest of the site has."""
    markup = _page()
    assert "IA-NAV:START" in markup or 'class="nav-link"' in markup
    # DERIVED, and I wrote this wrong first: it named "The World", "Knowledge", "Proof" as
    # literals, and the director's fold to five tabs took two of those three off the nav within
    # the hour. That is the same second-definition-of-the-nav defect I had just repaired in four
    # door tests, reintroduced by me in a new file. There is one definition of the nav.
    import sys as _sys
    _sys.path.insert(0, str(gen.SITE))
    from ia_register import CANONICAL_NAV
    for item in CANONICAL_NAV:
        assert f">{item.label}</a>" in markup, f"the placeholder lost the {item.label!r} door"
