"""The epistemic wall, defined ONCE — perimeter, seam, walker, classifier.

WHY THIS MODULE EXISTS
----------------------
Three instruments in this repo answer the question "is this an epistemic-wall
crossing?", and until 2026-08-09 they answered it from three different places:

  * `tests/architecture/test_epistemic_wall_ratchet.py` — the NET. Owned the
    walker and the classifier, and gates: a new crossing reds the suite.
  * `tools/knife_hotspot_measure.py` — the KNIFE ledger. Imported the walker
    FROM THE TEST MODULE (a tool importing a test), and reports.
  * `tools/epistemic_verifier.py` — the phase-close verifier. Had its own,
    independent notion of the seam and of the forbidden packages, expressed as
    a different kind of object (`APPROVED_SEAM` is a FILE; the ratchet's
    `SEAM_PACKAGE` is a PACKAGE).

That third divergence was not theoretical. KNIFE pass 2 added
`company/interfaces/supply_book.py`; the ratchet exempts it because it is under
the seam PACKAGE, while the verifier exempted it only because
`company/interfaces/` happens to sit in its unrelated `EXEMPT_PATHS` list. A
control passing for a reason other than the one it states is the shape R15
calls out, and it was recorded at the time as the second referent for this
extraction.

`KNIFE3_wall_crossing_paydown` names this extraction as its FIRST STEP, before
any cut, and the KNIFE ledger's own docstring explains why it was deferred to
here rather than done opportunistically: the walker is part of the NET that
protects the KNIFE passes, and moving the net while planning the cuts is the
error the MAP -> NET -> KNIFE sequence exists to prevent. The net is now
stable, both earlier passes have landed, so the move happens here.

PROVENANCE — THIS FILE WAS FOUND, NOT WRITTEN (2026-08-09)
-----------------------------------------------------------
It was ADOPTED, not authored. When pass 3 was drawn, this module already
existed in the working tree as an UNTRACKED file that no commit contained and
no module imported — an earlier attempt at this same extraction that died
before it was wired up or committed. The pass had already written its own
replacement when the new single-source control
(`tests/architecture/test_epistemic_wall_single_source.py::
test_no_second_walker_is_defined_anywhere`) failed on its FIRST run and named
this file as a second definition of `build_edges`/`company_reads_sim`/
`sim_reads_company`. The control caught its own author, which is the strongest
evidence available that it can fail.

The disposition follows the standing rule for work a guard flags as unmerged:
ADOPT, do not rebuild. This file is the survivor; the pass's own copy was
deleted. What the pass contributed on top is the two public predicates
(`is_sim_module`, `is_company_module`) that the verifier now shares with the
classifiers, the wiring of all three consumers, and the control that found it.
Recorded here rather than smoothed over, because "a landed pass had half its
code uncommitted" is a repeat class in this repo and the record is the only
place the next reader can see that the duplicate was resolved deliberately.

WHAT LIVES HERE, AND WHAT DELIBERATELY DOES NOT
------------------------------------------------
HERE: the PERIMETER (which packages are which side), the SEAM, the walker
(`build_edges`) and the two classifiers (`company_reads_sim`,
`sim_reads_company`). These are facts about what a crossing IS.

NOT HERE: the dated allowlists (`LEGACY_COMPANY_READS_SIM`,
`LEGACY_SIM_READS_COMPANY`). Those are the ratchet's BASELINE — a policy about
which crossings are grandfathered — and they stay in the ratchet test where
their shrink-only discipline is enforced. Moving them here would let a tool
edit the ratchet's floor, which is the opposite of the point.

Nothing in this module reads a baseline, a threshold or an allowlist. It
measures.

DEPENDENCIES: Python stdlib only (`ast`, `os`). The ratchet suite documents
that it runs even when the app's runtime dependencies are absent; importing
this module preserves that property, because this module imports nothing from
the project either.

PERIMETER RECON (carried over from the ratchet, where it was established)
-------------------------------------------------------------------------
Both sides of the wall turned out to be TWO packages, not one, and each was
established by an independent AST census rather than assumed from the directory
sharing the concept's name. A wall checker is only as honest as its perimeter.

COMPANY (business) side = {company, saas}:
  * `company/` — pricing, billing, CRM, risk, trading, compliance, ...
  * `saas/`    — the business layer proper (customers, CLV/CAC, churn,
                 cost-to-serve, reporting). Omitting `saas/` would have left
                 the single largest crossing class (simulation->saas) invisible.

SIM (simulated world) side = {sim, simulation}:
  * `sim/`        — market/price/weather/forward-curve/risk engine.
  * `simulation/` — population, households, settlement, customer-behaviour
                    engine. This is where the crossing mass lives.

SEAM: `company.interfaces`. An edge is EXEMPT iff its COMPANY-side endpoint
module lives under that package — in BOTH directions. The top-level
`interface/` package (singular) is a separate sim<->saas seam and is NEITHER
wall side, so it hosts no wall edge and cannot launder one; it is not walked.

SCOPE / KNOWN LIMIT (stated honestly)
-------------------------------------
STATIC imports only — `import X` and `from X import Y`, resolved with the
stdlib `ast` module over a pure read of the tree. Dynamic imports
(`__import__`, `importlib.import_module`), `getattr`-driven access and
string-eval escape it. That is a known, ACCEPTED limit of this (NET, static)
tier. Function-local imports are NOT a gap: `ast.walk` descends into function
bodies, so a lazy import is seen exactly as a module-level one — which is why
routing a dependency through a package the walker does not walk (`tools/`)
moves the measurement rather than the dependency, and why KNIFE pass 1 refused
that move.
"""

from __future__ import annotations

import ast
import os
import shutil
import subprocess
import tarfile
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass

# --------------------------------------------------------------------------
# Configuration — the two sides of the wall and the sanctioned seam.
# --------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Company/business side of the wall — TWO packages (see recon).
COMPANY_PACKAGES = frozenset({"company", "saas"})
# SIM side of the wall — the simulated world spans TWO packages (see recon).
SIM_PACKAGES = frozenset({"sim", "simulation"})
# The sanctioned company<->sim crossing surface. An edge whose COMPANY-side
# endpoint module is under this package is a legitimate seam crossing, not a
# wall violation. (The top-level `interface/` sim<->saas seam is deliberately
# NOT listed here — see the module docstring.)
SEAM_PACKAGE = "company.interfaces"
# The same seam as a repo-relative PATH prefix, for the instruments that work
# on paths rather than dotted names. Derived, never written twice: the verifier
# used to carry its own single-FILE spelling of the seam and drifted from the
# package spelling the moment a second seam module was added.
SEAM_PATH_PREFIX = SEAM_PACKAGE.replace(".", "/") + "/"

# Top-level directories walked (all under REPO_ROOT). These are exactly the
# four wall-side packages; `interface/` is intentionally excluded because it is
# neither wall side and cannot host a wall edge.
WALL_DIRS = ("company", "saas", "sim", "simulation")

WALL_DOCTRINE = (
    "Epistemic wall (CLAUDE.md, Architectural Laws): the company/business layer "
    "must only cross the SIM boundary through the sanctioned seam "
    f"`{SEAM_PACKAGE}` ({SEAM_PACKAGE.replace('.', '/')}/). A direct import "
    "between company-side internals (company/, saas/) and SIM internals (sim/, "
    "simulation/) bypasses that seam. If this crossing is intentional and "
    "unavoidable, route it through the seam; if it is genuinely legacy, add it "
    "to the dated allowlist in this file with a one-line justification — never "
    "silently. company-side reading SIM (class a) is the strictly forbidden "
    "direction and the highest-priority shrink target."
)


# --------------------------------------------------------------------------
# Static import extraction (stdlib `ast` only).
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class RawEdge:
    """One import edge: source module imports target module, at file:line."""

    src: str          # dotted module doing the importing
    dst: str          # dotted module being imported
    path: str         # file (repo-relative) where the import statement sits
    lineno: int


def _module_name(root: str, path: str) -> str:
    """Dotted module name for a .py file relative to `root` (drops __init__)."""
    rel = os.path.relpath(path, root)
    parts = rel[: -len(".py")].split(os.sep)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _resolve_relative(src: str, module: str | None, level: int) -> str:
    """Resolve a relative import (`from . import x`) to an absolute dotted name.

    Sibling top-level packages (company / saas / sim / simulation) cannot reach
    each other via a relative import, so relative imports never produce a wall
    crossing — but we resolve them correctly anyway for completeness.
    """
    pkg = src.split(".")
    base = pkg[: len(pkg) - level] if level <= len(pkg) else []
    tail = module.split(".") if module else []
    return ".".join(base + tail)


def build_edges(root: str, dirs: tuple[str, ...]) -> list[RawEdge]:
    """Walk `dirs` under `root` and return every static import edge.

    Pure static read: parses each file with `ast`, extracts `Import` and
    `ImportFrom` nodes. A file that fails to parse is skipped (it cannot import
    anything at runtime either). Parameterised by root so the R15 mutation
    fixtures can point it at a synthetic tmp tree.
    """
    edges: list[RawEdge] = []
    for top in dirs:
        for dirpath, _dirnames, filenames in os.walk(os.path.join(root, top)):
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                src = _module_name(root, path)
                try:
                    with open(path, encoding="utf-8") as fh:
                        tree = ast.parse(fh.read(), filename=path)
                except (SyntaxError, UnicodeDecodeError):
                    continue
                relpath = os.path.relpath(path, root)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            edges.append(RawEdge(src, alias.name, relpath, node.lineno))
                    elif isinstance(node, ast.ImportFrom):
                        if node.level:
                            dst = _resolve_relative(src, node.module, node.level)
                        else:
                            dst = node.module or ""
                        edges.append(RawEdge(src, dst, relpath, node.lineno))
    return edges


# --------------------------------------------------------------------------
# Classification — which edges cross the wall.
# --------------------------------------------------------------------------

def top_package(module: str) -> str:
    """The top-level package of a dotted module name (`""` for the empty name)."""
    return module.split(".", 1)[0] if module else ""


def under_seam(module: str) -> bool:
    """True iff `module` is the seam package or lives inside it."""
    return module == SEAM_PACKAGE or module.startswith(SEAM_PACKAGE + ".")


def is_sim_module(module: str) -> bool:
    """True iff `module` names SIM-side code.

    This is the predicate `tools/epistemic_verifier.py` asks of every import it
    finds in company-side code. It is the same predicate the classifiers below
    apply to an edge endpoint — deliberately one function, because the
    verifier's private copy of this question is where the drift started.
    """
    return top_package(module) in SIM_PACKAGES


def is_company_module(module: str) -> bool:
    """True iff `module` names company-side code."""
    return top_package(module) in COMPANY_PACKAGES


# Back-compat private aliases (the ratchet's own tests referred to these names
# while the definition lived there).
_top = top_package
_under_seam = under_seam


def company_reads_sim(edges: list[RawEdge]) -> dict[tuple[str, str], RawEdge]:
    """Class (a): company-side internals importing SIM internals, NOT via seam.

    Keyed by (src_module, dst_module) so many import statements collapsing to
    the same module pair count as one edge; value is a representative location.
    This is the STRICTLY FORBIDDEN direction — the business layer must never
    read the simulated world's internals.
    """
    out: dict[tuple[str, str], RawEdge] = {}
    for e in edges:
        if is_company_module(e.src) and is_sim_module(e.dst) and not under_seam(e.src):
            out.setdefault((e.src, e.dst), e)
    return out


def sim_reads_company(edges: list[RawEdge]) -> dict[tuple[str, str], RawEdge]:
    """Class (b): SIM internals importing company-side internals, NOT via seam.

    Symmetric to class (a): an edge whose company-side endpoint (here the
    TARGET) is under the seam package is a sanctioned crossing and exempt.
    """
    out: dict[tuple[str, str], RawEdge] = {}
    for e in edges:
        if is_sim_module(e.src) and is_company_module(e.dst) and not under_seam(e.dst):
            out.setdefault((e.src, e.dst), e)
    return out


def crossings_at(root: str) -> dict[tuple[str, str], RawEdge]:
    """Every wall crossing in the tree at `root`, both directions, keyed by edge.

    Parameterised by root for one reason: the tree under your feet is not the
    tree you ship. `live_crossings()` and `crossings_at_head()` are the two
    call sites, and they differ ONLY in this argument, so neither can drift
    into a second definition of "a crossing" (the defect this module exists
    to prevent, now applied to *which tree* as well as *what counts*).
    """
    raw = build_edges(root, WALL_DIRS)
    merged: dict[tuple[str, str], RawEdge] = {}
    merged.update(company_reads_sim(raw))
    merged.update(sim_reads_company(raw))
    return merged


def live_crossings() -> dict[tuple[str, str], RawEdge]:
    """Every live wall crossing in THIS WORKING TREE, both directions.

    The one call every consumer wants. Provided here so that "the crossings"
    is a single expression rather than a four-line recipe each instrument
    spells out for itself — the recipe is where the three definitions drifted.

    NOTE WHICH TREE. This reads the working tree, uncommitted edits included.
    That is the right default for a gate that must red BEFORE you commit a new
    crossing, and the wrong one for any claim about what LANDED — see
    `crossings_at_head()`.
    """
    return crossings_at(REPO_ROOT)


# --------------------------------------------------------------------------
# The same measurement, against HEAD instead of the working tree.
# --------------------------------------------------------------------------
#
# WHY THIS EXISTS (2026-08-10, third instance of one class in two days)
# ---------------------------------------------------------------------
# Every instrument above reads the working tree, and a green working tree
# proves nothing about what a reader of the repo will find. The class has now
# been paid for three times:
#
#   * KNIFE pass 1 was recorded LANDED in a COMMITTED document while four of
#     its files sat unstaged, so class (a) was still populated at HEAD while
#     the record said zero
#     (`WORKER_FINDING_A_LANDED_PASS_HAD_HALF_ITS_CODE_UNCOMMITTED_2026-08-09`).
#   * The capability index measured the working tree and reported it as the
#     repo's state (`WORKER_FINDING_THE_INDEX_READS_THE_WORKING_TREE`).
#   * KNIFE pass 3's B7 cut committed NOTHING while its own register asserted
#     "THIS register is the committed record" — the artefact claiming the
#     commit was, at the time of writing, proof that no commit had happened
#     (see WALL_CROSSING_DISPOSITION_REGISTER.md §3a CORRECTION).
#
# The first finding named the remedy exactly, and this is it: point the SAME
# walker at a `git archive HEAD` export. Not a second checker with its own
# notion of a crossing — one different argument to `crossings_at`. R16's shape
# applied to trees: verify the tree at HEAD, never the tree under your feet.


class HeadExportError(RuntimeError):
    """HEAD could not be exported or the export could not be trusted.

    Deliberately an ERROR, never an empty result. An export that silently came
    back short would make every `cut` claim verify against a tree that does not
    contain the code — the fail-open shape, and the exact failure this whole
    mechanism was built to catch. "Could not look" and "found nothing" are the
    same number and opposite facts.
    """


def _head_python_files(repo_root: str, dirs: tuple[str, ...]) -> set[str]:
    """The .py paths HEAD contains under `dirs`, per git's own record of it.

    This is the INDEPENDENT ORACLE for the export's completeness. It comes from
    git's object store (`ls-tree` of the commit), not from the exported
    filesystem, so a truncated or partially-extracted archive disagrees with it
    rather than being confirmed by it. A checker that validated the export
    against the export would be the tautology R15 names first.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", repo_root, "ls-tree", "-r", "--name-only", "HEAD", "--", *dirs],
            capture_output=True, text=True, check=False,
        )
    except OSError as exc:                       # git absent = a FAILED check
        raise HeadExportError(f"could not run git ls-tree: {exc}") from exc
    if proc.returncode != 0:
        raise HeadExportError(
            f"git ls-tree HEAD failed (rc {proc.returncode}): {proc.stderr.strip()}"
        )
    return {
        line for line in proc.stdout.splitlines()
        if line.endswith(".py")
    }


@contextmanager
def head_export(repo_root: str = REPO_ROOT, dirs: tuple[str, ...] = WALL_DIRS):
    """Extract the wall-side packages AT HEAD into a temp dir; yield its path.

    Uses `git archive`, which reads the commit object — never the index and
    never the working tree, so a staged-but-uncommitted edit is invisible here
    exactly as it is to someone who clones the repo.

    THREE WAYS THIS REFUSES TO FAIL OPEN, each of which would otherwise hand a
    caller an empty tree that verifies every claim ever made:
      1. git missing, or `git archive` rc != 0  -> HeadExportError.
      2. HEAD carries no .py files under `dirs` -> HeadExportError. A repo that
         genuinely had none would make the whole measurement meaningless, so
         "zero" is refused rather than reported.
      3. the extracted file set != git's own    -> HeadExportError, naming the
         difference both ways. This is the guard that catches a truncated
         archive, and it compares against the oracle above, not against itself.
    """
    expected = _head_python_files(repo_root, dirs)
    if not expected:
        raise HeadExportError(
            f"HEAD contains no .py files under {list(dirs)} — refusing to "
            "measure an empty tree, because an empty tree confirms every claim"
        )
    # `git archive` errors on a pathspec matching nothing, so archive only the
    # wall dirs HEAD actually has. Derived from `expected` (git's own listing)
    # rather than from the filesystem, which is the tree we are trying not to
    # trust.
    present = tuple(d for d in dirs if any(p.startswith(d + "/") for p in expected))

    tmp = tempfile.mkdtemp(prefix="wall-head-")
    try:
        archive = os.path.join(tmp, "head.tar")
        dest = os.path.join(tmp, "tree")
        os.makedirs(dest)
        with open(archive, "wb") as fh:
            try:
                proc = subprocess.run(
                    ["git", "-C", repo_root, "archive", "--format=tar", "HEAD", "--", *present],
                    stdout=fh, stderr=subprocess.PIPE, check=False,
                )
            except OSError as exc:
                raise HeadExportError(f"could not run git archive: {exc}") from exc
        if proc.returncode != 0:
            raise HeadExportError(
                f"git archive HEAD failed (rc {proc.returncode}): "
                f"{proc.stderr.decode('utf-8', 'replace').strip()}"
            )

        with tarfile.open(archive) as tar:
            _safe_extract(tar, dest)

        got = {
            os.path.relpath(os.path.join(dirpath, name), dest).replace(os.sep, "/")
            for dirpath, _, names in os.walk(dest)
            for name in names
            if name.endswith(".py")
        }
        if got != expected:
            missing = sorted(expected - got)[:5]
            extra = sorted(got - expected)[:5]
            raise HeadExportError(
                f"the HEAD export is not what HEAD contains: git lists "
                f"{len(expected)} .py file(s), the export has {len(got)}. "
                f"missing={missing} unexpected={extra}"
            )
        yield dest
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _safe_extract(tar: tarfile.TarFile, dest: str) -> None:
    """Extract, refusing any member that would escape `dest`.

    `git archive` of our own HEAD is not hostile input, but a tar extractor
    without a traversal check is the kind of thing that gets copied to a place
    where the input IS hostile. The check costs one comparison per member.
    """
    dest_abs = os.path.abspath(dest)
    for member in tar.getmembers():
        target = os.path.abspath(os.path.join(dest, member.name))
        if target != dest_abs and not target.startswith(dest_abs + os.sep):
            raise HeadExportError(f"archive member escapes the export dir: {member.name}")
        if member.issym() or member.islnk():
            raise HeadExportError(f"archive member is a link, refused: {member.name}")
    tar.extractall(dest)                                    # noqa: S202 — checked above


def crossings_at_head(repo_root: str = REPO_ROOT) -> dict[tuple[str, str], RawEdge]:
    """Every wall crossing IN THE COMMITTED TREE — what a fresh clone sees.

    The counterpart to `live_crossings()`. Same walker, same classifiers, same
    perimeter; the only difference is which tree. Where the two disagree, the
    working tree carries uncommitted wall work — which is a normal mid-pass
    state and a defect only when something CLAIMS the work has landed.
    """
    with head_export(repo_root) as root:
        return crossings_at(root)
