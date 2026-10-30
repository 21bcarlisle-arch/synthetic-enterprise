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

24 Oct 2026 (DIRECTOR_STEER_CAPABILITIES_SHORTER_AND_ITS_GAPS_ARE_A_FIX_LIST, section 4): each grid
row is one line with its evidence badge and the paragraph one tap down; the use-case register, its
tally and the generation stamp are written here too, so the register can sit collapsed below the
fold with its three counts visible, and the stamp in the footer reads the feed it describes. The
dated "Fixed this week" strip is the feed's `fixed_this_week`.
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BLOCKS = ("LEAD", "FIXED", "WORLD", "SUPPLIER", "ACCESS", "GOLIVE", "UCTALLY", "USECASES", "STAMP")
START = ("<!-- CAPABILITIES-{}:START (written at publish by "
         "tools/capabilities_page_figures.py -- do not hand-edit) -->")
END = "<!-- CAPABILITIES-{}:END -->"

STATES = ("Live", "Building", "Planned")
_ACCESS = (("OPEN", "open today"), ("SANDBOX", "reachable without qualifying"),
           ("GATED", "need a qualification we do not hold"))
_UC_TALLY = (("testable_now", "testable against hidden truth today"),
             ("waiting", "waiting on truth the world does not model yet"),
             ("unmodelled_truths", "truths nothing is working on at all"))

E = html.escape


def _pill(status):
    cls = {"Live": "pill-live", "Building": "pill-building"}.get(status, "pill-planned")
    return '<span class="pill {}">{}</span>'.format(cls, E(str(status)))


def _badge(e):
    """The one-line evidence badge beside a function's state (director, 24 Oct: "function name,
    state and evidence badge, such as '28 tests'"). A count of tests that EXIST, not a run:
    nothing records when a claim's tests last ran."""
    c = e.get("checks")
    if not c:
        return "no test cited"
    badge = "{} tests".format(c["checks"])
    if c["covered"] < c["of"]:
        badge += " · {} of {} parts tested".format(c["covered"], c["of"])
    return badge


def _item(e):
    # One line, the paragraph one tap down. Where a function is held from Live, or not served,
    # the reason sits in the paragraph, and the badge already says "no test cited".
    more = ""
    if e.get("status") == "Live" and e.get("checks") and e["checks"]["covered"] < e["checks"]["of"]:
        more = ' <span class="checks">The tests cover {} of the {} pieces of work it rests ' \
               'on.</span>'.format(E(str(e["checks"]["covered"])), E(str(e["checks"]["of"])))
    if e.get("evidence"):
        more += ' <a class="inline-link proof-link" href="{}">see the record</a>'.format(
            E(e["evidence"]))
    if e.get("held_from_live"):
        more += ' <span class="noproof">Shown as building: {}.</span>'.format(
            E(e["held_from_live"]))
    if e.get("not_served"):
        more += ' <span class="noproof">Built and tested, but not served today: {} accounts are ' \
                'suspended from the book.</span>'.format(E(" and ".join(e["not_served"])))
    return ('<details class="item"><summary class="item-h">{}{}<span class="badge">{}</span>'
            '</summary><div class="item-p">{}{}</div></details>').format(
        E(e["name"]), _pill(e["status"]), E(_badge(e)), E(e["what"]), more)


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


#: A commit hash in a record's sentence: seven or more hex characters with a digit AND a letter
#: in them, so "decade" and "2016" are left alone.
_HASH = r"\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b"
#: The hash with the words that only introduce it ("in d909b6933", "(140b5ff7b)"), which go with it.
_HASH_PHRASE = re.compile(r"\s*\(" + _HASH + r"\)|\s+(?:in|at|by)\s+" + _HASH + r"|\s*" + _HASH)


def _strip_hashes(text):
    """(the sentence a reader meets, the hashes it cited). Steer of 26 Oct, section 3(b): bare
    commit hashes leave the visible text and are kept in the "Show the evidence" toggle."""
    return _HASH_PHRASE.sub("", text), re.findall(_HASH, text)


def _plural(n, unit):
    return "{} {}{}".format(n, unit, "" if str(n) == "1" else "s")


def _feed_day(feed):
    """The publish day of the feed, in the strip's own "%d %b %Y" form, or None."""
    try:
        return datetime.strptime(str(feed.get("generated_at"))[:10], "%Y-%m-%d").strftime("%d %b %Y")
    except ValueError:
        return None


def render_fixed(feed):
    """The dated "Fixed this week" strip under In brief (director, 24 Oct). Every date is the
    commit's own, read from git when the feed was built; whether each fix is already in the run
    the page's figures come from is computed, not written. Empty until a feed carries the record."""
    fixed = feed.get("fixed_this_week")
    if not fixed:
        return ""
    # Steer of 26 Oct, section 3(c): a "Fixed in the N days to <date>" strip whose date is not
    # this publish's is dropped, not shown stale. The feed is built at publish, so its own day
    # is the publish day.
    if feed.get("generated_at") is not None and fixed.get("as_of") != _feed_day(feed):
        return ""
    head = '<p class="brief-h">Fixed in the {} to {}</p>'.format(
        E(_plural(fixed["window_days"], "day")), E(fixed["as_of"]))
    items = fixed.get("items") or []
    if not items:
        return '<div class="fixed">{}<p class="note">Nothing recorded.</p></div>'.format(head)
    rows, evidence = [], []
    for it in items:
        where = {True: "in the published figures",
                 False: "reaches the figures at the next published run"}.get(
                     it.get("in_published_run"))
        what, cited = _strip_hashes(it["what"])
        rows.append('<li><span class="fixed-d">{}</span> {}{}</li>'.format(
            E(it["date"]), E(what),
            ' <span class="fixed-w">{}</span>'.format(where) if where else ""))
        evidence.append("<li>{}: <code>{}</code>{}</li>".format(
            E(it["date"]), E(it["commit"][:9]),
            "".join(", cites <code>{}</code>".format(E(h)) for h in cited)))
    return ('<div class="fixed">{}<ul>{}</ul><details class="evidence"><summary>Show the '
            'evidence</summary><ul>{}</ul></details></div>').format(
                head, "".join(rows), "".join(evidence))


def _money(v, signed=False):
    sign = ("+" if v > 0 else "&minus;" if v < 0 else "") if signed else ("&minus;" if v < 0 else "")
    return "{}&pound;{:,.0f}".format(sign, abs(v))


def _where(fig, vals):
    """Where this run's own draw fell in its re-draw family: above, below or inside it."""
    if fig > max(vals):
        return "above every one of them"
    if fig < min(vals):
        return "below every one of them"
    return "inside their range"


def _leg_sentence(leg, what):
    """The range of the re-draws first, then this run's own draw and where it fell (advisor chase
    of 26 Oct, 19:30: "+£11,345" stood alone above re-draws of £4,722 to £7,846, and the level
    leg's -£6,101 sat below re-draws that are all positive). The point estimate never stands
    alone, and the reason a run's draw falls outside its family is not in the feed, so the page
    does not offer one."""
    fig = leg.get("figure_gbp") or 0
    st = (leg or {}).get("verdict_stability") or {}
    vals = [v for v in st.get("redraw_values_gbp") or [] if isinstance(v, (int, float))]
    if not st.get("checked") or not vals:
        return "{} was worth <strong>{}</strong> in this run's one draw, and it has not been re-drawn".format(
            what, _money(fig, True))
    same = all(v != 0 and (v > 0) == (vals[0] > 0) for v in vals) and (fig > 0) == (vals[0] > 0)
    return ("{} was worth <strong>{} to {}</strong> across its {}, and {} in this run's own draw, {}{}").format(
        what, _money(min(vals), True), _money(max(vals), True), _plural(len(vals), "re-draw"),
        _money(fig, True), _where(fig, vals),
        "; every draw the same sign" if same else "; so even its sign is not settled")


def render_lead(arms):
    """The opening paragraph (steer of 26 Oct, section 3: "Lead Capabilities with its best
    result ... Use the published figures from the live data, not these numbers typed in"). Every
    figure is the value-arms feed's own; the verdict clause follows the feed's withholding."""
    cw = (arms or {}).get("current_world") or {}
    sel, lvl = cw.get("selection_leg") or {}, cw.get("level_leg") or {}
    q = ("The question this project tests is whether deciding customer by customer creates value "
         "or only moves it.")
    if not cw.get("available") or not isinstance(sel.get("figure_gbp"), (int, float)) \
            or not isinstance(lvl.get("figure_gbp"), (int, float)):
        return ('<p class="lead-p">{} The value test below has no current figure to lead with, '
                'and says why. <a href="#value-arms">The value test &darr;</a></p>').format(q)
    when = str(cw.get("generated_at") or "")[:10]
    try:
        when = " (run of {})".format(datetime.strptime(when, "%Y-%m-%d").strftime("%-d %b %Y"))
    except ValueError:
        when = ""
    withheld = sel.get("verdict_withheld_because") or lvl.get("verdict_withheld_because")
    return ('<p class="lead-p">{} On the same book, run three ways{}, per-customer choosing over '
            'flat rules {}. In money terms, the price level alone is value moved, not made: one flat '
            'margin at the level the per-customer arm charged {}. {}Both are shown, with the spread '
            'across draws, <a href="#value-arms">in the value test below</a>. Money is not the whole '
            'of value: a supplier can also save a household time, and this world does not measure '
            'time yet. Measuring it is open work.</p>').format(
                q, when, _leg_sentence(sel, "").strip(), _leg_sentence(lvl, "").strip(),
                "This page states no settled direction for either yet; the test says why. "
                if withheld else "")


def render_uc_tally(feed):
    tally = (feed.get("use_cases") or {}).get("tally") or {}
    return "".join('<div class="fig"><div class="fig-v">{}</div><div class="fig-k">{}</div></div>'
                   .format(E(str(tally.get(k, 0))), E(label)) for k, label in _UC_TALLY)


def render_use_cases(feed):
    """The register, one click down. Its status is `testable_now`, which the generator computes
    from whether every truth the item is scored against is finished, never a stored string."""
    out = []
    for g in (feed.get("use_cases") or {}).get("gates") or []:
        out.append('<div class="uc-gate">{}</div>'.format(E(g["gate"])))
        for u in g.get("items") or []:
            waits = ""
            if not u["testable_now"]:
                waits = '<div class="uc-waits">Waits on {}.</div>'.format(
                    E(u["status"][len("Waits on "):] if u["status"].startswith("Waits on ")
                      else u["status"]))
                if u.get("unmodelled"):
                    waits += '<div class="uc-waits uc-none">No work is under way on {}.</div>'.format(
                        E("; ".join(u["unmodelled"])))
            out.append(
                '<div class="uc{}"><div class="item-h">{}<span class="pill {}">{}</span>'
                '<span class="uc-met">{} of {} in place</span></div><div class="item-p">{}</div>'
                '<div class="uc-test"><b>Scored against:</b> {}</div>{}</div>'.format(
                    " uc-testable" if u["testable_now"] else "", E(u["name"]),
                    "pill-testable" if u["testable_now"] else "pill-waits",
                    "Testable now" if u["testable_now"] else "Waits",
                    E(str(u["needs_met"])), E(str(u["needs_total"])), E(u["what"]),
                    E(u["test"]), waits))
    return "\n".join(out)


def use_case_count(feed):
    return sum(len(g.get("items") or []) for g in (feed.get("use_cases") or {}).get("gates") or [])


def render_stamp(feed):
    return ('<span id="stamp">Generated {} at commit <code>{}</code>, from the project&#x27;s own '
            'work record and the boundary walker.</span>').format(
                E(feed.get("generated_at") or "at an unknown time"),
                E(str(feed.get("git_commit") or "unknown")[:9]))


def render_blocks(feed, arms=None):
    go_live = feed.get("go_live") or {}
    return {"LEAD": render_lead(arms),
            "FIXED": render_fixed(feed),
            "WORLD": render_side(feed.get("world") or {}),
            "SUPPLIER": render_side(feed.get("supplier") or {}),
            "ACCESS": render_access(go_live),
            "GOLIVE": render_golive(go_live),
            "UCTALLY": render_uc_tally(feed),
            "USECASES": ('<summary>What this world is for: {} things a supplier could test here'
                         '</summary>\n{}').format(use_case_count(feed), render_use_cases(feed)),
            "STAMP": render_stamp(feed)}


def block(page, name):
    """The text currently between a block's markers, or None if the page lacks them."""
    start, end = page.find(START.format(name)), page.find(END.format(name))
    if start < 0 or end < start:
        return None
    return page[start + len(START.format(name)):end].strip("\n")


def read_arms(feed_path):
    """The value-arms feed beside the capabilities feed; None (and the lead says so) if absent."""
    try:
        return json.loads((Path(feed_path).parent / "value_arms.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def write_capabilities_figures(page_path, feed_path):
    """Rewrite every block on the Capabilities page from the feed. True if all were written."""
    try:
        page = Path(page_path).read_text(encoding="utf-8")
        feed = json.loads(Path(feed_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("CAPABILITIES FIGURES NOT WRITTEN: {}".format(exc), file=sys.stderr)
        return False
    out = page
    for name, inner in render_blocks(feed, read_arms(feed_path)).items():
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
