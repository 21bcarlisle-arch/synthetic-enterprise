"""The A/B's DENOMINATOR — every renewal the world offered, and the stage each stopped at.

THE DEFECT THESE TESTS WERE WRITTEN FROM (2026-08-28). `value_cycle_ab_s1_three_arm.json`
published `decision_shape.priced` = 25 against a book of 210 billing accounts settled in the
window, and `level_arm_decision_shape.priced` = 34 for an arm whose entire design is to price
EXACTLY the renewals the value arm prices. Nothing in the artefact could say where the other
renewals went, because the arm's eligibility guards return a 0.0 uplift and the rate chain logged
NOTHING for a renewal it did not price -- so "the world never offered it", "a guard refused it"
and "the arm priced it flat" were one indistinguishable absent log line. That is R15's FAIL-SILENT
pattern applied to a POPULATION rather than to a verdict, and it is why the headline could not be
read: a per-decision claim whose denominator cannot be counted is not a measurement.

Every test below is a MUTATION on the funnel: revert the named line and the test reds. The null
rungs are marked as such -- a control that only ever passes is the shape this file exists to
refuse.
"""
from __future__ import annotations

import ast
import inspect

import pytest

from company.policy.decision_policy import (
    CURRENT_POLICY,
    VALUE_ARM_POLICY,
    policy_scope,
)
from company.pricing import value_based_renewal as vbr
from company.pricing.renewal_rate_chain import decide_renewal_rate
from tools.run_value_cycle_ab import (
    FUNNEL_STAGE_MEANINGS,
    account_class_map,
    decision_population,
    funnel_by_account_class,
    product_label_by_account_class,
    renewal_funnel,
)

CHAIN_KWARGS = dict(
    customer_id="C1",
    billing_account="C1",
    commodity="electricity",
    term_start="2018-01-01",
    term_index=1,
    struck_unit_rate_gbp_per_mwh=120.0,
    portfolio_margin_rates=[],
    prior_term_margin_gbp=None,
    prior_term_revenue_gbp=0.0,
    is_domestic=True,
    segment="resi",
    settled_records=[],
)


def a_won_account_id() -> str:
    """A customer_id the WORLD records as won by the funnel, taken from the live roster.

    NOT HARD-CODED, since 2026-08-30. This file pinned `PROS-2019-0015`, which was a won account
    on the roster the day it was written. When `simulation/live_population` stopped letting the
    served-segments dial reach into the world's draw (director's ruling, 2026-08-30), the campaign
    began planning against the unfiltered world and won a DIFFERENT set of prospects — correctly —
    and that id left the roster. Two tests then reported `KeyError: 'won_by_the_funnel'` and
    `0 == 1`, which read as the funnel having stopped working. It had not: 176 accounts are won on
    the current roster.

    A control that names one account by id is pinned to today's answer and reds whenever the world
    legitimately redraws. The PROPERTY these tests assert is "a won account", so the fixture asks
    the world for one. Sorted for determinism; `acquisition_type` is the world's own record and is
    what `account_class_map` classifies on, so this establishes the precondition without borrowing
    the answer from the function under test.
    """
    from simulation.run_phase2b import CUSTOMERS

    won = sorted(c["customer_id"] for c in CUSTOMERS
                 if c.get("acquisition_type") == "net_new_won"
                 and c.get("commodity") == "electricity")
    assert won, "no won accounts on the roster -- these tests have lost their subject"
    return won[0]


def _row(**over):
    row = {
        "customer_id": "C1",
        "commodity": "electricity",
        "term_start": "2018-01-01",
        "term_index": 1,
        "tariff_type": "fixed",
        "arm": "value_based",
        "stage": vbr.STAGE_PRICED,
        "reason": None,
    }
    row.update(over)
    return row


def _result(rows):
    return {"phase2b": {"value_arm_funnel_log": list(rows)}}


# ---------------------------------------------------------------------------
# The chain writes the denominator at all, and writes it exactly once
# ---------------------------------------------------------------------------

def test_every_renewal_the_chain_sees_appears_in_the_funnel_exactly_once():
    """MUTATION: move `result.arm_funnel_entries.append(...)` inside the `declined` branch.

    The append is unconditional and sits ABOVE the priced/declined branches on purpose. A
    renewal that reaches the funnel by one path and misses it by another produces a denominator
    smaller than the population, and every share computed from it is then wrong in the
    flattering direction.
    """
    with policy_scope(VALUE_ARM_POLICY):
        for tariff_type in ("fixed", None, "deemed"):
            for commodity in ("electricity", "gas"):
                kwargs = dict(CHAIN_KWARGS, commodity=commodity)
                chain = decide_renewal_rate(tariff_type=tariff_type, **kwargs)
                assert len(chain.arm_funnel_entries) == 1, (
                    f"{commodity}/{tariff_type!r} produced "
                    f"{len(chain.arm_funnel_entries)} funnel rows, not one")


def test_the_control_arm_writes_a_funnel_even_though_it_prices_nothing():
    """THE FAIL-SILENT REPAIR ITSELF, and the reason the funnel is a separate list.

    `run_value_cycle_ab` ASSERTS that `value_arm_log` is empty on the control -- that emptiness
    is how it knows the writer is a no-op. So the world's own renewal count cannot live there.
    If the control's funnel were empty too, a reader could never tell how much of the book the
    arm can touch at all, which is the whole question this block answers.

    MUTATION: make the funnel append conditional on `arm != FLAT_RULES`.
    """
    with policy_scope(CURRENT_POLICY):
        chain = decide_renewal_rate(tariff_type="fixed", **CHAIN_KWARGS)
    assert chain.value_arm_entries == [], (
        "the control arm priced something -- this fixture no longer isolates the funnel")
    assert len(chain.arm_funnel_entries) == 1
    assert chain.arm_funnel_entries[0]["stage"] == vbr.STAGE_CONTROL_ARM


def test_the_funnel_row_never_leaks_into_the_arms_decision_log():
    """The two lists answer different questions and the A/B's control check reads only one.

    MUTATION: append the funnel row to `result.value_arm_entries` as well. The control-arm
    emptiness assertion in `run_value_cycle_ab.run_value_cycle_ab` would then raise on every
    run, which is a loud failure -- but on the VALUE arm it would silently inflate
    `decision_shape.priced` by every renewal the arm refused, which is not.
    """
    with policy_scope(VALUE_ARM_POLICY):
        chain = decide_renewal_rate(tariff_type=None, **CHAIN_KWARGS)
    assert chain.arm_funnel_entries[0]["stage"] == vbr.STAGE_PRODUCT_NOT_UPLIFTABLE
    assert chain.value_arm_entries == [], (
        "a renewal the arm was not eligible to price appeared in `value_arm_log`, where "
        "`arm_decision_shape` counts everything not flagged `declined` as PRICED")


# ---------------------------------------------------------------------------
# The stage names come from the adapter, not from a second copy in the counter
# ---------------------------------------------------------------------------

def test_every_stage_the_adapter_can_return_is_declared_and_described():
    """MUTATION: add a guard to `renewal_margin_uplift` with a fresh `not_run_stage=` literal.

    A counter carrying its own copy of the eligibility rule is how a funnel comes to report a
    population its subject does not have. This reads the guards out of the adapter's own source
    and refuses a stage the funnel does not know how to count or describe.
    """
    tree = ast.parse(inspect.getsource(vbr.renewal_margin_uplift))
    emitted = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg == "not_run_stage" and isinstance(kw.value, ast.Name):
                emitted.add(getattr(vbr, kw.value.id))
    assert emitted, (
        "no `not_run_stage=` keyword found in `renewal_margin_uplift` -- the guards stopped "
        "reporting which one fired, so every drop reads as one anonymous bucket")
    unknown = emitted - set(vbr.FUNNEL_STAGES)
    assert not unknown, f"{sorted(unknown)} is returned by a guard but not in FUNNEL_STAGES"
    undescribed = set(vbr.FUNNEL_STAGES) - set(FUNNEL_STAGE_MEANINGS)
    assert not undescribed, f"{sorted(undescribed)} is counted in the artefact but not described"


def test_the_prose_reason_alone_cannot_carry_the_funnel():
    """WHY `not_run_stage` EXISTS beside `not_run_reason`, asserted rather than argued.

    The prose interpolates the offending value ("tariff type None has no locked margin to
    move"), so a funnel grouping on the reason reports one bucket per distinct tariff type and
    can never report a stage total. MUTATION: delete `not_run_stage` and group on `reason`.
    """
    seen = {}
    with policy_scope(VALUE_ARM_POLICY):
        for tariff_type in (None, "deemed", "flex"):
            chain = decide_renewal_rate(tariff_type=tariff_type, **CHAIN_KWARGS)
            row = chain.arm_funnel_entries[0]
            seen[tariff_type] = (row["stage"], row["reason"])
    stages = {v[0] for v in seen.values()}
    reasons = {v[1] for v in seen.values()}
    assert stages == {vbr.STAGE_PRODUCT_NOT_UPLIFTABLE}, (
        f"three unpriceable products reported {len(stages)} stages: {stages}")
    assert len(reasons) == 3, (
        "the prose reasons collapsed too -- this fixture no longer demonstrates why a "
        "machine-readable stage key is needed")


# ---------------------------------------------------------------------------
# The funnel block itself
# ---------------------------------------------------------------------------

def test_a_run_without_the_log_is_unavailable_and_never_a_denominator_of_zero():
    """R15 FAIL-OPEN. MUTATION: return `{"priced": 0, ...}` for a run predating the log.

    A funnel that reports 0 for a run that never carried one is indistinguishable from a run in
    which the world offered no renewals at all -- and the second is a finding.
    """
    block = renewal_funnel({"phase2b": {}}, "value_arm")
    assert block["available"] is False
    assert "priced" not in block, "an unavailable funnel published a count anyway"
    assert renewal_funnel({"phase2b": {"value_arm_funnel_log": []}}, "value_arm")[
        "available"] is False


def test_the_stage_counts_reconcile_to_the_row_count():
    """MUTATION: drop any stage from `FUNNEL_STAGES`.

    The stages are exhaustive over the adapter's terminal states, so they must sum to the
    population. A funnel whose stages sum to less than its own denominator has lost renewals
    somewhere between the guard and the reader, and nothing else in the artefact would say so.
    """
    rows = (
        [_row(stage=vbr.STAGE_PRICED)] * 25
        + [_row(stage=vbr.STAGE_PRODUCT_NOT_UPLIFTABLE, tariff_type=None)] * 400
        + [_row(stage=vbr.STAGE_NOT_THE_ARMS_COMMODITY, commodity="gas")] * 563
        + [_row(stage=vbr.STAGE_ACQUISITION_TERM, term_index=0)] * 210
        + [_row(stage=vbr.STAGE_DECLINED)] * 3
    )
    block = renewal_funnel(_result(rows), "value_arm")
    assert block["renewals_the_world_offered"] == len(rows)
    assert sum(s["count"] for s in block["stages"]) == len(rows)
    assert block["priced"] == 25
    assert block["declined"] == 3
    assert block["priced_share_of_renewals_offered"] == round(25 / len(rows), 4)


def test_the_biggest_drop_is_broken_out_by_the_product_that_caused_it():
    """"213 terms whose product was never labelled" and "213 customers on a variable tariff"
    are the same integer and opposite conclusions. MUTATION: delete
    `product_not_upliftable_by_tariff_type` and read the stage count alone.
    """
    rows = (
        [_row(stage=vbr.STAGE_PRODUCT_NOT_UPLIFTABLE, tariff_type=None)] * 400
        + [_row(stage=vbr.STAGE_PRODUCT_NOT_UPLIFTABLE, tariff_type="variable")] * 6
        + [_row(stage=vbr.STAGE_PRICED)] * 25
    )
    breakdown = renewal_funnel(_result(rows), "value_arm")[
        "product_not_upliftable_by_tariff_type"]
    assert breakdown == {"'variable'": 6, "None": 400}


def test_an_unrecognised_stage_is_named_rather_than_folded_away():
    """MUTATION: fold unknown stages into an "other" bucket, or drop them silently.

    A stage this block does not know about means the adapter grew a guard and the counter did
    not follow it. Silently dropping it breaks the reconciliation above; silently bucketing it
    hides which guard appeared.
    """
    block = renewal_funnel(_result([_row(stage="a_guard_added_later")]), "value_arm")
    assert block["unrecognised_stages"] == ["a_guard_added_later"]


def test_the_funnel_names_the_accounts_the_arm_could_reach():
    """The 2026-08-28 finding in one field: 25 decisions, nine accounts.

    MUTATION: publish only the count. An account list is what turns "the experiment is small"
    into "the experiment runs on the nine hand-authored seed customers and no others".
    """
    rows = (
        [_row(stage=vbr.STAGE_PRICED, customer_id=f"C{i}") for i in range(1, 10)]
        + [_row(stage=vbr.STAGE_PRODUCT_NOT_UPLIFTABLE, customer_id="SYN-2021-001",
                tariff_type=None)]
    )
    block = renewal_funnel(_result(rows), "value_arm")
    assert block["accounts_the_arm_priced"] == [f"C{i}" for i in range(1, 10)]
    assert block["accounts_the_world_offered_a_renewal"] == 10


def test_a_null_funnel_in_which_the_arm_priced_everything_reads_as_such():
    """NULL RUNG. The block must be able to report a WIDE surface as well as a narrow one, or a
    reader cannot tell a measurement from a constant.
    """
    block = renewal_funnel(_result([_row(stage=vbr.STAGE_PRICED)] * 40), "value_arm")
    assert block["priced_share_of_renewals_offered"] == 1.0
    assert all(s["count"] == 0 for s in block["stages"] if s["stage"] != vbr.STAGE_PRICED)


# ---------------------------------------------------------------------------
# The cross-arm denominators
# ---------------------------------------------------------------------------

def _funnel(priced: int, arm: str) -> dict:
    return renewal_funnel(
        _result([_row(stage=vbr.STAGE_PRICED, customer_id=f"C{i}") for i in range(priced)]), arm)


def test_the_two_arms_denominators_are_published_beside_each_other():
    """THE 25-VERSUS-34 DEFECT. MUTATION: publish `per_arm` for one arm only, or drop
    `largest_denominator_difference`.

    `arm_identity` guards the POLICY fields; nothing guarded the decision POPULATION, so a
    reader could take a per-decision figure from the value arm and compare it with one from the
    level arm without anything in the file saying the books differ.
    """
    block = decision_population({
        "value_arm": _funnel(25, "value_arm"), "level_arm": _funnel(34, "level_arm")})
    assert block["available"] is True
    assert block["priced_by_arm"] == {"value_arm": 25, "level_arm": 34}
    assert block["largest_denominator_difference"] == 9
    assert block["difference_as_share_of_the_smaller"] == 0.36
    assert "roster divergence" in block["the_mechanism"].lower()


def test_one_arm_alone_cannot_produce_a_denominator_comparison():
    """R15 FAIL-OPEN. MUTATION: return a comparison with a spread of 0 for a single arm.

    A "difference of 0" published by a run that executed one arm reads exactly like two arms
    that agreed, and the second is a real and different result.
    """
    block = decision_population({"value_arm": _funnel(25, "value_arm")})
    assert block["available"] is False
    assert "largest_denominator_difference" not in block


def test_an_unavailable_funnel_does_not_count_as_an_arm():
    """FAIL-OPEN on the seam between the two blocks: an arm whose run predates the log has no
    denominator, and pairing it with one that does would publish a difference against nothing.
    """
    block = decision_population({
        "value_arm": _funnel(25, "value_arm"),
        "level_arm": renewal_funnel({"phase2b": {}}, "level_arm")})
    assert block["available"] is False


@pytest.mark.parametrize("priced", [25, 34])
def test_the_comparison_is_symmetric_in_which_arm_is_larger(priced):
    """NULL RUNG for the difference: whichever arm is larger, the spread is the same number.
    A comparison that only fires when a particular arm wins is measuring the arm, not the gap.
    """
    other = 34 if priced == 25 else 25
    block = decision_population({
        "value_arm": _funnel(priced, "value_arm"), "level_arm": _funnel(other, "level_arm")})
    assert block["largest_denominator_difference"] == 9


# ---------------------------------------------------------------------------
# WHOSE renewals these are — founder, won, or drawn
#
# THE DEFECT (2026-08-30). The funnel could say where 1,349 unpriced renewals went and could not
# say whose they were. The arm priced 20 renewals across 10 accounts, every one of them a
# hand-authored founder account, while the 90 accounts the acquisition funnel has won and the 69
# the curriculum drew had never had a single renewal reach the arm — and no stage total can show
# that, because `product_not_upliftable = 662` is true of the book as a whole. The enterprise
# value claim is that the advantage comes from inference over the customers the method FINDS, so
# a run that priced only the founding customers has not tested it at all.
# ---------------------------------------------------------------------------

def test_a_class_that_priced_nothing_is_reported_rather_than_missing():
    """MUTATION: build the buckets from `priced_accounts_by_class` instead of from every row.

    A class whose accounts all stopped at a guard would then be ABSENT from the block, and a
    missing class reads exactly like a class the world does not have. That is the fail-silent
    shape one layer up: "no won account was priced" and "there are no won accounts" are the same
    absence and opposite facts, and the second is the flattering one.
    """
    block = funnel_by_account_class([
        _row(customer_id="C1", stage="priced"),
        _row(customer_id=a_won_account_id(), stage="product_not_upliftable", tariff_type=None),
    ])
    assert block["classes"]["won_by_the_funnel"]["renewals_the_world_offered"] == 1
    assert block["classes"]["won_by_the_funnel"]["priced"] == 0
    assert block["priced_accounts_by_class"]["won_by_the_funnel"] == []
    assert block["accounts_the_company_won_or_drew_that_the_arm_priced"] == 0


def test_an_account_no_roster_claims_is_named_not_folded_into_the_founders():
    """MUTATION: default the class map lookup to `FOUNDER_ACCOUNT_CLASS`.

    "The roster does not know this account" and "the company was founded with it" are the same
    absence. Folding the first into the second would let a renamed or newly minted id be counted
    as evidence that the FOUNDING book is what the arm reaches — the exact claim this block
    exists to test — and nothing would say so.
    """
    block = funnel_by_account_class([_row(customer_id="GHOST-1", stage="priced")])
    assert "unclassified_no_roster_row" in block["classes"]
    assert block["classes"].get("founder_hand_authored") is None
    assert block["priced_accounts_by_class"]["unclassified_no_roster_row"] == ["GHOST-1"]


def test_the_won_book_counter_moves_when_a_won_account_is_priced():
    """NULL RUNG, and the one that makes the count a measurement rather than a constant.

    `accounts_the_company_won_or_drew_that_the_arm_priced` is 0 on every run to date. A counter
    that has only ever been observed at zero is indistinguishable from a counter that cannot
    leave zero — R15's unreachable-branch shape — so this rung prices a won account and asserts
    the count follows it.
    """
    won_id = a_won_account_id()
    priced_a_won_one = funnel_by_account_class([
        _row(customer_id=won_id, stage="priced")])
    assert priced_a_won_one["accounts_the_company_won_or_drew_that_the_arm_priced"] == 1
    assert priced_a_won_one["priced_accounts_by_class"]["won_by_the_funnel"] == [won_id]


def test_the_class_of_an_account_comes_from_the_world_not_from_its_id():
    """MUTATION: classify on `customer_id.startswith("PROS-")` instead of `acquisition_type`.

    A prefix test is a control pinned to today's naming: rename the funnel's ids and every won
    account reads as a founder account, which is the flattering direction, and the block would
    not say it had changed its mind. `acquisition_type` is the field the roster that MINTED the
    account writes, so the two populations here must be exactly the roster's own.
    """
    mapping = account_class_map()
    classes = {c for c in mapping.values()}
    assert "won_by_the_funnel" in classes and "founder_hand_authored" in classes
    # The successor of a hand-authored account was not won by anything, and its id carries no
    # marker either way — so it is the case that separates the two rules.
    assert mapping["C1_2"] == "founder_hand_authored"
    assert not any(k.startswith("legs_disagree_") for k in classes), sorted(classes)


# ---------------------------------------------------------------------------
# WHY, and it is the roster rather than the run
#
# THE DEFECT (2026-08-30). `by_account_class` above can say that no account the company found was
# priced in THIS run. It cannot say whether that is a fact about this run's size or about the
# world's record shapes, and the two license opposite decisions -- grow the book, versus fix the
# world. The live arms page already states the second ("a GATE, not a book size") and until this
# block its premise -- that the world renders `tariff_type = None` for every account it won or
# drew -- was ASSERTED in a hardcoded sentence and measured by nothing.
# ---------------------------------------------------------------------------

def _roster(*records):
    """A roster in the world's own shape. `tariff_type` is passed only where a caller sets it,
    because the whole subject here is the difference between a key that is ABSENT and one that is
    PRESENT AND `None` -- rendering it unconditionally in the fixture would erase the defect."""
    out = []
    for record in records:
        row = {"customer_id": record["customer_id"], "commodity": record["commodity"]}
        if "acquisition_type" in record:
            row["acquisition_type"] = record["acquisition_type"]
        if "tariff_type" in record:
            row["tariff_type"] = record["tariff_type"]
        out.append(row)
    return out


@pytest.fixture()
def roster(monkeypatch):
    """Bind a roster in place of the world's, for both readers of it."""
    import simulation.run_phase2b as p2b

    def _bind(records):
        monkeypatch.setattr(p2b, "CUSTOMERS", _roster(*records))
        monkeypatch.setattr(p2b, "SUCCESSOR_CUSTOMERS", [])
        return product_label_by_account_class()
    return _bind


def test_the_census_counts_what_the_guard_reads_not_whether_the_key_is_there():
    """MUTATION: census on `"tariff_type" in record` instead of `record.get(..., "fixed")`.

    The two are DIFFERENT CENSUSES and only the second is what the arm sees. A won electricity
    record carries the key PRESENT with value `None`, so `run_phase2b`'s `"fixed"` fallback never
    fires; a census keyed on key-presence would report those legs as labelled and the structural
    verdict below would invert. Both fields are published for exactly that reason, and this pins
    them apart on the live roster.
    """
    census = product_label_by_account_class()
    won_elec = [r for r in census["legs"]
                if r["account_class"] == "won_by_the_funnel"
                and r["commodity"] == "electricity"]
    assert won_elec, "the roster has no won electricity leg, so this control has no subject"
    for row in won_elec:
        assert row["tariff_type_key_present"] is True
        assert row["resolved_tariff_type"] is None
        assert row["the_guard_admits_it"] is False


def test_MUTATION_a_labelled_won_record_makes_the_gate_reachable(roster):
    """NULL RUNG on the verdict the live page's sentence turns on.

    `a_found_account_can_reach_the_product_gate` is False on every roster to date. A boolean only
    ever observed False cannot be told from one that is structurally unable to leave False --
    R15's unreachable-PASS-branch shape -- and this is the field that decides whether the page
    says "a GATE" or "book size". So: label one won electricity record and the verdict must
    follow it and NAME the account.
    """
    unlabelled = roster([
        {"customer_id": "PROS-2019-0015", "commodity": "electricity",
         "acquisition_type": "net_new_won", "tariff_type": None}])
    assert unlabelled["a_found_account_can_reach_the_product_gate"] is False
    assert unlabelled["found_accounts_the_guard_would_admit"] == []

    labelled = roster([
        {"customer_id": "PROS-2019-0015", "commodity": "electricity",
         "acquisition_type": "net_new_won", "tariff_type": "fixed"}])
    assert labelled["a_found_account_can_reach_the_product_gate"] is True
    assert labelled["found_accounts_the_guard_would_admit"] == ["PROS-2019-0015"]


def test_a_founder_account_passing_the_gate_is_not_a_found_account_reaching_it(roster):
    """MUTATION: drop the `name in _FOUND_ACCOUNT_CLASSES` clause from the reachability test.

    Every founder electricity leg resolves to `"fixed"` and IS admitted by the guard, so a
    reachability check that did not filter by class would report True on today's roster and the
    page would say the gate is passable while no found household has ever passed it. The
    flattering answer, produced by deleting one condition.
    """
    census = roster([
        {"customer_id": "C1", "commodity": "electricity"},
        {"customer_id": "PROS-2019-0015", "commodity": "electricity",
         "acquisition_type": "net_new_won", "tariff_type": None}])
    founder = [r for r in census["legs"] if r["account_class"] == "founder_hand_authored"]
    assert [r["the_guard_admits_it"] for r in founder] == [True]
    assert census["a_found_account_can_reach_the_product_gate"] is False


def test_a_gas_leg_that_omits_the_key_is_named_as_disagreeing_with_its_own_electricity_leg(
        roster):
    """MUTATION: report labelling per LEG only and drop `..._legs_disagree_about_labelling`.

    A won account's two legs are minted by two paths and answer the question differently: the
    electricity leg carries the key present and `None`, the gas leg omits it and takes the
    `"fixed"` default. That is invisible in a per-leg table -- both rows are individually
    truthful -- and it is latent rather than harmless: the gas leg would be priced as a product
    the world never decided for it the moment the commodity guard stops refusing gas one step
    earlier. 86 accounts on the live roster.
    """
    agreeing = roster([
        {"customer_id": "SYN-2016-003", "commodity": "electricity",
         "acquisition_type": "synthetic_draw", "tariff_type": None},
        {"customer_id": "SYN-2016-003g", "commodity": "gas",
         "acquisition_type": "synthetic_draw", "tariff_type": None}])
    assert agreeing["billing_accounts_whose_legs_disagree_about_labelling"] == []

    disagreeing = roster([
        {"customer_id": "PROS-2016-0072", "commodity": "electricity",
         "acquisition_type": "net_new_won", "tariff_type": None},
        {"customer_id": "PROS-2016-0072g", "commodity": "gas",
         "acquisition_type": "net_new_won"}])
    assert disagreeing["billing_accounts_whose_legs_disagree_about_labelling"] == [
        "PROS-2016-0072"]
