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

from company.billing.payment_deferral import DeferralReason, PaymentDeferralBook
from company.billing.prepayment import PPMAccount, PPMBook
from company.crm.campaign_tracker import (
    CampaignTracker,
    CampaignType,
    ContactChannel,
    ContactOutcome,
)
from company.crm.change_of_tenancy_register import TenancyChangeCoupler
from company.crm.lifecycle_tracker import CustomerLifecycleTracker, LifecycleStage
from company.crm.solr_intake import SoLRBook
from company.crm.tpi_book import TPIBook, TPICommissionBasis, TPITier
from company.finance.credit_facility import (
    CreditFacilityBook,
    DrawdownReason,
    FacilityDrawdown,
)
from company.market.dsr_book import DSRBook
from company.market.switch_governance import (
    ErroneousTransferStatus,
    ObjectionOutcome,
    ObjectionReason,
    SwitchGovernanceBook,
)
from company.risk.risk_appetite import RiskAppetiteFramework, RiskCategory

D = dt.date(2020, 1, 1)
ABSENT = "NEVER-REGISTERED-001"


def _deferral_book() -> PaymentDeferralBook:
    book = PaymentDeferralBook()
    book.create("KNOWN", DeferralReason.FINANCIAL_HARDSHIP, 120.0, D, dt.date(2020, 7, 1), 20.0)
    return book


def _ppm_book() -> PPMBook:
    book = PPMBook()
    book.register(PPMAccount(customer_id="KNOWN", meter_id="MTR-1", balance_gbp=10.0))
    return book


def _campaign_book() -> CampaignTracker:
    book = CampaignTracker()
    book.create_campaign("KNOWN", CampaignType.RETENTION_WINBACK, D, 10, ContactChannel.EMAIL)
    return book


def _tenancy_book() -> TenancyChangeCoupler:
    book = TenancyChangeCoupler()
    book._open_change("SP-KNOWN", "electricity")
    return book


def _lifecycle_book() -> CustomerLifecycleTracker:
    book = CustomerLifecycleTracker()
    book.register("KNOWN", D)
    return book


def _solr_book() -> SoLRBook:
    book = SoLRBook("OUR-SUPPLIER")
    book.register_batch("KNOWN", "FAILED-SUPPLIER", D, 100)
    return book


def _tpi_book() -> TPIBook:
    book = TPIBook()
    book.register("KNOWN", "A Broker", TPITier.PREFERRED, TPICommissionBasis.PCT_OF_ANNUAL_REVENUE, 1.5, D)
    return book


def _facility_book() -> CreditFacilityBook:
    book = CreditFacilityBook()
    book.register_facility("KNOWN", "A Lender", 1_000_000.0, 6.0, 0.5, dt.date(2025, 1, 1))
    return book


def _dsr_book() -> DSRBook:
    book = DSRBook()
    book.enroll("KNOWN", "MPAN-1", 2.0, D)
    return book


def _switch_book() -> SwitchGovernanceBook:
    book = SwitchGovernanceBook()
    book.raise_objection("MPAN-1", "SUP-1", D, D, ObjectionReason.DEBT)
    book.report_et("MPAN-2", "SUP-1", "SUP-2", D, D)
    return book


def _risk_book() -> RiskAppetiteFramework:
    book = RiskAppetiteFramework(D)
    book.add_limit("KNOWN", RiskCategory.MARKET, "a limit", 100.0, "GBP")
    return book


def _first_deferral_id(book: PaymentDeferralBook) -> str:
    return next(iter(book._deferrals))


def _first_objection_id(book: SwitchGovernanceBook) -> str:
    return next(iter(book._objections))


def _first_et_id(book: SwitchGovernanceBook) -> str:
    return next(iter(book._ets))


def _first_change_id(book: TenancyChangeCoupler) -> str:
    return next(iter(book._changes))


# (label, build, serve-a-registered-key, refuse-an-absent-key, book name, registrar name)
CASES = [
    (
        "PaymentDeferralBook.record_repayment", _deferral_book,
        lambda b: b.record_repayment(_first_deferral_id(b), 10.0),
        lambda b: b.record_repayment(ABSENT, 10.0),
        "PaymentDeferralBook._deferrals", "create()",
    ),
    (
        "PaymentDeferralBook.mark_defaulted", _deferral_book,
        lambda b: b.mark_defaulted(_first_deferral_id(b)),
        lambda b: b.mark_defaulted(ABSENT),
        "PaymentDeferralBook._deferrals", "create()",
    ),
    (
        "PaymentDeferralBook.cancel", _deferral_book,
        lambda b: b.cancel(_first_deferral_id(b)),
        lambda b: b.cancel(ABSENT),
        "PaymentDeferralBook._deferrals", "create()",
    ),
    (
        "PPMBook.top_up", _ppm_book,
        lambda b: b.top_up("KNOWN", 5.0, "2020-01-01"),
        lambda b: b.top_up(ABSENT, 5.0, "2020-01-01"),
        "PPMBook._accounts", "register()",
    ),
    (
        "PPMBook.consume_daily", _ppm_book,
        lambda b: b.consume_daily("KNOWN", 8.0, 0.15, 0.40, "2020-01-01"),
        lambda b: b.consume_daily(ABSENT, 8.0, 0.15, 0.40, "2020-01-01"),
        "PPMBook._accounts", "register()",
    ),
    (
        "CampaignTracker.get", _campaign_book,
        lambda b: b.get("KNOWN"),
        lambda b: b.get(ABSENT),
        "CampaignTracker._campaigns", "create_campaign()",
    ),
    (
        "CampaignTracker.record_contact", _campaign_book,
        lambda b: b.record_contact("KNOWN", "CUST-1", D, ContactOutcome.CONVERTED),
        lambda b: b.record_contact(ABSENT, "CUST-1", D, ContactOutcome.CONVERTED),
        "CampaignTracker._campaigns", "create_campaign()",
    ),
    (
        "CampaignTracker.close_campaign", _campaign_book,
        lambda b: b.close_campaign("KNOWN", D),
        lambda b: b.close_campaign(ABSENT, D),
        "CampaignTracker._campaigns", "create_campaign()",
    ),
    (
        "TenancyChangeCoupler.get", _tenancy_book,
        lambda b: b.get(_first_change_id(b)),
        lambda b: b.get(ABSENT),
        "TenancyChangeCoupler._changes", "_open_change()",
    ),
    (
        "TenancyChangeCoupler.record_exit_outcome", _tenancy_book,
        lambda b: b.get(_first_change_id(b)),
        lambda b: b.record_exit_outcome(ABSENT, _any_exit_outcome(), D),
        "TenancyChangeCoupler._changes", "_open_change()",
    ),
    (
        "TenancyChangeCoupler.record_acquisition_outcome", _tenancy_book,
        lambda b: b.record_acquisition_outcome(_first_change_id(b), won=True),
        lambda b: b.record_acquisition_outcome(ABSENT, won=True),
        "TenancyChangeCoupler._changes", "_open_change()",
    ),
    (
        "CustomerLifecycleTracker.get", _lifecycle_book,
        lambda b: b.get("KNOWN"),
        lambda b: b.get(ABSENT),
        "CustomerLifecycleTracker._customers", "register()",
    ),
    (
        "CustomerLifecycleTracker.transition", _lifecycle_book,
        lambda b: b.transition("KNOWN", LifecycleStage.ACTIVE, D),
        lambda b: b.transition(ABSENT, LifecycleStage.ACTIVE, D),
        "CustomerLifecycleTracker._customers", "register()",
    ),
    (
        "SoLRBook.batch_summary", _solr_book,
        lambda b: b.batch_summary("KNOWN"),
        lambda b: b.batch_summary(ABSENT),
        "SoLRBook._batches", "register_batch()",
    ),
    (
        "TPIBook.record_deal", _tpi_book,
        lambda b: b.record_deal("KNOWN", "CUST-1", 50.0, 6000.0, D),
        lambda b: b.record_deal(ABSENT, "CUST-1", 50.0, 6000.0, D),
        "TPIBook._tpis", "register()",
    ),
    (
        "CreditFacilityBook.drawdown", _facility_book,
        lambda b: b.drawdown("KNOWN", 1000.0, D, DrawdownReason.WORKING_CAPITAL),
        lambda b: b.drawdown(ABSENT, 1000.0, D, DrawdownReason.WORKING_CAPITAL),
        "CreditFacilityBook._facilities", "register_facility()",
    ),
    (
        "CreditFacilityBook.utilisation_pct", _facility_book,
        lambda b: b.utilisation_pct("KNOWN"),
        lambda b: b.utilisation_pct(ABSENT),
        "CreditFacilityBook._facilities", "register_facility()",
    ),
    (
        "DSRBook.dispatch", _dsr_book,
        lambda b: b.dispatch(
            "KNOWN", 1.0, dt.datetime(2020, 1, 1, 17), dt.datetime(2020, 1, 1, 18), 1.0),
        lambda b: b.dispatch(
            ABSENT, 1.0, dt.datetime(2020, 1, 1, 17), dt.datetime(2020, 1, 1, 18), 1.0),
        "DSRBook._participants", "enroll()",
    ),
    (
        "SwitchGovernanceBook.resolve_objection", _switch_book,
        lambda b: b.resolve_objection(_first_objection_id(b), ObjectionOutcome.UPHELD, D),
        lambda b: b.resolve_objection(ABSENT, ObjectionOutcome.UPHELD, D),
        "SwitchGovernanceBook._objections", "raise_objection()",
    ),
    (
        "SwitchGovernanceBook.resolve_et", _switch_book,
        lambda b: b.resolve_et(_first_et_id(b), ErroneousTransferStatus.CUSTOMER_RETURNED, D),
        lambda b: b.resolve_et(ABSENT, ErroneousTransferStatus.CUSTOMER_RETURNED, D),
        "SwitchGovernanceBook._ets", "report_et()",
    ),
    (
        "RiskAppetiteFramework.record_measurement", _risk_book,
        lambda b: b.record_measurement("KNOWN", 50.0, D),
        lambda b: b.record_measurement(ABSENT, 50.0, D),
        "RiskAppetiteFramework._limits", "add_limit()",
    ),
]


def _any_exit_outcome():
    from company.crm.change_of_tenancy_register import ExitOutcome

    return list(ExitOutcome)[0]


@pytest.mark.parametrize(
    "label,build,serve,refuse,book,registrar", CASES, ids=[c[0] for c in CASES]
)
def test_the_accessor_serves_a_registered_key_and_refuses_an_absent_one_by_name(
    label, build, serve, refuse, book, registrar
):
    """One control over the whole partition. The serve leg is not decoration: without it a book
    that refused every key -- registered or not -- would pass the refusal assertions cleanly."""
    served = build()
    serve(served)  # must not raise: the accessor is reachable for a registered key

    with pytest.raises(KeyError) as excinfo:
        refuse(build())

    message = str(excinfo.value)
    assert ABSENT in message, f"{label}: the refusal must name the key it refused"
    assert book in message, (
        f"{label}: the refusal must name the book that refused -- a traceback deep inside a "
        f"long run is the cheap evidence, and re-driving the run is the expensive one"
    )
    assert registrar in message, (
        f"{label}: the refusal must name what should have registered the key; without it the "
        f"reader has the symptom and no route to the cause"
    )


def test_a_drawdown_outliving_its_facility_names_the_disagreement_not_just_the_key():
    """`total_interest_accrued_gbp` keys on the DRAWDOWN's facility_id, so its refusal means the
    two stores disagree -- a different failure from 'nobody registered it', and the message says so.

    MUTATION: drop the try/except and the assertions on the book and the drawdown id both red."""
    book = _facility_book()
    book.drawdown("KNOWN", 1000.0, D, DrawdownReason.WORKING_CAPITAL)
    assert book.total_interest_accrued_gbp(dt.date(2021, 1, 1)) > 0.0, (
        "the accessor cannot even total a registered facility, so the leg below is vacuous"
    )

    book._drawdowns.append(FacilityDrawdown(
        drawdown_id="DD-ORPHAN", facility_id=ABSENT, amount_gbp=500.0,
        drawdown_date=D, reason=DrawdownReason.EMERGENCY,
    ))

    with pytest.raises(KeyError) as excinfo:
        book.total_interest_accrued_gbp(dt.date(2021, 1, 1))

    message = str(excinfo.value)
    assert ABSENT in message
    assert "CreditFacilityBook._facilities" in message
    assert "DD-ORPHAN" in message, (
        "which drawdown points at the absent facility is the whole diagnosis here"
    )


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
