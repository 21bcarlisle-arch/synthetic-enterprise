"""The why, kept. Commits keep what changed; this keeps the reasoning that produced it.

REUSE: tools/stretch_log.py
CLASS: CUSTOM
INDEX: searched "stretch", "report", "thesis", "direction", "delivery record", "status".
       `background/direction.py` already holds the seat's per-stretch prose (`thesis_read`) and an
       append-only `decisions.jsonl`; `tools/generate_delivery_page.py` already renders that prose
       into `site/data/delivery.json` for the director's page. Neither produces a READABLE,
       self-contained, durable document, and neither reaches `docs/`. This writes that one file and
       computes nothing either of them already computes.

WHY THIS EXISTS
---------------
Director console, 2026-09-06:

    "The prose you produce at the end of a piece of work is the most useful thing you make -- the
     corrections, the things you stopped short of, the reasoning behind a call -- and today it lives
     only in a window that gets cleared. The commits keep the what; the why is lost."

WHAT WAS ALREADY THERE, AND THE THREE GAPS. The seat writes ~3,000 characters of stretch prose into
`DIRECTION.yaml`'s `thesis_read` at every orientation, and it is committed. So the raw material
exists. What did not:

  1. It is a YAML SCALAR, not a document. Nobody reads a config field months later.
  2. It is OVERWRITTEN each orientation. Git has the history; a reader does not.
  3. It reaches `site/data/delivery.json` (Cloudflare) and never `docs/`, which is the tree the
     GitHub Pages mirror publishes and the channel the advisor actually fetches -- the director's
     own words were "somewhere my advisor reads without being told".

And a fourth the seat could never have covered: an INTERACTIVE session's reports -- the ones written
to the console at the end of a piece of work -- entered none of it.

THE TWO PROPERTIES HE ASKED FOR
-------------------------------
**A stretch that lands work without a report is a FINDING, not a refusal.** `--check` compares the
commits landed since the newest entry's recorded head against zero. A gate here would be wrong: a
report is written when a piece of work FINISHES, and refusing every commit in between would stop the
work it is meant to describe. A finding is visible and costs nothing when the machine is mid-piece.

**Each entry must be readable on its own months later.** So `append` requires a SUBJECT LINE that
names what the stretch was about, and refuses an entry that only points at conversation -- "as
discussed", "the above", "per your last" -- because a reader in six months has none of that.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
LOG = PROJECT / "docs" / "status" / "SEAT_STRETCH_LOG.md"

_HEADER = """# Delivery-seat stretch log

*What each stretch of work was about, what it got wrong, and the reasoning behind the calls made in
it. The commits record what changed; this records why. Newest first.*

*Written by `tools/stretch_log.py` as part of finishing a piece of work, not as a separate step.
A stretch that lands commits without an entry here is a finding, raised by `--check`.*

---
"""

#: An entry that leans on the conversation it was written in is unreadable later. These are the
#: phrases that do it, and they are refused in the SUBJECT rather than the body -- a body may
#: legitimately quote a console turn, a subject may not depend on one.
_CONVERSATIONAL = re.compile(
    r"\b(as (discussed|above|requested|agreed)|per (your|the) (last|previous)|the above|"
    r"as you said|continuing|carry on|keep going|following up|as before)\b", re.I)

_ENTRY_HEAD = re.compile(r"^## (\d{4}-\d{2}-\d{2}) — (.+?)\s*$", re.M)
_HEAD_STAMP = re.compile(r"^<!-- head: ([0-9a-f]{7,40}) -->\s*$", re.M)


def _git(*args: str) -> str | None:
    """Stdout on success; **None when git refused**, which is not the same as empty output.

    IT USED TO RETURN `""` FOR BOTH, and that is how this control acquired a silent green. The
    head stamp names a commit; if that commit is not reachable from this tree -- written in a
    worktree whose landing never promoted, or on a branch since rewritten -- `git log <stamp>..HEAD`
    exits 128 with "unknown revision". The old `_git` turned that into `""`, `commits_since_last_
    entry` read `""` as zero commits, and `check()` reported "up to date" forever. A control
    refusing on input it could not READ is one thing; this one did not refuse, it AGREED.
    """
    done = subprocess.run(("git", *args), cwd=str(PROJECT),
                          capture_output=True, text=True, timeout=60)
    return done.stdout.strip() if done.returncode == 0 else None


class StampUnreachable(RuntimeError):
    """The newest entry's head stamp names a commit this tree cannot resolve."""


def newest_entry_head() -> str | None:
    """The commit the newest entry was written at, or None if the log has no entries."""
    if not LOG.is_file():
        return None
    m = _HEAD_STAMP.search(LOG.read_text(encoding="utf-8", errors="replace"))
    return m.group(1) if m else None


def commits_since_last_entry() -> tuple[int, list[str]]:
    """(count, subjects) of commits landed since the newest entry's head.

    MERGES AND THE LOG'S OWN COMMIT ARE EXCLUDED. A merge lands no reasoning of its own, and
    counting the commit that WRITES the report would mean the log could never be up to date --
    a control that can only ever be red.
    """
    head = newest_entry_head()
    if head is None:
        return 0, []
    rng = f"{head}..HEAD"
    out = _git("log", rng, "--no-merges", "--format=%h %s")
    if out is None:
        raise StampUnreachable(
            f"the newest entry's head stamp {head} is not reachable from this tree, so the "
            "number of commits since the last report is UNMEASURABLE. Nothing is up to date; "
            "the measurement is missing.")
    lines = [ln for ln in out.splitlines() if ln.strip()]

    # EXCLUDE COMMITS THAT TOUCH THE LOG ITSELF, by PATH and not by title. The first version
    # filtered subjects containing "stretch log", and its own landing commit -- "the why, kept:
    # stretch reports land in a committed file..." -- said "stretch reports" and slipped through,
    # so the log reported itself as unreported the moment it shipped. A grep for a concept's NAME
    # is blind to the thing itself; the path cannot be dodged by phrasing.
    rel = str(LOG.relative_to(PROJECT)) if LOG.is_absolute() else str(LOG)
    own_out = _git("log", rng, "--format=%h", "--", rel)
    if own_out is None:
        raise StampUnreachable(
            f"the head stamp {head} resolved for the range query and not for the path-restricted "
            "one, so which commits are the log's OWN cannot be determined.")
    own = {ln.split()[0] for ln in own_out.splitlines() if ln.strip()}
    lines = [ln for ln in lines if ln.split()[0] not in own]
    return len(lines), lines


def validate_subject(subject: str) -> str | None:
    """None if the subject stands alone; otherwise why it does not."""
    if len(subject.strip()) < 25:
        return ("the subject is too short to say what the stretch was about -- a reader in six "
                "months has only this line to go on")
    m = _CONVERSATIONAL.search(subject)
    if m:
        return (f"the subject leans on the conversation it was written in ({m.group(0)!r}). "
                "Name the subject instead: what was this stretch ABOUT?")
    return None


def append(subject: str, body: str, at_head: str | None = None) -> Path:
    """Prepend one self-contained entry. Raises ValueError if the subject cannot stand alone."""
    bad = validate_subject(subject)
    if bad:
        raise ValueError(bad)
    head = at_head or _git("rev-parse", "HEAD") or "0" * 40
    today = dt.date.today().isoformat()
    entry = f"## {today} — {subject.strip()}\n\n<!-- head: {head[:12]} -->\n\n{body.strip()}\n\n---\n"

    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.is_file():
        LOG.write_text(_HEADER + "\n" + entry, encoding="utf-8")
        return LOG
    existing = LOG.read_text(encoding="utf-8", errors="replace")
    marker = "---\n"
    i = existing.index(marker) + len(marker)
    LOG.write_text(existing[:i] + "\n" + entry + existing[i:], encoding="utf-8")
    return LOG


#: WHEN AN OWED REPORT STOPS BEING ORDINARY AND BECOMES A FINDING THAT PAGES.
#:
#: The check has fired on EVERY publish cycle since the last entry -- 75 times between 2026-09-07
#: and 2026-09-10 -- into `docs/observability/sim-runner-log.md`, which is 250,000 lines long. It
#: never stopped. It was never read. So the threshold is not "is a report owed" (that is true most
#: of the time, correctly, because a report is written when a piece of work FINISHES) but "is this
#: gap unlike any gap this log has ever had".
#:
#: MEASURED AGAINST THE LOG'S OWN HISTORY, not chosen. The eleven stamped entries give ten gaps:
#: 1, 2, 2, 5, 8, 9, 20, 29, 37, 70 commits; median 8.5, max 70. In time, the largest gap between
#: consecutive entries was 16.7h (2026-09-06 18:02 -> 2026-09-07 10:42).
#:
#: So both legs sit ABOVE everything the log has ever done and neither would have fired on any
#: historical stretch: 24h (max observed 16.7h) and 80 commits (max observed 70). The gap that
#: prompted this was 253 commits over 68h -- 3.6x the largest count and 4x the longest silence.
#: OR, not AND: a machine that lands nothing for three days owes a report as much as one that
#: lands three hundred commits in an afternoon.
ESCALATE_AFTER_HOURS = 24.0
ESCALATE_AFTER_COMMITS = 80


def _entry_epoch(head: str) -> float | None:
    """Committer epoch of the commit the newest entry was written at, or None if unreadable."""
    out = _git("log", "-1", "--format=%ct", head)
    if not out:
        return None
    try:
        return float(out.split()[0])
    except (ValueError, IndexError):
        return None


def owed(now: float | None = None) -> dict:
    """The structured verdict: is a report owed, and is the gap bad enough to PAGE about it?

    `escalate` is what the caller raises an alarm on. `reason` names which leg carried it, because
    a page that does not say whether it is about a THREE-DAY SILENCE or a THREE-HUNDRED-COMMIT
    stretch tells the reader nothing they can act on.

    UNMEASURABLE IS ESCALATED, never quiet. A missing log, a missing stamp and an unreachable stamp
    all mean the same thing -- nobody can say whether a report is owed -- and the whole class of
    defect this file has been carrying is a control that answers "fine" when it means "I could not
    look".
    """
    now = time.time() if now is None else now
    if not LOG.is_file():
        return {"owed": True, "escalate": True, "commits": None, "hours": None,
                "reason": "the log file does not exist"}
    head = newest_entry_head()
    if head is None:
        return {"owed": True, "escalate": True, "commits": None, "hours": None,
                "reason": "the newest entry carries no head stamp"}
    try:
        n, _ = commits_since_last_entry()
    except StampUnreachable as exc:
        return {"owed": True, "escalate": True, "commits": None, "hours": None,
                "reason": f"the head stamp is unreachable: {exc}"}

    epoch = _entry_epoch(head)
    hours = None if epoch is None else max(0.0, (now - epoch) / 3600.0)
    if n == 0:
        return {"owed": False, "escalate": False, "commits": 0, "hours": hours,
                "reason": "up to date"}

    legs = []
    if hours is None:
        legs.append("the age of the last report is unreadable")
    elif hours > ESCALATE_AFTER_HOURS:
        legs.append(f"{hours:.0f}h since the last report (escalates above "
                    f"{ESCALATE_AFTER_HOURS:.0f}h; longest gap this log has ever had is 16.7h)")
    if n > ESCALATE_AFTER_COMMITS:
        legs.append(f"{n} commits since the last report (escalates above {ESCALATE_AFTER_COMMITS}; "
                    "largest gap this log has ever had is 70)")
    return {"owed": True, "escalate": bool(legs), "commits": n, "hours": hours,
            "reason": "; and ".join(legs) if legs
                      else f"{n} commit(s) owed, inside the ordinary range for this log"}


def alarm_message(verdict: dict | None = None) -> str:
    """The page text. STABLE PROSE ON PURPOSE -- the commit LISTING is deliberately absent.

    `alarm_repetition.normalise()` strips numbers and timestamps out of an alarm's identity but not
    prose, so a message carrying twelve rotating commit subjects would be a NEW condition every
    publish cycle: a fresh escalation document each time, and 28 documents standing for one
    condition. The listing belongs in `check()`, which the run log keeps; the page carries the
    condition and where to read the rest.
    """
    v = verdict or owed()
    return ("[stretch-log] NO STRETCH REPORT for work that has landed -- " + v["reason"] + ". "
            "The commits keep WHAT changed; nothing is keeping WHY. "
            "Read the owed list with `python3 tools/stretch_log.py --check`, then write one with "
            "`--append '<subject>' --body-file <path>`.")


def check() -> tuple[int, str]:
    """(rc, message). rc 1 when work has landed with no entry describing it."""
    if not LOG.is_file():
        return 1, ("[stretch-log] no log exists yet: docs/status/SEAT_STRETCH_LOG.md.\n"
                   "The reasoning behind every landing so far is in console scrollback only.")
    if newest_entry_head() is None:
        return 1, "[stretch-log] the newest entry carries no head stamp, so staleness is unmeasurable."
    try:
        n, subjects = commits_since_last_entry()
    except StampUnreachable as exc:
        return 1, f"[stretch-log] {exc}"
    if n == 0:
        return 0, "[stretch-log] up to date."
    listing = "\n".join(f"    {s}" for s in subjects[:12])
    more = f"\n    ... and {n - 12} more" if n > 12 else ""
    return 1, (
        f"[stretch-log] {n} commit(s) have landed since the last stretch report:\n{listing}{more}\n"
        "The commits keep WHAT changed. Nothing keeps WHY -- the corrections, what was stopped "
        "short of, the reasoning behind a call.\n"
        "Write one: `python3 tools/stretch_log.py --append '<subject>' --body-file <path>`"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--append", metavar="SUBJECT", help="prepend an entry with this subject")
    ap.add_argument("--body-file", help="file holding the entry body (use - for stdin)")
    ap.add_argument("--check", action="store_true", help="rc 1 if work landed with no report")
    args = ap.parse_args(argv)

    if args.append:
        if not args.body_file:
            print("[stretch-log] --append needs --body-file", file=sys.stderr)
            return 2
        body = sys.stdin.read() if args.body_file == "-" else Path(args.body_file).read_text()
        try:
            path = append(args.append, body)
        except ValueError as exc:
            print(f"[stretch-log] REFUSED: {exc}", file=sys.stderr)
            return 1
        print(f"[stretch-log] appended to {path.relative_to(PROJECT)}")
        return 0

    rc, msg = check()
    v = owed()
    if v["escalate"]:
        # Printed with the listing, not instead of it: the listing says what the report is owed
        # ABOUT, this line says why it has stopped being an ordinary between-pieces gap.
        msg += f"\n[stretch-log] ESCALATED -- {v['reason']}"
    print(msg, file=sys.stderr if rc else sys.stdout)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
