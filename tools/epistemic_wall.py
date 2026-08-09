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


def live_crossings() -> dict[tuple[str, str], RawEdge]:
    """Every live wall crossing in THIS repo, both directions, keyed by edge.

    The one call every consumer wants. Provided here so that "the crossings"
    is a single expression rather than a four-line recipe each instrument
    spells out for itself — the recipe is where the three definitions drifted.
    """
    raw = build_edges(REPO_ROOT, WALL_DIRS)
    merged: dict[tuple[str, str], RawEdge] = {}
    merged.update(company_reads_sim(raw))
    merged.update(sim_reads_company(raw))
    return merged
