"""LIVE per-run wiring of the W2_11 <-> D5 payment coupled triad.

This is the L3-escalation of the payment triad: the SAME belief-vs-truth flow
already built + tested OFFLINE in `tools/couple_w2_11_d5.py` (a frozen synthetic
population), run LIVE inside `simulation/run_phase2b.py` over the real run
population, once per run, writing the measured gap into the coupled gap ledger.

THE COUPLED LOOP, LIVE (COUPLED_TRIAD_DESIGN.md 1.3):

  1. SIM depth   -- `simulation.payment_behaviour_source.generate_payment_event`
                    is the CANONICAL payment TRUTH for each (customer, period).
                    run_phase2b's old `payment_timing.generate_payment_record`
                    path is REPLACED by this event; the analytics dict the run
                    still needs (`PaymentBehaviourAnalytics.record_payment`) is
                    DERIVED from this one event, so there is exactly ONE payment
                    reality per customer/period (never two generators drawing
                    conflicting results).
  2. COMPANY copes -- that truth crosses the W4_4 seam
                    (`simulation.payment_seam_adapter.emit_wall_responses`) into
                    `WallResponse`s -- the ONLY thing the company ever sees --
                    and `company.billing.payment_observation_consumer` turns the
                    stream into belief. The consumer NEVER receives the
                    `PaymentEvent` (epistemic wall; proven by the D5 module's own
                    AST import-freedom test and the offline
                    `test_consumer_never_receives_theta`).
  3. HARNESS measures -- at run end this module scores the belief-vs-truth GAP
                    using `tools.couple_w2_11_d5.score_triad` (the SAME scorer
                    the offline harness uses -- no bespoke live metric, R15
                    independence) and writes the DETECTION headline into
                    `docs/observability/coupled_gap_ledger.json` via
                    `background.gap_metric.write_gap_entry`.

WHY THIS MODULE LIVES IN background/ (NOT company/ or saas/): it is HARNESS
code -- the one place permitted to hold the hidden SIM truth (`PaymentEvent` /
`PeriodRecord`) and the company's observable-only belief (the consumer) side by
side to compute the gap (design 1.3). background/ is exempt from the epistemic
verifier's company/saas import scan for exactly this reason, identical to
`tools/couple_w2_11_d5.py`. The company-side consumer it drives still sees ONLY
`WallResponse`s -- the wall is intact.

DETERMINISM (C-S2): `period_index` is derived deterministically from the
billing month (`year*12 + (month-1)`), never from iteration order, so the
per-customer/per-period substream draw in `generate_payment_event` is
reproducible run-to-run. This module makes no clock/random draw of its own;
`measured_at`/`run_git_commit` are gathered by the caller-facing helper only at
write time and passed straight through to `write_gap_entry` (which never calls a
clock).

THE AMBIGUOUS-REMITTANCE COUNTERFACTUAL (atom D8, 2026-08-09). This module
carries a SECOND, shadow company -- an identical `LedgerBook` +
`PaymentObservationConsumer` fed the identical wall responses with ONE field
changed: every credit carries its invoice remittance reference. The WORLD is
held literally fixed (same events, same failures, same clearing dates, same
ARUDD lag draws -- the adapter's substream is keyed on `(customer_id,
period_index)` alone, so re-emitting the same event cannot move a date); the
only difference is whether the cash is ATTRIBUTABLE when it lands. The
DIFFERENCE between the two companies' measures is therefore what the
ambiguous-remittance channel costs, measured rather than argued. See
`attribute_to_ambiguous_remittance` for the guards that keep it a
counterfactual rather than a second world, and `_attribution_discrimination`
(atom D17) for why the fact that it explains 100% of every measure is a
statement about the OBSERVATION CHANNEL and not a pass mark for the
subtraction -- the thing that actually tests the subtraction is an injected
belief error no invoice reference can cure.

RECENCY-WINDOW NOTE: the consumer is constructed with a run-spanning
`dd_failure_window_days` (`_RUN_SPANNING_WINDOW_DAYS`). The DETECTION headline
(the ledger entry) reads `snapshot().recent_dd_failures`, which is NOT
window-limited, so the headline is window-independent regardless. The window
only affects `arrears_risk_belief`, which feeds the companion BELIEF gap; over a
multi-year live run it must span the whole run so the belief-severity count is
on the SAME all-time basis as the truth-severity count -- otherwise the two
would diverge on a recency artefact rather than on the channel blind spot this
triad is built to measure (the offline scorer's own 400-day window covers its
whole 3-period scenario for the identical reason).
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional

from simulation.payment_behaviour_source import (
    DIRECT_DEBIT,
    generate_payment_event,
    generate_payment_method,
)
from simulation.payment_seam_adapter import SeamAdapterInput, emit_wall_responses

from company.billing.account_ledger import (
    LedgerBook,
    LedgerEvent,
    LedgerEventType,
)
from company.billing.payment_observation_consumer import (
    DEFAULT_RECONCILIATION_GRACE_DAYS,
    PaymentObservationConsumer,
)

from background.gap_metric import (
    GapResult,
    format_ageing_summary,
    format_belief_summary,
    format_detection_summary as _format_detection_summary,
    write_gap_entry,
)
from tools.couple_w2_11_d5 import (
    AS_OF_BUFFER_DAYS,
    PAYMENT_TERMS_DAYS,
    PeriodRecord,
    TWIN_ATOM_ID,
    WORLD_ATOM_ID,
    detection_cell_measurements,
    format_detection_latency_summary,
    score_triad,
)

# Run-spanning belief window (see module docstring RECENCY-WINDOW NOTE). A live
# run covers ~2016-2025 (~3650 days); a comfortable ceiling keeps the belief
# severity count on the same all-time basis as the truth count.
_RUN_SPANNING_WINDOW_DAYS = 6000

# ---------------------------------------------------------------------------
# CAVEATS TRAVEL WITH THE ENTRY THAT IS WRITTEN, NOT WITH THE DIMENSION THEY
# WERE ATTACHED TO (2026-08-18, WORKER_FINDING_THE_SCORED_COMPANY_CLAUSE_IS_
# BLIND_TO_THE_COMPANY_IT_NAMES, leg 2)
#
# `score_triad` attaches `belief_resolution_caveat` and
# `scenario_constant_census_caveat` to the BELIEF dimension's `components`,
# under a comment stating the D22 rationale out loud: the ledger writer, the
# live wiring and the dashboard read `components` and never read `note`, so a
# limit only the prose carries is one the machine strips off.
#
# They were attached to an object this file never writes. `measure_and_write`
# writes the DETECTION dimension alone and splices the belief NUMBER in as a
# formatted string, so on the live path -- the only path with a public reader --
# the belief figure reached `coupled_gap_ledger.json` with none of the
# resolution apparatus two atoms were built to attach to it. Measured on the
# published artefact at 0a3113dfe: 19 component keys, neither caveat among
# them, while the detection-side caveats (`recon_saturation_caveat`,
# `drift_resolution_caveat`) were all present. The ledger was not dropping
# caveats; it was publishing the ones fastened to the written object.
#
# The lift below is deliberately GENERIC rather than a two-key copy: the defect
# class is "a caveat attached to a dimension nobody writes", and naming the two
# known instances would leave the next one to be found by an Expert Hour
# reading the JSON. `check_every_caveat_is_published` is the control, and it
# fails on exactly that.
CAVEAT_COMPONENT_SUFFIX = "_caveat"
_PUBLISHED_CAVEAT_KEY = "dimension_caveats"

# WHICH DIMENSIONS' CAVEATS ARE LIFTED, AND WHY THIS IS NOT "ALL OF THEM"
# (2026-08-18, measured, not preferred).
#
# The first build of this lift was generic over EVERY dimension, on the good
# argument that a hand-typed list cannot see tomorrow's caveat. The gate caught
# what that costs, and it is exactly the defect atom D36 exists to have fixed:
# `ageing.ordinal_direction_caveat` renders the ageing figure at SIX decimals.
# While nobody published it, D36's ruling was that a 6dp site nobody is handed
# does not set that figure's reading precision, so the register declares 3dp
# and every resolution floor derived from it is a 3dp floor. Publishing that
# caveat HANDS the reader the 6dp render, which would move `ageing`'s declared
# precision and cascade into floors this finding never measured -- a published
# resolution claim changed as a side effect of a caveat repair.
#
# So the set is DECLARED, in one place, with that reason beside it. Inside a
# declared dimension the lift stays generic by suffix, which is the half of the
# genericity the finding's class actually needs (both instances were belief
# caveats, and the next belief caveat is caught without anyone naming it).
# Adding a dimension here is a conscious act that must also re-measure
# `PUBLISHED_GAP_CONSUMERS` -- which is the point, not an oversight.
CAVEAT_LIFT_DIMENSIONS = ("belief", "belief_population_mix")


def caveats_by_dimension(result: dict) -> dict:
    """Every `*_caveat` component carried by each dimension in
    `CAVEAT_LIFT_DIMENSIONS`, keyed by dimension name.

    Derived by SUFFIX within each declared dimension, never from a list of the
    caveats this file happens to know about -- a hand-typed caveat list is the
    thing that cannot see the caveat added tomorrow."""
    out: dict = {}
    for name, dim in sorted(result.items()):
        if name not in CAVEAT_LIFT_DIMENSIONS:
            continue
        components = getattr(dim, "components", None)
        if not isinstance(components, dict):
            continue
        found = {k: v for k, v in sorted(components.items())
                 if k.endswith(CAVEAT_COMPONENT_SUFFIX)}
        if found:
            out[name] = found
    return out


def check_every_caveat_is_published(result: dict,
                                    published: "GapResult") -> List[str]:
    """R15: violations, empty means every caveat a lifted dimension carries
    reaches the object that is actually written.

    NOT a tautology -- the expectation is read off the SCORED dimensions and
    the subject is the WRITTEN one, which are two different objects; deleting
    the lift in `measure_and_write`, or lifting only the caveats someone
    remembered, makes this fire. FAIL-CLOSED on a missing map: an absent
    `dimension_caveats` is every caveat unpublished, not a clean pass.

    THE EXPECTATION IS DERIVED HERE, NOT BY CALLING `caveats_by_dimension`.
    Written the obvious way -- checker and publisher sharing the one helper --
    this control passed a mutation that neutered the publisher, because the
    mutation moved the expectation too. That is R15's TAUTOLOGY pattern exactly,
    caught by its own mutation test on 2026-08-18; the duplicated lines below
    are the independence, and are the point. The DIMENSION set is shared
    deliberately: it is a declared scope with a measured reason (see
    `CAVEAT_LIFT_DIMENSIONS`), not something a publisher may quietly narrow."""
    expected: dict = {}
    for name, dim in sorted(result.items()):
        if name not in CAVEAT_LIFT_DIMENSIONS:
            continue
        components = getattr(dim, "components", None)
        if not isinstance(components, dict):
            continue
        found = {k: v for k, v in sorted(components.items())
                 if k.endswith(CAVEAT_COMPONENT_SUFFIX)}
        if found:
            expected[name] = found
    got = (published.components or {}).get(_PUBLISHED_CAVEAT_KEY) or {}
    out: List[str] = []
    for dim, caveats in expected.items():
        for key, value in caveats.items():
            if got.get(dim, {}).get(key) != value:
                out.append(
                    f"{dim}.components[{key!r}] is attached to a dimension "
                    f"this writer does not publish and does not reach the "
                    f"written entry ({published.metric!r}) -- a limit only the "
                    "scorer's result dict carries is one no reader of the "
                    "ledger ever sees")
    return out


def _period_index_for(due_date: date) -> int:
    """Deterministic, iteration-order-independent period index for a billing
    month (C-S2). Unique per calendar month, stable run-to-run -- the only
    property `generate_payment_event`'s per-period substream needs."""
    return due_date.year * 12 + (due_date.month - 1)


def _counterfactual_correlation_id(invoice_ref: str, actual_correlation_id: str) -> str:
    """The reference the shadow company's credit carries (D8): the INVOICE ref,
    always -- a world in which every remittance advice says which invoice it
    pays. A single named seam for the counterfactual so an R15 mutation can
    replace it with the ambiguous reference and prove the attribution collapses
    to zero (a counterfactual identical to the actual measures nothing)."""
    return invoice_ref


# The measures the D8 finding is ABOUT, each already published on its own
# denominator by D7 (ageing) and D11 (detection). Attribution is a plain
# subtraction on each -- no normaliser, no share-of-total ratio: a denominator
# counting the truth's class balance is the exact trap D7's own mutation caught,
# and a ratio here would re-import it through the back door.
_ATTRIBUTED_MEASURES = (
    ("ageing", "mean_bucket_displacement",
     "buckets of debt-DATE displacement over the truly-overdue invoices"),
    ("ageing", "overstated_arrears_rate",
     # NOT "the wrongful-dunning exposure" (atom D16, 2026-08-09). That name
     # belongs to `detection.false_flag_rate` and to nothing else: this rate is
     # the company's ageing REPORT overstated at `as_of`, over a belief
     # population that drops a case once the report stops showing it, while
     # wrongful dunning is an EVENT that either happened to a customer or did
     # not. Both were published under one name from one output block, 3.5x
     # apart. This is the sibling half of that fix -- the same phrase, one file
     # over from where it was corrected.
     "truly-current invoices believed in arrears at as_of -- the AGEING-REPORT "
     "OVERSTATEMENT (NOT the wrongful-dunning exposure: atom D16)"),
    ("ageing", "understated_arrears_rate",
     "truly-overdue invoices believed settled -- debt never chased, under-provisioned"),
    ("detection", "missed_failure_rate",
     "truly-failed invoices the company does not hold flagged -- the WRONGFUL "
     "NON-PURSUIT twin: a real arrears case that disappears from the arrears view"),
    ("detection", "false_flag_rate",
     "never-flaggable invoices wrongly flagged"),
)

def unpursued_arrears(
    records: List[PeriodRecord],
    consumer: PaymentObservationConsumer,
    ever_flagged: set,
    as_of: date,
    *,
    payment_terms_days: int = PAYMENT_TERMS_DAYS,
    reconciliation_grace_days: int = DEFAULT_RECONCILIATION_GRACE_DAYS,
) -> dict:
    """WRONGFUL NON-PURSUIT: truly-failed invoices the company DID detect and
    then STOPPED holding in its arrears view (atom D8, the half D10 widened this
    atom to).

    WHY THIS MEASURE HAS TO EXIST SEPARATELY, and it is not a duplicate of the
    detection headline. D11 made that headline's population EVER-FLAGGED, and
    rightly: a detection is a fact about the day it happened. But the exact
    consequence THIS atom reports is the company later UN-knowing it -- a failed
    invoice going quiet when a later ambiguous credit lands on it oldest-first --
    and an ever-flagged population is, by construction, blind to that. Measured:
    after D11 the detection dimension's `missed_failure_rate` is 0.0000 both with
    and without the ambiguous channel, so the finding is invisible on every
    published surface unless something asks the question directly. This asks it.

    The denominator is the population the question is ABOUT (D7's rule): the
    truly-failed cases the company ACTUALLY DETECTED, since a case never detected
    cannot be un-detected. It does not count the truth's class balance.

    The company's arrears view is read from its OWN organ
    (`expected_collection_misses` at `as_of`), never re-derived here -- a harness
    copy of the rule could not fail if the organ's rule changed (R15
    independence)."""
    by_account: dict = {}
    for r in records:
        by_account.setdefault(r.account_id, {})[r.invoice_ref] = (r.customer_id, r.period_index)

    still_flagged: set = set()
    for account_id, ref_to_case in by_account.items():
        for m in consumer.expected_collection_misses(
            account_id, as_of=as_of, grace_days=reconciliation_grace_days,
            payment_terms_days=payment_terms_days,
        ):
            case = ref_to_case.get(m.invoice_ref)
            if case is not None:
                still_flagged.add(case)

    truth = {(r.customer_id, r.period_index) for r in records if r.result == "failed"}
    detected = truth & ever_flagged
    unpursued = detected - still_flagged
    return {
        "n_true_failures": len(truth),
        "n_ever_detected": len(detected),
        "n_unpursued": len(unpursued),
        # Vacuity is explicit: with nothing detected there is nothing that could
        # have been un-detected, and 0.0 would read as "the company never loses
        # an arrears case" (the D7 rule).
        "unpursued_arrears_rate": (
            round(len(unpursued) / len(detected), 6) if detected else None),
    }


_SAME_WORLD_KEYS = (
    "n_cases", "n_customers", "n_true_failures",
    "n_true_dd_failures", "n_true_non_dd_failures",
)


# The guard that carries the discrimination claim `_attribution_discrimination`
# below points at. Named as a constant, and asserted to RESOLVE to a real test
# by `test_d17_the_published_discrimination_pointer_resolves_to_a_live_guard` --
# a published sentence naming a mechanism that no longer exists is a measured
# failure class in this repo, not a hypothetical one.
DISCRIMINATION_GUARD = (
    "tests/background/test_live_payment_triad.py::"
    "test_R15_the_counterfactual_does_not_attribute_an_injected_non_allocation_error"
)


def _attribution_discrimination(measures: dict) -> dict:
    """WHAT 100% ATTRIBUTION DOES AND DOES NOT PROVE (atom D17).

    Until 2026-08-09 the anti-rubber-stamp guard on this counterfactual was a
    RESIDUAL: the ageing overstatement it could not explain (0.2188 of 0.2803 on
    the offline fixture) was taken as proof that the subtraction discriminated.
    D16 dissolved that residual -- it was composed entirely of invoices settled
    PAST the reconciliation grace, i.e. debt the company was RIGHT to carry, now
    excluded from both dimensions -- so every published measure reads
    `attributed == actual` and the guard had nothing left to check. This says so
    at source rather than letting the reader infer discrimination from a number
    that can no longer show its absence.

    The counts are DERIVED from the measures, never asserted, so the sentence
    cannot outlive the figures (the rule `format_remittance_attribution_summary`
    already follows). A measure whose `actual` error is zero is not counted
    either way: nothing was explained, so nothing was left unexplained."""
    with_error = {
        name: m for name, m in measures.items()
        if m["attributed"] is not None and m["actual"] not in (None, 0, 0.0)
    }
    fully = sorted(n for n, m in with_error.items() if m["remittance_complete"] == 0)
    partial = sorted(set(with_error) - set(fully))
    return {
        "n_measures_with_a_nonzero_error": len(with_error),
        "n_fully_attributed": len(fully),
        "fully_attributed_measures": fully,
        "partially_attributed_measures": partial,
        "guard": DISCRIMINATION_GUARD,
        "reading": (
            f"{len(fully)} of {len(with_error)} measure(s) carrying a non-zero "
            "error read attributed == actual. THAT IS A PROPERTY OF THE "
            "OBSERVATION CHANNEL, NOT EVIDENCE THAT THIS SUBTRACTION "
            "DISCRIMINATES (atom D17). Every successful payment in this world "
            "delivers its credit to BOTH books, and the never-flaggable band "
            "(D16) has already removed every invoice the company was right to "
            "carry as owed -- so the only mechanism left that can make the "
            "company believe a within-grace-settled invoice overdue is the "
            "oldest-first misallocation the counterfactual removes. Read it as "
            "'the channel is complete on this population', never as 'the "
            "counterfactual was tested and passed'. What DOES test it is an "
            "injected belief error no invoice reference can cure -- suppress "
            "the DELIVERY of a credit and the shadow company overstates arrears "
            f"too, so the attributed share falls below 1.0: {DISCRIMINATION_GUARD}."
        ),
    }


def attribute_to_ambiguous_remittance(
    actual: dict,
    counterfactual: dict,
    *,
    n_ambiguous_records: int,
    n_ambiguous_credits: int,
    actual_balance_gbp: float,
    counterfactual_balance_gbp: float,
    extra_measures: Optional[dict] = None,
) -> dict:
    """ATTRIBUTE the company's debt-dating and arrears-detection error to the
    ambiguous-remittance channel, by subtracting a remittance-complete shadow
    company from the real one (atom `D8_ambiguous_remittance_misdating`).

    THE FINDING THIS EXISTS TO REPORT. Unreferenced non-DD credits cross the
    W4_4 seam with no invoice reference, so `AccountLedger.allocate` falls back
    to oldest-first -- Clayton's Case, the English default rule a real supplier's
    cash-allocation actually follows. The consequence is NOT a wrong balance: the
    company's money is exactly right to the penny. It is that the money is
    attached to the WRONG INVOICES, which is what a real supplier is fined and
    sued over -- wrongful dunning of a customer who paid, statutory interest
    accrued from the wrong date, bad-debt provisioning off a fictional ageing
    profile, and (D10's widening of this atom) a genuinely failed invoice going
    QUIET when a later ambiguous payment lands on it, so the arrears case
    disappears from the view that would have pursued it.

    WHY A COUNTERFACTUAL AND NOT A CORRELATION. "Non-DD accounts age worse" is
    not attribution: non-DD customers also fail more often, so the channels are
    confounded in the raw numbers. Holding the WORLD literally fixed and moving
    only whether the credit is attributable removes the confound by construction.

    THREE GUARDS, because a counterfactual is the easiest control in this repo to
    make un-failable (R15):

    * SAME WORLD -- if the shadow population differs from the real one in case
      count, customer count or any truth count, the "counterfactual" changed the
      world and the subtraction is meaningless. RAISES; there is no honest
      degraded answer.
    * THE MONEY IS UNCHANGED -- the premise of the whole finding is that the
      balance is right while the dates are wrong. If the two portfolios' balances
      differ, that premise is FALSE on this population and every attributed
      figure is blanked with `premise_violated` set, rather than published. This
      is fail-CLOSED, not fail-loud, deliberately: it runs inside a live
      run_phase2b, and a diagnostic must not be able to kill the run it measures.
    * VACUITY -- with no ambiguous credit in the population the two companies are
      the same company, so every delta is trivially 0.0. Zero would then read as
      "measured, and the channel costs nothing", which is a lie about a
      measurement that never happened. Reported as `None` with a `vacuity`
      string (the D7 rule).

    A FOURTH GUARD LIVES OUTSIDE THIS FUNCTION, and it has to (atom D17). The
    three above catch a counterfactual that changed the world, moved the money,
    or measured nothing. None of them catches the opposite failure -- a shadow
    company that is clean BY CONSTRUCTION rather than by remittance, which would
    charge the remittance channel for every belief error the company could ever
    make. On this population every measure reads `attributed == actual`, which
    is exactly what that rubber stamp looks like from outside, so it cannot be
    distinguished from the honest answer by looking at these numbers at all --
    see `discrimination` in the returned dict for what it IS distinguished by.

    R12: this is a DIAGNOSTIC. Nothing here may be tuned, and the honest answer
    includes a delta of zero on a live channel -- which would itself be the
    finding refuted, not a failure.
    """
    a_stats, c_stats = actual["stats"], counterfactual["stats"]
    divergent = {
        k: (a_stats.get(k), c_stats.get(k))
        for k in _SAME_WORLD_KEYS if a_stats.get(k) != c_stats.get(k)
    }
    if divergent:
        raise ValueError(
            "D8 attribution: the remittance counterfactual is not the SAME "
            f"WORLD as the actual -- {divergent} (actual, counterfactual). Only "
            "the invoice reference on a credit may differ; a differing truth "
            "count means the shadow company was fed a different population, and "
            "subtracting one from the other would attribute the difference "
            "between two worlds to the remittance channel."
        )

    balance_delta = round(counterfactual_balance_gbp - actual_balance_gbp, 2)
    premise_violated = None
    if balance_delta != 0.0:
        premise_violated = (
            "THE MONEY MOVED. This finding's premise is that the balance is "
            f"exactly right while the dates are wrong, but the shadow portfolio "
            f"balance differs by GBP {balance_delta:+.2f}. Restoring a remittance "
            "reference re-ALLOCATES cash, it can never create or destroy any, so "
            "a non-zero delta means the counterfactual changed something other "
            "than attributability. No attributed figure is published from a "
            "population whose premise is false."
        )

    vacuity = None
    if n_ambiguous_credits == 0:
        vacuity = (
            "NO ambiguous credit landed in this population, so the shadow "
            "company IS the company: every delta below is trivially zero and "
            "measures NOTHING. Reported as undefined (None), never 0.0 -- a "
            "channel that was not exercised is not a channel that costs nothing."
        )

    pairs = [
        (f"{dimension}.{key}",
         actual[dimension].components.get(key),
         counterfactual[dimension].components.get(key),
         meaning)
        for dimension, key, meaning in _ATTRIBUTED_MEASURES
    ]
    for name, pair in (extra_measures or {}).items():
        pairs.append((name, pair["actual"], pair["remittance_complete"], pair["meaning"]))

    measures: dict = {}
    for name, a_val, c_val, meaning in pairs:
        if vacuity or premise_violated or a_val is None or c_val is None:
            attributed = None
        else:
            attributed = round(float(a_val) - float(c_val), 6)
        measures[name] = {
            "actual": a_val,
            "remittance_complete": c_val,
            "attributed": attributed,
            "meaning": meaning,
        }

    return {
        "counterfactual": (
            "the SAME world -- same payment outcomes, same clearing dates, same "
            "bills -- observed by a company whose every credit carries its "
            "invoice remittance reference, so `AccountLedger.allocate` never "
            "falls back to oldest-first. `attributed` = actual minus that."
        ),
        "discrimination": _attribution_discrimination(measures),
        "n_ambiguous_records": n_ambiguous_records,
        "n_ambiguous_credits": n_ambiguous_credits,
        "balance_gbp_actual": round(actual_balance_gbp, 2),
        "balance_gbp_remittance_complete": round(counterfactual_balance_gbp, 2),
        "balance_gbp_delta": balance_delta,
        "measures": measures,
        "vacuity": vacuity,
        "premise_violated": premise_violated,
        "normalisation": (
            "NONE. Each figure is a difference in the measure's own units on the "
            "measure's own denominator (D7's rule). There is deliberately no "
            "'share of the total error' ratio: its denominator would count the "
            "truth's class balance, which is the defect D7 exists to remove."
        ),
    }


def format_remittance_attribution_summary(attribution: dict) -> str:
    """Render the D8 attribution for a log line / published ledger note.

    Same anti-decay mechanism as `format_ageing_summary` /
    `format_detection_summary`: the numbers are INTERPOLATED from the
    measurement, so a sentence cannot outlive the figure it describes, and the
    undefined cases say so in words instead of printing a confident 0.0000."""
    if attribution.get("premise_violated"):
        return "ambiguous-remittance attribution NOT PUBLISHED -- " + attribution["premise_violated"]
    if attribution.get("vacuity"):
        return "ambiguous-remittance attribution UNDEFINED -- " + attribution["vacuity"]

    def _fmt(key: str, unit: str) -> str:
        m = attribution["measures"][key]
        att = m["attributed"]
        if att is None:
            return f"{key} undefined (no such population)"
        return (
            f"{key} {m['actual']} vs {m['remittance_complete']} "
            f"remittance-complete -> {att:+.4f} {unit} attributable"
        )

    return (
        "AMBIGUOUS-REMITTANCE ATTRIBUTION (D8, counterfactual): "
        f"{attribution['n_ambiguous_credits']} credit(s) landed with no invoice "
        f"reference out of {attribution['n_ambiguous_records']} unreferenced "
        "record(s); the company's MONEY is unaffected by every penny "
        f"(portfolio balance GBP {attribution['balance_gbp_actual']:.2f} both ways, "
        f"delta {attribution['balance_gbp_delta']:+.2f}) while its DATES are not: "
        + "; ".join((
            _fmt("ageing.mean_bucket_displacement", "buckets"),
            # D16: the ageing dimension does NOT publish the wrongful-dunning
            # rate -- it publishes the ageing report's overstatement at `as_of`.
            _fmt("ageing.overstated_arrears_rate", "ageing-overstatement rate"),
            _fmt("ageing.understated_arrears_rate", "debt-believed-settled rate"),
            _fmt("arrears_view.unpursued_arrears_rate", "wrongful-non-pursuit rate"),
        ))
        + ". Read as: what the no-remittance channel COSTS this company, holding "
        "the world literally fixed. R12: a diagnostic, never a target. "
        + _format_discrimination(attribution["discrimination"])
    )


def _format_discrimination(discrimination: dict) -> str:
    """One clause carrying the D17 caveat into the published ledger note.

    Short deliberately -- the note this joins is already long -- but it must
    carry the COUNTS, so a reader who sees every figure fully attributed cannot
    take that as the counterfactual having been tested.

    The measures are NAMED, not just counted: this clause covers every measure
    the attribution publishes, while the sentence it joins renders only the four
    that are not printed with the detection headline -- a bare count would have
    a reader matching '5' against four visible figures."""
    n_full = discrimination["n_fully_attributed"]
    n_err = discrimination["n_measures_with_a_nonzero_error"]
    if n_full < n_err:
        return (
            f"DISCRIMINATION (D17): {n_full} of {n_err} measure(s) with a "
            "non-zero error are fully attributed -- "
            + ", ".join(discrimination["partially_attributed_measures"])
            + " carry a residual this channel cannot explain."
        )
    return (
        f"DISCRIMINATION (D17): ALL {n_err} measure(s) with a non-zero error ("
        + ", ".join(discrimination["fully_attributed_measures"])
        + ") read attributed == actual, which is a property of a COMPLETE "
        "observation channel and NOT evidence that the counterfactual "
        "discriminates -- a rubber stamp looks identical from here. The "
        f"discrimination is proven by injection instead: {discrimination['guard']}."
    )


class LivePaymentTriad:
    """Accumulates the live coupled triad across one run_phase2b invocation.

    Usage (from simulation/run_phase2b.py):
        triad = LivePaymentTriad()
        ...
        analytics_rec = triad.record_period(
            customer_id=cid, due_date=due, amount_gbp=amount,
            income_stress_value=stress_str, segment=cust_segment,
        )
        _payment_analytics.record_payment(cid, analytics_rec)
        ...
        triad.measure_and_write(run_git_commit=head_sha)
    """

    def __init__(self, dd_failure_window_days: int = _RUN_SPANNING_WINDOW_DAYS) -> None:
        self._ledger_book = LedgerBook()
        self._consumer = PaymentObservationConsumer(
            ledger_book=self._ledger_book,
            dd_failure_window_days=dd_failure_window_days,
        )
        # THE D8 SHADOW COMPANY: identical construction, fed the identical
        # observations with the invoice remittance reference restored. Never
        # read by anything company-side -- it exists only so the harness can
        # subtract one company from the other (module docstring).
        self._cf_ledger_book = LedgerBook()
        self._cf_consumer = PaymentObservationConsumer(
            ledger_book=self._cf_ledger_book,
            dd_failure_window_days=dd_failure_window_days,
        )
        self._n_ambiguous_records = 0
        self._n_ambiguous_credits = 0
        self._records: List[PeriodRecord] = []
        # persistent per-customer method archetype cache (drawn once, C-S2)
        self._method_cache: dict = {}

    @property
    def records(self) -> List[PeriodRecord]:
        return self._records

    def detection_cells(self, as_of: date) -> dict:
        """The per-cell DETECTION measurements for the fidelity grid.

        THIS METHOD IS THE DOOR, and it exists because of what it REPLACED
        (KNIFE pass 3 step 33, disposition register §3ab). `run_phase2b` used
        to compute these itself: `detection_cell_measurements(triad.records,
        triad.consumer, as_of)`, importing the scorer from
        `tools.couple_w2_11_d5` and reading a public `consumer` property to get
        its second argument. That property was this class's ONLY route by which
        a caller could obtain a live company object, and `run_phase2b` was its
        only reader in the repo -- so it is gone, and asking for a company
        object here is now a hard `AttributeError` rather than a convention.

        No number moves: the body is the identical call on the identical
        arguments, which is also why the R15 suite does not compare before to
        after (that comparison is R15's TAUTOLOGY pattern -- it would pass
        whatever this returned). What it asserts instead is REACHABILITY: that
        the world can no longer get the consumer, and that the second bridge
        entry is gone from `run_phase2b`."""
        return detection_cell_measurements(self._records, self._consumer, as_of)

    def _method_for(self, customer_id: str) -> str:
        m = self._method_cache.get(customer_id)
        if m is None:
            # Method is a persistent per-customer archetype (W2_11's own model);
            # drawn once with a fixed fuel so a customer never flips method
            # between their gas and electricity months.
            m = generate_payment_method(customer_id, fuel="electricity")
            self._method_cache[customer_id] = m
        return m

    def record_period(
        self,
        *,
        customer_id: str,
        due_date: date,
        amount_gbp: float,
        income_stress_value: Optional[str],
        segment: str = "resi",
    ) -> dict:
        """Generate the ONE canonical W2_11 payment event for this
        (customer, period), cross the seam + feed the company consumer LIVE,
        record the harness-side truth, and RETURN the derived analytics dict for
        the run's existing `PaymentBehaviourAnalytics`.

        Returns the analytics record (ON_TIME/LATE/DD_FAILED) DERIVED from the
        single W2_11 event -- the caller feeds it to `record_payment`. There is
        never a second, independent payment draw."""
        period_index = _period_index_for(due_date)
        method = self._method_for(customer_id)
        account_id = f"ACC-{customer_id}"
        invoice_ref = f"{customer_id}::{period_index}"
        issue_date = due_date - timedelta(days=PAYMENT_TERMS_DAYS)

        stress = income_stress_value if income_stress_value else "low"
        event = generate_payment_event(
            customer_id, period_index, due_date, amount_gbp, stress, method,
            segment=segment,
        )

        # Post the bill into the COMPANY's own belief ledger so unpaid invoices
        # age (the ageing gap) exactly as the offline scenario does. This is the
        # company's isolated ledger, never the run's main treasury ledger.
        bill = LedgerEvent(
            event_id=f"bill:{customer_id}:{period_index}",
            account_id=account_id,
            event_type=LedgerEventType.BILL_DEBIT,
            amount_gbp=amount_gbp,
            valid_time=issue_date,
            transaction_time=datetime.combine(issue_date, time(0, 0)),
            invoice_ref=invoice_ref,
        )
        self._ledger_book.post(bill)
        # The shadow company is billed IDENTICALLY (D8): the counterfactual is
        # about what the company can attribute the CASH to, never about what it
        # invoiced. Posting a different bill set here would make the two books
        # incomparable in exactly the way the attribution guards look for.
        self._cf_ledger_book.post(bill)

        # DD payments carry a period-specific remittance (correlation_id ==
        # invoice_ref -> remittance-directed allocation matches the invoice).
        # Non-DD methods carry a still-unique-per-period but deliberately
        # invoice-AMBIGUOUS correlation_id (no remittance advice on a
        # customer-initiated push payment), forcing the ledger's oldest-first
        # fallback -- identical to the offline scenario's seeding.
        if method == DIRECT_DEBIT:
            correlation_id = invoice_ref
        else:
            correlation_id = f"{customer_id}::p{period_index}::ambiguous"
        seam_input = SeamAdapterInput(account_id=account_id, correlation_id=correlation_id)

        for response in emit_wall_responses(event, seam_input):
            self._consumer.observe(response)

        # ---- D8 counterfactual: the SAME event, remittance-complete --------
        # `correlation_id` is what the adapter puts in `RemittanceAdvice.
        # bank_reference`, and that reference is the ONLY thing standing between
        # `AccountLedger.allocate`'s remittance-directed path and its
        # oldest-first fallback. Re-emitting the identical event with the
        # invoice reference restored therefore isolates exactly one variable.
        # (Determinism: the adapter's lag draw is keyed on (customer_id,
        # period_index) under its own substream, so this second emission returns
        # the same dates -- proven, not assumed, by
        # test_counterfactual_differs_only_in_the_reference.)
        cf_correlation_id = _counterfactual_correlation_id(invoice_ref, correlation_id)
        if correlation_id != invoice_ref:
            self._n_ambiguous_records += 1
            if event.result == "success":
                # A credit that actually LANDED unattributable -- the only kind
                # that can displace an allocation. An ambiguous reference on a
                # payment that never arrived costs nothing, and counting it
                # would inflate the population the finding rests on.
                self._n_ambiguous_credits += 1
        for cf_response in emit_wall_responses(
            event,
            SeamAdapterInput(account_id=account_id, correlation_id=cf_correlation_id),
        ):
            self._cf_consumer.observe(cf_response)

        self._records.append(PeriodRecord(
            customer_id=customer_id, period_index=period_index,
            invoice_ref=invoice_ref, account_id=account_id,
            due_date=due_date, issue_date=issue_date,
            payment_method=method, result=event.result,
            dd_failure_reason=event.dd_failure_reason,
            correlation_id=correlation_id,
            days_late=event.days_late,
        ))

        return _derive_analytics_record(customer_id, due_date, amount_gbp, event)

    def measure(self, as_of: Optional[date] = None) -> Optional[dict]:
        """Score the accumulated triad (detection / belief / ageing). Returns
        the score_triad result dict, or None if the run produced no true payment
        failures at all (nothing for the detection metric to measure -- guarded
        rather than raising, so a defensible empty population never crashes)."""
        if not self._records:
            return None
        if not any(r.result == "failed" for r in self._records):
            return None
        if as_of is None:
            as_of = max(r.due_date for r in self._records) + timedelta(days=AS_OF_BUFFER_DAYS)
        result = score_triad(self._records, self._consumer, as_of)
        result["remittance_attribution"] = self._attribute_remittance(result, as_of)
        return result

    def _attribute_remittance(self, actual: dict, as_of: date) -> dict:
        """Score the SHADOW company through the SAME scorer and subtract (D8).

        The scorer is `score_triad` itself, not a bespoke re-derivation: a second
        implementation of the ageing/detection measures would be asserting a copy
        against a copy, the tautology R15 names first and the one this repo has
        already caught twice inside its own R15 tests. The TRUTH passed to both
        calls is the identical `self._records` -- the world did not change, only
        what the company could attribute the cash to."""
        counterfactual = score_triad(self._records, self._cf_consumer, as_of)
        a_unpursued = unpursued_arrears(
            self._records, self._consumer, actual["sets"]["flagged"], as_of)
        c_unpursued = unpursued_arrears(
            self._records, self._cf_consumer, counterfactual["sets"]["flagged"], as_of)
        attribution = attribute_to_ambiguous_remittance(
            actual, counterfactual,
            n_ambiguous_records=self._n_ambiguous_records,
            n_ambiguous_credits=self._n_ambiguous_credits,
            actual_balance_gbp=self._ledger_book.portfolio_balance_gbp(as_of),
            counterfactual_balance_gbp=self._cf_ledger_book.portfolio_balance_gbp(as_of),
            extra_measures={
                "arrears_view.unpursued_arrears_rate": {
                    "actual": a_unpursued["unpursued_arrears_rate"],
                    "remittance_complete": c_unpursued["unpursued_arrears_rate"],
                    "meaning": (
                        "truly-failed invoices the company DETECTED and then "
                        "stopped holding in its arrears view by as_of -- a real "
                        "arrears case that disappears from the view that would "
                        "have pursued it. The detection headline is EVER-FLAGGED "
                        "(D11) and structurally cannot see this; it is measured "
                        "here or nowhere."
                    ),
                },
            },
        )
        attribution["unpursued_counts"] = {
            "actual": a_unpursued, "remittance_complete": c_unpursued,
        }
        return attribution

    def measure_and_write(
        self,
        run_git_commit: Optional[str] = None,
        as_of: Optional[date] = None,
        ledger_path=None,
    ) -> Optional[dict]:
        """Measure the live gap and write the DETECTION headline into the
        coupled gap ledger (bare `WORLD_ATOM_ID` key -- the Proof door / contract
        reader key; NO ::suffixed keys, which the Proof door counts as unmapped
        extras and would wedge the publish gate). The companion belief/ageing
        gaps ride inline in the note. Returns the full score_triad result (with
        the headline note attached), or None if there was nothing to measure.

        R12: the gap is a DIAGNOSTIC, never a target."""
        result = self.measure(as_of=as_of)
        if result is None:
            return None

        headline: GapResult = result["detection"]
        headline.note = (
            "LIVE per-run coupled-triad gap (W2_11 payment TRUTH -> W4_4 seam -> "
            "D5 consumer belief, measured in-run by run_phase2b). HEADLINE = "
            "DD/non-DD failure DETECTION gap (fraction of true payment failures "
            "the company does not BELIEVE unresolved as at the measurement date "
            "-- NOT, as this note said until 2026-08-09, failures it never "
            "observes: D10 measured every truly-failed case being flagged on "
            "time at due+grace, and the residual is cases the company detected "
            "and then UN-flagged when a later ambiguous non-DD payment was "
            "allocated oldest-first onto the failed invoice, Clayton's Case, "
            "atom D8. The no-remittance blind spot is real but is not what this "
            "number counts). READ THE HEADLINE AS RECONCILIATION-DETERMINED ALONE "
            "(D10): `flagged_set` is a UNION and deleting the DD-observation "
            "channel leaves it bit-identical -- what that channel buys is EARLIER "
            "detection, reported in days beside it. "
            "RESHAPED 2026-08-09 (atom D11) -- THIS HEADLINE IS NOT COMPARABLE "
            "WITH ANY LEDGER ENTRY WRITTEN BEFORE THAT DATE, and the "
            "discontinuity is a fix, not a drift. The H27 Expert Hour measured "
            "two defects in the old figure and both are now closed at the "
            "measure rather than caveated in prose. (1) It was an as_of "
            "ARTEFACT: the truth (`result == 'failed'`) does not move with the "
            "clock but the belief was held AT the measurement date, so holding "
            "company and world fixed and moving only that date walked the figure "
            "~+70% over 60 days. The population is now EVER-FLAGGED -- a "
            "detection is a fact about the day it happened, whatever a later "
            "oldest-first allocation did to the invoice -- and the as_of sweep "
            "is flat. (2) It counted ONE ERROR DIRECTION: a company flagging "
            "EVERY invoice scored a perfect 0.0. The headline is now the "
            "BALANCED error of both directions on their own denominators, so "
            "both degenerate strategies score g0 = 0.5. "
            f"{_format_detection_summary(headline)}. The retired recall-only "
            "figure is NOT restated: it was scored over a different flagged "
            "population, so no arithmetic on these sets reproduces it. "
            "Companion per-dimension gaps: "
            f"{format_belief_summary(result['belief'])} "
            "[RESHAPED 2026-08-10, atom D19, and NOT comparable with the "
            "belief figure any earlier ledger entry carries: that was a "
            "population TV distance, which permuting which account holds which "
            "severity belief left bit-identical (0.0713 -> 0.0713 while "
            "per-case agreement fell 0.9287 -> 0.6432), so the degenerate "
            "'right mix, every individual wrong' scored exactly what the real "
            "company scored. The TV figure is not deleted -- it is published as "
            "belief_population_mix "
            f"{result['belief_population_mix'].gap:.4f}, the question it was "
            "always answering]; "
            f"{format_detection_latency_summary(result['detection_latency'])}; "
            f"{format_ageing_summary(result['ageing'])} "
            "[D7 RESHAPE 2026-08-08: the single prevalence-normalised ageing "
            "scalar that used to sit here (live 1.1538) was refuted in "
            "docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md and is "
            "RETIRED, not re-labelled. The three measures above each carry the "
            "denominator they are about; the displacement carries none at all]; "
            "allocation honestly dropped (metric-shape mismatch). "
            f"{format_remittance_attribution_summary(result['remittance_attribution'])} "
            "R12: diagnostic, not a target."
        )
        # The attribution travels as STRUCTURE too, not only as a sentence:
        # components survive a caller replacing `note` (the D6 lesson -- both
        # live callers do exactly that) and carry through to_ledger_entry ->
        # coupled_gap_ledger.json -> the Proof door.
        headline.components["remittance_attribution"] = result["remittance_attribution"]
        # AND SO DO THE OTHER DIMENSIONS' CAVEATS (2026-08-18). Everything this
        # writer publishes about `belief` -- the number, the mix, the reshape
        # history -- travelled without the two limits `score_triad` built for
        # it, because those were fastened to `result["belief"]` and this entry
        # is `result["detection"]`. Lifted generically and CHECKED, so the next
        # caveat attached to an unwritten dimension fails here at the seam.
        headline.components[_PUBLISHED_CAVEAT_KEY] = caveats_by_dimension(result)
        unpublished = check_every_caveat_is_published(result, headline)
        if unpublished:
            raise RuntimeError(
                "live payment triad: refusing to publish a gap entry that "
                "drops a caveat the scorer attached -- "
                + "; ".join(unpublished))
        measured_at = datetime.now(timezone.utc).isoformat()
        write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, headline,
            measured_at=measured_at, run_git_commit=run_git_commit,
            ledger_path=ledger_path,
        )
        return result


def _derive_analytics_record(
    customer_id: str, due_date: date, amount_gbp: float, event
) -> dict:
    """DERIVE the run's legacy analytics dict from the ONE canonical W2_11
    `PaymentEvent` -- so `PaymentBehaviourAnalytics` is fed from the single
    payment truth, never a second independent draw. Result mapping:

      * event.result == "failed"  -> "DD_FAILED" (unpaid, no cash)
      * event.result == "dispute" -> "DD_FAILED" (NAMED SIMPLIFICATION: the
        legacy analytics vocabulary has only ON_TIME/LATE/DD_FAILED; an I&C/SME
        BACS dispute -- a contested, unresolved collection -- is closest to
        DD_FAILED. Disputes arise only on the bacs/chaps path, i.e. I&C/SME
        segments; the legacy path never produced them for resi.)
      * event.result == "success", days_late>0 -> "LATE"
      * event.result == "success", days_late==0 -> "ON_TIME"

    `days_late` is now carried through (the legacy `generate_payment_record`
    omitted it, so `avg_days_late` was always 0.0); it is a genuine fidelity
    gain, unused by the on_time_rate/dd_fail_rate scoring that drives the churn
    signal."""
    if event.result in ("failed", "dispute"):
        return {
            "customer_id": customer_id,
            "due_date": due_date,
            "result": "DD_FAILED",
            "payment_date": None,
            "amount_gbp": amount_gbp,
            "amount_paid": 0.0,
            "days_late": 0,
        }
    # success
    if event.days_late > 0:
        payment_date = (
            date.fromisoformat(event.payment_date)
            if event.payment_date else due_date + timedelta(days=event.days_late)
        )
        return {
            "customer_id": customer_id,
            "due_date": due_date,
            "result": "LATE",
            "payment_date": payment_date,
            "amount_gbp": amount_gbp,
            "amount_paid": amount_gbp,
            "days_late": event.days_late,
        }
    return {
        "customer_id": customer_id,
        "due_date": due_date,
        "result": "ON_TIME",
        "payment_date": due_date,
        "amount_gbp": amount_gbp,
        "amount_paid": amount_gbp,
        "days_late": 0,
    }
