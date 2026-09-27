"""`compare` must keep a population change apart from a per-home change.

The defect it guards: on 2026-09-27 the book's fabric kWh fell 28% across the siting rebuild while
the premises fabric-driven in BOTH arms moved 0.3%. A comparison that reports only the total reads
a premise leaving the fabric path as the siting moving demand.
"""
from tools.siting_frame_counterfactual import compare


def _arm(eligible: dict, homes: dict, ids=None) -> dict:
    return {
        "account_ids": sorted(ids or homes),
        "homes": homes,
        "eligible": {c: {"elec_kwh": e, "gas_kwh": g} for c, (e, g) in eligible.items()},
    }


def _home(lat, area, cell, heads):
    return {"lat": lat, "lon": 0.0, "output_area": area, "store_cell": cell, "headcount": heads}


def test_a_premise_leaving_the_fabric_path_moves_the_total_and_not_the_stayers():
    old = _arm({"A": (4000, 10000), "B": (4000, 10000)},
               {"A": _home(51.0, "E1", "c1", 2), "B": _home(52.0, "E2", "c2", 3)})
    new = _arm({"A": (4000, 10000)},
               {"A": _home(51.0, "E1", "c1", 2), "B": _home(52.5, "E3", "no cell", 1)})
    out = compare(old, new)
    assert out["P5_book_kwh"]["elec_kwh"]["total_move_pct"] == -50.0
    assert out["P5_book_kwh"]["elec_kwh"]["stayers_move_pct"] == 0.0
    assert out["eligible_premises"]["left"] == ["B"]
    assert out["P1_share_frame_cell_changed"] == 0.5
    assert out["P3_share_store_resolution_changed"] == 0.5
    assert out["P4_mean_headcount"] == {"old": 2.5, "new": 1.5,
                                        "share_of_homes_changed": 0.5, "mean_abs_move": 1.0}


def test_a_different_account_set_is_reported_rather_than_compared_silently():
    homes = {"A": _home(51.0, "E1", "c1", 2)}
    out = compare(_arm({"A": (1, 1)}, homes), _arm({"A": (1, 1)}, homes, ids=["A", "Z"]))
    assert out["P0_same_accounts"] is False
