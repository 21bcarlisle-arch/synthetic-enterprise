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
    """Pin the activation flag OFF so each test states the state it tests.

    CHANGED 2026-08-13 (activation): this used to DELETE the variable, because
    unset meant OFF -- the draw was default-OFF and held for a director word.
    That word came, the committed curriculum
    (`docs/design/curriculum/population_draw_activation.json`) now says
    activated, and unset therefore means ON. The OFF-path invariants below are
    unchanged and still fully tested; what changed is that they now have to SAY
    off instead of assuming it. Tests of the new default set their own state.
    """
    monkeypatch.setenv("SE_DRAW_POPULATION", "0")
    yield


def test_flag_off_predicate_is_false():
    assert lp.draw_population_enabled() is False


def test_flag_off_is_static_book_byte_identical():
    """Flag OFF: the seam returns exactly the static CUSTOMERS content."""
    book = lp.live_population()
    assert book == list(CUSTOMERS)
    # A fresh list (mutating it must not corrupt the shared literal).
    assert book is not CUSTOMERS


def test_flag_off_returns_fresh_list_each_call():
    a = lp.live_population()
    a.append({"customer_id": "MUTANT"})
    b = lp.live_population()
    assert not any(c.get("customer_id") == "MUTANT" for c in b)
    assert b == list(CUSTOMERS)


def test_activation_adds_synthetic_acquisitions(monkeypatch):
    """Flag ON: the book is CUSTOMERS + additive SYN-* acquisitions (the wire
    is load-bearing — its presence is what adds the cohort).

    `SE_GROW_BOOK=0` pins PB3's net-new campaign OFF so this measures the DRAW and nothing
    else. Without it the test reads whatever `book_growth_activation.json` currently says and
    reds the moment that flag flips, on an assertion that was never about growth — the
    subject here is additive-not-replacive, and a second source of additions makes it
    untestable rather than wrong.
    """
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    monkeypatch.setenv("SE_GROW_BOOK", "0")
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
    monkeypatch.setenv("SE_DRAW_POPULATION", "0")
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


# ═══════════════════════════════════════════════════════════════════════════
# ACTIVATION (director console 2026-08-13). The draw is ON by committed
# curriculum, not by an export on one machine. These tests pin the ACTIVATED
# state itself -- without them the activation is a fact about this laptop's
# environment, which is exactly the out-of-tree state the IaC core forbids.
# ═══════════════════════════════════════════════════════════════════════════

import json as _json  # noqa: E402


def test_activation_is_on_by_committed_curriculum(monkeypatch):
    """THE ACTIVATION, pinned: with NO environment override, the seam draws.

    This is the test that fails if someone reverts the curriculum file, and the
    one that would have failed every day before 2026-08-13.
    """
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)
    assert lp.draw_population_enabled() is True
    book = lp.live_population()
    assert len(book) > len(CUSTOMERS)
    assert any(c["customer_id"].startswith("SYN-") for c in book)


def test_curriculum_file_is_the_state_of_record_not_the_environment(monkeypatch):
    """Reconstruct-from-repo-alone: the ON state comes from the committed file.

    MUTATION: point the module at a curriculum that says `activated: false` and
    the seam must go dark with the environment untouched -- proving the file is
    load-bearing and the activation is not secretly riding on an export.
    """
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)
    assert lp.draw_population_enabled() is True          # the real file
    import pathlib
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        off = pathlib.Path(d) / "off.json"
        off.write_text(_json.dumps({"activated": {"value": False}}))
        monkeypatch.setattr(lp, "_ACTIVATION_CURRICULUM", off)
        assert lp.draw_population_enabled() is False
        assert lp.live_population() == list(CUSTOMERS)


@pytest.mark.parametrize(
    "content",
    [None, "", "{}", '{"activated": {}}', '{"activated": {"value": "yes"}}', "not json at all"],
    ids=["missing", "empty", "no-key", "no-value", "wrong-type", "malformed"],
)
def test_unreadable_curriculum_fails_closed_to_off(monkeypatch, content):
    """R15 FAIL-OPEN killer: a broken curriculum file must NOT activate.

    OFF is the byte-identical default, so degrading to OFF leaves today's world
    running; degrading to ON would silently change which world the company faces
    on the strength of a typo.
    """
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)
    import pathlib
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        f = pathlib.Path(d) / "c.json"
        if content is not None:
            f.write_text(content)
        monkeypatch.setattr(lp, "_ACTIVATION_CURRICULUM", f)
        assert lp.draw_population_enabled() is False


def test_env_override_beats_the_curriculum_both_ways(monkeypatch):
    """An explicit env value wins in BOTH directions -- the escape hatch a test
    or a one-off replay needs, proven to work against an ACTIVATED curriculum."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "0")
    assert lp.draw_population_enabled() is False
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    assert lp.draw_population_enabled() is True


def test_the_book_stays_earned_never_granted(monkeypatch):
    """The director's binding constraint, as a control that can fail.

    Activation appends the lambda=1.0 EARNED trickle, never the N=200 coverage
    POOL. A regression that swapped the trickle for the pool would hand the
    company ~200 customers it never won; this fails long before anyone reads a
    margin figure and wonders why it moved.
    """
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)
    drawn = [c for c in lp.live_population() if c["customer_id"].startswith("SYN-")]
    assert 0 < len(drawn) <= 15, (
        f"activated book drew {len(drawn)} customers -- a trickle is single digits; "
        "anything near 200 means the coverage POOL has been appended as a BOOK"
    )
    assert all(c["acquisition_type"] == "synthetic_draw" for c in drawn), (
        "drawn points must stay distinguishable from fresh_market wins, or "
        "acquisition-cost accounting will charge CPA for a customer nobody won"
    )


def test_every_point_the_seam_returns_resolves_by_id(monkeypatch):
    """A book you can iterate but not RESOLVE is what broke the home-move path.

    `run_phase2b` looks a winning account back up through `registered_point()`
    and passes the result to `register_acquired_point()`. Before activation
    registered the drawn cohort, that lookup returned None for a SYN customer
    and the None went straight into the clone.
    """
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)
    from company.interfaces.supply_book import registered_point
    book = lp.live_population()
    unresolvable = [c["customer_id"] for c in book if registered_point(c["customer_id"]) is None]
    assert not unresolvable, f"seam returned points the book cannot resolve: {unresolvable}"


def test_registration_is_idempotent(monkeypatch):
    """Entrypoints bind the book at import time in arbitrary order, so the
    activation runs repeatedly per process. A non-idempotent register would
    grow the book on every call -- a grant by accident."""
    monkeypatch.delenv("SE_DRAW_POPULATION", raising=False)
    from company.interfaces.supply_book import drawn_supply_points
    first = len(lp.live_population())
    for _ in range(5):
        lp.live_population()
    assert len(lp.live_population()) == first
    ids = [c["customer_id"] for c in drawn_supply_points()]
    assert len(ids) == len(set(ids)), f"drawn book has duplicates: {ids}"


# ---------------------------------------------------------------------------
# PB3 — the net-new campaign's additions, through the same seam
# ---------------------------------------------------------------------------

def test_the_growth_mandate_adds_WON_accounts_on_top_of_the_drawn_cohort(monkeypatch):
    """Both flags ON: static roster, then the drawn trickle, then the accounts actually won.

    The ORDER is the assertion. Additive-not-replacive has to survive a second source of
    additions, and the two sources must stay distinguishable: `SYN-` was granted by the
    curriculum's trickle and `PROS-` was won through the funnel. A reader of the book who
    could not tell them apart could not tell a granted account from an earned one, which is
    the whole distinction PB3 exists to draw.
    """
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    monkeypatch.setenv("SE_GROW_BOOK", "1")
    book = lp.live_population()
    assert book[: len(CUSTOMERS)] == list(CUSTOMERS)
    extra = book[len(CUSTOMERS):]
    syn = [c for c in extra if c["customer_id"].startswith("SYN-")]
    won = [c for c in extra if c["customer_id"].startswith("PROS-")]
    assert syn and won, "both sources must be present when both flags are on"
    assert len(syn) + len(won) == len(extra), f"unclassified additions: {extra}"
    assert all(c["acquisition_type"] == "net_new_won" for c in won)
    assert all(c["commodity"] == "electricity" for c in won)


def test_the_growth_mandate_OFF_is_byte_identical_to_the_draw_alone(monkeypatch):
    """The seam's standing contract: OFF changes nothing.

    Same shape as the draw's own flag-off guarantee. If this ever reds, the campaign has
    started reaching the book through some path the flag does not gate, and every measurement
    taken with it off is suspect.
    """
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    monkeypatch.setenv("SE_GROW_BOOK", "0")
    off = lp.live_population()
    assert not [c for c in off if c["customer_id"].startswith("PROS-")]


def test_a_won_home_has_the_WORLDS_dwelling_not_the_suppliers_approximation(monkeypatch):
    """B12, on the accounts the campaign adds.

    `dwelling_records.build_properties` raises `DwellingNotDrawn` for a supplied customer the
    world drew no dwelling for, and it is right to: the alternative is `saas.property_model`
    filling one in from the supplier's modal band, so the company's guess would be correct by
    construction on the only cohort that grows. This is the regression test for the real
    failure — a full run stopped on `PROS-2016-0003` for exactly this.
    """
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    monkeypatch.setenv("SE_GROW_BOOK", "1")
    won = [c["customer_id"] for c in lp.live_population()
           if c["customer_id"].startswith("PROS-")]
    premises = lp.live_premises()
    households = lp.live_drawn_households()
    assert won, "fixture is vacuous if the campaign won nothing"
    assert all(cid in premises for cid in won)
    assert all(cid in households for cid in won)


# ═══════════════════════════════════════════════════════════════════════════
# PB2 -- THE UNWON REMAINDER, as a new SUBJECT of this existing instrument.
#
# `PB2_UNWON_REMAINDER_FRAME.md` §4(c) is explicit that PB2 must NOT build a
# third wall control: the static ratchet and this runtime guard already exist,
# and this repo's characteristic failure is an orphaned control, not an absent
# one. What PB2 supplies is the subject they never had -- the premises the
# world drew and the company never acquired.
#
# Why the static ratchet is not enough on its own here: the remainder is DATA,
# not an import. A company module that never imports `simulation.*` can still
# be HANDED the unwon set by a caller, and an import scan cannot see a value
# passed through a dict. That is the half this runtime guard covers.
# ═══════════════════════════════════════════════════════════════════════════


def _drawn_book_and_stock():
    """A book won out of a stock, with a non-empty remainder. Built here rather
    than in a fixture so each assertion below can state its own preconditions."""
    import datetime as dt

    from simulation.population_draw import draw_population
    from simulation.premise_population import draw_premise_population

    stock = draw_premise_population(200, base_seed=42, as_of=dt.date(2021, 1, 1))
    return draw_population(base_seed=42, premise_stock=stock), stock


def test_the_supplier_shaped_dict_never_carries_the_premise_it_was_won_at():
    """The account's premise is HIDDEN SIM TRUTH, exactly like `cohort`.

    The company discovers a home through `company.crm.property_discovery` and is
    entitled to be wrong about it. Emitting `premise` (or its id) in the saas-shaped
    dict would hand the company the world's answer -- and now that the premise is a
    STOCK member rather than a per-customer mint, its id would also hand over the
    account's position in the drawn population.
    """
    book, _ = _drawn_book_and_stock()
    assert book, "fixture is vacuous if nothing was drawn"
    for customer in book:
        rendered = customer.to_customer_dict()
        assert "premise" not in rendered
        assert "premise_id" not in rendered
        assert not any("premise" in str(k).lower() for k in rendered)


def test_the_unwon_remainder_is_reachable_only_from_sim():
    """A company-side read of the unwon set must be refused by the static ratchet.

    The remainder's only home is `simulation.population_draw.unwon_remainder`, and
    `simulation` is a wall side no `company.*` / `saas.*` module may import. This
    asserts the function IS in that module (so it inherits the ratchet's refusal)
    rather than having quietly been placed somewhere reachable.
    """
    from simulation.population_draw import subset_verdict, unwon_remainder

    for fn in (unwon_remainder, subset_verdict):
        assert fn.__module__ == "simulation.population_draw", (
            f"{fn.__name__} moved out of the SIM module the wall ratchet guards; "
            "the remainder would no longer be refused to the company by construction"
        )
        assert not fn.__module__.startswith(("company.", "saas."))


def test_the_remainder_is_not_derivable_from_what_the_company_can_see():
    """THE wall claim, stated as the leak it forbids.

    Given everything the seam hands the company -- the saas-shaped dicts for every
    account it holds -- the unwon premises must not be enumerable. This is the
    negative direction the FRAME names non-negotiable: a company-side read of
    drawn-but-not-acquired premises fails.
    """
    book, stock = _drawn_book_and_stock()
    remainder = {p.premise_id for p in __import__(
        "simulation.population_draw", fromlist=["unwon_remainder"]
    ).unwon_remainder(stock, book)}
    assert remainder, "fixture is vacuous if the company won the whole world"

    visible = set()
    for customer in book:
        for value in customer.to_customer_dict().values():
            visible.add(str(value))
            if isinstance(value, dict):
                visible.update(str(v) for v in value.values())

    assert not (remainder & visible), (
        "an unwon premise id surfaced in a supplier-visible dict -- the company can "
        "see a household it never approached"
    )


def test_the_remainder_leak_guard_can_fail():
    """R15 falsifier for the test above: deliberately leak one unwon premise into
    the observable dict and the SAME predicate must catch it. Without this, the
    assertion could be passing because the dicts happen to hold no ids at all."""
    book, stock = _drawn_book_and_stock()
    from simulation.population_draw import unwon_remainder

    remainder = {p.premise_id for p in unwon_remainder(stock, book)}
    leaked = sorted(remainder)[0]

    rendered = book[0].to_customer_dict()
    rendered["nearby_prospect"] = leaked  # the mutation

    visible = {str(v) for v in rendered.values()}
    assert remainder & visible, (
        "the leak guard did not fire on a deliberately leaked unwon premise -- "
        "it cannot fail, so it is not evidence"
    )


# ═══════════════════════════════════════════════════════════════════════════
# PB2 STEP 3 -- the wall, and the cross-path property the id guard used to carry
# ═══════════════════════════════════════════════════════════════════════════
def test_the_shipped_remainder_never_reaches_a_company_visible_dict(monkeypatch, tmp_path):
    """Exit (c) on the RUN's own stock, not a fixture's.

    The test above proves the property for a hand-built stock. This one proves it for
    the world the shipped seam actually draws -- 4,400 homes across the campaign's
    decade, of which the company won 68. The remainder is the other 4,332, and a
    supplier holds no object for any of them.
    """
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    monkeypatch.setenv("SE_GROW_BOOK", "1")
    # Never the repo's published path: resolving a campaign writes the verdict record,
    # and a test that resolves one must not restate the published figure as its own.
    monkeypatch.setattr(lp, "_SUBSET_VERDICT_RECORD", tmp_path / "verdict.json")
    lp._CAMPAIGN_MEMO.clear()
    try:
        from simulation.population_draw import unwon_remainder

        seed = lp._DEFAULT_BASE_SEED
        stock = lp.world_premise_stock(seed)
        book = [sc for sc in lp._drawn_trickle(seed)]
        book += [p for p, _w in lp._campaign(lp._pre_growth_book(seed), seed)["winners"]]
        remainder = {p.premise_id for p in unwon_remainder(stock, book)}
        assert remainder, "vacuous: the run left nothing unwon"

        visible = set()
        for c in lp.live_population(seed):
            visible.update(str(v) for v in c.values())
        assert not (remainder & visible), sorted(remainder & visible)[:5]
    finally:
        lp._CAMPAIGN_MEMO.clear()


def test_every_account_in_the_book_has_exactly_one_dwelling_of_its_own(monkeypatch, tmp_path):
    """The cross-path property `make_household`'s "one home, one id" guard USED to
    carry, asserted where the information actually is.

    That guard compared the drawn household's own label against the customer id, and
    it was independent evidence only because `draw_premise` labelled the household
    with the premise id and the premise id WAS the customer id -- the false join key.
    With a real join key the label is `PSTK-2021-0401` and the comparison is no longer
    available, so the property is stated directly instead of being inferred from an id
    collision: `live_premises()` and `live_population()` are two independent re-draws
    of the same world and they must agree on which accounts exist.

    Not hypothetical. The campaign memo's own comment records paying for this once --
    two callers keyed the memo differently and `live_premises()` ended up holding
    dwellings for winners that were not in the book.
    """
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    monkeypatch.setenv("SE_GROW_BOOK", "1")
    monkeypatch.setattr(lp, "_SUBSET_VERDICT_RECORD", tmp_path / "verdict.json")
    lp._CAMPAIGN_MEMO.clear()
    try:
        seed = lp._DEFAULT_BASE_SEED
        premises = lp.live_premises(seed)
        book_ids = {c["customer_id"] for c in lp.live_population(seed)}
        assert premises, "vacuous: the world drew no dwellings"

        orphans = set(premises) - book_ids
        assert not orphans, f"dwellings held for accounts not in the book: {sorted(orphans)}"

        # No dwelling serves two accounts. A set of premises smaller than the register
        # means one home was handed to more than one customer -- which `subset_verdict`'s
        # `double_won` clause would also catch, and this states at the seam.
        assert len({p.premise_id for p in premises.values()}) == len(premises)

        # And the household handed to each account is labelled for THAT account, which
        # is what keeps `simulation.household.make_household`'s guard meaningful.
        for cid, hh in lp.live_drawn_households(seed).items():
            assert hh.customer_id == cid
    finally:
        lp._CAMPAIGN_MEMO.clear()
