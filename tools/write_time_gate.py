"""AO2 -- the WRITE-TIME GATE: a new capability module cannot land without a record of the look.

Serves `DIRECTOR_PROGRAMME_ARCHITECTED_OUT_2026-08-05.md` step MAP, second half. AO1
(`tools/capability_index.py`) made the look cheap; this is the step that spends it -- the director's
own framing is that the index is a demo until this exists, and §5 names it "the only immediate
behaviour change" in the whole programme.

THE WALL THIS MECHANISM MUST NOT CROSS (director, verbatim): *"know, then choose -- forced reuse
that couples two purposes is the mirror error of duplication and is equally a defect."* So this gate
compels the LOOK and the RECORD. It never compels the reuse DECISION: every one of its refusals is
answerable by writing a truthful record and committing the new module anyway. There is no record
this gate accepts for "reuse" that it refuses for "wrote it fresh" -- reread the guards below and
check that property holds before changing any of them.

THE TWO QUESTIONS (director's same-day amendment). A record answers both:
  1. *Do we already have this?*  -> the INDEX line: the terms you put through `capability_index.py`.
  2. *Does the ecosystem already have this?* -> the CLASS line, under the three ruled part classes:
       CATALOGUE  -- calendars, timezones, money arithmetic, statistical fitting, solvers. ALWAYS
                     from a mature library, never hand-rolled. A new CATALOGUE module must name the
                     library it stands on (`LIBRARY:`); a catalogue part with no library named is
                     the 2026-08-03 from-scratch working-day calculator happening again, which is
                     the director's own named evidence class.
       CUSTOM     -- GB market mechanics, licence conditions, behavioural archetypes, the wall, the
                     harness. ALWAYS built: it is the product. No build-vs-buy note owed.
       SUBSYSTEM  -- dispatch, ledgers and similar. May be custom, but ONLY with a build-vs-buy note
                     naming the library EVALUATED and why REJECTED. "Silence is a gap" -- the
                     director's words, and the reason G4 refuses an absent note rather than warning.

RECORD FORMAT -- in the commit message, one block per new module:

    REUSE: tools/write_time_gate.py
    CLASS: CUSTOM
    INDEX: searched "commit gate", "pre-commit", "build vs buy" -- nearest is
           tools.pre_commit_test_gate, which gates test colour and asks no reuse question

  CATALOGUE adds   LIBRARY: holidays (pinned) -- this module is a thin wrapper over it
  SUBSYSTEM adds   EVALUATED: beancount, ledger-cli
                   REJECTED: both assume a file-backed journal; neither models GB settlement runs

`python3 tools/write_time_gate.py --explain <path>` prints the block pre-filled with the live index
matches, so producing the record costs a paste rather than a memory.

WHY commit-msg AND NOT pre-commit. The message does not exist yet when pre-commit runs (git writes
COMMIT_EDITMSG at prepare-commit-msg, after it), so a pre-commit hook reading the record would read
the PREVIOUS commit's message -- fail-open, and silently. Wired at `tools/git-hooks/commit-msg`,
which is live the moment it exists because core.hooksPath already points at that directory.

SCOPE, stated rather than left silent. This fires on a new tracked `.py` MODULE under a declared
code root -- not on a new function inside an existing module, which the director's sentence also
names. Function granularity is DEFERRED, not dropped: it would fire on nearly every commit, and a
gate that fires constantly is one people learn to route around (`--no-verify`), which is worse than
no gate. The module is also the unit the index has rows for, so the record and the answer share a
unit. Revisit if duplication reappears INSIDE modules; that would be evidence this scope is wrong.

FAIL-CLOSED, in all four directions (R15: an unavailable check is a FAILED check).
  * message file unreadable, while new modules are staged     -> REFUSE
  * the capability index cannot be built or queried           -> REFUSE (G6 cannot be evaluated)
  * mode file present but unreadable or holding an unknown word -> REFUSE
  * no mode file at all                                       -> GATE (strict is the default)
A commit that adds NO new code module is never touched, in any state.

ROLLOUT ESCAPE HATCH. `tools/write_time_gate.mode` holding `warn` downgrades every refusal to a
printed warning -- for de-fanging a false positive at 3am without a code change, matching the
precedent of `tools/moap_coherence_gate.mode`. It lands in `gate`, because §5 rules this the
immediate behaviour change; the flip is a deliberate one-line diff and never automatic.

R15 PROOF: `tests/tools/test_write_time_gate.py` -- every guard below has a source mutation proving
it fires alone, plus a vacuity guard (the whole suite passing while NO new module is ever detected
is the fail-open shape that would make this gate theatre).
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Reuse AO1's row builder and search verbatim -- this module must not re-derive the index it cites,
# or G6 would be checking a record against a second opinion of its own making (R15 tautology).
from tools.capability_index import build_rows, find  # noqa: E402

MODE_FILE = ROOT / "tools" / "write_time_gate.mode"
VALID_MODES = ("gate", "warn")

# Roots holding capability code. A new .py OUTSIDE these owes no record: tests, site assets and
# scratch are not capabilities anyone would later duplicate by not knowing they existed.
CODE_ROOTS = ("background/", "company/", "interface/", "saas/", "sim/", "simulation/", "tools/")

PART_CLASSES = ("CATALOGUE", "CUSTOM", "SUBSYSTEM")

# A record claiming the index found nothing. Checked against the LIVE index by G6, because this is
# the one claim in the record that an independent source can contradict.
_NOTHING_CLAIMED = re.compile(
    r"\b(none|nothing|no (existing|current|prior|other)|not? (existing )?match)", re.I)
_QUOTED_TERM = re.compile(r"[\"'“‘]([^\"'”’]{2,})[\"'”’]")

_HEADS = ("REUSE", "CLASS", "INDEX", "LIBRARY", "EVALUATED", "REJECTED")
_FIELD = re.compile(rf"^\s*({'|'.join(_HEADS)})\s*:\s*(.*)$", re.I)


# ── what owes a record ──────────────────────────────────────────────────────────────────────
def owes_a_record(added_paths: list[str]) -> list[str]:
    """The staged ADDED paths that are new capability modules. Pure -> mutation-testable.

    Excluded, each for a stated reason: anything outside CODE_ROOTS (not a capability), tests (a
    test is evidence about a capability, not one), `__init__.py` (packaging, no capability of its
    own), and non-`.py` (the index has no row to answer with)."""
    out = []
    for rel in added_paths:
        p = rel.strip().replace("\\", "/")
        if not p.endswith(".py") or Path(p).name == "__init__.py":
            continue
        if not p.startswith(CODE_ROOTS):
            continue
        if p.startswith("tests/") or "/tests/" in p or Path(p).name.startswith("test_"):
            continue
        out.append(p)
    return out


# ── parsing the record ──────────────────────────────────────────────────────────────────────
def parse_records(message: str) -> dict[str, dict[str, str]]:
    """{path: {field: value}} for every REUSE block in the commit message. Pure.

    A block opens at `REUSE: <path>` and runs to the next REUSE or the end. Continuation lines
    (indented, no recognised field head) append to the field in progress, so a long INDEX note may
    wrap -- a record refused for wrapping would just teach people to write shorter, worse notes."""
    records: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    field: str | None = None
    for line in message.splitlines():
        m = _FIELD.match(line)
        if m:
            head, value = m.group(1).upper(), m.group(2).strip()
            if head == "REUSE":
                current = {}
                records[value.strip().replace("\\", "/")] = current
                field = None
            elif current is not None:
                current[head] = value
                field = head
            continue
        if current is not None and field and line.strip() and line[:1].isspace():
            current[field] = (current[field] + " " + line.strip()).strip()
    return records


def index_terms(record: dict[str, str]) -> list[str]:
    """The quoted search terms in the INDEX line -- the evidence that a look happened. Pure."""
    return [t.strip() for t in _QUOTED_TERM.findall(record.get("INDEX", "")) if t.strip()]


def claims_nothing_exists(record: dict[str, str]) -> bool:
    """Does the record assert the index turned up nothing? Pure -- G6's trigger."""
    return bool(_NOTHING_CLAIMED.search(record.get("INDEX", "")))


# ── the guards ──────────────────────────────────────────────────────────────────────────────
def _guard_shape(path: str, record: dict[str, str]) -> list[str]:
    """G1-G5: the record exists and is internally complete for the class it declares."""
    findings = []
    cls = record.get("CLASS", "").strip().upper().split()[0] if record.get("CLASS") else ""
    if cls not in PART_CLASSES:
        findings.append(
            f"{path}: G2 CLASS is {cls or 'absent'} -- name one of {', '.join(PART_CLASSES)}. "
            f"The class IS the ecosystem answer; without it only half the gate's question is met.")
    if cls == "CATALOGUE" and not record.get("LIBRARY", "").strip():
        findings.append(
            f"{path}: G3 CLASS CATALOGUE with no LIBRARY named. Catalogue parts are always taken "
            f"from a mature library -- a hand-rolled one is the 2026-08-03 working-day calculator "
            f"again. Name the library, or the part is not CATALOGUE and the class is wrong.")
    if cls == "SUBSYSTEM":
        missing = [f for f in ("EVALUATED", "REJECTED") if not record.get(f, "").strip()]
        if missing:
            findings.append(
                f"{path}: G4 CLASS SUBSYSTEM with no {' and no '.join(missing)}. A subsystem may be "
                f"built custom only with a build-vs-buy note naming what was evaluated and why it "
                f"was rejected -- silence is a gap (director, 2026-08-05).")
    if not index_terms(record):
        findings.append(
            f"{path}: G5 INDEX quotes no search term. Record what you actually put through "
            f'capability_index.py, in quotes: INDEX: searched "term", "term" -- nearest is X.')
    return findings


def _guard_index_contradiction(path: str, record: dict[str, str], rows: list[dict]) -> list[str]:
    """G6: the record says the index found nothing, but the live index answers its own terms.

    This is the only guard with an INDEPENDENT source (R15 anti-tautology): every other guard reads
    the record against itself, so a record could be internally perfect and factually false. Here the
    filesystem-derived index gets to contradict the claim. It fires on the FALSE-NEGATIVE direction
    only -- claiming emptiness that is not there -- never on a builder who looked, found something,
    and chose to write fresh anyway. That choice is the director's to leave open, not this gate's."""
    if not claims_nothing_exists(record):
        return []
    hits = []
    for term in index_terms(record):
        for row in find(rows, term):
            if row.get("module") and row["module"] not in hits:
                hits.append(row["module"])
    if not hits:
        return []
    return [f"{path}: G6 the record says the index found nothing, but "
            f'"{index_terms(record)[0]}" and its siblings return {len(hits)} row(s): '
            f"{', '.join(hits[:4])}. Either the look did not happen, or the note is stale. "
            f"Finding something is not a refusal -- say what you found and why new code anyway."]


def evaluate(added_paths: list[str], message: str, rows: list[dict]) -> dict:
    """THE predicate. Pure given (staged adds, message, index rows) -> mutation-testable.

    Returns {"status": OK|REJECT, "findings": [...], "owed": [...]}. `owed` is reported even when
    empty so a caller (and a test) can tell "nothing to check" apart from "checked and clean" --
    the vacuity distinction that makes this gate falsifiable rather than reassuring."""
    owed = owes_a_record(added_paths)
    if not owed:
        return {"status": "OK", "findings": [], "owed": []}
    records = parse_records(message)
    findings: list[str] = []
    for path in owed:
        record = records.get(path)
        if record is None:
            findings.append(
                f"{path}: G1 no REUSE record. Before a new module: consult the index, then record "
                f"what you found and what you did about it. `python3 tools/write_time_gate.py "
                f"--explain {path}` prints the block with the live matches already in it.")
            continue
        findings += _guard_shape(path, record)
        findings += _guard_index_contradiction(path, record, rows)
    return {"status": "REJECT" if findings else "OK", "findings": findings, "owed": owed}


# ── mode + git IO ───────────────────────────────────────────────────────────────────────────
def read_mode(mode_file: Path | None = None) -> str:
    """`gate` (default, including when the file is absent) or `warn`. Raises on an unreadable file
    or an unknown word -- the caller turns that into a REFUSE, never into a silent pass: a mode file
    nobody can read is exactly the fail-silent shape that would make this gate optional by typo."""
    path = mode_file or MODE_FILE
    if not path.exists():
        return "gate"
    word = path.read_text(encoding="utf-8").strip().lower()
    if word not in VALID_MODES:
        raise ValueError(f"{path} holds {word!r}; expected one of {VALID_MODES}")
    return word


def staged_additions() -> list[str]:
    """Paths ADDED in this commit (read-only plumbing; never writes the index -- H24)."""
    env = {k: v for k, v in os.environ.items() if k != "GIT_PREFIX"}
    r = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
                       cwd=str(ROOT), env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git diff --cached failed (rc={r.returncode}): {r.stderr.strip()}")
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def explain(path: str) -> str:
    """The record block for `path`, pre-filled with what the index says right now."""
    stem = re.sub(r"[_/]+", " ", Path(path).stem).strip()
    # Drop the module being explained from its own near-matches: once the file exists on disk the
    # index has a row for it, and "nearest is the thing you just wrote" reads as a hit.
    rows = [r for r in find(build_rows(), stem) if r.get("path") != path]
    if rows:
        near = "; ".join(r["module"] for r in rows[:3])
        note = f'searched "{stem}" -- nearest {near} -- <why those do not fit>'
    else:
        note = f'searched "{stem}", "<second term>" -- no existing row covers this'
    return (f"REUSE: {path}\n"
            f"CLASS: <{'|'.join(PART_CLASSES)}>\n"
            f"INDEX: {note}\n"
            f"# CATALOGUE also needs   LIBRARY: <library it stands on>\n"
            f"# SUBSYSTEM also needs   EVALUATED: <libraries>  /  REJECTED: <why>\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="AO2 -- the write-time reuse gate (commit-msg hook).")
    ap.add_argument("message_file", nargs="?", help="path to COMMIT_EDITMSG (git passes this)")
    ap.add_argument("--explain", metavar="PATH", help="print the record block for a new module")
    args = ap.parse_args(argv)

    if args.explain:
        sys.stdout.write(explain(args.explain))
        return 0
    if not args.message_file:
        ap.error("a message file is required (or use --explain PATH)")

    try:
        added = staged_additions()
    except RuntimeError as exc:                       # cannot see the commit -> cannot clear it
        return _refuse([f"staged additions unreadable: {exc}"], "gate")
    if not owes_a_record(added):
        return 0                                      # ordinary commit -- pays nothing, always

    try:
        mode = read_mode()
    except (OSError, ValueError) as exc:
        return _refuse([f"mode file unusable: {exc}"], "gate")
    try:
        message = Path(args.message_file).read_text(encoding="utf-8")
    except OSError as exc:
        return _refuse([f"commit message unreadable: {exc}"], mode)
    try:
        rows = build_rows()
    except Exception as exc:                          # noqa: BLE001 -- any index failure is a failure
        return _refuse([f"capability index unavailable, so the record cannot be checked: {exc}"],
                       mode)

    result = evaluate(added, message, rows)
    if result["status"] == "REJECT":
        return _refuse(result["findings"], mode)
    return 0


def _refuse(findings: list[str], mode: str) -> int:
    """Emit the findings; return 1 in `gate`, 0 in `warn`. The text is identical in both modes so a
    warn-mode run reads exactly like the refusal it would be -- a quieter warning would let the
    escape hatch become a place findings go to die."""
    head = "❌ COMMIT REFUSED" if mode == "gate" else "⚠️  WARN ONLY (tools/write_time_gate.mode)"
    sys.stderr.write(f"\n[write-time-gate] {head} -- AO2, the write-time reuse gate.\n"
                     "Know, then choose: this refuses a missing RECORD, never your decision to "
                     "write new code.\n")
    for f in findings:
        sys.stderr.write(f"  • {f}\n")
    sys.stderr.write("  See docs/design/WRITE_TIME_GATE.md for the record format.\n")
    return 1 if mode == "gate" else 0


if __name__ == "__main__":
    raise SystemExit(main())
