"""THE REGISTER OF DERIVED ARTEFACTS — the class closure for the derived-artefact wedge.

WHY THIS EXISTS (R10: an absurdity-class defect may not close on an instance fix).
Four publish-gate wedges on 2026-08-09/10 had the same shape. A markdown document under
`docs/design/` is a PROJECTION of committed state (the maturity map, the `**Advances:**`
declarations in `docs/staging/**`). Each such document ships a `--write` CLI that renders it and
a blocking `--check` test that fails when the rendering and the sources disagree. Nothing ever
ran `--write`. So an ordinary, required act — minting an atom, archiving a finding to
`staging/done/` — silently invalidated a committed artefact that a blocking test checks, and
publishing wedged for hours until a worker tick hand-ran the regeneration:

    2026-08-09  cause 3  FORWARD_ATTACHMENT_LEDGER.md    stale after a staging archive
    2026-08-09  cause 4  PULL_FORWARD_PROPOSALS.md       stale after three findings staged
    2026-08-10  (this)   BLOCKED_ATOM_VISIBILITY.md      stale after 7 atoms minted (249 -> 256)

The filed finding (WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS_2026-08-09)
named the class and left ONE question open: whether regeneration belongs in the publish path or
in the staging-archive path, "both defensible, wants a design pass, not a guess".

THE ANSWER IS THE PUBLISH PATH, and this wedge decided it on evidence rather than taste: today's
drift was caused by a MAP MINT, not by a staging archive at all. A repair wired to the archive
path would not have prevented it. The publish path is the only place that is trigger-agnostic —
it repairs whatever went stale, however it went stale, at the one moment staleness does harm.

DERIVE FROM HEAD, NOT FROM THE TREE. Since DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09 the
gate's subject is a clean checkout of HEAD ("publishing tests committed truth only; the working
tree belongs to the lanes"). That makes the obvious implementation WRONG: regenerating in the
working tree renders a projection of UNCOMMITTED sources, which the gate — re-deriving at HEAD —
would then red on. It would swap a stale-artefact wedge for a phantom-artefact wedge. So
`repair_from` renders inside the HEAD checkout the gate already materialises, and copies the
rendering out into the real tree to be committed. What lands is exactly what the gate re-derives.

FIXED POINT, NOT ONE PASS. `forward_attachment_register` scans `docs/design/**` for its own
sources, so repairing one artefact can invalidate another. `repair_from` therefore iterates to a
fixed point and REPORTS non-convergence rather than looping or silently giving up — an
oscillating pair is a real defect and must be visible as one, not smoothed over.

THE REGISTER IS FAIL-CLOSED, NOT A LIST SOMEONE MAINTAINS. A hand-kept index of derived
artefacts is exactly the fail-open control this project has been bitten by before
(`feedback_index_is_a_fail_open_control`): the next derived artefact is simply absent from it and
inherits the whole hole. So `discover()` finds derived artefacts from the SOURCE — an AST scan
for a module that both takes `--write` and owns a module-level `docs/design/*.md` path — and
`unregistered()` is the difference. The completeness test reds when they disagree, so a new
derived artefact cannot ship unregistered. Discovery deliberately errs toward INCLUSION (a
module that merely reads such a path is flagged): over-inclusion costs one register line, while
under-inclusion silently recreates the class.
"""
from __future__ import annotations

import argparse
import ast
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

# How many repair passes before non-convergence is declared a defect. Two artefacts that
# invalidate each other need 2; anything beyond 3 is an oscillation, not slow convergence.
MAX_REPAIR_PASSES = 3


@dataclass(frozen=True)
class DerivedArtefact:
    """One projection: the module that renders it, and the path it renders to."""

    module: str          # importable module path, e.g. "background.blocked_atom_visibility"
    rendered: str        # repo-relative path of the rendering

    @property
    def source_file(self) -> str:
        return self.module.replace(".", "/") + ".py"


# THE REGISTER. Every entry must be discoverable by `discover()` and vice versa — the
# completeness test enforces both directions, so this tuple cannot silently fall behind.
REGISTER: tuple[DerivedArtefact, ...] = (
    DerivedArtefact("background.blocked_atom_visibility",
                    "docs/design/BLOCKED_ATOM_VISIBILITY.md"),
    DerivedArtefact("background.forward_attachment_register",
                    "docs/design/FORWARD_ATTACHMENT_LEDGER.md"),
    DerivedArtefact("background.pull_forward_proposal",
                    "docs/design/PULL_FORWARD_PROPOSALS.md"),
)

# Trees scanned for derived artefacts. Both are machine-owned code trees; a derived artefact
# living anywhere else would be a layering defect in its own right.
SCANNED_TREES = ("background", "tools")


# ── discovery: the INDEPENDENT oracle the register is measured against ──────────────────────

def _takes_write_flag(tree: ast.Module) -> bool:
    """True if the module registers a `--write` argparse option."""
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and getattr(node.func, "attr", None) == "add_argument"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == "--write"):
            return True
    return False


def _design_markdown_constants(tree: ast.Module) -> list[str]:
    """Module-level constants whose literal parts spell a `docs/design/*.md` path.

    Matched on the string literals of the assignment rather than on a resolved path, because
    these are all built as `PROJECT_DIR / "docs" / "design" / "NAME.md"` and must be found
    WITHOUT importing the module (importing every candidate to find out whether it is a
    candidate is both slow and a side-effect risk in a test).
    """
    found = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        parts = [c.value for c in ast.walk(node.value)
                 if isinstance(c, ast.Constant) and isinstance(c.value, str)]
        if "docs" in parts and "design" in parts:
            found.extend(s for s in parts if s.endswith(".md"))
    return found


def discover(root: Path | None = None) -> set[tuple[str, str]]:
    """Find (module, rendered) pairs for every derived `docs/design/*.md` artefact.

    Independent of REGISTER by construction — it reads the source tree, never the register.
    """
    root = Path(root) if root is not None else PROJECT_DIR
    out: set[tuple[str, str]] = set()
    for tree_name in SCANNED_TREES:
        for path in sorted((root / tree_name).glob("*.py")):
            try:
                parsed = ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, SyntaxError):
                # FAIL-CLOSED (R15): an unreadable/unparseable module is not evidence of
                # absence. It is surfaced as an unregistered artefact under its own name so the
                # completeness test reds rather than quietly shrinking the discovered set.
                out.add((f"{tree_name}.{path.stem}", "<unparseable>"))
                continue
            if not _takes_write_flag(parsed):
                continue
            for rendered in _design_markdown_constants(parsed):
                out.add((f"{tree_name}.{path.stem}", f"docs/design/{rendered}"))
    return out


def unregistered(root: Path | None = None) -> set[tuple[str, str]]:
    """Derived artefacts the source tree has and the register does not."""
    return discover(root) - {(a.module, a.rendered) for a in REGISTER}


def orphaned(root: Path | None = None) -> set[tuple[str, str]]:
    """Register entries discovery cannot find — a stale line, or a renamed module."""
    return {(a.module, a.rendered) for a in REGISTER} - discover(root)


# ── staleness and repair ────────────────────────────────────────────────────────────────────

def _run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, timeout=300)


def stale_in(root: Path) -> list[DerivedArtefact]:
    """Every registered artefact whose `--check` disagrees with its rendering, inside `root`.

    Driven as a subprocess exactly as each artefact's own blocking test drives it, so this
    measures the same surface the gate measures rather than a re-implementation of it (R15:
    a check derived from a different source than the one it guards is a tautology risk).

    NAMING: a non-zero `--check` means "not fresh", which for some artefacts covers CONTENT
    VIOLATIONS as well as staleness -- `forward_attachment_register` exits non-zero on an
    `unknown_atom` declaration too. Both are red at the gate and both are worth repairing, so
    they are treated alike here; the artefact's own stderr distinguishes them, and the caller
    logs it. Do not read "stale" as "regenerating will fix it" -- a violation needs the SOURCE
    corrected, and `repair_from` will honestly report non-convergence when that is the case.
    """
    out = []
    for art in REGISTER:
        proc = _run([sys.executable, "-m", art.module, "--check"], cwd=root)
        if proc.returncode != 0:
            out.append(art)
    return out


def repair_from(source_root: Path, write_root: Path | None = None) -> dict:
    """Re-render every stale artefact in `source_root`, copying results into `write_root`.

    `source_root` must be a checkout of COMMITTED truth (the publish gate's HEAD checkout) —
    see the module docstring for why rendering from the working tree is wrong. `write_root`
    defaults to the real repo and receives the renderings for committing.

    Returns {"repaired": [relpath...], "converged": bool, "passes": int, "still_stale": [...]}.
    Never raises into the publish path: a repair that cannot run reports itself and the gate
    then reds on the true, unrepaired state, which is the honest outcome.
    """
    source_root = Path(source_root)
    write_root = Path(write_root) if write_root is not None else PROJECT_DIR
    repaired: list[str] = []
    passes = 0

    for passes in range(1, MAX_REPAIR_PASSES + 1):
        stale = stale_in(source_root)
        if not stale:
            break
        for art in stale:
            proc = _run([sys.executable, "-m", art.module, "--write"], cwd=source_root)
            if proc.returncode != 0:
                continue
            src = source_root / art.rendered
            if not src.exists():
                continue
            dst = write_root / art.rendered
            # `--write` already rendered into source_root, so when the two roots coincide the
            # copy is both unnecessary and an error (shutil raises SameFileError). Callers do
            # pass the same root -- a local `--repair-from .`, and the tests -- so this is a
            # supported case, not a misuse to guard against.
            if src.resolve() != dst.resolve():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
            if art.rendered not in repaired:
                repaired.append(art.rendered)
    else:
        # Loop exhausted without the `break` — still stale after MAX_REPAIR_PASSES.
        pass

    still_stale = [a.rendered for a in stale_in(source_root)]
    return {"repaired": repaired,
            "converged": not still_stale,
            "passes": passes,
            "still_stale": still_stale}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="rc 1 if the register is incomplete or any artefact is stale")
    ap.add_argument("--completeness", action="store_true",
                    help="rc 1 only if the register disagrees with discovery")
    ap.add_argument("--repair-from", metavar="DIR",
                    help="re-render stale artefacts from a checkout of committed truth")
    args = ap.parse_args(argv)

    if args.repair_from:
        res = repair_from(Path(args.repair_from))
        for rel in res["repaired"]:
            print("repaired {}".format(rel))
        if not res["converged"]:
            print("NOT CONVERGED after {} pass(es); still stale: {}".format(
                res["passes"], ", ".join(res["still_stale"])), file=sys.stderr)
            return 1
        return 0

    missing, extra = unregistered(), orphaned()
    for mod, rel in sorted(missing):
        print("UNREGISTERED derived artefact: {} renders {}".format(mod, rel), file=sys.stderr)
    for mod, rel in sorted(extra):
        print("ORPHANED register entry: {} -> {} not found in the source tree".format(
            mod, rel), file=sys.stderr)
    if args.completeness:
        return 1 if (missing or extra) else 0

    stale = stale_in(PROJECT_DIR)
    for art in stale:
        print("STALE: {} (rerun `python3 -m {} --write`)".format(art.rendered, art.module))
    print("{} registered artefact(s), {} stale, {} unregistered, {} orphaned.".format(
        len(REGISTER), len(stale), len(missing), len(extra)))
    if args.check:
        return 1 if (stale or missing or extra) else 0
    return 0


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ImportError:
        from _seat import refuse_if_foreign
    refuse_if_foreign("derived_artefact_register")
    sys.exit(main())
