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
    decision_population,
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
