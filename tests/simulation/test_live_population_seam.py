"""R15 both-ways tests for the LIVE POPULATION SEAM (generator draw-wiring,
default-OFF, director-reserved activation).

The seam is the reversible half of the draw-wiring: DEFAULT-OFF it is byte
identical to the static book; ACTIVATED it additively appends the synthetic
SYN-* acquisition cohort. R15 demands the control can FAIL: these tests prove
the wire is LOAD-BEARING (flag-on adds SYN-*) AND that removing/omitting the
activation reverts exactly to the static book (mutation both-ways), and that
the epistemic wall holds (the drawn ground-truth `cohort` never surfaces).
"""

import ast
import dataclasses
import importlib

import pytest

from saas.customers import CUSTOMERS
from simulation import live_population as lp
from simulation.population_draw import Cohort

# The sanctioned crossing package, taken from the ratchet that DEFINES it rather
# than re-declared here -- two copies of a wall constant drift, and the drifting
# copy is always the one nobody is looking at.
from tests.architecture.test_epistemic_wall_ratchet import SEAM_PACKAGE

# Cohort dataclass fields that are DELIBERATELY OBSERVABLE (carried in the saas
# dict / public at enrolment): `region` is a public observable, `customer_id` is
# the identity key. EVERY OTHER field on the Cohort dataclass is HIDDEN SIM truth
# that must never reach an observable dict. Deriving the hidden set from the
# dataclass (rather than hardcoding it) keeps it in LOCKSTEP with Cohort — a NEW
# cohort field is hidden-by-default, so it cannot silently escape the wall test.
# This is the RUNTIME sibling of the static-scan FORBIDDEN_SEAM_SYMBOLS class
# closure (tools/epistemic_verifier.py): the static scan only scans SEAM files, so
# a leak through `SyntheticCustomer.to_customer_dict()` (a SIM internal, not a seam
# file) is invisible to it — the runtime wall test is the ONLY guard there, and its
# hardcoded set previously omitted `heating_fuel` (subset-coverage fail-open, CA1
# red-team 2026-07-29).
_OBSERVABLE_COHORT_FIELDS = {"customer_id", "region"}


def _hidden_cohort_field_names() -> set:
    """The set of field NAMES that must never appear as a key in an observable
    dict — derived from the Cohort dataclass so it stays total by construction."""
    names = {f.name for f in dataclasses.fields(Cohort)} - _OBSERVABLE_COHORT_FIELDS
    names.add("cohort")  # the container field on SyntheticCustomer itself
    return names


@pytest.fixture(autouse=True)
def _clear_flag(monkeypatch):
    """Ensure each test controls the activation flag explicitly (default OFF)."""
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)
    yield


def test_default_off_flag_predicate_is_false():
    assert lp.draw_population_enabled() is False


def test_default_off_is_static_book_byte_identical():
    """Flag OFF: the seam returns exactly the static CUSTOMERS content."""
    book = lp.live_population()
    assert book == list(CUSTOMERS)
    # A fresh list (mutating it must not corrupt the shared literal).
    assert book is not CUSTOMERS


def test_default_off_returns_fresh_list_each_call():
    a = lp.live_population()
    a.append({"customer_id": "MUTANT"})
    b = lp.live_population()
    assert not any(c.get("customer_id") == "MUTANT" for c in b)
    assert b == list(CUSTOMERS)


def test_activation_adds_synthetic_acquisitions(monkeypatch):
    """Flag ON: the book is CUSTOMERS + additive SYN-* acquisitions (the wire
    is load-bearing — its presence is what adds the cohort)."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    assert lp.draw_population_enabled() is True
    book = lp.live_population()
    # Additive-not-replacive: every static customer survives, in order, first.
    assert book[: len(CUSTOMERS)] == list(CUSTOMERS)
    extra = book[len(CUSTOMERS):]
    assert len(extra) >= 1, "activation must add at least one drawn acquisition"
    assert all(c["customer_id"].startswith("SYN-") for c in extra)
    # Fills the post-2020 acquisition gap the FRAME found.
    assert all(int(c["acquisition_date"][:4]) >= 2021 for c in extra)


def test_mutation_flag_off_reverts_exactly(monkeypatch):
    """MUTATION (both-ways): with the flag turned back off, the SYN-* cohort
    disappears and the book is exactly the static one again — proving the SYN
    entries come from the flag, not from an unconditional code path."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    assert any(c["customer_id"].startswith("SYN-") for c in lp.live_population())
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)
    off = lp.live_population()
    assert off == list(CUSTOMERS)
    assert not any(c["customer_id"].startswith("SYN-") for c in off)


def test_activation_is_deterministic_replay(monkeypatch):
    """C-S2 deterministic replay: activated twice yields an identical book."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    assert lp.live_population() == lp.live_population()


def test_wall_drawn_book_never_exposes_ground_truth_cohort(monkeypatch):
    """EPISTEMIC WALL: no saas-shaped dict the seam returns carries the hidden
    ground-truth `cohort` field — the company must discover, never read it."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    for c in lp.live_population():
        assert "cohort" not in c


def test_seam_requests_cohorts_load_bearing(monkeypatch):
    """CA1 LOAD-BEARING (R15 both-ways): the wall makes the flip UNOBSERVABLE in
    the returned dicts by construction, so the wall test alone cannot prove the
    seam actually activated cohorts. Spy on the draw the seam performs and assert
    it passes `assign_cohorts=True`. MUTATION: revert the flip (or its value) and
    this fires — the assertion is not derivable from the seam's output.
    """
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")

    import simulation.population_draw as pdmod

    captured = {}
    real_draw = pdmod.draw_population

    def _spy(seed, **kwargs):
        captured.update(kwargs)
        return real_draw(seed, **kwargs)

    # The seam imports draw_population LOCALLY from this module, so patch the name
    # at its source (simulation.population_draw) where the local import resolves it.
    monkeypatch.setattr(pdmod, "draw_population", _spy)

    lp.live_population()

    assert captured.get("assign_cohorts") is True, (
        "the live seam must draw with assign_cohorts=True (CA1 activation); "
        f"observed kwargs={captured}"
    )
    # The region activation (prior rung) is undisturbed by CA1.
    assert captured.get("draw_region") is True


def test_wall_re_proven_post_cohort_activation(monkeypatch):
    """CA1 (DIRECTOR_RULING_COHORT_ASSIGNMENT_ACTIVATED §1): after the live seam
    activates `assign_cohorts=True`, the wall must be RE-PROVEN to fire — i.e. the
    'no cohort in any dict' guarantee must hold precisely BECAUSE cohorts are now
    assigned, not because there is nothing to leak (that would be a tautological,
    R15-pattern-1 fail-open control).

    Both halves, tied to the SAME seed the seam uses:
      1. LOAD-BEARING: the underlying SIM-truth draw the seam consumes DOES carry
         a non-None cohort on every SYN customer (activation is live).
      2. WALL: none of those cohorts reaches any dict the seam returns.
    """
    from simulation.population_draw import draw_population

    monkeypatch.setenv("SE_DRAW_POPULATION", "1")

    # (1) The SIM-truth objects behind the seam, drawn with the seam's own seed +
    #     flags, all carry a cohort — so the wall has something real to hide.
    sim_truth = draw_population(
        lp._DEFAULT_BASE_SEED, draw_region=True, assign_cohorts=True
    )
    assert sim_truth, "activation must draw at least one synthetic customer"
    assert all(sc.cohort is not None for sc in sim_truth), (
        "post-activation every drawn SyntheticCustomer must carry a ground-truth "
        "cohort — otherwise the wall test below is vacuous"
    )

    # (2) The observable book the seam returns: the SYN-* dicts correspond 1:1 to
    #     those cohort-bearing objects, yet NONE exposes the cohort (nor any of its
    #     hidden fields). The company sees only saas-shaped observables.
    book = lp.live_population()
    syn = [c for c in book if c["customer_id"].startswith("SYN-")]
    assert len(syn) == len(sim_truth), (
        "the observable SYN-* stream must be 1:1 with the cohort-bearing draw"
    )
    hidden_fields = _hidden_cohort_field_names()
    for c in syn:
        assert not (hidden_fields & c.keys()), (
            f"wall breach: {hidden_fields & c.keys()} leaked into an observable dict"
        )


def test_runtime_wall_covers_every_forbidden_cohort_field():
    """CLASS-CLOSURE, sibling half (R15 subset-coverage, INDEPENDENT oracle).

    The static seam scan (tools/epistemic_verifier.FORBIDDEN_SEAM_SYMBOLS) is the
    canonical registry of cohort labels that must never cross the seam — but it
    only scans SEAM files, so it cannot see a leak through
    `SyntheticCustomer.to_customer_dict()`, which lives in the SIM-internal
    population_draw.py. The runtime wall test is the ONLY guard there. This asserts
    the runtime hidden-field set covers EVERY Cohort field the static scan forbids,
    so the two halves cannot drift: a Cohort field forbidden at the seam but
    unchecked at runtime (as `heating_fuel` was, CA1 red-team 2026-07-29) fails here.

    Non-tautological: the hidden set is DERIVED from the Cohort dataclass, the
    forbidden set is AUTHORED independently in the verifier. MUTATION: mark a genuine
    hidden field (e.g. add `heating_fuel`) OBSERVABLE, or drop it from the verifier's
    forbidden set, and the two lists diverge — this fires.
    """
    from tools.epistemic_verifier import FORBIDDEN_SEAM_SYMBOLS

    cohort_field_names = {f.name for f in dataclasses.fields(Cohort)}
    # Only Cohort-derived names (not the generic attitudinal tokens the scan also
    # lists like "Cohort"/"assign_cohort" that are class/function names, not fields).
    forbidden_cohort_fields = cohort_field_names & FORBIDDEN_SEAM_SYMBOLS
    assert "heating_fuel" in forbidden_cohort_fields, (
        "precondition: heating_fuel must be a Cohort field the static scan forbids"
    )
    missing = forbidden_cohort_fields - _hidden_cohort_field_names()
    assert not missing, (
        f"runtime wall omits Cohort fields the static scan canonically forbids: "
        f"{missing} — subset-coverage fail-open (sibling half of the "
        f"FORBIDDEN_SEAM_SYMBOLS class closure)"
    )


def test_to_customer_dict_never_emits_a_hidden_cohort_field():
    """Direct guard on the actual leak SURFACE: `to_customer_dict()` is an allowlist,
    so a NEW Cohort field is safe-by-construction — but if someone ever adds a
    hidden-field key to that render, this fires regardless of the seam wrapper.
    Checked against a real cohort-bearing draw so the render is exercised live."""
    from simulation.population_draw import draw_population

    hidden = _hidden_cohort_field_names()
    drawn = draw_population(lp._DEFAULT_BASE_SEED, draw_region=True, assign_cohorts=True)
    assert drawn and all(sc.cohort is not None for sc in drawn), (
        "draw must yield cohort-bearing customers or this guard is vacuous"
    )
    for sc in drawn:
        leaked = hidden & sc.to_customer_dict().keys()
        assert not leaked, f"to_customer_dict leaked hidden cohort field(s): {leaked}"


def _company_imports_in(source: str) -> set:
    """Every `company.*` module imported by `source`, extracted by AST.

    AST, not a substring scan: the previous form asserted `"from company" not in
    text`, which is the one-syntactic-form class -- it read the DOCSTRING as well
    as the code, missed `importlib.import_module("company...")` entirely, and
    could not tell the sanctioned seam package from company decisioning logic.

    Takes SOURCE, not the module path, so the extractor can be proven non-vacuous
    against a fixture. Deriving that proof from the live module instead would make
    it a vacuity guard that requires a LIVE DEBT: it would demand the seam keep
    importing `supply_book` forever and would fire falsely the day a later pass
    legitimately removes that import.
    """
    tree = ast.parse(source)
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module)
    return {m for m in found if m == "company" or m.startswith("company.")}


def _seam_module_source() -> str:
    src = importlib.util.find_spec("simulation.live_population").origin
    with open(src, "r", encoding="utf-8") as fh:
        return fh.read()


def _company_logic_offenders(modules) -> set:
    """The company imports that are NOT the sanctioned crossing surface."""
    return {m for m in modules
            if not (m == SEAM_PACKAGE or m.startswith(SEAM_PACKAGE + "."))}


def test_seam_module_imports_company_only_through_the_sanctioned_seam():
    """Wall hygiene: the seam must not import company LOGIC -- a discovery-side
    read of a supply-side book.

    It MAY import `company.interfaces.*`. That package is the declared crossing
    surface in either direction (`tests/architecture/test_epistemic_wall_ratchet.py`
    ::SEAM_PACKAGE), and KNIFE pass 2 deliberately routed sixteen `simulation/`
    roster reads through `company.interfaces.supply_book` to replace sixteen
    undeclared `from saas.customers import CUSTOMERS` crossings. Forbidding it
    here would have forbidden the very surface the wall sanctions -- which is
    exactly what wedged the publish gate on 2026-08-09.
    """
    offenders = _company_logic_offenders(_company_imports_in(_seam_module_source()))
    assert not offenders, (
        "simulation/live_population.py imports company logic outside the "
        f"sanctioned seam `{SEAM_PACKAGE}`: {sorted(offenders)}"
    )


def test_the_company_import_guard_can_fail():
    """R15 both-ways: the guard above is only evidence if it FIRES on its own
    named defect. Proven on FIXTURE sources, so the proof stays valid however the
    real seam's imports later change.

    The extractor half matters as much as the predicate half: the assertion this
    replaced was a substring scan, which the module's own docstring could satisfy.
    """
    # 1. EXTRACTOR: it sees real imports in both syntactic forms, and is not
    #    fooled by the word "company" appearing in prose.
    assert _company_imports_in(
        '"""A docstring that says: from company.analytics import everything."""\n'
        "import os\n"
    ) == set(), "prose mentioning an import must not count as one"
    assert _company_imports_in("import company.analytics.cohort_discovery\n") == {
        "company.analytics.cohort_discovery"
    }
    assert _company_imports_in(
        "from company.interfaces.supply_book import registered_supply_points\n"
    ) == {"company.interfaces.supply_book"}

    # 2. PREDICATE: company LOGIC is rejected, the sanctioned crossing survives.
    assert _company_logic_offenders({"company.analytics.cohort_discovery"}) == {
        "company.analytics.cohort_discovery"
    }
    assert _company_logic_offenders({"company"}) == {"company"}
    assert _company_logic_offenders({"company.interfaces.supply_book"}) == set()

    # 3. COMPOSED, on a source that is a real defect: the guard fires end-to-end.
    defect = (
        "from company.interfaces.supply_book import registered_supply_points\n"
        "import company.analytics.cohort_discovery\n"
    )
    assert _company_logic_offenders(_company_imports_in(defect)) == {
        "company.analytics.cohort_discovery"
    }
