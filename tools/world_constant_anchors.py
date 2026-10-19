"""Every constant the world draws from cites its anchor or is a labelled evidence range.

Director steer, 19 Oct 2026 (`docs/staging/advisor/DIRECTOR_STEER_KNOWLEDGE_THAT_CHECKS_THE_WORLD_2026-10-19.md`),
item 1, "Anchor or range": "Every constant the world draws from must either cite its knowledge page
or source, or be marked as a labelled evidence range (W7 principle 1, W8). A check refuses a bare
number, and refuses 'placeholder' with no anchor named. Name the existing unanchored ones and
register them; don't fix them all at once. `DEFAULT_BAND_WEIGHTS` is the first entry."

WHY THIS IS NOT `tools/domain_constant_origins.py` WITH `simulation` ADDED TO ITS SCOPE. That scan
keeps the world out on purpose, because two of its three origins -- a company BELIEF, a NAMED
SIMPLIFICATION -- would let a world calibration be discharged by a code comment. The steer accepts
only two origins for the world, and neither is a comment about ourselves: a source, or a range.
The comment-reading and literal-detection are shared from that module rather than re-written.

WHAT COUNTS AS "A CONSTANT THE WORLD DRAWS FROM" -- said before it is measured. A module-level
upper-case name in `simulation/` or `sim/` bound to a numeric literal, or a container of nothing
but numeric literals, WITH AT LEAST ONE FLOAT IN IT. The float is the cut: shares, weights,
probabilities, means and elasticities -- what a draw is made from -- are written as floats. The
integer-only constants are overwhelmingly calendar and regulatory day counts, simulation years,
seeds and machine sizing (`PERIODS_PER_DAY`, `COOLING_OFF_PERIOD_DAYS`, `RESERVED_CPUS`); 130 of
them were bare on 2026-10-19, and demanding a citation for 48 periods in a day would spend the
rule on noise. The integer that DOES decide who is in the world -- founder count, prospect cap --
is the steer's item 3, a re-run on change, not an anchor.

WHAT DISCHARGES IT, read from the comment block immediately above the assignment (and its trailing
comment), by the same rule the company scan uses:

  * CITED -- the company scan's own citation pattern: a `docs/` path, a named publisher, a URL.
  * RANGE -- the words "EVIDENCE RANGE" or "LABELLED RANGE" (W7: "carry a labelled range, not a
    number"). The label is the claim that the value is one point in a stated band and something
    sweeps it; it is not a licence to write no source at all for a published figure.
  * "PLACEHOLDER" IS NEVER AN ANCHOR ON ITS OWN. A comment that says placeholder discharges only
    by citing what would replace it -- the 13 July "documented placeholder" for the fuel split
    named no source and read as owned debt for three months.

THE REGISTER is `docs/design/world_constant_anchor_register.txt`, one `path::NAME` per line, and
the control is an EXACT SET against it, not a count. A count lets one constant be anchored and a
new bare one take its slot unseen; the exact set reds both ways -- a new bare number is refused by
name, and an anchored one still listed must be struck, which is how the register records progress.
"""
from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

from tools.domain_constant_origins import _CITED, _comment_block, _is_numeric

PROJECT = Path(__file__).resolve().parent.parent

#: The world's two packages: `simulation/` (households, the run) and `sim/` (market history).
SCOPE = ("simulation", "sim")

REGISTER = PROJECT / "docs" / "design" / "world_constant_anchor_register.txt"

_NAME = re.compile(r"_?[A-Z][A-Z0-9_]*")
_RANGE = re.compile(r"\bEVIDENCE RANGE\b|\bLABELLED RANGE\b", re.I)
_PLACEHOLDER = re.compile(r"placeholder", re.I)


def _has_float(node: ast.AST) -> bool:
    return any(isinstance(n, ast.Constant) and isinstance(n.value, float) for n in ast.walk(node))


def anchor(comment: str) -> str | None:
    """`"cited"`, `"range"`, or None for a bare number. A placeholder must cite."""
    if _CITED.search(comment):
        return "cited"
    if _PLACEHOLDER.search(comment):
        return None
    if _RANGE.search(comment):
        return "range"
    return None


def _files(root: Path):
    for package in SCOPE:
        base = root / package
        if base.is_dir():
            yield from sorted(p for p in base.rglob("*.py") if "tests" not in p.parts)


def scan(root: Path | None = None) -> tuple[list[dict], list[str]]:
    """Every world constant in scope with its anchor, and the files that would not parse."""
    root = PROJECT if root is None else root
    rows: list[dict] = []
    unreadable: list[str] = []
    for path in _files(root):
        rel = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            unreadable.append(rel)
            continue
        lines = source.splitlines()
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target, value = node.targets[0], node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                target, value = node.target, node.value
            else:
                continue
            if not (isinstance(target, ast.Name) and _NAME.fullmatch(target.id)):
                continue
            if not (_is_numeric(value) and _has_float(value)):
                continue
            rows.append({"key": f"{rel}::{target.id}",
                         "anchor": anchor(_comment_block(lines, node.lineno))})
    return rows, unreadable


def bare(root: Path | None = None) -> set[str]:
    return {r["key"] for r in scan(root)[0] if r["anchor"] is None}


def registered(path: Path = REGISTER) -> set[str]:
    return {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")}


_HEADER = """\
# Constants the world draws from that cite no anchor and carry no labelled range.
# Written by `python3 -m tools.world_constant_anchors --write`; controlled as an EXACT SET by
# tests/architecture/test_a_world_constant_cites_its_anchor_or_is_a_labelled_range.py.
# Anchor one (cite its page or source, or label it EVIDENCE RANGE) and strike its line here.
# Director steer 19 Oct 2026, item 1. Rank by impact: docs/design/world_constant_impact_ranking.md.
"""


def write(root: Path | None = None, path: Path = REGISTER) -> int:
    keys = sorted(bare(root))
    first = [k for k in keys if k.endswith("::DEFAULT_BAND_WEIGHTS")]
    ordered = first + [k for k in keys if k not in first]
    path.write_text(_HEADER + "\n".join(ordered) + "\n", encoding="utf-8")
    return len(ordered)


def _main() -> int:  # pragma: no cover - operator surface
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true", help="rewrite the register from the tree")
    args = ap.parse_args()
    if args.write:
        print(f"registered {write()} bare world constants -> {REGISTER.relative_to(PROJECT)}")
        return 0
    rows, unreadable = scan()
    counts: dict = {}
    for r in rows:
        counts[r["anchor"]] = counts.get(r["anchor"], 0) + 1
    print(f"world constants in {'/, '.join(SCOPE)}/: {len(rows)}  "
          f"cited {counts.get('cited', 0)}  range {counts.get('range', 0)}  "
          f"bare {counts.get(None, 0)}  unparseable files {len(unreadable)}")
    new, struck = bare() - registered(), registered() - bare()
    for k in sorted(new):
        print(f"  NEW BARE   {k}")
    for k in sorted(struck):
        print(f"  ANCHORED, STRIKE FROM REGISTER   {k}")
    return 1 if new or struck else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
