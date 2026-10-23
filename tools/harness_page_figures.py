"""How it's built: the scale of the build and last week's highlights, written into the page at publish.

Director, 23 Oct 2026 07:18 (advisor channel, DIRECTOR_STEER_THE_OTHER_PAGES_MATCH_THE_FRONT_DOOR,
item 4): "Make more appropriate for energy or tech person who is not familiar with the detail".
The page opens with the build's scale and a week's highlights. Both are written between markers by
`tools/generate_dashboard_data.py` at the weekly publish, the same way the front door's build strip
is, so a reader without JavaScript sees them and no figure is typed by hand.

Every figure says what it counts and carries its own clock. One the steer asks for has no store
behind it -- the share of changes that passed the gates first time, because a refused gate run
leaves no record -- so the strip says that in words rather than printing a number.
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

from tools.generate_dashboard_data import _day, _git_out

SCALE_START = ("<!-- HARNESS-SCALE:START (written at publish by "
               "tools/harness_page_figures.py -- do not hand-edit) -->")
SCALE_END = "<!-- HARNESS-SCALE:END -->"
WEEK_START = ("<!-- HARNESS-WEEK:START (written at publish by "
              "tools/harness_page_figures.py -- do not hand-edit) -->")
WEEK_END = "<!-- HARNESS-WEEK:END -->"

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
    kill = (proof or {}).get("control_killlist") or {}
    if kill.get("available") and kill.get("controls_total"):
        figures.append(("{:,} of {:,}".format(kill["mutation_proven"], kill["controls_total"]),
                        "registered controls proven able to fail",
                        "each shown firing by putting its own defect back; the register was last "
                        "graded {}".format(_day(kill.get("last_verified") or "on an unrecorded day"))))
    else:
        missing.append("the controls proven able to fail (the control register could not be read)")
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


def _replace(page, start_marker, end_marker, inner):
    start, end = page.find(start_marker), page.find(end_marker)
    if start < 0 or end < start:
        return None
    return page[:start] + start_marker + "\n" + inner + "\n" + page[end:]


def write_harness_figures(harness_path, proof_path):
    """Rewrite both blocks in the How it's built page. True if both were written."""
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
    if out is None:
        print("HOW IT'S BUILT FIGURES NOT WRITTEN: {} does not carry both pairs of markers".format(
            harness_path), file=sys.stderr)
        return False
    Path(harness_path).write_text(out, encoding="utf-8")
    return True


if __name__ == "__main__":
    site = Path(__file__).resolve().parent.parent / "site"
    sys.exit(0 if write_harness_figures(site / "harness" / "index.html",
                                        site / "data" / "proof.json") else 1)
