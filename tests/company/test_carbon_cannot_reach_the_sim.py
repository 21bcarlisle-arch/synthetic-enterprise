"""E5 FRAME control C9 — the wall breach: a SAVED carbon event sourced from
method-A CRN truth (`docs/design/E5_CARBON_THREE_LEDGER_FRAME.md` §2.2, §3).

C9's named defect is that the carbon ledger's SAVED figure comes from the SIM's
own counterfactual — the sim re-run under common random numbers, which is ground
truth and not an observable. A supplier cannot know what a customer WOULD have
consumed; if the carbon ledger can read that, the mission metric is measuring the
sim's answer and not the company's.

WHAT THE FRAME LITERALLY ASKED FOR, AND WHY THAT IS NOT WHAT IS BUILT HERE.
C9's control column reads: "`tools.epistemic_verifier` + a test that no
`company/carbon` module imports `simulation.*`/`sim.*`". Measured before built,
that ask decomposes into one half already shipped and one half that is the same
ADJACENCY-FOR-REACHABILITY defect the C4 and C8 passes cut out of the R14 publish
gate and the CARBON_NOT_A_TARGET guard on 2026-08-22:

  * The one-hop half ALREADY EXISTS and already covers this package.
    `tools/epistemic_verifier.py` scans every `company/`+`saas/` file for literal
    and dynamic SIM imports; `company/carbon/carbon_ledger.py` is in subject
    today `[observed-with-evidence: _is_company_file True, _is_exempt False, and
    an injected `from simulation.run_phase2b import x` scans as a violation]`.
    Rebuilding it here would have produced a second, divergent copy of a shipped
    control — so PART 1 DELEGATES to the verifier and pins the coverage instead.
    C9 names the verifier as half its control, so whether the verifier still
    looks at carbon is itself a fail-silent question and is asserted, not assumed.

  * The other half — "no `company/carbon` module imports `sim.*`" — is a ONE-HOP
    question standing in for a REACHABILITY claim, and the gap is not theoretical.
    `company/interfaces/` is the ONE path the verifier holds EXEMPT (it is the
    approved seam and its job is to touch sim internals). MEASURED THIS PASS: add
    `from company.interfaces.sim_interface import get_cached_prices` to
    `carbon_ledger.py` and the shipped verifier returns NO violation, while that
    one line puts the carbon ledger's forward closure at 16 modules with live
    routes to `sim.cache_store`, `sim.flex_dispatch`, `sim.gas_prices_history`
    and `sim.system_prices_history` — four sim internals, one attribute access
    away, with every test on the tree green. `test_the_guard_is_reachability_not_adjacency`
    states that as a live falsifier rather than a comment.

SO THE CONTROL IS DENY-BY-DEFAULT ON THE FORWARD CLOSURE. The subject set is
DERIVED (every module under `company/carbon`, whatever it is called tomorrow) and
the question is inverted from "did carbon import a sim module" to "does carbon
REACH sim by ANY chain of imports", walked FORWARDS over the whole graph. This is
the mirror of the CARBON_NOT_A_TARGET walk in `test_carbon_not_a_target.py`: that
one asks who can reach carbon, this one asks what carbon can reach. Any route
must be DECLARED by name with a written reason.

THE REGISTER IS EMPTY, and that is measured, not aspirational: over 996 modules
the carbon package's forward closure is ITSELF ALONE — it imports nothing in the
decision tree at all `[observed-with-evidence: closure size 2, zero banned hits,
2026-08-22]`. Empty is the strongest state, because while it holds, reachability
and adjacency give the same answer and the FRAME's claim is exactly true.

HONEST LIMITS — THREE, and none of them is closed by a green run here:

 (a) STATIC AND SYNTACTIC. `importlib.import_module(name)` on a runtime-built
     string is not an edge in this graph. The shipped verifier DOES catch the
     dynamic form, but only one hop and only in `company/`+`saas/` files, so a
     dynamic sim import inside an INTERMEDIARY that carbon reaches is covered by
     neither half. That hole is real and is why the register being empty matters.

 (b) THIS IS THE IMPORT PATH, NOT THE DATA PATH. It proves carbon cannot CALL
     into the sim. It cannot prove that a counterfactual number produced by the
     sim was not written to a JSON file, or a fixture, and read back as though it
     were an observable. The §2.2 method choice (B / C / A) stays a director
     values-call precisely because no import guard can make it for him.

 (c) THE SEAM IS NOT PRE-APPROVED HERE. `company/interfaces/sim_interface.py`
     is the legitimate observables seam and company code is meant to use it —
     but it reaches nine sim symbols, so a blanket exemption would hand carbon
     the whole bridge and inherit whatever the seam exposes NEXT. A carbon route
     through the seam is therefore permitted only as a named declaration with a
     written reason, and `test_a_declared_route_inherits_its_whole_forward_closure`
     is what makes that declaration expensive.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Mapping, Set, Tuple

import pytest

from tests.company.test_carbon_not_a_target import (
    _import_targets,
    _module_name,
    _read,
    _ROOT,
)
from tools import epistemic_verifier

_CARBON_PACKAGE = "company.carbon"

# The SIM side of the wall. Matched as package-or-submodule, never as a substring.
_SIM_PACKAGES: Tuple[str, ...] = ("sim", "simulation")

# The graph the forward walk runs over. This is deliberately WIDER than the
# subject set: these are TRANSIT roots, not subjects. A module here is not being
# accused of anything -- it is here so that a chain passing THROUGH it is still a
# chain. `tools/` and `site/` are in for exactly that reason, and their presence
# here is the difference between this walk and the backward one in
# `test_carbon_not_a_target.py`, which excludes them as out of SUBJECT: the
# reporting lane may legitimately READ carbon, but carbon routing to the sim via
# a reporting module would be the same breach by a longer road.
_TRANSIT_ROOTS: Tuple[str, ...] = (
    "company",
    "sim",
    "simulation",
    "saas",
    "background",
    "tools",
    "site",
)

# Routes permitted from `company/carbon` towards the sim, each with a WRITTEN
# REASON. MEASURED EMPTY on 2026-08-22 over 996 modules: the carbon package's
# forward closure is itself alone.
_CARBON_SIM_ROUTE_DECLARATIONS: Mapping[str, str] = {}

# FAIL-OPEN floor on the TRANSIT graph. A walk that silently narrowed to a few
# files would find no route because it had nowhere to go -- the classic
# passes-because-it-checked-nothing shape. 996 modules were in the graph when
# this floor was set; it is a floor on COVERAGE, never a target (R12).
_GRAPH_FLOOR = 800


# ===========================================================================
# PART 1 — the one-hop half is DELEGATED, and its coverage is pinned
# ===========================================================================

_CARBON_FILE = "company/carbon/carbon_ledger.py"


def test_the_epistemic_verifier_still_holds_carbon_in_subject():
    """FAIL-SILENT. C9 names `tools.epistemic_verifier` as half its control, so
    "does that verifier still look at this package" is a question the control
    must ANSWER, not assume. An unavailable check is a FAILED check (R15).

    MUTATION: add `company/carbon/` to `epistemic_verifier.EXEMPT_PATHS` → RED.
    """
    assert epistemic_verifier._is_company_file(_CARBON_FILE), (
        f"{_CARBON_FILE} is no longer a company file to the epistemic verifier -- "
        "the one-hop half of C9 has gone silent"
    )
    assert not epistemic_verifier._is_exempt(_CARBON_FILE), (
        f"{_CARBON_FILE} is EXEMPT from the epistemic verifier -- C9's own named "
        "control would pass vacuously on the carbon package"
    )


@pytest.mark.parametrize(
    "line",
    [
        "from simulation.run_phase2b import run",
        "import simulation.weather_engine",
        "from sim.cache_store import get_cached_prices",
        "import sim",
    ],
)
def test_the_verifier_catches_a_direct_sim_import_in_carbon(line):
    """The delegated half, proven on the REAL carbon source with a synthetic
    breach injected IN MEMORY -- never written to a tree other lanes share.

    MUTATION: remove `sim`/`simulation` from `epistemic_verifier.SIM_PACKAGES`,
    or drop the `^import {pkg}$` form from `FORBIDDEN_SOURCES` → RED.
    """
    source = _read(_ROOT / _CARBON_FILE)
    injected = source.replace(
        "from __future__ import annotations",
        f"from __future__ import annotations\n{line}",
        1,
    )
    assert line in injected, "the injection did not apply -- the probe is stale"
    findings = epistemic_verifier._scan_source(injected, _CARBON_FILE)
    assert findings, (
        f"the shipped epistemic verifier did not flag {line!r} in {_CARBON_FILE}. "
        "C9's one-hop half is delegated to that verifier; if it is silent here, "
        "nothing is checking the direct import"
    )


def test_the_shipped_carbon_source_is_clean_to_the_verifier():
    """The null control for PART 1. If the real file were already dirty, every
    assertion above would pass for the wrong reason.

    MUTATION: none needed -- this is the direction that proves the injected
    probes above are what turned the verifier red.
    """
    findings = epistemic_verifier._scan_source(_read(_ROOT / _CARBON_FILE), _CARBON_FILE)
    assert not findings, f"{_CARBON_FILE} already breaches the wall one-hop: {findings}"


# ===========================================================================
# PART 2 — deny-by-default: carbon may not REACH the sim by any chain
# ===========================================================================


def _carbon_subjects() -> Tuple[str, ...]:
    """DERIVED, not named: every module under the carbon package. A file added to
    `company/carbon/` tomorrow is a subject with nobody editing a list."""
    d = _ROOT / _CARBON_PACKAGE.replace(".", "/")
    if not d.is_dir():
        return ()
    return tuple(
        sorted(
            _module_name(p)
            for p in d.rglob("*.py")
            if "__pycache__" not in p.parts
        )
    )


def _transit_files() -> Tuple[Path, ...]:
    files = []
    for root in _TRANSIT_ROOTS:
        d = _ROOT / root
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            files.append(p)
    return tuple(files)


def _transit_edges() -> Tuple[Dict[str, Set[str]], Tuple[str, ...]]:
    """(module -> imported names, parse failures). A file that will not parse is
    returned as a FAILURE, never dropped: a scanner that skips what it cannot
    read is how a route leaves the graph without anyone noticing (R15
    fail-silent). Uses the SAME `_import_targets` as the backward walk, so there
    is one parser on this tree and not two that can drift apart."""
    edges: Dict[str, Set[str]] = {}
    failures = []
    for p in _transit_files():
        module = _module_name(p)
        try:
            tree = ast.parse(_read(p))
        except SyntaxError as exc:
            failures.append(f"{p.relative_to(_ROOT)}: {exc}")
            continue
        edges[module] = _import_targets(tree, module)
    return edges, tuple(failures)


def _is_sim(name: str) -> bool:
    return any(name == pkg or name.startswith(pkg + ".") for pkg in _SIM_PACKAGES)


def _resolve(edges: Mapping[str, Set[str]], name: str) -> str | None:
    """An imported NAME may be a module (`company.pricing.desk`) or a symbol
    inside one (`company.pricing.desk.Desk`). Resolve to the longest prefix that
    is a real module in the graph, so a `from pkg.mod import Thing` edge is
    followed to `pkg.mod` and not dropped as an unknown name."""
    parts = name.split(".")
    while parts:
        candidate = ".".join(parts)
        if candidate in edges:
            return candidate
        parts.pop()
    return None


def _routes_to_the_sim(
    edges: Mapping[str, Set[str]], starts: Tuple[str, ...]
) -> Tuple[Dict[str, str], Set[str]]:
    """Walk FORWARDS from `starts` over the whole graph.

    Returns ({sim name reached -> the module that imports it}, modules visited).
    Forwards, because the claim is about what carbon can reach; a one-hop
    neighbourhood would answer a different question and answer it wrongly the
    moment carbon imports anything at all."""
    hits: Dict[str, str] = {}
    seen: Set[str] = set(starts)
    frontier: Set[str] = set(starts)
    while frontier:
        nxt: Set[str] = set()
        for module in frontier:
            for target in edges.get(module, ()):  # noqa: B905 - plain lookup
                if _is_sim(target):
                    hits.setdefault(target, module)
                    continue
                resolved = _resolve(edges, target)
                if resolved and resolved not in seen:
                    seen.add(resolved)
                    nxt.add(resolved)
        frontier = nxt
    return hits, seen


def test_the_carbon_subject_set_is_derived_and_non_empty():
    """FAIL-OPEN. A guard whose subject set is empty passes every other test
    below while checking nothing at all.

    MUTATION: point `_CARBON_PACKAGE` at a directory that does not exist → RED.
    """
    subjects = _carbon_subjects()
    assert subjects, (
        f"no modules found under {_CARBON_PACKAGE} -- the subject set is empty, so "
        "this control is passing without checking anything"
    )
    assert all(s.startswith(_CARBON_PACKAGE) for s in subjects), subjects


def test_the_transit_graph_is_wide_enough_to_contain_a_route():
    """FAIL-OPEN. The walk can only find a chain that is in the graph.

    MUTATION: narrow `_TRANSIT_ROOTS` to one root → RED on the floor.
    """
    edges, failures = _transit_edges()
    assert not failures, (
        f"unparseable module(s) in the transit graph -- the walk is incomplete and "
        f"an incomplete walk is a FAILED check, not a clean one: {failures}"
    )
    assert len(edges) >= _GRAPH_FLOOR, (
        f"transit graph is {len(edges)} modules, floor {_GRAPH_FLOOR}. A route from "
        "carbon to the sim can only be found if the modules it passes through are here"
    )


def test_no_carbon_module_reaches_the_sim_undeclared():
    """THE CONTROL. Deny-by-default, by REACHABILITY, over the derived subject set.

    THE DEFECT: a SAVED event sourced from the sim's own CRN counterfactual
    (FRAME §2.2). The company cannot observe what a customer WOULD have used; if
    the ledger can reach the sim, the mission metric is reading ground truth
    through the wall.

    MUTATIONS: (1) add an import of any sim module to a carbon module → RED;
    (2) add an import of `company.interfaces.sim_interface` → RED here while the
    shipped one-hop verifier stays GREEN, which is the whole reason this exists;
    (3) replace `_routes_to_the_sim` with a one-hop scan → the adjacency test
    below goes RED.
    """
    edges, failures = _transit_edges()
    assert not failures, f"unparseable module(s) -- the walk is incomplete: {failures}"
    subjects = _carbon_subjects()
    assert subjects, "empty subject set"

    hits, _ = _routes_to_the_sim(edges, subjects)
    declared_modules = {
        _module_name(_ROOT / p) for p in _CARBON_SIM_ROUTE_DECLARATIONS
    }
    undeclared = {
        sim_name: via for sim_name, via in hits.items() if via not in declared_modules
    }
    assert not undeclared, (
        f"the carbon package can reach {len(undeclared)} sim name(s) with no declared "
        f"route: {sorted(undeclared.items())[:10]}. E5 C9: a SAVED figure that can be "
        "sourced from the sim's own counterfactual is not an observable, and the "
        "company cannot see inside the sim. Declare the route here with a written "
        "reason, or cut the import"
    )


def test_the_guard_is_reachability_not_adjacency():
    """THE LOAD-BEARING FALSIFIER. C9's literal ask, and the shipped verifier that
    implements it, both ask a ONE-HOP question. `company/interfaces/` is the one
    path the verifier holds exempt, so a single seam import in a carbon module
    opens a route to the sim that BOTH one-hop halves read as clean.

    This asserts the divergence live, on the real graph and the real verifier,
    rather than describing it in a comment.

    MUTATION: replace the forward closure with a one-hop scan of the carbon
    modules' own imports → RED (the mutated guard finds nothing).
    """
    edges, _ = _transit_edges()
    subjects = _carbon_subjects()
    seam = "company.interfaces.sim_interface"
    assert seam in edges, f"{seam} is no longer in the graph -- pick a new probe"

    # The one-hop half, on the same injected source: still green.
    injected = _read(_ROOT / _CARBON_FILE).replace(
        "from __future__ import annotations",
        "from __future__ import annotations\n"
        "from company.interfaces.sim_interface import get_cached_prices",
        1,
    )
    assert not epistemic_verifier._scan_source(injected, _CARBON_FILE), (
        "the shipped one-hop verifier now flags a seam import. If that has become "
        "a violation, this probe no longer demonstrates the gap -- re-derive it"
    )

    # The derived half, on the same edge: red, and red on real sim internals.
    mutated = {k: set(v) for k, v in edges.items()}
    mutated[subjects[-1]].add(seam)
    hits, _visited = _routes_to_the_sim(mutated, subjects)
    assert hits, (
        "a carbon module importing the approved seam did not reach the sim -- this "
        "guard is measuring adjacency, not reachability, and the seam's own nine "
        "sim imports are invisible to it"
    )
    assert any(name.startswith("sim.") for name in hits), (
        f"reached only {sorted(hits)} -- expected real sim internals through the seam"
    )


def test_relative_imports_are_resolved_not_dropped():
    """A dropped edge is a hole in the forward walk, and the carbon package is
    exactly where a relative import would be written (`from .factors import ...`).

    MUTATION: make `_import_targets` ignore `node.level` → RED.
    """
    tree = ast.parse("from .factors import GRID_INTENSITY")
    assert "company.carbon.factors" in _import_targets(tree, "company.carbon.carbon_ledger")
    tree2 = ast.parse("from ..interfaces.sim_interface import get_cached_prices")
    assert "company.interfaces.sim_interface" in _import_targets(
        tree2, "company.carbon.carbon_ledger"
    )


def test_a_symbol_import_is_followed_to_its_module():
    """`from company.interfaces.sim_interface import get_cached_prices` records an
    edge to the SYMBOL. If the walk only followed names that are literally modules,
    that edge would be dropped and the chain would end there.

    MUTATION: make `_resolve` return `None` unless the whole name is a module → RED.
    """
    edges, _ = _transit_edges()
    seam = "company.interfaces.sim_interface"
    assert _resolve(edges, f"{seam}.get_cached_prices") == seam
    assert _resolve(edges, "os.path.join") is None


def test_the_sim_match_is_package_shaped_not_a_substring():
    """A substring test would call `simplifications` or `similarity` a sim import
    and a package-shaped one will not.

    MUTATION: replace `_is_sim` with `"sim" in name` → RED.
    """
    assert _is_sim("sim") and _is_sim("sim.cache_store")
    assert _is_sim("simulation") and _is_sim("simulation.run_phase2b")
    assert not _is_sim("simplifications")
    assert not _is_sim("company.crm.similarity")
    assert not _is_sim("saas.simulator_shim")


# ===========================================================================
# PART 3 — the route register: an admission, and a non-growable one
# ===========================================================================


def test_every_declared_route_names_a_file_that_exists():
    """MUTATION: declare a path that is not on disk → RED. A declaration for a
    file nobody can find is an excuse with no subject."""
    missing = [
        p for p in _CARBON_SIM_ROUTE_DECLARATIONS if not (_ROOT / p).is_file()
    ]
    assert not missing, f"carbon->sim route declaration(s) name a missing file: {missing}"


def test_every_declared_route_is_still_used():
    """The REPAIRED direction. A route that has since been cut must lose its
    declaration, or the register becomes a standing permit for a future import.

    MUTATION: declare any file in the tree (the register is measured empty, so
    every module fails the still-used test) → RED.
    """
    edges, _ = _transit_edges()
    subjects = _carbon_subjects()
    _hits, visited = _routes_to_the_sim(edges, subjects)
    stale = [
        p
        for p in _CARBON_SIM_ROUTE_DECLARATIONS
        if (_ROOT / p).is_file() and _module_name(_ROOT / p) not in visited
    ]
    assert not stale, (
        f"declared carbon->sim route(s) the carbon package no longer reaches: {stale}. "
        "Remove the declaration -- a standing exemption for a repaired subject is how "
        "the register stops being an admission and starts being a loophole"
    )


def test_every_declared_route_carries_a_written_reason():
    """MUTATION: blank a reason → RED. A declaration without a reason is an
    allowlist entry, which is the thing deny-by-default exists to abolish."""
    blank = [
        p for p, why in _CARBON_SIM_ROUTE_DECLARATIONS.items() if not (why or "").strip()
    ]
    assert not blank, f"carbon->sim route declaration(s) with no written reason: {blank}"


def test_a_declared_route_inherits_its_whole_forward_closure():
    """What makes a declaration EXPENSIVE, and therefore rare — honest limit (c).
    Declaring the seam does not buy one edge: it buys everything the seam reaches,
    including whatever it is made to expose next. Asserted against the LIVE graph
    with a synthetic declaration, so it holds while the register is empty.

    MUTATION: make `_routes_to_the_sim` stop at a declared module instead of
    walking through it → RED.
    """
    edges, _ = _transit_edges()
    seam = "company.interfaces.sim_interface"
    assert seam in edges, f"{seam} is no longer in the graph -- pick a new probe"
    hits, visited = _routes_to_the_sim(edges, (seam,))
    assert len(hits) >= 5, (
        f"declaring {seam} was expected to inherit its whole sim surface; it reached "
        f"only {sorted(hits)}. If the seam has genuinely narrowed, re-derive the floor"
    )
    assert len(visited) >= 5, (
        f"the forward closure of {seam} is {len(visited)} module(s) -- a declaration "
        "that costs nothing downstream is not a cost, and the register would grow freely"
    )


def test_the_transit_roots_are_declared_and_real():
    """The boundary of this walk, written down. A root listed here that is not on
    disk contributes nothing and would silently shrink the graph.

    MUTATION: add a non-existent root, or drop `tools`/`site` (the reporting-lane
    transit paths) → the graph floor test goes RED.
    """
    missing = [r for r in _TRANSIT_ROOTS if not (_ROOT / r).is_dir()]
    assert not missing, (
        f"transit root(s) that do not exist: {missing} -- a root that is not there is "
        "a hole in the walk, not a boundary"
    )
    assert len(set(_TRANSIT_ROOTS)) == len(_TRANSIT_ROOTS), "duplicate transit root"
