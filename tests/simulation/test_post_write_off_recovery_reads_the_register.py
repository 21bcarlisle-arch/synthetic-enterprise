"""The world's post-write-off recovery is read from the assumption register, never typed.

Defect this exists to catch: the typed 25.5p / 17.0p / 12.0p per GBP returning to
`simulation/arrears_engine.py`, or any rate the register does not hold. Each control moves the
REGISTER and asks the world to move with it, so a typed constant cannot satisfy it whatever value
it happens to have.
"""
from __future__ import annotations

from datetime import date

import pytest
import yaml

from simulation import arrears_engine as ae


def _register_with(tmp_path, monkeypatch, **defaults):
    doc = yaml.safe_load(ae.ASSUMPTION_TOGGLES_PATH.read_text())
    for row in doc["toggles"]:
        if row["id"] in defaults:
            row["default"] = defaults[row["id"]]
    path = tmp_path / "assumption_toggles.yaml"
    path.write_text(yaml.safe_dump(doc))
    monkeypatch.setattr(ae, "ASSUMPTION_TOGGLES_PATH", path)


def _terminal(age_at_close_days=0):
    return ae._post_writeoff_stages(1000.0, date(2022, 3, 1),
                                    age_at_close_days=age_at_close_days)[-1]


def test_the_world_recovers_what_the_register_says():
    coverage = yaml.safe_load(ae.ASSUMPTION_TOGGLES_PATH.read_text())["toggles"]
    coverage = next(r for r in coverage if r["id"] == "prov_coverage_final_bill_over_90d")
    assert _terminal()["amount_gbp"] == round(1000.0 * (1 - coverage["default"]), 2)


def test_moving_the_register_moves_the_world(tmp_path, monkeypatch):
    _register_with(tmp_path, monkeypatch, prov_coverage_final_bill_over_90d=0.6)
    assert _terminal()["amount_gbp"] == 400.0
    assert ae.dca_recovered_amount(1000.0, 0) == 400.0


def test_without_a_sale_price_nothing_is_sold_and_the_reason_is_carried():
    price, reason = ae.debt_sale_price_share()
    assert price is None and reason.startswith("GAP.")
    assert ae.debt_sale_proceeds(1000.0) is None
    assert _terminal()["stage"] == "RECOVERED"


def test_at_a_published_purchase_price_the_supplier_works_the_debt(tmp_path, monkeypatch):
    # 0.07 is inside the register's all-sector range (0.054-0.093) and below the supplier's own
    # expected recovery (0.122), so it does not sell.
    _register_with(tmp_path, monkeypatch, q3_debt_sale_price_share_of_face=0.07)
    assert _terminal()["stage"] == "RECOVERED"


def test_the_sale_branch_is_taken_when_the_price_beats_the_suppliers_recovery(tmp_path, monkeypatch):
    # Catches: a sale branch nothing can reach. The choice is the supplier's (asked through the
    # door), and it is the same for every debt: no household label is in the question.
    _register_with(tmp_path, monkeypatch, q3_debt_sale_price_share_of_face=0.15)
    sold = _terminal()
    assert sold["stage"] == "SOLD" and sold["amount_gbp"] == 150.0
    assert ae.post_write_off_recovery_gbp(1000.0, age_at_close_days=0) == 150.0


def test_a_write_off_convention_with_no_register_row_is_refused():
    with pytest.raises(ValueError, match="no register row"):
        ae.post_write_off_recovery_share("default_at_twelve_months")


# 2026-11-20: recovery after write-off varies with the bill's age at close, a thing the supplier
# reads off its own ledger (debt_and_collections.md s.7.7). Before, every debt recovered one share,
# the same row the company's prior reads, so no per-debt rule had anything to find.


def test_both_age_cells_are_reached_and_the_aged_one_recovers_less():
    # Catches: a cut nothing reaches (the aged branch dead, or every debt in it), and a world flat
    # again. Both sides of the partition, keyed to the register, not to today's value.
    ratio, _basis = ae.post_write_off_aged_ratio()
    young = _terminal(ae.AGED_AT_CLOSE_DAYS)["amount_gbp"]
    aged = _terminal(ae.AGED_AT_CLOSE_DAYS + 1)["amount_gbp"]
    assert young == round(1000.0 * ae.post_write_off_recovery_share()[0], 2)
    assert aged == round(young * ratio, 2) and 0 < aged < young


def test_moving_the_aged_ratio_moves_only_the_aged_cell(tmp_path, monkeypatch):
    # Catches: a typed ratio beside the register row, or the ratio leaking onto younger debt.
    before_young = _terminal(0)["amount_gbp"]
    _register_with(tmp_path, monkeypatch, post_write_off_recovery_aged_over_young=0.25)
    assert _terminal(400)["amount_gbp"] == round(1000.0 * ae.post_write_off_recovery_share()[0] * 0.25, 2)
    assert _terminal(0)["amount_gbp"] == before_young


def test_the_age_is_read_off_the_walks_record_from_due_date_to_final_bill():
    # Catches: the age measured to the write-off (a year later, so every debt aged) or from a
    # household attribute. A statute-barred write-off has no close and reads 0.
    rec = {"due_date": date(2020, 1, 10), "final_bill_on": date(2021, 3, 1), "leg": "close"}
    assert ae.age_at_close_days(rec) == (date(2021, 3, 1) - date(2020, 1, 10)).days
    assert ae.age_at_close_days({**rec, "due_date": "2021-02-01"}) == 28
    assert ae.age_at_close_days({**rec, "final_bill_on": None, "leg": "statute_bar"}) == 0
