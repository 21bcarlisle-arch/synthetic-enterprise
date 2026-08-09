"""C10_self_rationing_detection -- unit + coupled-gap wiring tests.

Three layers:
  1. The detector reads OBSERVABLES only and separates a self-rationer (a DROP
     below floor) from a genuinely-low-need home (below floor but NO drop) -- the
     confound it must not fail -- plus the honest blind spots (no baseline,
     arrears, above floor) (unit tests).
  2. Wall + drift discipline: the detector imports nothing from `simulation.*`
     and its TDCV floor tracks the company-side source of truth.
  3. The W2_8 <-> C10 coupled gap wiring is REAL, not theatre: MUTATION tests
     prove the detection-gap fires on its named defects -- a perfect detector
     drives the gap to 0, a blind (flag-nobody) detector to 1, and the harm
     weighting is load-bearing. The scenario is deterministic (C-S2) and the
     ledger write is read-merge-write (preserves siblings). Per CLAUDE.md R15: a
     control that cannot fail is worse than none.
"""

import datetime as dt
import json

import pytest

from company.compliance.domain_invariants import TDCV_ELEC_LOW, TDCV_GAS_LOW
from company.crm.self_rationing_detector import (
    AccountRecord,
    AccountRecordType,
    SelfRationingDetector,
    SelfRationingObservation,
    TDCV_LOW_FLOOR_KWH,
    _MATERIAL_DROP_FRACTION,
)
from company.crm.vulnerability_register import VulnerabilityFlag, VulnerabilityRegister

from background.gap_metric import detection_gap, write_gap_entry

import tools.couple_w2_8_c10 as couple


# --------------------------------------------------------------------------
# 1. detector unit behaviour -- the rationer vs low-need discrimination
# --------------------------------------------------------------------------

FLOOR_E = TDCV_ELEC_LOW.low   # 1400


def _obs(**kw):
    base = dict(customer_id="C1", commodity="electricity")
    base.update(kw)
    return SelfRationingObservation(**base)


def test_self_rationer_flagged():
    """A DROP from a normal baseline down below the floor, clean payments,
    baseline present -> flagged, PPM_SELF_DISCONNECTED raised."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=1200.0))
    assert r.self_rationing_suspected is True
    assert r.vulnerability_flags == (VulnerabilityFlag.PPM_SELF_DISCONNECTED,)
    assert r.confidence > 0.5
    assert r.signals["below_floor"] is True
    assert r.signals["material_drop"] is True


def test_low_need_home_not_flagged_the_confound():
    """A genuinely-low-need home: below floor but NO drop (observed == baseline).
    This is THE confound -- it must NOT be flagged even though it is below the
    floor with a clean record."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=1050.0, observed_annual_kwh=1050.0))
    assert r.self_rationing_suspected is False
    assert r.vulnerability_flags == ()
    assert r.signals["below_floor"] is True
    assert r.signals["material_drop"] is False
    assert "low-need" in r.signals["not_flagged_reason"]


def test_below_floor_alone_never_flags_without_a_drop():
    """A detector that flags everyone below floor is naive/leaking. A slightly-
    below-floor home with only a trivial (sub-threshold) drop is NOT flagged."""
    det = SelfRationingDetector()
    # 5% drop -- below the 20% material threshold.
    r = det.detect(_obs(baseline_annual_kwh=1300.0, observed_annual_kwh=1235.0))
    assert r.self_rationing_suspected is False


def test_no_baseline_is_the_blind_spot():
    """No usable baseline (traditional meter / switched-in) -> the drop is
    unobservable -> NOT flagged, even though below floor. The detector does NOT
    fall back to below-floor-alone."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=None, observed_annual_kwh=1100.0))
    assert r.self_rationing_suspected is False
    assert r.signals["has_usable_baseline"] is False
    assert "NO usable baseline" in r.signals["not_flagged_reason"]


def test_arrears_deferred_to_collections():
    """A textbook rationing signature BUT arrears open -> the collections channel
    owns it; this silent-hardship flag defers rather than double-flag."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=1200.0,
                        arrears_open=True))
    assert r.self_rationing_suspected is False
    assert "collections" in r.signals["not_flagged_reason"]


def test_missed_payment_deferred():
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=1200.0,
                        missed_payments=1))
    assert r.self_rationing_suspected is False


def test_drop_but_above_floor_not_flagged():
    """A big cut that still leaves the home above the plausible-living floor is
    belt-tightening, not the below-floor hardship signature."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=4200.0, observed_annual_kwh=1800.0))
    assert r.signals["below_floor"] is False
    assert r.self_rationing_suspected is False


def test_weather_normalisation_masks_a_mild_year():
    """If the whole drop is explained by a much milder period (weather factor),
    the residual cut is below threshold -> NOT flagged (a warm year is not a
    ration). This is an honest observational limit, not a bug."""
    det = SelfRationingDetector()
    # baseline 1700, observed 1300 -> raw drop ~24%. But a mild year (factor
    # 0.80) makes weather-expected 1360, residual drop only ~4% -> not material.
    r = det.detect(_obs(baseline_annual_kwh=1700.0, observed_annual_kwh=1300.0,
                        weather_normalisation_factor=0.80))
    assert r.self_rationing_suspected is False
    assert r.signals["material_drop"] is False


def test_weather_normalisation_still_catches_a_real_cut():
    """A cut BEYOND what a mild year explains is still flagged."""
    det = SelfRationingDetector()
    r = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=1100.0,
                        weather_normalisation_factor=0.95))
    assert r.self_rationing_suspected is True


def test_confidence_deeper_cut_higher():
    det = SelfRationingDetector()
    shallow = det.detect(_obs(baseline_annual_kwh=1800.0, observed_annual_kwh=1390.0))
    deep = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=700.0))
    assert deep.confidence > shallow.confidence


def test_gas_commodity_floor():
    det = SelfRationingDetector()
    r = det.detect(_obs(commodity="gas", baseline_annual_kwh=11000.0,
                        observed_annual_kwh=4800.0))
    assert r.signals["floor_kwh"] == TDCV_GAS_LOW.low
    assert r.self_rationing_suspected is True


def test_apply_to_register_raises_ppm_flag_with_actions():
    det = SelfRationingDetector()
    reg = VulnerabilityRegister()
    r = det.detect(_obs(baseline_annual_kwh=2900.0, observed_annual_kwh=1100.0))
    det.apply_to_register(reg, r, dt.date(2024, 1, 1))
    rec = reg.get("C1")
    assert rec is not None
    assert VulnerabilityFlag.PPM_SELF_DISCONNECTED in rec.flags
    # The orphaned flag now drives a real support response.
    assert "offer_emergency_credit" in rec.required_actions
    assert "debt_referral" in rec.required_actions


def test_apply_to_register_no_detection_is_noop():
    det = SelfRationingDetector()
    reg = VulnerabilityRegister()
    r = det.detect(_obs(baseline_annual_kwh=1050.0, observed_annual_kwh=1050.0))
    det.apply_to_register(reg, r, dt.date(2024, 1, 1))
    assert reg.get("C1") is None


# --------------------------------------------------------------------------
# 1b. THE SUPPLIER'S OWN RECORDS (atom D18) -- the observable confounder
#     channel. Every test here is a differential: the SAME textbook rationing
#     signature, with and without a record, so a test can only pass because the
#     record did something.
# --------------------------------------------------------------------------

_AS_OF = dt.date(2024, 5, 30)
_PERIOD_START = dt.date(2023, 4, 1)


def _rationing_obs(**kw):
    """The textbook signature: a drop from 2900 to 1200 (below the 1400 floor),
    clean payments, baseline present -> flagged, absent any record."""
    base = dict(
        baseline_annual_kwh=2900.0, observed_annual_kwh=1200.0,
        as_of=_AS_OF, baseline_period_start=_PERIOD_START,
    )
    base.update(kw)
    return _obs(**base)


def _record(record_type, effective=dt.date(2023, 9, 1), received=dt.date(2023, 10, 1),
            saving=None):
    return AccountRecord(record_type=record_type, effective_date=effective,
                         received_date=received, expected_saving_fraction=saving)


def test_the_signature_is_still_flagged_with_no_records_at_all():
    """The differential's control arm. Every D18 test below changes ONE thing
    from this observation, so a suppression can only be the record's doing."""
    det = SelfRationingDetector()
    assert det.detect(_rationing_obs()).self_rationing_suspected is True


def test_arrived_cot_record_invalidates_the_baseline_and_is_not_a_clearance():
    """A change-of-tenancy the company HAS: the prior baseline belongs to the
    previous occupier, so the drop is not this household's drop and no flag can
    be raised from it. Critically it is NOT a finding of no hardship -- the
    incoming occupier may be rationing and the company simply cannot see it."""
    det = SelfRationingDetector()
    r = det.detect(_rationing_obs(
        account_records=(_record(AccountRecordType.CHANGE_OF_TENANCY),)))
    assert r.self_rationing_suspected is False
    assert r.signals["baseline_invalidated_by"] == "change_of_tenancy"
    assert r.signals["has_usable_baseline"] is False
    assert "NOT a finding of no hardship" in r.signals["not_flagged_reason"]
    assert r.signals["records_arrived"] == ("change_of_tenancy",)


def test_void_notification_behaves_the_same_way():
    det = SelfRationingDetector()
    r = det.detect(_rationing_obs(
        account_records=(_record(AccountRecordType.VOID_NOTIFICATION),)))
    assert r.self_rationing_suspected is False
    assert r.signals["baseline_invalidated_by"] == "void_notification"


def test_mutation_a_record_that_has_not_arrived_explains_nothing():
    """R15, THE LABEL-LEAK MUTATION the atom names. The event HAPPENED and the
    record EXISTS -- but it reaches us after the detection date (CoT discovery
    is weeks to months). The household must still be flaggable, exactly as it
    was before D18. A channel that fired on existence rather than arrival would
    be handing the detector the world's cause enum by another name."""
    det = SelfRationingDetector()
    late = _record(AccountRecordType.CHANGE_OF_TENANCY,
                   effective=dt.date(2024, 2, 1), received=dt.date(2024, 8, 1))
    r = det.detect(_rationing_obs(account_records=(late,)))
    assert r.self_rationing_suspected is True
    assert r.signals["records_arrived"] == ()
    assert r.signals["records_not_yet_arrived"] == ("change_of_tenancy",)
    assert r.signals["baseline_invalidated_by"] is None


def test_no_as_of_means_no_record_has_arrived():
    """Fail-SAFE, not fail-open: with no stated clock the company cannot claim a
    record had reached it, so the record suppresses nothing and the account gets
    looked at. An unknown clock must never silence a vulnerability flag."""
    det = SelfRationingDetector()
    r = det.detect(_rationing_obs(
        as_of=None, account_records=(_record(AccountRecordType.CHANGE_OF_TENANCY),)))
    assert r.self_rationing_suspected is True


def test_a_record_predating_the_baseline_period_does_not_explain_this_drop():
    """A tenancy change four years ago explains the BASELINE, not a fall away
    from it. Without this the channel would fail open on stale history."""
    det = SelfRationingDetector()
    stale = _record(AccountRecordType.CHANGE_OF_TENANCY,
                    effective=dt.date(2019, 6, 1), received=dt.date(2019, 7, 1))
    r = det.detect(_rationing_obs(account_records=(stale,)))
    assert r.self_rationing_suspected is True
    assert r.signals["records_not_yet_arrived"] == ("change_of_tenancy",)


def test_install_record_explains_a_retrofit_sized_fall():
    """Our own scheme insulated the home: the deemed saving on our own file
    lowers what we EXPECT the meter to read, so a retrofit-sized fall is no
    longer a material cut."""
    det = SelfRationingDetector()
    install = _record(AccountRecordType.OWN_SCHEME_INSTALL, saving=0.20)
    # 1550 -> 1200 is a 22.6% raw drop (material, and below the 1400 floor);
    # against a 20%-deemed-saving expectation of 1240 the residual is ~3%.
    obs = dict(baseline_annual_kwh=1550.0, observed_annual_kwh=1200.0)
    assert det.detect(_rationing_obs(**obs)).self_rationing_suspected is True
    r = det.detect(_rationing_obs(account_records=(install,), **obs))
    assert r.self_rationing_suspected is False
    assert r.signals["deemed_saving_fraction"] == 0.2
    assert "deemed saving" in r.signals["not_flagged_reason"]


def test_mutation_an_install_record_does_not_blanket_clear_a_deeper_cut():
    """The other half of the same control: a household that cut FAR beyond what
    its retrofit explains is still flagged. An install record that cleared any
    drop would be a blanket amnesty on exactly the accounts most at risk."""
    det = SelfRationingDetector()
    install = _record(AccountRecordType.OWN_SCHEME_INSTALL, saving=0.20)
    r = det.detect(_rationing_obs(account_records=(install,)))   # 2900 -> 1200
    assert r.self_rationing_suspected is True
    assert r.signals["deemed_saving_fraction"] == 0.2


def test_install_record_without_a_deemed_saving_adjusts_nothing():
    """A missing number must not become a free pass (the fail-open shape)."""
    det = SelfRationingDetector()
    install = _record(AccountRecordType.OWN_SCHEME_INSTALL, saving=None)
    obs = dict(baseline_annual_kwh=1550.0, observed_annual_kwh=1200.0)
    r = det.detect(_rationing_obs(account_records=(install,), **obs))
    assert r.self_rationing_suspected is True
    assert r.signals["deemed_saving_fraction"] == 0.0


def test_a_deemed_saving_can_never_swallow_an_arbitrary_drop():
    """Clamped below 1.0: an absurd saving on a record cannot drive expected
    consumption to zero and make every fall unremarkable."""
    det = SelfRationingDetector()
    install = _record(AccountRecordType.OWN_SCHEME_INSTALL, saving=0.99)
    r = det.detect(_rationing_obs(account_records=(install,)))   # 2900 -> 1200
    assert r.signals["deemed_saving_fraction"] == 0.9
    # expected 290, observed 1200 -> no drop at all; the clamp keeps the figure
    # finite and the account simply reads ABOVE its adjusted expectation.
    r2 = det.detect(_rationing_obs(observed_annual_kwh=100.0,
                                   account_records=(install,)))
    assert r2.self_rationing_suspected is True


# --------------------------------------------------------------------------
# 2. wall + drift discipline
# --------------------------------------------------------------------------

def test_detector_imports_no_simulation():
    import company.crm.self_rationing_detector as mod
    import inspect
    src = inspect.getsource(mod)
    assert "import simulation" not in src
    assert "from simulation" not in src


def test_floor_tracks_company_source_of_truth():
    """The detector floor is the domain_invariants source (regulation commons),
    not a re-derived threshold -- drift guard."""
    assert TDCV_LOW_FLOOR_KWH["electricity"] == TDCV_ELEC_LOW.low
    assert TDCV_LOW_FLOOR_KWH["gas"] == TDCV_GAS_LOW.low


def test_material_threshold_independent_of_sim_severity():
    """R15: the company's drop threshold is NOT the SIM's severity band. W2_8's
    minimum severity is 0.30; the detector's threshold is a lower, independently
    chosen 0.20 (so it is not reading the SIM's number)."""
    from simulation.self_rationing import _SEVERITY_RANGE
    assert _MATERIAL_DROP_FRACTION < _SEVERITY_RANGE[0]


# --------------------------------------------------------------------------
# 3. coupled-gap wiring -- MUTATION tests (the gap must be able to FAIL)
# --------------------------------------------------------------------------

def test_coupled_scenario_gap_is_non_degenerate():
    result, stats = couple.measure(n_customers=2500)
    assert stats["n_truth_detectable"] > 30, "need a real truth set"
    assert stats["n_low_need_below_floor"] > 0, "the confound must be present"
    # A real, honest gap: not perfect (blind spot), not blind (some recovery).
    assert 0.0 < result.gap < 1.0
    # THE FALSE-FLAG DIRECTION IS REAL NOW (atom D14). This assertion used to
    # read `false_positive_rate < 0.05` and it PASSED at 0.0000 -- on a world
    # where no non-rationer could drop at all, so no drop-based detector could
    # ever have failed it. A bound that tight was measuring the world's
    # emptiness and calling it detector precision (R12). What is asserted now is
    # STRUCTURAL: the rate can move, and the detector is far better than an
    # indiscriminate one -- never a target band.
    fp = stats["false_positive_rate"]
    assert fp is not None and 0.0 < fp < 0.5, fp
    assert stats["n_hard_negatives"] > 0, (
        "no non-rationer in the scored population has a real consumption drop "
        "-- the false-flag rate is structurally 0 again and means nothing"
    )


def test_the_false_flag_rate_is_scored_on_the_settled_negative_not_the_naive_one():
    """The D11 denominator rule, on this pair (atom D14). A household that IS
    self-rationing but sits ABOVE the floor is in NEITHER direction's
    population: it is not in the truth set, and a flag on it is CORRECT. Both
    rates are published every run so the defect cannot come back quietly."""
    result, stats = couple.measure(n_customers=2500)
    assert stats["negative_basis"] == couple.PUBLISHED_NEGATIVE_BASIS
    assert stats["n_neither_excluded"] > 0, "nothing excluded -- no differential"
    # The exclusion is PUBLISHED, not silent (D10): it travels in the components.
    assert result.components["n_excluded"] == stats["n_neither_excluded"]
    assert "ABOVE the TDCV Low floor" in result.components["exclusion_reason"]
    # The naive denominator sweeps the excluded set in -- a different number.
    by_basis = stats["false_flag_rate_by_basis"]
    assert set(by_basis) == set(couple.NEGATIVE_BASES)
    assert by_basis["settled_not_rationing"] != by_basis["naive_universe_minus_truth"]


def test_mutation_the_published_measure_never_runs_with_confounders_off():
    """R15: the world's hard negatives are what make the false-flag direction
    publishable, so the off-switch must be unreachable from the published path.
    Turning it off restores the pre-D14 vacuity -- and `detection_measures`
    would then report a false-flag rate of exactly 0.0000, the number the D13
    DISCOVER refused to publish."""
    pops = couple.build_populations(2500, confounders_enabled=False)
    assert pops.stats["n_hard_negatives"] == 0
    measures = couple.false_flag_measures(pops)
    assert measures[couple.PUBLISHED_NEGATIVE_BASIS].components["false_flag_rate"] == 0.0
    # The published entry point cannot reach that state.
    _result, stats = couple.measure(n_customers=800)
    assert stats["confounders_enabled"] is True
    # ...and the published company is the one that reads its own records (D18):
    # the off-switch there is a mutation instrument too, not a publishable mode.
    assert stats["record_channel_enabled"] is True


def test_every_miss_has_a_named_cause_and_the_channel_owns_its_share():
    """Every truth account the detector missed is a coverage blind spot, not a
    logic error: with a usable baseline the rationer is separable by
    construction. Since D18 there are exactly TWO ways to lose the baseline and
    both are counted -- the meter never gave us one, or a CoT/void record told
    us the history is not this occupier's. The second is the record channel's
    PRICE and it is named rather than absorbed into the first.

    THE ASSERTION THAT CHANGED, AND WHY IT HAD TO: this test previously read
    `missed_because_no_baseline == missed`, which would now be false by 4-9
    accounts -- and 'the channel lost us some hardship cases' is exactly the
    thing that must not vanish into a rounding argument."""
    result, stats = couple.measure(n_customers=2500)
    missed = result.components["missed"]
    assert missed == (
        stats["missed_because_no_baseline"]
        + stats["missed_because_record_invalidated_baseline"]
    )
    # Both causes are LIVE -- a decomposition where one term is always zero
    # would be a partition on paper only.
    assert stats["missed_because_no_baseline"] > 0
    assert stats["missed_because_record_invalidated_baseline"] > 0


# --------------------------------------------------------------------------
# 3b. THE OBSERVABLE CONFOUNDER CHANNEL, measured on the coupled population
#     (atom D18). The two R15 obligations the atom set: prove the channel is
#     not a label leak, and prove it actually MOVES the rate (a channel that
#     changes nothing is not evidence of anything).
# --------------------------------------------------------------------------

def test_mutation_the_channel_moves_the_false_flag_rate():
    """R15 obligation #2. Same world, same detector, records on vs off. If the
    published rate did not move, the channel would be decoration."""
    aided = couple.build_populations(2500)
    unaided = couple.build_populations(2500, record_channel_enabled=False)
    rate_aided = aided.stats["false_positive_rate"]
    rate_unaided = unaided.stats["false_positive_rate"]
    assert 0.0 < rate_aided < rate_unaided
    # The off-build reproduces the pre-D18 company EXACTLY -- the aided run's
    # own `..._unaided` figure is the same number, so the two ways of asking
    # agree and neither is a re-derivation of the other.
    assert unaided.stats["false_positive_rate"] == aided.stats["false_positive_rate_unaided"]
    assert unaided.stats["n_flagged"] == aided.stats["n_flagged_unaided"]
    # ...and with the channel off nothing is explained away.
    assert unaided.stats["n_false_flags_explained"] == 0
    assert unaided.stats["n_truth_explained_away"] == 0


def test_mutation_the_channel_is_not_a_label_leak():
    """R15 obligation #1, on the population. A household whose confounder fired
    but whose record has NOT arrived (or was never registered at all) must
    remain flaggable -- so the false-flag rate must stay well clear of zero and
    a large share of the pre-D18 false flags must remain UNEXPLAINABLE."""
    pops = couple.build_populations(2500)
    s = pops.stats
    assert s["false_positive_rate"] > 0.01, "the channel explained away everything"
    # A ceiling strictly below 1: some hard negatives can never be explained.
    assert 0.0 < s["explainable_share_of_false_flags"] < 0.75
    # And what was actually explained is strictly less than what could be --
    # coverage and latency both cost something.
    assert s["n_false_flags_explained"] < s["n_false_flags_explainable"]
    assert s["explanation_shortfall_share"] > 0.0
    # Records exist that have NOT arrived; without them latency is untested.
    assert s["n_records_arrived"] < s["n_records_exist"]


def test_a_voluntary_cut_can_never_produce_a_record():
    """The class that keeps the channel honest: nobody registers a decision to
    use less energy. Swept over the population's own ids, not one fixture."""
    from simulation.self_rationing import DropConfounder
    for i in range(2000):
        cid = f"W28C{i:06d}"
        assert couple.account_records_for(cid, DropConfounder.VOLUNTARY_CUT) == ()
        assert couple.account_records_for(cid, DropConfounder.NONE) == ()
    # ...while the causes that DO leave a record leave one for some households.
    assert any(couple.account_records_for(f"W28C{i:06d}", DropConfounder.HOUSE_MOVE)
               for i in range(50))


def test_all_three_record_types_occur_and_arrive_in_the_scored_population():
    """Vacuity guard: a channel whose rarest record never fires is untested by
    the measurement that cites it."""
    s = couple.build_populations(4000).stats
    for rtype in ("change_of_tenancy", "void_notification", "own_scheme_install"):
        assert s["record_mix"][rtype] > 0, rtype
        assert s["record_arrived_mix"][rtype] > 0, rtype


def test_mutation_the_channel_invariants_fire_on_their_own_defects():
    """R15 on the guard itself. `check_channel_invariants` is the function the
    real build calls, so these mutations exercise the shipped control rather
    than a copy of it."""
    # A record must never CREATE a flag.
    with pytest.raises(AssertionError, match="never create a flag"):
        couple.check_channel_invariants(
            flagged={"a", "b"}, flagged_unaided={"a"}, explained=set(), explainable=set())
    # Nothing may be explained away with no record behind it.
    with pytest.raises(AssertionError, match="no record behind it"):
        couple.check_channel_invariants(
            flagged={"a"}, flagged_unaided={"a", "b"},
            explained={"b"}, explainable=set())
    # The honest case passes.
    couple.check_channel_invariants(
        flagged={"a"}, flagged_unaided={"a", "b"},
        explained={"b"}, explainable={"b", "c"})


def test_the_price_of_the_channel_is_published_beside_the_benefit():
    """R12: the channel buys a lower false-flag rate and PAYS in missed
    hardship, and both travel. A published improvement whose cost is not in the
    same stats dict is how a metric gets gamed by accident."""
    s = couple.build_populations(2500).stats
    assert s["n_truth_explained_away"] > 0, (
        "no real rationer was explained away -- either the confounder draw has "
        "stopped landing on rationers (D14's independence property) or the cost "
        "term has gone blind"
    )
    assert s["false_positive_rate"] < s["false_positive_rate_unaided"]


def test_scenario_deterministic():
    a, _ = couple.measure(n_customers=1500)
    b, _ = couple.measure(n_customers=1500)
    assert a.gap == b.gap
    assert a.raw_gap == b.raw_gap


def test_mutation_perfect_detector_drives_gap_to_zero():
    """A detector that flags exactly the truth set has gap 0 -- proving the gap
    is not stuck high (a control that can never pass is also broken)."""
    truth, _flagged, harm, _stats = couple.build_scenario(1500)
    perfect = detection_gap(truth, truth, harm=harm)
    assert perfect.gap == 0.0


def test_mutation_blind_detector_drives_gap_to_one():
    """Flag nobody -> the whole detectable harm is missed -> gap == 1."""
    truth, _flagged, harm, _stats = couple.build_scenario(1500)
    blind = detection_gap(truth, set(), harm=harm)
    assert blind.gap == 1.0


def test_mutation_harm_weighting_is_load_bearing():
    """Missing a HIGH-harm account costs more than missing a low-harm one -- the
    harm weighting is real, not decorative."""
    truth = {"a", "b"}
    harm = {"a": 10.0, "b": 1.0}
    miss_high = detection_gap(truth, {"b"}, harm=harm)   # missed a (harm 10)
    miss_low = detection_gap(truth, {"a"}, harm=harm)    # missed b (harm 1)
    assert miss_high.gap > miss_low.gap


def test_ledger_write_is_read_merge_write(tmp_path):
    """Writing the W2_8<->C10 entry preserves existing sibling entries."""
    ledger = tmp_path / "coupled_gap_ledger.json"
    ledger.write_text(json.dumps({
        "W2_5_life_event_stream": {"twin_atom_id": "C7", "gap": 0.4}
    }))
    result, _ = couple.measure(n_customers=800)
    merged = write_gap_entry(
        couple.WORLD_ATOM_ID, couple.TWIN_ATOM_ID, result,
        measured_at="2026-07-13T00:00:00+00:00", run_git_commit="deadbeef",
        ledger_path=ledger,
    )
    assert "W2_5_life_event_stream" in merged   # sibling preserved
    assert "W2_8_self_rationing" in merged
    assert merged["W2_8_self_rationing"]["twin_atom_id"] == "C10_self_rationing_detection"
    assert merged["W2_8_self_rationing"]["metric"] == "detection"
