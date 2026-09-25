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

THE SECOND TRIGGER: THE MAP DIFF, NOT THE PROSE (2026-09-25)
------------------------------------------------------------
Wiring this gate into `tools/surgical_land.py` (68717e7e1) made it ABLE to fire on trunk traffic it
could not previously reach. It did not make anything fire it. Measured the same day over the last
200 first-parent commits, with the open-atom set read from the map:

    110 atoms open, 100 distinct number forms, and exactly ONE commit naming any of them.

So the gate refused 1 commit in 200, correctly, and was unasked on the other 199 -- because it asked
its question only of the MESSAGE. A message is the author's account of what a commit did; the map is
the project's record of it, and the two had come apart completely.

A commit whose staged diff MOVES an atom's `level_current` now owes a trailer whatever its prose
says. The message-naming leg is kept as well: it is the cheaper half and it catches the commit that
advances an atom without touching the map -- which is most of them, and is itself the finding in
`docs/staging/SEAT_FINDING_THE_NEXT_STEP_GATE_IS_REACHABLE_ON_ONE_COMMIT_IN_200_AND_NO_ATOM_HAS_
MOVED_IN_241_2026-09-25.md`.

THE TRIGGER IS THE VALUE, NOT THE LINE, and that distinction was measured rather than assumed.
Over the last 120 first-parent commits touching the map, 32 add and remove a line containing
`level_current` and only 31 move a value: `2cc924ed9` rewrote the trailing COMMENT on a level line
that stayed at 2. A line-keyed trigger would have demanded a successor for a bookkeeping edit. (The
same census says 89 of those 120 touch the map and move no level at all -- so a trigger keyed merely
to the map being STAGED would ask ~4x as often and be wrong most times it asked.) Prediction and
result: `docs/staging/records/PREREG_HOW_OFTEN_A_MAP_COMMIT_ACTUALLY_MOVES_A_LEVEL_VALUE_
2026-09-25.md`; I predicted 20-26 and the answer was 31, so the value parse is worth one commit in
120 on the record and is kept for the property, not for the count.

A WITHDRAWN LEVEL IS A MOVE TOO. `level_promotion_gate.level_increases` returns increases only --
correctly, because ITS question is whether a promotion was authorised. This gate's question is
different: an atom dropped from 2 to 0 is a claim withdrawn, and "what comes next" is exactly what a
reader needs. Keying to increases would have made that branch silent by construction. Nothing in the
last 120 map commits moves a level DOWN, so history cannot exercise that branch and the control is
the only evidence it works -- which is why one is written for it specifically.

AND THIS LEG IS NOT FAIL-OPEN BY ACCIDENT. When the map is absent from the index -- most commits --
there is no move, and asking nothing is the right answer, not a swallowed failure. When the map IS
staged and cannot be read, that is a real failure and it is reported on stderr with its cause rather
than passed off as "no atom moved". Those two look identical from outside if you let them.
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

# AFTER the path insert, for the reason immediately above -- this gate runs as a script. The map
# readers are IMPORTED, never reimplemented: `atom_levels` is the parse `level_promotion_gate`
# already uses to compare levels across a commit, `_whole_map` is its both-halves reader, and
# `MAP_PARTS_REL` is the store's single declaration of which files the map consists of.
#
# AT MODULE LEVEL, so a rename in `level_promotion_gate` fails on the renamer's OWN commit with a
# traceback naming the symbol, rather than inside this gate's fail-open branch where the last such
# import error sat swallowed on every commit for a whole wiring. It adds no wedge surface that is
# not already there: `tools/git-hooks/pre-commit` runs `level_promotion_gate` itself, so a tree
# where this import cannot resolve is a tree where the pre-commit chain was already refusing.
from tools.level_promotion_gate import _staged_names, _whole_map, atom_levels  # noqa: E402
from tools.maturity_map_store import MAP_PARTS_REL  # noqa: E402

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


def atoms_whose_level_moved(old_map_text: str, new_map_text: str) -> dict[str, tuple[int, int]]:
    """{atom_id: (from, to)} for atoms whose `level_current` VALUE differs between two map texts.

    Pure, so the controls can drive it without a repo -- and keyed to the VALUE for the reason in
    the module docstring: a rewritten comment on a level line is not a move, and there is a real
    commit in the record that does exactly that.

    An atom in only one of the two texts is NOT returned. Minting an atom is not advancing it, and
    removing one is not either; both halves of the map are read by the caller, so an atom moving
    between the live and closed files is present in both texts and is judged on its value like any
    other. Both values must be ints: a level that is not a number is a malformation for
    `level_promotion_gate` to refuse, and reading it as a move here would report a parse defect as
    an unrecorded successor.
    """
    old_levels = atom_levels(old_map_text)
    new_levels = atom_levels(new_map_text)
    moved: dict[str, tuple[int, int]] = {}
    for aid, new in new_levels.items():
        old = old_levels.get(aid)
        if isinstance(old, int) and isinstance(new, int) and old != new:
            moved[aid] = (old, new)
    return moved


def staged_level_moves() -> dict[str, tuple[int, int]]:
    """What this commit's STAGED map does to atom levels. {} when the map is not being committed.

    `_whole_map` is called rather than copied. It resolves BOTH halves of the map at a revision and
    carries the reasoning for why one half is not enough (an atom refiled from live to closed reads
    as a deletion when you look at one file), and it goes through the git-env-safe read-only
    plumbing `level_promotion_gate` established for running inside a commit hook. A second
    implementation here is the shape this project pays for most -- one rule, two copies, fixed in
    one of them.

    `:<path>` is the INDEX, which is exactly this commit's content: in an ordinary `git commit` the
    hook runs against the staged tree, and inside `surgical_land`'s extract the index is seeded from
    the PARENT and the landing's paths are `git add`ed onto it, so `git show :<path>` reads as this
    commit there too. That is the property that makes this trigger reachable through the sanctioned
    landing door at all, and it is asserted rather than assumed --
    `surgical_land._make_standalone_repo` states it and `materialise` stages before it overlays.
    """
    if not _map_is_staged():
        return {}
    new_text = _whole_map(":")
    if new_text is None:
        raise RuntimeError("the map is staged but no half of it could be read from the index")
    old_text = _whole_map("HEAD:")
    # A repo with no HEAD (the very first commit) has no baseline, so nothing has MOVED. That is a
    # different statement from "the map could not be read", and it must not be reported as one.
    return atoms_whose_level_moved(old_text or "", new_text)


def _map_is_staged() -> bool:
    """Is any half of the map in this commit's staged set?

    Asked separately from reading it, because `_whole_map(":")` returns the map for EVERY commit --
    `:<path>` resolves from the index, which holds every tracked file whether or not this commit
    touches it. Without this the gate would parse both halves of a 300KB map on every commit in the
    tree to discover, almost always, that nothing changed.

    `_staged_names` is the SAME reading `level_promotion_gate.main()` uses to decide whether it runs
    at all, called rather than re-rolled so the two gates cannot come to disagree about what this
    commit stages. It returns `[]` rather than raising when git cannot answer -- inherited, and left
    alone: the only way that read fails is a git that is broken or not a repo, and a commit does not
    survive either, so a louder failure here would be a control guarding a case that cannot reach it.
    """
    return any(rel in set(_staged_names()) for rel in MAP_PARTS_REL)


def verdict(message: str, known_open: set[str],
            moved: dict[str, tuple[int, int]] | None = None) -> tuple[bool, str]:
    """(passes, explanation). Pure, so the controls can drive it without a repo or a commit.

    `moved` is what the STAGED MAP DIFF says this commit did -- {atom_id: (from, to)} from
    `staged_level_moves()`. It defaults to nothing moved, so every caller that asks only the old
    question gets the old answer; `main()` is what supplies it.
    """
    # THE SUBJECT IS THE COMMIT, NOT ITS TRAILER. `atoms_named_in` scans the whole message, so a
    # successor named on the NEXT line names itself -- and the self-succession refusal below would
    # then reject every correct trailer. Strip the trailers first: what is left is what this commit
    # actually advanced.
    body = _NEXT_RE.sub("", message)
    named = atoms_named_in(body, known_open)
    moved = dict(moved or {})
    # THE MAP IS NOT FILTERED THROUGH `known_open`, AND THAT IS THE DEPARTURE FROM THE NAMING LEG.
    # `open_atom_ids` excludes an atom already at target because MENTIONING a finished atom advances
    # nothing -- a commit that merely says "as W2_18 established" must not be asked for a successor.
    # A MOVE is not a mention. A move that lands on target is a closure, and "what follows this" is
    # the question the director asked for at exactly that moment. `none -- <reason>` remains
    # available for the closure that genuinely ends a line of work, and remains counted.
    subjects = named | set(moved)
    if not subjects:
        return True, "no open atom named and no level moved; nothing to follow"

    found = _NEXT_RE.findall(message)
    if not found:
        return False, (
            "This commit advances " + ", ".join(sorted(subjects)) + " and records no next step.\n"
            + _why_this_commit_is_asked(named, moved) +
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
        if raw in subjects:
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


def _why_this_commit_is_asked(named: set[str], moved: dict[str, tuple[int, int]]) -> str:
    """WHICH trigger fired, in the refusal itself.

    Two legs can refuse a commit here and they call for different fixes: the message leg is often
    satisfied by rewording, the map leg never is. A refusal that did not say which one it was would
    send half its readers to edit the wrong thing -- and it would also make the two legs
    indistinguishable to a control, so a mutation disabling one would be caught by the other and
    read as proof that the disabled leg works.
    """
    lines = []
    if moved:
        lines.append(
            "THE MAP SAYS SO, whatever the message says: this commit's staged "
            "`docs/design/maturity_map.yaml` moves "
            + ", ".join(f"`{aid}` {frm} -> {to}" for aid, (frm, to) in sorted(moved.items()))
            + ".\n"
        )
    if named:
        lines.append(
            "The message names " + ", ".join(sorted(named)) + ", which the map still has open.\n"
        )
    return "".join(lines)


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

    try:
        moved = staged_level_moves()
    except Exception as exc:  # noqa: BLE001
        # Fails open on the SAME reasoning as the branch above and NOT on the same silence: this
        # one only runs when the map is actually in the commit, so reaching it means a map that is
        # being written and cannot be read -- rare, and worth a distinct line. The message leg still
        # runs; `moved` being empty narrows the gate, it does not disable it.
        print(f"[next-step-gate] staged map unreadable, asking the message only: {exc}",
              file=sys.stderr)
        moved = {}

    ok, why = verdict(message, known, moved)
    if not ok:
        print("[next-step-gate] COMMIT REFUSED.\n" + why, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
