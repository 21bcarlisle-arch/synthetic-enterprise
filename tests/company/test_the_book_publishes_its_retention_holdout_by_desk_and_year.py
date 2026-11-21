"""B8: every book carries `retention_holdout_by_desk_year`, and the coins behind it are blind.

The defect each test names: the 2026-10-21 blind pass found that the book carried no holdout key, so
"nothing measures the uplift" could not be read off the artefact at all. These red when the key
leaves the run's output, when a desk is dropped, when the per-year rows stop carrying their arms or
interval, or when a coin starts reading anything but the account and the day.
"""

from __future__ import annotations

import inspect

from company.crm.competitive_pressure import save_holdout_draws
from company.interfaces.growth_desk import RETENTION_DESKS, retention_holdout_by_desk
from company.pricing.discovered_price_sensitivity import (
    HOLDOUT_ROW_KEYS,
    RetentionHoldout,
    holdout_arm,
)


def _outcomes():
    holdout = RetentionHoldout()
    for i in range(40):
        account, day = f"acct-{i}", f"{2021 + i % 2}-04-01"
        holdout.record(account_id=account, event_date=day, arm=holdout_arm(account, day),
                       stayed=i % 3 != 0, payment_method="direct_debit")
    return holdout.outcomes(())


def test_the_run_output_carries_the_key_and_builds_it_from_the_desk_door():
    """Defect: the key leaves `run_phase2b`'s result, and the book goes back to silence."""
    from simulation import run_phase2b

    source = inspect.getsource(run_phase2b)
    assert source.count('"retention_holdout_by_desk_year": retention_holdout_by_desk(') == 1, (
        "the run's output no longer publishes retention_holdout_by_desk_year")


def test_both_sides_of_the_partition_are_reachable_and_every_desk_is_published():
    """Defect: a desk drops out, or one branch (assigned / not) can no longer be produced."""
    off = retention_holdout_by_desk(renewal_offer_holdout=False, save_rate_holdout_on=False)
    on = retention_holdout_by_desk(
        renewal_offer_holdout=True, renewal_offer_outcomes=_outcomes(), save_rate_holdout_on=True,
        save_offer_sums=({("fixed", 2022): {"n": 30, "sp": 3.0, "losses": 3}},
                         {("fixed", 2022): {"n": 10, "sp": 1.0, "losses": 2}}))
    assert set(off) == set(on) == set(RETENTION_DESKS)
    assert all(on[d]["assigned"] for d in RETENTION_DESKS)
    assert not any(off[d]["assigned"] for d in RETENTION_DESKS)
    assert all(off[d]["reason"] for d in RETENTION_DESKS)
    assert on["save_offer"]["by_year"]["2022"]["retained_held_out"] == 8


def test_the_assigned_table_carries_both_arms_retained_counts_and_the_interval_per_year():
    """Defect: the rows lose an arm, a count, or the interval, or stop summing to the outcomes."""
    outcomes = _outcomes()
    table = retention_holdout_by_desk(renewal_offer_holdout=True, renewal_offer_outcomes=outcomes,
                                      save_rate_holdout_on=False)["renewal_offer"]["by_year"]
    assert set(table) == {"2021", "2022"}
    for row in table.values():
        assert set(HOLDOUT_ROW_KEYS) <= set(row)
    assert sum(r["treated"] + r["held_out"] for r in table.values()) == len(outcomes)
    assert all(r["treated"] and r["held_out"] for r in table.values()), (
        "the fixture must exercise both arms")
    assert all(r["interval"] is not None for r in table.values())
    assert sum(r["retained_treated"] + r["retained_held_out"] for r in table.values()) == sum(
        o["stayed_at_decision"] for o in outcomes)


def test_an_empty_arm_publishes_no_interval_and_says_why():
    """Defect: a year with one arm only prints a difference against nothing."""
    rows = [{"event_date": "2023-01-01", "arm": "treated", "stayed_at_decision": True}]
    row = RetentionHoldout.holdout_rows_by_year(rows)["2023"]
    assert row["interval"] is None and "holdout arm holds no decision" in row["reason"]


def test_both_coins_read_only_the_account_and_the_day():
    """Defect: a coin starts reading something the world drew, and the arms stop being twins."""
    assert list(inspect.signature(holdout_arm).parameters) == ["account_id", "event_date"]
    assert list(inspect.signature(save_holdout_draws).parameters)[:2] == ["account_id", "event_date"]
