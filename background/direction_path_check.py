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
