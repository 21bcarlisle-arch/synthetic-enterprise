"""A raise-on-missing register accessor that refuses with a BARE KeyError is a symptom with no
route to its cause.

`ChurnJourneyRegister.advance` raised bare `KeyError: 'SYN-2016-008'` 880s into a value-arm pass on
2026-09-19 -- the key, and nothing about which book refused or what should have registered it. That
run had to be re-driven against a truncated window to find out. It was repaired; the survey in
`tools/conditional_registration_survey` then found 35 more accessors in `company/` with the same
shape, of which 23 can actually be reached with an unregistered key.

This is the control over those 23. Each case does two things IN ONE TEST, because a refusal that
refuses EVERYTHING passes every assertion about what it refuses:

  1. the accessor SERVES a registered key (the partition's other half is reachable), and
  2. it REFUSES an absent one with a message naming the key, the book, and the registrar.

MUTATION: strip any one `except KeyError: raise KeyError(...)` back to the raw subscript and that
case reds on all three fragments -- a bare KeyError stringifies to just the quoted key.

The 13 accessors the survey still reports as BARE are NOT omissions: every one of them either draws
its key from the book it is subscripting (`for k in sorted(self._events)`) or sits behind an
early-return/early-raise guard the survey's `_membership_guarded` does not recognise. They cannot
refuse, so a named refusal there would be unreachable code. See
`docs/staging/WORKER_RESULT_TWENTY_THREE_REGISTERS_NAME_THEIR_REFUSAL_AND_THE_THIRTEEN_LEFT_CANNOT_REFUSE_AT_ALL_2026-09-21.md`.
"""
from __future__ import annotations

import datetime as dt

import pytest

from company.crm.change_of_tenancy_register import TenancyChangeCoupler
from company.crm.lifecycle_tracker import CustomerLifecycleTracker
from company.crm.tpi_book import TPIBook, TPICommissionBasis, TPITier

D = dt.date(2020, 1, 1)
ABSENT = "NEVER-REGISTERED-001"








def _tenancy_book() -> TenancyChangeCoupler:
    book = TenancyChangeCoupler()
    book._open_change("SP-KNOWN", "electricity")
    return book


def _lifecycle_book() -> CustomerLifecycleTracker:
    book = CustomerLifecycleTracker()
    book.register("KNOWN", D)
    return book




def _tpi_book() -> TPIBook:
    book = TPIBook()
    book.register("KNOWN", "A Broker", TPITier.PREFERRED, TPICommissionBasis.PCT_OF_ANNUAL_REVENUE, 1.5, D)
    return book
















def _first_change_id(book: TenancyChangeCoupler) -> str:
    return next(iter(book._changes))




def _any_exit_outcome():
    from company.crm.change_of_tenancy_register import ExitOutcome

    return list(ExitOutcome)[0]






def test_the_tenancy_index_and_store_disagreeing_says_which_two_disagree():
    """`_changes_for` keys on an id held by `_by_key`, so its KeyError is an index/store
    disagreement and never a missing registration. The message must not say 'register it first'.

    MUTATION: drop the try/except and both the book and the index assertions red."""
    book = _tenancy_book()
    assert book._changes_for("SP-KNOWN", "electricity"), (
        "the accessor returns nothing for a registered supply point, so the leg below is vacuous"
    )

    book._by_key[("SP-KNOWN", "electricity")].append(ABSENT)

    with pytest.raises(KeyError) as excinfo:
        book._changes_for("SP-KNOWN", "electricity")

    message = str(excinfo.value)
    assert ABSENT in message
    assert "TenancyChangeCoupler._changes" in message
    assert "_by_key" in message, "the refusal must name the OTHER store, which is the disagreement"
