"""C12_channel_attribution_analytics -- unit + coupled-gap wiring tests.

Two layers:
  1. The twin computes the NAIVE DD business case from OBSERVABLES only and is
     STRUCTURALLY capable of the confound error -- it does NOT secretly correct
     for selection (unit tests + a direct no-de-confounding proof).
  2. The W2_10 <-> C12 coupled gap is REAL, not theatre: the gap is non-degenerate,
     deterministic, caused by the confound (perfect causal recovery collapses it to
     0), and fires on its named mutation. Per CLAUDE.md R15: a control that cannot
     fail is worse than none.

The harness (tools.couple_w2_10_c12) may import simulation.*; this test imports it
to exercise the LIVE coupled loop, but the twin under test (saas.channel_attribution)
imports nothing from the SIM -- asserted directly below.
"""
from __future__ import annotations

import pathlib

import pytest

from saas.channel_attribution import (
    DIRECT_DEBIT,
    ChannelObservation,
    analyse_ingredients,
    analyse_observations,
    make_observations,
)
from background.gap_metric import attribution_gap


# ---------------------------------------------------------------------------
# Layer 1 -- the twin reads observables only and is capable of the error
# ---------------------------------------------------------------------------

def test_twin_imports_nothing_from_the_sim():
    """The wall, mechanically: the twin's source must not import simulation/sim."""
    src = pathlib.Path("saas/channel_attribution.py").read_text(encoding="utf-8")
    for banned in ("import simulation", "from simulation", "import sim.",
                   "from sim.", "from sim import"):
        assert banned not in src, f"twin illegally references the SIM: {banned!r}"


def test_delta_naive_is_the_observed_arrears_difference_credited_to_dd():
    # 10 DD (2 arrears -> 0.2), 10 non-DD (5 arrears -> 0.5).
    obs = (
        [ChannelObservation(DIRECT_DEBIT, i < 2) for i in range(10)]
        + [ChannelObservation("standard_credit", i < 5) for i in range(10)]
    )
    r = analyse_observations(obs)
    assert r.arrears_rate_dd == pytest.approx(0.2)
    assert r.arrears_rate_non_dd == pytest.approx(0.5)
    assert r.delta_naive == pytest.approx(0.3)
    # The naive method credits the WHOLE observed difference to the DD channel.
    assert r.attributed_to_dd == r.delta_naive


def test_ingredients_and_observations_paths_agree():
    obs = (
        [ChannelObservation(DIRECT_DEBIT, i < 3) for i in range(20)]
        + [ChannelObservation("prepayment", i < 7) for i in range(15)]
    )
    from_obs = analyse_observations(obs)
    ingredients = {"n_dd": 20, "n_non_dd": 15, "arrears_dd": 3, "arrears_non_dd": 7}
    from_ing = analyse_ingredients(ingredients)
    assert from_ing.delta_naive == pytest.approx(from_obs.delta_naive)
    assert from_ing.dd_share == pytest.approx(from_obs.dd_share)


def test_any_non_dd_channel_folds_into_the_non_dd_cohort():
    # standard_credit AND prepayment both count as "not DD" (the company's binary).
    obs = [
        ChannelObservation(DIRECT_DEBIT, False),
        ChannelObservation("standard_credit", True),
        ChannelObservation("prepayment", True),
    ]
    r = analyse_observations(obs)
    assert r.n_dd == 1 and r.n_non_dd == 2


def test_discovery_hook_flags_but_never_corrects():
    # DD looks better -> the caveat fires, but delta_naive is UNCHANGED by it.
    obs = (
        [ChannelObservation(DIRECT_DEBIT, i < 1) for i in range(10)]     # 0.1
        + [ChannelObservation("standard_credit", i < 4) for i in range(10)]  # 0.4
    )
    r = analyse_observations(obs)
    assert r.confound_flag is True
    assert "CAVEAT" in r.confound_note and "not corrected" in r.confound_note
    # The headline figure is still the raw naive difference (no de-confounding).
    assert r.delta_naive == pytest.approx(0.3)
    assert r.attributed_to_dd == pytest.approx(0.3)


def test_no_caveat_when_dd_shows_no_advantage():
    obs = (
        [ChannelObservation(DIRECT_DEBIT, i < 5) for i in range(10)]     # 0.5
        + [ChannelObservation("standard_credit", i < 2) for i in range(10)]  # 0.2
    )
    r = analyse_observations(obs)
    assert r.delta_naive == pytest.approx(-0.3)
    assert r.confound_flag is False


def test_make_observations_copies_only_the_two_observables():
    rows = [
        {"payment_channel": DIRECT_DEBIT, "had_arrears": True,
         "organisation": 0.9, "income_decile": 8},   # hidden fields present in the row
    ]
    obs = make_observations(rows)
    assert obs[0].payment_channel == DIRECT_DEBIT and obs[0].had_arrears is True
    # The observation dataclass has no slot for the hidden fields -- they cannot ride along.
    assert not hasattr(obs[0], "organisation")


# ---------------------------------------------------------------------------
# Layer 2 -- the W2_10 <-> C12 coupled gap is real (import guarded: needs the SIM)
# ---------------------------------------------------------------------------

run = pytest.importorskip("tools.couple_w2_10_c12")


def test_coupled_gap_is_non_degenerate():
    result, extras = run.measure(n_customers=20000)
    assert result.gap is not None
    assert 0.0 < result.gap < 1.0
    # The naive method OVER-credits DD: delta_naive strictly exceeds the causal truth.
    assert extras["delta_naive"] > extras["delta_true"] > 0.0
    # Substantial fraction of the business case is confound (not tuned to a target;
    # a wide sanity band, R12 -- the value is whatever the frozen curriculum yields).
    assert 0.2 < result.gap < 0.8
    # The company raised the honest caveat but did not act on it.
    assert extras["confound_flag"] is True


def test_coupled_gap_is_deterministic():
    r1, e1 = run.measure(n_customers=8000)
    r2, e2 = run.measure(n_customers=8000)
    assert r1.gap == r2.gap
    assert e1["delta_naive"] == e2["delta_naive"]
    assert e1["delta_true"] == e2["delta_true"]


def test_gap_is_caused_by_the_confound_not_a_tautology():
    """Independence proof (R15). The measured gap exists because delta_naive is the
    naive (confounded) figure. If the company had somehow recovered the causal truth
    (delta_naive == delta_true), the attribution gap collapses to exactly 0 -- so the
    live non-zero gap is caused by the selection confound, not by the two sides
    trivially agreeing."""
    _, extras = run.measure(n_customers=20000)
    dt = extras["delta_true"]
    # Perfect causal recovery -> gap 0 (structurally unreachable through the wall).
    perfect = attribution_gap(dt, dt)
    assert perfect.raw_gap == 0.0
    assert perfect.gap == 0.0
    # The naive company differs from the truth -> a real, non-zero gap.
    assert extras["delta_naive"] != pytest.approx(dt)


def test_twin_does_not_secretly_de_confound():
    """The company's delta_naive must equal the OBSERVATIONAL cohort difference and
    must NOT have been quietly pulled toward the hidden causal truth. We recompute
    the naive figure independently from the observables and require an exact match,
    AND require it to differ materially from delta_true (proof no correction ran)."""
    from simulation.dd_attribution import (
        draw_dd_cohort,
        population_naive_channel_effect,
    )
    profiles = draw_dd_cohort(20000)
    obs = [ChannelObservation(p.payment_channel, p.had_arrears) for p in profiles]
    company = analyse_observations(obs)
    # Independent observational recomputation (world-side demonstration) -- exact match.
    assert company.delta_naive == pytest.approx(
        population_naive_channel_effect(profiles), abs=1e-12
    )
    # And it is NOT the causal truth -- no de-confounding happened.
    from simulation.dd_attribution import population_true_treatment_effect
    assert company.delta_naive > population_true_treatment_effect(profiles) + 0.01


def test_mutation_a_de_confounded_company_would_collapse_the_gap():
    """R15 mutation: had the twin (wrongly, for this atom) returned the causal
    effect as its headline, the gap would be 0. It does not -- so the control fires
    on the real naive figure and would go silent on the de-confounded mutant."""
    _, extras = run.measure(n_customers=20000)
    live = attribution_gap(extras["delta_naive"], extras["delta_true"])
    mutant = attribution_gap(extras["delta_true"], extras["delta_true"])
    assert live.gap > 0.1          # the naive company: real gap
    assert mutant.gap == 0.0       # the de-confounded mutant: gap gone


def test_ledger_write_matches_reader_contract(tmp_path):
    from background import coupled_triad as ct
    from background import gap_metric as gm
    result, _ = run.measure(n_customers=5000)
    path = tmp_path / "coupled_gap_ledger.json"
    ledger = gm.write_gap_entry(
        run.WORLD_ATOM_ID, run.TWIN_ATOM_ID, result,
        measured_at="2026-07-13T00:00:00Z", run_git_commit="cafe",
        ledger_path=path,
    )
    entry = ledger[run.WORLD_ATOM_ID]
    assert entry["twin_atom_id"] == run.TWIN_ATOM_ID
    assert isinstance(entry["gap"], float)
    reloaded = ct.load_gap_ledger(path)
    assert ct.gap_measured(run.WORLD_ATOM_ID, reloaded) is True


def test_ledger_write_preserves_existing_entries(tmp_path):
    """read-merge-write: writing the W2_10 pair must not clobber another pair's
    entry already in the ledger."""
    from background import gap_metric as gm
    path = tmp_path / "coupled_gap_ledger.json"
    path.write_text('{"W2_6_sme_distress_twin": {"twin_atom_id": "C8", "gap": 0.4}}',
                    encoding="utf-8")
    result, _ = run.measure(n_customers=3000)
    ledger = gm.write_gap_entry(
        run.WORLD_ATOM_ID, run.TWIN_ATOM_ID, result, ledger_path=path,
    )
    assert "W2_6_sme_distress_twin" in ledger      # preserved
    assert run.WORLD_ATOM_ID in ledger             # added
