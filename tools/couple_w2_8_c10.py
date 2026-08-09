"""COUPLED-TRIAD runner for the W2_8 <-> C10 pair (silent self-rationing).

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the
ONLY layer permitted to hold the hidden SIM truth (the household's true rationing
label + severity) and the company's observable-only belief (the C10 detector's
flag) side by side to compute the belief-vs-truth GAP (COUPLED_TRIAD_DESIGN.md
1.3; identical role to background/gap_metric.py and the W2_5/W2_9 runners). It
lives in tools/ -- NOT under company/ or saas/ -- so it is not scanned by the
epistemic verifier and may legitimately import `simulation.*`.

THE COUPLED LOOP (3 loops, COUPLED_TRIAD):

  1. SIM adds depth   -- simulation.self_rationing (W2_8) holds the HIDDEN
                         pay-but-don't-heat state: a budget-stressed household
                         that keeps paying (missed_payments always 0) but drops
                         its consumption below the TDCV Low floor. It also emits
                         the CONFOUND: genuinely-low-need homes below floor with
                         NO drop and NO stress.
  2. COMPANY copes    -- the company NEVER sees the label, severity or budget. It
                         sees only observables: two annual meter reads (baseline
                         + current) -- WHERE it has a baseline at all -- the
                         public floor, a clean payment record, a regional weather
                         factor. The C10 detector (company.crm.self_rationing_
                         detector) infers rationing from the drop-below-floor.
  3. HARNESS measures -- detection_measures(...): BOTH error directions on
                         their own denominators (atom D14). The harm-weighted
                         fraction of DETECTABLE silent hardship the company
                         MISSED, AND the fraction of the settled negative
                         population it wrongly flagged.

BOTH DIRECTIONS, AND WHY THIS COULD NOT BE PUBLISHED BEFORE (atom D14)
----------------------------------------------------------------------
Until 2026-08-09 this pair published the MISS direction only, and the reason was
a property of the WORLD, not of the metric. `simulation.self_rationing` returned
`observed == healthy` EXACTLY for every non-rationer: 0 of 3752 had any drop, 0
were flaggable under any weather factor, so the false-flag rate was 0.0000 for
ANY drop-based detector. Publishing it would have reported the world's emptiness
as detector precision (R12). The D13 DISCOVER named that; D14 fixed the WORLD
(`DropConfounder`: moves, voids, retrofits, voluntary cuts now cut consumption
with no hardship behind them), and only then did this measure become real.

THE NEGATIVE POPULATION IS THE SETTLED LABEL, NOT `universe - truth`. There are
THREE populations here, not two:

  must-flag     `is_silent_hardship`  -- rationing, below floor, paying
  NEITHER       rationing but ABOVE the floor -- a flag is CORRECT, so the case
                belongs in no denominator (D10: excluded, counted, and the
                reason published in the components)
  must-not-flag `label == NOT_RATIONING` -- the settled Bernoulli outcome

`NEGATIVE_BASES` scores BOTH the settled negative and the naive
`universe - truth` on every run, so the denominator defect the D13 DISCOVER
found in this file cannot return unnoticed. Unlike the W2_5<->C7 pair's
three-way R13 call, this is NOT a curriculum choice: the naive basis is simply
WRONG (it scores the company down for correctly flagging a real rationer) and
travels only so a reader can see what it is worth.

THE SUPPLIER'S OWN RECORDS, AND THE DISTANCE THEY DO NOT CLOSE (atom D18)
--------------------------------------------------------------------------
D14 hid every confounder CAUSE, which it registered as making detection
strictly HARDER than reality: a real supplier holds a change-of-tenancy
registration, a void notification, its own install file, and would explain some
of those drops away. So 0.0560 was an UPPER bound. D18 builds the channel --
`account_records_for` emits SUPPLIER RECORDS (never the cause enum) through a
coverage gate and a latency band, and the C10 detector reads them.

What the channel is NOT: a free pass. A voluntary cut leaves NO record in any
system, ever, so a whole class of hard negatives stays permanently
unexplainable; a record that has not ARRIVED by `_AS_OF` does not count; and a
CoT/void record only invalidates the baseline (the history is the previous
occupier's), it never certifies that no hardship exists.

Every run therefore scores TWO companies on ONE population -- with the records
(`flagged`) and without (`flagged_unaided`, the pre-D18 company) -- and
publishes the three numbers the atom actually asked for: what a supplier COULD
have explained away, what it DID, and the distance between them. It also
publishes the channel's PRICE, which is not a footnote: a genuine rationer who
also moved house is explained away and MISSED.

R12 ON THE RESULT, STATED BEFORE THE NUMBER IS READ: the false-flag rate falls
and the miss rate RISES, and because this pair's gap is the unweighted mean of
two rates on very different denominators (205 truth vs 3752 negatives), the
headline GAP gets WORSE even though the company trades ~70 false flags for ~9
misses. That is a diagnostic, not a verdict on the channel -- and the fix for
disliking it is a cost-weighted instrument argued on its own merits, never
switching metric because this one moved the wrong way.

THE HONEST GAP DRIVER -- SMART-METER / BASELINE COVERAGE. The drop signal needs a
usable prior baseline. A real UK supplier does not have one for every account:
traditional (non-smart/non-AMR) meters send no regular reads and switched-in
customers bring no history. For those accounts the rationer is indistinguishable
from a low-need home, so the silent hardship is structurally invisible. The gap
is therefore ~ the harm-weighted fraction of rationers WITHOUT a usable baseline
-- anchored to real smart-meter penetration, NOT tuned to a number.

R15 INDEPENDENCE. The world answer key comes from the hidden budget->severity
physics (W2_8); the detector's drop threshold and the baseline-coverage rate are
set independently (supplier reasoning + a market fact). A rationer WITH a
baseline IS separable from a low-need home by construction (the drop is the only
difference) -- so the detector catches those and the gap comes entirely from the
coverage blind spot, NOT from tuning. That is the honest, interpretable result.

R12/R13. The coverage rate and drop threshold are frozen here; nothing is
adjusted to move the gap. A near-zero gap would mean the coverage blind spot was
erased or the label leaked -- a defect to diagnose, never banked.

DETERMINISM (C-S2). Every draw is seeded from a stable sha256 (named substream):
the healthy baseline, the low-need/normal mix, and baseline availability. No
wall-clock, no global RNG. `measured_at`/`run_git_commit` for the ledger are
gathered by this harness (not by gap_metric, which never calls a clock).
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import subprocess
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Callable, Dict, Optional, Tuple

from simulation.self_rationing import DropConfounder, generate_self_rationing_state

from company.crm.self_rationing_detector import (
    AccountRecord,
    AccountRecordType,
    SelfRationingDetector,
    SelfRationingObservation,
)

from background.gap_metric import detection_measures, write_gap_entry

WORLD_ATOM_ID = "W2_8_self_rationing"
TWIN_ATOM_ID = "C10_self_rationing_detection"

# -- Smart-meter / usable-baseline coverage (R10 anchor, R13 curriculum). GB
# domestic smart+advanced meter penetration was ~57-64% of meters through
# 2023-24 (DESNZ/BEIS "Smart Meters in GB" quarterly stats). A supplier can read
# a recent baseline only where it has such a meter (or a switched-in read
# history). Frozen here as a market fact -- NOT tuned to any gap number.
_BASELINE_COVERAGE = 0.63

# -- Healthy-baseline population shape (kWh/yr, electricity). A spread of home
# sizes, INCLUDING genuinely-low-need homes that already sit at/below the TDCV
# Low floor (1400) -- the confound. Illustrative curriculum (R10/R13), not
# fitted. Each (mean, weight) is a lognormal-ish band the draw picks from.
_HEALTHY_BANDS = (
    (1050.0, 0.15),   # genuinely-low-need: efficient one-person flats, below floor
    (1900.0, 0.30),   # small homes
    (2900.0, 0.35),   # nominal median single-fuel
    (4200.0, 0.20),   # larger / electric-heated
)

# Observable regional weather-normalisation factor band (HDD ratio recent vs
# baseline). Modest year-to-year variation; the detector applies it so a mild
# year is not mistaken for a cut. Kept modest -- W2_8 itself models no weather,
# so this only exercises the detector's normalisation, it does not fabricate a
# consumption effect on the SIM's observed figure (R10 simplification note).
_WEATHER_FACTORS = (0.94, 0.98, 1.0, 1.02, 1.07)


# ---------------------------------------------------------------------------
# THE OBSERVABLE CONFOUNDER CHANNEL (atom D18) — the supplier's OWN records.
#
# D14 left every confounder cause as ANSWER KEY, which made detection strictly
# HARDER than reality: a real supplier holds a change-of-tenancy registration, a
# void notification, an install file for its own scheme. This channel hands the
# company those RECORDS — never the cause enum — through three gates that keep
# it a record and not a label: COVERAGE (does the event leave a record at all),
# LATENCY (has it reached us by the detection date), and the fact that a CoT or
# void record only INVALIDATES the baseline, it never certifies "no hardship".
#
# The rates below are CURRICULUM shapes (R13/[L]), fixed from the advisor scope
# brief before the resulting rates were measured, and never tuned to a gap:
#   - CoT: "supplier-internal ... industry-wide, nobody is told"; discovery
#     latency is itself a distribution ("week 1 vs month 6") — so a bit over
#     half of moves get registered at all and the tail arrives too late.
#   - Void: the landlord/agent has to bother telling us; fewer do.
#   - Install: the file exists only for the company's OWN scheme customers, so
#     coverage is roughly a supplier's share of a national programme.
# ---------------------------------------------------------------------------
_RECORD_CHANNEL: Dict[DropConfounder, Optional[Tuple[AccountRecordType, float, Tuple[int, int]]]] = {
    # cause -> (record type, coverage, latency band in days)
    DropConfounder.HOUSE_MOVE: (AccountRecordType.CHANGE_OF_TENANCY, 0.55, (7, 240)),
    DropConfounder.VACANCY: (AccountRecordType.VOID_NOTIFICATION, 0.35, (14, 150)),
    DropConfounder.EFFICIENCY_RETROFIT: (AccountRecordType.OWN_SCHEME_INSTALL, 0.30, (1, 75)),
    # NO RECORD EXISTS, EVER: nobody registers a decision to use less energy.
    # This is what keeps the channel from being the answer key — a whole class
    # of hard negatives stays permanently unexplainable.
    DropConfounder.VOLUNTARY_CUT: None,
    DropConfounder.NONE: None,
}

# The DEEMED saving on the company's own install file (ECO/GBIS deemed scores,
# ~10-30% typical). It is a SCHEME constant, deliberately NOT the household's
# realised cut — the deemed-vs-actual performance gap is real, and reading the
# realised figure would be the magnitude leaking through the record.
_DEEMED_INSTALL_SAVING = 0.20

# The consumption period the two meter reads bracket, and the date the detector
# runs. A record received after `_AS_OF` has not arrived (C-S3: the request and
# the answer are separate events in time).
_PERIOD_START = date(2023, 4, 1)
_PERIOD_END = date(2024, 3, 31)
_DETECTION_LAG_DAYS = 60
_AS_OF = _PERIOD_END + timedelta(days=_DETECTION_LAG_DAYS)


def _u01(*parts) -> float:
    """Deterministic uniform(0,1) from a stable sha256 of the parts (C-S2)."""
    key = ":".join(str(p) for p in parts)
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big") / float(1 << 64)


def _draw_healthy_kwh(cid: str) -> float:
    """Pick a healthy baseline for the household from the population bands, with
    a deterministic +/-15% jitter (C-S2, named substream)."""
    pick = _u01("healthy_band", cid)
    cum = 0.0
    mean = _HEALTHY_BANDS[-1][0]
    for m, w in _HEALTHY_BANDS:
        cum += w
        if pick < cum:
            mean = m
            break
    jitter = 0.85 + 0.30 * _u01("healthy_jitter", cid)
    return round(mean * jitter, 1)


def _weather_factor(cid: str) -> float:
    idx = int(_u01("weather", cid) * len(_WEATHER_FACTORS))
    return _WEATHER_FACTORS[min(idx, len(_WEATHER_FACTORS) - 1)]


def account_records_for(cid: str, confounder: DropConfounder) -> Tuple[AccountRecord, ...]:
    """The supplier-side records this household's event WOULD generate (D18).

    Returns the records that EXIST — arrival is the detector's problem, not this
    function's, so the harness can measure explainable-but-not-explained. A
    cause with no record type (a voluntary cut) returns nothing, whatever the
    draw: the channel cannot invent a record for an event nobody registers.
    Deterministic (C-S2), from this module's own named substreams.
    """
    spec = _RECORD_CHANNEL.get(confounder)
    if spec is None:
        return ()
    record_type, coverage, (lo_days, hi_days) = spec
    if _u01("record_coverage", cid) >= coverage:
        return ()          # the event happened; nobody registered it
    effective = _PERIOD_START + timedelta(
        days=int(_u01("record_effective", cid) * 364)
    )
    latency = lo_days + int(_u01("record_latency", cid) * (hi_days - lo_days))
    saving = (
        _DEEMED_INSTALL_SAVING
        if record_type is AccountRecordType.OWN_SCHEME_INSTALL
        else None
    )
    return (
        AccountRecord(
            record_type=record_type,
            effective_date=effective,
            received_date=effective + timedelta(days=latency),
            expected_saving_fraction=saving,
        ),
    )


def _has_baseline(cid: str) -> bool:
    """Whether the company holds a usable prior baseline (smart/advanced meter or
    read history). Deterministic Bernoulli against the coverage rate (C-S2)."""
    return _u01("baseline_coverage", cid) < _BASELINE_COVERAGE


@dataclass(frozen=True)
class DetectionPopulations:
    """The THREE populations this pair scores, held as SETS (never counts).

    A count cannot notice that a flag landed outside the scored universe, which
    is exactly what a join-key drift looks like -- and it cannot express that
    `neither` belongs in no denominator at all.
    """
    universe: frozenset
    must_flag: frozenset        # is_silent_hardship -- the harm case
    neither: frozenset          # rationing but ABOVE the floor: a flag is RIGHT
    must_not_flag: frozenset    # label == NOT_RATIONING -- the settled negative
    flagged: frozenset
    harm: Dict[str, float] = field(default_factory=dict)
    stats: Dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class NegativeBasis:
    """One candidate answer to "which cases is a flag WRONG on?"."""
    key: str
    label: str
    negative_of: Callable[[DetectionPopulations], frozenset]
    exclusion_reason: str


# The two candidates, both scored every run (atom D14). This is NOT the W2_5
# pair's three-way R13 curriculum call: `naive_universe_minus_truth` is a
# DEFECT, kept visible so the fix cannot silently regress.
NEGATIVE_BASES: Dict[str, NegativeBasis] = {
    "settled_not_rationing": NegativeBasis(
        key="settled_not_rationing",
        label="settled negative: label == NOT_RATIONING (the Bernoulli outcome)",
        negative_of=lambda p: p.must_not_flag,
        exclusion_reason=(
            "households that ARE genuinely self-rationing but sit ABOVE the TDCV "
            "Low floor, so they fall outside `is_silent_hardship` and are not in "
            "the truth set. A C10 flag on one of them is CORRECT -- the company "
            "is right about the household -- so counting it as a false flag "
            "would score the company down for being right (the D11 rule; the "
            "defect the D13 DISCOVER found in this file)."
        ),
    ),
    "naive_universe_minus_truth": NegativeBasis(
        key="naive_universe_minus_truth",
        label="naive (DEFECTIVE): every household not in the truth set",
        negative_of=lambda p: p.must_not_flag | p.neither,
        exclusion_reason="",  # nothing excluded -- that is precisely the defect
    ),
}

PUBLISHED_NEGATIVE_BASIS = "settled_not_rationing"


def check_channel_invariants(flagged, flagged_unaided, explained, explainable) -> None:
    """The two things that must be TRUE of a record channel, or it is a leak.

    Held as a named function, called by the real build, so the R15 mutation
    tests exercise the SAME code the measurement runs rather than a
    re-implementation of it (the tautology this repo keeps catching).

      1. A record can only ever SUPPRESS a flag -- it invalidates a baseline or
         explains part of a fall. An account the aided company flags but the
         unaided one does not means the channel is manufacturing suspicion out
         of a record, which no supplier record does.
      2. Nothing is explained away without a record behind it. If a false flag
         disappears where no record exists, the "channel" is reading something
         it should not be able to see.
    """
    if not set(flagged) <= set(flagged_unaided):
        raise AssertionError(
            "the record channel FLAGGED accounts the unaided detector did not: "
            f"{sorted(set(flagged) - set(flagged_unaided))[:5]} -- a record must "
            "never create a flag, only explain one away (D18)"
        )
    if not set(explained) <= set(explainable):
        raise AssertionError(
            "a false flag was explained away with no record behind it: "
            f"{sorted(set(explained) - set(explainable))[:5]} -- the channel is "
            "not record-driven (D18)"
        )


def build_populations(n_customers: int, confounders_enabled: bool = True,
                      record_channel_enabled: bool = True,
                      ) -> DetectionPopulations:
    """Run the coupled loop and partition the population into the three sets.

    Each customer is one household/detection instance. Truth = the household is
    genuinely self-rationing AND below floor with a clean payment record (W2_8
    `is_silent_hardship`) -- the DETECTABLE silent-hardship signature. Flagged =
    the C10 detector raised PPM_SELF_DISCONNECTED from observables.

    `confounders_enabled=False` reproduces the pre-D14 world (no non-budget
    drops). It is the R15 mutation instrument ONLY -- the published measurement
    never passes it, and `test_...` asserts that.

    `record_channel_enabled=False` reproduces the pre-D18 COMPANY: the same
    world, the same detector, but blind to the supplier's own CoT / void /
    install records. Every run scores BOTH companies on the same population
    (`flagged` vs `flagged_unaided` in the stats), because the point of D18 is
    the DISTANCE between what a supplier could explain away and what it does --
    a distance that cannot be seen from one of the two numbers alone.
    """
    detector = SelfRationingDetector()
    universe: set[str] = set()
    truth_set: set[str] = set()
    neither: set[str] = set()
    must_not: set[str] = set()
    flagged_set: set[str] = set()
    flagged_unaided: set[str] = set()   # the pre-D18 company, same population
    records_exist: set[str] = set()     # a record EXISTS (coverage hit)
    records_arrived: set[str] = set()   # ...and it reached us in time (latency)
    harm: dict[str, float] = {}

    n_rationing = 0
    n_low_need = 0            # below floor, not rationing (the confound)
    n_below_floor = 0
    true_positives = 0
    false_positives = 0
    missed_no_baseline = 0
    n_with_baseline = 0
    n_hard_negatives = 0      # NOT rationing, yet the meter really dropped (D14)
    confounder_mix: dict[str, int] = {c.value: 0 for c in DropConfounder}
    record_mix: dict[str, int] = {t.value: 0 for t in AccountRecordType}
    record_arrived_mix: dict[str, int] = {t.value: 0 for t in AccountRecordType}

    for i in range(n_customers):
        cid = f"W28C{i:06d}"
        universe.add(cid)
        healthy = _draw_healthy_kwh(cid)

        # SIM ground truth (hidden). Budget is drawn inside from W2_4 by cid.
        state = generate_self_rationing_state(
            customer_id=cid, healthy_annual_kwh=healthy, commodity="electricity",
            confounders_enabled=confounders_enabled,
        )

        below_floor = state.is_below_floor
        if below_floor:
            n_below_floor += 1
        if state.is_self_rationing:
            n_rationing += 1
        elif below_floor:
            n_low_need += 1
        confounder_mix[state.drop_confounder.value] += 1
        if state.is_hard_negative:
            n_hard_negatives += 1

        has_base = _has_baseline(cid)
        if has_base:
            n_with_baseline += 1

        # -- THE SUPPLIER'S OWN RECORDS (D18). Derived from the world's cause,
        # but what crosses to the company is a RECORD with a coverage gate and
        # two dates -- never the cause. Built even when the channel is off, so
        # the harness can count what was explainable either way.
        records = account_records_for(cid, state.drop_confounder)
        if records:
            records_exist.add(cid)
            for rec in records:
                record_mix[rec.record_type.value] += 1
                if rec.has_arrived(_AS_OF) and rec.effective_date >= _PERIOD_START:
                    records_arrived.add(cid)
                    record_arrived_mix[rec.record_type.value] += 1

        # -- Company observables ONLY. Baseline present only where covered.
        obs = SelfRationingObservation(
            customer_id=cid,
            commodity=state.commodity,
            observed_annual_kwh=state.observed_annual_kwh,
            baseline_annual_kwh=(state.healthy_annual_kwh if has_base else None),
            floor_kwh=state.floor_kwh,
            missed_payments=state.missed_payments,   # always 0 -- the silent channel
            arrears_open=False,
            weather_normalisation_factor=_weather_factor(cid),
            account_records=(records if record_channel_enabled else ()),
            as_of=_AS_OF,
            baseline_period_start=_PERIOD_START,
        )
        result = detector.detect(obs)
        # The SAME detector on the SAME account with the record channel removed:
        # the pre-D18 company, so every comparison below is company-vs-company on
        # one population rather than two runs of two worlds.
        unaided = detector.detect(dataclasses.replace(obs, account_records=()))
        if unaided.self_rationing_suspected:
            flagged_unaided.add(cid)

        # THE THREE POPULATIONS. DETECTABLE truth = silent hardship (rationing +
        # below floor + clean). A rationer ABOVE the floor is `neither`: not in
        # the truth set, but a flag on it is not wrong either. Everything else
        # carries the settled NOT_RATIONING label and is the real negative.
        is_truth = state.is_silent_hardship
        if state.is_self_rationing and not is_truth:
            neither.add(cid)
        elif not state.is_self_rationing:
            must_not.add(cid)
        if is_truth:
            truth_set.add(cid)
            # Harm = kWh shortfall below the plausible-living floor, deepened by
            # severity: a deeper cut = more under-heating = more harm. Both terms
            # principled, frozen (R13) -- not tuned to a gap.
            shortfall = max(0.0, state.floor_kwh - state.observed_annual_kwh)
            harm[cid] = round(shortfall * (1.0 + state.rationing_severity), 2)

        if result.self_rationing_suspected:
            flagged_set.add(cid)
            if is_truth:
                true_positives += 1
            else:
                false_positives += 1
        elif is_truth and not has_base:
            missed_no_baseline += 1

    # THE DENOMINATOR IS THE SETTLED NEGATIVE, not `universe - truth` (the D11
    # rule; the defect the D13 DISCOVER found here). The naive rate is computed
    # too and published beside it -- see `NEGATIVE_BASES`.
    n_settled_negative = len(must_not)
    fp_settled = len(flagged_set & must_not)
    n_naive = len(must_not) + len(neither)
    fp_naive = len(flagged_set - truth_set)

    # -- EXPLAINABLE vs EXPLAINED (the atom's actual question). Of the false
    # flags the pre-D18 company raised on the settled negative: how many COULD a
    # supplier have explained away (a record exists at all), and how many did it
    # actually explain (the record had arrived and bore on the drop)? The
    # difference is the price of coverage and latency, and it is published.
    fp_unaided_set = flagged_unaided & must_not
    explainable = fp_unaided_set & records_exist
    explained = fp_unaided_set - flagged_set
    check_channel_invariants(flagged_set, flagged_unaided, explained, explainable)
    n_fp_unaided = len(fp_unaided_set)
    # The COST, never left for a reader to discover: a genuine rationer who also
    # moved house or had a void is now explained away and MISSED.
    truth_explained_away = (truth_set & flagged_unaided) - flagged_set

    stats = {
        "n_customers": n_customers,
        "n_below_floor": n_below_floor,
        "n_rationing": n_rationing,
        "n_low_need_below_floor": n_low_need,
        "n_truth_detectable": len(truth_set),
        "n_neither_excluded": len(neither),
        "n_settled_negative": n_settled_negative,
        "n_hard_negatives": n_hard_negatives,
        "confounder_mix": confounder_mix,
        "confounders_enabled": confounders_enabled,
        "n_flagged": len(flagged_set),
        "true_positives": true_positives,
        "false_positives": fp_settled,
        "false_positive_rate": (fp_settled / n_settled_negative) if n_settled_negative else None,
        "false_positive_rate_naive": (fp_naive / n_naive) if n_naive else None,
        "baseline_coverage_actual": (n_with_baseline / n_customers) if n_customers else 0.0,
        "missed_because_no_baseline": missed_no_baseline,
        # -- THE OBSERVABLE CONFOUNDER CHANNEL (atom D18) --------------------
        "record_channel_enabled": record_channel_enabled,
        "record_mix": record_mix,
        "record_arrived_mix": record_arrived_mix,
        "n_records_exist": len(records_exist),
        "n_records_arrived": len(records_arrived),
        # The pre-D18 company on the SAME population -- the D14 upper bound.
        "n_flagged_unaided": len(flagged_unaided),
        "false_positives_unaided": n_fp_unaided,
        "false_positive_rate_unaided": (
            (n_fp_unaided / n_settled_negative) if n_settled_negative else None
        ),
        # COULD have explained away / DID explain away, and the shortfall
        # between them (coverage that arrived too late, or not at all).
        "n_false_flags_explainable": len(explainable),
        "n_false_flags_explained": len(explained),
        "explainable_share_of_false_flags": (
            (len(explainable) / n_fp_unaided) if n_fp_unaided else None
        ),
        "explained_share_of_false_flags": (
            (len(explained) / n_fp_unaided) if n_fp_unaided else None
        ),
        "explanation_shortfall_share": (
            ((len(explainable) - len(explained)) / n_fp_unaided) if n_fp_unaided else None
        ),
        # The price of the channel: real hardship the records talked us out of.
        "n_truth_explained_away": len(truth_explained_away),
        "missed_because_record_invalidated_baseline": len(truth_explained_away),
    }
    # `false_positives` above is the SETTLED count; the loop's running tally
    # counted a flag on `neither` as an error, which it is not.
    stats["false_positives_naive"] = false_positives
    return DetectionPopulations(
        universe=frozenset(universe),
        must_flag=frozenset(truth_set),
        neither=frozenset(neither),
        must_not_flag=frozenset(must_not),
        flagged=frozenset(flagged_set),
        harm=harm,
        stats=stats,
    )


def build_scenario(n_customers: int):
    """Backwards-compatible view: (truth_set, flagged_set, harm, stats)."""
    p = build_populations(n_customers)
    return set(p.must_flag), set(p.flagged), p.harm, p.stats


def false_flag_measures(pops: DetectionPopulations) -> Dict[str, object]:
    """Score the pair under EVERY candidate negative -- one `GapResult` per basis.

    Both are always computed. Measuring only the published one is how a
    denominator choice stops being visible; the naive basis is kept precisely
    because it is the defect this atom fixed (R12: every rate is a diagnostic).
    """
    out: Dict[str, object] = {}
    for key, basis in NEGATIVE_BASES.items():
        negatives = frozenset(basis.negative_of(pops))
        result = detection_measures(
            pops.must_flag, pops.flagged, universe=pops.universe,
            negative_set=negatives, exclusion_reason=basis.exclusion_reason,
            harm=pops.harm,
        )
        result.components["negative_basis"] = key
        result.components["negative_basis_label"] = basis.label
        result.note = (
            "W2_8 hidden pay-but-don't-heat -> observable consumption drop below "
            "the TDCV Low floor -> C10 detection, BOTH directions (atom D14). "
            f"NEGATIVE BASIS = {key}: {basis.label}. The MISS direction is driven "
            "by the smart-meter/baseline coverage blind spot (a rationer without "
            "a usable prior baseline is indistinguishable from a low-need home); "
            "the FALSE-FLAG direction is driven by the world's non-budget drop "
            "confounders (a house move, a void, a retrofit, a voluntary cut), "
            "which before D14 did not exist -- the rate was 0.0000 for ANY "
            "detector and was a property of the world, not of the company."
        )
        out[key] = result
    return out


def measure(n_customers: int = 4000):
    """The published measurement: both directions, on the settled negative, and
    (since D18) with the supplier's own record channel LIVE -- the company the
    published figure describes is the one that reads its own CoT, void and
    install records, because that is the company a real supplier is."""
    pops = build_populations(n_customers)
    measures = false_flag_measures(pops)
    stats = dict(pops.stats)
    stats["negative_basis"] = PUBLISHED_NEGATIVE_BASIS
    stats["false_flag_rate_by_basis"] = {
        k: r.components["false_flag_rate"] for k, r in measures.items()
    }
    return measures[PUBLISHED_NEGATIVE_BASIS], stats


def _git_head() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=4000)
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args()

    result, stats = measure(args.customers)

    print("W2_8 <-> C10 coupled silent-self-rationing scenario")
    print(f"  customers                    : {stats['n_customers']}")
    print(f"  below floor (any reason)     : {stats['n_below_floor']}")
    print(f"  truly self-rationing         : {stats['n_rationing']}")
    print(f"  low-need below floor (confound): {stats['n_low_need_below_floor']}")
    print("  -- THE THREE POPULATIONS --")
    print(f"  must-flag  (silent hardship) : {stats['n_truth_detectable']}")
    print(f"  NEITHER    (rationing, above floor, flag is RIGHT): "
          f"{stats['n_neither_excluded']}  <- in no denominator")
    print(f"  must-not-flag (NOT_RATIONING): {stats['n_settled_negative']}")
    print(f"  ... of which really DID drop : {stats['n_hard_negatives']}"
          "   <- the hard negatives D14 added; 0 before it")
    print(f"  confounder mix               : {stats['confounder_mix']}")
    print(f"  baseline coverage (actual)   : {stats['baseline_coverage_actual']:.4f}")
    print("  -- THE SUPPLIER'S OWN RECORDS (atom D18) --")
    print(f"  records that EXIST           : {stats['n_records_exist']}  {stats['record_mix']}")
    print(f"  ...arrived by as_of          : {stats['n_records_arrived']}  {stats['record_arrived_mix']}")
    print(f"  flagged: unaided -> with records: {stats['n_flagged_unaided']} -> {stats['n_flagged']}")
    print(f"  false flags COULD have explained: {stats['n_false_flags_explainable']}"
          f" of {stats['false_positives_unaided']}"
          f"  ({stats['explainable_share_of_false_flags']})")
    print(f"  false flags ACTUALLY explained  : {stats['n_false_flags_explained']}"
          f"  ({stats['explained_share_of_false_flags']})")
    print(f"  THE DISTANCE (coverage+latency) : {stats['explanation_shortfall_share']}")
    print(f"  PRICE: real hardship explained away: {stats['n_truth_explained_away']}")
    print(f"  flagged by detector          : {stats['n_flagged']}")
    print(f"  true positives               : {stats['true_positives']}")
    print(f"  missed for lack of baseline  : {stats['missed_because_no_baseline']}")
    print("  -- BOTH ERROR DIRECTIONS (atom D14) --")
    print(f"  recall (caught/truth)        : "
          f"{result.components['caught']}/{result.components['truth_size']} "
          f"= {1 - result.components['miss_rate']:.4f}")
    print(f"  missed_failure_rate (harm-wtd): {result.components['missed_failure_rate']}")
    for key, rate in stats["false_flag_rate_by_basis"].items():
        mark = "  <-- PUBLISHED" if key == PUBLISHED_NEGATIVE_BASIS else "  (DEFECTIVE, shown for contrast)"
        print(f"  false_flag_rate [{key}] : {rate}{mark}")
    print(f"  false_flag_rate [unaided, pre-D18 UPPER BOUND] : "
          f"{stats['false_positive_rate_unaided']}")
    print(f"  excluded (NEITHER)           : {result.components['n_excluded']}"
          f"  reason published in components")
    print(f"  baseline (g0)                : {result.baseline}")
    print(f"  GAP (mean of both directions): {result.gap}")

    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, result,
            measured_at=measured_at, run_git_commit=_git_head(),
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
