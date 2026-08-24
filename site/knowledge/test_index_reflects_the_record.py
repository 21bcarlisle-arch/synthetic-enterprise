#!/usr/bin/env python3
"""The Knowledge INDEX may not contradict the record the pages are written from.

THE DEFECT THIS FIRES ON, and it is not hypothetical -- it is what shipped. The index
carried a hand-typed section headed "Stubs — not yet written" listing seven pages with an
amber "Stub" badge. By 2026-08-24 every one of those seven had been written to seven rungs
and checked against a named published source, and each page's own header said, in as many
words, "A written page, not a stub." A reader arriving at Knowledge was told seven topics
were unwritten and then found seven written topics. Nothing was broken; the index was
simply a copy of a fact that had moved, which is the failure mode of every hand-typed
summary of a record.

So the rule is not "keep the index up to date". It is:

    the index states no review state of its own. It carries the LINKS -- which must be real
    <a href> markup, because tools/site_reachability.py strips inline scripts before reading
    hrefs and a script-built route is not a route -- and the badge text comes from
    site/data/knowledge_wholesale.json through the same rule the pages use.

Three things are graded here, and each can fail on its own:

  * COVERAGE -- every topic in the record is linked, and every link is a topic. A page added
    to the record and forgotten on the index is the orphan this catches before the reader.
  * COPY -- the card title and blurb are quoted from the record exactly. Drift in either is
    the same class of defect as the stub badge, one field smaller.
  * STATE -- no review-state word appears in the markup at all, and the rendered page (driven
    through site/_live_harness.mjs, the same harness the live verifier uses) labels every
    topic with the state Python computes. The fail-closed direction is tested too: with the
    feed unreachable, no badge may claim a check.
"""
from __future__ import annotations

import html as htmllib
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
PROJECT = SITE.parent
INDEX = HERE / "index.html"
FEED = SITE / "data" / "knowledge_wholesale.json"
LIVE_HARNESS = SITE / "_live_harness.mjs"
FEED_URL = "../data/knowledge_wholesale.json"

sys.path.insert(0, str(HERE))

from review_state import DUE, FRESH, STUB, UNCHECKED, review_state, states_for  # noqa: E402

_SCRIPT_RE = re.compile(r"<script\b.*?</script\s*>", re.IGNORECASE | re.DOTALL)
_STYLE_RE = re.compile(r"<style\b.*?</style\s*>", re.IGNORECASE | re.DOTALL)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_CARD_RE = re.compile(
    r"""<a\s+class="card"\s+href="\./(?P<slug>[^"/]+)/">(?P<body>.*?)</a>""", re.DOTALL)
_CARD_H_RE = re.compile(r"""<div class="card-h">(?P<h>.*?)</div>""", re.DOTALL)
_CARD_P_RE = re.compile(r"""<div class="card-p">(?P<p>.*?)</div>""", re.DOTALL)
_BADGE_RE = re.compile(r"""<span class="state-badge" id="state-(?P<slug>[^"]+)"></span>""")

#: Every word the review rule can put on a badge or a heading. The index may contain NONE of
#: them: it does not get to have an opinion about whether a page is written or checked.
_STATE_WORDS = (
    "stub", "not yet written", "unwritten", "not written yet",
    "review due", "awaiting check", "reviewed 20", "last checked",
)


@pytest.fixture(scope="module")
def feed() -> dict:
    return json.loads(FEED.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def markup() -> str:
    """The index reduced to what a reader is actually shown as words. Three regions are
    excluded and each for its own reason: the SCRIPT, because the review rule lives there by
    design; the STYLE block, because `rev-stub` is a class name and a state a badge may
    legitimately be styled for; and HTML COMMENTS, because the ones here describe the defect
    and would otherwise trip the check that describes it. What remains is copy, and copy is
    where the index is forbidden an opinion."""
    text = INDEX.read_text(encoding="utf-8")
    return _COMMENT_RE.sub("", _STYLE_RE.sub("", _SCRIPT_RE.sub("", text)))


def _cards(markup: str) -> dict[str, dict]:
    out = {}
    for m in _CARD_RE.finditer(markup):
        body = m.group("body")
        h = _CARD_H_RE.search(body)
        p = _CARD_P_RE.search(body)
        title = re.sub(r"<[^>]+>", "", h.group("h")).strip() if h else ""
        blurb = re.sub(r"<[^>]+>", "", p.group("p")).strip() if p else ""
        out[m.group("slug")] = {
            "title": htmllib.unescape(title),
            "blurb": htmllib.unescape(blurb),
        }
    return out


def state_words_in(text: str) -> list[str]:
    """Review-state vocabulary found in a fragment. The checker, factored out so the mutation
    test can drive it against the markup that actually shipped."""
    low = text.lower()
    return [w for w in _STATE_WORDS if w in low]


# ---------------------------------------------------------------------------
# COVERAGE
# ---------------------------------------------------------------------------
def test_every_topic_in_the_record_is_linked_from_the_index(feed, markup):
    linked = set(_cards(markup))
    recorded = {t["id"] for t in feed["topics"]}
    assert recorded - linked == set(), (
        f"in the record but not linked from the index: {sorted(recorded - linked)}"
    )
    assert linked - recorded == set(), (
        f"linked from the index but not in the record: {sorted(linked - recorded)}"
    )


def test_the_links_are_real_markup_not_built_by_script(feed):
    """tools/site_reachability.py strips inline scripts before reading hrefs, deliberately: a
    route only JavaScript can build is not a route a crawler -- or a reader whose JS failed --
    can follow. Moving these cards into the renderer would orphan eight pages and the
    reachability control would be right to say so."""
    stripped = _SCRIPT_RE.sub("", INDEX.read_text(encoding="utf-8"))
    for topic in feed["topics"]:
        assert f'href="./{topic["id"]}/"' in stripped, (
            f"{topic['id']} is not reachable without JavaScript"
        )


def test_every_linked_topic_has_a_badge_element_to_fill(feed, markup):
    slots = set(_BADGE_RE.findall(markup))
    assert slots == {t["id"] for t in feed["topics"]}, (
        f"badge slots {sorted(slots)} do not match the record"
    )


# ---------------------------------------------------------------------------
# COPY -- quoted from the record, not paraphrased
# ---------------------------------------------------------------------------
def test_the_card_copy_is_quoted_from_the_record(feed, markup):
    cards = _cards(markup)
    for topic in feed["topics"]:
        card = cards[topic["id"]]
        assert card["title"] == topic["title"], (
            f"{topic['id']} card title {card['title']!r} != record {topic['title']!r}"
        )
        assert card["blurb"] == topic["blurb"], (
            f"{topic['id']} card blurb {card['blurb']!r} != record {topic['blurb']!r}"
        )


# ---------------------------------------------------------------------------
# STATE -- the index has no opinion of its own
# ---------------------------------------------------------------------------
def test_the_markup_states_no_review_state(markup):
    """Card BLURBS are excluded, and the reason is not convenience: they are required
    byte-for-byte equal to the record by `test_the_card_copy_is_quoted_from_the_record`, so a
    state word inside one is the RECORD's word and not a claim the index is making. Without
    that exclusion this check is a substring census with a false positive already in it --
    gas-wholesale's own blurb calls the topic "not a driver-stub of electricity"."""
    found = state_words_in(_CARD_P_RE.sub("", markup))
    assert not found, (
        f"the index markup states a review state in words: {found}. That is a copy of a fact "
        "that moves; the badge is filled from the record instead."
    )


def test_MUTATION_the_markup_that_shipped_is_caught(feed):
    """The named defect, driven on the exact line that was live until 2026-08-24. The seven
    pages it called stubs are all `kind: page` with a recorded check, so the record and the
    markup disagreed -- and the checker must say so."""
    shipped = (
        '<div class="sec">Stubs — not yet written</div>\n'
        '<a class="card" href="./carbon-price/"><div class="card-h">Carbon price '
        '<span class="stub-badge">Stub</span></div></a>'
    )
    assert state_words_in(shipped), "the checker passed the markup that actually shipped"

    by_id = {t["id"]: t for t in feed["topics"]}
    assert review_state(by_id["carbon-price"], feed["review_policy"])["state"] != STUB, (
        "the record itself now calls carbon-price a stub -- this test's premise is gone"
    )


# ---------------------------------------------------------------------------
# The JavaScript mirror agrees with the Python rule
# ---------------------------------------------------------------------------
def _index_rule() -> str:
    js = INDEX.read_text(encoding="utf-8")
    start = js.index("function reviewState(")
    end = js.index("function renderBadges(")
    return js[start:end]


def _js_state(topic_id: str, feed: dict, today_iso: str) -> dict:
    runner = _index_rule() + f"""
const feed = {json.dumps(feed)};
const topic = feed.topics.find(t => t.id === {json.dumps(topic_id)});
const out = reviewState(topic, feed.review_policy, new Date({json.dumps(today_iso)} + "T00:00:00Z"));
console.log(JSON.stringify(out));
"""
    proc = subprocess.run(["node", "--input-type=module", "-e", runner],
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr[:400]
    return json.loads(proc.stdout)


def test_the_index_rule_agrees_with_python_on_every_topic(feed):
    today = date.today()
    py = states_for(feed, today)
    for topic in feed["topics"]:
        js = _js_state(topic["id"], feed, today.isoformat())
        assert js["state"] == py[topic["id"]]["state"], (
            f"{topic['id']}: index says {js['state']}, control says {py[topic['id']]['state']}"
        )
        assert js["label"] == py[topic["id"]]["label"], topic["id"]


def test_the_index_rule_agrees_on_every_threshold_boundary(feed):
    """Where a drift hides: one implementation using >= and the other >."""
    policy = feed["review_policy"]
    probe = dict(next(t for t in feed["topics"] if t["id"] == "electricity-wholesale"))
    probe["reviewed"] = {"last_verified": "2026-01-01", "source": "probe"}
    for cls, days in policy["threshold_days"].items():
        probe["rate_of_change"] = cls
        doctored = dict(feed, topics=[probe])
        for offset in (days - 1, days, days + 1):
            when = (date(2026, 1, 1) + timedelta(days=offset)).isoformat()
            js = _js_state(probe["id"], doctored, when)
            py = review_state(probe, policy, today=date.fromisoformat(when))
            assert js["state"] == py["state"], (
                f"{cls} at +{offset}d: index {js['state']} vs control {py['state']}"
            )


# ---------------------------------------------------------------------------
# What the page actually RENDERS -- driven through the live harness
# ---------------------------------------------------------------------------
def _render(feeds: dict) -> dict:
    proc = subprocess.run(
        ["node", str(LIVE_HARNESS), str(INDEX)],
        input=json.dumps(feeds), capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr[:600]
    return json.loads(proc.stdout)


def test_the_rendered_index_labels_every_topic_with_its_recorded_state(feed):
    rendered = _render({FEED_URL: feed})
    py = states_for(feed, date.today())
    for topic in feed["topics"]:
        el = rendered.get(f"state-{topic['id']}")
        assert el, f"{topic['id']} rendered no badge at all"
        assert el["textContent"] == py[topic["id"]]["label"], (
            f"{topic['id']}: page shows {el['textContent']!r}, "
            f"record says {py[topic['id']]['label']!r}"
        )


def test_MUTATION_a_topic_past_its_threshold_renders_review_due(feed):
    """The brief's named defect at the index level: a page past its threshold that does not
    say so. Driven by ageing the record, not by waiting for the calendar."""
    aged = json.loads(json.dumps(feed))
    aged["topics"] = [dict(t, reviewed=dict(t["reviewed"], last_verified="2020-01-01"))
                      for t in aged["topics"]]
    rendered = _render({FEED_URL: aged})
    for topic in aged["topics"]:
        el = rendered.get(f"state-{topic['id']}")
        assert el and el["textContent"] == "Review due", (
            f"{topic['id']} is years past its threshold and the index says "
            f"{el and el['textContent']!r}"
        )


def test_MUTATION_FAIL_CLOSED_an_unreachable_record_claims_no_check(feed):
    """An unavailable check is a FAILED check (R15). The shape that reaches a reader is the
    feed 404ing after a good deploy; the index must then show the pages WITHOUT a review
    state, never leave them looking checked."""
    rendered = _render({})  # the harness rejects any url it was not given, exactly as a 404
    for topic in feed["topics"]:
        el = rendered.get(f"state-{topic['id']}")
        assert not (el and el["textContent"].strip()), (
            f"{topic['id']} claims {el['textContent']!r} with the record unreachable"
        )
    note = rendered.get("review-note")
    assert note and "could not be loaded" in note["textContent"], (
        "the index went quiet about a record it could not read"
    )


def test_the_states_the_record_can_produce_are_all_stylable():
    """A state with no badge class renders unstyled -- visible, but not as information.
    Cheap, and it is the thing that gets forgotten when a fifth state is added."""
    css = INDEX.read_text(encoding="utf-8")
    for state in (FRESH, DUE, UNCHECKED):
        assert f".state-badge.rev-{state}" in css, f"no badge style for {state}"
    assert ".state-badge {" in css, "the stub/default badge has no style"
