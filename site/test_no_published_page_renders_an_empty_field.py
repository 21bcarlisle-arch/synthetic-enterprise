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

import json
import re
import sys
from html import unescape
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

SCRIPT_VALUE = "a script value printed as text"
_SCRIPT_TOKEN = EMPTY_FIELD_SHAPES[SCRIPT_VALUE]
_NOT_TEXT = re.compile(r"<(script|style)\b.*?</\1\s*>|<!--.*?-->", re.S | re.I)


_FETCHED_FEED = re.compile(r"""fetch\(\s*["']([^"'?#]+\.json)""")


def _strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in _strings(v)]
    return []


def static_text(html: str, page: Path | None = None) -> str:
    """The words a page is GIVEN: its own bytes with no script, style or comment, plus every string
    in the JSON feeds it fetches. A script printing a string it was given is printing text."""
    words = [unescape(re.sub(r"<[^>]+>", " ", _NOT_TEXT.sub(" ", html)))]
    if page is not None:
        for rel in _FETCHED_FEED.findall(html):
            feed = (page.parent / rel).resolve()
            try:
                words += _strings(json.loads(feed.read_text()))
            except (OSError, ValueError):
                continue
    return "\n".join(words)


def script_values_printed(text: str, static: str) -> int:
    """How many script-value tokens the rendered `text` carries beyond those in the page's bytes.

    "undefined" is also an English word: a seat's decision baked into the Harness page's HTML reads
    "the survivor tier is undefined" (18 Nov), carried to the Harness page from a decision record.
    A leaked value is one a SCRIPT made, so it is a token the rendered text has beyond what the
    page was given (`static_text`). A feed string carrying the word can mask one leak of it."""
    excess = 0
    for token in ("undefined", "NaN", "[object Object]"):
        pattern = re.compile(r"\b" + re.escape(token) + r"\b" if token[0].isalpha() else re.escape(token))
        excess += max(0, len(pattern.findall(text)) - len(pattern.findall(static)))
    return excess


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
        urls = {f"{base}/{p.relative_to(docroot).as_posix()}": p for p in pages}
        got = read_pages_in_browser([(u, [":body"]) for u in urls], open_all_details=True)
        yield {u: dict(payload, static=static_text(urls[u].read_text(errors="replace"), urls[u]))
               for u, payload in got.items()}


def test_no_published_page_renders_an_empty_field(readings):
    found = {}
    for url, payload in readings.items():
        text = ((payload.get("elements") or {}).get(":body") or {}).get("text") or ""
        assert text.strip(), f"{url} gave no body text, so nothing is claimed for it"
        holes = [h for h in empty_fields(text) if not h.startswith(SCRIPT_VALUE)]
        if script_values_printed(text, payload["static"]):
            holes += [h for h in empty_fields(text) if h.startswith(SCRIPT_VALUE)]
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


def test_MUTATION_a_script_value_is_one_the_page_bytes_did_not_carry():
    """The word in the served prose is text; the same word put there by a script is a hole; and a
    script's own `=== undefined` does not mask a leak."""
    prose = "the survivor tier is undefined. A run with S5 undefined could not discriminate"
    html = ("<html><head><script>if (x === undefined) {}</script></head><body><p>" + prose
            + "</p><p id='n'></p></body></html>")
    static = static_text(html)
    assert "=== undefined" not in static
    assert script_values_printed(prose, static) == 0
    assert script_values_printed(prose + " the run executed undefined and NaN", static) == 2
    assert script_values_printed("executed undefined", static_text("<script>undefined</script>")) == 1



def test_MUTATION_a_feed_string_the_page_fetched_is_text(tmp_path):
    """The 18 Nov case: the word reached the page in a fetched feed's string, then a script printed it."""
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "f.json").write_text(json.dumps({"rows": [{"why": "the tier is undefined"}]}))
    page = tmp_path / "p" / "index.html"
    page.parent.mkdir()
    html = '<script>fetch("../data/f.json").then(r => r.json())</script><p></p>'
    assert script_values_printed("the tier is undefined", static_text(html, page)) == 0
    assert script_values_printed("the tier is undefined", static_text(html)) == 1


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
