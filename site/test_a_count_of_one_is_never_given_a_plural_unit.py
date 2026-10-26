"""A count of one never takes a plural unit, anywhere a reader can meet it.

Steer, 26 Oct 2026 ("Built in the last 1 days" ... "Fix the pluraliser once, sitewide"): a page
checked yesterday read "Checked 1 days ago", on every knowledge page, from two renderers (the
pages' own script and `site/knowledge/review_state.py`) and the feed one of them writes.

Two legs, because the defect has two homes. The published bytes (every page and feed) carry no
"1 <unit>s"; and every inline script that joins a number to a time unit picks the unit by the
number, so a count rendered in the reader's browser is held too. KEYED TO THE PROPERTY: no count
is pinned, and a page with no such text passes.
"""
from __future__ import annotations

import re
from pathlib import Path

SITE = Path(__file__).resolve().parent
_UNITS = "days|weeks|months|years|hours|minutes"
#: "1 days", not "21 days", "1.5 days" or "£1 days".
_ONE_PLURAL = re.compile(r"(?<![\d.,£$-])\b1 (?:%s)\b" % _UNITS)
#: A script joining a variable to a hard plural: `+ age + " days`.
_JOINED = re.compile(r"\+\s*([A-Za-z_][\w.]*)\s*\+\s*[\"'] (?:%s)\b" % _UNITS)


def _published():
    for path in sorted(SITE.rglob("*")):
        if path.suffix in (".html", ".json", ".js") and "node_modules" not in path.parts:
            yield path


def test_no_published_page_or_feed_says_one_of_a_plural_unit():
    found = []
    for path in _published():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in _ONE_PLURAL.finditer(text):
            found.append("{}: ...{}...".format(path.relative_to(SITE), text[max(0, m.start() - 40):m.end()]))
    assert not found, "a count of one with a plural unit:\n" + "\n".join(found[:10])


def test_no_page_script_joins_a_count_to_a_hard_plural_unit():
    found = []
    for path in _published():
        if path.suffix == ".json":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in _JOINED.finditer(text):
            found.append("{}: {}".format(path.relative_to(SITE), m.group(0)))
    assert not found, (
        "a script prints a count with a fixed plural unit, so a count of one reads '1 days':\n"
        + "\n".join(found[:10]))
