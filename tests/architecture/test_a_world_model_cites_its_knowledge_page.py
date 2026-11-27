"""K8 covers world models: a world module under an L3+ atom names the knowledge beneath it.

Director, 25 Nov 2026 (`docs/staging/advisor/done/DIRECTOR_RULING_K8_FOR_WORLD_MODELS_FORWARD_
BANDS_YES_AND_STEP_BACK_ON_THE_RETENTION_RESULT_2026-11-25.md` §1): K8 covers world models as well
as supplier capabilities. The census that found models built to their ceiling with no mechanism
page beneath them is `docs/staging/done/SEAT_FINDING_WORLD_MODELS_BUILT_TO_THEIR_CEILING_WITH_NO_
MECHANISM_PAGE_BENEATH_THEM_2026-11-24.md`.

One leg, no baseline list. Every `.py` under `sim/` or `simulation/` named in the `file_scope` of
an atom at `level_current >= 3` must carry, in its module docstring, either a path to a
`docs/market_research/` or `site/knowledge/` page that exists, or the words `Knowledge: GAP`.
A bare directory in a `file_scope` (W2_11 names all of `simulation`) is not a module and is not
graded here.

What it cannot see: whether the cited page carries the mechanism. A citation is the floor a reader
can follow; the census's own caveat applies.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from tools.maturity_map_store import load_atoms

ROOT = Path(__file__).resolve().parents[2]
_PAGE = re.compile(r"(docs/market_research/[\w./-]+|site/knowledge/[\w-]+)")
_GAP = re.compile(r"Knowledge:\s*GAP")


def world_modules_at_l3_plus() -> dict[str, list[str]]:
    mods: dict[str, list[str]] = {}
    for atom in load_atoms():
        if int(atom.get("level_current") or 0) < 3:
            continue
        for p in atom.get("file_scope") or []:
            p = str(p)
            if p.startswith(("sim/", "simulation/")) and p.endswith(".py"):
                mods.setdefault(p, []).append(atom["id"])
    return mods


def why_uncited(docstring: str | None) -> str | None:
    """None if the docstring cites an existing page or names a GAP; else the reason it does not."""
    doc = docstring or ""
    if _GAP.search(doc):
        return None
    cited = [m.rstrip(".,;:)") for m in _PAGE.findall(doc)]
    if any((ROOT / c).exists() for c in cited):
        return None
    if cited:
        return f"cites {cited}, none of which exists"
    return "names no docs/market_research or site/knowledge page and no 'Knowledge: GAP'"


def test_the_census_is_not_empty():
    # A census that finds no module passes every module.
    assert len(world_modules_at_l3_plus()) >= 10


def test_the_check_can_refuse():
    assert why_uncited("A model.\n\nIt does things.") is not None
    assert why_uncited("Knowledge: docs/market_research/no_such_page_anywhere.md") is not None
    assert why_uncited("Knowledge: GAP -- nothing published says this.") is None
    assert why_uncited("Knowledge: docs/market_research/ASSUMPTIONS.md.") is None


def test_every_world_module_under_an_l3_atom_cites_its_knowledge():
    reds = []
    for path, atoms in sorted(world_modules_at_l3_plus().items()):
        f = ROOT / path
        if not f.exists():
            reds.append(f"{path} ({', '.join(atoms)}): in file_scope but not on disk")
            continue
        reason = why_uncited(ast.get_docstring(ast.parse(f.read_text())))
        if reason:
            reds.append(f"{path} ({', '.join(atoms)}): {reason}")
    assert not reds, (
        "K8 covers world models (director, 25 Nov). Add a 'Knowledge: <page>' line to the module "
        "docstring, or 'Knowledge: GAP -- <what is not published>':\n  " + "\n  ".join(reds)
    )
