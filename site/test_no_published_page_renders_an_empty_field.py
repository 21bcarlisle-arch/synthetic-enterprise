"""No published page shows a reader a field rendered empty.

THE DEFECT, read by the director on the live Capabilities page on 2 Nov: "produced at ,", "the run
executed  and this page", "Source:  Open question: ", "measured on .". One cause: a path or a
commit in a feed sentence was replaced by a label ("a file", "a commit") that the page drew as CSS
`content: attr(data-k)`. A painted screen showed it; copy and paste, reader mode, a fetch and the
advisor's reading did not, so the sentence reached them with a hole where its evidence was. The
label is now text (`evidence()` in site/capabilities/index.html).

WHAT A READING IS HERE. `innerText` of the whole body, every `<details>` opened, in chromium, over
the published (index) bytes of every page. innerText leaves out CSS-generated content -- which is
exactly the property that hid the defect from screenshots and showed it to everyone else.

THE SHAPES are what an empty slot leaves in a sentence, whatever the field was. Each is keyed to the
hole, never to a word on today's page, so a new page with a new field is covered on its first day:
  * a function word followed straight by punctuation -- "produced at ,", "measured on ."
  * empty brackets -- "( )"
  * a field label followed directly by another label -- "Source: Open question:"
  * a label left at the end of a line, with the next paragraph starting in capitals -- "Method:"
  * a script value printed as text -- "undefined", "NaN", "[object Object]"
A hole QUOTED is not a hole: the punctuation that closes each shape must be followed by space or
the end, so "'produced at ,'" -- the steer's own words, published on the Harness page -- is text.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from test_no_published_page_scrolls_sideways_on_a_phone import (  # noqa: E402
    _scratch,
    _skip_without_a_browser,
    published_pages,
)
from test_the_browser_reading import published_site, read_pages_in_browser  # noqa: E402

_FUNCTION_WORD = r"\b(?:at|on|from|of|by|in|to|for|with|and|the|a|an|is|was|executed)"

EMPTY_FIELD_SHAPES = {
    # The punctuation must END something (space or end after it): ".claude/" and ".rc" are names.
    "a function word with nothing after it": re.compile(
        _FUNCTION_WORD + r"[ \t]+[,.;:)](?=\s|$)"),
    # Not after a word: `build_merit_stack()` is a call, not a hole.
    "empty brackets": re.compile(r"(?<!\w)\([ \t\n]*\)|(?<!\w)\[[ \t\n]*\]"),
    "a label followed by another label": re.compile(
        r"\b[A-Z][a-z]+(?: [a-z]+)?:[ \t]*\n?[ \t]*[A-Z][a-z]+(?: [a-z]+)?:(?=\s|$)"),
    "a label left at the end of a line": re.compile(
        r"(?:^|[.!?] )[A-Z][a-z]+(?: [a-z]+)?:[ \t]*\n[ \t]*\n[ \t]*[A-Z]{3,} [A-Z]{2,}", re.M),
    "a script value printed as text": re.compile(r"\bundefined\b|\bNaN\b|\[object Object\]"),
}


def empty_fields(text: str) -> list[str]:
    """Every empty-field shape in `text`, each with the words either side of it."""
    out = []
    for name, shape in EMPTY_FIELD_SHAPES.items():
        for m in shape.finditer(text):
            around = text[max(0, m.start() - 60):m.end() + 30].replace("\n", " / ")
            out.append(f"{name}: ...{around}...")
    return out


@pytest.fixture(scope="module")
def readings():
    _skip_without_a_browser()
    with published_site() as (base, docroot):
        pages = published_pages(docroot)
        assert len(pages) >= 20, (
            f"only {len(pages)} published page(s) found under {docroot}: treated as a broken scan, "
            "since a short population makes the sweep below pass vacuously")
        jobs = [(f"{base}/{p.relative_to(docroot).as_posix()}", [":body"]) for p in pages]
        yield read_pages_in_browser(jobs, open_all_details=True)


def test_no_published_page_renders_an_empty_field(readings):
    found = {}
    for url, payload in readings.items():
        text = ((payload.get("elements") or {}).get(":body") or {}).get("text") or ""
        assert text.strip(), f"{url} gave no body text, so nothing is claimed for it"
        holes = empty_fields(text)
        if holes:
            found[url] = holes
    assert not found, "{} published page(s) show a reader an empty field:\n{}".format(
        len(found), "\n".join(f"  {u}\n    " + "\n    ".join(h[:8]) for u, h in sorted(found.items())))


def test_MUTATION_each_shape_fires_on_the_text_the_director_read():
    """Every shape fires on the 2 Nov hole it exists for, and none fires on the filled sentence."""
    holes = {
        "a function word with nothing after it": "the report produced at , and measured on .",
        # (`.claude/`, `func()` and a quoted "'measured on .'" are in the filled leg below)
        "empty brackets": "same houses ( ), different behaviour",
        "a label followed by another label": "crosses 0.3763. Source: \nOpen question: \n",
        "a label left at the end of a line": "does not reach the write-off. Method: \n\nAND THE VERDICT",
        "a script value printed as text": "the run executed undefined and NaN",
    }
    for name, text in holes.items():
        assert EMPTY_FIELD_SHAPES[name].search(text), f"{name!r} does not fire on {text!r}"
    filled = ("the report produced at a commit, and measured on 154 accounts. same houses "
              "(a commit), different behaviour. Source: a file Open question: a file. "
              "Method: a file\n\nAND THE VERDICT. This figure reaches one:\n\nmoney - measured. "
              "Held by .claude/agents/x.md, queued on the .rc, from build_merit_stack(): the "
              "steer quoted ('produced at ,', 'Source: Open question:', 'measured on .').")
    assert empty_fields(filled) == [], empty_fields(filled)


def test_MUTATION_a_label_drawn_as_css_content_is_caught_in_a_browser():
    """The defect's own mechanism, in chromium: a label drawn by CSS reads as a hole, and the same
    label as text does not. If innerText ever started carrying generated content, the first leg
    would go green on the defect and this would say so."""
    _skip_without_a_browser()
    css = ('<style>.ev::before{content:attr(data-k)} .ev-v{display:none}</style>')
    page = ('<!doctype html><html><head>{}</head><body><p>Source: <label class="ev" data-k="{}">'
            '<span class="ev-v">docs/x.md</span>{}</label>.</p><p>Open question: a file.</p>'
            '<details><summary>more</summary><p>produced at <span>{}</span>, then</p></details>'
            '</body></html>')
    with _scratch({"css.html": page.format(css, "a file", "", ""),
                   "text.html": page.format(css, "", "a file", "a commit")}) as base:
        got = read_pages_in_browser([(f"{base}/css.html", [":body"]),
                                     (f"{base}/text.html", [":body"])], open_all_details=True)
    text_of = {u: p["elements"][":body"]["text"] for u, p in got.items()}
    assert empty_fields(text_of[f"{base}/css.html"]), text_of
    assert not empty_fields(text_of[f"{base}/text.html"]), text_of
