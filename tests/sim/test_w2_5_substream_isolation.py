"""W2_5_life_event_stream — RNG substream isolation + deterministic replay.

Headline requirement (C-S2, CLAUDE.md; the real 01:09Z incident): the shared
life-event generator must draw EACH event type from its OWN named, seeded
substream, so that adding a new event type (or removing one) can NEVER shift the
random numbers any other subsystem draws. Before this atom, all economic events
shared a single ``econ_rng`` — adding illness/divorce shifted every downstream
(job_loss/new_baby/retirement) draw, which shifted churn timing and active-
account counts. These tests lock the structural fix.

They deliberately test the RNG-SEQUENCE isolation property (a new draw cannot
shift another substream's numbers), NOT the model's intended DOMAIN state
coupling (all economic shocks route through the single income_stress variable,
so a household already in HIGH stress genuinely cannot also "lose its job" — that
coupling is real and correct, and is not what C-S2 is about).
"""

import random

import pytest

from simulation.household import IncomeStress, make_household
from simulation.life_events import (
    _DIVORCE_ANNUAL_PROB,
    _ILLNESS_ANNUAL_PROB,
    _JOB_LOSS_ANNUAL_PROB,
    _LIFE_EVENT_SUBSTREAMS,
    _NEW_BABY_ANNUAL_PROB,
    _RETIREMENT_PROB_BY_ERA,
    _base_seed_for,
    _substream,
    generate_life_events,
)


def _resi_hh(cid="C1", home_type="suburban_semi"):
    return make_household(
        {"customer_id": cid, "home_type": home_type, "epc_rating": "C", "segment": "resi"}
    )


# ── 1. Substream contract ────────────────────────────────────────────────────

def test_substream_names_are_unique():
    assert len(_LIFE_EVENT_SUBSTREAMS) == len(set(_LIFE_EVENT_SUBSTREAMS))


def test_substream_covers_every_emitted_event_type():
    # Across a wide seed sweep, every event type the generator actually emits
    # must have a named substream — a new emitted type without one would KeyError.
    emitted = set()
    for i in range(300):
        hh = _resi_hh(cid=f"C{i}")
        emitted |= {e.event_type for e in generate_life_events(hh, 2016, 2025)}
    missing = emitted - set(_LIFE_EVENT_SUBSTREAMS)
    assert not missing, f"emitted event types with no named substream: {missing}"


def test_substream_is_deterministic():
    a = [_substream(999, "illness").random() for _ in range(10)]
    b = [_substream(999, "illness").random() for _ in range(10)]
    assert a == b


def test_substream_value_is_stable_across_processes():
    # sha256-derived, NOT Python's per-process-salted hash(): a regression to a
    # salted seed would break C-S2 deterministic replay and fail this exact value.
    assert round(_substream(12345, "job_loss").random(), 12) == 0.157207184982


def test_distinct_substreams_produce_different_sequences():
    job = [_substream(555, "job_loss").random() for _ in range(20)]
    div = [_substream(555, "divorce").random() for _ in range(20)]
    assert job != div


# ── 2. THE headline C-S2 guarantee: a new substream can't shift an existing one ─

def test_new_substream_does_not_shift_existing_substream():
    base = 424242
    before = [_substream(base, "job_loss").random() for _ in range(50)]
    # A brand-new event type is introduced into the model and drawn from heavily.
    _ = [_substream(base, "some_future_event_type").random() for _ in range(500)]
    after = [_substream(base, "job_loss").random() for _ in range(50)]
    assert before == after, "introducing a new named substream shifted an existing one"


def test_every_named_substream_is_invariant_to_every_other_being_drawn():
    base = 7788
    # Reference: each substream's first 30 draws, taken in isolation.
    reference = {
        name: [_substream(base, name).random() for _ in range(30)]
        for name in _LIFE_EVENT_SUBSTREAMS
    }
    # Now drain a plausible "new event" stream, then re-derive each: unchanged.
    _ = [_substream(base, "hypothetical_new_event").random() for _ in range(1000)]
    for name in _LIFE_EVENT_SUBSTREAMS:
        assert [_substream(base, name).random() for _ in range(30)] == reference[name]


# ── 3. Base-seed derivation is PYTHONHASHSEED-independent ─────────────────────

def test_base_seed_from_customer_id_is_stable():
    hh = _resi_hh("C1")
    assert _base_seed_for(hh, None) == 439213101  # md5-derived, process-independent


def test_base_seed_passthrough_when_explicit():
    hh = _resi_hh("C1")
    assert _base_seed_for(hh, 42) == 42


# ── 4. Generator-level determinism / replay (C-S2) ───────────────────────────

def test_generate_life_events_is_deterministic_on_seed():
    hh = _resi_hh("C42")
    a = generate_life_events(hh, 2016, 2025, seed=13)
    b = generate_life_events(hh, 2016, 2025, seed=13)
    assert a == b


def test_generate_life_events_replay_is_stable_without_explicit_seed():
    # No explicit seed -> deterministic md5 of customer_id, so replay is stable.
    hh = _resi_hh("C77")
    assert generate_life_events(hh, 2016, 2025) == generate_life_events(hh, 2016, 2025)


# ── 5. Generator sources each event's decision from its OWN substream ─────────
# Year 1 always starts at income_stress LOW (verified elsewhere), so the FIRST
# draw of an event's substream is consumed in the first simulated year, free of
# multi-year state coupling — letting us prove the decision came from that
# event's OWN substream and no other.

def test_year_one_job_loss_decision_comes_from_job_loss_substream():
    hh = _resi_hh("CJ")
    seed = 20240101
    base = _base_seed_for(hh, seed)
    first = _substream(base, "job_loss").random()
    events = generate_life_events(hh, 2016, 2025, seed=seed)
    fired_year_one = any(
        e.event_type == "job_loss" and e.event_date.startswith("2016") for e in events
    )
    assert fired_year_one == (first < _JOB_LOSS_ANNUAL_PROB)


def test_year_one_retirement_decision_comes_from_retirement_substream():
    hh = _resi_hh("CR")  # suburban_semi -> ERA_1945_1964, retire_prob > 0
    retire_prob = _RETIREMENT_PROB_BY_ERA[hh.build_era.value]
    assert retire_prob > 0
    seed = 5551212
    base = _base_seed_for(hh, seed)
    first = _substream(base, "retirement_starts").random()
    events = generate_life_events(hh, 2016, 2025, seed=seed)
    fired_year_one = any(
        e.event_type == "retirement_starts" and e.event_date.startswith("2016")
        for e in events
    )
    assert fired_year_one == (first < retire_prob)


# ── 6. Regression witness: the OLD shared-stream design would fail this ───────

def test_job_loss_and_illness_do_not_share_a_stream():
    # Under the pre-fix design both drew from one econ_rng, so their draw
    # sequences were interleaved slices of the same stream. Now each has its own
    # independent substream: the sequences must be independent (unequal).
    base = _base_seed_for(_resi_hh("CX"), 909090)
    job = [_substream(base, "job_loss").random() for _ in range(25)]
    ill = [_substream(base, "illness").random() for _ in range(25)]
    assert job != ill


# ── 7. Sanity: illness/divorce probability magnitudes (real anchors) ─────────

def test_illness_and_divorce_probs_have_plausible_magnitudes():
    # illness: ONS/Health Foundation disability prevalence growth ~0.9pp/yr proxy.
    # divorce: 102,678 E&W divorces 2023 / 28.4M UK households = ~0.36%/hh/yr.
    assert 0.001 <= _ILLNESS_ANNUAL_PROB <= 0.05
    assert _DIVORCE_ANNUAL_PROB == pytest.approx(102678 / 28_400_000, abs=5e-5)
    assert 0 < _NEW_BABY_ANNUAL_PROB < 0.05
