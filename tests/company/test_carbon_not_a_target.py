"""CARBON_NOT_A_TARGET guard (CARBON_NOT_A_TARGET_CONSTRAINT.md, MAKE_IT_STICK).

£/tCO2e and every carbon metric is a DIAGNOSTIC — it may NOT feed any decision
surface (the atom draw, the risk committee, a pricing/personalisation reward
path, a digest score, or a selection/fitness function). This file mechanises
that. It is the load-bearing control the constraint exists to provide, and the
E5 FRAME calls it the strongest of the four un-goal-seekability properties
because it is a REACHABILITY property: "a metric a decision surface cannot
import is a metric it cannot optimise."

TWO DEFECTS THIS FILE WAS BUILT AROUND, both measured on disk before anything
changed here, and both instances of the same class the E5 basis-gate pass
(2026-08-22) had just cut out of the R14 publish gate: A SUBJECT SET THAT IS A
HAND-MAINTAINED ALLOWLIST CHECKS ONLY WHAT SOMEBODY REMEMBERED TO NAME.

1. THE SUBJECT SET WAS AN ALLOWLIST (the class). The guard named nine globs and
   scanned the 50 files they matched. Of the 20 modules in the decision tree
   whose own filename says they decide, score, rank, recommend or draw, THREE
   were subjects. The seventeen outside it included the two most carbon-adjacent
   decision modules on disk — `company/crm/decarb_recommender.py` (a
   personalisation recommender: the exact "pricing/personalisation decision
   loop" the constraint names) and `company/sustainability/decarbonisation_score.py`
   (a score about decarbonisation) — plus `company/trading/hedge_decision.py`,
   `company/policy/decision_policy.py`, `background/axis_prescore.py` and
   `background/fidelity_grid_scorer.py`. A surface is a subject because it is on
   the list, not because it is a surface, so every decision surface written
   tomorrow is born unchecked.
2. THE CHECK CLAIMED REACHABILITY AND MEASURED ADJACENCY. The old guard asked
   only whether a named file imports carbon ITSELF. `saas/tariff_pricing.py` is
   imported by `company/pricing/renewal_desk.py` and `company/pricing/tou_desk.py`
   — both named subjects. Had `saas/tariff_pricing.py` imported the carbon
   ledger, a carbon figure would have been one plain attribute access away from
   two pricing decision surfaces and every test here would have stayed GREEN,
   because `saas/` was not on the list and neither desk imports carbon directly.
   That is the mutation `test_the_guard_is_reachability_not_adjacency` pins.

THE FIX IS DENY-BY-DEFAULT, the same shape as the derived basis-gate subject
set. The subject set is now DERIVED — every module in the machine's decision
tree — and the question is inverted: not "did a listed surface import carbon"
but "does ANY module reach carbon, by any chain of imports". Every module that
does must be DECLARED here by name with a written reason. The register is EMPTY
today, and that is a measured fact rather than an aspiration: no module under
`company/ sim/ simulation/ saas/ background/` imports `company.carbon` directly
or transitively (794 files scanned). An empty register is the strongest form of
this control, because it makes reachability and adjacency the same thing — and
a declaration is expensive to add on purpose, since declaring a reader forces
its whole importer closure to be declared too (`test_a_declaration_pulls_in_its_importer_closure`).

R15 — the control can FAIL, in each direction, and the mutations are named on
each test. The detector self-tests (fires on a synthetic import, quiet on clean
code) are kept from the original guard. The named-surface list is kept as well,
now with the resolve-check the E5 FRAME's control C8 asked for: an unresolvable
surface name is a FAILED check and never a silent skip. It found one on its
first run — `company/crm/renewal_pricing_engine.py` was named for over a month
and has never existed at that path; the real module is
`company/pricing/renewal_pricing_engine.py`, scanned only by the incidental
reach of a `company/pricing/*.py` glob. The old `len(files) >= 5` count could
not have caught it: the globs alone supplied 50.

HONEST LIMITS, THREE.
(a) The subject set is the machine's DECISION tree. `tools/` and `site/` are
    declared out of subject in `_OUT_OF_SUBJECT_ROOTS` with reasons, because
    they are the reporting/publishing lane where reading a carbon figure is the
    point. A decision surface implemented in `tools/` would escape this guard.
(b) The graph is STATIC and syntactic. An `importlib.import_module` on a name
    built at runtime, or a plugin loaded by string, is not an edge here.
(c) This proves carbon cannot REACH a decision surface. It cannot prove a human
    will not re-key a carbon number into a decision by hand — which is why the
    factor set is director-reserved (E5 FRAME §2.5's honest residual).
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Mapping, Set, Tuple

import pytest

_ROOT = Path(__file__).resolve().parent.parent.parent

_CARBON_PACKAGE = "company.carbon"


def _imports_company_carbon(source: str) -> bool:
    """True iff `source` imports anything from the `company.carbon` package
    (or the bare `carbon_ledger` module). AST-based, so a comment or a string
    mentioning carbon never false-positives."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")
            if root[:2] == ["company", "carbon"] or root[-1] == "carbon_ledger":
                return True
        elif isinstance(node, ast.Import):
            for n in node.names:
                parts = n.name.split(".")
                if parts[:2] == ["company", "carbon"] or parts[-1] == "carbon_ledger":
                    return True
    return False


# -- R15 self-test of the detector (both directions) ------------------------

def test_detector_fires_on_a_carbon_import():
    assert _imports_company_carbon(
        "from company.carbon.carbon_ledger import CarbonLedger\nx = CarbonLedger()"
    )
    assert _imports_company_carbon("import company.carbon.carbon_ledger")


def test_detector_quiet_on_clean_code():
    assert not _imports_company_carbon(
        "# carbon is the mission but this module must not read it\n"
        "from company.pricing.cost_to_serve import cost\nx = cost()"
    )


# ===========================================================================
# PART 1 — the named decision surfaces (kept, and now required to RESOLVE)
# ===========================================================================

# The decision surfaces the constraint doc names explicitly. These are NOT the
# subject set any more (Part 2 derives that); they are the surfaces whose loss
# must be LOUD. Every entry is required to resolve — see
# `test_every_named_surface_resolves`.
_SURFACE_GLOBS = (
    "background/supervisor.py",
    "sim/risk_committee.py",
    "sim/risk_committee_agent.py",
    "sim/risk_committee_rules.py",
    "company/risk/*.py",
    "company/pricing/*.py",
    # CORRECTED 2026-08-22: this was `company/crm/renewal_pricing_engine.py`,
    # a path that has never existed in any commit. The module is real and lives
    # under company/pricing, where the glob above was reaching it by accident.
    "company/pricing/renewal_pricing_engine.py",
    "company/crm/portfolio_repricing.py",
    "company/regulatory/supplier_fitness_register.py",
    # ADDED 2026-08-22: the two most carbon-adjacent decision modules on disk,
    # neither of which was a subject of this guard until today.
    "company/crm/decarb_recommender.py",
    "company/sustainability/decarbonisation_score.py",
)


def _resolve_named_surface(glob: str) -> Tuple[Path, ...]:
    """Files matched by one named-surface entry. Empty means UNRESOLVABLE, which
    is a failure at `test_every_named_surface_resolves`, never a silent skip."""
    if "*" in glob:
        return tuple(sorted(_ROOT.glob(glob)))
    p = _ROOT / glob
    return (p,) if p.is_file() else ()


def _surface_files() -> Tuple[Path, ...]:
    seen: Dict[Path, None] = {}
    for g in _SURFACE_GLOBS:
        for p in _resolve_named_surface(g):
            seen.setdefault(p, None)
    return tuple(seen)


def test_every_named_surface_resolves():
    """E5 FRAME control C8 — an unresolvable surface is a FAILED check, not a skip.

    THE DEFECT: the previous `_surface_files()` dropped a non-existent path
    silently, and the only guard on that was a COUNT (`len(files) >= 5`) against
    a population the globs alone filled to 50. A named surface could therefore be
    renamed, moved or misspelt and stop being checked with nothing going red.
    Live instance on first run: `company/crm/renewal_pricing_engine.py`, named
    since 2026-07-20, never existed at that path in any commit.

    MUTATION: put that path back → this test goes RED (the count test does not).
    """
    unresolved = [g for g in _SURFACE_GLOBS if not _resolve_named_surface(g)]
    assert not unresolved, (
        "named decision surface(s) do not resolve to any file on disk: "
        f"{unresolved}. A surface that cannot be found is a surface that is not "
        "being checked -- name the real path or remove the entry, never leave it "
        "to fail silently"
    )


def test_decision_surfaces_exist():
    # Guard against a silently-empty scan (fail-silent): the core surfaces must
    # resolve to real files, else the guard would vacuously "pass". Kept from the
    # original guard; `test_every_named_surface_resolves` is the per-name version
    # this count could never be.
    files = _surface_files()
    assert len(files) >= 5, f"decision-surface scan resolved too few files: {files}"


@pytest.mark.parametrize("path", _surface_files(), ids=lambda p: str(p.relative_to(_ROOT)))
def test_decision_surface_does_not_import_carbon(path):
    src = path.read_text(encoding="utf-8")
    assert not _imports_company_carbon(src), (
        f"{path.relative_to(_ROOT)} imports a carbon metric -- CARBON_NOT_A_TARGET: a carbon "
        "figure may never feed a decision surface (draw / risk committee / pricing / fitness)"
    )


# ===========================================================================
# PART 2 — deny-by-default: NOTHING in the decision tree may REACH carbon
# ===========================================================================

# The subject set, DERIVED. Every module under these roots is a subject because
# it is in the machine's decision tree, not because anyone named it.
_DECISION_TREE_ROOTS: Mapping[str, str] = {
    "company": "the company's own brain -- pricing, risk, CRM, trading, policy, compliance",
    "sim": "the world model, incl. the risk committee the constraint names by name",
    "simulation": "the run harness that drives selection and the population draw",
    "saas": "the business layer -- billing, CLV/CAC, churn, tariff pricing",
    "background": "the machine's own operations -- the atom draw, digests, scorers",
}

# Declared OUT of subject, with reasons, so the boundary is visible rather than
# accidental. This is honest limit (a) in the module docstring.
_OUT_OF_SUBJECT_ROOTS: Mapping[str, str] = {
    "tools": (
        "the reporting/publishing lane. Publishing a carbon figure is the POINT "
        "of the mission metric, so a carbon import here is expected, not a breach "
        "-- but a decision surface implemented in tools/ would escape this guard"
    ),
    "site": (
        "rendered output and its tests -- downstream of publishing, decides nothing"
    ),
    "tests": (
        "the test tree reads carbon deliberately in order to check it; a guard "
        "that forbade that would forbid its own subject"
    ),
}

# Modules permitted to reach `company.carbon`, each with a WRITTEN REASON.
# MEASURED EMPTY on 2026-08-22 over 794 files: nothing in the decision tree
# reaches the carbon ledger, directly or transitively. Empty is the strongest
# state of this register -- it is what makes reachability equal adjacency here.
_CARBON_READER_DECLARATIONS: Mapping[str, str] = {}

# FAIL-OPEN floor. A scan that silently narrows to a handful of files would pass
# every test below while checking almost nothing. 794 files were in subject when
# this floor was set; it is a floor on COVERAGE, never a target (R12).
_POPULATION_FLOOR = 600


def _read(path: Path) -> str:
    """Single read point, so a mutation can substitute a file's source in memory
    without writing to a tree that concurrent lanes share."""
    return path.read_text(encoding="utf-8")


def _module_name(path: Path) -> str:
    parts = list(path.relative_to(_ROOT).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _production_files() -> Tuple[Path, ...]:
    """Every module in the decision tree, EXCEPT the carbon package itself (which
    is allowed to import itself and is the thing being protected, not a reader)."""
    files = []
    for root in _DECISION_TREE_ROOTS:
        d = _ROOT / root
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            if _module_name(p).startswith(_CARBON_PACKAGE):
                continue
            files.append(p)
    return tuple(files)


def _import_targets(tree: ast.AST, module: str) -> Set[str]:
    """Every module name this source imports, including the `from pkg import mod`
    form (recorded as `pkg.mod`, since that is an edge to `pkg.mod` and not only
    to `pkg`). Relative imports are resolved against the importing package."""
    pkg = module.rsplit(".", 1)[0] if "." in module else ""
    targets: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level:
                base = pkg.split(".")
                base = base[: len(base) - (node.level - 1)] if node.level > 1 else base
                prefix = ".".join([b for b in base if b])
                mod = f"{prefix}.{node.module}" if node.module else prefix
            else:
                mod = node.module or ""
            if not mod:
                continue
            targets.add(mod)
            for a in node.names:
                targets.add(f"{mod}.{a.name}")
        elif isinstance(node, ast.Import):
            for a in node.names:
                targets.add(a.name)
    return targets


def _import_edges() -> Tuple[Dict[str, Set[str]], Tuple[str, ...]]:
    """(module -> imported names, parse failures). A file that will not parse is
    returned as a FAILURE, never dropped: an unavailable check is a FAILED check
    (R15 fail-silent doctrine), and a scanner that skips what it cannot read is
    exactly how a subject leaves a subject set without anyone noticing."""
    edges: Dict[str, Set[str]] = {}
    failures = []
    for p in _production_files():
        module = _module_name(p)
        try:
            tree = ast.parse(_read(p))
        except SyntaxError as exc:
            failures.append(f"{p.relative_to(_ROOT)}: {exc}")
            continue
        edges[module] = _import_targets(tree, module)
    return edges, tuple(failures)


def _modules_reaching(edges: Mapping[str, Set[str]], target_prefix: str) -> Set[str]:
    """Every module that reaches `target_prefix` by ANY chain of imports.

    Walks the graph BACKWARDS from the target, so the answer is a closure and not
    a one-hop neighbourhood -- this is the difference between the reachability
    property the FRAME claims and the adjacency property the old guard measured."""
    reverse: Dict[str, Set[str]] = {}
    for src, outs in edges.items():
        for out in outs:
            reverse.setdefault(out, set()).add(src)

    def _hits(name: str) -> bool:
        return name == target_prefix or name.startswith(target_prefix + ".")

    seen: Set[str] = set()
    frontier = {n for n in reverse if _hits(n)}
    while frontier:
        nxt: Set[str] = set()
        for name in frontier:
            for src in reverse.get(name, ()):  # noqa: B905 - plain lookup
                if src not in seen and not _hits(src):
                    seen.add(src)
                    nxt.add(src)
        frontier = nxt
    return seen


def test_the_scanned_population_is_the_whole_decision_tree():
    """FAIL-OPEN guard on the scan itself. Every declared root must contribute
    files and the total must clear the floor -- a scan that quietly narrowed to
    nothing would let every test below pass while checking nothing.

    MUTATION: drop a root from `_DECISION_TREE_ROOTS`, or point `_production_files`
    at an empty directory → RED.
    """
    files = _production_files()
    by_root = {r: sum(1 for f in files if f.relative_to(_ROOT).parts[0] == r)
               for r in _DECISION_TREE_ROOTS}
    empty = [r for r, n in by_root.items() if n == 0]
    assert not empty, f"declared decision-tree root(s) contributed no files: {empty} ({by_root})"
    assert len(files) >= _POPULATION_FLOOR, (
        f"the carbon guard scanned only {len(files)} files (floor {_POPULATION_FLOOR}) -- "
        f"a narrowed scan passes every check below while checking almost nothing: {by_root}"
    )


def test_every_scanned_file_parses():
    """An unparseable subject is a FAILED check, not a skip (R15 FAIL-SILENT).

    MUTATION: make `_import_edges` swallow SyntaxError and `continue` without
    recording it, then feed the scan an unparseable source → this goes RED.
    """
    _, failures = _import_edges()
    assert not failures, (
        "file(s) in the carbon guard's subject set could not be parsed, so they were "
        f"NOT checked: {failures}"
    )


def test_no_module_in_the_decision_tree_reaches_carbon_undeclared():
    """THE CONTROL. Deny-by-default over the derived subject set, by REACHABILITY.

    THE DEFECT IT REPLACES: the subject set was a nine-entry allowlist matching 50
    files. Three of the 20 decision-named modules in the tree were subjects;
    `company/crm/decarb_recommender.py` and `company/sustainability/decarbonisation_score.py`
    -- the two closest to carbon on the whole disk -- were not. A surface was
    checked because it had been named, which is the same fail-silent shape the
    R14 basis gate carried until 2026-08-22.

    MUTATIONS: (1) restore the old named-only subject set → a carbon import in
    `decarb_recommender.py` passes, so the test proving it is caught goes RED;
    (2) add an undeclared carbon import anywhere in the tree → RED here.
    """
    edges, failures = _import_edges()
    assert not failures, f"unparseable subject(s) -- the scan is incomplete: {failures}"
    reaching = _modules_reaching(edges, _CARBON_PACKAGE)
    declared = {_module_name(_ROOT / p) for p in _CARBON_READER_DECLARATIONS}
    undeclared = sorted(reaching - declared)
    assert not undeclared, (
        f"{len(undeclared)} module(s) in the decision tree can reach {_CARBON_PACKAGE} "
        f"with no declaration: {undeclared[:20]}. CARBON_NOT_A_TARGET: a carbon figure may "
        "never be reachable from the draw, the risk committee, a pricing/personalisation "
        "path, a digest score or a fitness function -- not directly and not through an "
        "intermediary. Declare it here with a written reason, or cut the import"
    )


def test_the_guard_is_reachability_not_adjacency():
    """The property the FRAME claims, stated as a live falsifier.

    The old guard asked "does this named file import carbon". `saas/tariff_pricing.py`
    is imported by `company/pricing/renewal_desk.py` and `company/pricing/tou_desk.py`,
    both named subjects; a carbon import in `saas/tariff_pricing.py` would have put a
    carbon figure one attribute access from two pricing decision surfaces with every
    test green. This asserts the graph walk actually follows that chain.

    MUTATION: replace `_modules_reaching` with a one-hop neighbourhood → RED.
    """
    edges, _ = _import_edges()
    probe = "saas.tariff_pricing"
    assert probe in edges, f"{probe} is no longer in the subject set -- pick a new probe"
    mutated = {k: set(v) for k, v in edges.items()}
    mutated[probe].add("company.carbon.carbon_ledger")
    reaching = _modules_reaching(mutated, _CARBON_PACKAGE)
    assert probe in reaching, "the direct importer was not detected"
    downstream = {"company.pricing.renewal_desk", "company.pricing.tou_desk"} & reaching
    assert downstream == {"company.pricing.renewal_desk", "company.pricing.tou_desk"}, (
        "a module importing carbon did not make its own importers reachable -- this guard "
        f"is measuring adjacency, not reachability. Reached: {sorted(reaching)[:10]}"
    )


def test_relative_imports_are_resolved_not_dropped():
    """A dropped edge is a hole in the reachability walk. The decision tree uses
    no relative imports today, so the resolver is proven on synthetic source
    rather than left as untested code that quietly does nothing.

    MUTATION: make `_import_targets` ignore `node.level` → RED.
    """
    tree = ast.parse("from .carbon_ledger import CarbonLedger")
    assert "company.carbon.carbon_ledger" in _import_targets(tree, "company.carbon.reporter")
    tree2 = ast.parse("from ..carbon.carbon_ledger import CarbonLedger")
    assert "company.carbon.carbon_ledger" in _import_targets(tree2, "company.pricing.desk")


# -- the declaration register: an admission, and a non-growable one ----------

def test_every_declaration_names_a_file_that_exists():
    """MUTATION: declare a path that is not on disk → RED. A declaration for a
    file nobody can find is an excuse with no subject."""
    missing = [p for p in _CARBON_READER_DECLARATIONS if not (_ROOT / p).is_file()]
    assert not missing, f"carbon-reader declaration(s) name a file that does not exist: {missing}"


def test_every_declaration_is_still_needed():
    """The REPAIRED direction. A module that has since stopped reading carbon must
    lose its declaration, or the register becomes a place to hide a future import.

    MUTATION: declare a file that does not import carbon (any module in the tree
    today, since the register is measured empty) → RED.
    """
    edges, _ = _import_edges()
    reaching = _modules_reaching(edges, _CARBON_PACKAGE)
    stale = [p for p in _CARBON_READER_DECLARATIONS
             if (_ROOT / p).is_file() and _module_name(_ROOT / p) not in reaching]
    assert not stale, (
        f"carbon-reader declaration(s) for module(s) that no longer reach carbon: {stale}. "
        "Remove the declaration -- a standing exemption for a repaired subject is how the "
        "register stops being an admission and starts being a loophole"
    )


def test_every_declaration_carries_a_written_reason():
    """MUTATION: blank a reason → RED. A declaration without a reason is an
    allowlist entry, which is the thing this file exists to abolish."""
    blank = [p for p, why in _CARBON_READER_DECLARATIONS.items() if not (why or "").strip()]
    assert not blank, f"carbon-reader declaration(s) with no written reason: {blank}"


def test_a_declaration_pulls_in_its_importer_closure():
    """What makes a declaration EXPENSIVE, and therefore rare. Declaring a reader
    does not stop at that module: everything that imports it now reaches carbon
    too, and must be declared as well. This is asserted against the live graph
    with a synthetic declaration, so it holds while the register is empty.

    MUTATION: make the reachability set stop at declared modules (i.e. prune the
    walk at a declaration instead of subtracting declarations at the end) → RED.
    """
    edges, _ = _import_edges()
    probe = "company.interfaces.supply_book"
    assert probe in edges, f"{probe} is no longer in the subject set -- pick a new probe"
    mutated = {k: set(v) for k, v in edges.items()}
    mutated[probe].add("company.carbon.carbon_ledger")
    reaching = _modules_reaching(mutated, _CARBON_PACKAGE)
    declared = {probe}
    still_undeclared = reaching - declared
    assert len(still_undeclared) >= 5, (
        "declaring one reader silently absolved its importers -- a declaration must cost its "
        f"whole closure. Undeclared after declaring {probe}: {sorted(still_undeclared)}"
    )


def test_the_out_of_subject_roots_are_declared_with_reasons():
    """Honest limit (a), pinned. The boundary of this guard is written down and
    reasoned, so nobody reads a green suite as covering `tools/`.

    MUTATION: add a root to `_OUT_OF_SUBJECT_ROOTS` with a blank reason, or list
    a root that is also in `_DECISION_TREE_ROOTS` → RED.
    """
    overlap = set(_OUT_OF_SUBJECT_ROOTS) & set(_DECISION_TREE_ROOTS)
    assert not overlap, f"root(s) declared both in and out of subject: {sorted(overlap)}"
    blank = [r for r, why in _OUT_OF_SUBJECT_ROOTS.items() if not (why or "").strip()]
    assert not blank, f"out-of-subject root(s) with no written reason: {blank}"
    for root in _OUT_OF_SUBJECT_ROOTS:
        assert (_ROOT / root).is_dir(), (
            f"out-of-subject root {root!r} does not exist -- an exclusion for a directory that "
            "is not there is a stale excuse, not a boundary"
        )
