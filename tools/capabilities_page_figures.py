"""Capabilities: the world-and-supplier grid and the go-live table, written into the page at publish.

Director, 23 Oct 2026 07:18 (advisor channel, DIRECTOR_STEER_THE_OTHER_PAGES_MATCH_THE_FRONT_DOOR,
item 3.1): the capability grid is "rendered static", and item 2: "No 'Loading…' above the fold.
Render the headline content into the HTML at publish, as the front door now does." Until this
module the grid and the go-live table were drawn by the page's own script after a fetch, so a
reader without JavaScript, or a slow one, met two empty columns where the page's best content sits.

Every block is rendered from `site/data/capabilities_door.json` -- the feed
`tools/publish_from_a_clean_tree` has just produced -- and nothing is typed here: a state is the
feed's computed state, a count is a count of the feed's entries. So the page cannot say more than
the feed, and `tests/tools/test_capabilities_page_figures.py` holds the committed page to the
committed feed.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

BLOCKS = ("WORLD", "SUPPLIER", "ACCESS", "GOLIVE")
START = ("<!-- CAPABILITIES-{}:START (written at publish by "
         "tools/capabilities_page_figures.py -- do not hand-edit) -->")
END = "<!-- CAPABILITIES-{}:END -->"

STATES = ("Live", "Building", "Planned")
_ACCESS = (("OPEN", "open today"), ("SANDBOX", "reachable without qualifying"),
           ("GATED", "need a qualification we do not hold"))

E = html.escape


def _pill(status):
    cls = {"Live": "pill-live", "Building": "pill-building"}.get(status, "pill-planned")
    return '<span class="pill {}">{}</span>'.format(cls, E(str(status)))


def _item(e):
    # A count of tests that EXIST, not a run: nothing records when a claim's tests last ran.
    # Where nothing published shows how a Live claim is checked, it says so in words rather
    # than linking somewhere plausible.
    proof = ""
    if e.get("status") == "Live":
        c = e.get("checks")
        if c:
            proof = ' <span class="checks">{} automated tests are written against this{}.</span>'.format(
                E(str(c["checks"])),
                ", covering {} of the {} pieces of work it rests on".format(
                    E(str(c["covered"])), E(str(c["of"]))) if c["covered"] < c["of"] else "")
        else:
            proof = ' <span class="noproof">Nothing published yet shows how this is checked.</span>'
        if e.get("evidence"):
            proof += ' <a class="inline-link proof-link" href="{}">see the record</a>'.format(
                E(e["evidence"]))
    if e.get("held_from_live"):
        proof += ' <span class="noproof">Shown as building: {}.</span>'.format(
            E(e["held_from_live"]))
    if e.get("not_served"):
        proof += ' <span class="noproof">Built and tested, but not served today: {} accounts are ' \
                 'suspended from the book.</span>'.format(E(" and ".join(e["not_served"])))
    return '<div class="item"><div class="item-h">{}{}</div><div class="item-p">{}{}</div></div>'.format(
        E(e["name"]), _pill(e["status"]), E(e["what"]), proof)


def render_side(side):
    """One column: a count per state, then the Live functions under Now and the rest under Next."""
    entries = side.get("entries") or []
    counts = " &middot; ".join("{} {}".format(sum(1 for e in entries if e.get("status") == s),
                                              s.lower()) for s in STATES)
    out = ['<p class="side-count">{} functions: {}</p>'.format(len(entries), counts)]
    for heading, wanted in (("Now", ("Live",)), ("Next", ("Building", "Planned"))):
        rows = [e for e in entries if e.get("status") in wanted]
        if rows:
            out.append('<h4 class="col-h">{} &middot; {}</h4>'.format(heading, len(rows)))
            out.extend(_item(e) for e in rows)
    return "\n".join(out)


def render_access(go_live):
    tally = go_live.get("access_tally") or {}
    return "".join('<div class="fig"><div class="fig-v">{}</div><div class="fig-k">{}</div></div>'
                   .format(E(str(tally.get(k, 0))), E(label)) for k, label in _ACCESS)


def render_golive(go_live):
    rows = []
    for s in go_live.get("seams") or []:
        if s.get("spec"):
            spec = '<span class="spec-read">read</span> ' + E(s["spec"]["what"])
        elif s.get("used"):
            spec = ('<span class="spec-used">read for what the run uses</span> '
                    + E(s["used"]["what"]) + '; the whole specification is not read')
        else:
            spec = '<span class="spec-unread">not read</span>'
        rows.append('<tr><td>{}</td><td class="who">{}</td><td><span class="pill pill-{}">{}</span> '
                    '{}</td><td>{}</td><td>{}</td></tr>'.format(
                        E(s["area"]), E(s["counterparty"]), E(str(s["access"]).lower()),
                        E(str(s["access"])), E(s["gate"]), spec, _pill(s["status"])))
    return "\n".join(rows)


def render_blocks(feed):
    go_live = feed.get("go_live") or {}
    return {"WORLD": render_side(feed.get("world") or {}),
            "SUPPLIER": render_side(feed.get("supplier") or {}),
            "ACCESS": render_access(go_live),
            "GOLIVE": render_golive(go_live)}


def block(page, name):
    """The text currently between a block's markers, or None if the page lacks them."""
    start, end = page.find(START.format(name)), page.find(END.format(name))
    if start < 0 or end < start:
        return None
    return page[start + len(START.format(name)):end].strip("\n")


def write_capabilities_figures(page_path, feed_path):
    """Rewrite every block on the Capabilities page from the feed. True if all were written."""
    try:
        page = Path(page_path).read_text(encoding="utf-8")
        feed = json.loads(Path(feed_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("CAPABILITIES FIGURES NOT WRITTEN: {}".format(exc), file=sys.stderr)
        return False
    out = page
    for name, inner in render_blocks(feed).items():
        if block(out, name) is None:
            print("CAPABILITIES FIGURES NOT WRITTEN: {} has no {} markers".format(page_path, name),
                  file=sys.stderr)
            return False
        start = out.find(START.format(name))
        out = out[:start] + START.format(name) + "\n" + inner + "\n" + out[out.find(END.format(name)):]
    Path(page_path).write_text(out, encoding="utf-8")
    return True


if __name__ == "__main__":
    site = Path(__file__).resolve().parent.parent / "site"
    sys.exit(0 if write_capabilities_figures(site / "capabilities" / "index.html",
                                             site / "data" / "capabilities_door.json") else 1)
