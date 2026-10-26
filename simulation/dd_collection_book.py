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

import simulation.bacs_rails as bacs_rails
from company.interfaces.bill_assembly import owed_after_scheme_credit
from company.interfaces.dd_collection_instructions import open_collections_desk
from simulation.arrears_engine import (
    PAY_ON_RECEIPT_METHOD,
    PAYMENT_TERMS_DAYS,
    _fuel_poor_for_bill,
    _tone_for_bill,
    bill_substream,
    mover_final_bill_outcome,
    payment_method,
    payment_outcome,
    stress_for_year,
)
from simulation.bacs_rails import (
    ARUDD_REASON_CODES,
    draw_re_mandate_answer,
    payer_cancellation,
    resolve_submission,
    submit_amendment,
    submit_collection,
    submit_mandate_setup,
)
from simulation.dd_payment_day import staggered_payment_day
from simulation.rng_substream import substream

#: The household's answer to an invitation back onto DD is drawn here, one stream per invitation.
RE_MANDATE_STREAM = "PB8_re_mandate_answer"

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


def supplier_dd_spells(bills: list[dict], behavioral: dict, seed: int = 42
                       ) -> dict[str, list[tuple[str, str | None]]]:
    """PB8: each household's spells off Direct Debit, as `[(off_after, on_after), ...]` of period_ends.

    A bill with `off_after < period_end <= on_after` is payable on receipt: `off_after` is the last
    bill the supplier presented by DD before the stop (its own, or the household's ADDACS 1), and
    `on_after` the last on-receipt bill before a re-mandate the household signed. `on_after` None:
    still off at the end of the bills. This is the money side's key (`arrears_engine.paying_method`).
    """
    return {cid: [(s[0], s[2]) for s in spells]
            for cid, spells in _run_rails(bills, behavioral, None, seed)[1].items()}


def supplier_dd_spell_notices(bills: list[dict], behavioral: dict, seed: int = 42
                              ) -> dict[str, list[tuple[str, str | None]]]:
    """The same spells as dates, `[(off_from, on_from), ...]`: the day the household was told its DD
    had ended (the return that stopped it, or the ADDACS 1 day), and the day AUDDIS confirmed the
    mandate it signed again. The as-of key for anything asked mid-run (`StopNoticeBoard`)."""
    return {cid: [(s[1], s[3]) for s in spells]
            for cid, spells in _run_rails(bills, behavioral, None, seed)[1].items()}


def supplier_dd_stops(bills: list[dict], behavioral: dict, seed: int = 42) -> dict[str, str]:
    """`{customer_id: period_end}` for the households still off DD at the end of these bills: the
    last bill presented by DD before their open spell. Readers that ask about one bill take
    `supplier_dd_spells`; a household that came back onto DD is not here."""
    return {cid: spells[-1][0] for cid, spells in supplier_dd_spells(bills, behavioral, seed).items()
            if spells[-1][1] is None}


def supplier_dd_stop_notices(bills: list[dict], behavioral: dict, seed: int = 42) -> dict[str, str]:
    """`{customer_id: notice_date}` of the open spell, as `supplier_dd_stops`."""
    return {cid: spells[-1][0]
            for cid, spells in supplier_dd_spell_notices(bills, behavioral, seed).items()
            if spells[-1][1] is None}


def _off_dd_notice(spells: list[tuple[str, str | None]], as_of: str) -> str | None:
    """The notice date of the spell `as_of` falls in, or None if the household was on DD then."""
    for off_from, on_from in spells:
        if off_from <= as_of and (on_from is None or as_of < on_from):
            return off_from
    return None


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

    def __init__(self, stress_trajectory_of, seed: int = 42, dd_shock_responses_of=None,
                 payment_truth_of=None) -> None:
        self._stress_trajectory_of = stress_trajectory_of
        # One payment truth: the triad's outcomes so far for a supply point, so the board's rails
        # stop a DD on the returns the household actually made. None while the switch is off.
        self._payment_truth_of = payment_truth_of
        self._seed = seed
        # DD4b: a household's own response to a DD shock moves its returns, so the board's rails
        # read it as the post-run rails do. None, or an empty answer, adds no key.
        self._dd_shock_responses_of = dd_shock_responses_of
        self._records: dict[str, list[dict]] = {}
        # A spell list nothing can change any more: the household is off DD and no invitation back
        # can be answered (`bacs_rails.REMANDATE_ACCEPTANCE_PROBABILITY` None), so the stop is final.
        self._final: dict[str, list[tuple[str, str | None]]] = {}
        # Otherwise the spells as billed through a month, re-asked once a later month is billed.
        self._spells_through: dict[str, tuple[date, list[tuple[str, str | None]]]] = {}
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
        """The notice date of the stop, if the household had been told by `as_of` and had not signed
        a new mandate that AUDDIS confirmed by then; else None."""
        final = self._final.get(supply_point)
        if final is not None:
            return _off_dd_notice(final, as_of)
        cutoff = date.fromisoformat(as_of).replace(day=1)
        known = self._spells_through.get(supply_point)
        if known is not None and known[0] >= cutoff:
            return _off_dd_notice(known[1], as_of)
        records = [r for r in self._records.get(supply_point, [])
                   if r.get("settlement_date", "9999") < cutoff.isoformat()]
        if not records:
            return None
        from company.interfaces.bill_assembly import issued_bills
        from simulation.run_phase4c_on_phase2b import build_monthly_bills
        bills = issued_bills(build_monthly_bills(records, set()))
        behavioral = {supply_point: {
            "income_stress_trajectory": self._stress_trajectory_of(supply_point)}}
        if self._dd_shock_responses_of is not None:
            from simulation.dd_shock_response import RECORD_KEY
            responses = self._dd_shock_responses_of(supply_point)
            if responses:
                behavioral[supply_point][RECORD_KEY] = responses
        if self._payment_truth_of is not None:
            from simulation.world_payment_truth import RECORD_KEY as TRUTH_KEY
            behavioral[supply_point][TRUTH_KEY] = self._payment_truth_of(supply_point)
        spells = supplier_dd_spell_notices(bills, behavioral, self._seed).get(supply_point, [])
        if spells and bacs_rails.REMANDATE_ACCEPTANCE_PROBABILITY is None:
            self._final[supply_point] = spells
        self._spells_through[supply_point] = (cutoff, spells)
        return _off_dd_notice(spells, as_of)


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
    Returns the desk and each household's spells off DD, `[off_after, off_from, on_after, on_from]`
    (`supplier_dd_spells` reads the period_ends, `supplier_dd_spell_notices` the dates).

    A spell is opened by the desk's stop or the household's ADDACS 1, and closed only by a mandate
    the household signs when the desk invites it back. The desk invites on its own ledger of on-receipt
    bills, which this loop feeds it (`_paid_on_receipt_by_due_date`); the household answers only
    while `bacs_rails.REMANDATE_ACCEPTANCE_PROBABILITY` is set. While it is None nobody is invited,
    and every spell stays open to the end of the bills.

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
    import simulation.world_payment_truth as wpt
    from simulation.dd_shock_response import RECORD_KEY as SHOCK_RECORD_KEY
    from simulation.dd_shock_response import bill_effect, failure_table
    rails_rngs: dict[str, random.Random] = {}
    desk = open_collections_desk()
    spells: dict[str, list[list]] = {}
    acceptance = bacs_rails.REMANDATE_ACCEPTANCE_PROBABILITY
    # Households that signed a new mandate: their earlier cancellation at the bank (DD4b) is spent.
    re_signed: set[str] = set()
    monthly_amount_by_customer = monthly_amount_by_customer or {}

    for bill in sorted(bills, key=lambda b: (b["customer_id"], b["period_end"])):
        cid = bill["customer_id"]
        segment = bill.get("segment", "resi")
        amount = bill["total_amount_gbp"]
        period_end = bill["period_end"]
        year = int(period_end[:4])

        method = payment_method(segment, amount, cid, bill.get("commodity", "electricity"))
        # ONE PAYMENT TRUTH (`simulation/world_payment_truth.py`): a leg whose record carries the
        # triad's truth is put on the rails by the channel it actually paid by that month, and its
        # outcome is the household's, not a second draw. Absent while the switch is off.
        told = wpt.truth_outcome((behavioral.get(cid) or {}).get(wpt.RECORD_KEY), period_end)
        if told is not None:
            method = told["method"]
        # A non-DD bill can now be skipped BEFORE drawing its outcome: the
        # draw is keyed by (cid, period_end), so not making it cannot shift
        # any other bill's result. Under the old shared stream this loop had
        # to draw for every bill purely to stay in lockstep with
        # compute_emergent_bad_debt() -- an obligation each of the four
        # consumers had to hand-maintain, and one of them (the billing ledger)
        # did not.
        if method != "direct_debit":
            continue
        # PB8: the DD has ended (the desk's stop or the household's ADDACS 1), so the bill is
        # payable on receipt and nothing is put on the rails for it. The desk sees whether it was
        # paid by its due date on its own ledger, and may invite the household back. Under one
        # payment truth the triad holds the channel, so its legs are not invited here.
        if desk.has_mandate(cid) and not desk.pays_by_direct_debit(cid):
            paid = None if told is not None else _paid_on_receipt_by_due_date(bill, behavioral, seed)
            if paid is not None:
                desk.note_receipt_payment(cid, paid)
                if acceptance is not None and _re_mandate(desk, cid, period_end, acceptance, seed,
                                                          spells[cid][-1]):
                    re_signed.add(cid)
            continue
        # DD4b (`simulation/dd_shock_response.py`): a household that cancelled its own mandate
        # after a DD shock has nothing on the rails from the month after; that month's collection
        # comes back unpaid. NO_EFFECT on every record while the toggles are at zero.
        shock = bill_effect((behavioral.get(cid) or {}).get(SHOCK_RECORD_KEY), period_end[:7])
        if shock.cancelled and told is None and cid not in re_signed:
            continue
        stress = stress_for_year(behavioral.get(cid) or {}, year)
        commodity = bill.get("commodity", "electricity")
        exit_ = (None if told is not None else
                 mover_final_bill_outcome(behavioral.get(cid) or {}, cid, period_end, commodity,
                                          amount, method, stress, seed))
        if told is not None:
            outcome = "success" if told["result"] == "success" else "failed"
        elif exit_ is not None:
            outcome = exit_[0]
        elif shock.cancel_return:
            outcome = "failed"
        else:
            outcome, _days_late = payment_outcome(
                method, stress, bill_substream(seed, cid, period_end, commodity),
                segment,
                _fuel_poor_for_bill(method, cid),
                _tone_for_bill(method, cid, period_end), cid,
                dd_failure_prob=failure_table(shock.failure_multiplier),
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
            spells.setdefault(cid, []).append([period_end, attempt_date, None, None])
        # PB8 L2, the household's route: it cancelled at its bank, the collection came back
        # "instruction cancelled", and the supplier reads ADDACS 1 the next working day. The desk
        # cancels from that date, so this is the last bill presented and the notice is the ADDACS day.
        if shock.cancel_return and told is None and exit_ is None:
            addacs = payer_cancellation(instruction.reference, cid, date.fromisoformat(attempt_date))
            if desk.record_payer_cancellation(cid, addacs.available_date.isoformat()):
                spells.setdefault(cid, []).append(
                    [period_end, addacs.available_date.isoformat(), None, None])

    return desk, spells


def _paid_on_receipt_by_due_date(bill: dict, behavioral: dict, seed: int) -> bool | None:
    """Was this on-receipt bill paid by its due date? None when the payer owed nothing on it.

    Drawn as `arrears_engine._resolve_bills` draws the same bill, from the same substream and the
    same inputs, so the desk's ledger is the money side's outcome and not a second opinion.
    """
    cid, period_end = bill["customer_id"], bill["period_end"]
    segment = bill.get("segment", "resi")
    commodity = bill.get("commodity", "electricity")
    occupier_share = bill.get("occupier_share", 0.0) + bill.get("void_owner_share", 0.0)
    if occupier_share >= 1.0 - 1e-9:
        return None
    amount = bill["total_amount_gbp"]
    if occupier_share > 0.0:
        amount = round(amount * (1.0 - occupier_share), 2)
    amount = owed_after_scheme_credit(amount, segment, commodity, period_end[:7])
    if amount <= 0:
        return None
    stress = stress_for_year(behavioral.get(cid) or {}, int(period_end[:4]))
    method = PAY_ON_RECEIPT_METHOD
    exit_ = mover_final_bill_outcome(behavioral.get(cid) or {}, cid, period_end, commodity, amount,
                                     method, stress, seed)
    if exit_ is not None:
        outcome, days_late = exit_[0], exit_[1]
    else:
        outcome, days_late = payment_outcome(
            method, stress, bill_substream(seed, cid, period_end, commodity), segment,
            _fuel_poor_for_bill(payment_method(segment, amount, cid, commodity), cid),
            _tone_for_bill(method, cid, period_end), cid,
        )
    return outcome == "success" and days_late == 0


def _re_mandate(desk, cid: str, period_end: str, acceptance: float, seed: int, spell: list) -> bool:
    """Put the desk's invitation, if it makes one, to the household, and close `spell` if it signs.

    The desk reviews on the bill's due date, the day it knows the bill was paid in time. A signed
    mandate goes through AUDDIS like any setup; the bills after this one are presented by DD again.
    """
    as_of = date.fromisoformat(period_end) + timedelta(days=PAYMENT_TERMS_DAYS)
    invitation = desk.review_re_mandate(cid, as_of.isoformat(), staggered_payment_day(cid))
    if invitation is None:
        return False
    u = substream(RE_MANDATE_STREAM, f"{cid}::{period_end}", seed).random()
    if not draw_re_mandate_answer(u, acceptance):
        desk.record_re_mandate_declined(invitation)
        return False
    resolved = resolve_submission(submit_mandate_setup(invitation.reference, cid, as_of), "success")
    confirmed = resolved.expected_outcome_date.isoformat()
    desk.confirm_mandate(invitation, confirmed)
    spell[2], spell[3] = period_end, confirmed
    return True
