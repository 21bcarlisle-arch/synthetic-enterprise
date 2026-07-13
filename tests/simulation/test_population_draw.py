"""Tests for the world-side stochastic population draw (W2_2_population_draw).

Covers the atom's falsifiable success criterion (acquisitions continue through
2025, not stopping dead at 2020) plus the three HARD architectural constraints:
drift-guard on duplicated anchored constants (epistemic wall), RNG substream
isolation (C-S2), and deterministic replay (C-S2).
"""
from __future__ import annotations

import datetime as dt
import random
from pathlib import Path

import pytest

from simulation import population_draw as pd

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Falsifiable success criterion (the FRAME note's own bar)
# ---------------------------------------------------------------------------
def test_acquisitions_continue_through_2025_not_stopping_at_2020():
    """The whole point of the atom: the synthetic book must show acquisitions
    in the 2021-2025 window that the hand-authored cast leaves completely
    empty. Over a spread of seeds, every year 2021..2025 must be reachable and
    the cohort must be non-empty."""
    years_seen = set()
    for seed in range(200):
        for cust in pd.iter_acquisition_events(base_seed=seed):
            year = int(cust.acquisition_date[:4])
            assert 2021 <= year <= 2025
            years_seen.add(year)
    assert years_seen == {2021, 2022, 2023, 2024, 2025}


def test_default_window_never_produces_pre_2021_acquisitions():
    for seed in range(50):
        for cust in pd.draw_population(base_seed=seed):
            assert cust.acquisition_date >= "2021-01-01"
            assert cust.acquisition_date <= "2025-12-31"


def test_customer_ids_are_synthetic_prefixed_and_unique():
    pop = pd.draw_population(base_seed=7, start_year=2021, end_year=2025)
    ids = [c.customer_id for c in pop]
    assert all(cid.startswith("SYN-") for cid in ids)
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# CONSTRAINT 1: drift-guard on duplicated anchored constants (epistemic wall)
# tests/ may import company.* / read docs -- the module itself may not.
# ---------------------------------------------------------------------------
def test_tdcv_bands_do_not_drift_from_domain_invariants():
    from company.compliance import domain_invariants as di

    expected = {
        "electricity": {
            "LOW": (di.TDCV_ELEC_LOW.low, di.TDCV_ELEC_LOW.high),
            "MEDIUM": (di.TDCV_ELEC_MEDIUM.low, di.TDCV_ELEC_MEDIUM.high),
            "HIGH": (di.TDCV_ELEC_HIGH.low, di.TDCV_ELEC_HIGH.high),
        },
        "gas": {
            "LOW": (di.TDCV_GAS_LOW.low, di.TDCV_GAS_LOW.high),
            "MEDIUM": (di.TDCV_GAS_MEDIUM.low, di.TDCV_GAS_MEDIUM.high),
            "HIGH": (di.TDCV_GAS_HIGH.low, di.TDCV_GAS_HIGH.high),
        },
    }
    assert pd.TDCV_BANDS_KWH == expected, (
        "population_draw's duplicated TDCV bands have drifted from "
        "company/compliance/domain_invariants.py -- re-sync them (WALL DISCIPLINE)."
    )


def test_dd_share_does_not_drift_from_assumptions_md():
    text = (REPO_ROOT / "docs" / "market_research" / "ASSUMPTIONS.md").read_text()
    # The exact anchored sentence in ASSUMPTIONS.md (DESNZ QEP June 2026).
    assert "72% of standard electricity customers and 75% of gas customers" in text, (
        "ASSUMPTIONS.md's DD-share anchor sentence changed -- re-verify "
        "DD_SHARE_ELEC / DD_SHARE_GAS against the new figure (WALL DISCIPLINE)."
    )
    assert pd.DD_SHARE_ELEC == 0.72
    assert pd.DD_SHARE_GAS == 0.75


def test_module_does_not_import_company_or_saas():
    src = (REPO_ROOT / "simulation" / "population_draw.py").read_text()
    for banned in ("import company", "from company", "import saas", "from saas"):
        assert banned not in src, f"epistemic-wall violation: '{banned}' in population_draw.py"


# ---------------------------------------------------------------------------
# DIRECTOR CURRICULUM "PROFILE B: TRICKLE CONTINUATION" (~1 new customer/year)
# BUILD_THE_BACKLOG.md, director P0. The headline L2 bar: the draw's realised
# arrival RATE is the signed profile-B trickle -- ~1/yr on average over many
# seeds, per year and window-wide -- neither a growth explosion nor static.
# This is a DIAGNOSTIC check of the mechanism's cadence (R12/Law A), a loose
# statistical band around the director's lambda, never a tuned point.
# ---------------------------------------------------------------------------
def test_profile_b_window_mean_arrivals_approx_one_per_year():
    """Averaged over many seeds, total acquisitions per run divided by the
    number of years in the window must sit close to 1.0 -- the profile-B
    trickle rate (Poisson lambda=1.0)."""
    n_seeds = 3000
    n_years = pd.DEFAULT_END_YEAR - pd.DEFAULT_START_YEAR + 1
    total = sum(len(pd.draw_population(base_seed=s)) for s in range(n_seeds))
    mean_per_year = total / n_seeds / n_years
    # Poisson(1) over 5 years, 3000 seeds: SE of the per-year mean ~= 0.008;
    # a 0.1 band is a generous DIAGNOSTIC sanity flag, not a tuned target.
    assert abs(mean_per_year - pd.DEFAULT_ACQUISITIONS_PER_YEAR_LAMBDA) < 0.1, (
        f"realised trickle rate {mean_per_year:.3f}/yr is not profile-B ~1/yr"
    )


def test_profile_b_each_year_is_a_trickle_not_a_growth_explosion():
    """Every individual year in the window averages ~1 acquisition -- the
    trickle is flat across years (continuation), and NO year runs away into a
    growth explosion. Guards the profile-B shape, not just the aggregate."""
    n_seeds = 2000
    per_year = {y: 0 for y in range(pd.DEFAULT_START_YEAR, pd.DEFAULT_END_YEAR + 1)}
    for s in range(n_seeds):
        for c in pd.draw_population(base_seed=s):
            per_year[int(c.acquisition_date[:4])] += 1
    for year, count in per_year.items():
        mean = count / n_seeds
        assert 0.85 < mean < 1.15, f"{year} mean {mean:.3f}/run is not a ~1/yr trickle"


def test_profile_b_rate_tracks_the_curriculum_lambda_not_hardcoded():
    """The realised rate is DRIVEN BY the director's curriculum lambda, not a
    baked-in constant -- doubling lambda ~doubles arrivals, halving ~halves
    them. Proves the trickle is the curriculum instrument (R13), tunable only
    by a director-authored change to the rate, and that ~1/yr is not a fluke of
    some other fixed cap."""
    n_seeds = 2000
    n_years = pd.DEFAULT_END_YEAR - pd.DEFAULT_START_YEAR + 1

    def rate(lam):
        total = sum(
            len(pd.draw_population(base_seed=s, acquisitions_per_year_lambda=lam))
            for s in range(n_seeds)
        )
        return total / n_seeds / n_years

    assert abs(rate(1.0) - 1.0) < 0.1
    assert abs(rate(2.0) - 2.0) < 0.15
    assert abs(rate(0.5) - 0.5) < 0.1


# ---------------------------------------------------------------------------
# CONSTRAINT 2: RNG substream isolation (C-S2)
# ---------------------------------------------------------------------------
def test_substream_isolation_global_random_untouched():
    """Drawing a population must NOT consume from or perturb the global
    `random` module -- a draw here can never shift another subsystem that uses
    global random."""
    random.seed(12345)
    before = [random.random() for _ in range(20)]

    random.seed(12345)
    _ = pd.draw_population(base_seed=999)  # draws happen here
    after = [random.random() for _ in range(20)]

    assert before == after


def test_substream_isolation_other_named_stream_untouched():
    """A separately-named subsystem substream, seeded from the SAME base seed,
    is unaffected by any number of population draws -- the exact property the
    01:09Z incident violated."""
    base = 55

    def other_subsystem_sequence():
        # An independent subsystem deriving its own named substream.
        key = f"some_other_subsystem::{base}".encode("utf-8")
        import hashlib
        seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
        r = random.Random(seed_int)
        return [r.random() for _ in range(30)]

    seq_before = other_subsystem_sequence()
    _ = pd.draw_population(base_seed=base)
    _ = pd.draw_population(base_seed=base)  # draw twice, more churn
    seq_after = other_subsystem_sequence()

    assert seq_before == seq_after


def test_population_substream_advance_never_shifts_sibling():
    """The exact 01:09Z-incident guard, in its sharpest form: ADVANCING the
    population substream by DIFFERENT amounts (more/fewer draws via a bigger
    window and a higher lambda) must leave an independently-named sibling
    subsystem's sequence byte-identical every time. Adding or growing this
    draw can never perturb another subsystem's RNG output."""
    base = 808

    def sibling_sequence():
        import hashlib
        key = f"unrelated_sibling_subsystem::{base}".encode("utf-8")
        seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
        r = random.Random(seed_int)
        return [r.random() for _ in range(40)]

    baseline = sibling_sequence()
    # Each of these advances the population substream by a different number of
    # internal draws; the sibling must be unmoved after all of them.
    pd.draw_population(base_seed=base)
    assert sibling_sequence() == baseline
    pd.draw_population(base_seed=base, start_year=2016, end_year=2025)
    assert sibling_sequence() == baseline
    pd.draw_population(base_seed=base, acquisitions_per_year_lambda=5.0)
    assert sibling_sequence() == baseline
    # ...and a full materialisation of a long, dense cohort.
    pd.draw_population(base_seed=base, start_year=2010, end_year=2030,
                       acquisitions_per_year_lambda=8.0)
    assert sibling_sequence() == baseline


def test_substream_seed_derivation_is_named_not_shared():
    """Two different base seeds yield different isolated substream states, and
    the derivation is a pure function of (STREAM_NAME, base_seed)."""
    a = pd._substream(1)
    b = pd._substream(2)
    assert [a.random() for _ in range(5)] != [b.random() for _ in range(5)]


# ---------------------------------------------------------------------------
# CONSTRAINT 3: deterministic replay / idempotency (C-S2)
# ---------------------------------------------------------------------------
def test_deterministic_replay_identical_population_same_seed():
    pop1 = pd.draw_population(base_seed=2024)
    pop2 = pd.draw_population(base_seed=2024)
    assert pop1 == pop2  # frozen dataclasses compare by value


def test_deterministic_replay_survives_intervening_global_rng_use():
    """Replay determinism must not depend on global RNG state -- an unrelated
    global draw between two runs must not change the result."""
    pop1 = pd.draw_population(base_seed=77)
    random.seed()  # reseed global from entropy
    _ = [random.random() for _ in range(1000)]
    pop2 = pd.draw_population(base_seed=77)
    assert pop1 == pop2


def test_different_seeds_generally_differ():
    pops = {tuple(c.customer_id + c.acquisition_date for c in pd.draw_population(base_seed=s))
            for s in range(30)}
    # Not all 30 seeds should collapse to one identical population.
    assert len(pops) > 1


# ---------------------------------------------------------------------------
# Attribute plausibility (anchored distributions honoured)
# ---------------------------------------------------------------------------
def test_eac_within_anchored_tdcv_band_for_its_commodity_and_band():
    for seed in range(100):
        for c in pd.draw_population(base_seed=seed):
            low, high = pd.TDCV_BANDS_KWH[c.commodity][c.consumption_band]
            assert low <= c.eac_kwh <= high


def test_payment_method_share_tracks_dd_anchor():
    """Aggregate DD share across a large synthetic sample should land near the
    commodity-weighted anchor (72% elec / 75% gas), a DIAGNOSTIC not a target
    -- a loose band, not a tuned point."""
    elec_dd = elec_n = gas_dd = gas_n = 0
    for seed in range(1000):
        for c in pd.draw_population(base_seed=seed):
            if c.commodity == "electricity":
                elec_n += 1
                elec_dd += c.payment_method == "direct_debit"
            else:
                gas_n += 1
                gas_dd += c.payment_method == "direct_debit"
    assert elec_n > 100 and gas_n > 100
    assert abs(elec_dd / elec_n - pd.DD_SHARE_ELEC) < 0.06
    assert abs(gas_dd / gas_n - pd.DD_SHARE_GAS) < 0.06


def test_region_is_explicit_placeholder_not_fabricated():
    for c in pd.draw_population(base_seed=3):
        assert c.region == pd._PLACEHOLDER_REGION


def test_data_regime_is_synthetic():
    for c in pd.draw_population(base_seed=4):
        assert c.data_regime == "synthetic"
        assert c.to_customer_dict()["data_regime"] == "synthetic"


def test_segment_weights_override_is_honoured():
    pop = pd.draw_population(
        base_seed=9, segment_weights={"resi": 1.0, "SME": 0.0, "I&C": 0.0}
    )
    assert pop  # non-empty for this seed
    assert all(c.segment == "resi" for c in pop)


def test_events_arrive_in_date_order():
    events = pd.draw_population(base_seed=2024)
    dates = [e.acquisition_date for e in events]
    assert dates == sorted(dates)


def test_iter_is_lazy_stream_not_prebuilt_list():
    it = pd.iter_acquisition_events(base_seed=1)
    first = next(it, None)
    # Either a SyntheticCustomer or exhausted; must be an iterator, not a list.
    assert not isinstance(pd.iter_acquisition_events(base_seed=1), list)
    if first is not None:
        assert isinstance(first, pd.SyntheticCustomer)
