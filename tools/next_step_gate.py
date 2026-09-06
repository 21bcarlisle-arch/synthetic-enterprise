"""A next step named in prose is a next step nobody can draw. This makes it a queue entry.

REUSE: tools/next_step_gate.py
CLASS: CUSTOM
INDEX: searched "next step", "follow on", "commit message gate", "trailer", "mint atom".
       `tools/write_time_gate.py` is the nearest organ and this is deliberately its SIBLING rather
       than an extension of it: that one refuses a commit that ADDS a capability without recording
       what it reused, this one refuses a commit that ADVANCES an atom without recording what comes
       next. Same hook, same shape (a required record, never a required decision), different
       question. `tools/maturity_map_store` supplies the queue; nothing here writes to it, because a
       gate that mints its own atoms would be a gate marking its own homework.

WHY THIS EXISTS
---------------
Director console, 2026-09-05, after reading a session report that named R1's next step:

    "You named that step in a report to me. It exists in a chat window and nowhere in your queue,
     so nothing can draw it -- and the queue offers machinery because machinery is what's in it.
     That's why the canon's ranking didn't move the share: I ranked things that weren't there.

     Fix that. When a session names a next step, it becomes work in the queue with a rank before
     the session ends. If it isn't worth minting, it wasn't worth saying."

The measured shape of the failure: PB4 landed, its commit message said the company would need the
observable to cross the seam, and that sentence was the ONLY place the work existed. The autonomous
side then drew machinery for the rest of the day -- correctly, because machinery was what the queue
held. The ranking canon could not move the share because the thing it ranked had never been minted.

WHAT IS ENFORCED, AND WHAT DELIBERATELY IS NOT
----------------------------------------------
A commit that NAMES AN OPEN ATOM must carry a `NEXT:` trailer. That is all. It is a record
requirement, not a work requirement -- exactly the line `write_time_gate` holds, and for the same
reason: a gate that forced a successor to exist would be a gate that made people mint filler.

    NEXT: <atom_id>            the successor is in the queue and drawable
    NEXT: none -- <reason>     nothing follows, and why

THE ESCAPE IS DELIBERATE AND COUNTED. `NEXT: none -- <reason>` cannot be prevented; any reason a
person types will satisfy any predicate a gate can write, and a gate that pretends otherwise is an
exhortation wearing a mechanism's clothes (this project's own most expensive recurring shape). So
instead of pretending, the escape RATE is measurable: `--report` derives it from the commit record.
A run of escapes is then a finding about how work is being closed, in the same way the
product/machinery split is a finding about how work is being chosen.

THE COUNT IS DERIVED FROM `git log`, NOT FROM A STORE, and the first version got this wrong.
It appended each escape to `docs/observability/next_step_escapes.jsonl` under `PROJECT`, which is
`Path(__file__).parent.parent` -- and the sanctioned landing move runs the hook chain inside a
`tempfile.mkdtemp(prefix="surgical-land-")` extract that is `rmtree`'d afterwards. So every escape
from every properly-landed commit was written into a directory that then ceased to exist, the file
was never even tracked, and the register read "one escape, ever": a flattering number produced by
counting nothing. A measurement whose subject is a throwaway checkout is the same shape as a
measurement whose subject is another process's uncommitted copy, and this project has paid for both.

The trailer is already in the commit message, which is durable, tracked, and cannot be lost to a
temp directory. So the record IS the store, and there is no store to lose.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
# RUN AS A SCRIPT BY THE COMMIT-MSG HOOK, not as `-m`, so the repo root is NOT on sys.path and
# `from tools import maturity_map_store` raises ModuleNotFoundError -- which this gate's own
# fail-open branch would then swallow on EVERY commit, silently, forever. It was doing exactly
# that when first wired: nine controls green, and the thing dead in production. The controls
# import the module (pytest has already set the path), so only running it the way the hook runs
# it could have found this.
if str(PROJECT) not in sys.path:
    sys.path.insert(0, str(PROJECT))

#: `NEXT:` at the start of a line, case-insensitive, to the end of that line.
_NEXT_RE = re.compile(r"^\s*NEXT:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)
#: A `none` declaration must carry a reason after a dash. The dash is what stops a bare "none"
#: passing; the reason's CONTENT is not judged, for the reason in the module docstring.
_NONE_RE = re.compile(r"^none\b\s*[-—:]{1,2}\s*(\S.*)$", re.IGNORECASE)


def open_atom_ids() -> set[str]:
    """Atom ids that are NOT yet at their target level -- the ones a successor could follow.

    A CLOSED atom is excluded on purpose: "what comes next" is a question about unfinished work,
    and demanding a trailer on the commit that finishes something is how a gate teaches people to
    type `none` reflexively, which would destroy the escape count's meaning.
    """
    from tools import maturity_map_store
    out = set()
    for atom in maturity_map_store.load_live_atoms():
        aid = atom.get("id")
        if not aid:
            continue
        try:
            current = int(atom.get("level_current") or 0)
            target = int(atom.get("level_target") or 0)
        except (TypeError, ValueError):
            continue
        if current < target:
            out.add(aid)
    return out


def atoms_named_in(message: str, known: set[str]) -> set[str]:
    """Which open atoms this commit message names -- BY FULL ID OR BY NUMBER.

    Substring rather than a word boundary for the full id, because atom ids are long and
    distinctive (`PB4_engagement_separated_from_elasticity`) and appear inside prose, backticks,
    paths and parentheses. A false positive costs one trailer; a false negative costs the point.

    THE NUMBER FORM IS WHY THIS GATE WAS SILENT FOR FIVE INSTANCES OF ITS OWN DEFECT. Measured
    2026-09-06 over the 17 commits that carried a NEXT trailer: only FOUR named an atom by its full
    id. Nobody writes `W2_18_the_housing_joint_the_sample_and_the_ceiling` in a subject line -- they
    write "W2_18 stage 1". So `named` came back empty, `verdict` took its "no open atom named;
    nothing to follow" branch, and the trailer was NEVER EXAMINED. Every successor I wrote was
    decorative, and the queue stayed empty while the commits looked compliant.
    Matching the number prefix as well lifts the gate from 4 of 17 to 10; the other 7 genuinely name
    no atom and are correctly left alone.

    A number matching several atoms returns all of them. Over-matching costs a trailer; under-
    matching is the failure above.
    """
    named = {aid for aid in known if aid in message}
    for aid in known:
        m = re.match(r"^([A-Z]+[0-9]+(?:_[0-9]+)?)_", aid)
        if m and re.search(rf"(?<![A-Za-z0-9_]){re.escape(m.group(1))}(?![A-Za-z0-9_])", message):
            named.add(aid)
    return named


def verdict(message: str, known_open: set[str]) -> tuple[bool, str]:
    """(passes, explanation). Pure, so the controls can drive it without a repo or a commit."""
    # THE SUBJECT IS THE COMMIT, NOT ITS TRAILER. `atoms_named_in` scans the whole message, so a
    # successor named on the NEXT line names itself -- and the self-succession refusal below would
    # then reject every correct trailer. Strip the trailers first: what is left is what this commit
    # actually advanced.
    body = _NEXT_RE.sub("", message)
    named = atoms_named_in(body, known_open)
    if not named:
        return True, "no open atom named; nothing to follow"

    found = _NEXT_RE.findall(message)
    if not found:
        return False, (
            "This commit advances " + ", ".join(sorted(named)) + " and records no next step.\n"
            "A next step named only in prose is one nothing can draw -- which is how the queue "
            "ends up holding only machinery.\n"
            "Add ONE line:\n"
            "    NEXT: <atom_id>          (the successor, already minted and ranked)\n"
            "    NEXT: none -- <reason>   (nothing follows, and why)\n"
            "Mint the successor first if it does not exist; `tools/maturity_map_store` holds the "
            "queue and the dial is what ranks it."
        )

    for raw in found:
        if _NONE_RE.match(raw):
            continue
        if raw in named:
            # SELF-SUCCESSION, and it is why this gate did not stop five instances of the defect
            # it was built for. Measured 2026-09-05: four of six NEXT trailers named
            # `W2_18_the_housing_joint_the_sample_and_the_ceiling` -- INCLUDING the commits that
            # were W2_18 work. Every one satisfied the gate and none of them put a drawable thing
            # in the queue.
            #
            # The reason is that a ruling-sized atom is not a queue unit. "The housing joint, the
            # sample and the ceiling" is a programme: a bounded tick reading it has no first move,
            # so it falls back to the machinery in front of it, which does. Naming it as your own
            # successor is true and useless.
            #
            # So the successor must be a DIFFERENT atom -- which forces the sub-step to be minted,
            # which is the whole point. `none -- <reason>` is still available and still counted.
            return False, (
                f"NEXT names `{raw}`, which this commit is already working on.\n"
                "An atom cannot be its own successor: naming it puts nothing new in the queue, and "
                "a ruling-sized atom is not something a bounded tick can pick up -- it draws the "
                "machinery in front of it instead. That is the exact failure this gate exists to "
                "prevent and it passed five times.\n"
                "Mint the next bounded step and name THAT, or `NEXT: none -- <reason>`."
            )
        if raw in known_open or _looks_like_atom_id(raw):
            continue
        return False, (
            f"NEXT: {raw!r} is neither an atom id in the live map nor a `none -- <reason>` "
            "declaration.\nA trailer that names something unminted is the same defect as no "
            "trailer at all: it is still only prose."
        )
    return True, "next step recorded"


def _looks_like_atom_id(value: str) -> bool:
    """An id shape the map does not currently hold.

    Accepted so a commit can name a successor it mints IN THE SAME COMMIT -- the map file is being
    written by that very commit, and reading the pre-commit copy would refuse exactly the workflow
    this gate is trying to produce. The shape check is what stops it degrading into "any text".
    """
    return bool(re.fullmatch(r"[A-Z]{1,3}[0-9]{0,3}_[a-z0-9_]{6,}", value.strip()))


def escape_rate(window: int = 200) -> dict:
    """How often the escape is taken, derived from the commit record itself.

    `declared` counts commits carrying any NEXT: trailer; `escaped` counts the subset declaring
    `none`. Commits with no trailer are not in either -- most commits name no open atom and are
    never asked for one, so including them would bury the rate in traffic.
    """
    done = subprocess.run(
        ["git", "log", f"-{int(window)}", "--format=%x00%B"],
        cwd=str(PROJECT), capture_output=True, text=True, timeout=120,
    )
    if done.returncode != 0:
        raise RuntimeError(f"git log failed: {done.stderr.strip()[:200]}")

    declared = escaped = 0
    reasons: list[str] = []
    for body in done.stdout.split("\x00"):
        trailers = _NEXT_RE.findall(body)
        if not trailers:
            continue
        declared += 1
        for raw in trailers:
            m = _NONE_RE.match(raw)
            if m:
                escaped += 1
                reasons.append(m.group(1)[:160])
                break
    return {"window": window, "declared": declared, "escaped": escaped,
            "rate": (escaped / declared) if declared else None, "reasons": reasons}


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "--report":
        r = escape_rate()
        pct = "n/a" if r["rate"] is None else f"{r['rate'] * 100:.0f}%"
        print(f"[next-step-gate] over the last {r['window']} commits: {r['declared']} declared a "
              f"next step, {r['escaped']} took the `none` escape ({pct}).")
        for reason in r["reasons"]:
            print(f"    none -- {reason}")
        return 0
    if len(argv) < 2:
        return 0
    try:
        message = Path(argv[1]).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0
    try:
        known = open_atom_ids()
    except Exception as exc:  # noqa: BLE001
        # FAILS OPEN, LOUDLY, AND THE CHOICE IS DELIBERATE. This gate runs on every commit in a
        # tree several lanes write at once; an unreadable map would otherwise wedge all of them.
        # One commit without a trailer is recoverable, a wedged tree is the thing that eats days.
        print(f"[next-step-gate] map unreadable, not blocking: {exc}", file=sys.stderr)
        return 0

    ok, why = verdict(message, known)
    if not ok:
        print("[next-step-gate] COMMIT REFUSED.\n" + why, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
