"""The landing door's per-path classifier, asked at the point a focus item is WRITTEN.

THE HALF THAT WAS STILL OPEN. `delivery_lane.path_note` (landed `dca82c164`) grades every path a
Lane 0 item names and prints the verdicts to the worker who DREW it. That closes the reader's half
and leaves the writer's wide open: the draw can only annotate prose that already exists, and the
orientation is where a spent pile becomes an item in the first place. Measured on the four live
focus items at 07:40 on 2026-09-22, every file path the focus list named graded `already landed` --
nothing to land on any of them -- and the list was authored blind to that.

IT IS ONE CLASSIFIER AND NOT A SECOND ONE. `_path_verdict` and `_path_roles` are imported from
`delivery_lane` rather than re-derived. Two answers to "what are these bytes" would drift, and the
draw's is the one with a reader, so this side would be the one nobody maintained.

THE ROLE SPLIT IS LOAD-BEARING HERE AND THE DRAW DOES NOT NEED IT. `already landed` on a path the
item names only to READ is the ordinary state of a file and says nothing at all; the same verdict on
a path the item asks to be CHANGED is the signal. Grading the union would fire on almost every item
ever written, and a note that fires on everything is read by nobody. `_path_roles` is the reading
that already paid for this distinction (`_claim_subject_paths`, 2026-09-22).

IT ANNOTATES AND NEVER REFUSES, for `path_note`'s reason exactly and one more of its own. An item
whose every named path has nothing to land is OFTEN still the right work -- the staging-archival
item on this very record names one tracked module and a directory full of deletions, so its change
set is vacuously landed and its work is entirely real. What this can say honestly is what it
MEASURED. What it must never do is turn that into a verdict about the item, so every concern below
carries the evidence that would overturn it: the directory tokens the door has no opinion about, and
the count of paths it could not grade.

NEVER RAISES, and an unanswerable tree yields no concerns. Same fail-soft direction as
`background/direction.py` itself: direction is advice, and advice that wedges the orientation when
git hiccups is worse than no advice.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

#: The two classes the commissioning item named, as stable strings a caller may switch on. Named
#: constants and not literals because `orient()` records them into `decisions.jsonl`, and a
#: reworded sentence would silently become a new class in an append-only store.
NOTHING_TO_LAND = "nothing to land"
REVERTING_REMEDY = "a remedy that would land the revert"

#: The remedy vocabulary that makes a `predates landing` path DANGEROUS rather than merely noted.
#: `isolate_hunks` separates hunks by AUTHOR and not by AGE, so an item that names a stale copy and
#: then prescribes it -- which is what `land-the-weather-hdd-pile-written-twice-and-committed-never`
#: did, and what cost three invocations -- is asking for the revert to be landed faithfully.
#: `--content` is here because `surgical_land --content` writes the bytes without reading the file,
#: which is the same trap with the door's name on it. The correct door is `tools.refresh_to_head`
#: and it is named in the concern's own text so the reader is not left to find it.
_REVERTING_REMEDY_WORDS = re.compile(r"isolate_hunks|--content", re.I)

#: Verdict tags that mean "this working copy has nothing to contribute". Only `already landed`
#: today; kept as a set because `_path_verdict` owns the vocabulary and a tag added there must be
#: an explicit decision here rather than a silent widening.
_SPENT_TAGS = frozenset({"already landed"})

#: The third door's own class. A hand-off is written at the END of a turn about work NOT YET DONE,
#: so what can be wrong with the bytes it names is not that they are spent -- it is that they are
#: not what the prose assumes the next tick will find. `predates landing` means the copy reverts a
#: landing; `deleted` means there is no file there at all. Either way the tick is sent at bytes the
#: handing-off seat did not describe.
HAND_OFF_STALE = "the bytes named are not what a hand-off assumes"

#: Tags where the WORKING COPY contradicts what a hand-off's prose is describing. Deliberately does
#: NOT include `dirty` or `holder work`: both are the ordinary state of a tree several lanes are
#: writing, and a hand-off naming one is usually right to. See `_hand_off_concerns`.
_WRONG_BYTES_TAGS = frozenset({"predates landing", "deleted"})

#: How many graded rows travel on a stored reading. The store is read into prompts, and the bound
#: is `path_note`'s for the same reason -- what was DROPPED is carried as a count, never silently.
_MAX_STORED_PATHS = 12


def _tracked(root: Path) -> set[str]:
    """Every file git tracks in `root`, or the empty set. ASKED OF `root`, NEVER OF THIS MODULE'S
    OWN TREE -- `delivery_lane._tracked_files` reads its own `PROJECT_DIR`, which in a linked
    worktree is the worktree, and confirming an item's paths against the wrong tree is how a real
    subject reads as prose that named nothing."""
    from background.delivery_lane import _git
    out = _git("ls-files", cwd=root) or ""
    return {line.strip() for line in out.splitlines() if line.strip()}


def _item_text(item) -> str:
    from background.delivery_lane import _ITEM_PROSE_KEYS
    if not isinstance(item, dict):
        return ""
    return " ".join(str(item.get(key) or "") for key in _ITEM_PROSE_KEYS)


def grade_item(item, root: Path, tracked: set[str] | None = None) -> dict:
    """One focus item's paths, split by role and graded by the landing door. Never raises.

    THE `directories` AND `ungraded` COUNTS TRAVEL WITH THE VERDICTS AND ARE NOT DECORATION. They
    are the two ways `every change-path is already landed` is true of an item whose work is
    entirely real, and a concern that omits them is a verdict wearing a measurement's clothes.
    """
    from background.delivery_lane import _NAMED_PATH, _path_roles, _path_verdict

    blank = {"id": "", "to_change": [], "mentioned": [], "directories": 0, "ungraded": 0,
             "concerns": []}
    try:
        text = _item_text(item)
        blank["id"] = str(item.get("id") or "") if isinstance(item, dict) else ""
        if not text:
            return blank
        known = _tracked(root) if tracked is None else tracked
        to_change, mentioned = _path_roles(text, known=known)

        def _rows(paths):
            return [(p,) + tuple(_path_verdict(root, p)) for p in paths]

        graded = {"id": blank["id"], "to_change": _rows(to_change), "mentioned": _rows(mentioned)}

        # THE DIRECTORY COUNT IS TAKEN FROM THE PROSE TOKENS AND NOT FROM `to_change`, because
        # `_path_roles` confirms against `git ls-files` and git tracks no directories -- so a bare
        # `docs/staging/` can never reach the role split at all. It is exactly the token that
        # makes an item's real subject invisible to this whole reading, which is why it is counted
        # separately rather than dropped with the other unresolvable prose.
        tokens = dict.fromkeys(tok.rstrip(".,;:)]}-") for tok in _NAMED_PATH.findall(text))
        for token in tokens:
            if token in known:
                continue
            tag, _detail = _path_verdict(root, token)
            if tag == "directory":
                graded["directories"] = graded.get("directories", 0) + 1
        graded.setdefault("directories", 0)
        graded["ungraded"] = sum(1 for _p, tag, _d in graded["to_change"] if tag == "ungraded")
        graded["concerns"] = _concerns(graded, text)
        return graded
    except Exception:
        # FAIL-SOFT AND SILENT IS RIGHT HERE AND NOWHERE NEAR THE VERDICTS THEMSELVES. A raise in
        # this walk means the annotation is missing, which the orienting session can see; the
        # thing that must never be silent is a classifier that RAN and could not decide, and that
        # arrives as the `ungraded` tag on its own row and is counted above.
        return blank


def _concerns(graded: dict, text: str) -> list[dict]:
    """The two classes, each with the evidence that would overturn it. Order is severity."""
    out: list[dict] = []
    change = graded.get("to_change") or []
    gradable = [row for row in change if row[1] != "ungraded"]

    reverting = [p for p, tag, _d in change if tag == "predates landing"]
    if reverting and _REVERTING_REMEDY_WORDS.search(text):
        out.append({
            "class": REVERTING_REMEDY,
            "paths": reverting,
            "says": (
                "this item names {n} path(s) whose working copy PREDATES the last landing to that "
                "path ({paths}) and its prose prescribes `isolate_hunks`/`--content`, which "
                "separate hunks by AUTHOR and not by AGE -- applied as written the remedy lands "
                "the revert. The door for an out-of-date copy is "
                "`python3 -m tools.refresh_to_head <path>`.".format(
                    n=len(reverting), paths=", ".join(reverting[:3]))),
        })

    if gradable and all(tag in _SPENT_TAGS for _p, tag, _d in gradable):
        out.append({
            "class": NOTHING_TO_LAND,
            "paths": [p for p, _t, _d in gradable],
            "says": (
                "every path this item asks to be CHANGED is identical to HEAD, so there is "
                "nothing to land on any of them: {paths}. THIS IS A MEASUREMENT AND NOT A VERDICT "
                "-- it is also true of an item whose real subject is a directory ({dirs} bare "
                "directory token(s) named here, which this door has no opinion about) or whose "
                "work is on files the prose has not named yet. If neither applies, the ask is "
                "spent before it is filed.".format(
                    paths=", ".join(p for p, _t, _d in gradable)[:300],
                    dirs=graded.get("directories", 0))),
        })
    return out


def grade(record, root: Path | None = None) -> list[dict]:
    """Every focus item in `record`, graded. `[]` for anything that is not a direction record."""
    from background import seat_continuation
    try:
        root = Path(root) if root is not None else seat_continuation.shared_tree_dir()
        focus = (record or {}).get("focus") or []
        if not isinstance(focus, list):
            return []
        tracked = _tracked(root)
        return [grade_item(item, root, tracked=tracked) for item in focus]
    except Exception:
        return []


def concerns(record, root: Path | None = None) -> list[dict]:
    """Flat `[{id, class, paths, says}]` over the whole record. What `orient()` records."""
    out = []
    for graded in grade(record, root):
        for concern in graded.get("concerns") or []:
            out.append({"id": graded.get("id", ""), **concern})
    return out


def note(record, root: Path | None = None) -> str:
    """The prose an authoring seat reads, or "" when there is nothing to say.

    "" AND NOT "no concerns" IS THE CHOICE, and it is the same one `path_note` made: this text is
    concatenated into a prompt that is already at its truncation limit, and a block that says
    nothing every time it runs teaches the reader to skip the block that one day says something.
    """
    from background import seat_continuation
    rows = concerns(record, root)
    if not rows:
        return ""
    try:
        where = Path(root) if root is not None else seat_continuation.shared_tree_dir()
    except Exception:
        where = Path(".")
    body = "".join("\n  * `{}` -- [{}] {}".format(r["id"], r["class"], r["says"]) for r in rows)
    return (
        "THE LANDING DOOR'S VERDICT ON THE FOCUS ITEMS THAT ARE LIVE RIGHT NOW, read from the "
        "SHARED tree {where} just now. The draw prints these to whoever DRAWS an item; this is the "
        "same classifier asked before the next one is WRITTEN, so a spent ask can be corrected "
        "instead of filed. It annotates and never refuses -- each row carries what would overturn "
        "it:{body}\n"
        "IF YOU CARRY ONE OF THESE ITEMS FORWARD, say in its `what` what is actually left to do on "
        "those paths, or drop it. An item whose change set has nothing to land costs a whole "
        "invocation to re-derive that.".format(where=where, body=body)
    )


def _hand_off_concerns(graded: dict, text: str) -> list[dict]:
    """The classes that are real at the HAND-OFF door, which are not the ones the orientation has.

    `NOTHING_TO_LAND` IS DELIBERATELY DROPPED HERE AND THAT IS THE WHOLE FINDING (2026-09-22). The
    commissioning item asked for `grade_item` to be called straight through. Measured over the
    live continuation store at 08:47, it fires on 183 of the 265 entries that name a change path
    (69%), and the rate falls 84% / 67% / 59% / 48% as the item names 1, 2, 3, 4+ paths -- against
    84 / 71 / 59 / 50 for a geometric 0.84^n. That geometry is the signature of a property of the
    TREE (each named file is independently ~84% clean) and NOT of the item.

    THE NUMBER MOVING IS BETTER EVIDENCE THAN THE NUMBER. The same walk 17 minutes earlier gave
    133 of 264 (50%) and 71 / 43 / 32 / 33 -- a geometric 0.71^n. Nothing about the 358 hand-offs
    changed in between; another lane committed a batch, and files that had been `dirty` became
    `already landed`. A reading that moves 19 points because somebody else ran `git commit` is not
    telling you anything about the item it is attached to.

    IT HAS TO BE THIS WAY. An orientation item can say "land this pile", so `already landed` may
    mean the ask is spent; a hand-off is written at the END of a turn about work NOT YET DONE, so
    `already landed` is the EXPECTED PRECONDITION and says nothing at all.

    THE TWO LIVE ENTRIES SHOWED IT FIRING EXACTLY BACKWARDS, which is why this is a rewrite and not
    a threshold. `restore-the-six-live-reverts-before-anything-regenerates-from-them` IS a pile item
    and its ask CAN go spent -- it stayed SILENT, because one of its six paths was still dirty. The
    item that commissioned this work names one file it intends to WRITE, where the verdict is
    meaningless -- and that is the one that fired.

    WHAT IS LEFT IS THE BYTES-CONTRADICT-THE-PROSE CLASS, and it is rare rather than universal:
    this door fires on 13 of the 359 entries (3.6%), all of them the stale class -- `predates
    landing` or `deleted`. `REVERTING_REMEDY` fires on NONE of them, which is the honest reading of
    a class inherited from a door where the remedy vocabulary is common and this one where a
    hand-off has no occasion to prescribe a landing for work that does not exist yet. It is kept
    anyway: it costs nothing, it is the stricter of the two, and the day a seat does write it, the
    row that names `refresh_to_head` is the one worth having. A concern that fires on 3.6% of a
    store is one a reader will still be reading in a month.
    """
    out = [c for c in (graded.get("concerns") or []) if c.get("class") != NOTHING_TO_LAND]
    rows = (graded.get("to_change") or []) + (graded.get("mentioned") or [])
    # NAMED AT ALL, not only named-to-CHANGE. The role split earns its keep for `NOTHING_TO_LAND`,
    # where `already landed` on a read-only path is the ordinary state of every committed file. It
    # earns nothing here: a hand-off that sends the next tick to READ a copy which reverts a
    # landing has misled it exactly as badly as one that sends it to write there.
    wrong = [(p, tag) for p, tag, _d in rows if tag in _WRONG_BYTES_TAGS]
    if wrong and not any(c.get("class") == REVERTING_REMEDY for c in out):
        out.append({
            "class": HAND_OFF_STALE,
            "paths": [p for p, _t in wrong],
            "says": (
                "this hand-off names {n} path(s) whose working copy is not what its prose "
                "describes ({rows}). `predates landing` means the copy REVERTS a landing and "
                "supplies nothing HEAD lacks -- the door is `python3 -m tools.refresh_to_head "
                "<path>`; `deleted` means there is no file there at all. THE NEXT TICK READS THIS "
                "HOURS FROM NOW and will trust the prose over the bytes. Say in `what` which "
                "state you mean, or name a path that is in it.".format(
                    n=len(wrong),
                    rows=", ".join("{} [{}]".format(p, t) for p, t in wrong[:3]))),
        })
    return out


def hand_off_reading(item, root: Path | None = None, now: float | None = None) -> dict:
    """One hand-off's paths, graded, stamped, and small enough to store. `{}` when unanswerable.

    THIS IS A MEASUREMENT WITH A CLOCK ON IT AND NOT A VERDICT THE DRAW SHOULD BELIEVE. The draw
    already runs `delivery_lane.path_note` fresh, so a second opinion stored hours earlier would be
    exactly this project's commonest rot -- a stale literal sitting in a sentence whose conclusion
    has since inverted. What the draw CANNOT compute, and the only reason these rows are kept, is
    the DIFFERENCE: the tree state when the piece was handed on versus now. `drift_note` is the
    only reader, and it reports movement rather than repeating the verdict.
    """
    try:
        from background import seat_continuation
        where = Path(root) if root is not None else seat_continuation.shared_tree_dir()
        # THE TWO WAYS THIS GRADES NOTHING ARE NOT THE SAME RESULT AND COLLAPSED INTO THE
        # FLATTERING ONE until the fail-soft test below caught it. `grade_item` swallows its own
        # exception and hands back a blank, so a hand-off naming no path and a hand-off graded
        # against a tree git could not read BOTH arrive as zero rows and zero concerns -- and the
        # note then says "nothing contradicting the prose", which is a clean verdict over an
        # unanswerable tree. An empty `git ls-files` is the cheapest honest witness: a real repo
        # always tracks something, so `readable: False` is carried and the note leads with it.
        known = _tracked(where)
        if not known:
            return {"at": float(now) if now is not None else time.time(), "root": str(where),
                    "paths": [], "not_graded": 0, "concerns": [], "readable": False}
        graded = grade_item(item, where, tracked=known)
        rows = (graded.get("to_change") or []) + (graded.get("mentioned") or [])
        text = _item_text(item)
        kept = [[p, tag] for p, tag, _d in rows[:_MAX_STORED_PATHS]]
        return {
            "at": float(now) if now is not None else time.time(),
            "root": str(where),
            "paths": kept,
            # NEVER SILENTLY TRUNCATED, for `_MAX_GRADED_PATHS`'s reason: a table that stops and
            # says nothing reads as "those were all of them".
            "not_graded": max(0, len(rows) - len(kept)),
            "concerns": _hand_off_concerns(graded, text),
            "readable": True,
        }
    except Exception:
        return {}


def hand_off_note(item, root: Path | None = None, now: float | None = None) -> str:
    """What the handing-off seat reads, the moment it hands on. Never "" -- see below.

    THE ONE PLACE THE "SAY NOTHING WHEN THERE IS NOTHING" RULE INVERTS, and the difference is the
    reader. `note` above is concatenated into a 60k orientation prompt, where a block that says
    nothing every time teaches the reader to skip the block that one day says something. This is
    the output of a command a seat JUST RAN and is looking straight at. There, silence is
    indistinguishable from the check not running -- and the quiet reading is itself informative:
    "names no tracked file at all" is the shape of a hand-off the next tick cannot locate.
    """
    # THE STORED READING IS PREFERRED AND THAT IS NOT AN OPTIMISATION. What the seat is shown has
    # to be the bytes the next tick will be handed; re-grading here would walk the tree a second
    # time and could legitimately return a DIFFERENT answer, leaving the seat correcting prose
    # against a reading nobody kept.
    reading = (item or {}).get("path_reading") if isinstance(item, dict) else None
    if not reading:
        reading = hand_off_reading(item, root, now)
    if not reading or reading.get("readable") is False:
        return ("  path check: the tree at {} could not be read, so NOTHING was graded -- this is "
                "NOT a clean verdict, and the next tick gets no write-time reading for this "
                "entry.".format((reading or {}).get("root", "the shared tree")))
    rows = reading.get("concerns") or []
    graded = reading.get("paths") or []
    if not rows:
        return ("  path check: {n} named path(s) graded against {root}, nothing contradicting the "
                "prose. `already landed` is NOT reported here -- for work not yet done it is the "
                "expected state, not a spent ask.".format(n=len(graded), root=reading.get("root")))
    body = "".join("\n  * [{}] {}".format(r["class"], r["says"]) for r in rows)
    return (
        "  PATH CHECK ON WHAT YOU ARE HANDING ON, read from {root} just now. It annotates and "
        "never refuses -- the entry is stored either way:{body}\n"
        "  Re-word the hand-off and run it again under the same id; a re-stamp replaces the "
        "entry.".format(root=reading.get("root"), body=body))


def drift_note(item, root: Path | None = None) -> str:
    """What has MOVED under a hand-off between its writing and this draw, or "".

    THE QUESTION THE DRAW STRUCTURALLY CANNOT ASK ITSELF, and the one the commissioning item's own
    WHY is about: two of the six reverts focus item 1 named were fixed by another lane between
    07:40 and 08:10, which is exactly the window a hand-off lives in. `path_note` grades the tree
    NOW and is right to; it has no record of what the handing-off seat saw, so "these were clean
    when this was written and are dirty now -- somebody has been working here since" is not
    available to it from any store but this one.

    IT REPORTS MOVEMENT AND NEVER RE-STATES THE VERDICT. Where the two readings agree there is
    nothing here to say, because `path_note` has already said it, freshly, three lines up.
    """
    try:
        prior = (item or {}).get("path_reading") or {}
        before = {p: tag for p, tag in (prior.get("paths") or [])}
        if not before:
            return ""
        from background import seat_continuation
        from background.delivery_lane import _path_verdict
        where = Path(root) if root is not None else seat_continuation.shared_tree_dir()
        moved = []
        for path, was in before.items():
            now_tag = _path_verdict(where, path)[0]
            if now_tag != was and "ungraded" not in (was, now_tag):
                moved.append((path, was, now_tag))
        if not moved:
            return ""
        hours = ""
        written = prior.get("at")
        if written:
            hours = " over the {:.1f}h since it was handed on".format(
                max(0.0, (time.time() - float(written)) / 3600.0))
        rows = "".join("\n  * `{}` -- was [{}] when handed on, now [{}]".format(p, a, b)
                       for p, a, b in moved[:6])
        return (
            "PATH DRIFT (what MOVED under this item{hours}): {n} of the {t} path(s) the handing-off "
            "seat graded are in a different state now. This is the only reading here that is not "
            "available from the tree alone -- the tags above are fresh and these are the "
            "CHANGE:{rows}\nA path that went `dirty` -> `already landed` was LANDED by somebody "
            "while this item waited, so the ask for it may be spent; one that went the other way "
            "has a lane in it right now.\n".format(
                hours=hours, n=len(moved), t=len(before), rows=rows))
    except Exception:
        return ""


def main(argv=None) -> int:
    """Print the note for a direction record. ALWAYS EXITS 0 -- this is advice, not a gate."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--record", default=None,
                        help="the DIRECTION.yaml to grade (default: the live one)")
    parser.add_argument("--root", default=None,
                        help="the tree to grade the paths against (default: the shared tree)")
    parser.add_argument("--json", action="store_true", help="print the concerns as JSON")
    args = parser.parse_args(argv)

    from background import direction as direction_mod
    path = Path(args.record) if args.record else direction_mod.DIRECTION_PATH
    try:
        import yaml
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print("could not read {}: {!r}".format(path, exc))
        return 0
    root = Path(args.root) if args.root else None
    if args.json:
        print(json.dumps(concerns(record, root), indent=1))
        return 0
    print(note(record, root) or "no concern: every focus item's change set has something to land, "
                                "or names no tracked file at all")
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/direction_path_check.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("direction_path_check")
    sys.exit(main())
