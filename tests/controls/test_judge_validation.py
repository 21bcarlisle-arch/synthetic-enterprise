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


# ── R15 FAIL-OPEN: a thin record must not read as a measured-clean judge ──────
def test_thin_record_escapes_measurement_not_a_clean_bill(_isolated_ledger):
    """THE fail-open mutation for this metric: one PASS with no post-close defect
    computes error_rate 0.0. If that 0.0 were reported as a clean judge, an
    unmeasured organ would silently pass -- the R15 FAIL-OPEN pattern. The metric
    must instead flag `escapes_measurement=True`: 0.0 over one verdict is
    UNMEASURED, not perfect."""
    tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS,
                      evaluator_name="phase-close-evaluator", subject="commit_thin")
    j = jv.outcome_error_rates()["per_judge"]["phase-close-evaluator"]
    assert j["error_rate"] == 0.0          # the raw computed signal
    assert j["escapes_measurement"] is True  # ... but honestly flagged as unmeasured


def test_error_rate_is_measured_only_after_enough_passes(_isolated_ledger):
    """The floor mirrors autonomy_level's >=3: a genuinely-measured 0.0 (a judge
    that passed >= MIN times and reality never disagreed) is a real clean bill and
    must NOT carry the escapes_measurement flag -- so the flag discriminates
    unmeasured-thin from measured-clean, it is not always-on theatre."""
    for i in range(jv.MIN_PASSES_FOR_MEASURED_RATE):
        tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS,
                          evaluator_name="cold-eyes-walk", subject=f"commit_m{i}")
    j = jv.outcome_error_rates()["per_judge"]["cold-eyes-walk"]
    assert j["passes"] == jv.MIN_PASSES_FOR_MEASURED_RATE
    assert j["error_rate"] == 0.0
    assert j["escapes_measurement"] is False  # measured, and clean


def test_a_measured_judge_whose_pass_later_fails_shows_a_real_error_rate(_isolated_ledger):
    """OUTCOME-test (R15 extension): the strongest validation. A judge with a
    measured record whose PASS later proves defective must show a non-zero error
    rate -- the metric FIRES on the judge's own named failure (a pass that later
    failed), exactly as a mutation test fires a mechanical control."""
    for i in range(4):
        tl.record_verdict(tl.TaskClass.PRICING, tl.Verdict.PASS,
                          evaluator_name="epistemic-verifier", subject=f"px_{i}")
    tl.record_post_close_defect("px_0", 1, notes="later-found pricing defect")
    j = jv.outcome_error_rates()["per_judge"]["epistemic-verifier"]
    assert j["passes"] == 4
    assert j["passes_with_later_defect"] == 1
    assert j["error_rate"] == 0.25          # 1 of 4 passes later proved defective
    assert j["escapes_measurement"] is False


# ── measurement coverage: which verdict-organs escape measurement (forbidden) ──
def test_measurement_coverage_names_the_unmeasured_organ(_isolated_ledger):
    tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS,
                      evaluator_name="phase-close-evaluator", subject="commit_u1")
    cov = jv.measurement_coverage()
    assert cov["unmeasured_judges"] == ["phase-close-evaluator"]
    assert cov["measured_judges"] == []
    assert cov["coverage"] == 0.0          # 100% of verdict-organs escape measurement
    assert cov["all_measured"] is False


def test_measurement_coverage_all_measured_when_every_judge_has_enough(_isolated_ledger):
    for i in range(jv.MIN_PASSES_FOR_MEASURED_RATE):
        tl.record_verdict(tl.TaskClass.SITE_PRESENTATION, tl.Verdict.PASS,
                          evaluator_name="cold-eyes-walk", subject=f"s{i}")
    cov = jv.measurement_coverage()
    assert cov["measured_judges"] == ["cold-eyes-walk"]
    assert cov["coverage"] == 1.0
    assert cov["all_measured"] is True


def test_measurement_coverage_is_none_on_empty_record(_isolated_ledger):
    cov = jv.measurement_coverage()
    assert cov["coverage"] is None
    assert cov["all_measured"] is False    # nothing measured is NOT all-clear


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


def test_summary_surfaces_measurement_coverage(_isolated_ledger):
    """The forbidden-state must reach the published surface, not just the library:
    summary() carries measurement_coverage so a reader sees which verdict-organs
    escape measurement."""
    tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS,
                      evaluator_name="phase-close-evaluator", subject="commit_s1")
    s = jv.summary()
    assert "measurement_coverage" in s
    assert s["measurement_coverage"]["unmeasured_judges"] == ["phase-close-evaluator"]


def test_published_json_is_serialisable():
    # the site publisher must be able to write it
    json.dumps(jv.summary())


# ── R11: the PUBLISHED site value must reflect the REAL computed rate ─────────
def test_published_site_data_reflects_the_real_computed_rate(tmp_path, monkeypatch):
    """R11 (verify to the rendered value): the generator writes site/data, and the
    number it publishes must EQUAL what the library computes from the same ledger
    -- not a stale or hand-edited figure. We seed a ledger with a real
    pass-that-later-failed, run the actual generator against a temp output, then
    assert the on-disk published error_rate and coverage match a fresh
    computation over that same ledger."""
    import importlib
    gen = importlib.import_module("tools.generate_judge_validation_data")

    ledger = tmp_path / "trust_ledger.json"
    out = tmp_path / "judge_validation.json"
    monkeypatch.setattr(tl, "LEDGER_PATH", ledger)
    monkeypatch.setattr(gen, "OUT_PATH", out)

    for i in range(4):
        tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS,
                          evaluator_name="phase-close-evaluator", subject=f"b{i}")
    tl.record_post_close_defect("b0", 1)

    gen.main()

    published = json.loads(out.read_text())
    computed = jv.outcome_error_rates()  # same (monkeypatched) ledger
    assert published["outcome_correlation"]["overall"]["error_rate"] == \
        computed["overall"]["error_rate"] == 0.25
    assert published["measurement_coverage"]["measured_judges"] == \
        jv.measurement_coverage()["measured_judges"] == ["phase-close-evaluator"]
    assert published["measurement_coverage"]["coverage"] == 1.0


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
