#!/usr/bin/env python3
"""The Capabilities door and the three brief controls that land with it (SITE7).

Per brief §9.3 controls arrive WITH the surface they govern, never as a block up front:
landing all five §7 controls before the migration would red the whole site mid-transition.
So this file carries the three that apply to this tab, scoped to this tab:

  §7 #2  a published page with no heading structure fails
  §7 #3  a link label used more than twice on a page fails
  §6.2   internal vocabulary on a public page fails, against a named list

and the property that makes the page worth publishing at all:

  the STATUS of every capability is DERIVED from the recorded work, never written here.

WHY THE LAST ONE IS THE IMPORTANT TEST. A capabilities page is the easiest page on any
site to lie on, because nothing contradicts it. This one cannot outrun its record: each
entry cites the work items it rests on, the status is computed from those items' levels by
the same rule the architecture diagram uses, and `test_MUTATION_a_dropped_level_downgrades_the_page`
proves the page moves when the record moves. A page that renders "Live" from a hand-typed
string would pass every other test in this file.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
PROJECT = SITE.parent
INDEX = HERE / "index.html"
FEED = SITE / "data" / "capabilities_door.json"

sys.path.insert(0, str(SITE))
sys.path.insert(0, str(PROJECT))

from tools import generate_capabilities_door as gen  # noqa: E402


@pytest.fixture(scope="module")
def html() -> str:
    return INDEX.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def feed() -> dict:
    assert FEED.is_file(), "the door's feed has never been generated"
    return json.loads(FEED.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# §7 #2 — heading structure
# ---------------------------------------------------------------------------
def _headings(text: str) -> list[tuple[str, str]]:
    return [(m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip())
            for m in re.finditer(r"<(h[1-4])[^>]*>(.*?)</\1>", text, re.S | re.I)]


def test_the_page_has_heading_structure(html):
    """Eight of sixteen areas carry zero h1-h4 today, including two current nav
    destinations. A new tab does not get to join them."""
    hs = _headings(html)
    levels = {h for h, _ in hs}
    assert "h1" in levels, "no <h1> — the page does not say what it is"
    assert "h2" in levels, "no <h2> — a 900-line page with no sections is not skimmable"
    assert len([h for h, _ in hs if h == "h1"]) == 1, f"exactly one h1 expected, got {hs}"


def test_every_heading_has_text(html):
    for tag, text in _headings(html):
        assert text, f"empty {tag} — a heading with no words is markup, not structure"


def test_MUTATION_a_page_with_no_headings_fires():
    stripped = re.sub(r"<h1[^>]*>.*?</h1>", "", INDEX.read_text(encoding="utf-8"), flags=re.S | re.I)
    levels = {h for h, _ in _headings(stripped)}
    assert "h1" not in levels  # the control's own subject, absent


# ---------------------------------------------------------------------------
# §7 #3 — link labels
# ---------------------------------------------------------------------------
def _link_labels(text: str) -> list[str]:
    body = re.sub(r"<nav\b.*?</nav>", "", text, flags=re.S | re.I)  # nav is the register's
    return [re.sub(r"<[^>]+>", "", m.group(1)).strip().lower()
            for m in re.finditer(r"<a\b[^>]*>(.*?)</a>", body, re.S | re.I)]


def test_no_link_label_is_used_more_than_twice(html):
    """The homepage carries the same 'Evidence behind this stage' label six times, word
    for word. That is the defect this control generalises."""
    labels = _link_labels(html)
    counts = {lab: labels.count(lab) for lab in set(labels) if lab}
    over = {lab: n for lab, n in counts.items() if n > 2}
    assert not over, f"link label(s) used more than twice: {over}"


def test_MUTATION_a_thrice_repeated_label_fires():
    labels = ["evidence", "evidence", "evidence"]
    counts = {lab: labels.count(lab) for lab in set(labels)}
    assert {lab: n for lab, n in counts.items() if n > 2}


# ---------------------------------------------------------------------------
# §6.2 — no internal vocabulary
# ---------------------------------------------------------------------------
# The named list. Every term here is one this project uses constantly in its own records
# and which means nothing to an outsider. Matched on word boundaries against the page's
# VISIBLE TEXT ONLY -- markup, class names and the nav are excluded, because `class="item"`
# is not vocabulary a reader meets.
INTERNAL_TERMS = (
    "atom", "atoms", "loop_stage", "level_current", "level_target", "maturity map",
    "lane", "lanes", "epoch", "R11", "R12", "R15", "R16", "one-way door",
    "DISCOVER", "FRAME", "HARDEN", "expert hour", "coupled triad", "dial",
    "file_scope", "provenance record", "gate_authorizations", "self-certif",
)


def visible_text(text: str) -> str:
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S | re.I)
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"<nav\b.*?</nav>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)


def test_no_internal_vocabulary_in_the_visible_text(html):
    text = visible_text(html).lower()
    hits = [t for t in INTERNAL_TERMS if re.search(rf"\b{re.escape(t.lower())}\b", text)]
    assert not hits, (
        f"internal vocabulary on a public page: {hits}. §6.2 -- if a concept genuinely "
        "needs a name, name it in the reader's language."
    )


def test_the_rendered_feed_carries_no_internal_vocabulary(feed):
    """The prose is curated, but it is curated in a Python file, and nothing stops the next
    editor pasting a work item's own name into it. This is the control that would catch it."""
    prose = " ".join(
        [e["name"] + " " + e["what"] for e in feed["world"]["entries"] + feed["supplier"]["entries"]]
        + [s["area"] + " " + s["what"] for s in feed["go_live"]["seams"]]
    ).lower()
    hits = [t for t in INTERNAL_TERMS if re.search(rf"\b{re.escape(t.lower())}\b", prose)]
    assert not hits, f"internal vocabulary in the published prose: {hits}"


def _vocabulary_hits(page_html: str) -> list[str]:
    """The control itself, extracted so the mutations can drive the REAL one."""
    text = visible_text(page_html).lower()
    return [t for t in INTERNAL_TERMS if re.search(rf"\b{re.escape(t.lower())}\b", text)]


def test_MUTATION_an_internal_term_injected_into_the_REAL_page_fires(html):
    """Driven against the actual page, not a synthetic string. A mutation that only proves
    a regex works has tested the regex, not the control."""
    doctored = html.replace(
        "<h1 class=\"hero-h\">Capabilities</h1>",
        "<h1 class=\"hero-h\">Capabilities</h1><p>Each atom sits in a lane at level_current 2.</p>",
    )
    assert doctored != html, "the injection point moved — fix the mutation, not the control"
    hits = _vocabulary_hits(doctored)
    assert "atom" in hits and "lane" in hits and "level_current" in hits
    assert _vocabulary_hits(html) == [], "the undoctored page must still be clean"


def test_MUTATION_the_vocabulary_control_ignores_markup_and_nav(html):
    """The other half: a control that fired on class names or on the nav's own words would
    be unusable, and would be 'fixed' by weakening it. It must be silent on both."""
    doctored = html.replace("<body>", '<body><div class="lane atom" data-epoch="2">')
    assert _vocabulary_hits(doctored) == [], (
        "the control read markup as prose — it must inspect visible text only"
    )


# ---------------------------------------------------------------------------
# The page cannot outrun its record
# ---------------------------------------------------------------------------
def test_every_capability_cites_work_that_exists(feed):
    levels = gen._levels()
    for entry in feed["world"]["entries"] + feed["supplier"]["entries"] + feed["go_live"]["seams"]:
        for wid in entry["rests_on"]:
            assert wid in levels, f"{entry['name']!r} cites {wid}, which is not in the record"


def test_status_matches_the_record_for_every_entry(feed):
    levels = gen._levels()
    for entry in feed["world"]["entries"] + feed["supplier"]["entries"] + feed["go_live"]["seams"]:
        assert entry["status"] == gen._status_for(entry["rests_on"], levels), entry["name"]


def test_the_page_states_what_is_absent(feed):
    """'Honest about what does not exist yet' is a requirement, not a tone. If nothing is
    Planned this test should be re-read, not deleted -- on this project it would be news."""
    planned = [e for e in feed["world"]["entries"] + feed["supplier"]["entries"]
               if e["status"] == "Planned"]
    assert planned, "no capability is marked absent — verify against the record before believing it"


def test_the_go_live_seams_do_not_claim_to_exist(feed):
    """Every counterparty connection is at the bottom of its scale today. If one ever reads
    Live, that is a real go-live claim and it must be made deliberately, not by this test
    quietly continuing to pass."""
    for seam in feed["go_live"]["seams"]:
        assert seam["status"] != "Live", (
            f"{seam['counterparty']} reads Live — a published claim that this project talks "
            "to a real counterparty. Verify it before this test is changed."
        )


def test_MUTATION_a_dropped_level_downgrades_the_page(tmp_path):
    """THE test. Rewrite the record so one cited work item sits below target, and the page's
    status must follow. If it does not, the status is decoration."""
    feed_src = json.loads((SITE / "data" / "maturity_map.json").read_text(encoding="utf-8"))
    target = "D1_bill_correctness"
    for atom in feed_src["atoms"]:
        if atom["id"] == target:
            assert atom["level_current"] >= atom["level_target"], "fixture assumption broke"
            atom["level_current"] = 0
    doctored = tmp_path / "maturity_map.json"
    doctored.write_text(json.dumps(feed_src), encoding="utf-8")

    before = gen._status_for([target], gen._levels())
    after = gen._status_for([target], gen._levels(doctored))
    assert before == "Live" and after == "Planned", f"{before} -> {after}"


def test_MUTATION_a_phantom_citation_raises(tmp_path):
    """A capability citing work that does not exist must RAISE, not render blank. On a page
    a reader cannot check, a phantom citation is worse than in the record."""
    with pytest.raises(gen.CapabilitySourceUnavailable, match="absent from the record"):
        gen._status_for(["NO_SUCH_WORK_ITEM"], gen._levels())


@pytest.mark.parametrize("payload", ['{"atoms": []}', "{}", "not json"])
def test_MUTATION_FAIL_OPEN_an_empty_or_broken_record_raises(tmp_path, payload):
    bad = tmp_path / "map.json"
    bad.write_text(payload, encoding="utf-8")
    with pytest.raises(gen.CapabilitySourceUnavailable):
        gen._levels(bad)


def test_MUTATION_FAIL_OPEN_a_missing_interfaces_directory_raises(tmp_path):
    with pytest.raises(gen.CapabilitySourceUnavailable):
        gen.typed_seams(tmp_path / "nowhere")


# ---------------------------------------------------------------------------
# Freshness and provenance (§6.5, §6.6)
# ---------------------------------------------------------------------------
def test_the_feed_carries_its_own_stamp_and_sources(feed):
    assert feed.get("generated_at"), "no generation stamp — freshness must be visible"
    assert feed.get("git_commit") and feed["git_commit"] != "latest", (
        "git_commit is absent or the literal 'latest' — the fail-open shape a prior "
        "Expert Hour found on six published feeds"
    )
    for key in ("record", "status_rule", "seams", "wall"):
        assert feed["sources"].get(key), f"provenance missing for {key}"


def test_the_page_renders_the_stamp_and_does_not_hardcode_a_figure(html):
    assert 'id="stamp"' in html, "the page must render its generation stamp"
    body = visible_text(html)
    assert not re.search(r"\b\d{2,}\s+(capabilities|seams|crossings)\b", body), (
        "a count is hardcoded in the markup — every figure comes from the feed"
    )


def test_the_door_boots_against_its_own_feed():
    """R11's repo-side half: drive the page's own script with the real feed and assert it
    rendered real content, rather than trusting that the markup looks right."""
    harness = SITE / "_live_harness.mjs"
    if not harness.is_file():
        pytest.skip("shared render harness not present")
    feeds = {"../data/capabilities_door.json": json.loads(FEED.read_text(encoding="utf-8"))}
    proc = subprocess.run(
        ["node", str(harness), str(INDEX)],
        input=json.dumps(feeds), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr[:500]
    out = json.loads(proc.stdout)
    for element in ("world", "supplier", "golive", "wall", "stamp"):
        rendered = out.get(element) or {}
        content = rendered.get("innerHTML") or rendered.get("textContent") or ""
        assert content.strip(), f"#{element} rendered nothing"
        assert "could not load" not in content.lower(), f"#{element} rendered its error path"
