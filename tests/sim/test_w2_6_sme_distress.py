"""W2_6_sme_distress_twin — hidden SME/I&C business-distress twin.

Covers the atom's headline requirements:
  * RNG SUBSTREAM ISOLATION (C-S2, the 01:09Z incident): advancing this
    subsystem's substream leaves the live siblings (population_draw, life_events)
    and a household_budget-shaped sibling BYTE-IDENTICAL, and never touches the
    global ``random`` module.
  * DETERMINISTIC REPLAY (C-S2) on seed / customer_id, across processes.
  * THE CONFOUND: late-payment CULTURE (habitual late, healthy) vs genuine
    DISTRESS emit the SAME observable (is_paying_late) with a DIFFERENT hidden
    cause -- the exact disambiguation job of the coupled twin C8.
  * INSOLVENCY = bad debt AND a lost supply point (not just a write-off).
  * Epistemic wall: pure sim, no company/saas import.
  * Anchored rate plausibility (real UK figures, never fabricated).
  * Segment gating: residential is the life-event stream's job, not this twin.
"""
from __future__ import annotations

import hashlib
import random
from pathlib import Path

import pytest

from simulation import sme_distress as sd

REPO_ROOT = Path(__file__).resolve().parents[2]

WINDOW = dict(sim_start_year=2016, sim_end_year=2025)


def _profiles(n=400, segment="SME", **kw):
    return [
        sd.generate_business_distress(f"B{i}", segment, seed=i, **{**WINDOW, **kw})
        for i in range(n)
    ]


# ── 1. Substream contract ────────────────────────────────────────────────────

def test_substream_names_are_unique():
    assert len(sd._SUBSTREAMS) == len(set(sd._SUBSTREAMS))


def test_substream_is_deterministic():
    a = [sd._substream(999, "insolvency_hazard").random() for _ in range(10)]
    b = [sd._substream(999, "insolvency_hazard").random() for _ in range(10)]
    assert a == b


def test_substream_value_is_stable_across_processes():
    # sha256-derived, NOT Python's per-process-salted hash(): a regression to a
    # salted seed would break C-S2 deterministic replay and fail this exact value.
    key = "W2_6_sme_distress::insolvency_hazard::12345".encode("utf-8")
    expected_seed = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
    assert sd._substream(12345, "insolvency_hazard").random() == \
        random.Random(expected_seed).random()


def test_distinct_substreams_produce_different_sequences():
    a = [sd._substream(555, "insolvency_hazard").random() for _ in range(20)]
    b = [sd._substream(555, "late_payment_culture").random() for _ in range(20)]
    assert a != b


def test_base_seed_from_customer_id_is_stable_and_process_independent():
    expected = int(hashlib.md5(b"B7").hexdigest()[:8], 16)
    assert sd._base_seed_for("B7", None) == expected
    assert sd._base_seed_for("B7", 42) == 42  # explicit seed passes through


# ── 2. THE headline C-S2 guarantee: this substream can't shift a sibling ─────

def test_new_substream_does_not_shift_existing_substream():
    base = 424242
    before = [sd._substream(base, "insolvency_hazard").random() for _ in range(50)]
    _ = [sd._substream(base, "some_future_mechanism").random() for _ in range(500)]
    after = [sd._substream(base, "insolvency_hazard").random() for _ in range(50)]
    assert before == after


def test_every_named_substream_is_invariant_to_every_other_being_drained():
    base = 7788
    reference = {
        name: [sd._substream(base, name).random() for _ in range(30)]
        for name in sd._SUBSTREAMS
    }
    _ = [sd._substream(base, "hypothetical_new_mechanism").random() for _ in range(1000)]
    for name in sd._SUBSTREAMS:
        assert [sd._substream(base, name).random() for _ in range(30)] == reference[name]


def test_advancing_distress_does_not_perturb_global_random():
    random.seed(12345)
    before = [random.random() for _ in range(20)]
    random.seed(12345)
    _ = _profiles(300)  # heavy generation
    after = [random.random() for _ in range(20)]
    assert before == after


def test_advancing_distress_leaves_population_draw_byte_identical():
    """The direct 01:09Z-incident guard against a LIVE sibling: generating any
    amount of SME distress must leave population_draw's cohort byte-identical."""
    from simulation import population_draw as pd

    baseline = pd.draw_population(base_seed=808)
    # Advance this subsystem by wildly different amounts.
    _ = _profiles(500, segment="SME")
    _ = _profiles(500, segment="I&C")
    _ = [sd.generate_business_distress("X", "SME", 2000, 2040, seed=s) for s in range(50)]
    assert pd.draw_population(base_seed=808) == baseline


def test_advancing_distress_leaves_life_events_byte_identical():
    """Same guard against the OTHER live sibling: household life-event streams
    must be byte-identical whether or not SME distress has been drawn."""
    from simulation.household import make_household
    from simulation.life_events import generate_life_events

    hh = make_household(
        {"customer_id": "C1", "home_type": "suburban_semi",
         "epc_rating": "C", "segment": "resi"}
    )
    baseline = generate_life_events(hh, 2016, 2025)
    _ = _profiles(500)
    _ = _profiles(300, segment="I&C")
    assert generate_life_events(hh, 2016, 2025) == baseline


def test_advancing_distress_leaves_household_budget_shaped_sibling_identical():
    """household_budget (W2_4) is not yet built; a subsystem deriving its own
    named substream in the SAME convention must be byte-identical after any
    amount of distress churn -- the property that future sibling will rely on."""
    base = 55

    def household_budget_shaped_sequence():
        key = f"W2_4_household_budget::monthly_shortfall::{base}".encode("utf-8")
        seed_int = int.from_bytes(hashlib.sha256(key).digest()[:8], "big")
        return [random.Random(seed_int).random() for _ in range(30)]

    before = household_budget_shaped_sequence()
    _ = _profiles(400)
    _ = _profiles(400, segment="I&C")
    assert household_budget_shaped_sequence() == before


# ── 3. Deterministic replay (C-S2) ───────────────────────────────────────────

def test_deterministic_replay_identical_profile_same_seed():
    a = sd.generate_business_distress("B42", "SME", seed=13, **WINDOW)
    b = sd.generate_business_distress("B42", "SME", seed=13, **WINDOW)
    assert a == b  # frozen dataclasses + tuple events compare by value


def test_deterministic_replay_survives_intervening_global_rng_use():
    a = sd.generate_business_distress("B77", "I&C", **WINDOW)
    random.seed()
    _ = [random.random() for _ in range(1000)]
    b = sd.generate_business_distress("B77", "I&C", **WINDOW)
    assert a == b


def test_different_seeds_generally_differ():
    profiles = _profiles(60)
    shapes = {(p.sector, p.late_payment_culture, len(p.events)) for p in profiles}
    assert len(shapes) > 1


# ── 4. THE CONFOUND: culture vs distress, same observable, different cause ────

def test_late_payment_culture_and_distress_share_the_observable():
    """A habitual-late-payer (healthy) and a genuinely distressed business both
    return is_paying_late()==True while trading -- identical observable. The
    hidden CAUSE differs (CULTURE vs DISTRESS): the exact confound the company
    twin C8 must disentangle, and it can never read the cause directly."""
    # A healthy habitual-late-payer, hand-built to isolate the CULTURE case.
    culture = sd.BusinessDistressProfile(
        customer_id="CULT", segment="SME", sector="other",
        late_payment_culture=True, events=(),
    )
    assert culture.is_paying_late("2020-06-01") is True
    assert culture.late_payment_cause("2020-06-01") == sd.LatePaymentCause.CULTURE
    assert culture.distress_state_at("2020-06-01") == sd.DistressState.TRADING

    # A genuinely distressed, non-habitual payer.
    distress = sd.BusinessDistressProfile(
        customer_id="DIST", segment="SME", sector="construction",
        late_payment_culture=False,
        events=(sd.DistressEvent("DIST", "2020-01-15", "distress_onset", {}),),
    )
    assert distress.is_paying_late("2020-06-01") is True
    assert distress.late_payment_cause("2020-06-01") == sd.LatePaymentCause.DISTRESS
    assert distress.distress_state_at("2020-06-01") == sd.DistressState.DISTRESSED

    # SAME observable, DIFFERENT hidden truth -- unresolvable from the observable.
    assert culture.is_paying_late("2020-06-01") == distress.is_paying_late("2020-06-01")
    assert culture.late_payment_cause("2020-06-01") != distress.late_payment_cause("2020-06-01")


def test_healthy_prompt_payer_is_not_late():
    p = sd.BusinessDistressProfile(
        customer_id="OK", segment="I&C", sector="professional_services",
        late_payment_culture=False, events=(),
    )
    assert p.is_paying_late("2020-06-01") is False
    assert p.late_payment_cause("2020-06-01") == sd.LatePaymentCause.NONE


def test_distress_dominates_culture_as_the_hidden_cause():
    """A business BOTH habitually-late AND distressed is scored DISTRESS: both
    are true, but the credit-risk truth is the distress (the confound remains,
    the risk-relevant cause is well-defined)."""
    p = sd.BusinessDistressProfile(
        customer_id="BOTH", segment="SME", sector="wholesale_retail",
        late_payment_culture=True,
        events=(sd.DistressEvent("BOTH", "2019-03-01", "distress_onset", {}),),
    )
    assert p.late_payment_cause("2020-01-01") == sd.LatePaymentCause.DISTRESS


def test_recovery_returns_a_habitual_payer_to_culture_not_none():
    p = sd.BusinessDistressProfile(
        customer_id="REC", segment="SME", sector="other",
        late_payment_culture=True,
        events=(
            sd.DistressEvent("REC", "2019-03-01", "distress_onset", {}),
            sd.DistressEvent("REC", "2019-09-01", "distress_recovery", {}),
        ),
    )
    assert p.late_payment_cause("2019-05-01") == sd.LatePaymentCause.DISTRESS
    # After recovery, still late -- but now by CULTURE, not distress.
    assert p.distress_state_at("2020-01-01") == sd.DistressState.TRADING
    assert p.late_payment_cause("2020-01-01") == sd.LatePaymentCause.CULTURE


# ── 5. Insolvency = bad debt AND a lost supply point ─────────────────────────

def test_insolvency_is_bad_debt_and_lost_supply_point():
    # Find a seed producing an insolvency (sweep). High-hazard sector to help.
    prof = None
    for i in range(3000):
        p = sd.generate_business_distress(
            f"I{i}", "SME", seed=i, sector="construction", **WINDOW
        )
        if any(e.event_type == "insolvency" for e in p.events):
            prof = p
            break
    assert prof is not None, "no insolvency produced across 3000 seeds -- check hazard"
    ins = [e for e in prof.events if e.event_type == "insolvency"][0]
    # Bad debt: a real, high per-insolvency write-off (low-priority creditor).
    assert 0.60 <= ins.payload["writeoff_fraction"] <= 1.00
    # Lost supply point, NOT just a write-off:
    assert ins.payload["lost_supply_point"] is True
    assert isinstance(ins.payload["landlord_liable"], bool)
    assert ins.payload["procedure"] in {
        sd.InsolvencyProcedure.CVL.value, sd.InsolvencyProcedure.COMPULSORY.value
    }
    # Terminal: state stays INSOLVENT afterwards, no resurrection.
    assert prof.distress_state_at("2025-12-31") == sd.DistressState.INSOLVENT


def test_insolvency_is_terminal_no_events_after_it():
    for i in range(3000):
        p = sd.generate_business_distress(
            f"T{i}", "I&C", seed=i, sector="construction", **WINDOW
        )
        ins_dates = [e.event_date for e in p.events if e.event_type == "insolvency"]
        if ins_dates:
            last_ins = ins_dates[0]
            after = [e for e in p.events if e.event_date > last_ins]
            assert not after, "events emitted after insolvency (should be terminal)"
            break


# ── 6. Anchored rate plausibility (real UK figures, never fabricated) ────────

def test_anchored_constants_have_plausible_real_world_magnitudes():
    # UK company insolvency rate ~50-57 per 10,000 active companies/yr.
    assert 0.0040 <= sd._BASE_ANNUAL_INSOLVENCY_HAZARD <= 0.0070
    # 76% of insolvencies are CVLs.
    assert sd._CVL_SHARE == pytest.approx(0.76, abs=0.02)
    # ~33% aggregate SME energy debt write-off.
    assert sd._AGGREGATE_SME_WRITEOFF_RATE == pytest.approx(0.33, abs=0.02)
    # Sector shock ordering matches insolvency concentration (construction top).
    m = sd._SECTOR_SHOCK_MULT
    assert m["construction"] > m["wholesale_retail"] > m["accommodation_food"] > m["other"]


def test_realised_insolvency_rate_tracks_the_anchor_not_a_runaway():
    """Over many businesses, the realised share ever going insolvent across a
    10-year window sits in a plausible band around base_hazard*sector*10yr --
    a DIAGNOSTIC sanity flag (R12), not a tuned target."""
    n = 4000
    profiles = [
        sd.generate_business_distress(f"R{i}", "SME", seed=i, **WINDOW)
        for i in range(n)
    ]
    ever_insolvent = sum(
        any(e.event_type == "insolvency" for e in p.events) for p in profiles
    )
    share = ever_insolvent / n
    # base 0.0055 * mean sector mult (~1.0) * 10 yrs ~= 0.05; generous band.
    assert 0.01 < share < 0.12, f"realised 10yr insolvency share {share:.3f} implausible"


def test_higher_shock_sector_fails_more_often():
    """Sector shocks are real: a high-concentration sector (construction) must
    produce materially more insolvencies than a resilient one over the book."""
    def ever_insolvent_share(sector):
        n = 4000
        c = sum(
            any(e.event_type == "insolvency" for e in
                sd.generate_business_distress(f"S{sector}{i}", "SME", seed=i,
                                              sector=sector, **WINDOW).events)
            for i in range(n)
        )
        return c / n
    assert ever_insolvent_share("construction") > ever_insolvent_share("professional_services")


# ── 7. Segment gating & epistemic wall ───────────────────────────────────────

def test_residential_segment_is_rejected():
    with pytest.raises(ValueError):
        sd.generate_business_distress("R1", "resi", **WINDOW)


def test_business_segments_accepted():
    for seg in sd.BUSINESS_SEGMENTS:
        p = sd.generate_business_distress("B1", seg, **WINDOW)
        assert p.segment == seg
        assert p.data_regime == "synthetic"


def test_module_does_not_import_company_or_saas():
    src = (REPO_ROOT / "simulation" / "sme_distress.py").read_text()
    for banned in ("import company", "from company", "import saas", "from saas"):
        assert banned not in src, f"epistemic-wall violation: '{banned}' in sme_distress.py"


# ── 8. Event stream hygiene (C-S1 arrival tolerance) ─────────────────────────

def test_events_arrive_in_date_order():
    for i in range(200):
        p = sd.generate_business_distress(f"O{i}", "SME", seed=i, **WINDOW)
        dates = [e.event_date for e in p.events]
        assert dates == sorted(dates)


def test_events_are_immutable():
    p = sd.generate_business_distress("IMM", "SME", seed=1, sector="construction", **WINDOW)
    assert isinstance(p.events, tuple)
    if p.events:
        with pytest.raises(Exception):
            p.events[0].event_date = "2099-01-01"  # frozen dataclass


def test_late_payment_culture_incidence_tracks_the_curriculum_parameter():
    n = 4000
    culture = sum(
        sd.generate_business_distress(f"L{i}", "SME", seed=i, **WINDOW).late_payment_culture
        for i in range(n)
    )
    share = culture / n
    assert abs(share - sd._LATE_PAYMENT_CULTURE_INCIDENCE) < 0.03
