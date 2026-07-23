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


def _sample_cells(rows):
    # rows: {cid: (cost, {field: value, ...})} -> a sample carrying cost + cell attrs.
    return {
        "customers": {
            cid: dict({"cost_to_serve_gbp": cost}, **attrs) for cid, (cost, attrs) in rows.items()
        }
    }


def test_payment_channel_coverage_cell_follows_source_r15():
    # RC6 §C follow-on: cost-to-serve broken out by payment_channel -- the load-bearing
    # activity-based-pricing cell. R15: each cell's median FOLLOWS its members (a baked
    # figure fails). standard_credit customers here cost more to serve than direct_debit.
    out = _cost_to_serve_distribution(
        _sample_cells(
            {
                "C1": (100.0, {"payment_channel": "direct_debit"}),
                "C2": (200.0, {"payment_channel": "direct_debit"}),
                "C3": (900.0, {"payment_channel": "standard_credit"}),
                "C4": (1100.0, {"payment_channel": "standard_credit"}),
            }
        )
    )
    cells = {c["cell"]: c for c in out["by_payment_channel"]}
    assert set(cells) == {"direct_debit", "standard_credit"}
    assert cells["direct_debit"]["n"] == 2 and cells["direct_debit"]["median_gbp"] == 150.0
    assert cells["standard_credit"]["n"] == 2 and cells["standard_credit"]["median_gbp"] == 1000.0
    # Killer mutation: move one standard_credit customer's cost -> its cell median moves.
    mutated = _cost_to_serve_distribution(
        _sample_cells(
            {
                "C1": (100.0, {"payment_channel": "direct_debit"}),
                "C2": (200.0, {"payment_channel": "direct_debit"}),
                "C3": (900.0, {"payment_channel": "standard_credit"}),
                "C4": (5000.0, {"payment_channel": "standard_credit"}),
            }
        )
    )
    mcells = {c["cell"]: c for c in mutated["by_payment_channel"]}
    assert mcells["standard_credit"]["median_gbp"] != cells["standard_credit"]["median_gbp"]


def test_absent_cell_attribute_is_skipped_not_bucketed():
    # A customer with no payment_channel (gas leg / I&C) is SKIPPED from the cell
    # breakdown, never bucketed as a fabricated "None" cell. The total still counts it.
    out = _cost_to_serve_distribution(
        _sample_cells(
            {
                "C1": (100.0, {"payment_channel": "direct_debit"}),
                "C2": (200.0, {"payment_channel": "direct_debit"}),
                "Cg": (300.0, {}),  # gas leg: no payment_channel
            }
        )
    )
    assert out["n"] == 3  # the total counts all three
    cells = {c["cell"]: c for c in out["by_payment_channel"]}
    assert "None" not in cells and None not in cells
    # only direct_debit present -> a single cell is not a distribution -> collapses to []
    assert out["by_payment_channel"] == []


def test_single_cell_group_collapses_to_empty():
    # A cell group with only ONE distinct populated cell is theatre (the total covers
    # it) -> emitted as [] rather than a one-bar "distribution".
    out = _cost_to_serve_distribution(
        _sample_cells(
            {
                "C1": (100.0, {"tenure": "owner_occupier"}),
                "C2": (200.0, {"tenure": "owner_occupier"}),
            }
        )
    )
    assert out["by_tenure"] == []


def test_cells_absent_on_bare_sample_no_crash():
    # The bare sample (cost only, no cell attrs) must still produce a valid distribution
    # with empty cell groups -- the follow-on must not break the base function.
    out = _cost_to_serve_distribution(_sample({"C1": 100.0, "C2": 200.0}))
    assert out["available"] is True
    assert out["by_payment_channel"] == [] and out["by_tenure"] == []


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
