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


def _terminal():
    return ae._post_writeoff_stages(1000.0, date(2022, 3, 1))[-1]


def test_the_world_recovers_what_the_register_says():
    coverage = yaml.safe_load(ae.ASSUMPTION_TOGGLES_PATH.read_text())["toggles"]
    coverage = next(r for r in coverage if r["id"] == "prov_coverage_final_bill_over_90d")
    assert _terminal()["amount_gbp"] == round(1000.0 * (1 - coverage["default"]), 2)


def test_moving_the_register_moves_the_world(tmp_path, monkeypatch):
    _register_with(tmp_path, monkeypatch, prov_coverage_final_bill_over_90d=0.6)
    assert _terminal()["amount_gbp"] == 400.0
    assert ae.dca_recovered_amount(1000.0, "OVERWHELMED") == 400.0


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
    assert ae.post_write_off_recovery_gbp(1000.0) == 150.0


def test_a_write_off_convention_with_no_register_row_is_refused():
    with pytest.raises(ValueError, match="no register row"):
        ae.post_write_off_recovery_share("default_at_twelve_months")
