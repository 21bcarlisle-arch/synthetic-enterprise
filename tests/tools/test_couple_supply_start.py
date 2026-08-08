"""Tests for the re-contracting <-> supply-start coupled-triad runner
(``tools/couple_supply_start.py``).

This closes residual (c) of ``C_supply_start_semantic_separation``: *"L3 additionally
owes the coupled-triad gap measurement: the company has not yet been tested against a
world that re-contracts a customer and then checks whether its believed tenure tracks
the truth."*

R15 is the point of this file. A coupled-gap runner is a CONTROL -- it is evidence in a
level promotion and it is rendered on the Proof door -- so it does not count unless a
MUTATION proves it fires on its own named defect. The mutations below each break one
specific thing and assert the measurement MOVES:

  1. The company re-couples supply_start to the anchor (today's pre-fix behaviour)
     -> the separated gap must jump from 0 to the naive gap.
  2. The world stops re-contracting (activation == anchor) -> the naive gap must
     collapse to 0. This proves the measured gap is caused by the world's
     re-contracting, NOT manufactured by the harness.
  3. The company is handed the answer key directly -> gap 0, i.e. the leak is
     detectable rather than indistinguishable from competence.
  4. Abstentions are dropped instead of scored at no-skill -> the company would look
     perfect by declining to answer; the shipped scorer must not permit that.

Plus the FAIL-OPEN sweep on the scorer (empty / mismatched / all-abstain populations)
and the wall check that the answer key never reaches the company side.
"""
import datetime as dt

import pytest

from background import coupled_triad as ct
from tools import couple_supply_start as run


AS_OF = run.DEFAULT_AS_OF


# ---------------------------------------------------------------------------
# The world
# ---------------------------------------------------------------------------

def test_world_recontracts_and_the_anchor_is_not_the_truth():
    """A successor's real relationship start is a LATER term boundary than the
    predecessor's genesis anchor its record carries. If these were equal there
    would be no defect to measure."""
    world = run.draw_recontracting_world(AS_OF)
    recontracted = [a for a in world if a.is_recontracted]

    assert recontracted, "the world must actually re-contract someone"
    for account in recontracted:
        assert account.true_relationship_start > account.term_anchor
        # on the 365-day term grid the anchor pinning exists to preserve
        delta = (dt.date.fromisoformat(account.true_relationship_start)
                 - dt.date.fromisoformat(account.term_anchor)).days
        assert delta % run.TERM_DAYS == 0
        assert account.true_relationship_start <= AS_OF


def test_base_accounts_are_undisturbed():
    """Base customers genuinely began on the date their record carries -- they are in
    the population so the score is not taken on successors alone, and the harness
    must not invent a re-contracting for them."""
    world = run.draw_recontracting_world(AS_OF)
    base = [a for a in world if not a.is_recontracted]

    assert len(base) > len([a for a in world if a.is_recontracted])
    for account in base:
        assert account.true_relationship_start == account.term_anchor


def test_world_is_deterministic():
    """C-S2: same inputs -> same population on every machine, no global RNG."""
    assert run.draw_recontracting_world(AS_OF) == run.draw_recontracting_world(AS_OF)


# ---------------------------------------------------------------------------
# The wall
# ---------------------------------------------------------------------------

def test_company_observables_carry_only_crm_fields():
    """The record handed to the company is exactly what a CRM row holds -- the
    anchor, the predecessor link, and the account's own registration/metering/
    billing observables. Pinned as an exact set: if the answer key ever rode along
    in some extra field, every gap below would become a tautology."""
    world = run.draw_recontracting_world(AS_OF)
    records, _ = run.observables_for(world, run.FULL_OBSERVABILITY)

    for record in records:
        assert set(record) == {
            "customer_id", "acquisition_date", "successor_of",
            "acquisition_event_date", "first_meter_read_date",
            "first_issued_bill_date",
        }


def test_withholding_the_registration_event_actually_bites():
    """Under a regime that loses the registration event, the derivation must not
    still come out with the right answer -- otherwise 'degraded' would be degraded
    in name only and the sweep would prove nothing."""
    world = run.draw_recontracting_world(AS_OF)
    regime = run.ObservableRegime("no_activation", activation_capture=0.0)
    records, activations = run.observables_for(world, regime)
    by_id = {a.account_id: a for a in world}

    for record in records:
        account = by_id[record["customer_id"]]
        if not account.is_recontracted:
            continue
        assert account.account_id not in activations
        assert record["acquisition_event_date"] is None
        derived = run.derive_supply_start(record, activations)
        assert derived != account.true_relationship_start


def test_the_metering_observable_is_present_and_the_derivation_ignores_it():
    """A NAMED, MEASURED FINDING -- recorded, not fixed on sight (SELF-INTERRUPT
    DISCIPLINE), and minted as its own atom.

    `first_meter_read_date` is a legitimate observable that the world hands over and
    that does NOT go missing with the registration paperwork: a supplier that is not
    reading the meter is not supplying. `derive_supply_start`'s middle rung
    nonetheless hands back an `acquisition_date` that predates it -- emitting a value
    that violates `SUPPLY_START_NOT_BEFORE_FIRST_OBSERVABLE`, the very invariant this
    same atom registered as law. The guard catches it downstream (below), so nothing
    published is wrong; but the derivation and the invariant disagree, and this test
    pins that disagreement so it cannot quietly persist as an unnoticed assumption."""
    world = run.draw_recontracting_world(AS_OF)
    regime = next(r for r in run.SWEEP_REGIMES if r.name == "activation_lost_link_lost")
    records, activations = run.observables_for(world, regime)
    by_id = {a.account_id: a for a in world}

    contradicted = 0
    for record in records:
        account = by_id[record["customer_id"]]
        if not account.is_recontracted:
            continue
        assert record["first_meter_read_date"] == account.true_relationship_start
        derived = run.derive_supply_start(record, activations)
        if derived is not None and derived < record["first_meter_read_date"]:
            contradicted += 1

    assert contradicted > 0


# ---------------------------------------------------------------------------
# The headline measurement
# ---------------------------------------------------------------------------

def test_headline_gap_is_the_live_company_belief_and_is_non_degenerate():
    """The published gap is what the company believes TODAY (tenure from
    `acquisition_date`), and it is a real, bounded, non-zero number."""
    result, _ = run.measure(AS_OF)

    assert result.gap is not None
    assert 0.0 < result.gap <= 1.0
    assert result.metric == "prediction"
    assert result.components["n_recontracted"] > 0


def test_measurement_is_deterministic():
    r1, _ = run.measure(AS_OF)
    r2, _ = run.measure(AS_OF)
    assert r1.gap == r2.gap
    assert r1.components["regime_sweep"] == r2.components["regime_sweep"]


def test_live_belief_invents_a_multi_year_phantom_tenure():
    """The defect in one number: every re-contracted account reads as though the
    relationship never restarted."""
    result, extras = run.measure(AS_OF)
    naive = extras["headline"]["naive"]

    # every re-contracted account is wrong, and wrong by years -- not a rounding edge
    assert naive.n_confident_wrong == result.components["n_recontracted"]
    assert naive.n_unknown == 0, "the live belief never abstains; it answers, wrongly"
    assert naive.mean_phantom_years > 1.0


# ---------------------------------------------------------------------------
# What the built mechanism achieves -- and where the world defeats it
# ---------------------------------------------------------------------------

def test_separated_mechanism_recovers_truth_when_the_registration_arrived():
    """With the activation observable present the CRM records the date it actually
    processed. Zero here is CORRECT, not a wall leak: the registration date is not
    hidden world state the company has to infer (see the module docstring)."""
    _, extras = run.measure(AS_OF)
    separated = extras["headline"]["separated"]

    assert separated.gap == 0.0
    assert separated.n_unknown == 0
    assert separated.n_confident_wrong == 0


def test_losing_the_activation_costs_coverage_not_truth():
    """Activation lost, link kept -> the company abstains. An honest UNKNOWN: it
    scores worse, but it never invents a tenure."""
    world = run.draw_recontracting_world(AS_OF)
    regime = next(r for r in run.SWEEP_REGIMES if r.name == "activation_lost_link_kept")
    row = run.measure_regime(world, regime, AS_OF)

    assert row["separated"].n_unknown > 0
    assert row["separated"].n_confident_wrong == 0
    assert row["separated"].mean_phantom_years == 0.0
    assert row["separated"].gap > 0.0


def test_losing_the_link_as_well_defeats_the_mechanism_entirely():
    """THE NAMED DEFEAT. `derive_supply_start`'s middle rung says "no `successor_of`,
    so this record's own `acquisition_date` is its start" -- so when the predecessor
    link is lost too, it hands back the anchor and is CONFIDENTLY WRONG again. The
    atom's protection is contingent on the linkage observable, and this asserts that
    contingency out loud rather than leaving it implied."""
    world = run.draw_recontracting_world(AS_OF)
    regime = next(r for r in run.SWEEP_REGIMES if r.name == "activation_lost_link_lost")
    row = run.measure_regime(world, regime, AS_OF)

    n_recontracted = sum(1 for a in world if a.is_recontracted)
    assert row["separated"].n_unknown == 0
    assert row["separated"].n_confident_wrong == n_recontracted
    assert row["separated"].mean_phantom_years > 1.0
    # no better than the pre-fix company: the DERIVATION buys nothing here
    assert row["separated"].gap == pytest.approx(row["naive"].gap)


# ---------------------------------------------------------------------------
# Defence in depth -- the R10 class guard is a genuine second line
# ---------------------------------------------------------------------------

def test_the_class_guard_catches_every_phantom_the_derivation_lets_through():
    """The derivation is defeated when both observables go missing -- but the atom
    is not. `SUPPLY_START_NOT_BEFORE_FIRST_OBSERVABLE` re-derives the bound from the
    account's own meter reads and bills, which do not vanish with the paperwork, so
    every phantom is REJECTED rather than published."""
    world = run.draw_recontracting_world(AS_OF)
    regime = next(r for r in run.SWEEP_REGIMES if r.name == "activation_lost_link_lost")
    row = run.measure_regime(world, regime, AS_OF)

    assert row["separated_phantoms"] > 0
    assert row["separated_caught_by_guard"] == row["separated_phantoms"]


def test_the_class_guard_also_catches_the_live_companys_phantoms():
    """The reason this measurement is worth publishing: the guard this atom built
    ALREADY detects the live damage that `C_supply_start_consumer_routing` has to
    fix. That routing atom therefore has a ready-made acceptance oracle rather than
    needing a new one."""
    result, _ = run.measure(AS_OF)
    live = result.components["regime_sweep"][0]

    assert live["naive_phantoms"] == result.components["n_recontracted"]
    assert live["naive_caught_by_guard"] == live["naive_phantoms"]


def test_mutation_a_guard_that_cannot_fail_is_detected(monkeypatch):
    """MUTATION 5: make the class guard pass everything (the fail-open shape R15
    exists to resist). The catch count must collapse -- otherwise this runner would
    keep reporting defence-in-depth that no longer exists."""
    monkeypatch.setattr(run, "check_supply_start_not_before_first_observable",
                        lambda record: True)
    world = run.draw_recontracting_world(AS_OF)
    regime = next(r for r in run.SWEEP_REGIMES if r.name == "activation_lost_link_lost")
    row = run.measure_regime(world, regime, AS_OF)

    assert row["separated_phantoms"] > 0
    assert row["separated_caught_by_guard"] == 0


# ---------------------------------------------------------------------------
# R15 mutations -- the measurement must MOVE when its named defect is injected
# ---------------------------------------------------------------------------

def test_mutation_recoupling_supply_start_to_the_anchor_fires(monkeypatch):
    """MUTATION 1: revert the company to pre-fix behaviour (borrow the anchor for a
    successor). The separated gap must stop being 0 and become the naive gap."""
    def recoupled(customer, activation_by_account=None):
        return customer.get("acquisition_date")

    monkeypatch.setattr(run, "derive_supply_start", recoupled)
    _, extras = run.measure(AS_OF)

    separated = extras["headline"]["separated"]
    naive = extras["headline"]["naive"]
    assert separated.gap != 0.0
    assert separated.gap == pytest.approx(naive.gap)
    assert separated.n_confident_wrong == naive.n_confident_wrong


def test_mutation_a_world_that_never_recontracts_collapses_the_gap(monkeypatch):
    """MUTATION 2 (the independence proof): if the world stops re-contracting, the
    anchor IS the truth and the naive gap must fall to 0. So the measured gap is
    caused by the world's behaviour, not manufactured by the harness."""
    real = run.draw_recontracting_world

    def never_recontracts(as_of=AS_OF):
        return [
            run.WorldAccount(
                account_id=a.account_id,
                predecessor_id=a.predecessor_id,
                term_anchor=a.term_anchor,
                true_relationship_start=a.term_anchor,
                activation_event=a.term_anchor,
            )
            for a in real(as_of)
        ]

    monkeypatch.setattr(run, "draw_recontracting_world", never_recontracts)
    result, _ = run.measure(AS_OF)

    assert result.raw_gap == 0.0
    assert result.gap == 0.0


def test_mutation_handing_the_company_the_answer_key_is_visible(monkeypatch):
    """MUTATION 3: a leak must be DETECTABLE. If the company is fed the truth its
    gap is exactly 0 -- which for the naive (inference-free) belief means the
    observables carried something they should not have."""
    def leaked(record, as_of):
        world = {a.account_id: a for a in run.draw_recontracting_world(as_of)}
        return run._tenure_years(
            world[record["customer_id"]].true_relationship_start, as_of)

    monkeypatch.setattr(run, "believed_tenure_naive", leaked)
    world = run.draw_recontracting_world(AS_OF)
    row = run.measure_regime(world, run.FULL_OBSERVABILITY, AS_OF)

    assert row["naive"].gap == 0.0


def test_mutation_dropping_abstentions_would_flatter_the_company():
    """MUTATION 4: score only the accounts the company answered. Under the
    activation-lost regime that reads as a PERFECT company, because every account it
    got wrong is one it declined to answer. The shipped scorer must not do this --
    asserted both ways so a later reader cannot 'simplify' it back."""
    world = run.draw_recontracting_world(AS_OF)
    regime = next(r for r in run.SWEEP_REGIMES if r.name == "activation_lost_link_kept")
    records, activations = run.observables_for(world, regime)
    truth = {a.account_id: run._tenure_years(a.true_relationship_start, AS_OF)
             for a in world}

    truth_years = [truth[r["customer_id"]] for r in records]
    belief = [run.believed_tenure_separated(r, activations, AS_OF) for r in records]

    answered = [(t, b) for t, b in zip(truth_years, belief) if b is not None]
    dropped = run.score_belief([t for t, _ in answered], [b for _, b in answered])
    shipped = run.score_belief(truth_years, belief)

    assert dropped.gap == 0.0          # the flattering, wrong answer
    assert shipped.gap > 0.0           # what the shipped scorer reports
    assert shipped.n_unknown > 0


def test_an_all_abstain_company_scores_exactly_no_skill():
    """The stated abstention convention, pinned. Declining to answer everything is
    worth exactly the blind baseline -- not 0 (which would reward silence) and not
    an invented penalty."""
    truth = [1.0, 3.0, 9.0, 4.0]
    score = run.score_belief(truth, [None] * len(truth))

    assert score.gap == pytest.approx(1.0)
    assert score.unknown_share == 1.0
    assert score.n_confident_wrong == 0


def test_an_abstention_is_never_scored_as_zero_tenure():
    """'Treat UNKNOWN as zero' is the forbidden shortcut (it silently restores the
    phantom in the opposite direction). Proven by contrast, not by assertion."""
    truth = [10.0, 10.0, 10.0, 10.0]
    abstaining = run.score_belief(truth, [10.0, 10.0, None, None])
    as_zero = run.score_belief(truth, [10.0, 10.0, 0.0, 0.0])

    assert abstaining.raw_gap < as_zero.raw_gap
    assert abstaining.n_unknown == 2


# ---------------------------------------------------------------------------
# Fail-open sweep on the scorer (R15: absent/degenerate input must fail CLOSED)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("truth,belief", [
    ([], []),                      # empty population -- nothing was measured
    ([1.0, 2.0], [1.0]),           # length mismatch -- silently zipping would drop one
    ([1.0], [1.0, 2.0]),
])
def test_scorer_fails_loud_on_degenerate_input(truth, belief):
    with pytest.raises(ValueError):
        run.score_belief(truth, belief)


def test_confident_wrong_counts_only_overstatement_beyond_tolerance():
    """A phantom is an OVERSTATED relationship. An understatement is a different
    defect and must not be counted here, or the two would be averaged into one
    uninterpretable number."""
    truth = [10.0, 10.0, 10.0]
    score = run.score_belief(truth, [14.0, 6.0, 10.2])

    assert score.n_confident_wrong == 1
    assert score.max_phantom_years == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# Ledger contract
# ---------------------------------------------------------------------------

def test_ledger_entry_matches_the_reader_contract(tmp_path):
    """Round-trips through the SAME reader the Proof door and the BUILD draw gate
    use. Written to tmp_path -- never the real ledger."""
    from background.gap_metric import write_gap_entry

    result, _ = run.measure(AS_OF)
    path = tmp_path / "coupled_gap_ledger.json"
    write_gap_entry(run.WORLD_ATOM_ID, run.TWIN_ATOM_ID, result,
                    measured_at="2026-08-08T00:00:00+00:00",
                    run_git_commit="deadbeef", ledger_path=path)

    ledger = ct.load_gap_ledger(path)
    assert ct.gap_measured(run.WORLD_ATOM_ID, ledger)
    entry = ledger[run.WORLD_ATOM_ID]
    assert entry["twin_atom_id"] == run.TWIN_ATOM_ID
    assert entry["components"]["n_recontracted"] > 0
    assert "regime_sweep" in entry["components"]
