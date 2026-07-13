"""W2_10_dd_attribution_confound -- hidden DD selection-bias trap (world side).

Covers the atom's headline requirements:
  * THE CONFOUND: a naive channel-attribution (delta_naive, observables only)
    OVER-CREDITS DD relative to the genuine causal effect (delta_true, answer key)
    -- delta_naive > delta_true > 0 with a materially non-zero confound share.
  * SELECTION is real & coupled: the DD cohort is systematically more organised /
    higher income decile (W2_4 coupling) -- the back-door path that makes the
    confound consistent, not free-floating.
  * The hidden/observable SEAM: the company sees only payment_channel + had_arrears;
    organisation / counterfactuals / income decile are the answer key.
  * RNG SUBSTREAM ISOLATION (C-S2, the 01:09Z incident): advancing this subsystem
    leaves the live siblings (population_draw, life_events, household_budget,
    sme_distress) BYTE-IDENTICAL and never touches the global ``random`` module.
  * DETERMINISTIC REPLAY (C-S2) on (customer_id, seed), across processes.
  * Anchored plausibility (Ofgem DD share, Citizens Advice arrears scale) -- never
    fabricated, DIAGNOSTIC bands not targets (R12/R13).
  * Epistemic wall: pure sim, no company/saas import.
"""
from __future__ import annotations

import hashlib
import random
from pathlib import Path

import pytest

from simulation import dd_attribution as dd

REPO_ROOT = Path(__file__).resolve().parents[2]


def _cohort(n=6000, seed=1):
    return dd.draw_dd_cohort(n, seed=seed)


# -- 1. Substream contract ----------------------------------------------------

def test_substream_names_are_unique():
    assert len(dd._SUBSTREAMS) == len(set(dd._SUBSTREAMS))


def test_substream_is_deterministic():
    a = [dd._substream(999, "selection").random() for _ in range(10)]
    b = [dd._substream(999, "selection").random() for _ in range(10)]
    assert a == b


def test_substream_value_is_stable_across_processes():
    # sha256-derived, NOT Python's per-process-salted hash(): a regression to a
    # salted seed would break C-S2 deterministic replay and fail this exact value.
    key = "W2_10_dd_attribution::selection::12345".encode("utf-8")
    expected_seed = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    assert dd._substream(12345, "selection").random() == \
        random.Random(expected_seed).random()


def test_distinct_substreams_produce_different_sequences():
    a = [dd._substream(555, "selection").random() for _ in range(20)]
    b = [dd._substream(555, "arrears_realisation").random() for _ in range(20)]
    assert a != b


def test_base_seed_from_customer_id_is_stable_and_process_independent():
    expected = int(hashlib.md5(b"C7").hexdigest()[:8], 16)
    assert dd._base_seed_for("C7", None) == expected
    assert dd._base_seed_for("C7", 42) == 42  # explicit seed passes through


# -- 2. THE headline C-S2 guarantee: this substream can't shift a sibling -----

def test_new_substream_does_not_shift_existing_substream():
    base = 424242
    before = [dd._substream(base, "selection").random() for _ in range(50)]
    _ = [dd._substream(base, "some_future_mechanism").random() for _ in range(500)]
    after = [dd._substream(base, "selection").random() for _ in range(50)]
    assert before == after


def test_every_named_substream_is_invariant_to_a_new_one_being_drained():
    base = 7788
    reference = {
        name: [dd._substream(base, name).random() for _ in range(30)]
        for name in dd._SUBSTREAMS
    }
    _ = [dd._substream(base, "hypothetical_new_mechanism").random() for _ in range(1000)]
    for name in dd._SUBSTREAMS:
        assert [dd._substream(base, name).random() for _ in range(30)] == reference[name]


def test_advancing_dd_does_not_perturb_global_random():
    random.seed(12345)
    before = [random.random() for _ in range(20)]
    random.seed(12345)
    _ = _cohort(800)  # heavy generation
    after = [random.random() for _ in range(20)]
    assert before == after


def test_advancing_dd_leaves_population_draw_byte_identical():
    from simulation import population_draw as pdraw
    baseline = pdraw.draw_population(base_seed=808)
    _ = _cohort(1500)
    _ = [dd.generate_dd_attribution("Z", seed=s) for s in range(100)]
    assert pdraw.draw_population(base_seed=808) == baseline


def test_advancing_dd_leaves_life_events_byte_identical():
    from simulation.household import make_household
    from simulation.life_events import generate_life_events
    hh = make_household(
        {"customer_id": "C1", "home_type": "suburban_semi",
         "epc_rating": "C", "segment": "resi"}
    )
    baseline = generate_life_events(hh, 2016, 2025)
    _ = _cohort(1500)
    assert generate_life_events(hh, 2016, 2025) == baseline


def test_advancing_dd_leaves_household_budget_byte_identical():
    """W2_4 is READ (coupled) by this module -- proving the coupling never mutates
    or shifts the budget twin's own draw for the same or any other customer."""
    from simulation.household_budget import draw_household_budget
    baseline = draw_household_budget("BUDGET_CUST_42")
    _ = _cohort(1500)
    _ = [dd.generate_dd_attribution(f"K{i}", seed=i) for i in range(200)]
    assert draw_household_budget("BUDGET_CUST_42") == baseline


def test_advancing_dd_leaves_sme_distress_byte_identical():
    from simulation.sme_distress import generate_business_distress
    baseline = generate_business_distress("B9", "SME", 2016, 2025, seed=9)
    _ = _cohort(1200)
    assert generate_business_distress("B9", "SME", 2016, 2025, seed=9) == baseline


# -- 3. Deterministic replay (C-S2) -------------------------------------------

def test_deterministic_replay_identical_profile_same_seed():
    a = dd.generate_dd_attribution("C42", seed=13)
    b = dd.generate_dd_attribution("C42", seed=13)
    assert a == b  # frozen dataclass compares by value


def test_deterministic_replay_survives_intervening_global_rng_use():
    a = dd.generate_dd_attribution("C77")
    random.seed()
    _ = [random.random() for _ in range(1000)]
    b = dd.generate_dd_attribution("C77")
    assert a == b


def test_cohort_is_reproducible_as_a_unit():
    assert _cohort(300, seed=5) == _cohort(300, seed=5)


def test_different_customers_generally_differ():
    prof = _cohort(80)
    shapes = {(p.payment_channel, round(p.organisation, 3), p.had_arrears) for p in prof}
    assert len(shapes) > 1


# -- 4. THE CONFOUND: naive over-credits DD relative to the causal truth -------

def test_naive_over_credits_dd_vs_true_treatment_effect():
    """delta_naive (observed arrears-rate gap by channel) OVER-STATES the genuine
    causal effect delta_true (the do-operator) because the DD cohort is selected
    clean -- both positive, naive strictly larger. This IS the trap."""
    prof = _cohort(8000)
    delta_true = dd.population_true_treatment_effect(prof)
    delta_naive = dd.population_naive_channel_effect(prof)
    assert delta_true > 0.0, "DD should have a genuine (small) causal benefit"
    assert delta_naive > delta_true, "naive analytics must over-credit DD (the confound)"


def test_confound_share_is_materially_nonzero():
    """The gap = |delta_naive - delta_true| / |delta_naive| = the fraction of the
    DD business case that is confound artefact. A DIAGNOSTIC sanity band (R12),
    not a tuned target -- just proves the trap is real, not degenerate."""
    prof = _cohort(8000)
    delta_true = dd.population_true_treatment_effect(prof)
    delta_naive = dd.population_naive_channel_effect(prof)
    confound_share = abs(delta_naive - delta_true) / abs(delta_naive)
    assert 0.15 < confound_share < 0.75, f"confound share {confound_share:.3f} implausible"


def test_dd_cohort_has_lower_observed_arrears():
    """The surface correlation a real supplier sees (and mis-reads): DD customers
    observably fall into arrears less often."""
    prof = _cohort(8000)
    dd_grp = [p for p in prof if p.on_dd]
    nd_grp = [p for p in prof if not p.on_dd]
    rate_dd = sum(p.had_arrears for p in dd_grp) / len(dd_grp)
    rate_nd = sum(p.had_arrears for p in nd_grp) / len(nd_grp)
    assert rate_dd < rate_nd


def test_selection_is_real_dd_cohort_more_organised():
    """The hidden mechanism behind the surface correlation: the DD cohort is
    systematically MORE ORGANISED -- the selection that the naive reading ignores."""
    prof = _cohort(8000)
    dd_grp = [p for p in prof if p.on_dd]
    nd_grp = [p for p in prof if not p.on_dd]
    mean_org_dd = sum(p.organisation for p in dd_grp) / len(dd_grp)
    mean_org_nd = sum(p.organisation for p in nd_grp) / len(nd_grp)
    assert mean_org_dd > mean_org_nd


def test_coupling_dd_cohort_higher_income_decile():
    """W2_4 coupling is load-bearing: DD selection correlates with the SAME hidden
    affordability the budget twin draws, so the DD cohort skews to higher income
    deciles -- one coherent hidden person across the two twins."""
    prof = _cohort(8000)
    dd_grp = [p for p in prof if p.on_dd]
    nd_grp = [p for p in prof if not p.on_dd]
    mean_dec_dd = sum(p.income_decile for p in dd_grp) / len(dd_grp)
    mean_dec_nd = sum(p.income_decile for p in nd_grp) / len(nd_grp)
    assert mean_dec_dd > mean_dec_nd


def test_delta_true_equals_mean_individual_treatment_effect():
    prof = _cohort(500)
    expected = sum(p.individual_treatment_effect() for p in prof) / len(prof)
    assert dd.population_true_treatment_effect(prof) == pytest.approx(expected)


# -- 5. The hidden / observable SEAM ------------------------------------------

def test_individual_treatment_effect_is_nonnegative_and_from_counterfactuals():
    p = dd.generate_dd_attribution("SEAM1", seed=3)
    assert p.individual_treatment_effect() >= 0.0
    assert p.counterfactual_arrears_prob(True) == p.true_arrears_prob_dd
    assert p.counterfactual_arrears_prob(False) == p.true_arrears_prob_non_dd
    # DD counterfactual is always the cleaner one (genuine treatment benefit).
    assert p.true_arrears_prob_dd <= p.true_arrears_prob_non_dd


def test_observable_fields_do_not_expose_the_cause():
    """The only observables a naive channel-attribution reads are the channel and
    the realised arrears flag -- never the counterfactual, organisation, or decile."""
    p = dd.generate_dd_attribution("SEAM2", seed=7)
    assert p.payment_channel in (dd.DIRECT_DEBIT, dd.NON_DD)
    assert isinstance(p.had_arrears, bool)
    # naive_ingredients touches ONLY observable fields (channel + had_arrears).
    ing = dd.naive_ingredients(_cohort(200))
    assert set(ing) == {"n_dd", "n_non_dd", "arrears_dd", "arrears_non_dd", "dd_share"}


def test_data_regime_is_synthetic():
    assert dd.generate_dd_attribution("R1", seed=1).data_regime == "synthetic"


# -- 6. Anchored plausibility (real UK figures, never fabricated) -------------

def test_dd_share_tracks_the_ofgem_anchor():
    """Ofgem 2026: ~74% of consumers pay by direct debit. DIAGNOSTIC band (R12)."""
    prof = _cohort(8000)
    dd_share = dd.naive_ingredients(prof)["dd_share"]
    assert 0.66 < dd_share < 0.82, f"DD share {dd_share:.3f} off the Ofgem anchor"


def test_population_arrears_rate_is_plausible():
    """Citizens Advice: ~5.3m people (~19% of GB households) in energy debt. The
    realised population arrears rate should land in a plausible band around that
    scale (R12 sanity flag, not a target)."""
    prof = _cohort(8000)
    rate = sum(p.had_arrears for p in prof) / len(prof)
    assert 0.08 < rate < 0.25, f"population arrears rate {rate:.3f} implausible"


def test_treatment_mult_is_a_genuine_but_bounded_benefit():
    # DD genuinely helps (mult < 1) but is not the whole story (mult not tiny).
    assert 0.70 < dd._DD_TREATMENT_MULT < 1.00
    assert dd._TARGET_DD_SHARE == pytest.approx(0.74, abs=0.01)


def test_arrears_prob_monotonic_in_organisation():
    """Structural sanity: more organised => lower arrears prob, on either channel."""
    for on_dd in (True, False):
        probs = [dd._arrears_prob(o / 10, on_dd) for o in range(11)]
        assert probs == sorted(probs, reverse=True)


# -- 7. Epistemic wall --------------------------------------------------------

def test_module_does_not_import_company_or_saas():
    src = (REPO_ROOT / "simulation" / "dd_attribution.py").read_text()
    for banned in ("import company", "from company", "import saas", "from saas"):
        assert banned not in src, f"epistemic-wall violation: '{banned}' in dd_attribution.py"
