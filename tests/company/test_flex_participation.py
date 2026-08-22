"""W1_9 COMPANY-side flex-participation tests. The company copes THROUGH THE
WALL: it forms its belief from OBSERVED price + its OWN settlement history only,
never a SIM internal. Covers the L1 price-proxy belief, the L2 learned delivery
de-rating + baseline estimate, and the epistemic-wall no-sim-import guard.
"""
from __future__ import annotations

import datetime as _dt

import numpy as np
import pytest

from company.interfaces.crossing_conversation import UnaskedLeg
from company.interfaces.wall_protocol import WallProtocolError
from company.market.flex_participation import (
    DEFAULT_PRICE_SCARCITY_PERCENTILE,
    VENUE_OPERATORS,
    CompanyVenueOffer,
    FlexEnrolmentBook,
    FlexEnrolmentRefused,
    MisroutedOutcome,
    WrongVenueOperator,
    encode_enrolment_payload,
    form_participation_belief,
    form_participation_belief_l2,
    learn_delivery_ratio,
    realised_revenue_from_settlement,
)
from interface.contracts.flex_observable_seam import (
    ENROLMENT_REFUSAL_CODES,
    REQUEST_PAYLOAD_FIELDS,
    FlexDirection,
    FlexEnrolment,
    FlexVenue,
)
from sim.flex_dispatch import (
    NETWORK_OPERATOR_CREDENTIAL,
    NETWORK_OPERATOR_ID,
    SYSTEM_OPERATOR_ID,
    VenueRegistrations,
    answer_enrolment,
)


def _prices(n=200, seed=0):
    rng = np.random.default_rng(seed)
    return 40 + rng.normal(0, 10, n)


def test_l1_belief_predicts_top_price_percentile():
    price = _prices()
    b = form_participation_belief(price, enrolled_mw=1.0, period_hours=1.0)
    # dispatch predicted only in the top-percentile price periods
    thr = np.percentile(price, DEFAULT_PRICE_SCARCITY_PERCENTILE)
    assert np.array_equal(b.predicted_dispatch_mask, price >= thr)
    assert b.total_expected_revenue_gbp > 0.0


def test_l1_empty_price_fails_loud():
    with pytest.raises(ValueError):
        form_participation_belief([], enrolled_mw=1.0, period_hours=1.0)


def test_learn_delivery_ratio_from_own_settlement():
    # instructed 2 MWh/event; observed metered mean 1.4 -> learned ratio 0.7
    ratio = learn_delivery_ratio([1.4, 1.4, 1.4], instructed_mwh=2.0)
    assert ratio == pytest.approx(0.7)
    # cold start (no history) falls back to the L1 perfect-delivery assumption
    assert learn_delivery_ratio(None, instructed_mwh=2.0) == 1.0
    assert learn_delivery_ratio([], instructed_mwh=2.0) == 1.0
    # FAIL-CLOSED on a degenerate enrolment
    with pytest.raises(ValueError):
        learn_delivery_ratio([1.0], instructed_mwh=0.0)


def test_l2_belief_de_rates_expected_revenue_below_l1():
    """The L2 company, having learned its portfolio under-delivers, forecasts
    LESS utilisation revenue than the L1 perfect-delivery belief."""
    price = _prices()
    l1 = form_participation_belief(price, enrolled_mw=2.0, period_hours=1.0)
    # observed history: 70% delivery against the 2 MWh instructed volume
    l2 = form_participation_belief_l2(
        price, enrolled_mw=2.0, period_hours=1.0,
        observed_delivery_mwh=[1.4] * 10)
    assert l2.learned_delivery_ratio == pytest.approx(0.7)
    assert l2.total_expected_revenue_gbp == pytest.approx(0.7 * l1.total_expected_revenue_gbp)
    # same dispatch SET as L1 (only the volume de-rates, not the trigger)
    assert np.array_equal(l1.predicted_dispatch_mask, l2.predicted_dispatch_mask)


def test_l2_baseline_estimate_carries_the_bias():
    price = _prices()
    unbiased = form_participation_belief_l2(price, enrolled_mw=2.0, period_hours=1.0)
    assert unbiased.estimated_baseline_mwh == pytest.approx(2.0)
    biased = form_participation_belief_l2(
        price, enrolled_mw=2.0, period_hours=1.0, baseline_bias=0.15)
    assert biased.estimated_baseline_mwh == pytest.approx(2.0 * 1.15)


def test_realised_revenue_tolerant_of_empty_feed():
    assert realised_revenue_from_settlement(None) == 0.0
    assert realised_revenue_from_settlement([]) == 0.0


def test_no_sim_import():
    """Epistemic wall: the company module must not import any SIM/simulation
    internal (it reads observables only)."""
    import company.market.flex_participation as mod

    src = open(mod.__file__).read()
    assert "import sim" not in src and "from sim" not in src
    assert "import simulation" not in src and "from simulation" not in src


# ===========================================================================
# EP6 pass 53 -- THE ENROLMENT EXCHANGE, COMPANY SIDE.
#
# The request leg (pass 52) landed 675 lines of production code across both
# sides of the wall with NO test of any kind. These are its controls. The
# round trip is driven end to end -- company encodes, the VENUE's own
# independent codec answers, the company reads the answer -- because a
# company-side test that stubbed the venue's reply would be asserting that
# this module agrees with a fixture I wrote, which is the R15 TAUTOLOGY for
# the one question a seam is asked.
# ===========================================================================

_W_START = _dt.datetime(2026, 3, 1, 16, 0)
_W_END = _dt.datetime(2026, 3, 1, 19, 0)
_ASOF = _dt.datetime(2026, 2, 20, 9, 0)
#: The venue reads the request well before the window closes, so a refusal in
#: any test below is about the thing that test names and never about the clock.
_VENUE_CLOCK = _dt.datetime(2026, 2, 20, 10, 0)


def _offer(mw=5.0, venue="dfs_turn_down"):
    return CompanyVenueOffer(venue=venue, offered_mw=mw, priority=1)


def _submit(book, *, unit_id="UNIT-A", start=_W_START, end=_W_END, mw=5.0):
    return book.submit(
        _offer(mw=mw),
        unit_id=unit_id,
        window_start=start,
        window_end=end,
        as_of=_ASOF,
    )


def test_the_full_enrolment_ROUND_TRIP_crosses_the_wall_and_comes_back_registered():
    """THE SUCCESS CASE, and it is the null control every refusal below needs:
    if this did not pass, a test asserting a refusal would prove only that the
    exchange never works."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()

    wire = _submit(book)
    answer = answer_enrolment(wire, venue_clock=_VENUE_CLOCK, registrations=venue)
    outcome = book.observe_outcome(answer)

    assert outcome.unit_id == "UNIT-A"
    assert outcome.venue is FlexVenue.DFS_TURN_DOWN
    # The reference is the VENUE's, minted from its own sequence -- the one
    # thing in this payload the company could not have assumed.
    assert outcome.enrolment_reference == "DFS_TURN_DOWN-REG-000001"
    assert book.registered_references() == ("DFS_TURN_DOWN-REG-000001",)


def test_the_conversation_is_OPEN_between_the_ask_and_the_answer_and_closed_after():
    """`awaiting_answer` is the thing a response-driven company cannot produce:
    it would learn the crossing existed only from the message that ended it."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()

    assert book.awaiting_answer() == ()
    wire = _submit(book)
    assert len(book.awaiting_answer()) == 1  # the ask is on the books before any reply

    book.observe_outcome(answer_enrolment(wire, venue_clock=_VENUE_CLOCK, registrations=venue))
    assert book.awaiting_answer() == ()


def test_MUTATION_an_outcome_on_a_correlation_id_this_company_NEVER_SUBMITTED_is_refused():
    """The REGISTER is the evidence that we asked; the message never is, or any
    process able to mint a plausible id is registered with us.

    The mutation is the forged id and nothing else: the SAME venue, the SAME
    bytes-shape, answered against a book that did not submit it."""
    submitter, bystander = FlexEnrolmentBook(), FlexEnrolmentBook()
    venue = VenueRegistrations()

    answer = answer_enrolment(
        _submit(submitter), venue_clock=_VENUE_CLOCK, registrations=venue
    )

    with pytest.raises(UnaskedLeg):
        bystander.observe_outcome(answer)

    # NULL CONTROL: the identical answer is ACCEPTED by the book that really
    # asked -- so the refusal is keyed on the register and not on the message.
    assert submitter.observe_outcome(answer).unit_id == "UNIT-A"


def test_a_MISROUTED_acceptance_is_refused_against_our_own_submission_not_the_message():
    """The echoed unit/venue are what a mis-routed registration gets wrong, so
    believing them is believing the thing under suspicion."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()
    wire = _submit(book, unit_id="UNIT-A")
    answer = answer_enrolment(wire, venue_clock=_VENUE_CLOCK, registrations=venue)

    # The venue answers our correlation id describing somebody else's unit.
    # Mutated INSIDE `fields`: putting a stray top-level key on the payload
    # would be caught by the key-set belt one layer earlier, and this test
    # would then pass without the refusal it names ever firing.
    #
    # And mutated INSIDE THE FRAME, leaving the sender and its credential
    # untouched: the point of this test is the belt that reads our own
    # submission book, so the transport identity must still be valid or the
    # frame would refuse first and this refusal would never fire.
    answer["envelope"]["payload"]["fields"]["unit_id"] = "UNIT-ELSEWHERE"

    with pytest.raises(MisroutedOutcome):
        book.observe_outcome(answer)
    # ...and it never reached the reference book.
    assert book.registered_references() == ()


def test_a_REFUSED_registration_RAISES_and_can_never_read_as_a_quiet_absence_of_flex():
    """A company that read its own rejected registration as "no flex this
    window" would go on forecasting revenue from a venue with no record of it.

    Asserted by REASON CODE, not a bare `raises`: two refusals on this leg call
    for different repairs, and a bare raises cannot tell them apart."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()
    # A window that ended before the venue ever read the request.
    wire = _submit(book, start=_dt.datetime(2026, 1, 1, 1), end=_dt.datetime(2026, 1, 1, 2))
    answer = answer_enrolment(wire, venue_clock=_VENUE_CLOCK, registrations=venue)

    with pytest.raises(FlexEnrolmentRefused) as exc:
        book.observe_outcome(answer)
    assert exc.value.code == "WINDOW_ALREADY_CLOSED"
    assert exc.value.code in ENROLMENT_REFUSAL_CODES
    assert book.registered_references() == ()


def test_MUTATION_a_field_added_to_the_payload_cannot_cross_UNDECLARED():
    """The published declaration is load-bearing: the encoder measures its own
    wire form against the CONTRACT's key set, so a field added on one side and
    not published is refused rather than silently crossing.

    Mutating the DECLARATION (not the encoder) is what proves the encoder reads
    it -- if it did not, widening the contract would change nothing."""
    enrolment = FlexEnrolment(
        unit_id="UNIT-A",
        venue=FlexVenue.DFS_TURN_DOWN,
        offered_mw=5.0,
        direction=FlexDirection.TURN_DOWN,
        window_start=_W_START,
        window_end=_W_END,
    )
    # NULL CONTROL: it encodes cleanly against the real declaration.
    assert set(encode_enrolment_payload(enrolment)) == set(
        REQUEST_PAYLOAD_FIELDS["FlexEnrolment"]
    )

    original = REQUEST_PAYLOAD_FIELDS["FlexEnrolment"]
    REQUEST_PAYLOAD_FIELDS["FlexEnrolment"] = original + ("settlement_priority",)
    try:
        with pytest.raises(WallProtocolError) as exc:
            encode_enrolment_payload(enrolment)
        assert exc.value.reason == "CONTRACT_VIOLATION"
    finally:
        REQUEST_PAYLOAD_FIELDS["FlexEnrolment"] = original


def test_the_company_cannot_submit_into_a_venue_the_seam_publishes_no_market_for():
    """Its own book naming a venue nobody runs a market for is refused at the
    seam rather than crossing as a string the venue would have to guess at."""
    book = FlexEnrolmentBook()
    with pytest.raises(WallProtocolError) as exc:
        book.submit(
            _offer(venue="a_venue_that_does_not_exist"),
            unit_id="UNIT-A",
            window_start=_W_START,
            window_end=_W_END,
            as_of=_ASOF,
        )
    assert exc.value.reason == "CONTRACT_VIOLATION"


# ===========================================================================
# EP6 pass 54 -- ONE MINTING SITE, TWO DOORS.
#
# `submit_enrolment` exists because the SIM/company seam's `enrol_flex` is
# handed a `FlexEnrolment` the caller already assembled, while `submit` is
# handed an offer. The failure being controlled for is not hypothetical: the
# seam HAD its own minting site with its own grammar (`flex-{unit}-{date}`,
# no venue in the key), so one unit's enrolments into two venues over one day
# collided on a single correlation id.
# ===========================================================================


def test_both_doors_into_the_book_mint_the_SAME_correlation_id():
    """The offer-shaped door and the enrolment-shaped door are one exchange. If
    they can disagree about the id, the register cannot answer 'did I ask for
    this?' for whichever door the answer comes back to."""
    via_offer = _submit(FlexEnrolmentBook())
    via_enrolment = FlexEnrolmentBook().submit_enrolment(
        FlexEnrolment(
            unit_id="UNIT-A",
            venue=FlexVenue.DFS_TURN_DOWN,
            offered_mw=5.0,
            direction=FlexDirection.TURN_DOWN,
            window_start=_W_START,
            window_end=_W_END,
        ),
        as_of=_ASOF,
    )
    assert via_offer["correlation_id"] == via_enrolment["correlation_id"]
    assert via_offer == via_enrolment  # the whole wire, not just the key


def test_MUTATION_one_unit_in_TWO_VENUES_on_one_day_is_TWO_conversations():
    """The defect the seam's own grammar had. Both enrolments are legitimate --
    a unit registered into several DIFFERENT venues over one window is the
    multi-venue book `dispatch_and_settle_stacked` models -- so an id that keys
    only on unit+date makes the venue's second answer arrive on the first
    submission's id, and `observe_outcome` would check it against the wrong
    offer."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()

    dfs = _submit(book)
    bm = book.submit_enrolment(
        FlexEnrolment(
            unit_id="UNIT-A",
            venue=FlexVenue.BALANCING_MECHANISM,
            offered_mw=5.0,
            direction=FlexDirection.TURN_DOWN,
            window_start=_W_START,
            window_end=_W_END,
        ),
        as_of=_ASOF,
    )

    assert dfs["correlation_id"] != bm["correlation_id"]
    assert len(book.awaiting_answer()) == 2

    book.observe_outcome(answer_enrolment(dfs, venue_clock=_VENUE_CLOCK, registrations=venue))
    book.observe_outcome(answer_enrolment(bm, venue_clock=_VENUE_CLOCK, registrations=venue))
    # Two references, one per venue -- and neither answer was read against the
    # other's submission (a `MisroutedOutcome` would have been raised above).
    # The SEQUENCE is the desk's own and runs across both market functions, so
    # the numbers are 1 and 2: what the company may assert is that it holds two
    # distinct references, never what the venue's counter says next.
    assert set(book.registered_references()) == {
        "DFS_TURN_DOWN-REG-000001", "BALANCING_MECHANISM-REG-000002",
    }


# ---------------------------------------------------------------------------
# WHO IS SPEAKING (EP6 pass 61, Q13) -- the flex response leg's transport frame.
#
# Before this, the ONLY thing standing between this company and a registration
# reference minted by anything at all was that the impostor echo the right
# unit and venue back at us: `MisroutedOutcome` reads both fields out of the
# message it is checking. Every test below moves that evidence off the message
# and onto a credential the sender has to hold.
# ---------------------------------------------------------------------------


def test_the_ANSWER_is_authenticated_before_any_of_it_is_believed():
    """NULL CONTROL for every refusal below: the honest exchange, framed by the
    operator this company expects, still registers."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()
    answer = answer_enrolment(_submit(book), venue_clock=_VENUE_CLOCK, registrations=venue)

    assert answer["sender"] == SYSTEM_OPERATOR_ID
    assert book.observe_outcome(answer).enrolment_reference == "DFS_TURN_DOWN-REG-000001"


def test_an_UNREGISTERED_sender_is_refused_however_well_formed_its_ANSWER_is():
    """The forgery `MisroutedOutcome` could never see. The envelope inside is
    the venue's own, byte for byte -- the correct correlation id, our unit, our
    venue -- and it is refused because the participant around it is one this
    build holds no record of.

    Asserted by REASON, not a bare `raises`: this leg now carries four belts
    and a bare raises cannot say which one fired."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()
    answer = answer_enrolment(_submit(book), venue_clock=_VENUE_CLOCK, registrations=venue)
    answer["sender"] = "SOMEBODY-ELSE-01"

    with pytest.raises(WallProtocolError) as exc:
        book.observe_outcome(answer)
    assert exc.value.reason == "UNKNOWN_SENDER"
    assert book.registered_references() == ()


def test_a_KNOWN_participant_that_cannot_PRESENT_its_credential_is_refused():
    """Knowing a participant's NAME is public; holding its key is not. Without
    this, the frame would be a label anyone could copy off a previous message."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()
    answer = answer_enrolment(_submit(book), venue_clock=_VENUE_CLOCK, registrations=venue)
    answer["credential"] = "system-operator-01::participant-credential::v2"

    with pytest.raises(WallProtocolError) as exc:
        book.observe_outcome(answer)
    assert exc.value.reason == "BAD_CREDENTIAL"


def test_a_REGISTERED_participant_may_not_speak_for_a_venue_it_does_not_OPERATE():
    """THE SECOND QUESTION, and the reason this seam has two counterparties.

    The network operator is a participant this build IS registered with and its
    credential is genuine, so the transport frame accepts it. It still may not
    answer a DFS registration, because it does not run that market -- identity
    proved is not authorisation granted.

    This is the case a single-counterparty registry could not express: with one
    flex participant, a check of the operator would pass for the same reason a
    check of nothing would."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()
    answer = answer_enrolment(_submit(book), venue_clock=_VENUE_CLOCK, registrations=venue)

    # A real participant, its real credential -- and the wrong market function.
    answer["sender"] = NETWORK_OPERATOR_ID
    answer["credential"] = NETWORK_OPERATOR_CREDENTIAL

    with pytest.raises(WrongVenueOperator):
        book.observe_outcome(answer)
    assert book.registered_references() == ()


def test_the_expected_operator_is_read_off_OUR_SUBMISSION_and_not_off_the_ANSWER():
    """THE R15 INDEPENDENCE CHECK for this belt. An implementation that took the
    venue from the message's own payload would agree with any impostor that
    named the venue it was signing for -- the tautology the frame exists to
    remove. So: keep the honest payload (it still says `dfs_turn_down`) and
    move only the SIGNER to the participant that operates a DIFFERENT venue.
    A check reading the payload would accept this; one reading our submission
    book refuses it, and the test above is what makes that distinguishable."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()
    answer = answer_enrolment(_submit(book), venue_clock=_VENUE_CLOCK, registrations=venue)
    assert answer["envelope"]["payload"]["fields"]["venue"] == "dfs_turn_down"

    answer["sender"] = NETWORK_OPERATOR_ID
    answer["credential"] = NETWORK_OPERATOR_CREDENTIAL

    with pytest.raises(WrongVenueOperator):
        book.observe_outcome(answer)


def test_MUTATION_the_expected_operator_table_has_NO_DEFAULT_for_an_unknown_venue(
    monkeypatch,
):
    """The fail-open reading is "we hold no operator for this venue, so accept
    whoever replied", and it is how a registry with a fallback stops being able
    to say no. Emptying the company's table must make the honest exchange
    REFUSE, not sail through.

    NULL CONTROL is the test above: against the real table the same bytes are
    accepted, so this is the lookup failing closed and not the seam being
    always-red."""
    book, venue = FlexEnrolmentBook(), VenueRegistrations()
    answer = answer_enrolment(_submit(book), venue_clock=_VENUE_CLOCK, registrations=venue)

    monkeypatch.setattr(
        "company.market.flex_participation.VENUE_OPERATORS", {}
    )
    with pytest.raises(WrongVenueOperator):
        book.observe_outcome(answer)


def test_the_companys_operator_table_is_its_OWN_and_agrees_with_the_worlds_today():
    """The two tables are written independently -- the world's is the FACT of
    who runs each market function, the company's is its BELIEF about it -- and
    neither imports the other. A company that read the operator table off the
    world could not be wrong about it, and being able to be wrong is what makes
    the check a check.

    Asserted as AGREEMENT rather than identity: they agree today, and the
    mechanism that would let them disagree is intact. That the company does not
    READ the world's table is owned by `test_no_sim_import` above -- a source
    scan here would be a second copy of it, and one that this comment's own
    mention of the symbol would defeat."""
    from sim.flex_dispatch import FLEX_VENUE_OPERATORS

    assert dict(VENUE_OPERATORS) == dict(FLEX_VENUE_OPERATORS)
    assert VENUE_OPERATORS is not FLEX_VENUE_OPERATORS
    # Neither is total over the enum: `OTHER` is a venue nobody runs a market
    # for, and a default on either side is the fail-open shape both refuse.
    assert FlexVenue.OTHER not in VENUE_OPERATORS
    assert FlexVenue.OTHER not in FLEX_VENUE_OPERATORS


# ---------------------------------------------------------------------------
# EP6 pass 62, Q13's other half -- THE COMPANY CHECKS WHO IS SETTLING IT.
#
# Pass 61 framed the enrolment leg. These two feeds -- the dispatch instruction
# and the settlement statement -- stayed bare, so anything able to put bytes in
# front of `observe_response_wire` could tell this company it had been called
# and how much it had been paid. A registration wrongly believed is a business
# that does not exist; a settlement line wrongly believed goes into revenue.
# ---------------------------------------------------------------------------

_FEED_HANDED_OVER_AT = _dt.datetime(2024, 7, 1, 7, 0)


def _flex_record(n=200, seed=0):
    rng = np.random.default_rng(seed)
    residual = rng.normal(30000, 4000, n)
    price = 40 + 0.004 * (residual - 30000) + rng.normal(0, 15, n)
    dates = np.array([f"2024-{1 + i % 12:02d}-{1 + i % 28:02d}" for i in range(n)])
    return {"dates": dates, "residual_mw": residual, "derived_price": price}


def _settlement_feed(*, venue=FlexVenue.BALANCING_MECHANISM):
    """One venue's real settlement feed, off the world's own emitter.

    Built by the WORLD and not hand-written here, unlike the envelope fixtures
    in `tests/company/market/test_flex_participation.py`, and the two serve
    different purposes: those ask whether the two codecs agree without ever
    talking to each other, these ask what this company does with a message the
    world actually sent. Impostors below are made by MUTATING this feed, so the
    only thing separating an accepted message from a refused one is the change
    the test names.
    """
    from sim.flex_dispatch import dispatch_and_settle, emit_settlement_lines_over_wire

    truth = dispatch_and_settle(_flex_record())
    stamps = [_dt.datetime.strptime(str(d)[:10], "%Y-%m-%d") for d in truth.dates]
    called = [s for s, on in zip(stamps, truth.dispatch_mask) if on]
    book = VenueRegistrations()
    book.register(FlexEnrolment(
        unit_id="FLEX_UNIT_1",
        venue=venue,
        offered_mw=float(truth.enrolled_mw),
        direction=FlexDirection.TURN_DOWN,
        window_start=min(stamps),
        window_end=max(called) + _dt.timedelta(hours=truth.period_hours),
    ))
    return emit_settlement_lines_over_wire(
        truth, venue=venue, registrations=book,
        handed_over_at=_FEED_HANDED_OVER_AT)


def test_an_UNFRAMED_settlement_line_is_REFUSED_however_well_formed_it_is():
    """THE DEFECT, reproduced as the thing that no longer crosses.

    The bare envelope taken out of the frame is byte-for-byte the message this
    company accepted before this pass: same correlation id, same payload, same
    version. It is refused now because nothing in it says who sent it -- which
    is the whole difference between a feed and a claim.

    NULL CONTROL: the SAME message inside its frame is accepted, so what fires
    is the missing frame and not the message being malformed."""
    from company.market.flex_participation import observe_settlement_wire

    framed = _settlement_feed()
    assert len(framed) > 0
    bare = [m["envelope"] for m in framed]

    with pytest.raises(WallProtocolError):
        observe_settlement_wire(bare)

    assert observe_settlement_wire(framed)[0].unit_id == "FLEX_UNIT_1"


def test_an_UNREGISTERED_sender_cannot_tell_this_company_it_was_PAID():
    """Identity first: a participant with no registry row is refused before the
    statement is parsed at all, so the work an unknown sender wanted done is
    never done."""
    from company.market.flex_participation import observe_settlement_wire

    feed = _settlement_feed()
    feed[0]["sender"] = "A-PARTICIPANT-NOBODY-REGISTERED"

    with pytest.raises(WallProtocolError) as exc:
        observe_settlement_wire(feed)
    assert exc.value.reason == "UNKNOWN_SENDER"


def test_a_KNOWN_participant_that_cannot_PRESENT_its_credential_is_refused_on_the_FEED():
    """The registry names the sender; the credential is what the sender has to
    hold. Naming a real participant is not being one.

    Deliberately a SEPARATE node from the enrolment leg's test of the same rule
    rather than a shared one: the two legs reach `_verify_frame` through
    different call paths, and a single test proving the rule once would go on
    passing if either path stopped calling it."""
    from company.market.flex_participation import observe_settlement_wire

    feed = _settlement_feed()
    feed[0]["credential"] = "system-operator-01::participant-credential::v1-guessed"

    with pytest.raises(WallProtocolError) as exc:
        observe_settlement_wire(feed)
    assert exc.value.reason == "BAD_CREDENTIAL"


def test_a_REGISTERED_participant_may_not_SETTLE_a_venue_it_does_not_OPERATE():
    """Identity proved is not authorisation granted, on the money leg.

    The network operator holds a GENUINE credential and this build IS registered
    with it -- it runs the local constraint market. It does not run the
    balancing mechanism, so it may not send this company a BM settlement line,
    and a check that stopped at "the frame verified" would let it.

    NULL CONTROL: the untouched feed from the venue's real operator crosses."""
    from company.market.flex_participation import observe_settlement_wire

    feed = _settlement_feed(venue=FlexVenue.BALANCING_MECHANISM)
    assert observe_settlement_wire(feed)[0].venue is FlexVenue.BALANCING_MECHANISM

    feed[0]["sender"] = NETWORK_OPERATOR_ID
    feed[0]["credential"] = NETWORK_OPERATOR_CREDENTIAL
    with pytest.raises(WrongVenueOperator) as exc:
        observe_settlement_wire(feed)
    assert NETWORK_OPERATOR_ID in str(exc.value)


def test_the_INSTRUCTION_feed_is_checked_TOO_and_not_only_the_money_one():
    """Both feeds go through one reader, and this is what says so. A dispatch
    instruction the company wrongly believes is a delivery obligation it will
    be measured against -- the cheaper message to forge and the one a
    settlement-only check would wave through."""
    from company.market.flex_participation import observe_response_wire
    from interface.contracts.flex_observable_seam import FlexDispatchInstruction
    from sim.flex_dispatch import (
        dispatch_and_settle,
        emit_dispatch_instructions_over_wire,
    )

    truth = dispatch_and_settle(_flex_record())
    stamps = [_dt.datetime.strptime(str(d)[:10], "%Y-%m-%d") for d in truth.dates]
    called = [s for s, on in zip(stamps, truth.dispatch_mask) if on]
    book = VenueRegistrations()
    book.register(FlexEnrolment(
        unit_id="FLEX_UNIT_1", venue=FlexVenue.BALANCING_MECHANISM,
        offered_mw=float(truth.enrolled_mw), direction=FlexDirection.TURN_DOWN,
        window_start=min(stamps),
        window_end=max(called) + _dt.timedelta(hours=truth.period_hours)))
    feed = emit_dispatch_instructions_over_wire(
        truth, registrations=book, handed_over_at=_FEED_HANDED_OVER_AT)

    # NULL CONTROL first: the honest instruction crosses and is the right type.
    assert isinstance(
        observe_response_wire(feed[0], expect=FlexDispatchInstruction),
        FlexDispatchInstruction,
    )

    feed[0]["sender"] = NETWORK_OPERATOR_ID
    feed[0]["credential"] = NETWORK_OPERATOR_CREDENTIAL
    with pytest.raises(WrongVenueOperator):
        observe_response_wire(feed[0], expect=FlexDispatchInstruction)


def test_MUTATION_the_operator_table_has_NO_DEFAULT_on_the_FEED_leg(monkeypatch):
    """The fail-open reading -- "we hold no expected operator for this venue, so
    accept whoever sent it" -- restored as a one-line mutation.

    ITS OWN CONTROL, not a copy of the wrong-operator test above: there the
    refusal fires because two named participants differ, here it must fire
    because the company holds NOTHING to compare against. An implementation
    written `if expected is not None and sender != expected` passes every test
    above and this one reds.

    NULL CONTROL is every test above: against the real table these same bytes
    are accepted, so this is the lookup failing closed rather than the feed
    being always-red."""
    from company.market.flex_participation import observe_settlement_wire

    feed = _settlement_feed()
    monkeypatch.setattr("company.market.flex_participation.VENUE_OPERATORS", {})
    with pytest.raises(WrongVenueOperator):
        observe_settlement_wire(feed)
