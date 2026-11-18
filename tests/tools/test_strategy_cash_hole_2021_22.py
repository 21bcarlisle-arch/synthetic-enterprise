"""Controls on the 2021-22 strategy cash-hole composer (`tools/strategy_cash_hole_2021_22.py`).

Each names the defect it catches. Keyed to properties of the instrument, not to today's holes.
"""

import pytest

from tools.strategy_cash_hole_2021_22 import (
    _MID,
    STRATEGIES,
    credit_balance_path,
    hole,
    monthly_volume_mwh,
    run,
    verdict,
    world_monthly_hdd,
)

# Elexon MID lives in the gitignored sim/cache/, so a clean checkout (the landing gate's) has no
# electricity spot. The world-reading controls skip there with that reason; the rule control runs
# everywhere. The committed SEAT_RESULT_..._2026-11-18.json is the record of the run itself.
needs_world = pytest.mark.skipif(not _MID.exists(), reason=f"{_MID.name} is gitignored and not cached here")


@needs_world
def test_with_no_default_tariff_book_s4_and_s5_are_the_same_strategy():
    # Defect caught: S5's cap-index hedge leaking into its fixed book (or S4's SVT ladder into
    # its fixed book). With fixed share 1.0 both are "fixed, fully hedged at strike".
    a = hole("S4", 1.0, STRATEGIES["S4"]["fixed"][0], 65.0, "static")
    b = hole("S5", 1.0, STRATEGIES["S5"]["fixed"][0], 65.0, "static")
    assert a["series"] == b["series"]


@needs_world
def test_the_credit_balance_level_cancels_and_its_change_does_not():
    # Only the change in balances held is cash in the window. Defect caught: the level being
    # added as cash (H would move by the level), or the change being dropped (no credit term).
    lo = hole("S1", 0.5, (3, 0.0, 0.0), 65.0, "static")
    hi = hole("S1", 0.5, (3, 0.0, 0.0), 80.0, "static")
    assert lo["H_gbp"] == hi["H_gbp"]
    assert any(r["credit_change_gbp"] != 0 for r in lo["series"])


def test_the_verdict_rule_can_pass_and_can_fail():
    # A rule that refuses everything passes every "does it refuse" test. Both legs, one control.
    def pt(s, h, fs=0.5):
        return {"strategy": s, "fixed_share": fs, "credit_sep_dec_gbp": 65.0, "cover_3m_9m": [0, 0],
                "H_gbp": h}
    good = [pt("S5", -10)] + [pt(s, -200) for s in ("S1", "S2", "S3", "S4")]
    bad = [pt("S5", -300)] + [pt(s, -200) for s in ("S1", "S2", "S3", "S4")]
    assert verdict(good)["passes"] and not verdict(bad)["passes"]
    assert verdict(bad)["inversions"]


@needs_world
def test_every_strategy_point_is_run_on_the_world():
    res = run("static")
    assert {p["strategy"] for p in res["points"]} == set(STRATEGIES)
    assert all(p["H_gbp"] <= 0 for p in res["points"])


def test_the_worlds_weather_is_read_with_each_cells_level_added_back():
    # Defect caught (made, then found, 18 Nov): parsing the store file raw reads each regime's
    # ANOMALY, centred on zero, and gives about 260 HDD in a British July. Through `for_cell` the
    # level is restored. Keyed to the property: in every July of the record, Britain heats little,
    # and every January it heats a lot.
    hdd = world_monthly_hdd()
    assert all(hdd[(y, 7)] < 40 for y in range(2016, 2026))
    assert all(hdd[(y, 1)] > 200 for y in range(2016, 2026))


def test_the_weather_moves_gas_and_only_gas_and_the_direct_debit_is_set_on_normal():
    # Defect caught: weather not reaching volume (the second test would silently rerun the first),
    # or reaching electricity, which is out of scope; or the direct debit being re-set on the
    # weather that happened, which a supplier could not have known and which would make the year
    # balance whatever the winter did.
    assert monthly_volume_mwh("gas", "anomaly") != monthly_volume_mwh("gas", "normal")
    assert monthly_volume_mwh("electricity", "anomaly") == monthly_volume_mwh("electricity", "normal")
    # With the DD fixed on normal, the month-on-month change in (actual - normal) balance is
    # exactly that month's bill difference; a DD re-set on actual weather adds its own term.
    from datetime import date

    from simulation.price_cap_enforcement import ofgem_cap_unit_rate_gbp_per_mwh_inc_vat as rate

    normal, actual = credit_balance_path(65.0, "normal"), credit_balance_path(65.0, "anomaly")
    for y, m, py, pm in ((2021, 12, 2021, 11), (2022, 2, 2022, 1)):
        step = (actual[f"{y}-{m:02d}"] - normal[f"{y}-{m:02d}"]) - (
            actual[f"{py}-{pm:02d}"] - normal[f"{py}-{pm:02d}"])
        bill_gap = (monthly_volume_mwh("gas", "normal")[(y, m)]
                    - monthly_volume_mwh("gas", "anomaly")[(y, m)]) * rate("gas", date(y, m, 15))
        assert abs(step - bill_gap) < 1e-6


@needs_world
def test_at_normal_weather_the_second_test_reproduces_the_first_tests_record():
    # Defect caught: the plan/actual split changing the arithmetic when there is no weather gap.
    # Read against the committed record of the first run, not against this module's own default.
    import json
    from pathlib import Path

    rec = Path(__file__).resolve().parents[2] / (
        "docs/staging/records/SEAT_RESULT_CASH_HOLE_BY_STRATEGY_2021_22_2026-11-18.json")
    first = json.loads(rec.read_text())["static"]["points"]
    for p in first:
        if p["fixed_share"] == 0.75 and p["credit_sep_dec_gbp"] == 65.0:
            pair = (3, *p["cover_3m_9m"])
            got = hole(p["strategy"], 0.75, pair, 65.0, "static", "normal")
            assert got["series"] == p["series"]
