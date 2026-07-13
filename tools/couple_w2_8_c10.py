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
  3. HARNESS measures -- detection_gap(truth, flagged, harm): the harm-weighted
                         fraction of DETECTABLE silent hardship the company
                         MISSED, normalised to the flag-nobody baseline.

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
import hashlib
import subprocess
from datetime import datetime, timezone

from simulation.self_rationing import generate_self_rationing_state

from company.crm.self_rationing_detector import (
    SelfRationingDetector,
    SelfRationingObservation,
)

from background.gap_metric import detection_gap, write_gap_entry

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


def _has_baseline(cid: str) -> bool:
    """Whether the company holds a usable prior baseline (smart/advanced meter or
    read history). Deterministic Bernoulli against the coverage rate (C-S2)."""
    return _u01("baseline_coverage", cid) < _BASELINE_COVERAGE


def build_scenario(n_customers: int):
    """Run the coupled loop and return (truth_set, flagged_set, harm, stats).

    Each customer is one household/detection instance. Truth = the household is
    genuinely self-rationing AND below floor with a clean payment record (W2_8
    `is_silent_hardship`) -- the DETECTABLE silent-hardship signature. Flagged =
    the C10 detector raised PPM_SELF_DISCONNECTED from observables.
    """
    detector = SelfRationingDetector()
    truth_set: set[str] = set()
    flagged_set: set[str] = set()
    harm: dict[str, float] = {}

    n_rationing = 0
    n_low_need = 0            # below floor, not rationing (the confound)
    n_below_floor = 0
    true_positives = 0
    false_positives = 0
    missed_no_baseline = 0
    n_with_baseline = 0

    for i in range(n_customers):
        cid = f"W28C{i:06d}"
        healthy = _draw_healthy_kwh(cid)

        # SIM ground truth (hidden). Budget is drawn inside from W2_4 by cid.
        state = generate_self_rationing_state(
            customer_id=cid, healthy_annual_kwh=healthy, commodity="electricity"
        )

        below_floor = state.is_below_floor
        if below_floor:
            n_below_floor += 1
        if state.is_self_rationing:
            n_rationing += 1
        elif below_floor:
            n_low_need += 1

        has_base = _has_baseline(cid)
        if has_base:
            n_with_baseline += 1

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
        )
        result = detector.detect(obs)

        # DETECTABLE truth = silent hardship (rationing + below floor + clean).
        is_truth = state.is_silent_hardship
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

    n_non_truth = n_customers - len(truth_set)
    stats = {
        "n_customers": n_customers,
        "n_below_floor": n_below_floor,
        "n_rationing": n_rationing,
        "n_low_need_below_floor": n_low_need,
        "n_truth_detectable": len(truth_set),
        "n_flagged": len(flagged_set),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_positive_rate": (false_positives / n_non_truth) if n_non_truth else 0.0,
        "baseline_coverage_actual": (n_with_baseline / n_customers) if n_customers else 0.0,
        "missed_because_no_baseline": missed_no_baseline,
    }
    return truth_set, flagged_set, harm, stats


def measure(n_customers: int = 4000):
    truth_set, flagged_set, harm, stats = build_scenario(n_customers)
    result = detection_gap(truth_set, flagged_set, harm=harm)
    result.note = (
        "harm-weighted fraction of DETECTABLE silent self-rationing the company "
        "MISSED (W2_8 hidden pay-but-don't-heat -> observable consumption drop "
        "below the TDCV Low floor -> C10 detection). The gap is driven by the "
        "smart-meter/baseline coverage blind spot: a rationer without a usable "
        "prior baseline is indistinguishable from a low-need home. Miss-only "
        "metric; false positives reported separately."
    )
    return result, stats


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
    print(f"  DETECTABLE silent hardship   : {stats['n_truth_detectable']}  (truth set)")
    print(f"  baseline coverage (actual)   : {stats['baseline_coverage_actual']:.4f}")
    print(f"  flagged by detector          : {stats['n_flagged']}")
    print(f"  true positives               : {stats['true_positives']}")
    print(f"  false positives              : {stats['false_positives']}"
          f"  (fp rate {stats['false_positive_rate']:.4f})")
    print(f"  missed for lack of baseline  : {stats['missed_because_no_baseline']}")
    print(f"  recall (caught/truth)        : "
          f"{result.components['caught']}/{result.components['truth_size']} "
          f"= {1 - result.components['miss_rate']:.4f}")
    print(f"  baseline (g0)                : {result.baseline}")
    print(f"  GAP (harm-weighted miss)     : {result.gap}")

    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, result,
            measured_at=measured_at, run_git_commit=_git_head(),
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
