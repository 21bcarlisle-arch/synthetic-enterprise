"""Generator-side tests for tools/generate_world_data.py.

Focus: SITE_EH1_segment_disclosure BLOCKER-2 (cold-eyes, 2026-07-29) -- "the book
declares itself I&C exactly where a residential benchmark is missed... the single
disclosure of true composition sits in a note field where it functions as an
excuse. Classification must be picked ONCE and held EVERYWHERE."

_book_composition classifies the book from dashboard.financial.segment_annual (the
SAME source and method as generate_company_data._segment_mix, so the two surfaces
can never silently disagree). _anchors_runtime then stamps every anchor CARD with
which population its benchmark measures and whether that population mismatches
the book's held classification -- structurally, not as an ad hoc excuse note.

R15 (a control must be able to FAIL): the classification and the mismatch flags
must FOLLOW the source (a baked/hardcoded shape fails these).
"""
from tools.generate_world_data import _anchors_runtime, _book_composition


def _dashboard(segment_annual):
    return {"financial": {"segment_annual": segment_annual}}


def test_book_composition_follows_segment_annual_r15():
    dash = _dashboard([
        {"year": 2024,
         "i&c_electricity": {"revenue_gbp": 9000.0},
         "resi_electricity": {"revenue_gbp": 1000.0}},
    ])
    out = _book_composition(dash)
    assert out["available"] is True
    assert out["classification"] == "I&C-majority"
    assert out["ic_revenue_pct"] == 90.0
    assert out["residential_revenue_pct"] == 10.0


def test_book_composition_mutation_flips_classification_r15():
    # Killer mutation: swap which segment dominates -- classification must follow.
    ic_majority = _dashboard([
        {"year": 2024, "i&c_electricity": {"revenue_gbp": 9000.0},
         "resi_electricity": {"revenue_gbp": 1000.0}},
    ])
    resi_majority = _dashboard([
        {"year": 2024, "i&c_electricity": {"revenue_gbp": 1000.0},
         "resi_electricity": {"revenue_gbp": 9000.0}},
    ])
    a = _book_composition(ic_majority)
    b = _book_composition(resi_majority)
    assert a["classification"] == "I&C-majority"
    assert b["classification"] == "residential-majority"


def test_book_composition_fail_closed_on_empty_input_r15():
    assert _book_composition({})["available"] is False
    assert _book_composition(_dashboard([]))["available"] is False
    assert _book_composition(_dashboard([{"year": 2024, "i&c_electricity": {"revenue_gbp": 0.0}}]))["available"] is False


# --- BLOCKER-2: population disclosure + mismatch flag on every anchor card ------


def _anchoring():
    return {
        "overall_rag": "RED",
        "long_run_comparison": {
            "sim_avg_pct": 6.1, "ofgem_avg_pct": 13.6, "ratio": 0.45, "rag": "GREEN",
            "note": "SIM portfolio is predominantly I&C...",
        },
        "bad_debt_vs_benchmark": [
            {"year": 2025, "bad_debt_rate": -0.0, "benchmark_low_pct": 0.5, "benchmark_high_pct": 2.5, "rag": "AMBER"},
        ],
        "complaints_vs_benchmark": [
            {"year": 2025, "complaint_rate_pct": 5.52, "benchmark_lo": 1.0, "benchmark_green_hi": 6.0, "rag": "GREEN", "is_crisis_year": False},
        ],
        "arrears_vs_benchmark": [
            {"year": 2025, "ic_aggregate_rate_pct": 8.1, "rag": "AMBER"},
        ],
    }


def test_every_card_states_its_benchmark_population():
    out = _anchors_runtime(_anchoring(), _book_composition(_dashboard([
        {"year": 2024, "i&c_electricity": {"revenue_gbp": 9000.0}, "resi_electricity": {"revenue_gbp": 1000.0}},
    ])))
    assert out["cards"], "no cards produced"
    for card in out["cards"]:
        assert card.get("benchmark_population"), card
        assert card.get("book_classification"), card


def test_churn_card_flags_population_mismatch_on_ic_majority_book_r15():
    # THE named defect: a residential benchmark (Ofgem switching) measured
    # against an I&C-majority book must be flagged, not silently GREEN with no
    # structural signal beyond a note that reads as an excuse.
    comp = _book_composition(_dashboard([
        {"year": 2024, "i&c_electricity": {"revenue_gbp": 9000.0}, "resi_electricity": {"revenue_gbp": 1000.0}},
    ]))
    out = _anchors_runtime(_anchoring(), comp)
    churn = next(c for c in out["cards"] if c["metric"].startswith("Churn"))
    assert churn["population_mismatch"] is True
    assert "residential" in churn["benchmark_population"].lower()


def test_mismatch_flag_follows_composition_mutation_r15():
    # Killer mutation: flip the book to residential-majority -- the SAME churn
    # benchmark (residential) is now aligned, so the mismatch flag must clear.
    resi_comp = _book_composition(_dashboard([
        {"year": 2024, "i&c_electricity": {"revenue_gbp": 1000.0}, "resi_electricity": {"revenue_gbp": 9000.0}},
    ]))
    out = _anchors_runtime(_anchoring(), resi_comp)
    churn = next(c for c in out["cards"] if c["metric"].startswith("Churn"))
    assert churn["population_mismatch"] is False


def test_bad_debt_card_is_population_neutral_never_flagged():
    # The industry-wide bad-debt benchmark is segment-neutral by construction --
    # it must never be flagged as a mismatch regardless of book classification.
    comp = _book_composition(_dashboard([
        {"year": 2024, "i&c_electricity": {"revenue_gbp": 9000.0}, "resi_electricity": {"revenue_gbp": 1000.0}},
    ]))
    out = _anchors_runtime(_anchoring(), comp)
    bd = next(c for c in out["cards"] if c["metric"].startswith("Bad debt"))
    assert bd["population_mismatch"] is False


def test_book_composition_single_source_of_truth_present_on_register():
    # BLOCKER-2's core ask: the classification is picked ONCE and held on the
    # register itself (anchors.runtime.book_composition), not just scattered
    # per-card -- so a reader sees the one fact, not four different tellings.
    comp = _book_composition(_dashboard([
        {"year": 2024, "i&c_electricity": {"revenue_gbp": 9000.0}, "resi_electricity": {"revenue_gbp": 1000.0}},
    ]))
    out = _anchors_runtime(_anchoring(), comp)
    assert out["book_composition"]["classification"] == "I&C-majority"
    # every card's book_classification is the identical string -- one classification,
    # held everywhere, never re-derived per card.
    labels = {c["book_classification"] for c in out["cards"]}
    assert labels == {out["book_composition"]["classification_label"]}


def test_anchors_runtime_fail_closed_on_missing_composition():
    # A card with no composition available must still render (the anchor data
    # itself is not gated on this atom's addition) but with an honest absent
    # book_composition rather than a fabricated classification.
    out = _anchors_runtime(_anchoring(), None)
    assert out["book_composition"]["available"] is False
    for card in out["cards"]:
        assert card["book_classification"] is None
        assert card["population_mismatch"] is None


def test_live_world_json_book_composition_matches_company_segment_mix():
    # BLOCKER-2's binding requirement: THIS register's classification and
    # /company/'s segment_mix classification must be the SAME fact, computed
    # the same way from the same source -- never two independent tellings.
    from tools.generate_company_data import _segment_mix, _stress_bands
    from tools.generate_world_data import generate as gen_world
    import json
    from pathlib import Path

    world = gen_world()
    dashboard = json.loads((Path(__file__).resolve().parent.parent / "site" / "data" / "dashboard.json").read_text())
    sample = json.loads((Path(__file__).resolve().parent.parent / "site" / "data" / "customer_sample.json").read_text())
    company_mix = _segment_mix(dashboard, _stress_bands(sample))
    world_comp = world["anchors"]["runtime"]["book_composition"]
    if not (company_mix.get("available") and world_comp.get("available")):
        return  # nothing to compare if either input is absent this run
    assert world_comp["classification"] == company_mix["classification"]
    assert world_comp["ic_revenue_pct"] == company_mix["ic_revenue_pct"]
