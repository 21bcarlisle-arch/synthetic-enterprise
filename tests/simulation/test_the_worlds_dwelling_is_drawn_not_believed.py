"""B12 — THE WORLD'S DWELLING FOR A DRAWN HOME IS DRAWN, NOT BELIEVED.

The defect these controls exist to keep dead
(`WORKER_FINDING_THE_WORLDS_DWELLING_FOR_A_DRAWN_HOME_IS_THE_COMPANYS_OWN_ESTIMATE_
2026-08-17`, BLOCKING, lane W4_the_wall):

`saas.property_model.build_properties()` builds the world's ground-truth dwelling
record. For a DRAWN (`SYN-*`) home it had no authored dwelling to read, so it called
`_derive_syn_property_fields()`, whose own docstring says it returns "saas-side
approximations" — the SUPPLIER's guess. Its EPC band was the literal `"D"`, and the
company's zero-knowledge fallback (`company.crm.property_discovery.
DEFAULT_EPC_RATING`, confidence 0.10) is also `D`. So the company's belief about a
drawn home's fabric was correct 2/2 (100%) against 3/7 (43%) on the authored cohort,
and it could not have been anything else: one literal produced both sides.

Two things make it BLOCKING rather than cosmetic. The dwelling drives EPC
consumption multipliers, ASHP uplift and demand shape through
`HouseholdDemandRegister`, so a harness figure scoring the supplier's property
belief scores a copy against its original. And the drawn cohort is the half that
GROWS — the book scales by drawing, not by authoring — so measured accuracy climbs
toward 100% for no reason connected to skill (the R12 shape through the back door).

WHAT THE CONTROLS BELOW MUST DO, and why each direction is here (R15): the world's
dwelling must MOVE with the published distribution and NOT move with either
supplier-side constant. A test that only pinned "mutating the supplier's constant
leaves the world alone" would pass just as well if the world's dwelling were a third
hardcoded letter, so `test_mutating_the_published_band_distribution_moves_the_worlds_
dwelling` proves the drawn band really is read from the published anchor, and
`test_the_suppliers_modal_band_is_still_reachable_without_the_worlds_dwelling` proves
the mutation is reachable at all — that the guard, not vacuity, is what makes the
other direction pass.

The anchor is `simulation.premise_population`'s EHS 2022-23 Energy Chapter AT1_2
band marginal, raked into the published property-type/build-era joint. It was in the
tree already: the finding's own "the anchor is not in the tree and must not be
invented" was WRONG, and B12's DISCOVER block died on that fact rather than on a new
research pass.
"""
from __future__ import annotations

import ast
import math
import re
from pathlib import Path

import pytest

from saas.property_model import BASIS_SAAS_APPROXIMATION
from simulation import premise_population as pp
from simulation.dwelling_records import (
    BASIS_WORLD_DRAW,
    DwellingNotDrawn,
    build_properties,
)
from simulation.live_population import (
    live_drawn_households,
    live_dwellings,
    live_population,
)
from simulation.population_draw import draw_population

REPO_ROOT = Path(__file__).resolve().parents[2]

# A cohort big enough to judge a share against its published target. λ=300/yr over
# the drawn window; the draw saturates far above this (`WORKER_FINDING_THE_
# POPULATION_DRAW_SATURATES_ABOVE_LAMBDA_745`), so this is inside the honest range.
_BIG_LAMBDA = 300.0
_BIG_SEED = 20260817


@pytest.fixture(scope="module")
def big_drawn_cohort():
    """Every DOMESTIC drawn home in a large cohort, as (customer, premise) pairs."""
    drawn = [
        sc
        for sc in draw_population(
            _BIG_SEED, acquisitions_per_year_lambda=_BIG_LAMBDA, draw_region=True
        )
        if sc.premise is not None
    ]
    assert len(drawn) > 800, f"fixture precondition: need a judgeable cohort, got {len(drawn)}"
    return drawn


@pytest.fixture
def activated_book(monkeypatch):
    """The real live book with the draw pinned ON, independent of the curriculum."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    return live_population()


def _drawn_records(book, dwellings):
    static_free = {cid for cid in dwellings}
    props = build_properties(book, dwellings=dwellings)
    return {cid: rec for cid, rec in props.items() if cid in static_free}


def _abs_tolerance(p: float, n: int) -> float:
    """3.5 binomial standard deviations, floored so a tiny published share is not
    judged to a tolerance narrower than one draw."""
    return max(3.5 * math.sqrt(p * (1 - p) / n), 2.0 / n)


# ---------------------------------------------------------------------------
# The premise: the world really does draw the dwelling now
# ---------------------------------------------------------------------------
def test_every_drawn_home_in_the_live_book_carries_the_worlds_dwelling(monkeypatch, activated_book):
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    dwellings = live_dwellings()
    assert dwellings, "the activated book must hand the world a dwelling per drawn home"
    records = _drawn_records(activated_book, dwellings)
    assert records, "no drawn resi-electricity record to judge"
    for cid, rec in records.items():
        assert rec["dwelling_basis"] == BASIS_WORLD_DRAW, (
            f"{cid} was built at basis {rec['dwelling_basis']} — the supplier's "
            "approximation is standing in as the world's ground truth again"
        )


def test_the_drawn_band_shares_recover_the_published_marginal(big_drawn_cohort):
    """The band a drawn home actually gets comes from EHS AT1_2, not a constant.

    Judged on the CUSTOMER draw (the subject of the finding), not on
    `premise_population`'s own population — the wiring is what was broken.
    """
    n = len(big_drawn_cohort)
    observed: dict[str, float] = {}
    for sc in big_drawn_cohort:
        observed[sc.premise.epc_band] = observed.get(sc.premise.epc_band, 0.0) + 1 / n
    worst = {}
    for band, target in pp.PUBLISHED_EPC_BAND_SHARE.items():
        got = observed.get(band, 0.0)
        worst[band] = (got, target, _abs_tolerance(target, n))
    failures = {b: v for b, v in worst.items() if abs(v[0] - v[1]) > v[2]}
    assert not failures, f"drawn band shares departed from the published marginal: {failures}"


def test_the_dwelling_draw_does_not_perturb_the_acquisition_stream(monkeypatch):
    """C-S2: the premise draw runs in its OWN substream, so switching it off must
    leave every OBSERVABLE acquisition field byte-identical."""
    import simulation.population_draw as popdraw

    with_dwelling = [sc.to_customer_dict() for sc in draw_population(_BIG_SEED)]
    monkeypatch.setattr(popdraw, "_draw_dwelling", lambda *a, **k: None)
    without = [sc.to_customer_dict() for sc in draw_population(_BIG_SEED)]
    assert with_dwelling == without


# ---------------------------------------------------------------------------
# The wall: the world's dwelling is not an observable
# ---------------------------------------------------------------------------
def test_the_worlds_dwelling_never_crosses_the_wall():
    """No `company/**` or `saas/**` module may read the world's dwelling. The
    accessors are world-side by name; this is the control that keeps them there."""
    accessors = ("live_premises", "live_dwellings", "live_drawn_households")
    # The IMPORT is the crossing (the same definition `tools/epistemic_wall.py` uses),
    # and a company-side module cannot reach a world accessor without one. Prose
    # naming the accessor — `saas.property_model` documents where its `dwellings`
    # argument comes from — is not a crossing and must not be counted as one.
    offenders = []
    for root in ("company", "saas"):
        for path in (REPO_ROOT / root).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for line_no, line in enumerate(text.splitlines(), start=1):
                stripped = line.strip()
                if not (stripped.startswith("from ") or stripped.startswith("import ")):
                    continue
                if "live_population" not in stripped:
                    continue
                for name in accessors:
                    if re.search(rf"\b{name}\b", stripped):
                        offenders.append(f"{path.relative_to(REPO_ROOT)}:{line_no}:{name}")
    assert not offenders, f"the world's dwelling is being read company-side: {offenders}"


def test_the_drawn_customer_dict_still_carries_no_dwelling(monkeypatch):
    """The repair must not have fixed the mirror by opening a leak: the saas-shaped
    dict the company is handed carries OBSERVABLES only, so the premise the world
    drew must not appear in it under any key."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    hidden = {"premise", "epc_rating", "home_type", "bedrooms", "property_type", "build_era"}
    for sc in draw_population(20260724, draw_region=True):
        leaked = hidden & sc.to_customer_dict().keys()
        assert not leaked, f"{sc.customer_id}: dwelling truth leaked through the seam: {leaked}"


# ---------------------------------------------------------------------------
# R15 — the mutations, in both directions
# ---------------------------------------------------------------------------
def test_mutating_the_suppliers_modal_band_does_not_move_the_worlds_dwelling(
    monkeypatch, activated_book
):
    """THE FINDING'S OWN FALSIFIER, run against the drawn cohort specifically — on
    the authored cohort it always passed, which is exactly how this survived."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    dwellings = live_dwellings()
    before = _drawn_records(activated_book, dwellings)
    import saas.property_model as prop

    monkeypatch.setattr(prop, "_SYN_MODAL_EPC_RATING", "A")
    monkeypatch.setattr(prop, "_SYN_PROPERTY_TYPE_BY_BAND", {"LOW": "detached", "MEDIUM": "detached", "HIGH": "detached"})
    after = _drawn_records(activated_book, dwellings)
    assert before == after


def test_the_suppliers_modal_band_is_still_reachable_without_the_worlds_dwelling(
    monkeypatch, activated_book
):
    """The vacuity guard for the test above: the SAME mutation must move SOMETHING,
    or the other direction passes because the constant is dead rather than because
    the world is independent of it.

    REWRITTEN 2026-08-18 (KNIFE3 step 35, B12 split), and the change of subject is
    deliberate rather than incidental. This guard used to call `build_properties`
    with no world dwelling and read the `saas_approximation` record that came back —
    step 31's "deliberately silent-but-labelled rather than" fatal choice, pinned
    below at line ~299. The split REVERSES that choice for the world: its builder now
    raises `DwellingNotDrawn` instead of guessing, because the world knows every home
    it drew. The supplier's derivation is untouched and still labels its own output
    `saas_approximation`, so the mutation is still reachable — through the supplier,
    which is the only side that was ever entitled to it.
    """
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    drawn_ids = set(live_dwellings())
    import saas.property_model as prop

    drawn = [c for c in activated_book if c["customer_id"] in drawn_ids]
    assert drawn, "no drawn customers — the guard would be vacuous itself"

    before = {c["customer_id"]: prop._derive_syn_property_fields(c)["epc_rating"] for c in drawn}
    monkeypatch.setattr(prop, "_SYN_MODAL_EPC_RATING", "A")
    after = {c["customer_id"]: prop._derive_syn_property_fields(c)["epc_rating"] for c in drawn}
    moved = [cid for cid in drawn_ids if before[cid] != after[cid]]
    assert moved, "the mutation is unreachable — this whole file would be theatre"
    # And the supplier's answer is still labelled as the supplier's answer.
    assert BASIS_SAAS_APPROXIMATION == "saas_approximation"

    # The world, meanwhile, refuses the guess outright rather than labelling it.
    with pytest.raises(DwellingNotDrawn):
        build_properties(drawn)


def test_mutating_the_companys_default_moves_the_belief_and_not_the_world(monkeypatch):
    """The other direction the finding names: the company's own constant must move
    the company's BELIEF and nothing about the world."""
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    import company.crm.property_discovery as disc
    from company.crm.property_model import EPCRating

    world_before = {cid: dict(d) for cid, d in live_dwellings().items()}
    belief_before = disc.open_belief_from_signup("UPRN-1", __import__("datetime").date(2024, 1, 1))
    monkeypatch.setattr(disc, "DEFAULT_EPC_RATING", EPCRating.A)
    belief_after = disc.open_belief_from_signup("UPRN-1", __import__("datetime").date(2024, 1, 1))
    world_after = {cid: dict(d) for cid, d in live_dwellings().items()}
    assert belief_before.epc_rating != belief_after.epc_rating, "the belief mutation is unreachable"
    assert world_before == world_after


def test_mutating_the_published_band_distribution_moves_the_worlds_dwelling(monkeypatch):
    """The direction that proves the world reads the ANCHOR: swap the published C and
    F shares and the drawn cohort's bands follow the swap. Without this, a world
    dwelling frozen at a third hardcoded letter would pass every test above."""
    swapped = dict(pp.PUBLISHED_EPC_BAND_SHARE)
    swapped["C"], swapped["F"] = pp.PUBLISHED_EPC_BAND_SHARE["F"], pp.PUBLISHED_EPC_BAND_SHARE["C"]
    monkeypatch.setattr(pp, "PUBLISHED_EPC_BAND_SHARE", swapped)
    bands = [
        sc.premise.epc_band
        for sc in draw_population(
            _BIG_SEED, acquisitions_per_year_lambda=_BIG_LAMBDA, draw_region=True
        )
        if sc.premise is not None
    ]
    n = len(bands)
    f_share = bands.count("F") / n
    c_share = bands.count("C") / n
    assert f_share > 0.30 and c_share < 0.10, (
        f"published C/F swap did not reach the drawn cohort (C={c_share:.3f}, F={f_share:.3f})"
    )


# ---------------------------------------------------------------------------
# The measurement the finding reported — repaired
# ---------------------------------------------------------------------------
def test_the_companys_guess_about_a_drawn_home_is_wrong_at_the_published_rate(big_drawn_cohort):
    """The finding's headline number, judged on a cohort big enough to have one.

    The company's confidence-0.10 fallback is band D and property type semi-detached.
    Its accuracy on the drawn cohort must now be the PUBLISHED prevalence of those
    values — i.e. a real prior's hit rate — never 100%.
    """
    import company.crm.property_discovery as disc
    from company.crm.property_model import EPCRating
    from company.crm.property_model import PropertyType as CompanyPropertyType

    assert disc.DEFAULT_EPC_RATING is EPCRating.D
    assert disc.DEFAULT_PROPERTY_TYPE is CompanyPropertyType.SEMI_DETACHED
    n = len(big_drawn_cohort)
    band_hits = sum(1 for sc in big_drawn_cohort if sc.premise.household.epc_rating == "D") / n
    type_hits = sum(
        1
        for sc in big_drawn_cohort
        if pp.PROPERTY_TYPE_RECORD_NAME[sc.premise.household.property_type] == "semi"
    ) / n
    band_target = pp.PUBLISHED_EPC_BAND_SHARE["D"]
    type_target = pp.PUBLISHED_PROPERTY_TYPE_SHARE[pp.PropertyType.SEMI_DETACHED]
    assert abs(band_hits - band_target) <= _abs_tolerance(band_target, n), (
        f"the company's D guess is right {band_hits:.3f} of the time against a "
        f"published prevalence of {band_target:.3f}"
    )
    assert abs(type_hits - type_target) <= _abs_tolerance(type_target, n)
    assert band_hits < 0.6 and type_hits < 0.6, "the mirror is back"


# ---------------------------------------------------------------------------
# No fail-open: every live consumer must be wired
# ---------------------------------------------------------------------------
def test_every_live_consumer_asks_the_world_for_the_dwelling():
    """Forgetting to pass the world's dwelling was the fail-open risk while the
    builder fell back to the supplier's guess, so the call sites are enumerated
    here: a new consumer that omits it fails by name, without anyone having
    remembered this rule.

    2026-08-18 (KNIFE3 step 35): that fallback is gone on the world side — the
    builder raises `DwellingNotDrawn` — so this enumeration is no longer the ONLY
    thing standing between a forgetful consumer and a laundered guess. It is kept
    because it still fails EARLIER and by name, at the call site rather than at the
    first drawn customer, and because the other two consumers it lists have no
    equivalent raise of their own.
    """
    # Parsed, not grepped: a text scan counts every docstring that NAMES
    # `build_properties()` and then gets muted for it (the false-positive route the
    # drawn-shape class guard already refused). `ast` sees calls only.
    consumers = {
        "build_properties": "dwellings",
        "HouseholdDemandRegister": "drawn_households",
    }
    offenders = []
    for root in ("simulation", "saas", "company", "tools", "background"):
        for path in sorted((REPO_ROOT / root).rglob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:  # pragma: no cover - a file we do not own the grammar of
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                func = node.func
                name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
                required = consumers.get(name)
                if required is None:
                    continue
                if not any(kw.arg == required for kw in node.keywords):
                    offenders.append(
                        f"{path.relative_to(REPO_ROOT)}:{node.lineno} {name}()"
                    )
    assert not offenders, (
        "these live call sites build a dwelling record without asking the world for "
        f"the drawn homes: {offenders}"
    )
