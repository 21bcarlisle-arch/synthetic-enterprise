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

ARCHETYPES = ("OVERWHELMED", "NEUTRAL", "AVOIDANT")


def _register_with(tmp_path, monkeypatch, **defaults):
    doc = yaml.safe_load(ae.ASSUMPTION_TOGGLES_PATH.read_text())
    for row in doc["toggles"]:
        if row["id"] in defaults:
            row["default"] = defaults[row["id"]]
    path = tmp_path / "assumption_toggles.yaml"
    path.write_text(yaml.safe_dump(doc))
    monkeypatch.setattr(ae, "ASSUMPTION_TOGGLES_PATH", path)


def _terminal(archetype):
    return ae._post_writeoff_stages(1000.0, date(2022, 3, 1), archetype)[-1]


def test_the_world_recovers_what_the_register_says_for_every_archetype():
    coverage = yaml.safe_load(ae.ASSUMPTION_TOGGLES_PATH.read_text())["toggles"]
    coverage = next(r for r in coverage if r["id"] == "prov_coverage_final_bill_over_90d")
    expected = round(1000.0 * (1 - coverage["default"]), 2)
    assert {a: _terminal(a)["amount_gbp"] for a in ARCHETYPES} == dict.fromkeys(ARCHETYPES, expected)


def test_moving_the_register_moves_the_world(tmp_path, monkeypatch):
    _register_with(tmp_path, monkeypatch, prov_coverage_final_bill_over_90d=0.6)
    assert [_terminal(a)["amount_gbp"] for a in ARCHETYPES] == [400.0] * 3
    assert ae.dca_recovered_amount(1000.0, "OVERWHELMED") == 400.0


def test_without_a_sale_price_nothing_is_sold_and_the_reason_is_carried():
    price, reason = ae.debt_sale_price_share()
    assert price is None and reason.startswith("GAP.")
    assert ae.debt_sale_proceeds(1000.0) is None
    assert _terminal("AVOIDANT")["stage"] == "RECOVERED"


def test_the_sale_branch_can_be_taken_once_the_register_prices_it(tmp_path, monkeypatch):
    _register_with(tmp_path, monkeypatch, q3_debt_sale_price_share_of_face=0.07)
    sold, worked = _terminal("AVOIDANT"), _terminal("NEUTRAL")
    assert sold["stage"] == "SOLD" and sold["amount_gbp"] == 70.0
    assert worked["stage"] == "RECOVERED"


def test_a_write_off_convention_with_no_register_row_is_refused():
    with pytest.raises(ValueError, match="no register row"):
        ae.post_write_off_recovery_share("default_at_twelve_months")
