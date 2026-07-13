"""COUPLED-TRIAD runner for the W2_10 <-> C12 pair (DD channel-attribution confound).

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the ONLY
layer permitted to hold the hidden SIM truth (each customer's do-operator
counterfactual arrears probabilities -> ``delta_true``) and the company's
observable-only belief (``delta_naive``, from ``payment_channel`` + ``had_arrears``)
side by side to compute the belief-vs-truth GAP (COUPLED_TRIAD_DESIGN.md 1.3; same
role as background/gap_metric.py and the other couple_* runners). It lives in
tools/ -- NOT under saas/ or company/ -- so it is not scanned by the epistemic
verifier and may legitimately import ``simulation.*``.

THE COUPLED LOOP (3 loops, COUPLED_TRIAD):

  1. SIM adds depth   -- simulation.dd_attribution (W2_10) holds each customer's
                         hidden ORGANISATION latent (a back-door confound: it BOTH
                         raises DD adoption AND independently lowers true arrears
                         risk), the selection model, and the two do-operator
                         counterfactual arrears probabilities. ``delta_true`` (the
                         mean genuine causal DD effect) is the ANSWER KEY, read
                         HERE and NEVER by the company.
  2. COMPANY copes    -- the company NEVER sees the confound. This harness extracts
                         the two OBSERVABLES a real billing system records
                         (``payment_channel``, ``had_arrears``) and hands ONLY those
                         to saas.channel_attribution (C12), which computes
                         ``delta_naive`` = observed non-DD arrears rate - DD arrears
                         rate and credits the whole of it to the DD channel.
  3. HARNESS measures -- attribution_gap(delta_naive, delta_true) =
                         |delta_naive - delta_true| / |delta_naive|: the fraction of
                         the company's DD business case that is confound artefact.

R15 INDEPENDENCE / NOT A TAUTOLOGY. ``delta_true`` comes from the SIM's do-operator
over the hidden counterfactuals; ``delta_naive`` comes from the company's aggregate
of two observables. They are computed from DIFFERENT sources (causal answer key vs
observational cohort comparison), so the gap is a real selection-bias measurement,
not two sides trivially agreeing. If the observables perfectly recovered the causal
truth the gap would collapse to 0 -- which for a wall-respecting pair means a leak,
not a triumph (design 1.2).

NO GOAL-SEEKING (R12/R13). Nothing here (or in C12) is tuned to hit a target gap.
The selection strength, organisation->arrears protection and DD treatment effect are
W2_10's frozen director-curriculum diagnostics; the gap is whatever they produce.

DETERMINISM (C-S2). The cohort is drawn deterministically from stable per-customer
seeds (simulation.dd_attribution.draw_dd_cohort). No wall-clock, no global RNG in
the measurement. ``measured_at`` / ``run_git_commit`` for the ledger are gathered by
this harness (not by gap_metric, which never calls a clock).
"""
from __future__ import annotations

import argparse
import subprocess
from datetime import datetime, timezone

from simulation.dd_attribution import (
    draw_dd_cohort,
    population_true_treatment_effect,
)

from saas.channel_attribution import ChannelObservation, analyse_observations

from background.gap_metric import attribution_gap, write_gap_entry

WORLD_ATOM_ID = "W2_10_dd_attribution_confound"
TWIN_ATOM_ID = "C12_channel_attribution_analytics"


def build_scenario(n_customers: int, seed: int | None = None):
    """Run the coupled loop and return (result, extras).

    Draws the hidden DD cohort SIM-side, extracts ONLY the two observables per
    customer for the company, and holds ``delta_true`` (answer key) and
    ``delta_naive`` (company belief) side by side for the gap.
    """
    profiles = draw_dd_cohort(n_customers, seed=seed)

    # -- COMPANY side: observables ONLY cross into the twin. We copy just
    #    payment_channel + had_arrears; the hidden fields never leave this frame. --
    observations = [
        ChannelObservation(
            payment_channel=p.payment_channel,
            had_arrears=p.had_arrears,
        )
        for p in profiles
    ]
    company = analyse_observations(observations)
    delta_naive = company.delta_naive

    # -- HARNESS side: the causal answer key from the SIM's do-operator. --
    delta_true = population_true_treatment_effect(profiles)

    result = attribution_gap(delta_naive, delta_true)
    result.components.update({
        "delta_naive": delta_naive,
        "delta_true": delta_true,
        "arrears_rate_dd": company.arrears_rate_dd,
        "arrears_rate_non_dd": company.arrears_rate_non_dd,
        "dd_share": company.dd_share,
        "n_dd": company.n_dd,
        "n_non_dd": company.n_non_dd,
        "company_confound_flag": company.confound_flag,
    })
    result.note = (
        "fraction of the company's DD-discount business case that is SELECTION "
        "artefact: C12 delta_naive (observed non-DD arrears rate - DD arrears rate, "
        "credited wholesale to the DD channel) vs W2_10 delta_true (the do-operator "
        "causal DD effect). The DD cohort is pre-selected clean by the hidden "
        "organisation confound, so delta_naive over-credits the channel; the company "
        "cannot see this and does not correct for it."
    )
    extras = {
        "n_customers": n_customers,
        "delta_naive": delta_naive,
        "delta_true": delta_true,
        "arrears_rate_dd": company.arrears_rate_dd,
        "arrears_rate_non_dd": company.arrears_rate_non_dd,
        "dd_share": company.dd_share,
        "n_dd": company.n_dd,
        "n_non_dd": company.n_non_dd,
        "confound_flag": company.confound_flag,
        "confound_note": company.confound_note,
    }
    return result, extras


def measure(n_customers: int = 20000, seed: int | None = None):
    return build_scenario(n_customers, seed=seed)


def _git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--customers", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args()

    result, extras = measure(args.customers, seed=args.seed)

    print("W2_10 <-> C12 coupled DD channel-attribution scenario")
    print(f"  customers                 : {extras['n_customers']}")
    print(f"  DD cohort / non-DD        : {extras['n_dd']} / {extras['n_non_dd']}"
          f"  (DD share {extras['dd_share']:.4f})")
    print(f"  arrears rate DD / non-DD  : {extras['arrears_rate_dd']:.4f}"
          f" / {extras['arrears_rate_non_dd']:.4f}")
    print(f"  delta_naive (company)     : {extras['delta_naive']:.6f}"
          "   (whole difference credited to DD)")
    print(f"  delta_true  (answer key)  : {extras['delta_true']:.6f}"
          "   (do-operator causal effect)")
    print(f"  company confound flag     : {extras['confound_flag']}")
    print(f"  attribution GAP           : {result.gap}"
          "   (fraction of the DD business case that is confound)")
    print(f"    baseline (g0)           : {result.baseline}")

    if args.write_ledger:
        measured_at = datetime.now(timezone.utc).isoformat()
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, result,
            measured_at=measured_at, run_git_commit=_git_head(),
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
