"""Generator-side tests for tools/generate_company_data.py.

Focus: the RC6 §C cost-to-serve DISTRIBUTION (DIRECTOR 2026-07-23 -- "distributions
across coverage cells ... certainly not totals from a random sample of customers").

R15 (a control must be able to FAIL): the distribution must FOLLOW the per-customer
cost_to_serve_gbp values (a baked/aggregate-only figure fails these), split by
coverage cell (segment), and FAIL-CLOSED on an empty sample (never a silent zero).
"""
from tools.generate_company_data import _cost_to_serve_distribution


def _sample(vals_by_id):
    return {"customers": {cid: {"cost_to_serve_gbp": v} for cid, v in vals_by_id.items()}}


def test_distribution_follows_per_customer_values_r15():
    # Three resi customers with known costs -> min/median/max/mean derived from THEM.
    out = _cost_to_serve_distribution(_sample({"C1": 100.0, "C2": 300.0, "C3": 200.0}))
    assert out["available"] is True
    assert out["n"] == 3
    assert out["min_gbp"] == 100.0
    assert out["median_gbp"] == 200.0
    assert out["max_gbp"] == 300.0
    assert out["mean_gbp"] == 200.0
    assert out["values_gbp"] == [100.0, 200.0, 300.0]


def test_mutation_of_one_customer_moves_the_distribution_r15():
    # Killer mutation: change ONE customer's cost -> the max (and mean) must move.
    base = _cost_to_serve_distribution(_sample({"C1": 100.0, "C2": 200.0}))
    mutated = _cost_to_serve_distribution(_sample({"C1": 100.0, "C2": 9000.0}))
    assert mutated["max_gbp"] != base["max_gbp"]
    assert mutated["max_gbp"] == 9000.0
    assert mutated["mean_gbp"] != base["mean_gbp"]


def test_segment_split_is_the_coverage_cell_distribution():
    # IC accounts (id contains "IC") split from residential -> two coverage cells,
    # each with its own median. This is the "distribution across coverage cells".
    out = _cost_to_serve_distribution(
        _sample({"C1": 100.0, "C2": 200.0, "C_IC1": 3000.0, "C_IC2": 4000.0})
    )
    segs = {s["segment"]: s for s in out["by_segment"]}
    assert set(segs) == {"resi", "ic"}
    assert segs["resi"]["n"] == 2 and segs["resi"]["median_gbp"] == 150.0
    assert segs["ic"]["n"] == 2 and segs["ic"]["median_gbp"] == 3500.0


def test_fail_closed_on_empty_sample_r15():
    # FAIL-CLOSED: an empty/uncomputable sample returns available:False, never a
    # silently-zero total the page would render as a real figure.
    for empty in ({}, {"customers": {}}, {"customers": {"C1": {}}}, None):
        out = _cost_to_serve_distribution(empty)
        assert out.get("available") is not True, out
        assert out.get("n", 0) == 0, out


def test_no_goal_seek_reads_only_cost_to_serve_r12():
    # R12/R13: the distribution reads cost_to_serve_gbp ONLY -- a company-P&L field
    # (net_gbp) on the customer must not perturb it (no write-back / goal-seek path).
    plain = _cost_to_serve_distribution(_sample({"C1": 100.0, "C2": 200.0}))
    s = {
        "customers": {
            "C1": {"cost_to_serve_gbp": 100.0, "net_gbp": -50000.0},
            "C2": {"cost_to_serve_gbp": 200.0, "net_gbp": 99999.0},
        }
    }
    with_pnl = _cost_to_serve_distribution(s)
    assert with_pnl["values_gbp"] == plain["values_gbp"]
    assert with_pnl["median_gbp"] == plain["median_gbp"]
