#!/usr/bin/env python3
"""ONE-SHOT drain (2026-09-17): the map's duplicated dial provenance, stated once instead of 30.

WHY THIS EXISTS AS A SCRIPT AND NOT AS THIRTY HAND EDITS. Six paragraphs of dial provenance were
pasted onto 30 rows between them -- 6,814 bytes of byte-identical text -- and each one's subject is
a FAMILY of rows (the R1-R5 re-ranking, the EP6 block lift, the three-stage supersession, the
phase-1 dial inheritance, two "minted ahead of its predecessor" mints) rather than the row it sits
on. The copies were not merely wasteful: one of them argues a derivation for dial 45 while sitting
on a row carrying 50, and the paragraph above it says so. That is what recitation costs.

THE CONTROL IS THE POINT, and it is why this is a script: a comment drain must not be able to
change a single parsed value. `verify()` re-loads BOTH halves after the rewrite and compares the
atom records for deep equality against before. If any field, any order, any value moved, it refuses
and writes nothing. Run with --check to prove the tree is already drained (idempotent, so it is
also the falsifier for anyone asking whether this landed).

The removed text is not deleted from the record: each paragraph is now in
docs/design/MATURITY_MAP.md section 8, once, naming the rows it covers.

    python3 -m tools.drain_map_duplicated_provenance --check   # exit 0 == already drained
    python3 -m tools.drain_map_duplicated_provenance           # apply, verified
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
LIVE = PROJECT / "docs" / "design" / "maturity_map.yaml"
CLOSED = PROJECT / "docs" / "design" / "maturity_map_closed.yaml"

#: (file, exact text to delete, expected copies). The text is the whole duplicated comment run,
#: extracted from the file itself rather than retyped -- a retyped block matches nothing and a
#: drain that matches nothing reports success having done nothing.
#:
#: ORDER MATTERS AND THE FIRST RUN PROVED IT. The three-stage supersession block below ENDS with
#: its own copy of the "Derived, not picked" paragraph, so asking for that paragraph first finds 11
#: copies where the census said 9 and the run refused rather than deleting two blocks it had not
#: been told about. The containing block is therefore removed FIRST, which leaves exactly the 9
#: free-standing copies the census counted.
DELETIONS: list[tuple[Path, str, int]] = [
    (LIVE, """    #   SUPERSEDED 2026-09-05 by the director's three-stage sequencing, which he said
    #   supersedes the ranking where they conflict. The derivation above was for 45 and is
    #   NOT redone here, because the sequence is not a weighting argument: it is first,
    #   second, only then. MEASURED after the change -- stage 1 takes 26.2% of the
    #   dial-weighted draw (300 of 1144 over 93 drawable atoms), stage 2 13.1%. That is a
    #   PREFERENCE, not a sequence, and no dial value can make it one while 85 other atoms
    #   remain drawable. What the dial can do it now does; the order itself is held by the
    #   seat and by the direction record, and that gap is reported to the director.
  #   Derived, not picked: 45 gives the eleven R1-R5 atoms 75% of a dial-weighted draw
  #   against the other 71 drawable atoms' total weight of 163. One draw in four still
  #   goes elsewhere, which is what keeps a broken machine fixable without it becoming
  #   the week. A change of WEIGHTS, not of machinery (§5).
""", 2),
    (LIVE, """  #   Derived, not picked: 45 gives the eleven R1-R5 atoms 75% of a dial-weighted draw
  #   against the other 71 drawable atoms' total weight of 163. One draw in four still
  #   goes elsewhere, which is what keeps a broken machine fixable without it becoming
  #   the week. A change of WEIGHTS, not of machinery (§5).
""", 9),
    (LIVE, """  #   reading accepted for EP6 on 24 August: epoch position alone never reserves an atom,
  #   because typing an interface changes how the two sides speak, not what the company
  #   faces or how hard its world is. These now rank BELOW R1-R5 (§2), by weight not by block.
""", 7),
    (LIVE, """  #   held by blocked_on, and dropping under the 45 product floor would strip the exemption.
""", 6),
    (LIVE, """  #   director's fifth instance of "the follow-on was not in the queue" was traced to a NEXT
  #   trailer naming W2_18 -- the whole ruling deliverable -- which is true and undrawable. A
  #   bounded tick cannot pick up "the housing joint"; it can pick up this.
""", 2),
    (CLOSED, """  #   tick reading "derive the weather cells" has no first move -- the third time that shape has
  #   left an expensive prerequisite finished and its work undrawn. The HadUK pull completed
  #   2026-09-05 (318 files, 19.8 GB, zero failures) and nothing was drawn for eighteen hours.
""", 4),
]

#: Four of the six paragraphs continue a sentence STARTED on the field's own inline comment, so
#: deleting the block alone would leave "order is", "because the", "and a bounded" dangling. The
#: inline line is rewritten to a complete sentence that still names its subject.
REWRITES: list[tuple[Path, str, str, int]] = [
    (LIVE,
     "  block_reason: null    # LIFTED by DIRECTOR_CANON_RERANKING_THE_ARC_2026-09-04 §4, on the\n",
     "  block_reason: null    # LIFTED by DIRECTOR_CANON_RERANKING_THE_ARC_2026-09-04 §4.\n", 7),
    (LIVE,
     "  dial_inherited: 60    # the phase-1 parent's, not decayed by phase number; order is\n",
     "  dial_inherited: 60    # the phase-1 parent's; order held by blocked_on, not by the dial.\n", 2),
    (LIVE,
     "  dial_inherited: 50    # the phase-1 parent's, not decayed by phase number; order is\n",
     "  dial_inherited: 50    # the phase-1 parent's; order held by blocked_on, not by the dial.\n", 4),
    (LIVE,
     "  dial_inherited: 60    # STAGE 1. Minted BEFORE the work that precedes it finished, because the\n",
     "  dial_inherited: 60    # STAGE 1, minted ahead of W2_18 -- MATURITY_MAP.md §8.\n", 2),
    (CLOSED,
     "  dial_inherited: 60    # STAGE 1. Minted 2026-09-07 because W1_14 is ruling-sized and a bounded\n",
     "  dial_inherited: 60    # STAGE 1, minted ahead of W1_14 -- MATURITY_MAP.md §8.\n", 4),
]


def duplicated_comment_blocks(text: str, min_bytes: int = 1) -> dict[str, list[int]]:
    """{comment run: the 1-indexed lines it starts on}, for every run appearing MORE THAN ONCE.

    THE CLASS, NOT THE SIX INSTANCES. This is what `tests/design/` asks of the live map, so the
    control is keyed to the property -- shared reasoning belongs in one place -- rather than to
    today's answer. A check spelling out the six paragraphs would go green the moment someone
    pasted a SEVENTH, which is the shape this repository keeps paying for.

    `min_bytes` defaults to 1 because after the drain there are NO duplicated runs at any size in
    either half, so there is no floor to justify and none is invented. A future run that genuinely
    needs one should raise it against a measurement, and say what it measured."""
    from collections import defaultdict

    runs: dict[str, list[int]] = defaultdict(list)
    current: list[str] = []
    start = 0
    for i, line in enumerate(text.splitlines(keepends=True)):
        if line.strip().startswith("#"):
            if not current:
                start = i
            current.append(line)
        else:
            if current:
                runs["".join(current)].append(start + 1)
                current = []
    if current:
        runs["".join(current)].append(start + 1)
    return {
        block: lines for block, lines in runs.items()
        if len(lines) > 1 and len(block.encode("utf-8")) >= min_bytes
    }


def plan() -> dict[Path, str]:
    """The rewritten text of each half, or a refusal. Nothing is written here."""
    texts = {p: p.read_text(encoding="utf-8") for p in (LIVE, CLOSED)}
    out = dict(texts)
    for path, block, expected in DELETIONS:
        found = out[path].count(block)
        if found != expected:
            raise SystemExit(
                f"REFUSED: expected {expected} copies of a {len(block)}B block in {path.name}, "
                f"found {found}. The map has moved on -- re-measure the duplicates rather than "
                f"letting this delete a different number of them.\n  first line: "
                f"{block.splitlines()[0].strip()[:90]}"
            )
        out[path] = out[path].replace(block, "")
    for path, old, new, expected in REWRITES:
        found = out[path].count(old)
        if found != expected:
            raise SystemExit(
                f"REFUSED: expected {expected} copies of the inline line {old.strip()[:70]!r} in "
                f"{path.name}, found {found}. A dangling sentence would be left behind."
            )
        out[path] = out[path].replace(old, new)
    return out


def verify(before: dict[Path, str], after: dict[Path, str]) -> None:
    """A COMMENT DRAIN MAY NOT MOVE A SINGLE PARSED VALUE. Deep equality over the atom records of
    both halves, not a count: a drain that dropped a field would keep the count."""
    for path in before:
        old = yaml.safe_load(before[path])
        new = yaml.safe_load(after[path])
        if old != new:
            old_ids = [a.get("id") for a in (old or [])]
            new_ids = [a.get("id") for a in (new or [])]
            if old_ids != new_ids:
                raise SystemExit(f"REFUSED: {path.name} atom ids changed -- {len(old_ids)} -> {len(new_ids)}")
            for a, b in zip(old, new):
                if a != b:
                    keys = {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
                    raise SystemExit(
                        f"REFUSED: {path.name} atom {a.get('id')} changed in {sorted(keys)} -- a "
                        "comment drain must not touch a value"
                    )
            raise SystemExit(f"REFUSED: {path.name} parsed differently for a reason not localised")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="exit 0 if already drained, 1 if not")
    args = ap.parse_args()

    before = {p: p.read_text(encoding="utf-8") for p in (LIVE, CLOSED)}
    if args.check:
        # Idempotence IS the check: if no copy of any block is left, the drain has landed.
        left = sum(before[path].count(block) for path, block, _ in DELETIONS)
        print(f"duplicated provenance blocks still in the map: {left}")
        return 0 if left == 0 else 1

    after = plan()
    verify(before, after)
    saved = sum(len(before[p].encode()) - len(after[p].encode()) for p in before)
    for path, text in after.items():
        path.write_text(text, encoding="utf-8")
    print(f"drained {saved} bytes of duplicated dial provenance; parsed content proven identical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
