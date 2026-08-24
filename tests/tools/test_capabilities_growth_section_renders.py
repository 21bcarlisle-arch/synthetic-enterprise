"""The growth curve must reach a READER, not just a JSON file.

Director, 2026-08-24 console: *"say so on the site"*, and his test for the week is explicitly
reader-visible -- *"by Friday I want to open the site and see something a customer or a domain
expert would care about that isn't there today ... the growth path"*.

WHY THIS ASSERTS THE RENDERED VALUE AND NOT THE MARKUP. `site/data/book_growth.json` existing
proves nothing a reader can see; the campaign record it derives from had been written every run
for weeks and reached no page at all, which is the exact defect this section exists to end. R11:
"done" means the rendered value changed. These drive the page's own boot path through the repo's
render harness (`site/_live_harness.mjs`, the same one `live_pixel_verify` uses on the live doors)
and read what came out.

The LIVE fetch is deliberately not attempted here: publishing has been wedged since 09:07 and the
deployed page is stale, so a live assertion would be red for a reason that has nothing to do with
this section. That limitation is recorded in
WORKER_FINDING_THE_PRODUCER_OOMS_BECAUSE_THE_BOOK_GREW_AND_SETTLEMENT_SCALES_WITH_IT_2026-08-24.md
and this file is the local half of the same check.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "site"))

PAGE = ROOT / "site" / "capabilities" / "index.html"


def _render(growth: dict) -> dict:
    import live_pixel_verify as lpv

    door = ROOT / "site" / "data" / "capabilities_door.json"
    feeds = {
        "../data/capabilities_door.json": json.loads(door.read_text(encoding="utf-8")),
        "../data/book_growth.json": growth,
    }
    try:
        return lpv.run_harness(PAGE.read_text(encoding="utf-8"), feeds)
    except lpv.LiveCheckUnavailable as exc:  # node missing in this environment
        pytest.skip(f"render harness unavailable: {exc}")


def _text(rendered: dict, node_id: str) -> str:
    node = rendered.get(node_id) or {}
    return str(node.get("textContent") or "") + str(node.get("innerHTML") or "")


def _growth(*bindings, available=True):
    return {
        "available": available,
        "years": [
            {"year": 2016 + i, "quotes_issued": 10, "wins": 2, "accounts_after": 20 + i,
             "spend_gbp": 100.0, "clock": "settled", "homes_in_market": 400,
             "switching_multiplier": 1.0, "binding": b,
             "binding_label": "Our settlement engine" if b == "settlement_engine" else "Capital",
             "binding_is_our_artefact": b == "settlement_engine",
             "binding_meaning": "because reasons"}
            for i, b in enumerate(bindings)
        ],
        "engine_bound_statement": "STATEMENT-UNDER-TEST about the settlement engine",
        "settlement": {"customer_years_committed": 599.9, "customer_year_budget": 600.0},
        "totals": {"quotes": 10, "wins": 2, "spend_gbp": 100.0, "clock": "settled"},
        "notes": [],
    }


def test_the_reader_is_told_when_our_own_engine_stopped_the_book():
    """THE ASSERTION THAT CARRIES THE SECTION. The headline must reach the page in words."""
    out = _render(_growth("settlement_engine", "capital"))

    assert "STATEMENT-UNDER-TEST" in _text(out, "growth-headline")
    body = _text(out, "growth")
    assert "Our settlement engine" in body
    assert "2016" in body and "2017" in body


def test_MUTATION_the_section_is_not_hard_coded_to_say_engine_bound():
    """R15 null control. A section that always printed the warning would pass the test above on a
    page that ignored its data entirely -- and would libel the supplier in years it really did
    lose commercially. Feed it a run our engine never bound and the flag must be absent."""
    out = _render(_growth("capital", "capital"))
    body = _text(out, "growth")

    assert "Our settlement engine" not in body
    assert "Capital" in body


def test_an_unavailable_record_renders_ABSENT_and_never_an_empty_table():
    """FAIL-OPEN GUARD. A blank table reads as 'the supplier won nothing', which is a claim. The
    page must say the figures are absent instead."""
    out = _render({"available": False, "reason": "no campaign record on disk", "years": []})

    assert "absent rather than empty" in _text(out, "growth-note")
    assert "<table" not in _text(out, "growth")


def test_the_settled_clock_is_stated_on_the_page():
    """R14: no financial figure without its clock, on the surface a reader actually reads."""
    note = _text(_render(_growth("capital")), "growth-note")

    assert "settled clock" in note
    assert "599.9" in note and "600" in note


def test_the_section_survives_the_growth_feed_failing_entirely():
    """The capability columns above this section predate it and must not go down with it. A feed
    that never resolves must leave the rest of the door rendered."""
    import live_pixel_verify as lpv

    door = ROOT / "site" / "data" / "capabilities_door.json"
    feeds = {"../data/capabilities_door.json": json.loads(door.read_text(encoding="utf-8"))}
    try:
        out = lpv.run_harness(PAGE.read_text(encoding="utf-8"), feeds)
    except lpv.LiveCheckUnavailable as exc:
        pytest.skip(f"render harness unavailable: {exc}")

    # The pre-existing door content still rendered -- the growth section is additive, not load-bearing.
    assert _text(out, "world") or _text(out, "supplier"), (
        "a failing growth feed took the capability columns down with it"
    )
