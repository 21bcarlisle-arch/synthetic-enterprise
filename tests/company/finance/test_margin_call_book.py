import pytest
from company.finance.margin_call_book import (
    MarginCallBook, MarginCallEvent, MarginCallStatus, build_margin_calls_from_mtm,
    book_scaled_credit_facility_gbp, FACILITY_COVERAGE_MULTIPLE, FACILITY_MIN_GBP,
)
from company.trading.forward_book import ForwardContract, TradingBook
from company.trading.wholesale_credit_exposure import (
    ClearingStatus, CounterpartyCreditRating, CounterpartyType,
)


def _call(cid="MC001", date="2022-09-15", cpty="BARCLAYS", contract="FWD001",
          init=100_000.0, var=800_000.0, deadline="2022-09-16"):
    return MarginCallEvent(
        call_id=cid, call_date=date, counterparty=cpty, contract_id=contract,
        initial_margin_gbp=init, variation_margin_gbp=var, settlement_deadline=deadline
    )


def test_total_margin_required():
    c = _call(init=100_000.0, var=800_000.0)
    assert abs(c.total_margin_required_gbp - 900_000.0) < 0.01


def test_is_stress_event():
    c = _call(var=800_000.0)
    assert c.is_stress_event is True


def test_not_stress_event():
    c = _call(var=100_000.0)
    assert c.is_stress_event is False


def test_is_settled_initial():
    c = _call()
    assert c.is_settled is False


def test_settle_call():
    book = MarginCallBook()
    book.record_call(_call())
    settled = book.settle_call("MC001")
    assert settled is not None
    assert settled.is_settled is True
    assert len(book.outstanding_calls()) == 0


def test_settle_unknown_call():
    book = MarginCallBook()
    assert book.settle_call("UNKNOWN") is None


def test_total_outstanding():
    book = MarginCallBook()
    book.record_call(_call(cid="MC001", init=100_000.0, var=200_000.0))
    book.record_call(_call(cid="MC002", init=50_000.0, var=100_000.0))
    book.settle_call("MC001")
    assert abs(book.total_outstanding_gbp() - 150_000.0) < 0.01


def test_headroom():
    book = MarginCallBook(credit_facility_gbp=5_000_000.0)
    book.record_call(_call(init=200_000.0, var=300_000.0))
    assert abs(book.headroom_gbp() - 4_500_000.0) < 0.01


def test_is_liquidity_stressed():
    book = MarginCallBook(credit_facility_gbp=1_000_000.0)
    book.record_call(_call(init=400_000.0, var=500_000.0))
    assert book.is_liquidity_stressed() is True


def test_margin_call_summary_keys():
    book = MarginCallBook()
    book.record_call(_call())
    s = book.margin_call_summary()
    for k in ("total_calls", "outstanding_calls", "total_outstanding_gbp",
               "credit_facility_gbp", "headroom_gbp", "is_liquidity_stressed", "stress_events"):
        assert k in s


def test_stress_events():
    book = MarginCallBook()
    book.record_call(_call(cid="MC001", var=1_000_000.0))
    book.record_call(_call(cid="MC002", var=100_000.0))
    assert len(book.stress_events()) == 1


# --- Phase LK depth tests ---

def test_call_id_stored():
    c = _call(cid="MC_LK_001")
    assert c.call_id == "MC_LK_001"


def test_call_date_stored():
    c = _call(date="2022-10-01")
    assert c.call_date == "2022-10-01"


def test_counterparty_stored():
    c = _call(cpty="DEUTSCHE")
    assert c.counterparty == "DEUTSCHE"


def test_contract_id_stored():
    c = _call(contract="FWD_LK_001")
    assert c.contract_id == "FWD_LK_001"


def test_initial_margin_stored():
    c = _call(init=250_000.0)
    assert c.initial_margin_gbp == pytest.approx(250_000.0)


def test_variation_margin_stored():
    c = _call(var=600_000.0)
    assert c.variation_margin_gbp == pytest.approx(600_000.0)


def test_settlement_deadline_stored():
    c = _call(deadline="2022-09-17")
    assert c.settlement_deadline == "2022-09-17"


def test_status_default_received():
    c = _call()
    assert c.status == MarginCallStatus.RECEIVED


def test_calls_for_date():
    book = MarginCallBook()
    book.record_call(_call(cid="MC001", date="2022-09-15"))
    book.record_call(_call(cid="MC002", date="2022-09-16"))
    calls = book.calls_for_date("2022-09-15")
    assert len(calls) == 1
    assert calls[0].call_id == "MC001"


def test_record_call_returns_call():
    book = MarginCallBook()
    c = _call()
    result = book.record_call(c)
    assert result is c


# --- VALUE_CHAIN observation feed: build_margin_calls_from_mtm (2026-07-24) ---
# R15 both-ways: the feed is proven against the REAL producer
# (TradingBook.exposure_by_counterparty), not a hand-built dict, so it is tied to the live
# stream the run loop consumes. Each control asserts the feed is LOAD-BEARING (variation
# margin ACTUALLY moves off the netted MtM) and that the liquidity controls CAN FIRE.

def _otm_contract(customer_id, cp_id, agreed, notional, cp_type, rating):
    """A bilateral contract; at a lower spot it nets OUT-of-the-money (company owes margin)."""
    return ForwardContract(
        customer_id=customer_id, term_start="2022-01-01", term_end="2022-12-31",
        notional_mwh=notional, agreed_price_gbp_per_mwh=agreed, hedge_fraction=1.0,
        bid_ask_cost_gbp=0.0, counterparty_id=cp_id, counterparty_type=cp_type,
        clearing_status=ClearingStatus.BILATERAL_ISDA, counterparty_rating=rating,
    )


def _feed(book_contracts, prices, **kw):
    book = TradingBook()
    for c in book_contracts:
        book.open_hedge(c)
    exposure = book.exposure_by_counterparty(prices)
    return build_margin_calls_from_mtm(
        exposure, as_of_date="2022-06-30", settlement_deadline="2022-07-01", **kw
    )


def test_margin_feed_derives_variation_margin_from_otm():
    """LOAD-BEARING: an OTM netted position (agreed £90, spot £40, 1000 MWh -> netted -£50k)
    posts variation margin = £50k. A feed that zeroed VM would leave outstanding at 0."""
    mc = _feed(
        [_otm_contract("C1", "TRADER-1", 90.0, 1000.0,
                       CounterpartyType.ENERGY_TRADER, CounterpartyCreditRating.A)],
        {"C1": 40.0},
    )
    assert mc.margin_call_summary()["total_calls"] == 1
    assert abs(mc.total_outstanding_gbp() - 50_000.0) < 0.01


def test_margin_feed_in_the_money_posts_no_margin():
    """Fail-open guard: an ITM netted position (company is OWED, not owing) must NOT create a
    margin call — that credit side belongs to the credit register, not this liquidity book."""
    mc = _feed(
        [_otm_contract("C1", "BANK-1", 40.0, 1000.0,
                       CounterpartyType.MAJOR_BANK, CounterpartyCreditRating.AA)],
        {"C1": 100.0},  # spot > agreed -> ITM -> netted +£60k
    )
    assert mc.margin_call_summary()["total_calls"] == 0
    assert mc.total_outstanding_gbp() == 0.0


def test_margin_feed_stress_controls_can_fire():
    """R15: a large adverse mark (agreed £90, spot £40, 20_000 MWh -> netted -£1.0M -> VM £1.0M)
    MUST make is_stress_event / is_liquidity_stressed fire. A book that can never stress is
    fail-open — this proves it can."""
    mc = _feed(
        [_otm_contract("C1", "TRADER-1", 90.0, 20_000.0,
                       CounterpartyType.ENERGY_TRADER, CounterpartyCreditRating.A)],
        {"C1": 40.0},
        credit_facility_gbp=1_000_000.0,
    )
    s = mc.margin_call_summary()
    assert s["stress_events"] == 1               # VM £1.0M > £500k stress threshold
    assert s["is_liquidity_stressed"] is True    # £1.0M outstanding > 0.8 × £1.0M facility


def test_margin_feed_idempotent_on_replay():
    """C-S1: re-feeding the SAME snapshot into the SAME book adds no duplicate call."""
    contracts = [_otm_contract("C1", "TRADER-1", 90.0, 1000.0,
                               CounterpartyType.ENERGY_TRADER, CounterpartyCreditRating.A)]
    book = TradingBook()
    for c in contracts:
        book.open_hedge(c)
    exposure = book.exposure_by_counterparty({"C1": 40.0})
    mc = build_margin_calls_from_mtm(exposure, as_of_date="2022-06-30",
                                     settlement_deadline="2022-07-01")
    # Feed the identical snapshot a second time into the same book.
    build_margin_calls_from_mtm(exposure, as_of_date="2022-06-30",
                               settlement_deadline="2022-07-01", book=mc)
    assert mc.margin_call_summary()["total_calls"] == 1


def test_margin_feed_deterministic_replay():
    """C-S2: two fresh feeds of the same snapshot produce identical call content."""
    contracts = [_otm_contract("C1", "TRADER-1", 90.0, 1000.0,
                               CounterpartyType.ENERGY_TRADER, CounterpartyCreditRating.A)]
    book = TradingBook()
    for c in contracts:
        book.open_hedge(c)
    exposure = book.exposure_by_counterparty({"C1": 40.0})
    a = build_margin_calls_from_mtm(exposure, as_of_date="2022-06-30", settlement_deadline="2022-07-01")
    b = build_margin_calls_from_mtm(exposure, as_of_date="2022-06-30", settlement_deadline="2022-07-01")
    assert a.margin_call_summary() == b.margin_call_summary()


def test_margin_feed_skips_unattributed():
    """A contract with no counterparty forms no phantom margin call (wall/data-quality)."""
    mc = _feed(
        [ForwardContract(customer_id="C1", term_start="2022-01-01", term_end="2022-12-31",
                         notional_mwh=1000.0, agreed_price_gbp_per_mwh=90.0, hedge_fraction=1.0)],
        {"C1": 40.0},  # OTM but UNATTRIBUTED
    )
    assert mc.margin_call_summary()["total_calls"] == 0


# --- MC-2 §3: book-scaled committed facility (2026-07-25) ---
# R15 both-ways: the facility must SCALE WITH THE BOOK (the property the director demanded) and the
# fixed-£5m defect must be gone. Each control is written so that reverting the mechanism to a
# constant facility (the named defect) makes it FAIL — a control that cannot fail is worthless.

def test_facility_scales_with_book_MUTATION_KILLER():
    """R15 KILLER: doubling the book's gross marked exposure STRICTLY increases the derived
    facility. Reverting book_scaled_credit_facility_gbp to a constant (the fixed-£5m defect) makes
    this assertion FAIL — this is the mutation test proving the control fires on its own defect."""
    small = {"CP1": {"netted_mtm_gbp": -1_000_000.0}}
    big = {"CP1": {"netted_mtm_gbp": -2_000_000.0}}
    f_small = book_scaled_credit_facility_gbp(small)
    f_big = book_scaled_credit_facility_gbp(big)
    assert f_big > f_small                       # scales with the book — a constant facility fails here
    assert f_big == pytest.approx(2 * f_small)   # linear in gross exposure


def test_facility_is_not_the_fixed_5m_defect():
    """The activated small book must NOT get a £5m facility — that was the named defect (an
    orders-of-magnitude-too-large facility nothing can kill). A £1m gross book gets £1.5m, not £5m."""
    f = book_scaled_credit_facility_gbp({"CP1": {"netted_mtm_gbp": -1_000_000.0}})
    assert f == pytest.approx(FACILITY_COVERAGE_MULTIPLE * 1_000_000.0)
    assert f != 5_000_000.0
    assert f < 5_000_000.0


def test_facility_gross_is_two_way_magnitude():
    """The book-size signal is the GROSS two-way magnitude of the netted mark: an ITM name (+) and
    an OTM name (-) both add exposure the facility must relate to — they do not net to zero."""
    f = book_scaled_credit_facility_gbp({
        "CP1": {"netted_mtm_gbp": -1_000_000.0},   # company owes
        "CP2": {"netted_mtm_gbp": +1_000_000.0},   # company owed
    })
    assert f == pytest.approx(FACILITY_COVERAGE_MULTIPLE * 2_000_000.0)


def test_facility_floor_never_zero():
    """Fail-safe (R12 the OTHER way): an empty/flat book is NOT instantly dead — the facility floors
    at FACILITY_MIN_GBP, never zero. A zero facility would force death, the same breach as forcing
    survival."""
    assert book_scaled_credit_facility_gbp({}) == pytest.approx(FACILITY_MIN_GBP)
    assert book_scaled_credit_facility_gbp({"CP1": {"netted_mtm_gbp": 0.0}}) == pytest.approx(FACILITY_MIN_GBP)
    assert FACILITY_MIN_GBP > 0.0


def test_facility_min_cannot_make_stressed_book_unbreakable():
    """The floor must stay modest — well below a plausible stress call — so it cannot by itself make
    a stressed book unbreakable (that would re-introduce the theatre the ruling removes)."""
    assert FACILITY_MIN_GBP <= 500_000.0   # a single stress event (>£500k VM) can exceed the bare floor


def test_facility_ignores_unattributed_in_sizing():
    """UNATTRIBUTED marks are a data-quality bucket, not a real counterparty position — they do not
    inflate the committed facility."""
    f = book_scaled_credit_facility_gbp({
        "CP1": {"netted_mtm_gbp": -1_000_000.0},
        "UNATTRIBUTED": {"netted_mtm_gbp": -9_000_000.0},
    })
    assert f == pytest.approx(FACILITY_COVERAGE_MULTIPLE * 1_000_000.0)


def test_builder_derives_book_scaled_facility_by_default():
    """LOAD-BEARING wiring: with no explicit facility the live builder path derives a book-scaled
    facility (not £5m). The OTM £50k book (agreed £90, spot £40, 1000 MWh) gets a facility scaled to
    its own £50k gross mark, floored at the minimum — proving the fixed-£5m default is gone live."""
    mc = _feed(
        [_otm_contract("C1", "TRADER-1", 90.0, 1000.0,
                       CounterpartyType.ENERGY_TRADER, CounterpartyCreditRating.A)],
        {"C1": 40.0},
    )
    # gross mark = £50k -> 1.5 × 50k = £75k < floor -> floored at FACILITY_MIN_GBP
    assert mc.credit_facility_gbp == pytest.approx(FACILITY_MIN_GBP)
    assert mc.credit_facility_gbp != 5_000_000.0


def test_builder_facility_scales_up_on_larger_book():
    """A larger book yields a larger derived facility above the floor: agreed £90, spot £40,
    20_000 MWh -> gross mark £1.0M -> facility 1.5 × £1.0M = £1.5M."""
    mc = _feed(
        [_otm_contract("C1", "TRADER-1", 90.0, 20_000.0,
                       CounterpartyType.ENERGY_TRADER, CounterpartyCreditRating.A)],
        {"C1": 40.0},
    )
    assert mc.credit_facility_gbp == pytest.approx(1_500_000.0)


def test_builder_explicit_facility_still_honoured():
    """A caller pinning an explicit facility (unit test / sweep origination) still overrides the
    book-derived default — the override path is preserved."""
    mc = _feed(
        [_otm_contract("C1", "TRADER-1", 90.0, 20_000.0,
                       CounterpartyType.ENERGY_TRADER, CounterpartyCreditRating.A)],
        {"C1": 40.0},
        credit_facility_gbp=3_000_000.0,
    )
    assert mc.credit_facility_gbp == pytest.approx(3_000_000.0)
