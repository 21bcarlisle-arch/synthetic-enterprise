#!/usr/bin/env python3
"""What a value-pricing supplier would DO with this book, beside what today's supplier does.

REUSE: tools/couple_value_based_pricing.py
CLASS: PATTERN-REUSE
INDEX: searched "couple", "baseline", "arm", "control", "counterfactual", "clv". The COUPLED-
       RUNNER pattern is taken wholesale from `tools/couple_pb3_book_growth.py` and its
       siblings: harness code in `tools/`, outside the wall by design, the only layer allowed to
       hold the company's belief and the world's outcome side by side
       (COUPLED_TRIAD_DESIGN 1.3). The decision itself is
       `company/pricing/value_based_renewal.decide_margin` and nothing is recomputed here.
       `company/analytics/counterfactual_retention.py` was read and is NOT the same thing: it
       scores retention OFFERS against a fixed effectiveness assumption; this compares two
       PRICING RULES on the same book.

WHY IT EXISTS
-------------
Director, 2026-08-25: *"there has to be a baseline to beat. Average behaviour is the control —
the same book run by a supplier applying flat rules with no per-customer view. Without that
comparison, 'it performed well' means nothing."*

The control is free, because today's company IS it: a flat £2.00/MWh for every account. So this
runs both arms over the real book and reports what they would decide differently.

WHAT IT MEASURES, AND WHAT IT CANNOT
------------------------------------
DECISIONS, not earnings. It reports what each arm would OFFER and what each arm BELIEVES that
offer is worth. It does not report what either would earn, and it must not be read as though it
did: the value arm maximises the company's own expected value, so scoring the arms on expected
value lets the value arm win by construction — R15's tautology with money in it.

The honest earnings comparison is REALISED: the same book, the same world, run once per arm,
scored on what actually happened. That needs two full runs and is the next step.

WHETHER IT MEASURES THE COMPANY'S INFERENCE -- the thing the thesis is actually about -- IS ONE
OF TWO QUESTIONS, and only the first has moved. The belief-versus-truth block below holds the
company's churn estimate beside the world's response.

  LEG ONE, INDEPENDENCE: DISCHARGED 2026-08-31, by taking the route this module's own
  `what_would_discharge_it` names as (b). Until then the company leg was read as
  `market_conditions.MARKET_SWITCHING_RATE_PCT_BY_YEAR` -- the PRIOR, the published DESNZ series
  that the world's response also descends from, and two fits of one series disagreeing about
  noise is not a supplier knowing something. But the company does not renew on the prior:
  `company/crm/competitive_pressure` blends it with the company's OWN realised departures and
  every churn estimate downstream scales by the POSTERIOR. Pointed at what the company acts on,
  the leg reads 3.0% for 2018 against a published 19.5-20.0% and is outside the band in four of
  the six years the run priced renewals in, 17.0pp at the widest. `co_calibrated` is now False.

  LEG TWO, SKILL: NOT DISCHARGED, and it is the one binding. `tools/inference_claim` scores the
  method's own ranking at 0.333 against a null interval of 0.133-0.867 on six decisions -- it
  cannot be told from chance. So the gap is still publishable only as a MEASUREMENT. Nor is most
  of the book scored where the world is observing: past `_CALIBRATED_SAVINGS_CEILING_GBP` of
  annual shortfall the world continues its last informed slope, and the median account here sits
  well beyond that.

AND THE DIRECTION THE POSTERIOR MOVED IS NOT A CREDIT. The company over-predicted its own losses
by about 1.6x -- 22 realised against 35.2 predicted on 453 closed decisions -- so the posterior
drags its implied market rate DOWN, away from a published record the world sits on. That is
independence and inaccuracy at once, exactly the clause `inference_claim` holds: "the company's
estimator differs from the world" and "the company's estimator is bad" produce the same number.
The likelihood is one supplier's book and not a market sample, which is both why the leg is now
independent of the published series and why the number it produces is a poor estimate of it.

WHAT IT FOUND ON ITS FIRST RUN, which is why the arm is not wired to the renewal desk. See
`value_based_renewal.max_supported_rate_increase_pct` for the mechanism.

Run:  python3 -m tools.couple_value_based_pricing
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from background.gap_metric import _normalise, write_gap_entry
from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.pricing.regulated_average_margin import (
    AverageMarginUnavailable,
    average_player_margin,
)
from company.pricing.value_based_renewal import (
    FLAT_RULES,
    VALUE_BASED,
    MarginDecisionUnavailable,
    decide_margin,
    max_supported_rate_increase_pct,
)
from saas.non_commodity import standing_charge_rate
from saas.payment_behaviour import (
    CREDIT_RISK_BY_CUSTOMER,
    DEFAULT_CREDIT_RISK,
    PAYMENT_TIMING_DAYS_BY_CREDIT_RISK,
)
from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH
from simulation.churn_ceiling import WORLD_MAX_CHURN_PROBABILITY
from simulation.customer_events import _price_differential_vs_market
from simulation.market_switching_propensity import (
    _CALIBRATED_SAVINGS_CEILING_GBP,
    CALIBRATION_ANNUAL_BILL_GBP,
    churn_position_multiplier,
)
from tools import maturity_map_store as map_store
from tools.inference_claim import inference_claim

PROJECT = Path(__file__).resolve().parent.parent
BOOK_PATH = PROJECT / "site" / "data" / "customers.json"
OUT_PATH = PROJECT / "docs" / "observability" / "value_based_pricing_arms.json"


def _git_head() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT),
                             capture_output=True, text=True, timeout=30)
        return out.stdout.strip()[:12] if out.returncode == 0 else None
    except Exception:  # noqa: BLE001 -- any failure is "cannot name the commit", not "fine"
        return None


#: THE COMMIT THIS ARTEFACT WAS PRODUCED AT, resolved at import and never again -- the discipline
#: `tools/run_value_cycle_ab.py` landed in `f9866cd2a` and this file was never given. Import is when
#: Python bound the modules that will price these arms; the tree can move before the file is
#: written, and a sha read at assembly names a tree that did not make these numbers.
#:
#: A run that cannot resolve one publishes `None` and the reason, never the assembly tree's sha: the
#: whole use of this field is to let a reader tell two trees apart, and a wrong commit defeats that
#: where an admitted absence does not.
PRODUCING_COMMIT: str | None = _git_head()
PRODUCING_COMMIT_RESOLVED_AT: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_world_identity() -> dict:
    try:
        from simulation.departure_level_anchor import world_level_identity

        return dict(world_level_identity(), unavailable_because=None)
    except Exception as exc:  # noqa: BLE001 -- any failure is "cannot establish", not "fine"
        return {
            "digest": None,
            "unavailable_because": (
                "the world's departure-level block could not be read in this process ({}), so "
                "this comparison cannot name the world it priced in".format(exc)),
        }


#: WHICH WORLD, beside which code. The commit says what was BUILT; this says what departure level
#: it was built over, and that is the quantity a later reader has to compare. It is load-bearing
#: HERE specifically: `belief_versus_truth` reads the world's own response curve, so a re-fit of the
#: departure anchor moves every belief figure in this artefact without moving a single line of this
#: file. Resolved at import for the same reason `PRODUCING_COMMIT` is.
WORLD_IDENTITY: dict = _resolve_world_identity()

#: WHICH FIELDS OF THIS ARTEFACT ARE ITS RUN IDENTITY. Read by
#: `tools.promoted_artefact_claim_census` under the key `run_identity_fields` and by nothing else.
#:
#: WHAT IS DELIBERATELY OUT: `book_identity` and `world_identity.anchors` are facts about what the
#: run was measured OVER, not about which run it is. A reader citing them is not citing a run.
_RUN_IDENTITY_FIELDS = [
    "generated_at",
    "producing_commit.commit",
    "producing_commit.resolved_at",
    "world_identity.digest",
    # WHICH RUN OUTPUT, AND WHETHER ANYONE COULD READ IT AGAIN. A census grading "which run sits
    # at this path" cannot answer it from a commit and a digest: two checkouts of one commit
    # priced two different runs, so the input's own identity is part of this artefact's.
    "book_identity.read_from.run_output.path",
    "book_identity.read_from.run_output.reproducible_across_checkouts",
]


def producing_commit() -> dict:
    """The commit that made this artefact, as a block a consumer can fail closed on.

    A READ OF A CONSTANT, NOT A MEASUREMENT -- everything interesting happened at import. Calling
    `_git_head()` here would reintroduce exactly the defect the constant exists to remove.

    `unavailable_because` IS THE FAIL-CLOSED LEG. Consumers key on the ABSENCE of `commit`; they
    never meet an empty string or a placeholder sha, because a consumer that cannot tell "no
    commit" from "some commit" is the fail-open shape this field replaces.
    """
    return {
        "commit": PRODUCING_COMMIT,
        "resolved_at": PRODUCING_COMMIT_RESOLVED_AT,
        "resolved_when": (
            "at process start, when Python bound the modules that priced these arms -- NOT at "
            "artefact assembly, which is a later tree"),
        "unavailable_because": (
            None if PRODUCING_COMMIT else
            "`git rev-parse HEAD` did not answer in this process, so this comparison cannot name "
            "the code that priced it"),
    }


def world_identity() -> dict:
    """WHICH WORLD these arms were priced in. See `WORLD_IDENTITY` for why it is not the commit."""
    return dict(WORLD_IDENTITY)

#: Renewal year the comparison is struck at. The arms are compared at ONE moment so the
#: difference between them is the RULE and never the calendar.
AS_OF_YEAR = 2025

#: Months per year, for turning a bill count into the years a meter has been on supply. The book
#: publishes `bill_count` and `total_kwh` and not an EAC, so the annualisation is stated here
#: rather than hidden in an expression.
BILLS_PER_YEAR = 12.0

#: THE ONE SERIES BOTH SIDES OF THIS PAIR WERE FITTED FROM. The coupled measurement below is
#: read as "the company's inference against the world's truth", and that reading requires the two
#: to be INDEPENDENT. They are not. The world's response and the company's estimator descend from
#: the same published market-level switching counts, so the gap between them is, at least in part,
#: two calibrations of one series disagreeing about noise -- an arithmetic residue wearing the
#: costume of a company knowing something.
SHARED_CALIBRATION_SERIES = (
    "DESNZ electricity switching series 2015-2025, cross-referenced with the Ofgem Consumer "
    "Engagement Survey"
)

#: EACH SIDE'S YEAR-KEYED NUMBERS, AND THE RECORD THEY ARE JUDGED AGAINST.
#:
#: REBUILT 2026-08-30, DIRECTOR: "A witness that matches one sentence in one file was never a
#: guard; it's a tripwire that any unrelated edit can move. Rebuild it so it answers the actual
#: question -- do the company's estimator and the world's response descend from the same record --
#: and make it fail-closed when it cannot tell. It should be impossible for a docstring change
#: anywhere to lift it."
#:
#: WHAT THE OLD ONE DID AND HOW IT FAILED. It asked whether a fixed SENTENCE appeared in each
#: side's source file, reasoning that "if either side is ever genuinely re-calibrated from an
#: independent source, its witness leaves its source file and the refusal lifts by itself." The
#: intent was right. The mechanism could not tell re-calibration from any other edit -- and on
#: 2026-08-30 the world's sentence left its file because it was a FALSE CLAIM being deleted (the
#: curve was never calibrated to that series and said it was). Deleting a lie lifted a publication
#: refusal, at the exact moment the two sides became MORE coupled: the world's level had just moved
#: onto the published record via `departure_level_anchor`, which is the record the company's
#: estimator also descends from. A guard that a correction can switch off is not a guard.
#:
#: WHAT THIS ONE DOES. It asks the question of the NUMBERS. Both sides carry a year-keyed table
#: about GB domestic switching; the commons artefact states, per year, the band the published
#: record bears. A side whose table lies inside that band for the years the record covers IS
#: calibrated to the record, whatever its docstring says. Two such sides descend from one record,
#: which is the question. Prose cannot move it in either direction.
#:
#: WHY "AGREES WITH THE RECORD" IS THE RIGHT OPERATIONALISATION, and its one honest weakness: two
#: independently-derived tables could in principle both land inside the band by coincidence, and
#: would be scored co-calibrated. That error is in the FAIL-CLOSED direction -- it refuses
#: publication -- and the band is deliberately narrow (`test_switching_rate_commons` asserts it is
#: "narrower than the thing it is meant to discriminate"), so the coincidence is not a cheap one.
#: The opposite error, scoring genuinely-coupled sides independent, is the one that publishes a
#: false claim, and it is the one this design makes hard.
_SHARED_RECORD = "docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json"

#: side -> (dotted module, what it reads).
#:
#: POINTED AT WHAT THE COMPANY ACTS ON, NOT WHAT IT STARTS FROM, 2026-08-31. This leg used to read
#: `company.crm.market_conditions.MARKET_SWITCHING_RATE_PCT_BY_YEAR` -- the PRIOR, and the
#: company does not renew on the prior. `company/crm/competitive_pressure` already blends that
#: prior with the company's own realised departures and every churn estimate scales by the
#: POSTERIOR. Grading the prior was grading the table the company starts from against a world it
#: has since observed, which is the guard checking a quantity nothing downstream uses.
#:
#: WHAT THE PRODUCT MEANS, said out loud because the ratio is the load-bearing step. The prior is
#: a market-wide switching rate in percent. The posterior/prior ratio is the correction the
#: company's OWN BOOK put on its competitive-pressure multiplier -- realised departures over
#: predicted ones, precision-weighted. The multiplier is the rate table normalised, so the two are
#: one quantity in two units and the ratio applies to either. The product is therefore "the
#: market-wide rate the company's acted belief implies", which is exactly what the world leg is
#: quoted in. It is ALSO why that number is a poor market estimate: the likelihood is one
#: supplier's book, not a market sample. Independence and inaccuracy at once -- see
#: `tools/inference_claim`, which is the reason this guard's verdict does not by itself publish.
_SIDE_TABLES = {
    "company": ("company.crm.competitive_pressure",
                "CompetitivePressureLedger.reading (posterior, prior x ratio**w)"),
}

#: The company's PRIOR, kept separately because the posterior is expressed as a correction to it
#: and because the artefact reports the two side by side. A reader who cannot see both cannot
#: tell a belief that MOVED from one that could not.
_COMPANY_PRIOR_TABLE = ("company.crm.market_conditions", "MARKET_SWITCHING_RATE_PCT_BY_YEAR")

#: WHERE THE COMPANY'S OWN RENEWAL EXPERIENCE IS READ FROM, and it has to be an artefact of a real
#: run: the ledger is run-scoped state (`pressure_ledger_scope`) and outside a run the posterior
#: IS the prior. `tools/_ladder_chase_arm` already books the ledger out at the end of every run it
#: drives, so this reads that census rather than minting a second recorder for one quantity.
#:
#: THE CHASE-ON ARM IS THE CANONICAL WORLD -- `_ladder_chase_arm` only redirects
#: `AGGRESSION_PATH` for arm "off", so "on" is the committed default the company actually lives
#: in. Grading the company against a world configuration it does not inhabit would be measuring
#: a counterfactual supplier.
_COMPANY_POSTERIOR_CENSUS = (
    PROJECT / "docs" / "observability" / "ladder_chase_on_founder_2021.ledger_census.json"
)

#: The world's side is not a table but a function, and it is read through the SAME instrument the
#: commons is read through so the two cannot drift apart.
_WORLD_RATE_READER = ("simulation.market_switching_propensity", "market_departure_rate_pct")


def _published_bands() -> dict:
    """The record's per-year band, via the instrument that measures the world against it."""
    from tools.measure_departure_level import published_bands

    return published_bands()


def _company_posterior_readings(bands: dict) -> tuple[dict, str]:
    """The company's ACTED competitive-pressure belief, year by year, with its prior beside it.

    Returns `({}, reason)` at every step it cannot complete, and the reason is carried to the
    artefact rather than collapsed into "no overlapping year": a leg that cannot say WHY it is
    blind is a leg nobody can unblind.

    FAIL-CLOSED ON AN UNARMED LEDGER, and that is the one branch worth reading twice. An unarmed
    ledger's `reading()` returns the prior by design -- `arm_loss_reporting` documents why. If
    this returned those numbers they would be the PRIOR wearing a posterior's label, the guard
    would grade the prior while reporting that it graded the posterior, and the change made here
    would be undetectable from the artefact. So an unarmed ledger is "cannot tell", which the
    caller reads as co-calibrated.

    ONLY YEARS THE RUN PRICED RENEWALS IN. `reading()` is defined for any year -- past the end of
    the run it keeps returning the last closed window's ratio -- but a year the run never reached
    is a year the company held no belief in, and extrapolating one would put four invented rows
    in front of a reader who is being asked whether the belief moved.
    """
    import importlib

    try:
        census = json.loads(_COMPANY_POSTERIOR_CENSUS.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, (f"the company's own renewal ledger could not be read from "
                    f"{_COMPANY_POSTERIOR_CENSUS.name}: {type(exc).__name__}")
    runs = census.get("runs") or []
    if not runs:
        return {}, f"{_COMPANY_POSTERIOR_CENSUS.name} carries no run to read a ledger from"
    # RUN 0 IS THE FLAT-RULES CONTROL -- the census `run_order` names it, and it is today's
    # company. The rungs after it are price experiments, not what the book was run on.
    booked = runs[0]
    if not booked.get("armed"):
        return {}, ("the run's competitive-pressure ledger was never armed, so its posterior is "
                    "the prior and reading it as a posterior would be a tautology")
    try:
        cp = importlib.import_module("company.crm.competitive_pressure")
        prior_rates = getattr(
            importlib.import_module(_COMPANY_PRIOR_TABLE[0]), _COMPANY_PRIOR_TABLE[1])
        ledger = cp.CompetitivePressureLedger()
        ledger.arm_loss_reporting()
        ledger.decisions_by_year = {
            int(y): int(n) for y, n in (booked.get("decisions_by_year") or {}).items()}
        ledger.expected_by_year = {
            int(y): float(v) for y, v in (booked.get("predicted_losses_by_year") or {}).items()}
        ledger.losses_by_year = {
            int(y): int(v) for y, v in (booked.get("realised_losses_by_year") or {}).items()}
    except Exception as exc:
        return {}, f"the company's posterior could not be rebuilt: {type(exc).__name__}"
    if not ledger.decisions_by_year:
        return {}, "the run priced no renewals, so there is nothing for a posterior to move on"

    out: dict[int, dict] = {}
    for year in sorted(set(ledger.decisions_by_year) & set(bands)):
        prior_rate = prior_rates.get(year)
        reading = ledger.reading(year)
        if prior_rate is None or not reading.prior:
            continue
        out[year] = {
            "year": year,
            "prior_pct": round(float(prior_rate), 2),
            "posterior_pct": float(prior_rate) * (reading.multiplier / reading.prior),
            "moved_from_prior": reading.moved_from_prior,
            "ratio": None if reading.ratio is None else round(reading.ratio, 4),
            "weight": round(reading.weight, 4),
            "closed_decisions": reading.decisions,
            "predicted_losses": round(reading.expected_losses, 2),
            "realised_losses": reading.observed_losses,
            "basis": reading.basis,
        }
    if not out:
        return {}, "no year the run priced renewals in is covered by the published record"
    return out, ""


def _side_rate_table(side: str, bands: dict) -> dict:
    """One side's year-keyed reading as a rate in percent, or {} if it cannot be read."""
    import importlib

    try:
        if side == "world":
            dotted, fn_name = _WORLD_RATE_READER
            fn = getattr(importlib.import_module(dotted), fn_name)
            return {y: float(fn(y)) for y in bands}
        readings, _why = _company_posterior_readings(bands)
        return {y: r["posterior_pct"] for y, r in readings.items()}
    except Exception:
        return {}


#: The published band is quoted to one decimal place; a difference smaller than that is not a
#: disagreement with it, it is arithmetic.
_BAND_EPS = 1e-6


def _sides_are_indistinguishable(a: dict, b: dict, bands: dict) -> dict:
    """Do the two sides' own series differ by less than the record's own precision, everywhere?

    THE SECOND LEG, AND THE ONE THAT CLOSES THE REAL HOLE. Leg one asks whether each side agrees
    with the RECORD, which catches the case both sides ARE the record. It does not catch two sides
    that share some OTHER source and are both off the record -- and that case is live here, because
    the company's own docstring says its table "mirrors `simulation.market_switching_propensity`,
    reimplemented rather than re-derived". Two re-fits of one abandoned curve are exactly the
    "arithmetic residue wearing the costume of a company knowing something" this guard exists for,
    and leg one alone would score them independent.

    The threshold is the record's OWN band width for that year, not a number chosen here: two
    series closer than the record's precision are not distinguishable as different fits of
    anything. Fail-closed -- no overlapping years returns None, "cannot tell".
    """
    overlap = sorted(set(a) & set(b) & set(bands))
    if not overlap:
        return {"indistinguishable": None, "years_checked": 0, "max_divergence_pp": None,
                "why_unknown": "the two sides share no year the record covers"}
    gaps = {y: abs(a[y] - b[y]) for y in overlap}
    worst_year = max(gaps, key=gaps.get)
    apart = [y for y in overlap if gaps[y] > (bands[y][1] - bands[y][0]) + _BAND_EPS]
    return {
        "indistinguishable": not apart,
        "years_checked": len(overlap),
        "max_divergence_pp": round(gaps[worst_year], 2),
        "max_divergence_year": worst_year,
        "years_further_apart_than_the_band_is_wide": apart,
    }


def _agrees_with_the_record(rates: dict, bands: dict) -> dict:
    """Does this side's table lie inside the published band everywhere the record covers?

    FAIL-CLOSED at every step. An empty table, or one that covers none of the record's years,
    returns `agrees=None` -- "cannot tell" -- which the caller reads as co-calibrated, never as
    independent.
    """
    overlap = sorted(set(rates) & set(bands))
    if not rates or not overlap:
        return {"agrees": None, "years_checked": 0, "years_outside": [],
                "why_unknown": "no year of this side's table overlaps the published record"}
    # THE BAND IS QUOTED TO ONE DECIMAL PLACE, so the comparison is too. Without `_BAND_EPS` the
    # world's 2017 reading -- which IS the record, read straight back out of it -- came to
    # 14.000000000000002 against a band top of 14.0 and scored OUTSIDE. A float artefact would
    # then have been read as "this side is not fitted to the record", i.e. as evidence of
    # independence, which is the direction that publishes. Measured, not hypothesised.
    outside = [
        {"year": y, "reads_pct": round(rates[y], 2),
         "band_pct": [bands[y][0], bands[y][1]]}
        for y in overlap
        if not (bands[y][0] - _BAND_EPS <= rates[y] <= bands[y][1] + _BAND_EPS)
    ]
    return {"agrees": not outside, "years_checked": len(overlap), "years_outside": outside}


#: The two sentences a reader of the artefact needs, hoisted so the record-unreadable
#: branch and the normal branch cannot drift into saying different things.
_WHY_IT_DISQUALIFIES = (
        "A belief-versus-truth gap is quotable as evidence of the company's INFERENCE only if "
        "the two sides were arrived at independently. Both of these were fitted from the same "
        "market-level switching counts, so a small gap can be shared arithmetic and a large "
        "one can be two fits disagreeing about noise. Neither reading distinguishes a company "
        "that knows something from one that shares a source with the world it is being "
        "scored against."
)

_WHAT_WOULD_DISCHARGE = (
        "ONE of: (a) the world leg re-calibrated from a series the company cannot read -- a "
        "SUPPLIER-level churn series against that supplier's own position versus the market "
        "(the 2018-19 small-supplier failures and the SoLR events are where to look), which "
        "`churn_position_multiplier` already names as the thing that would settle its own "
        "extrapolation; or (b) the company estimator re-fitted from its OWN observed "
        "departures rather than the published market series, which is what a real supplier "
        "actually has and this one does not yet use. Scoring the pair inside the calibrated "
        "window does NOT discharge it -- that removes the extrapolation flag below and leaves "
        "the shared source untouched. Neither does the realised two-run earnings comparison "
        "named in this module's docstring, but that comparison does not need this to be "
        "discharged: it scores what happened, not two curves against each other."
)


def shared_calibration_holds() -> dict:
    """Do the company's estimator and the world's response still descend from ONE series?

    FAIL-CLOSED, DELIBERATELY. A witness file that cannot be read leaves the pair recorded as
    CO-CALIBRATED and therefore unpublishable, because "we could not check" is not "they are
    independent" -- an unavailable check is a failed check (R15 fail-silent).

    Returns the record itself rather than a bare bool: a reader of
    `docs/observability/value_based_pricing_arms.json` must be able to see the shared provenance,
    both witnesses, and what would discharge it, without opening a source file.
    """
    try:
        bands = _published_bands()
    except Exception as exc:
        # THE RECORD ITSELF IS UNREADABLE. Every side is then undecidable, so the pair is
        # co-calibrated and the gap is unpublishable. "We could not check" is not "they are
        # independent" -- and this is the branch where that sentence does the most work.
        return {
            "co_calibrated": True,
            "series": SHARED_CALIBRATION_SERIES,
            "record": _SHARED_RECORD,
            "sides": {},
            "undecidable": ["the published record could not be read: "
                            f"{exc.__class__.__name__}: {str(exc)[:80]}"],
            "why_it_disqualifies_the_gap": _WHY_IT_DISQUALIFIES,
            "what_would_discharge_it": _WHAT_WOULD_DISCHARGE,
        }

    sides, undecidable = {}, []
    for side in ("world", "company"):
        rates = _side_rate_table(side, bands)
        verdict = _agrees_with_the_record(rates, bands)
        source = (_WORLD_RATE_READER[0] if side == "world" else _SIDE_TABLES[side][0])
        sides[side] = {
            "source": source,
            "reads": (_WORLD_RATE_READER[1] if side == "world" else _SIDE_TABLES[side][1]),
            "descends_from_the_record": verdict["agrees"],
            "years_checked": verdict["years_checked"],
            "years_outside_the_band": verdict["years_outside"],
        }
        if "why_unknown" in verdict:
            sides[side]["why_unknown"] = verdict["why_unknown"]
        if side == "company":
            # BOTH READINGS SIDE BY SIDE, because "the belief did not move" and "the belief
            # cannot move" are the two facts this leg exists to tell apart, and a reader given
            # only the posterior cannot tell them apart at all.
            readings, why_blind = _company_posterior_readings(bands)
            sides[side]["prior_source"] = ".".join(_COMPANY_PRIOR_TABLE)
            # `os.path.relpath`, not `Path.relative_to`: the latter RAISES on a path outside the
            # project, which turns the guard's own reporting line into a crash on exactly the
            # branch -- a redirected or absent census -- that the fail-closed path exists for.
            sides[side]["ledger_read_from"] = os.path.relpath(
                _COMPANY_POSTERIOR_CENSUS, PROJECT)
            sides[side]["prior_and_posterior_by_year"] = [
                {**r, "posterior_pct": round(r["posterior_pct"], 2)}
                for r in readings.values()
            ]
            sides[side]["years_the_belief_moved"] = sorted(
                y for y, r in readings.items() if r["moved_from_prior"])
            if why_blind:
                sides[side]["why_unknown"] = why_blind
        if verdict["agrees"] is None:
            undecidable.append(source)

    pairwise = _sides_are_indistinguishable(
        _side_rate_table("world", bands), _side_rate_table("company", bands), bands)
    if pairwise["indistinguishable"] is None:
        undecidable.append("the two sides could not be compared with each other")

    # CO-CALIBRATED unless a side is DEMONSTRABLY off the record. `None` (cannot tell) counts as
    # co-calibrated, which is the fail-closed direction: independence has to be shown, never
    # inferred from an absence. Only a side whose own numbers sit OUTSIDE the published band --
    # a positive demonstration that it was not fitted to the record -- can lift this.
    # TWO LEGS, EITHER OF WHICH MEANS SHARED DESCENT.
    #
    # (a) both sides agree with the RECORD -- then both ARE the record. `all`, not `any`: with one
    #     side demonstrably off the record they are not both fitted to it, and `any` would have
    #     read "one side is on the record" as co-calibrated, which is the branch that publishes.
    # (b) the two sides are indistinguishable FROM EACH OTHER -- then they share a source whatever
    #     it is, including one neither the record nor this tool knows about.
    #
    # Independence therefore requires BOTH legs to fail, and each leg fails closed on "cannot
    # tell": independence is demonstrated, never inferred from an absence.
    both_on_the_record = all(s["descends_from_the_record"] is not False for s in sides.values())
    same_as_each_other = pairwise["indistinguishable"] is not False
    co_calibrated = both_on_the_record or same_as_each_other
    return {
        "co_calibrated": co_calibrated,
        "series": SHARED_CALIBRATION_SERIES,
        "record": _SHARED_RECORD,
        "sides": sides,
        "both_sides_on_the_record": both_on_the_record,
        "sides_indistinguishable_from_each_other": pairwise,
        "undecidable": undecidable,
        "why_it_disqualifies_the_gap": _WHY_IT_DISQUALIFIES,
        "what_would_discharge_it": _WHAT_WOULD_DISCHARGE,
    }


#: THE RUN OUTPUT A SECOND CHECKOUT CAN RESOLVE, and the one the book is already built from.
#: `tools/generate_customers_json.generate` reads exactly this path to produce
#: `site/data/customers.json`, and unlike every dated sibling it is TRACKED IN GIT -- so which
#: bytes it holds is decided by the commit, not by which working copy happens to be on this disk.
#: That is the property the glob below does not have and cannot be given.
TRACKED_RUN_OUTPUT = PROJECT / "docs" / "reports" / "run_output_latest.json"


def latest_run_output(reports_dir: Path | None = None) -> Path:
    """The newest dated run output BY NAME. Raises rather than returning None: an arms comparison
    with no book is not an empty comparison, it is one that did not run.

    NO LONGER THE DEFAULT, and that is the repair rather than a preference -- `resolve_run_output`
    is. Kept reachable because a run that has just finished and has not yet been reduced into
    `run_output_latest.json` is a legitimate thing to price. It is now opted into BY NAME, and the
    artefact records that a reading taken this way is not reproducible.
    """
    reports = Path(reports_dir) if reports_dir else (PROJECT / "docs" / "reports")
    dated = [p for p in glob.glob(str(reports / "run_output_*.json"))
             if "2026" in Path(p).name]
    if not dated:
        raise MarginDecisionUnavailable("no dated run output to read a book from")
    return Path(max(dated, key=lambda p: p.rsplit("_", 1)[-1]))


def _how(resolved_by: str, reproducible: bool, selected_by: str) -> dict:
    """One selection, in the shape the artefact publishes it. `reproducible_across_checkouts` is
    a SEPARATE field from `resolved_by` on purpose: a reader grading a re-run needs the answer,
    not a tier name they have to know this file to interpret."""
    return {"resolved_by": resolved_by,
            "reproducible_across_checkouts": reproducible,
            "selected_by": selected_by}


def resolve_run_output(explicit: str | Path | None = None, *, prefer_newest: bool = False,
                       reports_dir: Path | None = None) -> tuple[Path, dict]:
    """WHICH run output this comparison prices, and WHETHER a second checkout would agree.

    Returns `(path, how)`. Both halves go on the artefact, because "which run" and "could anyone
    re-derive this" are two questions and until now only the first was answerable.

    THE DEFECT THIS ENDS. The only answer used to be `latest_run_output()` -- the lexical max of a
    glob over `docs/reports/run_output_*.json`, every one of which is UNTRACKED. Measured
    2026-09-16 at one commit from two checkouts of it:

        shared tree      6,219 candidates -> run_output_edded3973_20260916T085959Z.json  27.5 MB
        linked worktree      4 candidates -> run_output_f5808bd_20260618T054253Z.json   205.9 KB

    Same code, same commit, same command; a run from that morning against one from June holding 14
    accounts. `79f7484f3` made the choice VISIBLE in every artefact this producer writes. It did
    not make a re-run REPRODUCIBLE -- and a repair that cannot be re-run against the published
    reading cannot be graded, which is the cost this selection has actually charged twice.

    THE FIX IS NOT A NEW POINTER FILE, and that is the whole of why it is small.
    `docs/reports/run_output_latest.json` is ALREADY tracked in git and is ALREADY the file
    `tools/generate_customers_json` builds `site/data/customers.json` from. Defaulting to it makes
    the run and the book one run by construction -- which is the same defect's other half, the one
    that left the published 397-account artefact joining only 81 of its accounts to the book then
    on disk. The glob's `"2026" in name` filter is exactly what excluded it.

    PRECEDENCE, each tier saying what it is worth:

      * `explicit` -- `--run-output PATH`, or `generate(run_path=...)`. Reproducible: the caller
        named it. A named path that does not exist RAISES rather than falling through, because a
        silent fallback from a named path is how the wrong world gets priced quietly.
      * `prefer_newest` -- `--adopt-latest`. The old behaviour, opted into by name, and recorded
        as NOT reproducible. Not deleted: a dial that orders work, never zeroes it.
      * the tracked run output, if this checkout has it. The default.
      * nothing -- RAISES, naming the missing file and how many candidates the glob would have had
        to choose from here. "We cannot tell" is a result; silently picking one of 6,219
        unreviewed files is not.
    """
    reports = Path(reports_dir) if reports_dir else (PROJECT / "docs" / "reports")
    tracked = reports / TRACKED_RUN_OUTPUT.name
    if explicit is not None:
        path = Path(explicit)
        if not path.is_file():
            raise MarginDecisionUnavailable(
                "the run output named by the caller does not exist: {}".format(path))
        return path, _how("argument", True, "named by the caller: {}".format(path))
    if prefer_newest:
        path = latest_run_output(reports)
        return path, _how(
            "newest_by_name", False,
            "lexical max over the glob `run_output_*.json` restricted to names containing "
            "'2026' -- NOT a content check, and the candidate set differs between checkouts of "
            "one commit because these files are untracked. Opted into with --adopt-latest, so "
            "this reading is NOT reproducible from the commit alone.")
    if tracked.is_file():
        shown = (tracked.relative_to(PROJECT) if tracked.is_relative_to(PROJECT) else tracked)
        return tracked, _how(
            "tracked_run_output", True,
            "`{}`, which is TRACKED IN GIT and is the same file `tools/generate_customers_json` "
            "builds the book from -- so a second checkout of this commit reads the same run, and "
            "the run and the book are one run by construction".format(shown))
    raise MarginDecisionUnavailable(
        "no reproducible run output: {} is not in this checkout. Pass --run-output PATH to name "
        "one, or --adopt-latest to take the newest of the {} untracked candidate(s) here and have "
        "the artefact record that the reading is not reproducible.".format(
            tracked, _run_output_candidate_count(reports)))


def _legs(book: dict) -> dict:
    out = {}
    for customer in book.get("customers") or []:
        for leg in (customer.get("legs") or {}).values():
            cid = leg.get("cid")
            if cid:
                out[cid] = leg
    return out


def book_at_read(run_path: Path, book_path: Path, run: dict, book: dict,
                 how: dict | None = None) -> dict:
    """WHICH TWO FILES this comparison priced, snapshotted BY THE CALLER as it read them.

    The sibling producer's `book_at_run` snapshots per arm because an arm there is a two-hour
    phase-4c pass and the curriculum can move between arms. **That is not the free variable here**,
    and propagating it verbatim would have missed the one that is. Both arms in this file are
    priced in ONE loop over ONE `per_customer_lifetime`, so they cannot be on two books and no
    cross-arm comparison has a reachable FAIL branch -- see `inputs_agree_on_the_book`.

    WHAT CAN DIFFER, AND DID, is which pair of INPUT FILES the process read, because both are
    regenerated independently by other lanes and neither is named anywhere in the output.
    `latest_run_output()` takes the lexical max of a glob over `docs/reports/run_output_*.json`,
    and those files are UNTRACKED. Measured 2026-09-16 at one commit, from two checkouts of it:

        shared tree      6,219 candidates -> run_output_edded3973_20260916T085959Z.json   27.5 MB
        linked worktree      4 candidates -> run_output_f5808bd_20260618T054253Z.json    205.9 KB

    Same code, same commit, same command; a run from this morning against a run from June, one
    holding 14 accounts and the other tens of thousands. Nothing in the artefact said which, so the
    published 397-account reading and a 226-account re-run read as rival calibrations of one book
    when they were two different books -- `SEAT_RESULT_THE_TWO_BLIND_ARM_ARTEFACTS_ARE_TWO_WORLDS_
    NOT_TWO_CALIBRATIONS_AND_NEITHER_CAN_GRADE_THE_OTHER_2026-09-16`, which cost a full Lane 0
    invocation to establish by hand.

    `served_segments` is recorded in the sibling's shape so the two artefacts can be read against
    each other at all, with the override kept SEPARATELY from the resolved list for the sibling's
    reason: an env-overridden run and a curriculum run are different claims even when they resolve
    the same.
    """
    from simulation.live_population import served_segments

    override = os.environ.get("SE_SERVED_SEGMENTS", "").strip()

    def _stat(path: Path) -> dict:
        try:
            st = path.stat()
            return {"bytes": st.st_size,
                    "mtime": datetime.fromtimestamp(
                        st.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        except OSError as exc:
            return {"bytes": None, "mtime": None, "unavailable_because": str(exc)}

    # The run's OWN stamp where it carries one, rather than a re-derivation from the filename:
    # the filename is a convention and `_cache_meta` is what the producer wrote.
    meta = run.get("_cache_meta") if isinstance(run.get("_cache_meta"), dict) else {}
    # THE JOIN, MEASURED HERE, because this is the only place both files are in hand. It must NOT
    # be re-derived from `compare`'s output: `accounts_skipped` counts an account the book has
    # never heard of in the same bucket as one the book holds with no consumption, so
    # `priced + skipped` equals the run's account count whatever the book is -- a denominator that
    # tracks its own numerator, and a control that cannot fail. Caught by its own test.
    run_ids = set(run.get("per_customer_lifetime") or {})
    book_ids = set(_legs(book))
    return {
        "run_output": {
            "path": str(run_path.relative_to(PROJECT)) if run_path.is_relative_to(PROJECT)
                    else str(run_path),
            #: WHETHER THIS FILE IS THE TRACKED ONE, by identity with the path the default
            #: tier resolves and never by name alone: a `run_output_latest.json` sitting in some
            #: other directory is a different file that a checkout cannot resolve, and calling it
            #: tracked would be the flattering answer.
            "tracked_in_git": run_path.resolve() == TRACKED_RUN_OUTPUT.resolve(),
            #: HOW IT WAS CHOSEN, TAKEN FROM THE CALLER'S OWN RESOLUTION and never re-derived
            #: here. Re-deriving would describe the selection this snapshot WOULD make now, which
            #: is a different measurement from the one that produced these figures -- the same
            #: mistake `book_at_read` exists to stop `book_identity` making about the book.
            "selected_by": (how or {}).get("selected_by") or (
                "NOT RECORDED BY THE CALLER -- this snapshot cannot say how the run output was "
                "chosen"),
            "resolved_by": (how or {}).get("resolved_by"),
            #: WOULD A SECOND CHECKOUT OF THIS COMMIT READ THE SAME FILE. None means the caller
            #: did not say, which is not False and must never be read as True.
            "reproducible_across_checkouts": (how or {}).get("reproducible_across_checkouts"),
            "candidates_seen": _run_output_candidate_count(),
            "producing_commit": meta.get("git_commit"),
            "generated_at": meta.get("generated_at_utc"),
            "accounts_in_per_customer_lifetime": len(run_ids),
            **_stat(run_path),
        },
        "join": {
            "run_accounts": len(run_ids),
            "book_legs": len(book_ids),
            "accounts_in_both": len(run_ids & book_ids),
            "run_accounts_absent_from_the_book": len(run_ids - book_ids),
        },
        "book": {
            "path": str(book_path.relative_to(PROJECT)) if book_path.is_relative_to(PROJECT)
                    else str(book_path),
            "generated": book.get("generated"),
            "customer_count": book.get("customer_count"),
            "legs": len(_legs(book)),
            **_stat(book_path),
        },
        "served_segments": list(served_segments()),
        "resolved_from": "SE_SERVED_SEGMENTS" if override else "curriculum",
        "override_env": override or None,
    }


def _run_output_candidate_count(reports_dir: Path | None = None) -> int | None:
    """How many files the GLOB tier would have chosen from. Still published under the tracked
    default, and that is deliberate: it is the standing evidence that two checkouts of one commit
    see different candidate sets, which is why the default is no longer the glob. A candidate set
    of 4 and one of 6,219 are different questions and the answer looks identical either way."""
    reports = Path(reports_dir) if reports_dir else (PROJECT / "docs" / "reports")
    try:
        return sum(1 for p in glob.glob(str(reports / "run_output_*.json"))
                   if "2026" in Path(p).name)
    except OSError:
        return None


def inputs_agree_on_the_book(at_read: dict | None, data: dict) -> dict:
    """Do the run output and the customers book describe the SAME population? The reachable control.

    THE SIBLING'S `same_book_across_arms` IS NOT PROPAGATED, DELIBERATELY, and this is its place.
    There, two arms are two phase-4c passes and can genuinely serve two books. Here both arms are
    decided inside one loop over one list, so a cross-arm book check compares a value with itself:
    a control whose FAIL branch does not exist, which is the exact shape `book_at_run`'s own
    docstring warns against and `docs/design/CONTROLS_THAT_CANNOT_FAIL.md` forbids. Shipping it
    would have looked like discharging this finding while guarding nothing.

    THE FREE VARIABLE IS THE JOIN. `compare` walks the run's `per_customer_lifetime` and looks each
    account up in the book by `customer_id`, and the two files are regenerated independently. That
    key is NOT stable across runs -- `C1` has appeared in two artefacts with different `eac_kwh` --
    so a run output and a book from different vintages still join, thinly and silently, and produce
    a clean complete artefact over a population that never existed. Measured in a linked worktree
    on 2026-09-16: 13 of 14 run accounts joined a 251-leg book, and the published 397-account
    artefact joins only 81 of its accounts to the book now on disk.

    TRI-STATE, and `None` is "cannot tell" -- the verdict whenever no snapshot was recorded. FAILS
    CLOSED there rather than assuming agreement, for `book_identity`'s reason: a `None` a reader
    can see beats the current answer standing in for a join nobody observed.

    NOT KEYED TO TODAY'S ANSWER. The threshold asks whether the run's accounts are MOSTLY absent
    from the book, which is a property of a mismatched pair; it does not pin a coverage figure that
    would go red the day the book legitimately grows.
    """
    snapshot = at_read if isinstance(at_read, dict) else {}
    join = snapshot.get("join") if isinstance(snapshot.get("join"), dict) else {}
    run_accounts = join.get("run_accounts")
    in_both = join.get("accounts_in_both")
    joined = None
    if isinstance(run_accounts, int) and run_accounts and isinstance(in_both, int):
        joined = in_both / run_accounts
    return {
        "same_book": None if joined is None else joined >= 0.5,
        "run_accounts": run_accounts,
        "book_legs": join.get("book_legs"),
        "accounts_in_both": in_both,
        "share_joined": None if joined is None else round(joined, 4),
        "unavailable_because": (
            None if joined is not None else
            "no snapshot of the input pair was recorded at read time, so whether the two files "
            "describe one population is not known -- stated rather than assumed, because the join "
            "succeeds thinly and silently when they do not"),
        "why_this_is_here": (
            "`compare` joins two independently-regenerated files on `customer_id`, which is not a "
            "stable key across runs. A mismatched pair still produces a complete-looking artefact "
            "over a population that never existed. This is the population control the sibling's "
            "`same_book_across_arms` plays there; a cross-arm check HERE would be a tautology."
        ),
    }


def book_identity(data: dict, at_read: dict | None = None) -> dict:
    """WHICH BOOK this priced, so the next reader does not infer it from a date.

    Dual-fuel share is here for the sibling's reason: one household is one billing account, so a
    gas leg moves cost-to-serve, churn and lifetime value together. The legs are collapsed on the
    `-g` suffix this file's own ids carry.

    FAILS CLOSED when the caller recorded nothing. The segment list is the CALLER'S snapshot, taken
    when the inputs were read, and never a fresh resolve here -- resolving here would report the
    curriculum at assembly time, which is a different measurement and would silently stand in for a
    book this comparison may never have been priced on.
    """
    rows = data.get("accounts") or []
    accounts: dict[str, set] = collections.defaultdict(set)
    for row in rows:
        cid = row.get("customer_id")
        if not isinstance(cid, str):
            continue
        # The gas leg is the same billing account as its electricity twin; `-g` is how this
        # artefact's own ids mark it, and `PROS-2025-0136`/`PROS-2025-0136g` is one household.
        accounts[cid[:-1] if cid.endswith("g") else cid].add(
            "gas" if cid.endswith("g") else "electricity")
    snapshot = at_read if isinstance(at_read, dict) else {}
    elec = sum(1 for c in accounts.values() if "electricity" in c)
    gas = sum(1 for c in accounts.values() if "gas" in c)
    dual = sum(1 for c in accounts.values() if {"electricity", "gas"} <= c)
    return {
        "served_segments": snapshot.get("served_segments"),
        "served_segments_resolved_from": snapshot.get("resolved_from"),
        "served_segments_override_env": snapshot.get("override_env"),
        "served_segments_unavailable_because": (
            None if snapshot else
            "the caller recorded no book when it read the inputs, so which segments this priced "
            "is not known -- stated rather than filled in from the current curriculum, which "
            "would report a book this comparison may never have been run on"),
        "read_from": {"run_output": snapshot.get("run_output"), "book": snapshot.get("book")}
                     if snapshot else None,
        "billing_accounts_priced": len(accounts),
        "with_an_electricity_leg": elec,
        "with_a_gas_leg": gas,
        "dual_fuel": dual,
        "dual_fuel_share_of_accounts": (dual / len(accounts)) if accounts else None,
        "what_each_count_selects": {
            "billing_accounts_priced": (
                "billing accounts with at least one PRICED leg, dual-fuel legs collapsed. Smaller "
                "than `accounts_priced`, which counts LEGS and is the unit of every other count "
                "in this file -- see `population.unit`."
            ),
        },
        "inputs_agree_on_the_book": inputs_agree_on_the_book(at_read, data),
        "why_this_is_here": (
            "So a reader can tell WHICH book a figure describes without diffing a commit date "
            "against a run timestamp. Two readings of this artefact days apart were read as rival "
            "calibrations of one book when they were two books, two worlds and two producer "
            "vintages, and nothing in the file could say so -- SEAT_RESULT_THE_TWO_BLIND_ARM_"
            "ARTEFACTS_ARE_TWO_WORLDS_NOT_TWO_CALIBRATIONS_AND_NEITHER_CAN_GRADE_THE_OTHER_"
            "2026-09-16."
        ),
    }


def belief_versus_truth(*, offered_rate: float, current_rate: float, tenure_years: float,
                        eac_kwh: float, segment: str, term_start: str) -> dict | None:
    """What the COMPANY believes would happen at its own chosen price, against what the WORLD
    would actually do. The coupled-triad measurement, at the price the decision picks.

    HARNESS ONLY, and this file is where that is allowed: `tools/` sits outside the wall and is
    the one layer permitted to hold the company's belief and the world's outcome side by side
    (COUPLED_TRIAD_DESIGN 1.3). Nothing here is reachable from `company/`.

    WHY IT IS WORTH MEASURING NOW AND WAS NOT THIS MORNING. Until `baec3efb2` the world's churn
    did not read the supplier's own price at all, so both sides were blind and the gap was
    identically zero by construction -- a guaranteed zero contributes nothing to a score. The
    world now responds, and `fbe8b0ab6` let that response reach the world's ceiling. The
    company's model still saturates at 0.95 with a floor of customers who never leave. So the
    gap is real for the first time, and it points the way the thesis says it should: a company
    that predicts badly should lose.
    """
    differential = _price_differential_vs_market(offered_rate, term_start)
    if differential is None:
        return None
    believed = float(enriched_churn_estimate(
        current_rate, offered_rate, tenure_years, float(eac_kwh), segment=segment))
    # The world's response to this position, applied to the same base the company started from,
    # so the comparison isolates the PRICE response and not the rest of the chain.
    base = float(enriched_churn_estimate(current_rate, current_rate, tenure_years,
                                         float(eac_kwh), segment=segment))
    actual = min(base * churn_position_multiplier(differential), WORLD_MAX_CHURN_PROBABILITY)
    # WHERE ON THE WORLD'S CURVE THIS ACCOUNT WAS SCORED, per account, because the curve stops
    # being a measurement partway along it. `churn_position_multiplier` reads the differential as
    # an annual shortfall against a GBP 1,700 bill and the DESNZ series informs it only to
    # GBP 400 of that; past there the world continues the LAST INFORMED SLOPE, which is a named
    # simplification and not an observation. An account scored out there is being compared against
    # an extrapolation, and a reader of one row cannot tell unless the row says so.
    shortfall_gbp = differential * CALIBRATION_ANNUAL_BILL_GBP
    beyond = differential > 0.0 and shortfall_gbp > _CALIBRATED_SAVINGS_CEILING_GBP
    if beyond:
        basis = ("EXTRAPOLATED -- GBP {:.0f}/yr past the GBP {:.0f} the series informs, on the "
                 "last measured slope".format(shortfall_gbp - _CALIBRATED_SAVINGS_CEILING_GBP,
                                              _CALIBRATED_SAVINGS_CEILING_GBP))
    elif -shortfall_gbp > _CALIBRATED_SAVINGS_CEILING_GBP:
        # THE CHEAP SIDE IS NOT THE SAME CASE and calling it "inside the window" would be false.
        # Past the ceiling the WIN leg is flat at `_MAX_RATE`, and the world defends that as a
        # real bound rather than an extrapolation: you cannot win more customers than the market
        # has engaged households to give. Not an observation either -- a saturation.
        basis = ("saturated -- GBP {:.0f}/yr of saving, past the ceiling, where the win leg is "
                 "flat at the engaged-segment maximum the world defends as a real bound".format(
                     -shortfall_gbp))
    else:
        basis = "observed -- inside the calibrated window"
    return {
        "price_differential_vs_svt": round(differential, 4),
        "company_believes_p_leave": round(believed, 4),
        "world_would_p_leave": round(actual, 4),
        "belief_error_pp": round(100.0 * (believed - actual), 1),
        "world_annual_shortfall_gbp": round(shortfall_gbp, 2),
        "world_calibration_ceiling_gbp": _CALIBRATED_SAVINGS_CEILING_GBP,
        "world_curve_beyond_calibration": beyond,
        "world_curve_basis": basis,
        #: NOT INDEPENDENT, said on the row itself. See `shared_calibration_holds`.
        "both_sides_calibrated_from": SHARED_CALIBRATION_SERIES,
    }


def _average_player(*, annual_revenue_gbp: float, eac_kwh: float) -> dict | None:
    """What Ofgem's published EBIT allowance says an efficient supplier earns on this customer.

    THE BILL BASIS IS NAMED RATHER THAN ASSUMED. The allowance's variable component scales with
    the cap level EXCLUDING EBIT, headroom and VAT. What this book publishes is `revenue_gbp` --
    this company's own revenue, which includes its GBP 2.00/MWh margin and excludes VAT. Using it
    as the base slightly OVERSTATES the average player's variable component, by 1.3975% of a
    margin that is itself tiny -- about a penny a year. Named because an unnamed approximation in
    a control is how a control stops being one.
    """
    try:
        result = average_player_margin(annual_revenue_gbp, eac_kwh, fuels=1)
    except AverageMarginUnavailable as exc:
        return {"available": False, "why": str(exc)[:120]}
    return {
        "available": True,
        "low": round(result.low_gbp_per_mwh, 2),
        "high": round(result.high_gbp_per_mwh, 2),
        "low_gbp_per_year": round(result.low_gbp_per_year, 2),
        "high_gbp_per_year": round(result.high_gbp_per_year, 2),
    }


def _average_player_summary(rows: list[dict]) -> dict:
    """THE QUESTION THE ARMS COMPARISON COULD NOT ANSWER UNTIL NOW: is the control a credible
    average player?

    Director, 2026-08-25: *"there has to be a baseline to beat. Average behaviour is the control
    ... Without that comparison, 'it performed well' means nothing."* The control has been this
    company's own flat rule, and nothing in the tree could say whether that rule was anywhere
    near average. Ofgem's Default Tariff Cap publishes the regulator's own answer.
    """
    scored = [r["average_player_gbp_per_mwh"] for r in rows
              if (r.get("average_player_gbp_per_mwh") or {}).get("available")]
    if not scored:
        return {"available": False,
                "why": "no account carried both a bill and a consumption, so no average-player "
                       "margin could be computed for any of them"}
    lows = sorted(s["low"] for s in scored)
    highs = sorted(s["high"] for s in scored)
    n = len(lows)
    median_low, median_high = lows[n // 2], highs[n // 2]
    return {
        "available": True,
        "accounts_scored": n,
        "source": "Ofgem Default Tariff Cap EBIT allowance, decision 25 August 2023, cap period "
                  "11a -- docs/domain_artefact_library/regulatory/price_cap_ebit_allowance.md",
        "median_gbp_per_mwh_low": round(median_low, 2),
        "median_gbp_per_mwh_high": round(median_high, 2),
        "this_companys_flat_rule_gbp_per_mwh": TARGET_MARGIN_GBP_PER_MWH,
        "flat_rule_as_share_of_average_low": round(TARGET_MARGIN_GBP_PER_MWH / median_low, 3)
        if median_low else None,
        "flat_rule_as_share_of_average_high": round(TARGET_MARGIN_GBP_PER_MWH / median_high, 3)
        if median_high else None,
        "what_it_means": (
            "The control this comparison scores the value arm against is this company's own flat "
            "rule. If that rule sits well below what the regulator allows an efficient supplier "
            "to earn, then an arm 'beating' it has demonstrated the control's implausibility and "
            "not its own inference -- which is the one thing the director's frame says the "
            "comparison must not do. A RANGE rather than a figure because the published "
            "allowance is dual fuel and this book is single fuel; see the source."
        ),
    }


def compare(run: dict, book: dict, as_of_year: int = AS_OF_YEAR) -> dict:
    """Both arms over every account the company has enough of its own record to price."""
    legs = _legs(book)
    per_account, skipped = [], collections.Counter()

    for cid, record in (run.get("per_customer_lifetime") or {}).items():
        leg = legs.get(cid) or {}
        total_kwh = float(leg.get("total_kwh") or 0.0)
        # THE EFFECTIVE RATE, BECAUSE "WHAT THIS CUSTOMER CURRENTLY PAYS" IS THE WHOLE BILL
        # (2026-08-31). This read `avg_rate_gbp_per_mwh`, which was the COMMODITY leg alone --
        # wholesale energy, no network charges, no levies, no standing charge, no VAT -- and then
        # used it as `current_rate_gbp_per_mwh` and derived `base_rate = current_rate -
        # TARGET_MARGIN` from it. Measured over the whole book: the commodity leg is 102.57
        # GBP/MWh against 156.42 actually paid, so every price this arm compared against was
        # anchored **1.53x low** at book level, median 1.59x per account and 4.17x at worst.
        #
        # Nothing was wrong with the field; it was correctly computed and misleadingly named, and
        # the walk that found it predicted exactly this reader. `tools/generate_customers_json`
        # now publishes `avg_commodity_rate_gbp_per_mwh` and `avg_effective_rate_gbp_per_mwh`, so
        # a caller has to choose. This one wants the effective rate and says so.
        avg_rate = float(leg.get("avg_effective_rate_gbp_per_mwh") or 0.0)
        bills = float(leg.get("bill_count") or 0.0)
        years = max(1.0, bills / BILLS_PER_YEAR)
        eac = total_kwh / years
        legacy_rate = (leg.get("avg_commodity_rate_gbp_per_mwh")
                       or leg.get("avg_rate_gbp_per_mwh"))
        if avg_rate <= 0.0 and legacy_rate:
            # THE SURFACE PREDATES THE TWO-RATE PUBLICATION, and that is its own answer rather than
            # a missing number (2026-08-31). A leg carrying `avg_rate_gbp_per_mwh` (the ambiguous
            # old name) or only `avg_commodity_rate_gbp_per_mwh` was published before the generator
            # started saying which rate is which. BOTH legacy shapes are recognised, because the
            # first version of this branch checked only the newer one and the live artefact -- the
            # one that actually exists -- carries the older. There is deliberately NO FALLBACK to the
            # commodity leg: reading it as the price is the exact defect this change fixes, and a
            # silent fallback would restore it while looking like resilience.
            skipped["the published surface carries no effective rate yet (regenerate it)"] += 1
            continue
        if eac <= 0.0 or avg_rate <= 0.0:
            # NAMED, not dropped. An account the company cannot price is a fact about its own
            # records, and a comparison that silently covers 200 of 263 accounts is a different
            # claim from one that covers all of them.
            skipped["no consumption or rate on this company's own record"] += 1
            continue
        common = dict(
            customer_id=cid,
            current_rate_gbp_per_mwh=avg_rate,
            base_rate_gbp_per_mwh=avg_rate - TARGET_MARGIN_GBP_PER_MWH,
            eac_kwh=eac,
            tenure_years=years,
            cost_to_serve_gbp_per_year=float(record.get("cost_to_serve_gbp") or 0.0) / years,
            expected_periods=min(6.0, years),
            segment=record.get("segment") or "resi",
            renewal_year=as_of_year,
            # EXPECTED COST, from the company's own records. Credit risk is the supplier's own
            # segmentation (`CREDIT_RISK_BY_CUSTOMER`, seed estimates, defaulting to medium for
            # an account it has not segmented -- which is 259 of 263 and is itself worth
            # noticing); payment timing is that segment's own expected delay; and the standing
            # charge is what this customer really pays per day and the first version forgot.
            credit_risk=CREDIT_RISK_BY_CUSTOMER.get(cid, DEFAULT_CREDIT_RISK),
            payment_delay_days=PAYMENT_TIMING_DAYS_BY_CREDIT_RISK.get(
                CREDIT_RISK_BY_CUSTOMER.get(cid, DEFAULT_CREDIT_RISK)),
            annual_revenue_gbp=float(leg.get("revenue_gbp") or 0.0) / years,
            fixed_revenue_gbp_per_year=365.0 * standing_charge_rate(
                record.get("commodity") or "electricity", record.get("segment") or "resi"),
        )
        try:
            flat = decide_margin(arm=FLAT_RULES, **common)
            value = decide_margin(arm=VALUE_BASED, **common)
        except MarginDecisionUnavailable as exc:
            skipped[str(exc)[:60]] += 1
            continue
        per_account.append({
            "customer_id": cid,
            "segment": common["segment"],
            "eac_kwh": round(eac, 1),
            "flat_margin_gbp_per_mwh": flat.margin_gbp_per_mwh,
            "value_margin_gbp_per_mwh": value.margin_gbp_per_mwh,
            "value_over_flat_multiple": round(
                value.margin_gbp_per_mwh / flat.margin_gbp_per_mwh, 1) if flat.margin_gbp_per_mwh else None,
            "implied_bill_change_pct": round(
                100.0 * (value.margin_gbp_per_mwh - flat.margin_gbp_per_mwh) / avg_rate, 1),
            "endpoint_bound": value.endpoint_bound,
            #: WHICH end, because "wanted to charge more than it may" and "wanted to charge less
            #: than it may" are opposite findings and this record used to report them as one.
            "endpoint_side": value.endpoint_side,
            #: WHICH LAWFUL CEILING THIS ANSWER WAS DECIDED UNDER, or none -- read off the
            #: arguments actually passed rather than described in a comment. This call site
            #: passes no `max_offered_rate_gbp_per_mwh`, so `ceiling_bound` below is
            #: structurally False for every account here and `endpoint_side == "ceiling"` can
            #: only mean the top of the candidate grid under the churn model's support bound.
            #: The sibling artefact (`docs/observability/value_cycle_ab.json`) prices under the
            #: Ofgem domestic cap and publishes counts with the SAME NAMES, and the two were
            #: read side by side as contradicting each other. Recorded per account so the day a
            #: ceiling is threaded through here this becomes true by itself instead of leaving
            #: a comment to rot.
            "lawful_ceiling_gbp_per_mwh": common.get("max_offered_rate_gbp_per_mwh"),
            "ceiling_bound": value.ceiling_bound,
            "extrapolation_bound": value.extrapolation_bound,
            #: How many candidates the bounds took off the grid, separately from whether that
            #: changed the answer. The two used to be the same field and the count was being read
            #: as the cause.
            "candidates_removed": value.candidates_removed,
            "withheld_reason": value.withheld_reason,
            "credit_risk": CREDIT_RISK_BY_CUSTOMER.get(cid, DEFAULT_CREDIT_RISK),
            "expected_cost_gbp_per_year": round(value.costs.total_gbp, 2) if value.costs else None,
            "bad_debt_gbp_per_year": round(value.costs.bad_debt_gbp, 2) if value.costs else None,
            "unsourced_cost_terms": list(value.costs.unsourced) if value.costs else [],
            # WHAT AN AVERAGE PLAYER WOULD HAVE EARNED on this same customer, from Ofgem's
            # published EBIT allowance. Read `company/pricing/regulated_average_margin.py` for
            # why a single-fuel answer is a RANGE. This is a COMPARATOR and never a target: the
            # value arm is not scored against it and no decision reads it.
            "average_player_gbp_per_mwh": _average_player(
                annual_revenue_gbp=float(leg.get("revenue_gbp") or 0.0) / years, eac_kwh=eac),
            "belief_vs_truth": belief_versus_truth(
                offered_rate=common["base_rate_gbp_per_mwh"] + value.margin_gbp_per_mwh,
                current_rate=avg_rate, tenure_years=years, eac_kwh=eac,
                segment=common["segment"], term_start=f"{as_of_year}-01-01"),
        })

    chosen = collections.Counter(r["value_margin_gbp_per_mwh"] for r in per_account)
    n = len(per_account)
    # The verdict READS the gap rather than restating a cause beside it -- see `_belief_clause`.
    belief = _belief_summary(per_account)
    return {
        "as_of_year": as_of_year,
        "accounts_priced": n,
        "accounts_skipped": dict(skipped),
        #: WHAT THE COUNTS BELOW ARE OVER, AND UNDER WHICH BOUNDS. See `_population`: this
        #: artefact and the realised A/B publish `endpoint_at_ceiling` under one name over two
        #: different populations under two different ceilings, and on 2026-08-26 the two were
        #: read as contradicting each other ("interior on 255 of 263" against "at the ceiling on
        #: 20 of 42"). Both were true. Neither could say so in its own words.
        "population": _population(per_account, as_of_year),
        "control": {
            "arm": FLAT_RULES,
            "margin_gbp_per_mwh": TARGET_MARGIN_GBP_PER_MWH,
            "what_it_is": (
                "what this company does today: one margin for every account, whoever they are. "
                "Imported from saas/tariff_pricing.py rather than restated, so the control "
                "cannot drift from the supplier it describes."
            ),
        },
        "average_player": _average_player_summary(per_account),
        "model_support_bound_pct": round(max_supported_rate_increase_pct(), 1),
        "differs_from_control": sum(
            1 for r in per_account if r["value_margin_gbp_per_mwh"] != TARGET_MARGIN_GBP_PER_MWH),
        "endpoint_bound": sum(1 for r in per_account if r["endpoint_bound"]),
        "endpoint_at_ceiling": sum(1 for r in per_account if r["endpoint_side"] == "ceiling"),
        "endpoint_at_floor": sum(1 for r in per_account if r["endpoint_side"] == "floor"),
        "extrapolation_bound": sum(1 for r in per_account if r["extrapolation_bound"]),
        "grid_trimmed": sum(1 for r in per_account if r["candidates_removed"]),
        #: THE SHARE OF THE BOOK ON ONE MARGIN, which is how a quantised search confesses. On
        #: 2026-08-25 this was 0.407 -- 107 of 263 accounts on exactly GBP 130/MWh, a rung of the
        #: candidate grid -- while every one of those accounts had a distinct interior optimum
        #: within a pound of a different number. A record of per-customer decisions in which two
        #: thirds of the book share two values is reporting the grid.
        "chosen_margin_concentration": round(
            max(chosen.values()) / n, 3) if n else None,
        "withheld_on_vulnerability": sum(1 for r in per_account if r["withheld_reason"]),
        "chosen_margins": {str(k): v for k, v in sorted(chosen.items())},
        "segmented_credit_risk": sum(1 for r in per_account if r["customer_id"] in CREDIT_RISK_BY_CUSTOMER),
        "median_implied_bill_change_pct": (
            sorted(r["implied_bill_change_pct"] for r in per_account)[n // 2] if n else None),
        "belief_vs_truth": belief,
        "verdict": _verdict(per_account, belief, _average_player_summary(per_account)),
        "accounts": per_account,
    }


def _population(rows: list[dict], as_of_year: int) -> dict:
    """WHICH decisions these counts are over, so they cannot be compared by name alone.

    THE DEFECT THIS DISCHARGES is a reconciliation, not an arithmetic error. This artefact and
    `docs/observability/value_cycle_ab.json` both publish `endpoint_bound`, `endpoint_at_ceiling`
    and `ceiling_bound`, computed by the same `decide_margin` — and they disagree, because they
    ask it different questions:

      * here — ONE decision per account, taken at a single moment (`as_of_year`), off a finished
        run's own record, with NO lawful ceiling passed;
      * there — one decision per RENEWAL EVENT a ten-year run actually reached, at that term's
        own rate under that term's own Ofgem cap window.

    So `endpoint_at_ceiling` does not mean the same thing in the two files, and until this block
    existed nothing in either said so. `what_endpoint_at_ceiling_means` is COMPUTED from whether
    a ceiling was in fact passed, not asserted, so it changes by itself if that ever changes.
    """
    under_ceiling = sum(1 for r in rows if r.get("lawful_ceiling_gbp_per_mwh") is not None)
    return {
        "unit": "one renewal decision per ACCOUNT, taken at a single moment",
        "as_of_year": as_of_year,
        "decisions": len(rows),
        "distinct_accounts": len({r["customer_id"] for r in rows}),
        "priced_under_a_lawful_ceiling": under_ceiling,
        "lawful_ceiling_passed": bool(under_ceiling),
        "what_endpoint_at_ceiling_means": (
            "the top of the candidate grid under the churn model's own support bound, and NOT "
            "the Ofgem price cap: this call site passes no `max_offered_rate_gbp_per_mwh`, so "
            "`ceiling_bound` is structurally False for every account here and its count is not "
            "a measurement of anything. A run that DOES price under the cap will report a far "
            "larger ceiling count on the same book and the same module, and that is not a "
            "contradiction."
            if not under_ceiling else
            "the highest margin this account could lawfully be offered -- a real ceiling was "
            "passed for {} of {} decisions, so `ceiling_bound` here is a measurement and can be "
            "compared with the realised A/B's.".format(under_ceiling, len(rows))
        ),
        "sibling_artefact": "docs/observability/value_cycle_ab.json",
    }


def _belief_summary(rows: list[dict], provenance: dict | None = None,
                    claim: dict | None = None) -> dict:
    """How wrong the company would be, at the price its own arm chooses.

    UNDER-ESTIMATES ARE COUNTED SEPARATELY because the sign is the whole story: a company that
    believes fewer customers will leave than actually will is a company that will over-price and
    be punished for it, and that is the failure mode this arm has.
    """
    scored = [r["belief_vs_truth"] for r in rows if r.get("belief_vs_truth")]
    if not scored:
        return {"available": False, "why": "no account could be scored against the world"}
    errors = sorted(s["belief_error_pp"] for s in scored)
    n = len(errors)
    beyond = sum(1 for s in scored if s.get("world_curve_beyond_calibration"))
    differentials = sorted(s["price_differential_vs_svt"] for s in scored
                           if s.get("price_differential_vs_svt") is not None)
    # INJECTABLE, so the refusal can be exercised in BOTH directions (2026-08-30). It used to
    # read live provenance unconditionally, which made every test of this block a test of today's
    # tree: the three controls below it asserted `publishable_as_evidence_of_inference is False`
    # with synthetic rows and went red the day the live verdict flipped, having never been able
    # to test the other branch at all.
    provenance = shared_calibration_holds() if provenance is None else provenance
    # THE STANDING RULE, APPLIED FROM ONE PLACE (2026-08-30). This used to be
    # `not provenance["co_calibrated"]` -- i.e. the codebase encoded "independent therefore
    # inferring" as an identity, which is precisely the thing `tools/inference_claim` corrects.
    # Independence is the FIRST of two necessary legs; the second is the method's own ranking
    # clearing the interval a random signal produces. Injectable for the same reason
    # `provenance` is.
    claim = inference_claim(provenance) if claim is None else claim
    return {
        "available": True,
        "accounts_scored": n,
        "median_belief_error_pp": errors[n // 2],
        "mean_belief_error_pp": round(sum(errors) / n, 1),
        "underestimating_departures": sum(1 for e in errors if e < -1.0),
        "median_price_differential_vs_svt": (
            round(differentials[len(differentials) // 2], 4) if differentials else None),
        "scored_beyond_the_world_calibration": beyond,
        "share_beyond_the_world_calibration": round(beyond / n, 3),
        # THE REFUSAL, AND IT IS THE POINT OF THIS BLOCK. The number above is a real
        # measurement of a real disagreement; what it is NOT is evidence that the company
        # inferred anything. Published without this, a median of a couple of percentage points
        # reads as "the company nearly knows the world" -- which is exactly what two calibrations
        # of one series look like, and exactly what a reader will quote it as.
        "publishable_as_evidence_of_inference": claim["publishable_as_evidence_of_skill"],
        # THE TWO LEGS, REPORTED APART, because they fail for different reasons and are fixed by
        # different work: the first by re-fitting one side off a series the other cannot read,
        # the second only by scoring more decisions. A single flag hid which one was binding.
        "sides_are_independent": claim["sides_are_independent"],
        "the_method_clears_its_null": claim["the_method_clears_its_null"],
        "inference_claim": claim,
        "shared_calibration": provenance,
        "refusal": "" if claim["publishable_as_evidence_of_skill"] else (
            "NOT EVIDENCE OF THE COMPANY'S INFERENCE. {} And {} of {} scored accounts were "
            "compared at a differential where the world EXTRAPOLATES rather than observes. Quote "
            "this as a measured disagreement; do not quote it as the company predicting the "
            "world. See `shared_calibration.what_would_discharge_it`."
        ).format(claim["sentence"], beyond, n),
        "what_it_means": (
            "Positive means the company expects MORE departures than the world would deliver; "
            "negative means it expects FEWER -- it will over-price and be punished. This is the "
            "shape the thesis says the advantage must come from -- but the shape is not the "
            "evidence: see `refusal` and `inference_claim.rule`."
        ),
    }


def _belief_clause(belief: dict) -> str:
    """Which of the two candidate causes the belief-vs-truth gap actually supports, READ OFF
    THE GAP rather than asserted beside it.

    The two are not the same problem and they need opposite work. If the company UNDER-estimates
    departures at its own chosen price it will over-price and be punished, and the belief is
    still wrong. If the gap is small or conservative, the belief is carrying the decision and
    what remains is whether the FLAT CONTROL is a credible average player -- because an arm that
    beats a control nobody would run measures the control, not the inference.
    """
    if not belief.get("available"):
        return ("The belief-vs-truth gap could not be scored, so which of the two causes this is "
                "cannot be read off this run.")
    median = belief["median_belief_error_pp"]
    under = belief["underestimating_departures"]
    scored = belief["accounts_scored"]
    if median < -1.0:
        return ("The belief is still the cause: the company under-estimates departures at its "
                "own chosen price on {} of {} accounts (median {:+.1f}pp), so it would "
                "over-price and be punished for it.").format(under, scored, median)
    return ("The belief is no longer the obvious cause -- the median account is scored {:+.1f}pp "
            "against the world, on the conservative side, with {} of {} under-estimating "
            "departures.").format(median, under, scored)


def _co_calibration_clause(belief: dict) -> str:
    """WHAT THE GAP ABOVE IS NOT, said in the same paragraph that quotes it.

    A caveat that lives in a nested key is a caveat nobody reads: the verdict paragraph is what
    gets pasted into a digest, so the refusal has to travel with the number rather than beside it.
    Derived from the same record the refusal is derived from, so it cannot say "co-calibrated"
    while the record says otherwise.

    REWRITTEN 2026-08-30. This clause used to read, on the independent branch: *"The two sides no
    longer share a calibration source, so that gap now speaks to the company's own inference."*
    That sentence is the standing rule's own worked example of what may not be said -- it takes
    independence for inference, and it quotes the gap with no interval anywhere near it. The
    sentence now comes from `tools.inference_claim`, which derives it from the flags rather than
    writing it beside them, so this clause cannot say something the verdict does not support.
    """
    if not belief.get("available"):
        return ""
    claim = belief.get("inference_claim") or {}
    beyond = belief.get("scored_beyond_the_world_calibration") or 0
    scored = belief.get("accounts_scored") or 0
    extrapolation = (
        " Separately, {} of {} accounts were scored where the world extrapolates the last "
        "informed slope rather than observing anything.".format(beyond, scored) if beyond else "")
    return (claim.get("sentence") or "") + extrapolation


def _control_clause(average: dict, rows: list[dict]) -> str:
    """WHETHER THE CONTROL IS A CREDIBLE AVERAGE PLAYER, answered with an external figure instead
    of left open.

    This clause used to end "what that leaves open is whether the flat control is a credible
    average player" and stop there, which is a question a reader cannot answer either. Ofgem's
    published EBIT allowance answers it, and the answer is not the convenient one: the control IS
    under-priced, and nowhere near enough to explain the arm.
    """
    if not average.get("available"):
        return ("Whether the flat control is a credible average player could not be scored on "
                "this run, so that cause stays open.")
    low = average["median_gbp_per_mwh_low"]
    high = average["median_gbp_per_mwh_high"]
    flat = average["this_companys_flat_rule_gbp_per_mwh"]
    chosen = sorted(r["value_margin_gbp_per_mwh"] for r in rows)[len(rows) // 2] if rows else 0.0
    ratio_low = chosen / high if high else 0.0
    return ("The flat control IS under-priced -- GBP {:.2f}/MWh against a regulated average of "
            "GBP {:.2f}-{:.2f} for an efficient supplier -- but not nearly enough to be the "
            "cause: the value arm's median choice of GBP {:.0f}/MWh is still {:.0f}x the TOP of "
            "that range. Repricing the control to average behaviour would move it by a factor of "
            "two to four and leave the arm's answer an order of magnitude away, so the arm is "
            "not beating a straw man -- it is asking to charge many times what a regulated "
            "efficient supplier earns.").format(flat, low, high, chosen, ratio_low)


def _verdict(rows: list[dict], belief: dict, average: dict) -> dict:
    """The one paragraph a reader needs, DERIVED, so it cannot go stale beside the numbers.

    A comparison that leaves the reader to work out whether the arm is usable will be quoted as
    though it were, and this one is not usable — see the reason it names.
    """
    if not rows:
        return {"fit_to_run": False, "why": "no account could be priced, so nothing was compared"}
    at_ceiling = sum(1 for r in rows if r.get("endpoint_side") == "ceiling")
    at_floor = sum(1 for r in rows if r.get("endpoint_side") == "floor")
    at_edge = sum(1 for r in rows if r["endpoint_bound"])
    median_change = sorted(r["implied_bill_change_pct"] for r in rows)[len(rows) // 2]
    fit = at_edge == 0 and median_change < 25.0
    if fit:
        why = ("The value arm found interior optima and moves the median bill "
               "by {:+.0f}%. ").format(median_change) + _co_calibration_clause(belief)
    else:
        # THE DIAGNOSIS IS DERIVED, NOT WRITTEN DOWN, and this paragraph is the reason that
        # rule earned itself. Until 2026-08-25 it asserted a fixed cause -- the churn model's
        # 0.95 ceiling and its floor of captive customers -- which was true when it was
        # written and became FALSE the moment the ceiling was fixed, while the verdict stayed
        # correctly False for an entirely different reason. A stale cause beside a live number
        # is worse than no cause: a reader trusts it and stops looking.
        parts = []
        # THE TWO EDGES ARE OPPOSITE FINDINGS AND THIS SENTENCE USED TO CONFLATE THEM. Until
        # 2026-08-25 any endpoint read as "chose the highest margin available", which on the
        # book that then existed happened to be true. It is not true of the floor: the accounts
        # sitting there are 190-340 kWh/year meters whose 98.55 GBP standing charge IS the
        # relationship, and whose profit-maximising COMMODITY margin is NEGATIVE -- the arm wants
        # to sell them electricity below cost to keep the standing charge, and cannot, because
        # the lowest candidate on the grid is 0.50. A reader told that as "chose the highest
        # margin available" concludes the exact opposite of what the arm found.
        if at_ceiling:
            parts.append(
                "chose the highest margin available to it on {} of {} accounts, which is a "
                "ceiling reporting itself as a decision".format(at_ceiling, len(rows)))
        if at_floor:
            parts.append(
                "wanted to price BELOW the lowest margin it may offer on {} of {} accounts -- "
                "micro-consumption meters whose standing charge is the whole relationship, where "
                "the profit-maximising commodity margin is negative and the grid's floor is what "
                "decided".format(at_floor, len(rows)))
        if median_change >= 25.0:
            parts.append(
                "would move the median bill by {:+.0f}%, far outside anything this company has "
                "ever charged or observed a customer respond to".format(median_change))
        why = ("The value arm " + " and ".join(parts) + ". Not fit to wire to the renewal desk. "
               + _belief_clause(belief) + " " + _co_calibration_clause(belief) + " "
               + _control_clause(average, rows))
    return {
        "fit_to_run": fit,
        "belief_gap_publishable_as_inference": bool(
            belief.get("publishable_as_evidence_of_inference")),
        "at_grid_edge": at_edge,
        "at_grid_edge_ceiling": at_ceiling,
        "at_grid_edge_floor": at_floor,
        "median_implied_bill_change_pct": median_change,
        "why": why,
    }


#: The coupled pair this tool measures. The WORLD owns how a household responds to its own
#: supplier's price position (`simulation/market_switching_propensity.churn_position_multiplier`,
#: reached through `customer_events`); the COMPANY owns its estimate of the same thing
#: (`company/crm/enriched_churn_estimate`). Named as atom ids because that is what the ledger and
#: the coupled-triad gate read.
WORLD_ATOM_ID = "B10_competitor_switching_response"
TWIN_ATOM_ID = "B4_competitor_field"


def coupling_is_declared() -> tuple[bool, str]:
    """Does the MAP declare this world/twin pair, or would writing the ledger invent one?

    THE LEDGER IS READ AS THE MAP'S OWN RECORD, and `tools/couple_clv.py` records what happens
    when a row's key and its actual subject come apart: a control keyed `EP1_clv_three_horizon`
    that graded a different module's belief entirely, and stayed bit-identical when its named
    subject's whole output was deleted. It called that shape MIS-SUBJECTED. A row keyed on a pair
    the map does not declare is the same defect one step earlier -- the pair itself would be this
    tool's invention, and a reader would take it for the map's.

    So the write REFUSES rather than asserting a coupling nobody declared, and says what would
    make it legal: `B10_competitor_switching_response` currently has no twin on the map, and
    naming one there is a map edit with its own owner.
    """
    try:
        from background.coupled_triad import build_coupling

        atoms = map_store.load_atoms(PROJECT / "docs" / "design" / "maturity_map.yaml")
        coupling = build_coupling(atoms)
    except Exception as exc:
        return False, f"the map's coupling could not be read ({exc!r}), so the pair is unverified"
    declared = coupling.get(WORLD_ATOM_ID)
    if declared == TWIN_ATOM_ID:
        return True, "the map declares {} -> {}".format(WORLD_ATOM_ID, TWIN_ATOM_ID)
    return False, (
        "the map does not declare {} -> {} (it says {!r}). Writing the row would invent a "
        "coupling and publish it as the map's. Declare the twin on the map first."
    ).format(WORLD_ATOM_ID, TWIN_ATOM_ID, declared)


def price_belief_gap(rows: list[dict], provenance: dict | None = None,
                     claim: dict | None = None):
    """The company's price-response belief against the world's, normalised by NO SKILL.

    THE GAP IS THE SCORE (COUPLED_TRIAD_DESIGN). The belief-vs-truth summary beside this reports
    a median error in percentage points, which says how BIASED the company is and nothing about
    whether its belief carries any information. This says the second thing, and it is the one the
    thesis is about: the no-skill baseline is a supplier that predicts the SAME departure
    probability for every account -- the population mean -- which is exactly "a supplier applying
    flat rules with no per-customer view".

    A gap above 1.0 means the company's per-customer belief is WORSE than that flat rule. That is
    a result worth publishing, not a bug: an advantage that must come from inference cannot be
    claimed by a model carrying less information than the mean.
    """
    scored = [r["belief_vs_truth"] for r in rows if r.get("belief_vs_truth")]
    if len(scored) < 2:
        return None
    believed = [s["company_believes_p_leave"] for s in scored]
    actual = [s["world_would_p_leave"] for s in scored]
    mean_actual = sum(actual) / len(actual)
    raw = sum(abs(b - a) for b, a in zip(believed, actual)) / len(actual)
    g0 = sum(abs(mean_actual - a) for a in actual) / len(actual)
    # INJECTABLE for the same reason `_belief_summary` is: the control below asserts the refusal
    # reaches the ledger ROW, and it could only ever exercise whichever branch today's tree
    # happened to be in.
    provenance = shared_calibration_holds() if provenance is None else provenance
    claim = inference_claim(provenance) if claim is None else claim
    beyond = sum(1 for s in scored if s.get("world_curve_beyond_calibration"))
    return _normalise(
        raw, g0,
        "a supplier that predicts the population-mean departure probability for every account "
        "-- flat rules, no per-customer view",
        "belief",
        {"accounts_scored": len(scored),
         "company_mean_abs_error": round(raw, 4),
         "no_skill_mean_abs_error": round(g0, 4),
         "world_mean_p_leave": round(mean_actual, 4),
         # CARRIED INTO THE COMPONENTS, not only into the prose, because the ledger row is what
         # a later reader consults and a note is the first thing an aggregator drops.
         "publishable_as_evidence_of_inference": claim["publishable_as_evidence_of_skill"],
         "sides_are_independent": claim["sides_are_independent"],
         "the_method_clears_its_null": claim["the_method_clears_its_null"],
         "co_calibrated_from": provenance["series"],
         "accounts_beyond_the_world_calibration": beyond},
        note=("Measured at the price the company's OWN value arm chooses, which is where it "
              "would actually be wrong. Below 1.0 the per-customer belief beats the flat rule; "
              "above 1.0 it is worse than predicting the mean."
              + ("" if claim["publishable_as_evidence_of_skill"] else
                 " NOT PUBLISHABLE AS EVIDENCE OF THE COMPANY'S INFERENCE: {} {} of {} accounts "
                 "were scored where the world extrapolates rather than observes.".format(
                     claim["sentence"], beyond, len(scored)))),
    )


def generate(out_path: Path | None = None, run_path: Path | str | None = None, *,
             prefer_newest: bool = False) -> dict:
    # WHICH RUN, RESOLVED ONCE AND CARRIED, never re-asked. `how` travels with the path for the
    # same reason the snapshot travels with the read: re-deriving the selection at assembly would
    # answer a question about the tree as it is now, not about the files these figures came from.
    run_path, how = resolve_run_output(run_path, prefer_newest=prefer_newest)
    run = json.loads(run_path.read_text(encoding="utf-8"))
    book = json.loads(BOOK_PATH.read_text(encoding="utf-8"))
    # SNAPSHOTTED HERE, BESIDE THE READ, and passed down -- never re-resolved at assembly. That
    # difference is the whole control rather than a style point: see `book_at_read`.
    at_read = book_at_read(run_path, BOOK_PATH, run, book, how)
    data = compare(run, book)
    # PROVENANCE FIRST IN THE FILE, above every figure it qualifies, because a reader who has to
    # scroll past 400 accounts to find out which book they describe will not scroll.
    data = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        # WHICH CODE MADE THIS. `generated_at` is the one timestamp here guaranteed NOT to be when
        # the numbers were decided.
        "producing_commit": producing_commit(),
        # WHICH WORLD, beside which code -- the departure level every belief figure below is
        # measured over, which a commit hash does not answer.
        "world_identity": world_identity(),
        # WHICH OF THESE FIELDS IS THE RUN IDENTITY, said here because only the producer knows.
        "run_identity_fields": _RUN_IDENTITY_FIELDS,
        # WHICH BOOK, and which two files it was read from.
        "book_identity": book_identity(data, at_read),
        **data,
    }
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return data


if __name__ == "__main__":
    _ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    _ap.add_argument("--write-ledger", action="store_true",
                     help="persist the measured price-belief gap into coupled_gap_ledger.json")
    _ap.add_argument("--run-output", metavar="PATH", default=None,
                     help="price THIS run output. The reproducible form: a re-run given the path "
                          "the published artefact names reads the same file this one did.")
    _ap.add_argument("--adopt-latest", action="store_true",
                     help="take the newest dated run output by name instead of the tracked one. "
                          "The pre-2026-09-16 behaviour, and NOT reproducible -- the candidate "
                          "set differs between checkouts of one commit. Recorded as such on the "
                          "artefact.")
    _args = _ap.parse_args()
    d = generate(run_path=_args.run_output, prefer_newest=_args.adopt_latest)
    # THE PROVENANCE ON THE SURFACE, not only in the file. The operator who runs this is the one
    # person who can still tell that the wrong run output was picked, and only while they are here.
    _book = d["book_identity"]
    _src = (_book.get("read_from") or {}).get("run_output") or {}
    print("read {} ({} accounts) against {}".format(
        _src.get("path"), _src.get("accounts_in_per_customer_lifetime"),
        ((_book.get("read_from") or {}).get("book") or {}).get("path")))
    # WHETHER THIS RUN CAN BE REPEATED, on the surface and not only in the file. The operator is
    # the one person who can still name a run deliberately, and only while they are here.
    if _src.get("reproducible_across_checkouts"):
        print("  selection REPRODUCIBLE ({}): {}".format(
            _src.get("resolved_by"), _src.get("selected_by")))
    else:
        print("  selection NOT REPRODUCIBLE ({}): {} of {} untracked candidate(s) in this "
              "checkout. A second checkout of this commit would read a different file; re-run "
              "with --run-output {} to repeat exactly this reading.".format(
                  _src.get("resolved_by"), 1, _src.get("candidates_seen"), _src.get("path")))
    print("code {} | world {}".format(
        d["producing_commit"]["commit"] or "UNAVAILABLE",
        d["world_identity"].get("digest") or "UNAVAILABLE"))
    _agree = _book["inputs_agree_on_the_book"]
    if _agree["same_book"] is False:
        print("  INPUTS DISAGREE ON THE BOOK: only {} of the run's accounts are in the book -- "
              "these two files are probably not from one population".format(
                  _agree["share_joined"]))
    elif _agree["same_book"] is None:
        print("  CANNOT TELL whether the inputs describe one book: {}".format(
            _agree["unavailable_because"]))
    print("priced {} account(s); {} differ from the control; {} at a grid edge".format(
        d["accounts_priced"], d["differs_from_control"], d["endpoint_bound"]))
    print("fit to run: {} -- {}".format(d["verdict"]["fit_to_run"], d["verdict"]["why"]))
    _gap = price_belief_gap(d["accounts"])
    if _gap is None:
        print("price-belief gap: NOT MEASURABLE -- fewer than two accounts could be scored "
              "against the world")
    else:
        print("price-belief gap: {} (company {} vs no-skill {})".format(
            _gap.gap, _gap.raw_gap, _gap.g0))
        if _gap.gap is not None and _gap.gap > 1.0:
            print("  -> WORSE THAN THE FLAT RULE: the per-customer belief carries less "
                  "information than predicting the population mean, so no inference advantage "
                  "can be claimed from it.")
        _declared, _why = coupling_is_declared()
        _provenance = shared_calibration_holds()
        if _provenance["co_calibrated"]:
            print("  NOT EVIDENCE OF INFERENCE: both sides descend from {}. {}".format(
                _provenance["series"], _provenance["what_would_discharge_it"]))
        if _args.write_ledger and _provenance["co_calibrated"]:
            # THE REFUSAL WITH TEETH. The ledger is where this pair is read as the company's
            # inference against the world's truth; writing a co-calibrated pair there publishes
            # shared arithmetic under that heading, and no caveat further down the file survives
            # the quoting. Refuses BEFORE the undeclared-coupling check because it is the wider
            # objection: declaring the twin on the map would not make the two sides independent.
            print("  ledger NOT written: the pair is co-calibrated, so the gap cannot be "
                  "published as evidence of the company's inference")
        elif _args.write_ledger and not _declared:
            print("  ledger NOT written: {}".format(_why))
        elif _args.write_ledger:
            _ledger = write_gap_entry(
                WORLD_ATOM_ID, TWIN_ATOM_ID, _gap,
                measured_at=datetime.now(timezone.utc).isoformat(),
                # THE COMMIT THAT PRICED IT, not the tree at the moment the ledger is written.
                # Two answers to "which commit" in one file would be two facts that drift.
                run_git_commit=PRODUCING_COMMIT,
            )
            print("  ledger written: {} -> gap={}".format(
                WORLD_ATOM_ID, _ledger[WORLD_ATOM_ID]["gap"]))
