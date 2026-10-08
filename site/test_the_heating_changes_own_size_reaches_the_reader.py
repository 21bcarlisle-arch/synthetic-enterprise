"""The heating change's own size reaches the rendered `/capabilities/` page, beside the sentence
that names the change. Drives the real door through `site/_live_harness.mjs` against the
published (index) bytes; `site/test_the_published_bytes_reader.py` argues why the index.

Each leg mutates the feed and asserts the page follows it, so a literal on the page reds.
"""
from __future__ import annotations

import copy
import html as html_lib
import json
import re
import subprocess
from pathlib import Path

import pytest
from test_the_published_bytes_reader import (
    published_file,
    published_json,
    refuse_working_tree_reads,
)

SITE = Path(__file__).resolve().parent
HARNESS = SITE / "_live_harness.mjs"
DOOR_REL = "site/capabilities/index.html"
FEED_REL = "site/data/value_arms.json"
GROWTH_REL = "site/data/book_growth.json"
CAPS_REL = "site/data/capabilities_door.json"
DD_ARMS_REL = "site/data/dd_opening_arms.json"
PANEL = "arms-redraw"


def test_no_subject_of_this_file_is_read_from_the_working_tree():
    refuse_working_tree_reads(__file__, (DOOR_REL, FEED_REL, GROWTH_REL, CAPS_REL, DD_ARMS_REL))


def _prose(sentence: str) -> str:
    return re.sub(r"\s+", " ", sentence).replace(" -- ", " — ")


def _render(feed: dict) -> str:
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing, so the render check is unavailable")
    payload = {
        "../data/value_arms.json": feed,
        "../data/dd_opening_arms.json": published_json(DD_ARMS_REL),
        "../data/engagement_separation.json": published_json("site/data/engagement_separation.json"),
        "../data/billing_accuracy.json": published_json("site/data/billing_accuracy.json"),
        "../data/book_growth.json": published_json(GROWTH_REL),
        "../data/capabilities_door.json": published_json(CAPS_REL),
    }
    proc = subprocess.run(["node", str(HARNESS), str(published_file(DOOR_REL))],
                          input=json.dumps(payload), capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr[-2000:]
    out = json.loads(proc.stdout)
    meta = out.get("_meta") or {}
    assert not meta.get("unresolved"), meta.get("unresolved")
    assert not meta.get("scriptError"), meta.get("scriptError")
    html = (out.get(PANEL) or {}).get("innerHTML") or ""
    assert html, "the page wrote nothing into #{}".format(PANEL)
    return html


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def _block(html: str) -> str:
    match = re.search(r'<p class="cw-w220"[^>]*>.*?</p>', html, re.S)
    assert match, "the page renders no element for the heating change's own size"
    return match.group(0)


@pytest.fixture(scope="module")
def feed() -> dict:
    loaded = published_json(FEED_REL)
    if not (loaded.get("current_world") or {}).get("w2_20_own_effect"):
        pytest.fail("the published feed carries no `current_world.w2_20_own_effect`")
    return loaded


def test_the_published_size_is_on_the_page(feed):
    block = _block(_render(feed))
    effect = feed["current_world"]["w2_20_own_effect"]
    shown = effect["sentence"] if effect["available"] else effect["why_not"]
    assert _prose(shown) in _text(block)


def test_the_page_follows_the_feeds_sentence_not_a_literal(feed):
    mutated = copy.deepcopy(feed)
    mutated["current_world"]["w2_20_own_effect"] = {
        "available": True, "sentence": "On its own, the heating change takes 99 accounts off."}
    block = _block(_render(mutated))
    assert "takes 99 accounts off" in _text(block) and "var(--muted)" in block


def test_a_withdrawn_size_renders_its_reason_in_amber(feed):
    mutated = copy.deepcopy(feed)
    mutated["current_world"]["w2_20_own_effect"] = {
        "available": False, "why_not": "The heating change's size was measured at another commit."}
    block = _block(_render(mutated))
    assert "measured at another commit" in _text(block) and "var(--amber)" in block
