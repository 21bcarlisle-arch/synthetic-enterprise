"""Generator-side tests for tools/generate_company_data.py.

Focus: the RC6 §C cost-to-serve DISTRIBUTION (DIRECTOR 2026-07-23 -- "distributions
across coverage cells ... certainly not totals from a random sample of customers").

R15 (a control must be able to FAIL): the distribution must FOLLOW the per-customer
cost_to_serve_gbp values (a baked/aggregate-only figure fails these), split by
coverage cell (segment), and FAIL-CLOSED on an empty sample (never a silent zero).
"""
from tools.generate_company_data import (
    _arrears_distribution,
    _cost_to_serve_distribution,
)


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


# --- SITE_MODEL_SPINE §C remainder: arrears, under Ofgem's definition ---
#
# An account is in arrears when a bill is still owed more than 91 days after its due date;
# owed is the bill's own outstanding_gbp, so a scheme credit is never counted as owed. R15: the
# distribution FOLLOWS the per-bill amounts; FAIL-CLOSED on a ledger with no dated bills.


def _ledger(billed_paid_by_id):
    """One bill per account, due 2020-01-01 and owing max(billed - paid, 0), plus a later paid
    bill that puts the ledger's as-of date at 2021-01-01 (far past 91 days)."""
    return {
        "customers": {
            cid: {
                "segment": seg,
                "invoices": [
                    {"issue_date": "2019-12-15", "due_date": "2020-01-01",
                     "total_amount_gbp": b, "outstanding_gbp": round(max(b - p, 0.0), 2)},
                    {"issue_date": "2021-01-01", "due_date": "2021-01-15",
                     "total_amount_gbp": 10.0, "outstanding_gbp": 0.0},
                ],
            }
            for cid, (b, p, seg) in billed_paid_by_id.items()
        }
    }


def test_arrears_follows_each_bills_outstanding_r15():
    out = _arrears_distribution(
        {},
        _ledger({"C1": (1000.0, 900.0, "resi"), "C2": (500.0, 700.0, "resi"),
                 "C3": (2000.0, 1500.0, "resi")}),
    )
    assert out["available"] is True and out["n"] == 3
    assert out["clock"] == "owed_past_due" and out["as_of"] == "2021-01-01"
    # owed: C1=100, C2=0 (overpaid: a credit is not arrears), C3=500
    assert out["values_gbp"] == [0.0, 100.0, 500.0]
    assert out["median_gbp"] == 100.0
    assert out["in_arrears"] == 2 and out["not_overdue"] == 1


def test_arrears_distribution_is_mutation_sensitive_r15():
    base = _arrears_distribution({}, _ledger({"C1": (1000.0, 900.0, "resi"),
                                              "C2": (1000.0, 950.0, "resi")}))
    mutated = _arrears_distribution({}, _ledger({"C1": (1000.0, 900.0, "resi"),
                                                 "C2": (1000.0, 100.0, "resi")}))
    assert mutated["max_gbp"] != base["max_gbp"] and mutated["max_gbp"] == 900.0
    assert mutated["gross_exposure_gbp"] != base["gross_exposure_gbp"]


def test_a_scheme_credit_is_never_counted_as_owed_and_every_band_can_be_reached():
    """The 2026-11-11 Expert Hour defect: billed-minus-banked counted the GBP 400 EBSS credit,
    which the government paid, as the household's debt. A bill settled by the credit owes
    nothing. One fixture reaches all three bands (in arrears, overdue under 91 days, not
    overdue), so a rule that refuses or admits everything cannot pass."""
    def acct(*bills):
        return {"segment": "resi", "invoices": [
            {"issue_date": i, "due_date": d, "total_amount_gbp": t, "outstanding_gbp": o,
             **({"scheme_credit_gbp": sc} if sc else {})}
            for i, d, t, o, sc in bills]}
    ledger = {"customers": {
        # EBSS bill: 400 billed, 400 scheme credit, household paid nothing, owes nothing.
        "EBSS": acct(("2023-01-01", "2023-01-15", 400.0, 0.0, 400.0)),
        "OLD": acct(("2023-01-01", "2023-01-15", 80.0, 80.0, None)),     # 165 days late
        "RECENT": acct(("2023-05-01", "2023-05-15", 60.0, 60.0, None)),  # 46 days late
        "NOTDUE": acct(("2023-06-30", "2023-07-14", 70.0, 70.0, None)),  # sets as-of 2023-06-30
    }}
    out = _arrears_distribution({}, ledger)
    assert out["as_of"] == "2023-06-30"
    assert out["in_arrears"] == 1 and out["overdue_under_91_days"] == 1 and out["not_overdue"] == 2
    assert out["gross_exposure_gbp"] == 140.0  # 80 + 60; the EBSS bill adds nothing


def test_arrears_gross_exposure_is_a_positive_floor():
    out = _arrears_distribution(
        {},
        _ledger({"C1": (1000.0, 900.0, "resi"),     # owes 100
                 "C2": (1000.0, 2000.0, "resi")}),  # overpaid
    )
    assert out["gross_exposure_gbp"] == 100.0
    assert out["gross_exposure_is_floor"] is True
    assert out["in_arrears"] == 1 and out["not_overdue"] == 1


def test_arrears_segment_split_is_the_coverage_cell_distribution():
    out = _arrears_distribution(
        {},
        _ledger({"C1": (1000.0, 900.0, "resi"), "C2": (1000.0, 800.0, "resi"),
                 "I1": (5000.0, 4000.0, "I&C"), "I2": (5000.0, 2000.0, "I&C")}),
    )
    segs = {s["segment"]: s for s in out["by_segment"]}
    assert set(segs) == {"resi", "I&C"}
    assert segs["resi"]["n"] == 2 and segs["resi"]["median_gbp"] == 150.0
    assert segs["I&C"]["n"] == 2 and segs["I&C"]["median_gbp"] == 2000.0


def test_arrears_payment_channel_cell_joins_sample_r15():
    # The activity cell (payment_channel) is joined from customer_sample, not the
    # ledger. Standard-credit vs direct-debit split must follow the source balances.
    ledger = _ledger({"C1": (1000.0, 950.0, "resi"), "C2": (1000.0, 900.0, "resi"),
                      "C3": (1000.0, 500.0, "resi"), "C4": (1000.0, 400.0, "resi")})
    sample = {"customers": {
        "C1": {"payment_channel": "direct_debit"},
        "C2": {"payment_channel": "direct_debit"},
        "C3": {"payment_channel": "standard_credit"},
        "C4": {"payment_channel": "standard_credit"},
    }}
    out = _arrears_distribution(sample, ledger)
    cells = {c["cell"]: c for c in out["by_payment_channel"]}
    assert cells["direct_debit"]["median_gbp"] == 75.0   # (50, 100)
    assert cells["standard_credit"]["median_gbp"] == 550.0  # (500, 600)


def test_arrears_absent_cell_attribute_skipped_not_bucketed():
    # A customer with no payment_channel in the sample (I&C leg) is skipped from
    # the cell split, never bucketed as a fabricated cell.
    ledger = _ledger({"C1": (1000.0, 900.0, "resi"), "C2": (1000.0, 800.0, "resi"),
                      "I1": (5000.0, 4000.0, "I&C")})
    sample = {"customers": {
        "C1": {"payment_channel": "direct_debit"},
        "C2": {"payment_channel": "standard_credit"},
        "I1": {},  # no channel
    }}
    out = _arrears_distribution(sample, ledger)
    total_cell_n = sum(c["n"] for c in out["by_payment_channel"])
    assert total_cell_n == 2  # I1 excluded from the cell split


def test_arrears_fail_closed_on_empty_ledger_r15():
    # FAIL-CLOSED: no customer carrying BOTH billed and paid -> available:False.
    for empty in ({}, {"customers": {}}, {"customers": {"C1": {"segment": "resi"}}}, None):
        out = _arrears_distribution({}, empty)
        assert out.get("available") is not True, out
        assert out.get("n", 0) == 0, out
    # missing_lines are always enumerated when available (RC7 honest-absent).
    ok = _arrears_distribution({}, _ledger({"C1": (100.0, 50.0, "resi"),
                                            "C2": (100.0, 90.0, "resi")}))
    assert ok["missing_lines"] and len(ok["missing_lines"]) >= 3
