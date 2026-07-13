"""Tests for the JUDGE-VALIDATION harness (JUDGING_THE_JUDGES.md Part 1, P1).

The judges' verdict QUALITY is un-mutation-testable, so it is OUTCOME-tested.
These tests exercise the four approaches on real/synthetic data, and assert the
gold set is grounded in the director's actual Expert-Hour catches. They are
DETERMINISTIC (no real Opus / no network) -- the real-Opus consistency and
independence samples accrue live, exactly as the module documents.
"""
import json

import pytest

from background import judge_validation as jv
from background import trust_ledger as tl


# ── APPROACH 1: OUTCOME CORRELATION ──────────────────────────────────────────
@pytest.fixture
def _isolated_ledger(tmp_path, monkeypatch):
    monkeypatch.setattr(tl, "LEDGER_PATH", tmp_path / "trust_ledger.json")
    return tl


def test_outcome_error_rate_is_zero_before_any_defect_is_linked(_isolated_ledger):
    tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS,
                      evaluator_name="phase-close-evaluator", subject="commit_aaa")
    tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS,
                      evaluator_name="phase-close-evaluator", subject="commit_bbb")
    rates = jv.outcome_error_rates()
    j = rates["per_judge"]["phase-close-evaluator"]
    assert j["passes"] == 2
    assert j["passes_with_later_defect"] == 0
    assert j["error_rate"] == 0.0


def test_linkage_attaches_a_later_defect_to_the_pass_that_let_it_through(_isolated_ledger):
    """The minimal linkage the staged doc asks for: a defect found LATER is
    charged back to the PASS verdict on that same subject, and the judge's
    empirical error rate moves as a CONSEQUENCE."""
    tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS,
                      evaluator_name="phase-close-evaluator", subject="commit_ccc")
    tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS,
                      evaluator_name="phase-close-evaluator", subject="commit_ddd")
    # reality later disagrees with the verdict on commit_ccc
    updated = tl.record_post_close_defect("commit_ccc", 1, notes="SME-as-household missed")
    assert updated["defects_found_post_close"] == 1
    assert updated["rework_required"] is True

    rates = jv.outcome_error_rates()
    j = rates["per_judge"]["phase-close-evaluator"]
    assert j["passes"] == 2
    assert j["passes_with_later_defect"] == 1
    assert j["error_rate"] == 0.5  # 1 of 2 passes later proved defective


def test_linkage_refuses_to_charge_a_defect_to_a_judge_that_never_passed(_isolated_ledger):
    tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.NEEDS_WORK,
                      evaluator_name="phase-close-evaluator", subject="commit_eee")
    with pytest.raises(KeyError):
        tl.record_post_close_defect("commit_eee")  # only a NEEDS_WORK exists -> no PASS to charge


def test_outcome_error_rate_is_none_on_empty_record(_isolated_ledger):
    rates = jv.outcome_error_rates()
    assert rates["overall"]["error_rate"] is None  # never claim a rate from nothing


# ── APPROACH 2: CONSISTENCY ───────────────────────────────────────────────────
def test_consistency_flip_rate_zero_when_judge_never_flips():
    assert jv.consistency_flip_rate(["pass", "pass", "pass"])["flip_rate"] == 0.0


def test_consistency_flip_rate_catches_a_noisy_judge():
    r = jv.consistency_flip_rate(["pass", "defect", "pass", "defect"])
    assert r["flip_rate"] == 0.5
    assert r["distinct_verdicts"] == 2


def test_consistency_none_below_two_samples():
    assert jv.consistency_flip_rate(["pass"])["flip_rate"] is None


def test_repeat_invoke_exposes_an_impure_judge():
    seq = iter(["pass", "defect", "pass"])
    verdicts = jv.repeat_invoke(lambda case: next(seq), {"x": 1}, 3)
    assert jv.consistency_flip_rate(verdicts)["flip_rate"] > 0


# ── APPROACH 3: INDEPENDENCE ──────────────────────────────────────────────────
def test_independence_unanimous():
    r = jv.independence_disagreement_rate({"a": "defect", "b": "defect", "c": "defect"})
    assert r["disagreement_rate"] == 0.0
    assert r["unanimous"] is True


def test_independence_flags_a_split_panel():
    r = jv.independence_disagreement_rate({"cold_eyes": "defect", "phase_close": "pass", "naive": "pass"})
    assert r["disagreement_rate"] == pytest.approx(1 / 3, abs=1e-3)
    assert r["majority_verdict"] == "pass"


def test_independence_none_for_single_judge():
    assert jv.independence_disagreement_rate({"only": "pass"})["disagreement_rate"] is None


# ── APPROACH 4: GOLD SET ──────────────────────────────────────────────────────
def test_gold_set_loads_the_four_director_cases():
    cases = jv.load_gold_set()
    ids = {c["case_id"] for c in cases}
    assert {"c6_sme_as_household_vat", "naked_hedging_volatility_leak",
            "bad_debt_consumption_smell_test", "c1_meter_read_mismatch"} <= ids


def test_every_gold_case_is_a_director_catch_with_a_checkable_source():
    for c in jv.load_gold_set():
        assert c["director_verdict"] == "defect", c["case_id"]
        assert c.get("source"), c["case_id"]           # checkable provenance, never fabricated
        assert c.get("defect_class"), c["case_id"]
        assert c.get("the_catch"), c["case_id"]


def test_rubber_stamp_judge_misses_every_director_catch():
    """The load-bearing discrimination: a judge that passes everything scores
    recall 0.0 -- if it ever scored higher, the gold set/scorer is theatre."""
    r = jv.score_judge_against_gold(jv.rubber_stamp_judge)
    assert r["recall"] == 0.0
    assert r["missed"] == r["total_cases"] == 4


def test_oracle_judge_catches_every_director_catch():
    r = jv.score_judge_against_gold(jv.oracle_judge)
    assert r["recall"] == 1.0
    assert r["missed"] == 0


def test_scorer_names_the_specific_misses():
    """A partial judge that only catches VAT: the scorer must NAME the three it
    missed, so a weak judge's blind spots are legible, not just a scalar."""
    def vat_only_judge(case):
        return "defect" if case["case_id"] == "c6_sme_as_household_vat" else "pass"
    r = jv.score_judge_against_gold(vat_only_judge)
    assert r["caught"] == 1
    assert {m["case_id"] for m in r["misses"]} == {
        "naked_hedging_volatility_leak", "bad_debt_consumption_smell_test",
        "c1_meter_read_mismatch"}


# ── the published summary ─────────────────────────────────────────────────────
def test_summary_wires_all_four_approaches_and_the_standing_rule():
    s = jv.summary()
    assert "OUTCOME-tested" in s["standing_rule"]
    assert "outcome_correlation" in s
    assert s["gold_set"]["rubber_stamp_baseline"]["recall"] == 0.0
    assert s["gold_set"]["oracle_ceiling"]["recall"] == 1.0
    assert s["consistency"]["accrues_live"] is True
    assert s["independence"]["accrues_live"] is True


def test_published_json_is_serialisable():
    # the site publisher must be able to write it
    json.dumps(jv.summary())


def test_gold_case_detectable_by_names_real_importable_controls():
    """Where a gold case claims a mechanical control CAN catch its class, that
    control must actually exist and be callable -- links the gold set to the
    CONTROLS_THAT_CANNOT_FAIL / R15 mutation apparatus (test_control_mutation.py
    proves those same controls fire on their named defect). A null means the
    catch is a judgment no mechanical control encodes -- legitimately an
    LLM-judge / director-only case, not a gap."""
    import importlib
    for c in jv.load_gold_set():
        for dotted in (c.get("detectable_by") or []):
            # `dotted` is either a module (e.g. tools.epistemic_verifier) or a
            # module.symbol (e.g. company.compliance.domain_invariants.check_vat).
            try:
                importlib.import_module(dotted)
                continue  # names a real module
            except ModuleNotFoundError:
                pass
            module_name, _, symbol = dotted.rpartition(".")
            mod = importlib.import_module(module_name)
            assert hasattr(mod, symbol), f"{c['case_id']}: {dotted} does not exist"
            assert callable(getattr(mod, symbol)), f"{c['case_id']}: {dotted} not callable"
