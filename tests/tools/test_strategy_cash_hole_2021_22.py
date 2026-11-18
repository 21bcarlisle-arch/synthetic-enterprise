"""Controls on the 2021-22 strategy cash-hole composer (`tools/strategy_cash_hole_2021_22.py`).

Each names the defect it catches. Keyed to properties of the instrument, not to today's holes.
"""

import pytest

from tools.strategy_cash_hole_2021_22 import _MID, STRATEGIES, hole, run, verdict

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
