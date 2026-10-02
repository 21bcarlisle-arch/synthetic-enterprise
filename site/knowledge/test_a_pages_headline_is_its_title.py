"""The defect: two knowledge pages opened with another page's headline -- "How the GB electricity
market fits together", copied with the template and never edited -- under correct <title>s, and a
third had no <h1> at all, its headline written by a script from a feed whose wording disagreed with
its <title> (and a third wording on a failed fetch). Found by the director's review, 2026-10-02.

MADE IMPOSSIBLE, NOT CHECKED-AFTER: every knowledge page carries exactly one <h1>, its text equals
the page's <title> (less the site prefix), and no script on the page may write to that <h1>, so the
headline a reader sees is the one this test reads. Keyed to every page found on disk, not a list.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

KNOWLEDGE = Path(__file__).resolve().parent
PAGES = sorted(p for p in KNOWLEDGE.glob("*/index.html"))
_PREFIX = re.compile(r"^Poesys\s*(?:—|--|–|-)\s*")


def _text(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", fragment)).split())


def _title(src: str) -> str:
    m = re.search(r"<title>(.*?)</title>", src, re.S)
    return _PREFIX.sub("", _text(m.group(1))) if m else ""


def _h1s(src: str) -> list[tuple[str, str]]:
    """(id, text) of every <h1> in the page."""
    return [(re.search(r'id="([^"]+)"', attrs).group(1) if re.search(r'id="([^"]+)"', attrs) else "",
             _text(body)) for attrs, body in re.findall(r"<h1([^>]*)>(.*?)</h1>", src, re.S)]


def test_there_are_pages_to_check():
    assert len(PAGES) >= 15, [p.parent.name for p in PAGES]


def test_every_page_has_exactly_one_headline_and_it_is_its_title():
    wrong = {}
    for p in PAGES:
        src = p.read_text(encoding="utf-8")
        heads, title = _h1s(src), _title(src)
        if len(heads) != 1 or heads[0][1] != title:
            wrong[p.parent.name] = {"title": title, "h1": [t for _, t in heads]}
    assert not wrong, f"headline and title disagree: {wrong}"


def test_no_script_writes_the_headline():
    """A script that sets the <h1> makes the rendered headline something this test never read."""
    writers = {}
    for p in PAGES:
        src = p.read_text(encoding="utf-8")
        for hid, _ in _h1s(src):
            if not hid:
                continue
            pat = re.compile(rf"""set\(\s*["']{re.escape(hid)}["']|getElementById\(\s*["']{re.escape(hid)}["']\s*\)\s*\.\s*(?:innerHTML|textContent|innerText)\s*=""")
            if pat.search(src):
                writers[p.parent.name] = hid
    assert not writers, f"pages whose scripts write their own headline: {writers}"
