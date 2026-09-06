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


def _git(*args: str) -> str:
    done = subprocess.run(("git", *args), cwd=str(PROJECT),
                          capture_output=True, text=True, timeout=60)
    return done.stdout.strip() if done.returncode == 0 else ""


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
    lines = [ln for ln in out.splitlines() if ln.strip()]

    # EXCLUDE COMMITS THAT TOUCH THE LOG ITSELF, by PATH and not by title. The first version
    # filtered subjects containing "stretch log", and its own landing commit -- "the why, kept:
    # stretch reports land in a committed file..." -- said "stretch reports" and slipped through,
    # so the log reported itself as unreported the moment it shipped. A grep for a concept's NAME
    # is blind to the thing itself; the path cannot be dodged by phrasing.
    rel = str(LOG.relative_to(PROJECT)) if LOG.is_absolute() else str(LOG)
    own = {ln.split()[0] for ln in _git("log", rng, "--format=%h", "--", rel).splitlines() if ln.strip()}
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


def check() -> tuple[int, str]:
    """(rc, message). rc 1 when work has landed with no entry describing it."""
    if not LOG.is_file():
        return 1, ("[stretch-log] no log exists yet: docs/status/SEAT_STRETCH_LOG.md.\n"
                   "The reasoning behind every landing so far is in console scrollback only.")
    n, subjects = commits_since_last_entry()
    if newest_entry_head() is None:
        return 1, "[stretch-log] the newest entry carries no head stamp, so staleness is unmeasurable."
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
    print(msg, file=sys.stderr if rc else sys.stdout)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
