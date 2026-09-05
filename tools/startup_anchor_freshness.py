"""The startup surface must carry its own COMPUTED age, so it can be stale but never silently so.

REUSE: tools/startup_anchor_freshness.py
CLASS: CUSTOM
INDEX: searched "freshness", "stale", "anchor", "startup", "last updated". The near rows are
       `tools/assert_deployed_bytes_are_served.py` (asserts the EDGE serves the commit just
       deployed -- a transport check, and it passes here) and `tools/publish_surface_gate.py`
       (gates whether a publish's FIGURES are right). Neither asks the question this one asks:
       whether a document's own claim about its age agrees with its age. That question has no
       existing home, and the incident below is what happens without one.

WHY THIS EXISTS -- and the answer was neither of the two candidates
------------------------------------------------------------------
Director console, 2026-09-05: another session's startup read PROJECT_OVERVIEW.md, LATEST.md and
ASSUMPTIONS.md from the published Pages URLs "and found them dated 3-10 August", against an origin
whose LATEST.md had been written at 07:06Z that morning. Two hypotheses were offered: the anchor is
stale at the edge, or the files have moved since the site rebuild.

Measured, both are false:

  * THE EDGE IS FRESH. All three fetch byte-identical to `origin/main` (md5, 2026-09-05), with
    `age: 0` and a `last-modified` of that morning.
  * NOTHING MOVED. Same paths, served correctly. The director's own check missed them only because
    the repo paths are `docs/PROJECT_OVERVIEW.md` and `docs/market_research/ASSUMPTIONS.md`, not
    the repo-root paths.

What the session actually read was each document's OWN self-declared date sentence -- and two of
the three are hand-typed, so nothing computes them and nothing can notice when they rot:

  * `PROJECT_OVERVIEW.md` says "Last updated: 2026-08-09". Its last commit is 2026-08-17. The
    sentence is wrong about its own document by 8 days, and its "23,826 tests collected" was 2,905
    behind CLAUDE.md on the day it was read. THIS IS THE DEFECT: not old, but lying about being old.
  * `ASSUMPTIONS.md` says "Last seeded: 2026-08-10" and genuinely last changed 2026-08-10. Old, and
    honest about it. That is not a defect and this module does not treat it as one.
  * `LATEST.md` says "2026-09-05T07:06:34Z" and is machine-stamped. Correct.

THE AGGRAVATING FACT, and the reason "silently" is the right word. The one automatic freshness
signal a reader can check -- HTTP `last-modified` -- is USELESS HERE AND WORSE THAN ABSENT. The
GitHub Pages mirror uploads the whole `docs/` tree as a single artefact, so a `docs/status/`
publish restamps every file in the mirror. A reader fetching a 19-day-old PROJECT_OVERVIEW.md is
told `last-modified: today`. The transport actively asserts freshness the content does not have.

WHAT IS REFUSED, AND WHAT DELIBERATELY IS NOT
---------------------------------------------
REFUSED: a declared date that DISAGREES with the document's real age (`LIES`). That is a property,
not today's answer -- it stays green when the document is updated and stays green when it rots for
a year with an honest line, and it is always satisfiable by editing one sentence.

NOT REFUSED: age itself. An anchor that is genuinely old and says so is working as intended, and a
control keyed to age would go red for a reason nobody could act on and would be turned off -- the
"headroom control that reds because it became unsatisfiable" shape. Age is REPORTED instead, into
`docs/status/STARTUP_ANCHORS.md`, which ships by the same push as LATEST.md (the route already
proven to reach the edge fresh) and which the anchor block itself now points at. So an undated or
stale anchor is still stale -- it just cannot be stale WITHOUT THE READER BEING TOLD, which is the
whole of the director's instruction.

FAIL-CLOSED. Git unavailable, the anchor block unparseable, or fewer than `MIN_ANCHORS` anchors
recovered all REFUSE. The floor is what stops the cheapest possible silencing of a register-driven
control: deleting the rows. An empty anchor set is a broken check, never a clean pass.
"""
from __future__ import annotations

import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
if str(PROJECT) not in sys.path:  # run as a script by the publish path, not as `-m`
    sys.path.insert(0, str(PROJECT))

OVERVIEW = PROJECT / "docs" / "PROJECT_OVERVIEW.md"
OUT = PROJECT / "docs" / "status" / "STARTUP_ANCHORS.md"

#: GitHub Pages serves the repo's `docs/` directory as the site root.
PAGES_ROOT = "https://21bcarlisle-arch.github.io/synthetic-enterprise/"
DOCS_ROOT = "docs"

#: Below this many parsed anchors the check is not measuring the startup surface, so it refuses.
#: Four is the count the anchor block has carried since it was written; a fifth added later raises
#: nothing, a deletion below four refuses. Keyed to "the block still describes a surface", not to
#: which four are in it today.
MIN_ANCHORS = 4

#: How far a document's own date sentence may sit from its real last-change date before the
#: sentence counts as a claim rather than a rounding. Three days absorbs a doc edited over a
#: weekend and stamped on the Friday; the incident's own gap was 8 days.
DECLARED_DATE_TOLERANCE_DAYS = 3

#: Purely descriptive: the age at which the published table calls an anchor OLD for the reader.
#: Nothing refuses on it -- see the module docstring.
REPORTED_STALE_AFTER_DAYS = 14

_ANCHOR_LINE_RE = re.compile(r"^\s*-\s+[^:]+:\s*(" + re.escape(PAGES_ROOT) + r"\S+)\s*$", re.M)
#: A document's own claim about when it was last touched. Deliberately narrow: only the leading
#: lines are read, because a date deep in an append-log is a fact ABOUT the log, not about the file.
_DECLARED_RE = re.compile(
    r"(?:last\s+updated|last\s+seeded|generated)\s*:?\s*"
    r"(\d{4}-\d{2}-\d{2})", re.I)
_DECLARED_HEAD_LINES = 10


class AnchorRefusal(RuntimeError):
    """The check could not be performed. Never raised for a merely stale anchor."""


def _git(*args: str) -> str:
    done = subprocess.run(("git", *args), cwd=str(PROJECT),
                          capture_output=True, text=True, timeout=60)
    if done.returncode != 0:
        raise AnchorRefusal(f"git {' '.join(args)} failed: {done.stderr.strip()[:200]}")
    return done.stdout.strip()


def anchor_paths(overview_text: str | None = None) -> list[str]:
    """Repo paths for the anchors the startup surface DECLARES, read from the block that declares
    them rather than from a list this module also authors.

    Deriving the subject from the document keeps the two from drifting, which is the defect this
    whole module is about. `MIN_ANCHORS` is what stops the derivation degrading into "no anchors,
    nothing to check" when the block is edited or the file is unreadable.
    """
    if overview_text is None:
        try:
            overview_text = OVERVIEW.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise AnchorRefusal(f"cannot read the anchor block at {OVERVIEW}: {exc}") from exc

    paths = []
    for url in _ANCHOR_LINE_RE.findall(overview_text):
        rest = url[len(PAGES_ROOT):].split("#", 1)[0].split("?", 1)[0]
        if rest and not rest.endswith("/"):
            paths.append(f"{DOCS_ROOT}/{rest}")
    # Order-preserving dedup: the block lists PROJECT_OVERVIEW.md as "this document".
    seen, ordered = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            ordered.append(p)
    if len(ordered) < MIN_ANCHORS:
        raise AnchorRefusal(
            f"only {len(ordered)} startup anchors parsed from {OVERVIEW.name} (floor is "
            f"{MIN_ANCHORS}). An empty or shrunken anchor set is a broken check, not a clean one -- "
            "a control that iterates a register is silenced by deleting the rows."
        )
    return ordered


def true_last_change(path: str, today: dt.date | None = None) -> dt.date | None:
    """When this anchor's CONTENT last changed, answered against the tree a commit would create.

    Git history for a path that is not being touched; TODAY for one that is, because a file with
    uncommitted or staged changes is a file whose content is changing now.

    THE ASYMMETRY THIS EXISTS TO AVOID, found by running the first draft against the very edit that
    was fixing the defect: `declared_date` reads the WORKING TREE and this read only HEAD, so from
    the moment anyone corrected a date sentence until they committed it, the two sides described
    different trees and the check refused -- on every commit, for every lane, for the whole window,
    and most loudly at the person doing the repair. The same shape appears twice in this project's
    own record: a measurement whose subject is another process's uncommitted copy, and a staged
    repair invisible to a gate whose subject is HEAD. Both sides must read one tree.

    mtime is deliberately not used: it would answer for a `touch`, and every fresh clone would
    disagree with every other. `None` means the path is in neither HEAD nor the working tree.
    """
    today = today or dt.date.today()
    # STAGED, not merely dirty -- the subject is the tree THIS COMMIT creates, and another lane's
    # open working-tree edit is not part of it.
    #
    # The first draft used `git status --porcelain`, which counts unstaged edits too, and it was
    # wrong the first time it met the real tree: a concurrent lane was mid-append to
    # ASSUMPTIONS.md, so this reported the file as changing today, called its honest
    # "Last seeded: 2026-08-10" a lie, and refused -- pointing at a file that lane held dirty and
    # that could not be corrected without carrying their uncommitted work into someone else's
    # commit. Scoping to the index gives the property that actually belongs here: the lane whose
    # commit makes a document's date wrong is the lane asked to fix it, and no other.
    if _git("diff", "--cached", "--name-only", "HEAD", "--", path):
        return today
    out = _git("log", "-1", "--format=%cI", "HEAD", "--", path)
    if not out:
        # Distinguish "absent at this revision" from "git could not answer" -- `git log` returns
        # empty for both, and treating an unanswerable query as a missing file would fabricate a
        # MISSING refusal out of a transient git failure.
        if _git("ls-tree", "--name-only", "HEAD", "--", path):
            raise AnchorRefusal(
                f"{path} is in HEAD but git could not date it -- the check cannot be performed")
        return None
    return dt.datetime.fromisoformat(out).date()


def declared_date(path: str) -> dt.date | None:
    """What the document CLAIMS about its own age, or None if it makes no claim."""
    try:
        head = "\n".join(
            (PROJECT / path).read_text(encoding="utf-8", errors="replace").splitlines()
            [:_DECLARED_HEAD_LINES]
        )
    except OSError:
        return None
    m = _DECLARED_RE.search(head)
    if not m:
        return None
    try:
        return dt.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def assess(today: dt.date | None = None) -> list[dict]:
    """One row per declared anchor. Raises AnchorRefusal if the check cannot be performed."""
    today = today or dt.date.today()
    rows = []
    for path in anchor_paths():
        true = true_last_change(path, today)
        claimed = declared_date(path)
        age = (today - true).days if true else None
        drift = abs((claimed - true).days) if (claimed and true) else None

        if true is None:
            verdict = "MISSING"
        elif drift is not None and drift > DECLARED_DATE_TOLERANCE_DAYS:
            verdict = "LIES"
        elif claimed is None:
            verdict = "UNDATED"
        elif age is not None and age > REPORTED_STALE_AFTER_DAYS:
            verdict = "OLD"
        else:
            verdict = "FRESH"

        rows.append({
            "path": path, "true_last_change": true.isoformat() if true else None,
            "declared": claimed.isoformat() if claimed else None,
            "age_days": age, "declared_drift_days": drift, "verdict": verdict,
        })
    return rows


def refusals(rows: list[dict]) -> list[dict]:
    """Only a document that MISSTATES its own age, or is not in HEAD at all.

    A merely old anchor is not here on purpose: it is reported, not refused. See the docstring.
    """
    return [r for r in rows if r["verdict"] in ("LIES", "MISSING")]


def render(rows: list[dict], today: dt.date | None = None) -> str:
    today = today or dt.date.today()
    out = [
        "# Startup anchors -- computed freshness",
        "",
        f"Generated: {today.isoformat()} by `tools/startup_anchor_freshness.py`.",
        "",
        "Every age below is computed from this repository's history at HEAD. **Do not use the HTTP",
        "`last-modified` header of any of these URLs to judge freshness**: the GitHub Pages mirror",
        "uploads the whole `docs/` tree as one artefact, so any publish restamps every file in it,",
        "and a document untouched for a month is served with today's date.",
        "",
        "| Anchor | Last really changed | Age (days) | Says about itself | Verdict |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        out.append("| `{}` | {} | {} | {} | {} |".format(
            r["path"], r["true_last_change"] or "not in HEAD",
            "?" if r["age_days"] is None else r["age_days"],
            r["declared"] or "nothing", r["verdict"]))
    out += [
        "",
        "`FRESH` recent · `OLD` genuinely old and honest about it (not a defect) · `UNDATED` states",
        f"no date of its own, so this table is the only age a reader gets · `LIES` its own date is "
        f"more than {DECLARED_DATE_TOLERANCE_DAYS} days from its real one · `MISSING` not in HEAD.",
        "",
    ]
    return "\n".join(out)


def staged_anchors(paths: list[str]) -> set[str]:
    """Which declared anchors THIS COMMIT changes."""
    out = _git("diff", "--cached", "--name-only", "HEAD", "--", *paths)
    return {line for line in out.splitlines() if line}


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    write = "--check" not in argv and "--gate" not in argv
    try:
        rows = assess()
        # `--gate` (the pre-commit hook) judges ONLY anchors this commit touches. Refusing an
        # unrelated lane's commit because some other document's date sentence is wrong would wedge
        # the whole tree on a defect that lane did not cause and cannot fix without carrying
        # someone else's uncommitted work -- and "the red that refused your land was already at
        # HEAD" is a trap this project has paid for before. The publish path (no flag) still
        # reports every anchor, so nothing goes unseen; only the REFUSAL is scoped to the author.
        if "--gate" in argv:
            touched = staged_anchors([r["path"] for r in rows])
            if not touched:
                return 0
            rows = [r for r in rows if r["path"] in touched]
    except AnchorRefusal as exc:
        # FAILS CLOSED. Unlike the next-step gate (one missed trailer is recoverable), an
        # unmeasurable startup surface is the exact condition being guarded against.
        print(f"[startup-anchors] REFUSED, check could not run: {exc}", file=sys.stderr)
        return 1

    if write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(render(rows), encoding="utf-8")
        print(f"[startup-anchors] wrote {OUT.relative_to(PROJECT)} ({len(rows)} anchors)")

    bad = refusals(rows)
    for r in bad:
        if r["verdict"] == "LIES":
            print(f"[startup-anchors] REFUSED: {r['path']} says it was last updated "
                  f"{r['declared']} but really changed {r['true_last_change']} "
                  f"({r['declared_drift_days']} days out). A reader orienting on this document is "
                  f"told an age it does not have. Correct the date sentence.", file=sys.stderr)
        else:
            print(f"[startup-anchors] REFUSED: {r['path']} is declared as a startup anchor but is "
                  f"not in HEAD.", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
