#!/usr/bin/env python3
"""A Knowledge page names the map atoms that build its mechanism, and goes red when one moves.

THE DEFECT, measured 2026-10-03 before this landed: of the 23 topics in
site/data/knowledge_wholesale.json, 21 named no atom anywhere in their record, and the two that
did (`W2_25_...`, `W2_26_...`) named them in body prose nothing reads. That is the director's P8
(2026-08-28) in his words: "knowledge pages describe mechanisms with no link to the atoms
implementing them, so page and code can disagree indefinitely and nothing notices." It is the
first of H45's three open joints (docs/design/simplifications/H45_the_queue_is_chained_to_the_map.yaml).

THE RULE. Every topic carries `atoms`, in one of two forms, mirroring the staging chain's
absent / UNMINTED split in background/staging_rooms.py:

    ["W3_1_price_cap_binding", ...]   the atoms that build it -- each must be a map cell
    "none -- <reason>"                someone looked and no atom builds it, and why

An ABSENT field means nobody looked, and is refused here and shown as that gap on the index.

"FAILS WHEN THEY MOVE" is the resolver: a named id that is in neither the live map nor the
closed store reds this file, so renaming or deleting an atom cannot leave a page pointing at
nothing. A CLOSED atom resolves -- a mechanism built and finished is still what builds the page.

NOT graded: whether the named atoms are the RIGHT ones. That is a judgement the writer makes
and the reader can now see on the index card; a control on it would be a list keyed to today.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
PROJECT = SITE.parent
INDEX = HERE / "index.html"
FEED = SITE / "data" / "knowledge_wholesale.json"
LIVE_HARNESS = SITE / "_live_harness.mjs"
FEED_URL = "../data/knowledge_wholesale.json"

sys.path.insert(0, str(PROJECT))

from tools import maturity_map_store  # noqa: E402

NONE_PREFIX = "none -- "


@pytest.fixture(scope="module")
def feed() -> dict:
    return json.loads(FEED.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def map_ids() -> set[str]:
    live = {a["id"] for a in maturity_map_store.load_live_atoms()}
    closed = {a["id"] for a in maturity_map_store.load_closed_atoms()}
    return live | closed


def malformed(topic: dict) -> str | None:
    """Why this topic's `atoms` is not one of the two forms, or None if it is."""
    if "atoms" not in topic:
        return "no `atoms` field: nobody has recorded which atom builds this"
    a = topic["atoms"]
    if isinstance(a, list):
        if not a:
            return "an empty list says nothing; write `none -- <reason>`"
        if not all(isinstance(x, str) and x for x in a):
            return f"non-string entries in {a!r}"
        return None
    if isinstance(a, str) and a.startswith(NONE_PREFIX) and a[len(NONE_PREFIX):].strip():
        return None
    return f"{a!r} is neither a list of atom ids nor `none -- <reason>`"


def unresolved(feed: dict, ids: set[str]) -> dict[str, list[str]]:
    """Named atoms that are on neither the live map nor the closed store, by topic."""
    out = {}
    for t in feed["topics"]:
        a = t.get("atoms")
        if isinstance(a, list):
            missing = [x for x in a if x not in ids]
            if missing:
                out[t["id"]] = missing
    return out


def expected_line(topic: dict) -> str:
    """The Python statement of what the card shows; the JavaScript must agree with it."""
    a = topic.get("atoms")
    if isinstance(a, list) and a:
        return "Built by: " + " · ".join(a)
    if isinstance(a, str) and a.startswith(NONE_PREFIX) and len(a) > len(NONE_PREFIX):
        return "Built by no atom: " + a[len(NONE_PREFIX):]
    return "No atom named: nobody has recorded which atom builds this."


def _render(feeds: dict) -> dict:
    proc = subprocess.run(
        ["node", str(LIVE_HARNESS), str(INDEX)],
        input=json.dumps(feeds), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr[:600]
    return json.loads(proc.stdout)


# ---------------------------------------------------------------------------
# The record
# ---------------------------------------------------------------------------
def test_every_topic_says_which_atoms_build_it(feed):
    bad = {t["id"]: why for t in feed["topics"] if (why := malformed(t))}
    assert not bad, f"topics whose `atoms` is missing or malformed: {bad}"


def test_every_named_atom_is_a_map_cell(feed, map_ids):
    missing = unresolved(feed, map_ids)
    assert not missing, (
        f"Knowledge pages name atoms the map no longer has: {missing}. An atom was renamed or "
        "removed; repoint the page at the cell that builds it now, or write `none -- <reason>`."
    )


def test_both_forms_are_taken(feed):
    """The rare branch can be taken: a rule that forced every page onto a list, or let every
    page say `none`, would pass both tests above."""
    forms = {type(t.get("atoms")).__name__ for t in feed["topics"]}
    assert forms == {"list", "str"}, f"forms present: {forms}"


def test_MUTATION_a_renamed_atom_is_caught(feed, map_ids):
    doctored = json.loads(json.dumps(feed))
    t = next(t for t in doctored["topics"] if isinstance(t.get("atoms"), list))
    t["atoms"] = [t["atoms"][0] + "_renamed"] + t["atoms"][1:]
    assert unresolved(doctored, map_ids) == {t["id"]: [t["atoms"][0]]}


def test_MUTATION_an_absent_or_bare_none_is_caught():
    assert malformed({"id": "x"})
    assert malformed({"id": "x", "atoms": []})
    assert malformed({"id": "x", "atoms": "none"})
    assert malformed({"id": "x", "atoms": "none -- "})
    assert malformed({"id": "x", "atoms": "none -- a reason"}) is None


# ---------------------------------------------------------------------------
# What the reader is shown
# ---------------------------------------------------------------------------
def test_every_card_has_a_slot_for_its_atoms(feed):
    markup = INDEX.read_text(encoding="utf-8")
    for t in feed["topics"]:
        assert f'<div class="card-a" id="atoms-{t["id"]}"></div>' in markup, (
            f"{t['id']} has no empty atoms slot on its index card"
        )


def test_the_rendered_index_shows_each_topics_atoms(feed):
    rendered = _render({FEED_URL: feed})
    for t in feed["topics"]:
        el = rendered.get(f"atoms-{t['id']}")
        assert el and el["textContent"] == expected_line(t), (
            f"{t['id']}: page shows {el and el['textContent']!r}, record says "
            f"{expected_line(t)!r}"
        )


def test_MUTATION_a_topic_with_no_field_is_shown_as_the_gap(feed):
    doctored = json.loads(json.dumps(feed))
    for t in doctored["topics"]:
        t.pop("atoms", None)
    rendered = _render({FEED_URL: doctored})
    for t in doctored["topics"]:
        el = rendered.get(f"atoms-{t['id']}")
        assert el and el["textContent"].startswith("No atom named"), (
            f"{t['id']} names no atom and the page shows {el and el['textContent']!r}"
        )


def test_MUTATION_FAIL_CLOSED_an_unreachable_record_names_no_atom(feed):
    rendered = _render({})
    for t in feed["topics"]:
        el = rendered.get(f"atoms-{t['id']}")
        assert not (el and el["textContent"].strip()), (
            f"{t['id']} shows {el['textContent']!r} with the record unreachable"
        )
