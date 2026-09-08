"""Who actually CHOSE each deletion a merge is credited with -- the second half of
`SEAT_FINDING_THE_STALE_COPY_GUARD_RE_ASKS_ON_A_MERGE_AND_MAKES_ONE_LANE_DECLARE_ANOTHERS_DELETION`.

The first half threaded the merge ref into `tools.stale_copy_refusal.violations` so a merge over a
path this side never touched lands instead of being refused. That closed the FUTURE. This closes the
PAST: while the guard could not tell the two cases apart, the only route through was `--drops`, whose
own comment says it "makes a deliberate deletion attributable to the landing that chose it". Used on
a merge it does the exact opposite, and the receipt is `22df46614`, which carries a declared drop
belonging to `d3e0e408b`. **Any census of who deleted what reads the wrong lane**, and nothing in the
record says so -- the declaration leaves no machine-readable mark on the commit at all.

WHAT THIS MEASURES, SAID BEFORE IT IS MEASURED, BECAUSE THE WORD "DELETION" HAS TWO POPULATIONS HERE
AND THEY ARE DISJOINT.

  A. **A NAME lost from a file that survives the merge.** This is the whole subject. It is what
     `stale_copy_refusal.judge` refuses, therefore the only thing `--drops` can ever exempt,
     therefore the only place the misattribution can occur. This census is population A.

  B. **A whole FILE the merge removes.** `judge` returns `None` when either side's blob is absent --
     "a deletion is explicit -- so neither is this control's business" -- so the guard never fires on
     one, `--drops` never declares one, and no lane is ever credited by a declaration for one.

They are disjoint, not nested, and the counts do not add. Measured 2026-09-08, population B is 48
merge-adopted file deletions across 22 merges: real, ordinary, and NOT this control's business. It is
recorded here so that a reader who asks the obvious next question finds it answered rather than
unasked -- not because the number belongs to the finding.

THE PREDICATE IS `stale_copy_refusal.adopted_from_merge`, CALLED, NOT REIMPLEMENTED. A census that
re-derives the guard's own judgement drifts from it, and then the two disagree and neither is wrong.
Every row here is a path the live guard would exempt today and did not exempt then, which is what
makes the row a statement about the record rather than about this module's opinion.

WHY THE CHOOSER IS FOUND PER NAME AND NOT PER PATH. "The last commit touching this path on the ref
side" is cheap and it is a different question -- it names the commit that DELIVERED the adopted blob,
which is often a later edit that merely carried the absence along. The commit that CHOSE the deletion
is the one where the name is present in its first parent and absent in it. That is what the finding
asks for, so that is what is computed, per lost name, walking the ref side forward.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools import stale_copy_refusal as scr


@dataclass(frozen=True)
class Misattribution:
    """One path a merge is credited with losing names from, that it merely adopted."""

    merge: str
    path: str
    rule: str
    #: name -> the commit that chose its deletion ("" when it could not be established).
    choosers: dict[str, str] = field(default_factory=dict)

    def unattributed(self) -> tuple[str, ...]:
        """Names whose chooser could not be established. NAMED, never folded into the total: a
        census that reports only what it could resolve reads as complete when it is not."""
        return tuple(sorted(n for n, sha in self.choosers.items() if not sha))

    def render(self, subjects: dict[str, str] | None = None) -> str:
        subjects = subjects or {}
        out = ["  {}  {}  [{}]".format(self.merge[:9], self.path, self.rule)]
        for name in sorted(self.choosers):
            sha = self.choosers[name]
            if sha:
                out.append("      - {}  CHOSEN BY {}  {}".format(
                    name, sha[:9], subjects.get(sha, "")[:70]))
            else:
                out.append("      - {}  CHOOSER NOT ESTABLISHED on the ref side".format(name))
        return "\n".join(out)


def _git(root: Path, *args: str) -> str:
    out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else ""


def _parents(root: Path, sha: str) -> list[str]:
    return _git(root, "rev-parse", sha + "^@").split()


def _changed(root: Path, a: str, b: str) -> list[str]:
    """`--no-renames` for the same reason `adopted_from_merge` uses it: with rename detection on, a
    renamed file reports only its new path and reads as untouched at the old one."""
    return [ln.strip() for ln
            in _git(root, "diff", "--no-renames", "--name-only", a, b).splitlines() if ln.strip()]


def _carries(text: str, path: str, token: str, rule: str) -> bool | None:
    """Does this copy of `path` still carry `token`? `None` when it cannot be told.

    THE TOKEN IS A DIFFERENT KIND OF THING PER RULE, and reading it the same way for both is how the
    first draft of this census reported "chooser not established" for 113 of its 120 rows and looked
    like missing history rather than a blind reader. `strict_symbol_subset` details are SYMBOL NAMES;
    `predates_landing` details are DISTINCTIVE LINES. Searching a line among symbol names never
    matches, so the whole `predates_landing` class was structurally untraceable and said so in a
    voice indistinguishable from a genuine gap.

    The line comparison is `judge`'s own -- stripped lines, membership -- because these tokens came
    out of `distinctive_lines` already stripped and must be tested the way they were produced."""
    if rule == scr.PREDATES:
        return token in {ln.strip() for ln in text.splitlines()}
    try:
        names = scr.symbols(text, path)
    except scr.Unparseable:
        return None
    return None if names is None else token in names


def chose_the_deletion(root: Path, base: str, ref: str, path: str,
                       token: str, rule: str) -> str:
    """The commit in `base..ref` whose first parent's copy of `path` carries `token` and whose own
    does not. "" when no such commit can be shown.

    NEWEST FIRST, AND THAT IS A CORRECTION. This walked forward and took the EARLIEST deletion until
    a mutation battery showed reversing it changed nothing, which was a missing test hiding a wrong
    rule. A name can be deleted, re-added and deleted again: after the re-add the name is PRESENT,
    so the earliest deletion is not the one the merge adopts -- it was undone. The absence in the
    adopted blob is made by the LAST commit that removed it, and that is the commit that chose the
    deletion this merge carries. Written down beside the claim it replaces because a rule corrected
    silently reads as a rule that was always right.

    FAIL TO "", NEVER TO A GUESS. An unparseable copy, an absent blob or a root commit yields no
    answer, and `Misattribution.unattributed()` reports that as its own state. A census that
    substituted "the last commit touching the path" here would return a plausible sha for every row
    and be unfalsifiable.

    AN `unparseable` ROW NEEDS NO SPECIAL CASE, and the draft that had one was wrong to. Its detail
    is a parser error message rather than a token of the source, so the ordinary walk below already
    returns "": no commit's copy carries it. The early return that used to sit here was written as
    though it were a guard, and a mutation battery showed it could not be made to fire -- an
    EQUIVALENCE, not a missing test. It is deleted rather than kept with a comment claiming a role
    it never had, and `test_an_unparseable_row_gets_no_chooser_from_a_live_walk` holds the property
    with a poison round proving the walk it relies on actually runs."""
    for sha in _git(root, "log", "--format=%H", "--no-renames",
                    "{}..{}".format(base, ref), "--", path).split():
        after, before = scr.blob_at(root, sha, path), scr.blob_at(root, sha + "^", path)
        if after is None or before is None:
            continue
        was, now = (_carries(before, path, token, rule), _carries(after, path, token, rule))
        if was is None or now is None:
            continue
        if was and not now:
            return sha
    return ""


def misattributions(root: Path, merge: str) -> list[Misattribution]:
    """Every path `merge` is credited with losing names from that it adopted from another parent.

    The two calls are the whole method and they are deliberately the guard's own: `violations`
    WITHOUT the merge ref is what the record credits to this lane, `adopted_from_merge` is what the
    guard would exempt today. The intersection is the misattribution."""
    parents = _parents(root, merge)
    if len(parents) < 2:
        return []
    first, refs = parents[0], parents[1:]
    paths = _changed(root, first, merge)
    if not paths:
        return []
    credited = {loss.path: loss for loss in scr.violations(root, first, merge, paths)}
    if not credited:
        return []

    out = []
    for ref in refs:
        base = _git(root, "merge-base", first, ref).strip()
        if not base:
            continue
        for path in sorted(scr.adopted_from_merge(root, first, ref, paths)):
            loss = credited.pop(path, None)
            if loss is None:
                continue
            out.append(Misattribution(
                merge=merge, path=path, rule=loss.rule,
                choosers={tok: chose_the_deletion(root, base, ref, path, tok, loss.rule)
                          for tok in loss.detail}))
    return out


def census(root: Path, revs: str = "HEAD") -> list[Misattribution]:
    """Every merge reachable from `revs`, oldest first."""
    out = []
    for merge in reversed(_git(root, "rev-list", "--merges", revs).split()):
        out.extend(misattributions(root, merge))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--revs", default="HEAD", help="rev range to census (default HEAD)")
    ap.add_argument("--root", default=".", type=Path)
    args = ap.parse_args(argv)

    rows = census(args.root, args.revs)
    subjects = {}
    for row in rows:
        for sha in row.choosers.values():
            if sha and sha not in subjects:
                subjects[sha] = _git(args.root, "log", "--format=%s", "-1", sha).strip()

    if not rows:
        print("[merge-attribution] no merge in {} is credited with a name loss it adopted."
              .format(args.revs))
        return 0
    print("[merge-attribution] {} path(s) across {} merge(s) are credited to the merge that "
          "ADOPTED the\ndeletion, not the commit that CHOSE it:\n"
          .format(len(rows), len({r.merge for r in rows})))
    for row in rows:
        print(row.render(subjects))
    unresolved = sum(len(r.unattributed()) for r in rows)
    if unresolved:
        print("\n[merge-attribution] {} name(s) could not be traced to a choosing commit."
              .format(unresolved))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
