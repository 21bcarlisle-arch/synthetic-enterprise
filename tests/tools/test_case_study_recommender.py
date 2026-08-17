"""Tests for tools/generate_case_study_recommender.py --
WEBSITE_AS_SHOWCASE.md tab 4 (CUSTOMER PORTAL -- MICRO MEETS MACRO): the
case-study recommender."""
import json
from pathlib import Path as _P
import sys

sys.path.insert(0, str(_P(__file__).resolve().parents[2]))

from tools.generate_case_study_recommender import (
    _max_divergence, _writeoffs, _retention_then_churn, _life_events,
    _score_households, _pick, _fmt_level, _fmt_points, _gap_points,
    build, generate,
)


def test_max_divergence_picks_largest_gap():
    sample = {"C1": {"churn_accuracy_by_renewal": [
        {"term_start": "2016-12-31", "sim_churn_probability": 0.1, "company_churn_estimate": 0.12, "churn_estimate_error_pct": 0.2},
        {"term_start": "2017-12-31", "sim_churn_probability": 0.1, "company_churn_estimate": 0.02, "churn_estimate_error_pct": -0.8},
    ]}}
    worst = _max_divergence(sample, "C1")
    assert worst["term_start"] == "2017-12-31"


def test_max_divergence_none_when_missing():
    assert _max_divergence({}, "C1") is None
    assert _max_divergence({"C1": {}}, "C1") is None


def test_writeoffs_filters_by_outcome():
    chain = [{"outcome": "FIRST_NOTICE"}, {"outcome": "WRITTEN_OFF", "date": "2016-01-01"}, {"outcome": "WRITTEN_OFF", "date": "2017-01-01"}]
    assert len(_writeoffs(chain)) == 2


def test_retention_then_churn_true_when_retention_precedes_churn():
    timeline = [{"type": "renewed", "date": "2018-01-01"}, {"type": "churned", "date": "2020-01-01"}]
    chain = [{"event_type": "retention_decision", "date": "2018-12-31", "outcome": "retained"}]
    assert _retention_then_churn(timeline, chain) is True


def test_retention_then_churn_false_when_retention_after_churn():
    timeline = [{"type": "churned", "date": "2020-01-01"}]
    chain = [{"event_type": "retention_decision", "date": "2021-01-01", "outcome": "retained"}]
    assert _retention_then_churn(timeline, chain) is False


def test_retention_then_churn_false_without_churn():
    timeline = [{"type": "renewed", "date": "2018-01-01"}]
    chain = [{"event_type": "retention_decision", "date": "2018-12-31", "outcome": "retained"}]
    assert _retention_then_churn(timeline, chain) is False


def test_life_events_filters_by_type():
    timeline = [{"type": "renewed"}, {"type": "life_event", "detail": "New baby"}]
    out = _life_events(timeline)
    assert len(out) == 1 and out[0]["detail"] == "New baby"


def test_fmt_level_uses_absolute_value_and_keeps_one_decimal():
    assert _fmt_level(-0.25) == "25.0%"
    assert _fmt_level(0.5) == "50.0%"
    # The defect this decimal exists for: the old formatter rounded 3.23% to
    # "3%", so the gap printed beside it could not be reproduced by a reader.
    assert _fmt_level(0.0323) == "3.2%"


def test_fmt_points_carries_its_unit_in_the_string():
    assert _fmt_points(91.77) == "91.8 percentage points"
    assert _fmt_points(-12.16) == "12.2 percentage points"


# ---------------------------------------------------------------------------
# coldwalk:site2_coo_2841_percent_error_arithmetic_doubt -- the CLASS control.
#
# The finding was adjudicated a false positive on its arithmetic (the ratio
# ties on unrounded inputs) with its framing half kept as a minor. Two things
# were undercounted, and both are covered here rather than at the instance:
#   (a) a SECOND live headline had the mirror-image defect -- a 12.2-point
#       difference published as "fell 12%", which reads as a relative fall;
#   (b) the RANKING, not just the framing, used the ratio, so the renewal a
#       household is shown (and deep-linked to via ?year=) was chosen by
#       1/denominator rather than by divergence.
# The controls below are over the produced OUTPUT and over the module's
# formatter surface, so a new headline cannot reintroduce the class.
# ---------------------------------------------------------------------------
# The slots whose whole claim IS a quantified change. Each must publish the
# figure and the levels it is derived from; named rather than counted so one
# cannot stand in for the other.
_QUANTIFIED_SLOTS = frozenset({
    "Largest company-vs-SIM churn divergence",
    "Silent-middle churn risk",
})
_CHANGE_WORDS = (
    "error", "fell", "rose", "gap", "apart", "divergence", "drop", "off by",
    "increase", "decrease", "wider", "narrower", "swing",
)


def _clause_outside_parentheses(headline):
    """The claim itself, with any (sim X vs company Y) inputs parenthetical
    removed. A bare percentage is legitimate INSIDE the parenthetical -- those
    are levels, and they are what makes the claim reproducible."""
    out, depth = [], 0
    for ch in headline:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _real_book_cases():
    """The live published book if it is on disk, so this control has the real
    population as its subject and not only a fixture."""
    import tools.generate_case_study_recommender as gcs
    if not gcs.SAMPLE_PATH.exists() or not (gcs.CUSTOMERS_DIR / "_index.json").exists():
        return []
    sample = json.loads(gcs.SAMPLE_PATH.read_text())
    return build(gcs._households(), sample.get("customers") or {})


def _synthetic_cases():
    """Drives BOTH defective slots with data shaped like the live book: an I&C
    account at the company's 0.95 estimate ceiling against a ~3% realised
    probability, and a never-responding household whose true satisfaction fell.
    Without this the control would be silent on a machine with no run on disk."""
    by_base = dict()
    # A decoy with real event density, or the "Most eventful journey" slot --
    # which runs first and takes the max over an all-zero pool -- consumes the
    # household the divergence slot needs and this fixture goes silent.
    by_base["C7"] = _customer(
        "C7", "C7",
        timeline=[{"type": "renewed", "date": str(y) + "-01-01"} for y in range(2016, 2026)],
    )
    by_base["C_IC1"] = _customer("C_IC1", "C_IC1", segment="I&C")
    by_base["C_IC2"] = _customer("C_IC2", "C_IC2", segment="I&C")
    sample = {
        "C_IC1": {"churn_accuracy_by_renewal": [
            {"term_start": "2018-01-31", "sim_churn_probability": 0.0323,
             "company_churn_estimate": 0.95, "churn_estimate_error_pct": 28.4118},
        ]},
        "C_IC2": {"feedback_survey_history": [
            {"term_start": "2019-01-31", "true_satisfaction": 0.6382,
             "csat_responded": False, "nps_responded": False},
            {"term_start": "2024-06-28", "true_satisfaction": 0.5166,
             "csat_responded": False, "nps_responded": False},
        ]},
    }
    return build(by_base, sample)


def test_the_control_sees_both_defective_slots():
    """Anti-vacuity: the guards below are worthless if the population they
    scan does not actually contain the two slots that carried the defect."""
    cats = {c["category"] for c in _synthetic_cases()}
    assert "Largest company-vs-SIM churn divergence" in cats
    assert "Silent-middle churn risk" in cats


def test_no_headline_expresses_a_change_or_gap_as_a_bare_percentage():
    cases = _synthetic_cases() + _real_book_cases()
    assert cases
    for c in cases:
        clause = _clause_outside_parentheses(c["headline"])
        if not any(w in clause.lower() for w in _CHANGE_WORDS):
            continue
        assert "%" not in clause, (
            "case '" + c["category"] + "' states a change or gap as a bare "
            "percentage: " + repr(c["headline"]) + " -- a difference between "
            "two levels must be published in percentage points (module unit "
            "doctrine); a bare % there reads as a relative change."
        )


def test_the_divergence_headline_gap_is_reproducible_from_its_own_two_levels():
    """The second direction, and the one that stops the guard above from being
    satisfied by deleting every number: the points figure a reader is shown
    must equal the difference of the two levels shown beside it. Tolerance is
    one rounding step -- two independently-rounded one-decimal levels admit at
    most 0.1 of drift in their difference, and more than that means the figure
    is genuinely not reproducible from what was printed."""
    import re
    cases = _synthetic_cases() + _real_book_cases()
    checked = set()
    for c in cases:
        h = c["headline"]
        points = [float(v) for v in re.findall(r"([\d.]+) percentage points", h)]
        # The slots that CARRIED the defect must publish the quantity, not just
        # avoid a bare %: satisfying the guard above by deleting every number
        # is the fail-open this direction exists to kill, and counting cases
        # rather than naming them let one slot stand for both.
        assert points or c["category"] not in _QUANTIFIED_SLOTS, (
            "case '" + c["category"] + "' states a gap with no figure at all: "
            + repr(h) + " -- the guard against a bare percentage must not be "
            "satisfiable by publishing no quantity"
        )
        if not points:
            continue
        levels = [float(v) for v in re.findall(r"([\d.]+)%", h)]
        assert len(levels) >= 2, (
            "case '" + c["category"] + "' publishes a points figure with fewer "
            "than two levels to reproduce it from: " + repr(h)
        )
        for p in points:
            best = min(abs(abs(a - b) - p) for a in levels for b in levels)
            assert best <= 0.1 + 1e-9, (
                "case '" + c["category"] + "' publishes " + str(p) + " points "
                "that no pair of its own printed levels " + str(levels) +
                " reproduces: " + repr(h)
            )
        checked.add(c["category"])
    assert checked >= _QUANTIFIED_SLOTS, (
        "the reproducibility check never reached " + str(_QUANTIFIED_SLOTS - checked)
        + " -- a control that counts cases instead of naming slots lets one "
        "slot stand for both"
    )


def test_the_module_exposes_no_shared_bare_percentage_formatter():
    """The root cause was ONE formatter serving a level, a ratio and a
    difference. Reintroducing it fails here by name."""
    import tools.generate_case_study_recommender as gcs
    assert not hasattr(gcs, "_fmt_pct"), (
        "_fmt_pct is back: a single bare-percentage formatter is what let a "
        "ratio and a difference be published in the same units as a level"
    )


def test_gap_points_ranks_by_divergence_not_by_one_over_the_denominator():
    """The ranking half. Shaped on the real C9 case: the renewal with the far
    larger relative error is the one with the SMALLER actual gap, because the
    ratio divides by the sim probability."""
    small_gap_big_ratio = {
        "term_start": "2024-06-29", "sim_churn_probability": 0.0902,
        "company_churn_estimate": 0.1402, "churn_estimate_error_pct": 0.554,
    }
    big_gap_small_ratio = {
        "term_start": "2023-06-30", "sim_churn_probability": 0.3220,
        "company_churn_estimate": 0.2000, "churn_estimate_error_pct": -0.379,
    }
    assert abs(small_gap_big_ratio["churn_estimate_error_pct"]) > abs(
        big_gap_small_ratio["churn_estimate_error_pct"]
    ), "fixture no longer has the two keys disagreeing -- the test is vacuous"
    assert _gap_points(big_gap_small_ratio) > _gap_points(small_gap_big_ratio)

    sample = {"C9": {"churn_accuracy_by_renewal": [small_gap_big_ratio, big_gap_small_ratio]}}
    assert _max_divergence(sample, "C9")["term_start"] == "2023-06-30"


def test_gap_points_fails_closed_on_a_missing_level():
    """churn_estimate_error_pct is documented nullable upstream; a renewal
    missing a level must be skipped, not crash the ranking or rank as zero."""
    assert _gap_points({"sim_churn_probability": None, "company_churn_estimate": 0.5}) is None
    assert _gap_points({"company_churn_estimate": 0.5}) is None
    assert _gap_points(None) is None
    sample = {"C1": {"churn_accuracy_by_renewal": [
        {"term_start": "2016-12-31", "sim_churn_probability": None, "company_churn_estimate": None},
    ]}}
    assert _max_divergence(sample, "C1") is None


def test_pick_excludes_already_used_and_respects_filter():
    scored = [
        {"base": "A", "score": 5, "ok": True},
        {"base": "B", "score": 10, "ok": False},
        {"base": "C", "score": 3, "ok": True},
    ]
    used = set()
    best = _pick(scored, used, lambda c: c["score"], filt=lambda c: c["ok"])
    assert best["base"] == "A"
    assert "A" in used
    best2 = _pick(scored, used, lambda c: c["score"], filt=lambda c: c["ok"])
    assert best2["base"] == "C"


def test_pick_returns_none_when_pool_empty():
    assert _pick([], set(), lambda c: c["score"]) is None


def _customer(cid, base, commodity="electricity", timeline=None, reaction_chain=None, segment="resi"):
    return (cid, dict(
        account_id=cid, base_account_id=base, commodity=commodity, segment=segment,
        timeline=timeline or [], reaction_chain=reaction_chain or [],
    ))


def test_build_selects_distinct_households_per_category():
    by_base = dict()
    by_base["C1"] = _customer(
        "C1", "C1",
        timeline=[{"type": "renewed", "date": str(y) + "-01-01"} for y in range(2016, 2026)],
    )
    c2_timeline = [{"type": "renewed", "date": "2018-01-01"}, {"type": "churned", "date": "2021-01-01"}]
    by_base["C2"] = _customer(
        "C2", "C2",
        timeline=c2_timeline,
        reaction_chain=[{"event_type": "retention_decision", "date": "2020-06-01", "outcome": "retained"}],
    )
    by_base["C3"] = _customer(
        "C3", "C3",
        reaction_chain=[
            {"outcome": "WRITTEN_OFF", "date": "2019-01-01"},
            {"outcome": "WRITTEN_OFF", "date": "2019-06-01"},
        ],
    )
    by_base["C7"] = _customer(
        "C7", "C7",
        timeline=[{"type": "life_event", "date": "2020-01-01", "detail": "New baby", "effect": "income stress low -> high"}],
    )
    by_base["C_IC2"] = _customer("C_IC2", "C_IC2", segment="I&C")

    sample = {"C_IC2": {"churn_accuracy_by_renewal": [
        {"term_start": "2019-12-31", "sim_churn_probability": 0.05, "company_churn_estimate": 0.9, "churn_estimate_error_pct": 17.0},
    ]}}
    cases = build(by_base, sample)
    categories = [c["category"] for c in cases]
    assert "Most eventful journey" in categories
    assert "Largest company-vs-SIM churn divergence" in categories
    assert "Retention save, then churned anyway" in categories
    assert "Heaviest arrears cascade" in categories
    assert "Notable life event" in categories
    for c in cases:
        assert "acc" in c["link"] and "tab" in c["link"]
    # every category picked a distinct household
    assert len({c["base_account_id"] for c in cases}) == len(cases)


def test_generate_skips_when_inputs_missing(tmp_path, monkeypatch):
    import tools.generate_case_study_recommender as gcs
    monkeypatch.setattr(gcs, "SAMPLE_PATH", tmp_path / "no_sample.json")
    monkeypatch.setattr(gcs, "CUSTOMERS_DIR", tmp_path / "no_dir")
    assert generate() == 0


def test_generate_end_to_end_writes_case_studies_json(tmp_path, monkeypatch):
    import tools.generate_case_study_recommender as gcs

    cust_dir = tmp_path / "customers"
    cust_dir.mkdir()
    (cust_dir / "_index.json").write_text(json.dumps(["C1"]))
    (cust_dir / "C1.json").write_text(json.dumps(dict(
        account_id="C1", base_account_id="C1", commodity="electricity", segment="resi",
        timeline=[{"type": "renewed", "date": "2018-01-01"}],
        reaction_chain=[],
    )))

    sample_path = tmp_path / "customer_sample.json"
    sample_path.write_text(json.dumps(dict(
        meta=dict(generated_at="2026-01-01T00:00:00Z", git_commit="abc123"),
        customers=dict(C1=dict(churn_accuracy_by_renewal=[])),
    )))

    out_path = tmp_path / "case_studies.json"
    monkeypatch.setattr(gcs, "CUSTOMERS_DIR", cust_dir)
    monkeypatch.setattr(gcs, "SAMPLE_PATH", sample_path)
    monkeypatch.setattr(gcs, "OUT_PATH", out_path)

    count = gcs.generate()
    assert count == 1
    out = json.loads(out_path.read_text())
    assert out["meta"]["household_count"] == 1
    assert out["meta"]["git_commit"] == "abc123"
    assert out["cases"][0]["category"] == "Most eventful journey"
