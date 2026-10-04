"""Wires simulation/bacs_rails.py's timing physics into the live DD flow --
M2's next build step (director in-console approval, 2026-07-11): "wire rails
timing into the live DD flow."

Real finding before building (R4 diagnosis discipline): grepped the whole
codebase for company/billing/direct_debit.py's DirectDebitBook/
record_attempt/DDPaymentAttempt and found ZERO callers anywhere -- that
class was entirely unwired, the exact "paper compliance" class the M2
payments-maturity audit already named for 18 other billing/collections
modules. The genuinely LIVE DD-relevant flow is
simulation/arrears_engine.py::payment_outcome(), called from
compute_emergent_bad_debt()/compute_debt_recovery() -- but those functions
compute REAL ground-truth bad-debt/recovery figures that flow into every
downstream financial number (net_margin_gbp, treasury_cash_balance_gbp),
exactly the class of code M1's own precedent (docs/design/
M1_EVENT_DRAIN_MATERIALITY_FRAME.md) already established extreme caution
around -- a same-day change to arrears TIMING there would shift which
calendar year a write-off lands in, silently changing historical financial
figures. Deliberately NOT touched.

This module instead does the SAFE, additive thing: populates the
previously-unwired DirectDebitBook with REAL Bacs-timed collection records,
using the SAME unchanged payment_outcome() decision (identical RNG seed and
call sequence as compute_emergent_bad_debt(), so this book's success/failure
pattern matches what's already baked into the real ground truth -- never
contradicts it) layered with bacs_rails.py's realistic submission/collection/
notification timing and ARUDD reason codes. No existing number changes;
this is a new, real, company-observable artefact where none existed before.

Scope: only bills paid by `method == "direct_debit"` (the genuine consumer
DD case) -- payment_method()'s "bacs"/"chaps" branch is B2B/corporate
direct-transfer, a different real-world rails entirely, out of scope here.

2026-07-12, L2->L3 attempt (W5_1_banking_payment_rails): mandate SETUP and
AMENDMENT wired through the same submit-then-resolve rails pattern as
collections. A fresh-context Expert Hour review (phase-close-evaluator,
2026-07-12) found this attempt does not yet earn L3 and named concrete,
fixed-this-pass bugs plus one still-open gap -- documented honestly here
rather than re-asserting the original (partly wrong) reasoning:

- FIXED: the amendment trigger originally compared a single bill's raw
  `total_amount_gbp` against the mandate's stored monthly amount -- for a
  seasonal resi customer this fired an ADDACS amendment almost every month,
  modelling on-demand billing, not smoothed Variable DD (real Variable DD
  holds a periodic re-estimate fixed against normal seasonal swings). Now
  compares the mandate's stored amount against a ROLLING MEDIAN (not mean --
  a mean is dragged by a single outlier, a median correctly ignores one
  anomalous bill while still moving once a majority of a trailing window
  reflects a genuine sustained change) of that customer's own bill amounts
  seen so far in this book -- an amendment only fires when the established
  level has genuinely drifted, not on every bill's noise, and the mandate is
  amended TO the median, never to the single triggering bill's amount.
- FIXED: the mandate-setup "no calibrated rejection rate exists" claim was
  wrong -- this lane's OWN charter (docs/design/charters/
  W5_banking_payment_rails.md) cites GoCardless's public mandate-lifecycle
  data (~95% confirmed by day 5, i.e. a real ~5% non-confirmation rate is
  citable). Outcome remains deterministic "success" in this pass -- not
  because no rate exists, but because modelling a REJECTED mandate would
  need a fallback-payment-method/retry mechanism that doesn't exist anywhere
  in this codebase yet; that is the honest limiting factor, registered as
  forward scope, not glossed over.
- FIXED (2026-07-12, third pass, closing the last named L3 blocker): mandate
  setup used to be submitted and resolved in the same step as the collection
  it precedes, rather than genuinely GATING the collection on AUDDIS
  confirmation first. Re-examined the earlier "risks changing ground-truth
  arrears/bad-debt outcomes" reasoning that had left this open twice before
  -- it conflated two independent things. payment_outcome()'s success/fail
  decision (compute_emergent_bad_debt()'s own ground truth) is drawn from
  the bill's own `bill_substream(seed, cid, period_end, commodity)` BEFORE
  any date logic runs and takes no date as an input
  at all -- gating a collection's own due_date can never change which bills
  succeed or fail. And this module's own dates feed nothing but a business-
  surface rendering (extract_dd_rails()) -- never the ledger/cash-timing
  pipeline that computes any actually-published financial figure. Once that
  was verified precisely (not just re-asserted), the fix was safe: a brand
  new mandate's first collection due_date is now `max(bill's own due_date,
  mandate's own AUDDIS confirmation date)` -- genuinely gated, matching what
  a real Bacs integration would require. Verified against the real full
  pipeline run (not just unit tests) with this change in place.
- FIXED (2026-07-12, second pass): "this module has ZERO callers from any
  real run pipeline" -- wired into simulation/run_phase4c_on_phase2b.py's
  main() (serialised via _serialize_dd_collection_book()), threaded through
  saas/reporting/annual_report.py::extract_report_data() into
  docs/reports/run_output_latest.json, exposed via
  tools/generate_dashboard_data.py::extract_dd_rails(), and rendered on the
  Supplier tab (site/supplier/index.html::ddRailsHtml()) with one real named
  customer's mandate + actual collection history. Verified against a real
  full run (not a fixture): 9 mandates, 751 collection attempts, 28 real
  ARUDD failures across 1588 bills.
- FIXED (2026-07-12, second Expert Hour review, phase-close-evaluator): a
  real product-mechanic incoherence in the rendered surface itself (caught
  by phase-close rule 0c, reading one instance as a human) -- the mandate's
  own smoothed/re-estimated `monthly_amount_gbp` (a Fixed-DD-shaped figure)
  sat directly above a collection table where every attempt's amount was the
  raw, varying bill total, with no code path connecting the two. This
  modelled no real UK DD product: a genuine smoothed Fixed DD collects the
  fixed amount and tracks seasonal variation as a running balance; a genuine
  Variable DD collects the real bill each cycle and has no fixed,
  re-estimated mandate figure gating anything. This module has always
  collected the real bill amount (`submit_collection(..., amount, ...)`
  below uses the bill's own `total_amount_gbp`, never `mandate.
  monthly_amount_gbp`) -- i.e. it always WAS Variable DD -- but the surface
  and this docstring never said so, letting the mandate's estimated
  reference figure read as if it were the actual collection size. Fixed by
  labelling, not re-engineering: `site/supplier/index.html`'s example block
  and portfolio KPI now state explicitly that this is Variable DD, the
  mandate figure is an "estimated reference level" that never sizes or gates
  a collection (only decides when an ADDACS re-estimation notice fires), and
  the KPI is relabelled "Est. Reference Total" rather than the misleading
  "Monthly Collection". No change to which cash amount is actually
  collected -- ground truth stays exactly as compute_emergent_bad_debt()
  computed it.
- The M2 audit's duplicated-register finding (DirectDebitBook vs
  company/billing/dd_mandate_register.py) is NOT fully resolved by this
  module -- see that module's own docstring for the honest, corrected
  statement (an earlier version of this docstring overclaimed "superseded"/
  "resolved"); the underlying reason it mattered (DirectDebitBook lacking a
  point-in-time discipline) is closed, the literal duplication (the file
  still exists, still unused) is not. `tests/company/billing/
  test_dd_mandate_register.py::test_module_stays_caller_free_structural_guard`
  now guards against the hazard the audit actually cared about (two live
  writers into overlapping mandate state) recurring silently.
- REGISTERED SIMPLIFICATION (2026-07-12, final Expert Hour review, not
  itself L3-blocking but named per R10 rather than left implicit): mandate
  setup is modelled as coincident with a customer's FIRST direct_debit bill
  (this function only sees `bills`, not a real contract-signup date), not
  at contract signup as a real supplier's mandate would be. This means
  every brand-new mandate's first collection is pushed exactly
  AUDDIS_CONFIRMATION_DAYS (2) later than its naive due_date, every time --
  a real supplier's DD mandate would usually already be confirmed by the
  time the first bill falls due, so this 2-day push is a modelling
  artefact of not having signup-date input, not a claim about real DD
  timing generally. Business-surface-only and harmless to any financial
  figure (see the gating fix's own safety reasoning above).

The prior reasoning stands unchanged: same unchanged payment_outcome()
decision (identical RNG seed and call sequence as compute_emergent_bad_debt())
for every collection, so this book's success/failure pattern matches what's
already baked into the real ground truth -- never contradicts it -- layered
with bacs_rails.py's realistic submission/collection/notification timing and
ARUDD reason codes. No existing number changes; this is a new, real,
company-observable artefact where none existed before.
"""
from __future__ import annotations

import random
from datetime import date, timedelta

from company.interfaces.dd_collection_instructions import open_collections_desk
from simulation.arrears_engine import (
    PAYMENT_TERMS_DAYS, bill_substream, payment_method, payment_outcome,
    stress_for_year, _fuel_poor_for_bill, _tone_for_bill,
)
from simulation.bacs_rails import (
    ARUDD_REASON_CODES, resolve_submission, submit_amendment,
    submit_collection, submit_mandate_setup,
)
from simulation.dd_payment_day import staggered_payment_day

# The amendment materiality floor and the trailing re-estimation window MOVED to
# `company/billing/dd_collections_desk.py` (KNIFE pass 3,
# B4_billing_mechanics_reached_directly, 2026-08-10). How far a standing amount must
# drift before the supplier writes to the customer's bank, and how much history the
# estimate looks back over, are the supplier's re-estimation routine -- a routine it
# is free to change without telling anyone, which is the one property this world had
# no business holding. They are deliberately NOT re-exported here.


def build_dd_collection_book(
    bills: list[dict], behavioral: dict, monthly_amount_by_customer: dict[str, float] | None = None,
    seed: int = 42,
):
    """The supplier's own collection register after this world's rails ran. See `_run_rails`."""
    return _run_rails(bills, behavioral, monthly_amount_by_customer, seed)[0].collection_register()


def supplier_dd_stops(bills: list[dict], behavioral: dict, seed: int = 42) -> dict[str, str]:
    """PB8 L2: the households the supplier has told their Direct Debit is stopped.

    `{customer_id: period_end}` of the last bill the supplier presented by DD. Every later bill
    is payable on receipt. This is what the household is told, so it is all the world reads.
    Why it stopped, and on what rule, stay behind the desk.
    """
    return {cid: stop[0] for cid, stop in _run_rails(bills, behavioral, None, seed)[1].items()}


def supplier_dd_stop_notices(bills: list[dict], behavioral: dict, seed: int = 42) -> dict[str, str]:
    """`{customer_id: notice_date}`: the day the household learnt its DD was stopped.

    That is the day of the return that made the supplier stop it. It is the as-of key for anything
    asked mid-run ("how does this household pay, on this date?"), where `supplier_dd_stops`'s
    period_end is the key for which bills are payable on receipt.
    """
    return {cid: stop[1] for cid, stop in _run_rails(bills, behavioral, None, seed)[1].items()}


class StopNoticeBoard:
    """PB8 L2, the seam half: has the supplier stopped this supply point's DD, as of a date?

    Answered mid-run, from the run's own settled records so far, by the money side's own route:
    the supplier's monthly bills over those records, through `issued_bills`, through the rails.
    Only records from calendar months that ended before `as_of` are billed. A stop's notice comes
    after its bill's due date, so the month containing `as_of` cannot carry a notice on or before
    it, and a partial month must not stand in for the full month's bill the money side sees.

    The rails resolve each customer on its own lag stream (`_run_rails`), so a customer's notices
    are a function of its own bills only. That is what makes this per-customer, as-of answer equal
    the money side's register cut at `as_of`.
    """

    def __init__(self, stress_trajectory_of, seed: int = 42) -> None:
        self._stress_trajectory_of = stress_trajectory_of
        self._seed = seed
        self._records: dict[str, list[dict]] = {}
        self._stopped: dict[str, str] = {}
        self._clear_through: dict[str, date] = {}
        self._billed: dict[tuple[str, str], str] = {}

    def observe(self, records: list[dict]) -> None:
        """Take a term's settled records as the run settles them."""
        from simulation.household import household_of
        for r in records:
            self._records.setdefault(r["customer_id"], []).append(r)
            self._billed.setdefault((household_of(r["customer_id"]), r.get("commodity")),
                                    r["customer_id"])

    def supply_point_billed(self, household: str, fuel: str) -> str | None:
        """The supply point this run has billed for the household's `fuel`, or None if none yet.

        Asked rather than spelled from the id: a dual-fuel household's gas leg is `C1g`, but a
        gas-only household's one leg carries no suffix (`SYN-2016-021`), and the records -- so the
        stops -- are keyed by the leg the run billed. None means nothing billed, so nothing stopped.
        """
        return self._billed.get((household, fuel))

    def notice_as_of(self, supply_point: str, as_of: str) -> str | None:
        """The notice date of the stop, if the household had been told by `as_of`; else None."""
        notice = self._stopped.get(supply_point)
        if notice is not None:
            return notice if notice <= as_of else None
        cutoff = date.fromisoformat(as_of).replace(day=1)
        if self._clear_through.get(supply_point, date.min) >= cutoff:
            return None
        records = [r for r in self._records.get(supply_point, [])
                   if r.get("settlement_date", "9999") < cutoff.isoformat()]
        if not records:
            return None
        from company.interfaces.bill_assembly import issued_bills
        from simulation.run_phase4c_on_phase2b import build_monthly_bills
        bills = issued_bills(build_monthly_bills(records, set()))
        behavioral = {supply_point: {
            "income_stress_trajectory": self._stress_trajectory_of(supply_point)}}
        notices = supplier_dd_stop_notices(bills, behavioral, self._seed)
        if supply_point in notices:
            self._stopped[supply_point] = notices[supply_point]
            return notices[supply_point] if notices[supply_point] <= as_of else None
        self._clear_through[supply_point] = cutoff
        return None


_ACTIVE_BOARD: StopNoticeBoard | None = None


def install_stop_notice_board(board: StopNoticeBoard | None) -> None:
    """The run hands the seam its board for the run's duration, and None at the end."""
    global _ACTIVE_BOARD
    _ACTIVE_BOARD = board


def active_stop_notice_board() -> StopNoticeBoard | None:
    return _ACTIVE_BOARD


def _run_rails(
    bills: list[dict], behavioral: dict, monthly_amount_by_customer: dict[str, float] | None,
    seed: int,
):
    """Run this world's Bacs rails against the supplier's collection instructions.
    Returns the desk and the stop notices it sent (`supplier_dd_stops`).

    Resolves each bill from the same per-bill substream compute_emergent_bad_debt()
    uses (`arrears_engine.bill_substream`, C-S2) -- the resulting success/failure
    pattern matches the real ground truth exactly; this adds the rails-timing and
    reason-code layer around it.

    DELIBERATELY UNANNOTATED (KNIFE pass 3, B4_billing_mechanics_reached_directly,
    2026-08-10). The return is a `DirectDebitBook`, and this module can no longer
    NAME that type -- which is the cut. Re-exporting the class through
    `company/interfaces/dd_collection_instructions.py` just to satisfy an annotation
    would hand the world back the ability to construct the supplier's register, with
    every static instrument in the tree still green, because an import terminating on
    the seam package is exempt by construction. An honest missing annotation is a
    smaller cost than a laundered dependency, and the seam module records the refusal.
    """
    # Separate, independently-seeded RNG for bacs_rails' own lag-day
    # randomization (resolve_submission()'s `rng` arg) -- deliberately NOT a
    # payment-outcome substream. Keeping the rails draws on their own stream
    # is what stops a rails-timing change from moving a payment outcome; the
    # converse (extra rails draws desyncing outcomes) is now structurally
    # impossible, since each bill's outcome is keyed by its own identity
    # rather than by the state of a stream this loop shares.
    #
    # ONE LAG STREAM PER CUSTOMER (PB8 L2, 2026-10-03). A single stream walked in customer order
    # made one household's notice date depend on every household sorted before it, so a stop could
    # not be asked about mid-run from that household's own bills (`StopNoticeBoard`).
    rails_rngs: dict[str, random.Random] = {}
    desk = open_collections_desk()
    stops: dict[str, tuple[str, str]] = {}
    monthly_amount_by_customer = monthly_amount_by_customer or {}

    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        cid = bill["customer_id"]
        segment = bill.get("segment", "resi")
        amount = bill["total_amount_gbp"]
        period_end = bill["period_end"]
        year = int(period_end[:4])

        method = payment_method(segment, amount, cid, bill.get("commodity", "electricity"))
        # A non-DD bill can now be skipped BEFORE drawing its outcome: the
        # draw is keyed by (cid, period_end), so not making it cannot shift
        # any other bill's result. Under the old shared stream this loop had
        # to draw for every bill purely to stay in lockstep with
        # compute_emergent_bad_debt() -- an obligation each of the four
        # consumers had to hand-maintain, and one of them (the billing ledger)
        # did not.
        if method != "direct_debit":
            continue
        # PB8: the supplier stopped this customer's DD after repeated returns, so the
        # bill is payable on receipt and nothing is put on the rails for it. The world
        # does not re-open a mandate the household never asked for.
        if desk.has_mandate(cid) and not desk.pays_by_direct_debit(cid):
            continue
        stress = stress_for_year(behavioral.get(cid) or {}, year)
        outcome, _days_late = payment_outcome(
            method, stress, bill_substream(seed, cid, period_end, bill.get("commodity", "electricity")),
            segment,
            _fuel_poor_for_bill(method, cid),
            _tone_for_bill(method, cid, period_end), cid,
        )

        issue_date = date.fromisoformat(period_end)
        due_date = issue_date + timedelta(days=PAYMENT_TERMS_DAYS)

        if not desk.has_mandate(cid):
            monthly_amount = monthly_amount_by_customer.get(cid, amount)
            # The SUPPLIER issues the setup instruction (reference, amount, the day
            # the customer picked); the WORLD puts it on the rails. Mandate setup
            # goes through the same rails-timing wiring as collections -- submit,
            # then resolve on the real AUDDIS 2-day confirmation window.
            # Deterministic "success" outcome; see the module docstring for the
            # corrected, honest basis for that choice.
            setup = desk.open_mandate(
                customer_id=cid,
                monthly_amount_gbp=monthly_amount,
                requested_date=due_date.isoformat(),
                # DD1 (2026-07-27): the customer's own staggered collection day
                # (1-28), deterministic per-customer so replay is identical and
                # no shared RNG stream moves. Spreads the book's collections
                # across the month onto real anniversaries. The customer picks it,
                # so the world holds it and TELLS the supplier.
                payment_day=staggered_payment_day(cid),
            )
            setup_submission = submit_mandate_setup(setup.reference, cid, due_date)
            setup_resolved = resolve_submission(setup_submission, "success")
            # The mandate exists once AUDDIS confirms it -- the world reports the
            # confirmation date and the desk registers it.
            desk.confirm_mandate(setup, setup_resolved.expected_outcome_date.isoformat())
            # FIXED (2026-07-12, third pass): a real Bacs integration cannot
            # submit a collection against an unconfirmed mandate -- this
            # bill's own collection due_date is now genuinely gated on the
            # mandate's own AUDDIS confirmation, pushed out if it would
            # otherwise land first. Safe by construction: payment_outcome()'s
            # success/fail decision (above, from this bill's own substream) is
            # entirely date-independent, so this never changes WHICH bills
            # succeed or fail, only the observed collection date for a
            # brand-new mandate's very first bill -- and this module's own
            # output reaches only a business-surface rendering
            # (tools/generate_dashboard_data.py::extract_dd_rails), never the
            # ledger/cash-timing pipeline that computes any published
            # financial figure, so no existing number is affected either way.
            due_date = max(due_date, setup_resolved.expected_outcome_date)
        else:
            # 2026-07-12, L2->L3 attempt: an ADDACS-style amendment fires when the
            # customer's own established bill level has genuinely drifted from the
            # mandate's collection amount -- not on a single bill's seasonal swing
            # (fixed after Expert Hour review). WHETHER it has drifted is now the
            # supplier's own re-estimation call, taken behind the door; the world
            # learns only that an amendment was issued and puts it on the rails.
            # Same deterministic-success reasoning as mandate setup -- see module
            # docstring for the corrected, honest basis (a real ~5%
            # GoCardless-cited non-confirmation rate exists, but modelling a
            # rejected amendment needs a fallback mechanism this codebase doesn't
            # have yet).
            amendment = desk.review_amendment(cid, period_end)
            if amendment is not None:
                amend_submission = submit_amendment(amendment.reference, cid, due_date)
                amend_resolved = resolve_submission(amend_submission, "success")
                desk.confirm_amendment(
                    amendment, amend_resolved.expected_outcome_date.isoformat()
                )

        # The supplier records what it billed. This is the only input its
        # re-estimation reads, and it is its own record, not a window onto the world.
        desk.note_billed_amount(cid, amount)

        # DD1 (2026-07-27): the actual collection lands on the customer's own
        # staggered day-of-month (on-or-after the rails-confirmed due date),
        # not the raw bill due date -- so the observed attempt dates spread
        # across the month rather than bunching on one relative offset. Safe
        # by construction: payment_outcome()'s success/fail decision is already
        # fixed (date-independent), rails reason-code draws depend on outcome
        # not date, and this book reaches only the DD-rails business surface
        # (extract_dd_rails), never the ledger/cash-timing pipeline -- so no
        # existing financial figure moves, only the observed collection date.
        instruction = desk.instruct_collection(
            customer_id=cid,
            period_end=period_end,
            amount_gbp=amount,
            earliest_date=due_date.isoformat(),
        )
        submission = submit_collection(
            instruction.reference,
            cid,
            instruction.amount_gbp,
            date.fromisoformat(instruction.collection_date),
        )
        decided = "success" if outcome == "success" else "failed"
        rails_rng = rails_rngs.setdefault(cid, random.Random(f"{seed + 1}:{cid}"))
        resolved = resolve_submission(submission, decided, rng=rails_rng)

        failure_reason = ""
        if resolved.status == "failed" and resolved.reason_code is not None:
            failure_reason = ARUDD_REASON_CODES.get(resolved.reason_code, "")

        # What happened to the money, reported back. The world states the fact
        # (`collected`) and the industry's own ARUDD reason text; the vocabulary the
        # register files it under is the supplier's, behind the door.
        attempt_date = resolved.expected_outcome_date.isoformat()
        if desk.record_collection_outcome(
            instruction,
            attempt_date=attempt_date,
            collected=resolved.status == "success",
            failure_reason=failure_reason,
        ):
            stops[cid] = (period_end, attempt_date)

    return desk, stops
