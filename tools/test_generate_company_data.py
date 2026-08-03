"""Generator-side tests for tools/generate_company_data.py.

Focus: the RC6 §C cost-to-serve DISTRIBUTION (DIRECTOR 2026-07-23 -- "distributions
across coverage cells ... certainly not totals from a random sample of customers").

R15 (a control must be able to FAIL): the distribution must FOLLOW the per-customer
cost_to_serve_gbp values (a baked/aggregate-only figure fails these), split by
coverage cell (segment), and FAIL-CLOSED on an empty sample (never a silent zero).
"""
from tools.generate_company_data import (
    _arrears_distribution,
    _check_segment_disclosure_present,
    _cost_to_serve_distribution,
    _segment_mix,
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


# --- SITE_MODEL_SPINE §C remainder: the arrears-£ balance distribution ---
#
# Through-the-wall observable: arrears = total_billed - total_paid per customer,
# from the company's OWN ledger (billing_ledger.json). R15: the distribution must
# FOLLOW those per-customer balances (a baked figure fails); the gross floor is
# positive-balances-only; FAIL-CLOSED on a ledger with no billed/paid pair.


def _ledger(billed_paid_by_id):
    return {
        "customers": {
            cid: {"total_billed_gbp": b, "total_paid_gbp": p, "segment": seg}
            for cid, (b, p, seg) in billed_paid_by_id.items()
        }
    }


def test_arrears_follows_billed_minus_banked_r15():
    # arrears per customer = billed - paid; the distribution is derived from THEM.
    out = _arrears_distribution(
        {},
        _ledger({"C1": (1000.0, 900.0, "resi"), "C2": (500.0, 700.0, "resi"),
                 "C3": (2000.0, 1500.0, "resi")}),
    )
    assert out["available"] is True and out["n"] == 3
    assert out["clock"] == "billed_minus_banked"
    # balances: C1=+100, C2=-200 (credit), C3=+500 -> sorted [-200, 100, 500]
    assert out["values_gbp"] == [-200.0, 100.0, 500.0]
    assert out["min_gbp"] == -200.0 and out["max_gbp"] == 500.0
    assert out["median_gbp"] == 100.0


def test_arrears_mutation_of_one_balance_moves_distribution_r15():
    # Killer mutation: change ONE customer's paid amount -> its balance, and the
    # max + gross floor, must move.
    base = _arrears_distribution({}, _ledger({"C1": (1000.0, 900.0, "resi"),
                                              "C2": (1000.0, 950.0, "resi")}))
    mutated = _arrears_distribution({}, _ledger({"C1": (1000.0, 900.0, "resi"),
                                                 "C2": (1000.0, 100.0, "resi")}))
    assert mutated["max_gbp"] != base["max_gbp"] and mutated["max_gbp"] == 900.0
    assert mutated["gross_exposure_gbp"] != base["gross_exposure_gbp"]


def test_arrears_gross_exposure_is_positive_only_floor():
    # RC7 floor-not-figure: gross exposure sums ONLY positive balances -- a credit
    # balance must NOT net it down (a bad-debt base is not reduced by prepayers).
    out = _arrears_distribution(
        {},
        _ledger({"C1": (1000.0, 900.0, "resi"),   # +100 (owes)
                 "C2": (1000.0, 2000.0, "resi")}),  # -1000 (in credit)
    )
    assert out["gross_exposure_gbp"] == 100.0  # NOT 100 - 1000
    assert out["gross_exposure_is_floor"] is True
    assert out["in_arrears"] == 1 and out["in_credit"] == 1


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


# --- SITE_EH1_segment_disclosure (cold-eyes BLOCKER-1, 2026-07-29) ---------------
#
# "The clock is labelled on every figure and the SEGMENT on none." _segment_mix
# discloses revenue/margin BY SEGMENT wherever this generator's own per-customer
# tiles divide money by customers. R12/R13: reads segment_annual + stress_bands
# ONLY -- it must never reweight or author the book.


def _dashboard(segment_annual):
    return {"financial": {"segment_annual": segment_annual}}


def test_segment_mix_follows_segment_annual_and_stress_bands_r15():
    # A book earned almost entirely by I&C accounts -- the classification, the
    # pct split and the per-customer figures must all FOLLOW the source (a baked
    # constant fails this).
    dash = _dashboard([
        {"year": 2024,
         "i&c_electricity": {"revenue_gbp": 9000.0, "net_gbp": 900.0},
         "resi_electricity": {"revenue_gbp": 1000.0, "net_gbp": 100.0}},
    ])
    sb = {"ic": 2, "residential": 8}
    out = _segment_mix(dash, sb)
    assert out["available"] is True
    assert out["classification"] == "I&C-majority"
    assert out["ic_revenue_pct"] == 90.0
    assert out["residential_revenue_pct"] == 10.0
    assert out["ic_customers"] == 2 and out["residential_customers"] == 8
    assert out["ic_net_margin_per_customer_gbp"] == 450.0  # 900 / 2
    assert out["residential_net_margin_per_customer_gbp"] == 12.5  # 100 / 8


def test_segment_mix_mutation_moves_classification_and_split_r15():
    # Killer mutation: flip the book to residential-majority -- classification
    # and every derived figure must follow, not stay pinned to the old shape.
    ic_majority = _dashboard([
        {"year": 2024, "i&c_electricity": {"revenue_gbp": 9000.0, "net_gbp": 900.0},
         "resi_electricity": {"revenue_gbp": 1000.0, "net_gbp": 100.0}},
    ])
    resi_majority = _dashboard([
        {"year": 2024, "i&c_electricity": {"revenue_gbp": 1000.0, "net_gbp": 100.0},
         "resi_electricity": {"revenue_gbp": 9000.0, "net_gbp": 900.0}},
    ])
    sb = {"ic": 2, "residential": 8}
    a = _segment_mix(ic_majority, sb)
    b = _segment_mix(resi_majority, sb)
    assert a["classification"] == "I&C-majority"
    assert b["classification"] == "residential-majority"
    assert a["ic_revenue_pct"] != b["ic_revenue_pct"]


def test_segment_mix_sme_folds_into_residential_not_dropped():
    # sme_electricity is neither "i&c_*" nor "resi_*" -- it must be counted
    # (folded into residential, per the includes_note), never silently dropped
    # from the total (which would corrupt the pct split).
    dash = _dashboard([
        {"year": 2024,
         "i&c_electricity": {"revenue_gbp": 500.0, "net_gbp": 50.0},
         "sme_electricity": {"revenue_gbp": 500.0, "net_gbp": 50.0}},
    ])
    sb = {"ic": 1, "residential": 1}
    out = _segment_mix(dash, sb)
    assert out["available"] is True
    assert out["ic_revenue_pct"] == 50.0
    assert out["residential_revenue_pct"] == 50.0
    assert "SME" in out["includes_note"]


def test_segment_mix_fail_closed_on_missing_inputs_r15():
    # FAIL-CLOSED: no segment_annual, no stress_bands, or a book with zero total
    # revenue -- never silently claim an available split from nothing.
    assert _segment_mix({}, {"ic": 1, "residential": 1})["available"] is False
    assert _segment_mix(_dashboard([{"year": 2024, "i&c_electricity": {"revenue_gbp": 1.0}}]), None)["available"] is False
    assert _segment_mix(_dashboard([{"year": 2024, "i&c_electricity": {"revenue_gbp": 0.0}}]), {"ic": 1, "residential": 1})["available"] is False


def test_segment_mix_no_goal_seek_reads_only_revenue_and_net_r12():
    # R12/R13: this reads revenue_gbp/net_gbp + customer counts ONLY -- it must
    # never reweight the book or read any other field that could turn a
    # disclosure surface into a tuning knob.
    dash = _dashboard([
        {"year": 2024,
         "i&c_electricity": {"revenue_gbp": 900.0, "net_gbp": 90.0, "net_margin_pct": 999.0},
         "resi_electricity": {"revenue_gbp": 100.0, "net_gbp": 10.0, "net_margin_pct": -999.0}},
    ])
    sb = {"ic": 1, "residential": 1}
    out = _segment_mix(dash, sb)
    assert out["ic_revenue_pct"] == 90.0  # unaffected by the absurd net_margin_pct values present


# --- R10 CLASS GUARD: any per-customer money figure must carry its segment ------


def test_segment_disclosure_gate_passes_with_no_per_customer_figures():
    # Nothing to disclose against -- the gate has nothing to fail on.
    assert _check_segment_disclosure_present({"finance": {}}) is True


def test_segment_disclosure_gate_fails_when_per_customer_figure_has_no_segment_mix_r15():
    # THE KILLER MUTATION named in the task: a per-customer money figure ships
    # with segment_mix missing entirely -- must fail, not pass by omission.
    doc = {"some_new_tile_per_customer_gbp": 12345.0}
    assert _check_segment_disclosure_present(doc) is False


def test_segment_disclosure_gate_fails_on_blank_or_unavailable_segment_mix_r15():
    # FAIL-CLOSED: segment_mix present but available:False, or present-but-blank
    # required fields, must still fail -- not pass on a hollow shell.
    doc_a = {"x_per_customer_gbp": 1.0, "segment_mix": {"available": False}}
    assert _check_segment_disclosure_present(doc_a) is False
    doc_b = {"x_per_customer_gbp": 1.0, "segment_mix": {
        "available": True, "classification": None, "ic_revenue_pct": 90.0,
        "residential_revenue_pct": 10.0, "ic_customers": 1, "residential_customers": 1,
    }}
    assert _check_segment_disclosure_present(doc_b) is False


def test_segment_disclosure_gate_passes_when_segment_mix_complete():
    doc = {"x_per_customer_gbp": 1.0, "segment_mix": {
        "available": True, "classification": "I&C-majority", "ic_revenue_pct": 90.0,
        "residential_revenue_pct": 10.0, "ic_customers": 1, "residential_customers": 1,
    }}
    assert _check_segment_disclosure_present(doc) is True


def test_segment_disclosure_gate_finds_per_customer_keys_at_any_depth():
    # The scan must find a future per-customer figure NESTED anywhere in the
    # document -- not just top-level -- so a new nested tile can't dodge the
    # gate by being buried inside another section.
    doc = {"some_section": {"nested": {"deep_per_customer_gbp": 1.0}}}
    assert _check_segment_disclosure_present(doc) is False
    doc["segment_mix"] = {
        "available": True, "classification": "I&C-majority", "ic_revenue_pct": 90.0,
        "residential_revenue_pct": 10.0, "ic_customers": 1, "residential_customers": 1,
    }
    assert _check_segment_disclosure_present(doc) is True


def test_live_company_json_segment_mix_passes_its_own_gate():
    # The real generated document must pass its own gate -- the gate this atom
    # adds must not immediately red the surface it protects.
    from tools.generate_company_data import generate
    data = generate()
    assert _check_segment_disclosure_present(data) is True
    assert data["segment_mix"]["available"] is True
