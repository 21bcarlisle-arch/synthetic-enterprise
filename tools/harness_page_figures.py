"""How it's built: the scale of the build and last week's highlights, written into the page at publish.

Director, 23 Oct 2026 07:18 (advisor channel, DIRECTOR_STEER_THE_OTHER_PAGES_MATCH_THE_FRONT_DOOR,
item 4): "Make more appropriate for energy or tech person who is not familiar with the detail".
The page opens with the build's scale and a week's highlights. Both are written between markers by
`tools/generate_dashboard_data.py` at the weekly publish, the same way the front door's build strip
is, so a reader without JavaScript sees them and no figure is typed by hand.

Every figure says what it counts and carries its own clock. One the steer asks for has no store
behind it -- the share of changes that passed the gates first time, because a refused gate run
leaves no record -- so the strip says that in words rather than printing a number.

Each of the stack's eight layers also carries its own evidence (director, 23 Oct 09:20, advisor
channel, DIRECTOR_STEER_SHOW_THE_HARNESS_AS_A_LIVE_CONTROL_STACK): how often it fired in the thirty
days to the published commit, when it last fired, and whether a test naming its code records a
mutation. Each layer is read from the one store that already records it, and the box names the
store's unit, because a refused publisher commit, a failed publish run and a new test file are not
the same thing counted. Most of the checks keep no record of a refusal. Those boxes say so, rather
than print a count of nothing.
"""
from __future__ import annotations

import ast
import html
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

from tools.generate_dashboard_data import _day, _git_out
from tools.python_code_text import searchable

SCALE_START = ("<!-- HARNESS-SCALE:START (written at publish by "
               "tools/harness_page_figures.py -- do not hand-edit) -->")
SCALE_END = "<!-- HARNESS-SCALE:END -->"
WEEK_START = ("<!-- HARNESS-WEEK:START (written at publish by "
              "tools/harness_page_figures.py -- do not hand-edit) -->")
WEEK_END = "<!-- HARNESS-WEEK:END -->"
LAYER_START = ("<!-- HARNESS-LAYER-{}:START (written at publish by "
               "tools/harness_page_figures.py -- do not hand-edit) -->")
LAYER_END = "<!-- HARNESS-LAYER-{}:END -->"

# The steer's own window: "how often the layer refused or caught something in the last 30 days".
WINDOW_DAYS = 30
# The project's convention for a test that has been seen to fail: its docstring names the
# MUTATION that put its defect back. The lower-case word is prose about mutation in general.
_MUTATION = re.compile(r"\bMUTATIONS?\b")

# The steer's own range: "five to eight highlights".
MOST_HIGHLIGHTS = 8
# A headline longer than this is a run-on list of findings, not a line a newcomer reads.
LONGEST_HEADLINE = 90

# A refusing gate in a hook is a line that runs a check and stops the commit when it fails.
_GATE_LINE = re.compile(r"^\s*python3\s+\S.*\|\|\s*(exit 1|\{)")
_ENTRY = re.compile(r"^## (\d{4}-\d{2}-\d{2}) — (.+)$")
_PLAIN = re.compile(r"^\*\*In plain English:\*\*\s*(.+)$")


def count_hook_gates(root):
    """{hook name: number of refusing checks it runs}, read from the hook files as committed at
    HEAD -- the commit being published, which is what the figure's clock names; None if unreadable."""
    out = {}
    for name in ("pre-commit", "commit-msg"):
        text = _git_out(root, "show", "HEAD:tools/git-hooks/{}".format(name))
        if text is None:
            return None
        out[name] = sum(1 for line in text.splitlines() if _GATE_LINE.match(line))
    return out


def weekly_commits(root):
    """[(monday iso, commits that week)] from the first commit's week to HEAD's, or None."""
    days = _git_out(root, "log", "--format=%cs", "HEAD")
    if not days:
        return None
    counts = {}
    for d in days.split():
        try:
            day = date.fromisoformat(d)
        except ValueError:
            continue
        monday = day - timedelta(days=day.weekday())
        counts[monday] = counts.get(monday, 0) + 1
    if not counts:
        return None
    week, last, weeks = min(counts), max(counts), []
    while week <= last:
        weeks.append((week.isoformat(), counts.get(week, 0)))
        week += timedelta(days=7)
    return weeks


def scale_figures(root, proof):
    """([(value, label, what it counts and its clock)], [(monday, commits)], [left out, and why])."""
    figures, missing = [], []
    head = (_git_out(root, "rev-parse", "--short=9", "HEAD") or "").strip()
    when = (_git_out(root, "log", "-1", "--format=%cs", "HEAD") or "").strip()
    clock = "counted from git at {}, {}".format(head, _day(when)) if head and when else None
    week = (_git_out(root, "rev-list", "--count", "--since=7 days ago", "HEAD") or "").strip()
    if clock and week.isdigit():
        figures.append(("{:,}".format(int(week)), "commits landed in the last seven days",
                        "about {:,} a day; {}".format(
                            round(int(week) / 7), clock)))
    else:
        missing.append("the week's commit count (git could not be read)")
    files = _git_out(root, "ls-files", "-z")
    if clock and files is not None:
        py = [f for f in files.split("\0") if f.endswith(".py")]
        tests = [f for f in py if f.rsplit("/", 1)[-1].startswith("test_")]
        figures.append(("{:,}".format(len(tests)), "test files",
                        "of {:,} Python files in all; {}".format(len(py), clock)))
    else:
        missing.append("the test-file count (git could not be read)")
    gates = count_hook_gates(root)
    if gates:
        figures.append(("{:,}".format(sum(gates.values())), "checks every commit must pass",
                        "{} before the commit is written and {} on its message, counted from the "
                        "hook files at {}".format(gates["pre-commit"], gates["commit-msg"],
                                                  head or "HEAD")))
    else:
        missing.append("the gate count (the hook files could not be read)")
    # Proven able to fail is counted over the tests, where the controls now live, not over the
    # 35-row register graded in July (docs/staging finding of 23 Oct); the register is named
    # beside it so the older figure is not lost.
    marked, n_tests = _mutation_index(root)
    kill = (proof or {}).get("control_killlist") or {}
    if clock and marked is not None and n_tests:
        register = ("; the older hand-kept register holds {:,} of {:,}, last graded {}".format(
            kill["mutation_proven"], kill["controls_total"],
            _day(kill.get("last_verified") or "on an unrecorded day"))
            if kill.get("available") and kill.get("controls_total") else "")
        figures.append(("{:,}".format(len(marked)), "tests proven able to fail",
                        "test files that record the mutation they were seen to fail on, of {:,}; "
                        "{}{}".format(n_tests, clock, register)))
    else:
        missing.append("the tests proven able to fail (git could not be read)")
    # Named rather than printed: no store records a gate run that refused.
    missing.append("the share of changes that passed the gates first time (a refused gate run "
                   "leaves no record, so this is not measured yet)")
    return figures, weekly_commits(root), missing


def render_timeline(weeks):
    """One single-series bar chart of commits per week, as static SVG, with its table."""
    if not weeks:
        return '<p class="sub">The weekly timeline could not be counted from git.</p>'
    top = max(c for _, c in weeks) or 1
    w, h, gap = 640, 120, 2
    bw = (w - gap * (len(weeks) - 1)) / len(weeks)
    bars = []
    for i, (monday, c) in enumerate(weeks):
        bh = max(1.0, h * c / top) if c else 0
        bars.append('<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" rx="2">'
                    '<title>Week of {}: {:,} commits</title></rect>'.format(
                        i * (bw + gap), h - bh, bw, bh, _day(monday), c))
    rows = "".join("<tr><td>{}</td><td>{:,}</td></tr>".format(_day(m), c) for m, c in weeks)
    return ('<figure class="timeline"><figcaption>Commits per week since the repository began'
            '</figcaption><svg viewBox="0 0 {w} {h}" role="img" aria-label="Commits per week, '
            '{a} to {b}, peaking at {top:,}" preserveAspectRatio="none">{bars}</svg>'
            '<div class="tl-axis"><span>{a}</span><span>busiest week: {top:,}</span>'
            '<span>{b}</span></div><details><summary>The same figures as a table</summary>'
            '<div class="table-scroll"><table><thead><tr><th>Week of</th><th>Commits</th></tr>'
            '</thead><tbody>{rows}</tbody></table></div></details></figure>').format(
                w=w, h=h, bars="".join(bars), rows=rows, top=top,
                a=_day(weeks[0][0]), b=_day(weeks[-1][0]))


def week_highlights(root, *, today=None):
    """[(day, headline)]: the stretch log's work entries from the seven days to HEAD's date.

    The seat's own orientation entries are left out: they read the week rather than do it. An
    entry that carries an `**In plain English:**` line is shown by that line, which its writer
    wrote for a newcomer. Otherwise its headline is the title up to its first semicolon, where the
    log's titles end the statement of what landed; a longer one is a run-on list of findings and
    is skipped, and so is a later entry on the same subject (its first two words)."""
    try:
        text = (Path(root) / "docs" / "status" / "SEAT_STRETCH_LOG.md").read_text(encoding="utf-8")
    except OSError:
        return None
    if today is None:
        when = (_git_out(root, "log", "-1", "--format=%cs", "HEAD") or "").strip()
        try:
            today = date.fromisoformat(when)
        except ValueError:
            return None
    since = today - timedelta(days=7)
    entries, current = [], None
    for line in text.splitlines():
        m = _ENTRY.match(line)
        if m:
            current = [m.group(1), re.sub(r"^\d{4}-\d{2}-\d{2} — ", "", m.group(2)), None]
            entries.append(current)
        elif current is not None and current[2] is None:
            p = _PLAIN.match(line)
            if p:
                current[2] = p.group(1).strip()
    seen, out = set(), []
    for day, title, plain in entries:
        if title.lower().startswith("orientation"):
            continue
        try:
            if date.fromisoformat(day) <= since:
                continue
        except ValueError:
            continue
        headline = plain or title.split(";")[0].strip().rstrip(":,")
        subject = " ".join(re.findall(r"[a-z0-9']+", headline.lower())[:2])
        if (not plain and len(headline) > LONGEST_HEADLINE) or subject in seen:
            continue
        seen.add(subject)
        out.append((day, headline[0].upper() + headline[1:]))
        if len(out) >= MOST_HIGHLIGHTS:
            break
    return out


def _jsonl(path):
    """The rows of a JSON-lines store, or None if it cannot be read; a torn line is skipped."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    rows = []
    for line in lines:
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return [r for r in rows if isinstance(r, dict)]


def _store_firings(rows, stamp, fired, since):
    """(fired in the window, of how many rows in the window, last day fired) over one store."""
    days = [(str(r.get(stamp) or "")[:10], fired(r)) for r in rows]
    window = [f for d, f in days if d >= since]
    last = max((d for d, f in days if f and d), default=None)
    return sum(window), len(window), last


def _mutation_marker(tree):
    """Does a docstring or other string in this parsed test record a MUTATION?

    Comments are not read: the census of source scans refuses a regex over raw text, and 34 test
    files that carry the marker only in a comment go uncounted, which errs low."""
    return any(isinstance(n, ast.Constant) and isinstance(n.value, str)
               and _MUTATION.search(n.value) for n in ast.walk(tree))


def _mutation_index(root):
    """{test path: its code, prose blanked} for every tracked test file that records a MUTATION,
    and the number of test files. The marker is read from the prose, where the convention puts
    it (its strings); which code a test names is read from its code, so a docstring that mentions a module does
    not make the test that module's."""
    files = _git_out(root, "ls-files", "-z")
    if files is None:
        return None, 0
    tests = [f for f in files.split("\0")
             if f.endswith(".py") and f.rsplit("/", 1)[-1].startswith("test_")]
    marked = {}
    for f in tests:
        try:
            source = (Path(root) / f).read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError, ValueError):
            continue
        if _mutation_marker(tree):
            marked[f] = searchable(source)
    return marked, len(tests)


def _added_since(root, since):
    """{path: day first added} for files added to HEAD's history on or after `since`."""
    out = _git_out(root, "log", "--diff-filter=A", "--name-only", "--format=%x00%cs",
                   "--since={}".format(since), "HEAD")
    added = {}
    for block in (out or "").split("\0")[1:]:
        lines = block.strip().splitlines()
        for f in lines[1:]:
            added.setdefault(f.strip(), lines[0].strip())
    return added


#: (layer, the code a test must name to count as this layer's, how its firings are read).
#: The stems are the files each box names as holding it.
LAYER_CODE = {
    1: ("one_way_door", "advisor_channel", "director_document_gate"),
    2: ("domain_constant_origins", "test_a_domain_constant_carries_its_origin",
        "knowledge_layer_gate"),
    3: ("sim_interface", "company_network_isolation", "lane_hook"),
    4: ("git-hooks", "time_the_commit_hook_chain"),
    5: (),
    6: ("phase-close-evaluator", "cold-eyes-walk", "cold_eyes", "blind_review"),
    7: ("assert_deployed_bytes_are_served", "world_claims", "canon_drift_check"),
    8: ("finding_classes", "weekly_rhythm"),
}


def layer_evidence(root, obs_dir=None):
    """{layer: [(label, value)]}: each box's firings, last firing and its tests, or why not.

    `obs_dir` is where the stores outside git live (the shared tree's docs/observability)."""
    obs = Path(obs_dir) if obs_dir else Path(root) / "docs" / "observability"
    when = (_git_out(root, "log", "-1", "--format=%cs", "HEAD") or "").strip()
    try:
        end = date.fromisoformat(when)
    except ValueError:
        return {n: [("Evidence", "not measured yet: git could not be read")] for n in LAYER_CODE}
    since = (end - timedelta(days=WINDOW_DAYS)).isoformat()
    marked, n_tests = _mutation_index(root)
    marked = marked or {}
    out = {}

    def fired(n, text, label="Fired"):
        out.setdefault(n, []).append(("{}, last {} days".format(label, WINDOW_DAYS), text))

    def git_firings(pattern, grep_body):
        log = _git_out(root, "log", "--format=%x00%cs%x01%B", "HEAD") or ""
        days = [b.split("\x01", 1)[0] for b in log.split("\0")[1:]
                if re.search(pattern, b.split("\x01", 1)[-1] if grep_body else "", re.M)]
        return sum(1 for d in days if d >= since), max(days, default=None)

    # 1. Direction: the director-document gate refuses a change to his documents unless the
    # commit carries a marked reason, so every marked commit is one the gate held.
    n, last = git_firings(r"^Director-doc:", True)
    fired(1, "{:,} commits changed a director document and carried the marked reason the gate "
             "demands; last {}. A refused one leaves no record.".format(n, _day(last or "never")))
    # 2. Knowledge: a new research document is refused unless it says which knowledge page it
    # feeds, so each one added is one the gate read.
    added = _added_since(root, since)
    research = {f: d for f, d in added.items()
                if f.startswith("docs/market_research/") and f.endswith(".md")}
    fired(2, "{:,} sourced research documents added, each refused unless it names the knowledge "
             "page it feeds; last {}. A refused one leaves no record.".format(
                 len(research), _day(max(research.values(), default="never"))))
    # 3. The walls: the network wall refuses by construction and leaves nothing to count; the
    # lane hook logs each tool call it denies.
    rows = _jsonl(obs / "lane_hook_denials.jsonl")
    if rows is None:
        fired(3, "not measured yet: the lane-hook denial log is not on this machine.")
    else:
        k, _, last = _store_firings(rows, "timestamp", lambda r: 1, since)
        fired(3, "{:,} tool calls denied for reaching across the wall; last {}. The network "
                 "wall refuses by construction and leaves nothing to count.".format(
                     k, _day(last or "never")))
    # 4. The commit gate: only the publisher records its gate's outcome, per commit attempt.
    rows = _jsonl(obs / "commit_hook_duration.jsonl")
    if rows is None:
        fired(4, "not measured yet: the publisher's gate log is not on this machine.")
    else:
        k, m, last = _store_firings(rows, "timestamp",
                                    lambda r: int(r.get("outcome") == "refused"), since)
        fired(4, "{:,} of the publisher's {:,} commit attempts refused; last {}. Only the "
                 "publisher logs its gate, so other agents' refusals are not counted.".format(
                     k, m, _day(last or "never")))
    # 5. Proof: defined over the tests, not the hand-kept register.
    if n_tests:
        new = sorted(d for f, d in added.items() if f in marked)
        fired(5, "{:,} of {:,} test files record the mutation they were seen to fail on; {:,} of "
                 "them added in the window, the last {}.".format(
                     len(marked), n_tests, len(new), _day(new[-1] if new else "never")),
             label="Counted")
    else:
        fired(5, "not measured yet: git could not be read.")
    # 6. Independent judgement: each blind review is written to its ledger.
    rows = _jsonl(obs / "blind_review_ledger.jsonl")
    if rows is None:
        fired(6, "not measured yet: the blind-review ledger is not on this machine.")
    else:
        k, _, last = _store_firings(rows, "recorded_at", lambda r: 1, since)
        fired(6, "{:,} blind reviews recorded; last {}.".format(k, _day(last or "never")))
    # 7. The published state: each run of the publish gate logs its outcome.
    rows = _jsonl(obs / "publish_gate_duration.jsonl")
    if rows is None:
        fired(7, "not measured yet: the publish gate's log is not on this machine.")
    else:
        k, m, last = _store_firings(rows, "timestamp",
                                    lambda r: int(r.get("outcome") == "fail"), since)
        fired(7, "{:,} of {:,} publish gate runs stopped a publish; last {}.".format(
            k, m, _day(last or "never")))
    # 8. Learning: a recurring defect becomes a registered class, dated in the register.
    try:
        from background.finding_classes import CLASSES
        days = [c.registered for c in CLASSES if getattr(c, "registered", None)]
        fired(8, "{:,} new classes of mistake registered, of {:,} in the register; last {}."
              .format(sum(1 for d in days if d >= since), len(days),
                      _day(max(days, default="never"))))
    except Exception:  # noqa: BLE001 -- a register that will not import is a box that says so
        fired(8, "not measured yet: the register of mistake classes could not be read.")
    for n, stems in LAYER_CODE.items():
        if n == 5:
            continue
        k = sum(1 for text in marked.values() if any(s in text for s in stems))
        out[n].append(("Shown able to fail",
                       "{:,} tests that name this layer's code record a mutation".format(k)
                       if k else "no test that names this layer's code records a mutation yet"))
    return out


def render_layer(rows):
    return '<span class="ev">{}</span>'.format("".join(
        '<span><b>{}:</b> {}</span>'.format(html.escape(lab), html.escape(val))
        for lab, val in rows))


def _replace(page, start_marker, end_marker, inner):
    start, end = page.find(start_marker), page.find(end_marker)
    if start < 0 or end < start:
        return None
    return page[:start] + start_marker + "\n" + inner + "\n" + page[end:]


def write_harness_figures(harness_path, proof_path, obs_dir=None):
    """Rewrite every block in the How it's built page. True if all were written."""
    try:
        page = Path(harness_path).read_text(encoding="utf-8")
    except OSError:
        return False
    try:
        proof = json.loads(Path(proof_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        proof = {}
    root = Path(harness_path).resolve().parent.parent.parent
    figures, weeks, missing = scale_figures(root, proof)
    cells = "\n".join(
        '  <div class="lf"><div class="v">{}</div><div class="l">{}</div>'
        '<div class="c">{}</div></div>'.format(html.escape(v), html.escape(lab), html.escape(c))
        for v, lab, c in figures)
    scale = '<div class="lf-row">\n{}\n</div>\n{}{}'.format(
        cells, render_timeline(weeks),
        '\n<p class="lf-prov">Not shown: {}.</p>'.format(html.escape("; ".join(missing)))
        if missing else "")
    highlights = week_highlights(root)
    if highlights:
        week = '<ul class="week">\n{}\n</ul>'.format("\n".join(
            '  <li><span class="wd">{}</span> {}</li>'.format(html.escape(_day(d)), html.escape(t))
            for d, t in highlights))
    else:
        week = ('<p class="sub">The stretch log could not be read, or holds no work entry in the '
                'seven days to this publish, so no highlight is shown.</p>')
    out = _replace(page, SCALE_START, SCALE_END, scale)
    out = out and _replace(out, WEEK_START, WEEK_END, week)
    for n, rows in layer_evidence(root, obs_dir).items():
        out = out and _replace(out, LAYER_START.format(n), LAYER_END.format(n), render_layer(rows))
    if out is None:
        print("HOW IT'S BUILT FIGURES NOT WRITTEN: {} does not carry every pair of markers".format(
            harness_path), file=sys.stderr)
        return False
    Path(harness_path).write_text(out, encoding="utf-8")
    return True


if __name__ == "__main__":
    site = Path(__file__).resolve().parent.parent / "site"
    sys.exit(0 if write_harness_figures(site / "harness" / "index.html",
                                        site / "data" / "proof.json") else 1)
