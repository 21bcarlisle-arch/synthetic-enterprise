"""R15 proof for the class `figures_on_a_superseded_clock` (2026-08-28).

The class: a figure re-summed from mutated rows, published beside a sibling read off a summary
scalar frozen before the mutation. Two instances in two days — the value-cycle A/B artefact and
`docs/reports/run_output_latest.json` on the live site — both GBP 39,962.17 out.

WHAT THIS FILE HAS TO PROVE, and the order matters:

1. The controls FIRE on the defect (`test_..._reds_...`). A control that has never been shown
   to fail is not evidence (R15).
2. They fire on the defect ANYWHERE IN THE FAMILY, not only on the two figures that were
   caught — `scalar_row_disagreements` is parametrised over every scalar in
   `ROW_DERIVED_SCALARS`, so a stage added next month that mutates `margin_gbp` reds without
   anyone editing the control. AND that the family cannot silently shrink: the parametrisation
   draws its cases from the registry the control iterates, so the membership is pinned
   literally as well (`test_the_class_boundary_cannot_shrink_...`) — without that, deleting a
   scalar removes it from both sides at once and the suite stays green.
3. They PASS on the repaired shape (the null rung). Without this, a control whose PASS branch
   is unreachable reports a constant verdict and every mutation "reds" because it was always
   red.
4. They fail CLOSED on the three killers — missing, empty, non-finite.
5. The REPAIR is wired: running the real mutation stage and then the refresh leaves the scalars
   reconciled, and REMOVING the refresh reds. That is the mutation that matters, because it is
   the one that reintroduces the shape.
"""

from __future__ import annotations

import math

import pytest

from simulation.arrears_engine import apply_debt_recovery, apply_emergent_bad_debt
from simulation.settlement_clocks import (
    CLOCK_DEFINITIONS,
    CLOCK_TOLERANCE_GBP,
    PROVISIONED_PREFIX,
    ROW_DERIVED_SCALARS,
    SETTLED_PROVISIONED,
    SETTLED_REALISED,
    derive_from_rows,
    reconcile_published_run_output,
    refresh_settlement_scalars,
    scalar_row_disagreements,
)

STARTING = 250_000.0


def _rows() -> list[dict]:
    """A three-row settled book whose treasury is the running total of net margin, which is
    what this world's `treasury_cash_balance_gbp` actually is."""
    rows = []
    running = STARTING
    for i, (gross, capital, bad_debt) in enumerate(
        [(1_000.0, 100.0, 50.0), (2_000.0, 200.0, 80.0), (3_000.0, 300.0, 120.0)]
    ):
        net = gross - capital - bad_debt
        running += net
        rows.append(
            {
                "customer_id": f"C{i}",
                "settlement_date": f"2020-01-0{i + 1}",
                "margin_gbp": gross,
                "capital_cost_gbp": capital,
                "bad_debt_gbp": bad_debt,
                "net_margin_gbp": net,
                "treasury_cash_balance_gbp": round(running, 2),
                "billing_account": f"BA{i}",
                "customer_year": 2020,
            }
        )
    return rows


def _frozen(rows: list[dict]) -> dict:
    """The run dict as `run_phase2b` returns it: scalars folded from the rows, in agreement
    with them — the state BEFORE any later stage mutates the book."""
    phase2b = {"all_records": rows, "starting_treasury": STARTING}
    phase2b.update(derive_from_rows(rows))
    return phase2b


# --------------------------------------------------------------------------------------
# 3. THE NULL RUNG FIRST. If these do not pass, every "mutation reds it" below is worthless.
# --------------------------------------------------------------------------------------


def test_null_rung_a_run_whose_scalars_match_its_rows_passes():
    assert scalar_row_disagreements(_frozen(_rows())) == []


def test_null_rung_a_published_output_that_adds_up_passes():
    rows = _rows()
    assert (
        reconcile_published_run_output(
            {
                "starting_treasury_gbp": STARTING,
                "total_net_gbp": sum(r["net_margin_gbp"] for r in rows),
                "final_treasury_gbp": rows[-1]["treasury_cash_balance_gbp"],
            }
        )
        == []
    )


# --------------------------------------------------------------------------------------
# 1 + 2. THE MUTATIONS. Every member of the family, not the two figures that were caught.
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("scalar", sorted(ROW_DERIVED_SCALARS))
def test_a_scalar_left_on_the_superseded_clock_reds(scalar):
    """THE CLASS MUTATION, applied to each scalar in turn: freeze the summary, then move the
    book underneath it. This is what `run_phase4c_on_phase2b` did to `all_records` for the
    whole of this defect's life."""
    phase2b = _frozen(_rows())
    phase2b[scalar] = phase2b[scalar] + 39_962.17

    failures = scalar_row_disagreements(phase2b)

    assert failures, f"a superseded `{scalar}` was not detected"
    assert any(scalar in f and "SUPERSEDED" in f for f in failures)


def test_the_real_mutation_stage_reds_when_the_refresh_is_not_run():
    """The instance, reproduced with the real arrears code rather than a hand-nudged number.

    `apply_emergent_bad_debt` replaces the flat-rate provision with realised write-offs and
    carries the delta through every later `treasury_cash_balance_gbp`. Without the refresh, the
    frozen scalars are exactly the defect that reached the site.
    """
    rows = _rows()
    phase2b = _frozen(rows)
    assert scalar_row_disagreements(phase2b) == []  # reconciled before the stage runs

    # The arrears model finds this customer-year's realised write-off to be far below the
    # flat-rate provision -- the direction the live run took, and the direction that made the
    # published treasury LOWER than starting + net.
    apply_emergent_bad_debt(rows, {("C0", 2020): 5.0})

    failures = scalar_row_disagreements(phase2b)
    assert failures, "the real mutation stage did not red the frozen scalars"
    assert any("total_bad_debt" in f for f in failures)
    assert any("total_net" in f for f in failures)
    assert any("final_treasury" in f for f in failures)


def test_the_refresh_repairs_what_the_real_mutation_stage_broke():
    """The repair, wired: run the stage, then the refresh, and the run reconciles again."""
    rows = _rows()
    phase2b = _frozen(rows)
    provisioned_bad_debt = phase2b["total_bad_debt"]
    provisioned_net = phase2b["total_net"]

    apply_emergent_bad_debt(rows, {("C0", 2020): 5.0})
    apply_debt_recovery(rows, {("C1", 2020): 10.0})
    audit = refresh_settlement_scalars(phase2b)

    assert scalar_row_disagreements(phase2b) == []
    # THE SUPERSEDED READ SURVIVES UNDER ITS OWN NAME. Dropping it would have been the other
    # available wrong answer: the provision is what the company believed and is worth keeping,
    # it just may not wear the unprefixed name.
    assert phase2b[f"{PROVISIONED_PREFIX}total_bad_debt"] == provisioned_bad_debt
    assert phase2b[f"{PROVISIONED_PREFIX}total_net"] == provisioned_net
    assert phase2b["total_bad_debt"] != provisioned_bad_debt
    assert audit["total_net"]["delta"] == pytest.approx(
        phase2b["total_net"] - provisioned_net
    )


def test_the_refresh_is_idempotent_on_the_provisioned_side():
    """A second call must not overwrite the provisioned figures with the realised ones the
    first call wrote — which would erase the provision and leave two names for one clock."""
    rows = _rows()
    phase2b = _frozen(rows)
    apply_emergent_bad_debt(rows, {("C0", 2020): 5.0})

    refresh_settlement_scalars(phase2b)
    first = {k: phase2b[k] for k in phase2b if k.startswith(PROVISIONED_PREFIX)}
    refresh_settlement_scalars(phase2b)

    assert {k: phase2b[k] for k in phase2b if k.startswith(PROVISIONED_PREFIX)} == first


def test_the_published_identity_reds_on_the_treasury_read_off_the_frozen_scalar():
    """THE INSTANCE THAT REACHED THE SITE, to the penny.

    `run_output_latest.json` on 2026-08-28: net margin summed from the mutated rows, treasury
    read off the pre-mutation scalar. A reader with a calculator can see it; until this control
    existed nothing in the repo could.
    """
    failures = reconcile_published_run_output(
        {
            "starting_treasury_gbp": 250_000.0,
            "total_net_gbp": 153_244.792035,
            "final_treasury_gbp": 363_282.6171350135,
        }
    )
    assert failures
    assert "39,962.17" in failures[0]


def test_the_published_identity_reds_wherever_the_stale_figure_is_put():
    """The mutation the direction asked for, in all three positions: put ONE figure back onto
    a clock the other two are not on. The control must not care which one moved — it checks an
    identity, not a named field."""
    good = {
        "starting_treasury_gbp": 250_000.0,
        "total_net_gbp": 153_244.792035,
        "final_treasury_gbp": 403_244.792035,
    }
    assert reconcile_published_run_output(good) == []
    for key in good:
        broken = dict(good)
        broken[key] = broken[key] - 39_962.17
        assert reconcile_published_run_output(broken), f"moving `{key}` was not detected"


# --------------------------------------------------------------------------------------
# 4. FAIL-CLOSED. The three R15 killers, each refused explicitly.
# --------------------------------------------------------------------------------------


def test_missing_rows_is_a_failure_not_a_pass():
    assert scalar_row_disagreements({"total_net": 1.0}) != []
    assert scalar_row_disagreements({"all_records": [], "total_net": 1.0}) != []


def test_a_scalar_absent_from_the_run_dict_is_a_failure_not_a_pass():
    phase2b = _frozen(_rows())
    del phase2b["final_treasury"]
    failures = scalar_row_disagreements(phase2b)
    assert any("final_treasury" in f and "absent" in f for f in failures)


def test_a_nan_scalar_is_a_failure_not_a_pass():
    """`abs(nan - x) > tol` is FALSE, so a tolerance test alone passes a NaN silently."""
    phase2b = _frozen(_rows())
    phase2b["total_net"] = math.nan
    assert not (abs(math.nan - 1.0) > 0.05)  # the trap, stated
    assert any("NaN" in f for f in scalar_row_disagreements(phase2b))


@pytest.mark.parametrize(
    "payload",
    [
        {"total_net_gbp": 1.0, "final_treasury_gbp": 2.0},
        {"starting_treasury_gbp": 1.0, "final_treasury_gbp": 2.0},
        {"starting_treasury_gbp": 1.0, "total_net_gbp": 1.0},
        {"starting_treasury_gbp": 1.0, "total_net_gbp": 1.0, "final_treasury_gbp": None},
        {"starting_treasury_gbp": 1.0, "total_net_gbp": 1.0, "final_treasury_gbp": math.nan},
        {"starting_treasury_gbp": 1.0, "total_net_gbp": 1.0, "final_treasury_gbp": True},
        {},
    ],
)
def test_the_published_identity_fails_closed_on_an_unusable_figure(payload):
    assert reconcile_published_run_output(payload) != []


def test_deriving_from_an_empty_book_raises_rather_than_returning_zeros():
    with pytest.raises(ValueError):
        derive_from_rows([])


# --------------------------------------------------------------------------------------
# The clock vocabulary itself. Two clocks, and the third one stays uninvented.
# --------------------------------------------------------------------------------------


def test_there_are_exactly_two_clocks_and_banked_is_not_one_of_them():
    """`treasury_cash_balance_gbp` is a running total of settled net margin, so
    `final - starting` reproduces settled net exactly and measures nothing about when cash
    arrived. A `banked` label would be a name for a clock this world does not have — the more
    comfortable of the two available wrong answers, and the one the finding warned about."""
    assert set(CLOCK_DEFINITIONS) == {SETTLED_REALISED, SETTLED_PROVISIONED}
    assert not any("bank" in name for name in CLOCK_DEFINITIONS)

    rows = _rows()
    assert rows[-1]["treasury_cash_balance_gbp"] - STARTING == pytest.approx(
        sum(r["net_margin_gbp"] for r in rows), abs=0.01
    )


#: The class boundary, written out. Each scalar beside the ONE row field it folds — derived
#: here by perturbing that field and watching which scalar moves, never by reading the fold
#: back out of `ROW_DERIVED_SCALARS`, which would make this test agree with the registry by
#: construction (R15 tautology) and prove nothing.
CLASS_BOUNDARY: dict[str, str] = {
    "total_gross": "margin_gbp",
    "total_capital": "capital_cost_gbp",
    "total_bad_debt": "bad_debt_gbp",
    "total_net": "net_margin_gbp",
    "final_treasury": "treasury_cash_balance_gbp",
}


def test_the_class_boundary_cannot_shrink_without_this_test_reddening():
    """THE MUTATION THAT SURVIVED, and the reason this test exists (2026-08-28, second pass).

    Every other mutation test in this file parametrises over `sorted(ROW_DERIVED_SCALARS)`, so
    it draws its case list from the very registry the control iterates. Deleting `total_gross`
    from that registry therefore removed it from BOTH sides at once: the suite dropped from 25
    tests to 24 and stayed entirely green while the class quietly stopped covering gross
    margin. A control whose scope is defined by the thing it checks cannot notice its own scope
    shrinking, and `realised_scalars == set(ROW_DERIVED_SCALARS)` above has the same shape.

    So the membership is pinned LITERALLY here, exactly as the two clocks are pinned in
    `test_there_are_exactly_two_clocks_...`. Adding a scalar is then a deliberate edit to this
    dict — which is the ratchet working, not friction — and removing one reds.
    """
    assert set(ROW_DERIVED_SCALARS) == set(CLASS_BOUNDARY)


@pytest.mark.parametrize("scalar,field", sorted(CLASS_BOUNDARY.items()))
def test_each_scalar_folds_the_row_field_it_claims_to(scalar, field):
    """Pinning the NAMES alone would still let a fold be re-pointed at another column — the
    registry would keep its five entries while `total_gross` quietly summed capital. Perturb
    one field across the book and exactly one scalar may move: its own."""
    rows = _rows()
    baseline = derive_from_rows(rows)

    for row in rows:
        row[field] += 100.0
    moved = {
        name
        for name, value in derive_from_rows(rows).items()
        if abs(value - baseline[name]) > CLOCK_TOLERANCE_GBP
    }

    assert moved == {scalar}, f"perturbing `{field}` moved {sorted(moved)}, not just `{scalar}`"


def test_the_refresh_records_both_clocks_on_the_run_dict():
    phase2b = _frozen(_rows())
    refresh_settlement_scalars(phase2b)
    clocks = phase2b["settlement_clocks"]
    assert set(clocks["definitions"]) == {SETTLED_REALISED, SETTLED_PROVISIONED}
    assert set(clocks["realised_scalars"]) == set(ROW_DERIVED_SCALARS)
    assert all(n.startswith(PROVISIONED_PREFIX) for n in clocks["provisioned_scalars"])
