"""The supplier's own Direct Debit collections desk — the code that OPERATES the
collection register.

WHY THIS MODULE EXISTS (KNIFE pass 3, design `B4_billing_mechanics_reached_directly`,
the LAST of that design's four edges)
--------------------------------------------------------------------------------
`simulation/dd_collection_book.py` used to do this:

    from company.billing.direct_debit import (
        DirectDebitBook, DDPaymentAttempt, next_collection_on_day,
    )

and then, inside the world's own loop: open a `DirectDebitBook`, create mandates on
it, decide when a mandate's standing amount had drifted far enough to amend, snap the
collection onto the customer's anniversary, and append `DDPaymentAttempt`s. The
register's B4 block named this the hard one and said why:

> `dd_collection_book` does not merely CONSULT the company's billing module — it
> BUILDS the company's artefact ... so the world is operating the supplier's
> collection register.

That is worse than an ordinary crossing in the same way B4's private-function import
was: not because of the edge count, but because the world had the supplier's routines
in its hands. A real household does not run its supplier's collections desk. It is
told an amount and a date, the money moves or it does not, and the supplier writes
that down.

WHAT CROSSES, PRECISELY
-----------------------
In (the world → the desk), all of it observable to a real supplier:

  * a customer is being billed £X for a period ending on a date, and the bill's
    payment terms make it due on a date;
  * the customer's chosen collection day-of-month (a customer fact — the world owns
    it, `simulation/dd_payment_day.py`, moved there by this same design);
  * what the BACS RAILS did: the date AUDDIS confirmed a new mandate, the date an
    ADDACS amendment confirmed, the date a collection resolved, whether the money
    arrived, and — when it did not — the ARUDD reason text. Rails timing is industry
    physics; the supplier observes it, it does not choose it.

Out (the desk → the world) — three instructions and nothing else:

  * `MandateSetupInstruction` — please set this mandate up, at this amount, on this
    day, under this reference;
  * `AmendmentInstruction` — the standing amount has been re-estimated to this;
  * `CollectionInstruction` — collect this amount on this date under this reference.

NOT crossing, and this is the substance of the cut: `DirectDebitBook`,
`DirectDebitMandate`, `DDPaymentAttempt`, `next_collection_on_day`, the re-estimation
window and its materiality floor. The world can no longer construct a mandate, cannot
name an attempt's outcome vocabulary, and cannot re-derive a collection date. It
reports what happened to the money.

THIS ONE IS A PUSH, AND THAT IS WORTH SAYING PLAINLY
-----------------------------------------------------
B4's other two landed cuts (`company/interfaces/credit_refund_requests.py`,
`company/interfaces/dd_review_outcome.py`) are PULLS through named doors, and both
docstrings record the same honest limit: the design asks for the company to EMIT and
the world to APPLY, and there was no company-side emitter to emit from. That blocker
was measured away at step 11 (`company/billing/monthly_bill_assembly.py`). This edge
does not need to borrow that emitter — the instruction it needs is a collection
instruction, and this module is its emitter. The world applies what it receives.

WHAT THIS DELIBERATELY DOES NOT DO
-----------------------------------
It does not decide WHETHER the money arrives. That is the world's: the household's
balance on the day is a fact about the household, and `simulation/arrears_engine.py`
keeps it, drawn from its own per-bill substream. A desk that decided its own
collection outcomes would be the B2 inversion in miniature — the company's belief
constituting the fact it is a belief about.

It does not move a number. Every routine below was lifted from
`build_dd_collection_book` with its arithmetic, its ordering and its reference
strings unchanged, because a wall pass is not where a behaviour change gets
discovered. `tests/company/billing/test_dd_collections_desk.py` pins that as an
equivalence claim rather than an assertion.

REUSE: company/billing/dd_collections_desk.py
CLASS: CUSTOM
INDEX: searched "direct debit", "collection", "mandate", "collections desk" -- 21/33/35/1
rows. Two candidates were real and both were answered rather than waved past.
`company.billing.direct_debit` holds the REGISTER (`DirectDebitBook`,
`DDPaymentAttempt`, `next_collection_on_day`) and this module STANDS ON it, importing
all three and duplicating none -- what is new here is the operating routine that used
to sit in `simulation/dd_collection_book.py`, which is a different thing from the
store it writes into and does not belong in a dataclass module.
`company.billing.dd_mandate_register` is the closer name and extending it is
FORBIDDEN BY AN EXISTING CONTROL: it is the caller-free duplicate the M2 payments audit
named, and `tests/company/billing/test_dd_mandate_register.py::test_module_stays_caller_free_structural_guard`
exists precisely to stop a second live writer arriving in overlapping mandate state.
Extending it would have red that guard, correctly.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from company.billing.direct_debit import (
    DDPaymentAttempt,
    DirectDebitBook,
    next_collection_on_day,
)

# The supplier's re-estimation routine. Both constants were the world's before this
# cut and neither is a fact about a household: the floor is what the supplier thinks
# is worth writing a letter about, and the window is how much history its estimate
# looks back over. See `_review_amendment` for why the statistic is a median.
AMENDMENT_MATERIALITY_THRESHOLD_GBP = 1.00
AMENDMENT_WINDOW_BILLS = 12  # roughly a year of monthly billing

# The masked bank detail the register carries. No real bank data exists anywhere in
# this project and none is invented here; the mask matches `DirectDebitMandate`'s own
# convention. It is the SUPPLIER's placeholder, which is why it sits on this side.
_MASKED_SORT_CODE = "00-00-**"
_MASKED_ACCOUNT_LAST4 = "0000"


@dataclass(frozen=True)
class MandateSetupInstruction:
    """Set this mandate up on the rails. The reference is the supplier's."""

    reference: str
    customer_id: str
    monthly_amount_gbp: float
    requested_date: str
    payment_day: int


@dataclass(frozen=True)
class AmendmentInstruction:
    """The standing amount has been re-estimated; tell the bank (ADDACS)."""

    reference: str
    customer_id: str
    new_monthly_amount_gbp: float


@dataclass(frozen=True)
class CollectionInstruction:
    """Collect this amount, on this date, under this reference."""

    reference: str
    customer_id: str
    amount_gbp: float
    collection_date: str


class DirectDebitCollectionsDesk:
    """Operates one supplier's DD collection register.

    The world drives the desk one bill at a time and reports rails outcomes back;
    every write into the register happens in here.
    """

    def __init__(self) -> None:
        self._book = DirectDebitBook()
        # Amounts this desk has actually billed each customer, oldest first. It is
        # the desk's own record of its own bills — not a window onto the world.
        self._billed_history: dict[str, list[float]] = {}

    # -- what the world may ask about the register -------------------------------

    def has_mandate(self, customer_id: str) -> bool:
        return self._book.get_mandate(customer_id) is not None

    def collection_register(self) -> DirectDebitBook:
        """The supplier's own collection register, published for reporting.

        This is an OUTPUT of the desk, not a handle the world writes through: the
        world receives it at the end of a run and passes it to the report serialiser.
        The register class itself is unnameable from the SIM after this cut, so the
        world cannot construct one, cannot add a mandate to one and cannot append an
        attempt to one — which is the property B4 was about.
        """
        return self._book

    # -- mandate lifecycle -------------------------------------------------------

    def open_mandate(
        self,
        customer_id: str,
        monthly_amount_gbp: float,
        requested_date: str,
        payment_day: int,
    ) -> MandateSetupInstruction:
        """Issue a mandate-setup instruction. Nothing is registered yet — a real
        mandate exists once AUDDIS confirms it, which is the rails' answer to give.
        """
        return MandateSetupInstruction(
            reference=f"MANDATE-{customer_id}-{requested_date}",
            customer_id=customer_id,
            monthly_amount_gbp=monthly_amount_gbp,
            requested_date=requested_date,
            payment_day=payment_day,
        )

    def confirm_mandate(
        self, instruction: MandateSetupInstruction, confirmed_date: str
    ) -> None:
        """AUDDIS confirmed on `confirmed_date`: register the mandate."""
        self._book.create_mandate(
            customer_id=instruction.customer_id,
            sort_code=_MASKED_SORT_CODE,
            account_last4=_MASKED_ACCOUNT_LAST4,
            monthly_amount_gbp=instruction.monthly_amount_gbp,
            setup_date=instruction.requested_date,
            setup_rails_reference=instruction.reference,
            setup_confirmed_date=confirmed_date,
            payment_day=instruction.payment_day,
        )

    def review_amendment(
        self, customer_id: str, period_end: str
    ) -> AmendmentInstruction | None:
        """Re-estimate this customer's standing monthly amount, and return an
        amendment instruction if the established level has genuinely drifted.

        The statistic is a MEDIAN over a trailing window, and both choices are
        load-bearing rather than incidental — a mean is dragged by one anomalous or
        seasonal bill, and an unbounded all-time average chases a sustained step
        change forever without converging. Neither is what an annual re-estimate
        does. The window is trailing and the comparison is against the mandate's own
        stored amount, so an amendment fires when the level has moved, not when a
        single winter bill has.
        """
        mandate = self._book.get_mandate(customer_id)
        if mandate is None:
            return None
        history = (self._billed_history.get(customer_id) or [])[-AMENDMENT_WINDOW_BILLS:]
        if not history:
            return None
        rolling_median = statistics.median(history)
        if abs(rolling_median - mandate.monthly_amount_gbp) <= AMENDMENT_MATERIALITY_THRESHOLD_GBP:
            return None
        return AmendmentInstruction(
            reference=f"AMEND-{mandate.mandate_reference}-{period_end}",
            customer_id=customer_id,
            new_monthly_amount_gbp=round(rolling_median, 2),
        )

    def confirm_amendment(
        self, instruction: AmendmentInstruction, confirmed_date: str
    ) -> None:
        """ADDACS confirmed on `confirmed_date`: the new amount stands."""
        self._book.amend_mandate(
            customer_id=instruction.customer_id,
            new_monthly_amount_gbp=instruction.new_monthly_amount_gbp,
            rails_reference=instruction.reference,
            confirmed_date=confirmed_date,
        )

    # -- billing and collection --------------------------------------------------

    def note_billed_amount(self, customer_id: str, amount_gbp: float) -> None:
        """Record what this customer was actually billed. This is the desk's own
        history and the only input `review_amendment` reads."""
        self._billed_history.setdefault(customer_id, []).append(amount_gbp)

    def instruct_collection(
        self,
        customer_id: str,
        period_end: str,
        amount_gbp: float,
        earliest_date: str,
    ) -> CollectionInstruction:
        """Decide when and for how much to collect.

        This is Variable DD: the bill's own amount is collected, and the mandate's
        stored `monthly_amount_gbp` is an estimated reference level that sizes
        nothing (it only decides when a re-estimation notice fires). The date snaps
        forward onto the customer's own collection anniversary, never earlier than
        `earliest_date`.
        """
        mandate = self._book.get_mandate(customer_id)
        if mandate is None:
            raise ValueError(
                f"no mandate registered for {customer_id}; confirm one before instructing a collection"
            )
        return CollectionInstruction(
            reference=f"{mandate.mandate_reference}-{period_end}",
            customer_id=customer_id,
            amount_gbp=amount_gbp,
            collection_date=next_collection_on_day(earliest_date, mandate.payment_day),
        )

    def record_collection_outcome(
        self,
        instruction: CollectionInstruction,
        attempt_date: str,
        collected: bool,
        failure_reason: str = "",
    ) -> None:
        """The rails resolved: write the attempt into the register.

        `collected` is a fact about the money, which is the world's to report. The
        outcome VOCABULARY the register stores it under is the supplier's, which is
        why the world passes a bool and not a string.
        """
        mandate = self._book.get_mandate(instruction.customer_id)
        if mandate is None:
            raise ValueError(
                f"no mandate registered for {instruction.customer_id}; cannot record an attempt"
            )
        self._book.record_attempt(
            DDPaymentAttempt(
                mandate_reference=mandate.mandate_reference,
                customer_id=instruction.customer_id,
                attempt_date=attempt_date,
                amount_gbp=instruction.amount_gbp,
                outcome="collected" if collected else "failed",
                failure_reason=failure_reason,
            )
        )
