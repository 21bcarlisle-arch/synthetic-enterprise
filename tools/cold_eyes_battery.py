#!/usr/bin/env python3
"""EP6 L3 — the cold-eyes BATTERY is the exit criterion, and its QUESTIONS are the unit.

WHAT THIS REPLACES, AND WHY IT IS A REPAIR RATHER THAN AN ADDITION
------------------------------------------------------------------
`tools/wall_channel_census.cold_eyes_walk_outstanding` asks ONE question: has a blind
review of this capability been RECORDED? It returns `()` — no blocker — the moment a
single record with a matching `capability` exists, whatever that record says.

Pass 33 of `EP6_wall_protocol_typing` ran the walk, reconciled FIVE of the battery's
seventeen questions against the code, found two of them failing, and wrote, verbatim:

    "greening a level on the mere fact that the review happened would make the
     instrument a ceremony. So the level is held."

It then shipped a predicate that greens on the mere fact that the review happened. The
level was held by JUDGMENT, in prose, in a store entry; the MECHANISM said unblocked.
That is this project's recorded failure mode for exactly this class — a rule that lives
as prose evaporates, and R15's FAIL-OPEN pattern is a control that passes on the state it
exists to catch. Measured at the time of writing: `cold_eyes_walk_outstanding()` returns
`()` while NINE of the battery's twelve DISQUALIFYING questions do not pass against the
live tree, and SEVEN of those nine had never been reconciled by any pass.

THE UNIT IS THE DISQUALIFYING QUESTION, NOT THE REVIEW
------------------------------------------------------
The blind reviewer's battery is stored VERBATIM in the ledger record beside the packet it
answered (`tools/blind_review.py` keeps transcript and result as one record precisely so
they cannot be separated). Each question carries its own `verdict` — DISQUALIFYING or
SUPPORTING — assigned by the reviewer BEFORE any of the code was seen. So the exit
criterion is not a judgement this lane gets to make: it is a closed set, authored blind,
sitting on disk.

That closure is the point. Passes 34, 35 and 36 each derived a fresh "WHAT REMAINS FOR L3"
list from their own investigation — three different lists, none of them the battery, while
seven of the battery's own disqualifying questions sat unanswered. A criterion that is
re-derived each pass cannot be met by definition, which is how an atom takes twenty-eight
passes without its level moving. This makes the criterion the thing the reviewer actually
wrote down.

WHY A RECONCILIATION FILE IS NOT A TAUTOLOGY
---------------------------------------------
The reconciliation is authored by the lane, so the obvious objection is R15 TAUTOLOGY: the
control reads a source the checked party writes. What makes it hold is the DIRECTION of
the failure. To green this predicate the lane must record, per question, an explicit PASS
with cited evidence — twelve falsifiable claims a reader can check against the code, each
naming a file. To red it, the lane need do nothing at all. Silence blocks; only a specific,
attributable, checkable assertion releases. Compare the predicate it replaces, where
silence RELEASED and no claim was required of anyone.

FAIL-CLOSED AT EVERY STEP, and the direction is the same as the ceiling this feeds. An
unreadable ledger, an unreadable reconciliation, a battery with no disqualifying questions,
a reconciliation row naming a question the battery does not carry, two rows for one
question, a verdict outside the vocabulary — every one of these RAISES rather than
reporting "nothing outstanding". An unavailable check is a FAILED check (R15 FAIL-SILENT),
and "nothing blocks L3", computed from a source nobody could read, is the reading that
turned this atom's level into a twenty-eight-pass no-op in the first place.

A NON-EMPTY EVIDENCE STRING IS NOT A TRUE ONE, and the subject is HEAD (pass 51, filed as
`WORKER_FINDING_THE_BATTERY_CHECKS_THAT_ITS_EVIDENCE_IS_NON_EMPTY_NEVER_THAT_IT_IS_TRUE`)
-----------------------------------------------------------------------------------------
Everything above is fail-closed against SILENCE. None of it was fail-closed against a claim
that cites something which does not exist. `RECONCILIATION_KEYS` was enforced by a
TRUTHINESS test, so it refused an absent evidence string and accepted every non-empty one —
while this docstring claimed the rows were "twelve falsifiable claims a reader can check
against the code" and nothing in the module ever opened the code. Pass 43 recorded a repair
against eight source files that sat uncommitted in the shared worktree across at least one
further tick, and this control could not tell.

WHY THE OBVIOUS REPAIR IS THEATRE, MEASURED RATHER THAN ARGUED. Requiring every cited repo
PATH to resolve was tested against `2c0ba712b`, the real tree as it stood while the defect
was live: of the twelve rows' citations, unresolvable paths = ZERO. A path-existence control
would have been GREEN throughout. Pass 43 added a new SYMBOL to a file that already existed,
so the location resolved and the claim was still false. This is the inverse of the recorded
lesson that a symbol-presence control is fail-open because the claim carries a location:
here the claim carries BOTH, and checking only the location is the fail-open half.

SO THE UNIT IS `path::symbol`, RESOLVED AGAINST HEAD. `git show HEAD:<path>` is parsed and
the cited name must be DEFINED there — not merely present as text, which a comment mentioning
it would satisfy. HEAD, never the working tree, is the entire mechanism: a symbol present
only in the worktree is precisely the defect, and because `surgical_land` materialises
HEAD-plus-pathspec as a real repo, a row citing a symbol authored in the SAME commit resolves
inside the gate and nowhere else. That property is what makes this check landable at all —
and what it costs is that `battery_outstanding()` run against a worktree mid-pass will RAISE
until the pass lands its code with its row. That is the discipline, not a defect.

FOUR NAMED FAIL-OPEN RESIDUES, because a control's limits belong at the code:

1. THE CHECK COVERS THE NOTATION, NOT THE CLAIM. Only `path.py::Name` is resolvable. Q11
   cites `company/interfaces/wall_protocol.py:176-179` — a line range, which drifts and
   cannot be resolved by name — and prose citations resolve to nothing at all.
2. A DOTTED TAIL IS NOT RESOLVED. `X.method` verifies `X` only. Resolving the attribute
   would need type inference the citation does not carry.
3. A PASS ROW CITING NO PATH STAYS UNCHECKED, AND THAT IS CORRECT, NOT AN OVERSIGHT. Q17 is
   a PASS whose reviewer-specified right answer is an ABSENCE — "an honest 'they don't,
   they're outside this' is fine and expected". A rule requiring every PASS to cite a
   resolvable symbol would red the one question the reviewer pre-authorised a negative
   answer for. Absence-claims are left alone deliberately.
4. IT CANNOT MOVE A VERDICT, ONLY BLOCK ONE. Both citations that would have caught pass 43
   sit in rows that were already FAIL, and FAIL blocks anyway. Its value is catching the
   UNLANDED STATE — a record describing code in no tree. Claiming it would have protected
   the exit criterion would be the overclaim this atom's own walk exists to stop.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

#: The capability id the blind review is recorded under — a join key into the ledger, not a
#: label. `tools/blind_review.py` keys on the maturity-map atom id.
CAPABILITY = "EP6_wall_protocol_typing"

#: Where the per-question reconciliation lives. Beside the ledger it reconciles against,
#: because the two are read together and a reader looking for one wants the other.
RECONCILIATION_REL = "docs/observability/cold_eyes_battery_reconciliation.jsonl"

#: The criterion reported when NO walk has been recorded at all. Preserved verbatim from
#: `wall_channel_census.COLD_EYES_WALK_CRITERION` so the map's history stays joinable.
COLD_EYES_WALK_CRITERION = "L3_cold_eyes_walk_on_the_three_seam_codecs"

#: The reviewer's own word for "this question, unanswered, disqualifies the capability".
#: Assigned blind, before any code was seen.
DISQUALIFYING = "DISQUALIFYING"

#: Keys a reconciliation row must carry. A row missing one is REFUSED, not skipped: a
#: verdict with no evidence is an opinion, and an opinion is what this file exists to
#: replace.
RECONCILIATION_KEYS = ("capability", "n", "verdict", "evidence")

#: A citation this module can actually resolve: a repo-relative path to a Python module, `::`,
#: and a top-level name. Deliberately narrow — residues 1 and 2 in the module docstring say
#: what it therefore does not cover, which is the honest half of shipping it.
CITATION = re.compile(r"([A-Za-z0-9_][A-Za-z0-9_./-]*\.py)::([A-Za-z_][A-Za-z0-9_]*)")

#: The ref citations resolve against. HEAD, never the working tree — see the module docstring
#: for why that choice IS the mechanism rather than an implementation detail.
CITATION_REF = "HEAD"

#: Blob cache keyed by (resolved sha, path), so a survey that reads one atom's twelve rows
#: does not shell out once per citation. Keyed on the SHA rather than the ref name so a
#: long-lived process cannot serve a stale HEAD after a commit lands under it.
_BLOB_CACHE: dict[tuple[str, str], str | None] = {}

#: The only two answers. `PARTIAL`, `IN_PROGRESS` and their friends are deliberately absent:
#: a question that is partly answered has not been answered, and a vocabulary that lets a
#: blocker be recorded as nearly-cleared is how a blocker stops blocking.
VERDICTS = ("PASS", "FAIL")


class BatteryUnavailable(RuntimeError):
    """A check that could not be run. Never a pass — see the fail-closed paragraph above."""


def _reconciliation_path(path: Path | str | None = None) -> Path:
    return Path(path) if path is not None else PROJECT_DIR / RECONCILIATION_REL


def _git(args: list[str], project_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(project_dir), capture_output=True, text=True, timeout=30
    )


def _resolve_ref(ref: str, project_dir: Path) -> str:
    """The ref's SHA, or RAISE naming the ref rather than blaming a citation.

    An unreadable ref is git being unavailable, which is a FAILED check and not a false
    claim — and the two must not share a message, or a broken checkout reads as a lane
    fabricating evidence. Same distinction the publish gate draws when it says "DISK, not
    code".
    """
    try:
        done = _git(["rev-parse", "--verify", f"{ref}^{{commit}}"], project_dir)
    except (OSError, subprocess.SubprocessError) as exc:
        raise BatteryUnavailable(
            f"git could not be run in {project_dir}, so no cited symbol can be resolved and "
            f"whether the evidence is true is UNKNOWN -- a failed check, not a passed one: {exc}"
        ) from exc
    if done.returncode != 0:
        raise BatteryUnavailable(
            f"the citation ref {ref!r} does not resolve in {project_dir}, so no cited symbol "
            f"can be checked against committed truth: {done.stderr.strip()}"
        )
    return done.stdout.strip()


def _blob_at(sha: str, path: str, project_dir: Path) -> str | None:
    """The file's committed bytes at `sha`, or None when it is not in that tree."""
    key = (sha, path)
    if key not in _BLOB_CACHE:
        done = _git(["show", f"{sha}:{path}"], project_dir)
        _BLOB_CACHE[key] = done.stdout if done.returncode == 0 else None
    return _BLOB_CACHE[key]


def _defined_names(source: str) -> set[str] | None:
    """Every name BOUND at any depth in `source`, or None if it does not parse.

    Defined, not merely mentioned: a substring search would be satisfied by a comment naming
    the symbol, which is the same fail-open shape one level down.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
        elif isinstance(node, ast.alias):
            names.add((node.asname or node.name).split(".")[0])
    return names


def cited_symbols(evidence: str) -> tuple[tuple[str, str], ...]:
    """The `path.py::Name` pairs an evidence string claims, in order, deduplicated."""
    seen: list[tuple[str, str]] = []
    for path, symbol in CITATION.findall(evidence or ""):
        if (path, symbol) not in seen:
            seen.append((path, symbol))
    return tuple(seen)


def unresolved_citations(
    evidence: str, ref: str = CITATION_REF, project_dir: Path | str | None = None
) -> tuple[str, ...]:
    """Cited `path::symbol` pairs that are NOT defined at `ref`, each with why.

    Empty for an evidence string that cites nothing resolvable — residues 1-3 in the module
    docstring, and residue 3 in particular is load-bearing rather than a gap.
    """
    project = Path(project_dir) if project_dir is not None else PROJECT_DIR
    citations = cited_symbols(evidence)
    if not citations:
        return ()
    sha = _resolve_ref(ref, project)
    bad: list[str] = []
    for path, symbol in citations:
        source = _blob_at(sha, path, project)
        if source is None:
            bad.append(f"{path}::{symbol} (no such file at {ref})")
            continue
        names = _defined_names(source)
        if names is None:
            bad.append(f"{path}::{symbol} ({path} does not parse at {ref})")
        elif symbol not in names:
            bad.append(f"{path}::{symbol} ({symbol} is not defined in {path} at {ref})")
    return tuple(bad)


def disqualifying_questions(
    capability: str = CAPABILITY, ledger_path: Path | str | None = None
) -> dict[int, dict]:
    """The battery's DISQUALIFYING questions for `capability`, keyed by their number.

    Raises when a walk IS recorded but its battery cannot be read as a set of numbered
    questions, and when that set is empty. Zero disqualifying questions is the reassuring
    answer a broken parse produces, and it is indistinguishable from a capability nobody
    could fault — so it is refused rather than believed.
    """
    try:
        from tools.blind_review import load_records
    except ImportError as exc:  # pragma: no cover - the module is in-tree
        raise BatteryUnavailable(f"blind_review unavailable, so the battery is unknowable: {exc}")
    try:
        records = load_records(ledger_path)
    except Exception as exc:  # noqa: BLE001 - any read failure is a failed check
        raise BatteryUnavailable(
            f"the blind-review ledger could not be read, so whether L3's criteria are met "
            f"is unknown -- that is a failed check, not an answer: {exc}"
        ) from exc

    matched = [r for r in records if r.get("capability") == capability]
    if not matched:
        return {}

    out: dict[int, dict] = {}
    for record in matched:
        battery = record.get("battery")
        if not isinstance(battery, list) or not battery:
            raise BatteryUnavailable(
                f"{capability}: a walk is recorded with no readable battery, so the criterion "
                f"it set is unknown -- a recorded review that asked nothing is not a pass"
            )
        for question in battery:
            if not isinstance(question, dict) or "n" not in question:
                raise BatteryUnavailable(
                    f"{capability}: a battery entry carries no question number, so the "
                    f"criterion cannot be joined to its reconciliation"
                )
            if question.get("verdict") == DISQUALIFYING:
                out[int(question["n"])] = question

    if not out:
        raise BatteryUnavailable(
            f"{capability}: the recorded battery carries ZERO {DISQUALIFYING} questions. That "
            f"is the answer a broken read gives and the answer a flawless capability gives, "
            f"and they are not the same -- refused rather than reported as unblocked"
        )
    return out


def load_reconciliations(
    capability: str = CAPABILITY,
    path: Path | str | None = None,
    citation_ref: str = CITATION_REF,
    project_dir: Path | str | None = None,
) -> dict[int, dict]:
    """Question number -> its reconciliation row. An ABSENT file is empty, not unreadable.

    Nothing recorded is the honest reading that no question has been answered, and it blocks
    every one of them. An unparseable or self-contradictory file is a different thing and
    raises — and so, since pass 51, does a row whose evidence cites a `path::symbol` that is
    not defined at `citation_ref`. See the module docstring's HEAD-not-worktree paragraph.
    """
    target = _reconciliation_path(path)
    if not target.exists():
        return {}
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise BatteryUnavailable(f"reconciliation unreadable, so no question is answered: {exc}")

    out: dict[int, dict] = {}
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            raise BatteryUnavailable(f"{target.name}:{lineno} is not readable JSON: {exc}")
        if row.get("capability") != capability:
            continue
        missing = [k for k in RECONCILIATION_KEYS if not row.get(k)]
        if missing:
            raise BatteryUnavailable(
                f"{target.name}:{lineno} is missing {missing} -- a verdict that does not say "
                f"what it was checked against is an opinion, not a reconciliation"
            )
        if row["verdict"] not in VERDICTS:
            raise BatteryUnavailable(
                f"{target.name}:{lineno} carries verdict {row['verdict']!r}, which is outside "
                f"{list(VERDICTS)} -- an unrecognised verdict is not a pass"
            )
        unresolved = unresolved_citations(row["evidence"], citation_ref, project_dir)
        if unresolved:
            raise BatteryUnavailable(
                f"{target.name}:{lineno} (question {row['n']}) cites symbols that do not exist "
                f"at {citation_ref}: {'; '.join(unresolved)} -- a record describing code that "
                f"is in no commit is not evidence, whatever it says. Land the code with the "
                f"row, or cite what is actually there"
            )
        n = int(row["n"])
        if n in out:
            raise BatteryUnavailable(
                f"{target.name}:{lineno} is a SECOND row for question {n}. Which one is the "
                f"answer is unknowable, so neither is taken"
            )
        out[n] = row
    return out


def battery_outstanding(
    capability: str = CAPABILITY,
    ledger_path: Path | str | None = None,
    reconciliation_path: Path | str | None = None,
    citation_ref: str = CITATION_REF,
    project_dir: Path | str | None = None,
) -> tuple[str, ...]:
    """THE L3 EXIT CRITERION, AS A FUNCTION. `()` only when every DISQUALIFYING question PASSES.

    Three ways a question is outstanding, and they are deliberately not distinguished in the
    return value because they have the same consequence: no walk has run at all; the question
    has no reconciliation row; the row says FAIL. Only a recorded, evidenced PASS clears one.
    """
    questions = disqualifying_questions(capability, ledger_path)
    if not questions:
        return (COLD_EYES_WALK_CRITERION,)

    rows = load_reconciliations(
        capability, reconciliation_path, citation_ref, project_dir
    )
    stranded = sorted(set(rows) - set(questions))
    if stranded:
        raise BatteryUnavailable(
            f"{capability}: reconciliation rows exist for questions {stranded}, which the "
            f"recorded battery does not carry as {DISQUALIFYING}. The two refs have drifted "
            f"and an answer to a question nobody asked would silently clear a real one"
        )

    return tuple(
        f"Q{n}" for n in sorted(questions) if rows.get(n, {}).get("verdict") != "PASS"
    )


def unpayable_here(
    capability: str = CAPABILITY,
    ledger_path: Path | str | None = None,
    reconciliation_path: Path | str | None = None,
    citation_ref: str = CITATION_REF,
    project_dir: Path | str | None = None,
) -> tuple[str, ...]:
    """The outstanding criteria this SEAT cannot pay for — the map's `infeasible_here` half.

    A strict subset of `battery_outstanding`: a question is unpayable here only when it is
    outstanding AND its reconciliation row marks it `epoch_gated`. The distinction is the
    whole value of the pair — an atom blocked on ordinary build work must keep being drawn,
    and an atom blocked on a reserved-class act must not be drawn again until that act
    happens. Recording the second as the first is what buys an unbounded pass loop; recording
    the first as the second is how a lane retires work it simply did not want to do.

    `epoch_gated` is only consulted on rows that are ALREADY outstanding, so marking a PASSING
    question as gated changes nothing. The flag can narrow this set, never widen it past the
    blockers that genuinely remain.
    """
    outstanding = set(battery_outstanding(capability, ledger_path, reconciliation_path))
    rows = load_reconciliations(
        capability, reconciliation_path, citation_ref, project_dir
    )
    return tuple(
        f"Q{n}"
        for n in sorted(rows)
        if f"Q{n}" in outstanding and bool(rows[n].get("epoch_gated"))
    )


def _render() -> str:
    questions = disqualifying_questions()
    rows = load_reconciliations()
    lines = [
        f"{CAPABILITY} -- L3 cold-eyes battery: "
        f"{len(questions)} {DISQUALIFYING} questions, "
        f"{sum(1 for n in questions if rows.get(n, {}).get('verdict') == 'PASS')} PASS",
        "",
    ]
    for n in sorted(questions):
        row = rows.get(n)
        verdict = row["verdict"] if row else "UNRECONCILED"
        gated = " [epoch-gated]" if row and row.get("epoch_gated") else ""
        lines.append(f"  Q{n:<3} {verdict:<13}{gated} {questions[n]['question'][:78]}")
    lines += ["", f"outstanding: {battery_outstanding() or '() -- L3 criterion MET'}"]
    lines.append(f"unpayable here: {unpayable_here() or '()'}")
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover - CLI
    print(_render())
