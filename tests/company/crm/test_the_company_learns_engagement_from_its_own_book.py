"""PB7: the payment-method engagement factor is a PRIOR the company updates, not a coefficient.

THE DEFECT THESE CONTROLS EXIST FOR. PB6 gave the company a churn belief conditioned on payment
method, using Ofgem's published CIM w6 rates as the coefficient. A constant cannot be wrong, so
the belief-vs-truth gap this project scores itself on had nothing to bite on for that channel --
and `docs/design/COMPETITOR_FIELD_FRAME.md` §5 is explicit that "a defect is a gap that never
moves in response to new observations".

Every test below names the specific way that could be got wrong. Two of them cover the shapes
that have actually shipped here before: the absence of an observation channel read as an
observation of absence (`arm_loss_reporting`'s own history), and a belief informed by the outcome
it is predicting.
"""
from __future__ import annotations

import ast
import math
import statistics
from pathlib import Path

from company.crm.churn_desk import RenewalObservation, estimate_renewal_churn
from company.crm.competitive_pressure import (
    PRIOR_LOG_VARIANCE,
    CompetitivePressureLedger,
    log_space_update_weight,
    pressure_ledger_scope,
)
from company.crm.enriched_churn_estimate import (
    enriched_churn_estimate,
    payment_method_engagement_factor,
    payment_method_engagement_reading,
)

_METHOD = "prepayment"
_OTHER = "direct_debit"
_PRIOR = payment_method_engagement_factor(_METHOD)


def _book(
    *,
    channel_renewals: int,
    channel_losses: int,
    other_renewals: int,
    other_losses: int,
    year: int = 2018,
) -> CompetitivePressureLedger:
    """A closed book: renewals priced and departures realised, split by channel."""
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    for _ in range(channel_renewals):
        ledger.observe_renewal_decision(year, 0.05, payment_method=_METHOD)
    for _ in range(other_renewals):
        ledger.observe_renewal_decision(year, 0.05, payment_method=_OTHER)
    for _ in range(channel_losses):
        ledger.observe_competitive_loss(year, payment_method=_METHOD)
    for _ in range(other_losses):
        ledger.observe_competitive_loss(year, payment_method=_OTHER)
    return ledger


def test_the_belief_moves_with_the_books_own_leavers_and_moves_the_right_way():
    """DEFECT: a coefficient. The whole point of PB7 is that this number can now be wrong.

    Strictly increasing in realised losses on the channel, holding the book fixed -- the same
    monotonicity claim `log_space_update_weight` documents for the market-wide multiplier, and
    the property that would silently fail if the weight were ever computed at the realised rate
    instead of under the null.
    """
    factors = []
    for channel_losses in (0, 5, 10, 20, 40):
        ledger = _book(channel_renewals=200, channel_losses=channel_losses,
                       other_renewals=800, other_losses=40)
        with pressure_ledger_scope(ledger):
            factors.append(payment_method_engagement_reading(_METHOD, 2020).factor)

    assert factors == sorted(factors), factors
    assert factors[0] < factors[-1], "the belief did not move at all across a 0-to-40 loss sweep"
    # It must be able to cross its own prior in BOTH directions, or "updating" only ever means
    # "confirming Ofgem more or less strongly".
    assert factors[0] < _PRIOR < factors[-1], (factors, _PRIOR)


def test_the_learned_factor_reaches_the_churn_estimate_itself():
    """DEFECT: a belief that updates in a reading nobody consumes.

    `enriched_churn_estimate` must scale by the POSTERIOR. If it still called the published table
    the reading above could move freely and no decision would change.

    THE TWO BOOKS HAVE IDENTICAL BOOK-WIDE TOTALS and differ only in WHICH channel the eighty
    departures fell on. That is not tidiness: comparing against the no-ledger case instead would
    move the competitive-pressure multiplier at the same time, and this assertion passed under a
    mutation that reverted the call to the published table because that second, larger movement
    was carrying it. Two things changed, so nothing was attributable.
    """
    args = (200.0, 240.0, 3.0, 3100.0)
    kwargs = dict(renewal_year=2020, payment_method=_METHOD)

    with pressure_ledger_scope(_book(channel_renewals=400, channel_losses=80,
                                     other_renewals=1600, other_losses=0)):
        channel_shopped = enriched_churn_estimate(*args, **kwargs)
    with pressure_ledger_scope(_book(channel_renewals=400, channel_losses=0,
                                     other_renewals=1600, other_losses=80)):
        channel_stayed = enriched_churn_estimate(*args, **kwargs)

    assert channel_shopped > channel_stayed, (
        f"eighty departures all on prepayment ({channel_shopped}) and all on direct debit "
        f"({channel_stayed}) produced the same estimate, so the channel reached no decision"
    )
    # AND THE QUIET ARM IS NOT ZERO. Four hundred prepayment renewals and no departures among them
    # is a real and unremarkable observation; without the Jeffreys correction it is `log(0)`, the
    # ratio is 0, and the factor collapses to 0 -- the company would price those accounts as
    # incapable of leaving on four hundred renewals of evidence. Dropping the correction survived
    # the comparison above, because zero is still less than the other arm.
    assert channel_stayed > 0.0, "a channel nobody has left yet was priced as unable to leave"


def test_every_no_evidence_branch_returns_the_published_prior_and_all_of_them_are_reachable():
    """DEFECT: a refusal that cannot be taken, or one that fails open to something other than Ofgem.

    ONE CONTROL OVER THE WHOLE PARTITION rather than a test per branch: a `reading` that refused
    EVERYTHING would pass a per-branch test of what each refusal returns. So the reasons are
    collected and asserted to be four DISTINCT ones, which is what proves each branch was entered.
    """
    armed_book = _book(channel_renewals=200, channel_losses=10,
                       other_renewals=800, other_losses=40)
    unarmed = CompetitivePressureLedger()
    unarmed.arm_loss_reporting()
    for _ in range(200):
        unarmed.observe_renewal_decision(2018, 0.05, payment_method=_METHOD)
        unarmed.observe_competitive_loss(2018)          # book-wide only: no channel on the wire

    readings = {}
    readings["no run scope"] = payment_method_engagement_reading(_METHOD, 2020)
    with pressure_ledger_scope(armed_book):
        readings["no renewal year"] = payment_method_engagement_reading(_METHOD, None)
        readings["unrecognised channel"] = payment_method_engagement_reading("cheque", 2020)
    with pressure_ledger_scope(unarmed):
        readings["channel never on the wire"] = payment_method_engagement_reading(_METHOD, 2020)
    with pressure_ledger_scope(_book(channel_renewals=0, channel_losses=0,
                                     other_renewals=800, other_losses=40)):
        readings["no closed renewals on the channel"] = payment_method_engagement_reading(
            _METHOD, 2020)

    for name, reading in readings.items():
        assert reading.factor == reading.prior, f"{name} did not fail back to the prior"
        assert not reading.moved_from_prior, f"{name} claims it moved"
        assert reading.basis, f"{name} refused without naming a reason"
    assert len({r.basis for r in readings.values()}) == len(readings), (
        "two branches gave the same reason, so at least one of them was never entered: "
        + repr({n: r.basis for n, r in readings.items()})
    )
    assert readings["unrecognised channel"].prior == 1.0
    assert readings["no run scope"].prior == _PRIOR


def test_a_departure_booked_without_its_channel_cannot_arm_the_engagement_numerator():
    """DEFECT, and it has shipped here before: absence of an observation read as absence.

    The book-wide numerator is armed and filling. If that armed the per-channel numerator too, a
    run that books every loss WITHOUT a channel would read "no prepayment customer has ever left
    us" -- 200 renewals, zero losses -- and collapse the factor towards zero on evidence that does
    not exist. The flattering direction, which is how the same defect nearly survived in 2026-08.
    """
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    for _ in range(200):
        ledger.observe_renewal_decision(2018, 0.05, payment_method=_METHOD)
    for _ in range(60):
        ledger.observe_competitive_loss(2018)           # no payment_method argument

    assert ledger.losses_by_year[2018] == 60, "the book-wide wire is not live, so this proves nothing"
    assert not ledger.method_loss_reporting_armed
    with pressure_ledger_scope(ledger):
        reading = payment_method_engagement_reading(_METHOD, 2020)
    assert reading.factor == _PRIOR
    assert not reading.moved_from_prior

    # ...and one channel-bearing departure is all it takes to arm it, or the guard above is a wall.
    ledger.observe_competitive_loss(2018, payment_method=_METHOD)
    assert ledger.method_loss_reporting_armed
    with pressure_ledger_scope(ledger):
        assert payment_method_engagement_reading(_METHOD, 2020).moved_from_prior


def test_the_channels_own_year_is_not_evidence_for_the_price_it_is_setting():
    """DEFECT: an estimate informed by its own outcome. One variable moves -- the year.

    THE REST OF THE BOOK IS HELD IN A CLOSED YEAR IN BOTH ARMS, and that is what makes this bite.
    Moving the whole book into 2020 also empties the book-wide window, so `_closed_window`'s own
    `y < renewal_year` refuses first and the reading returns the prior whatever the CHANNEL window
    does -- a mutation flipping `_closed_method_window` to `y <= renewal_year` survived that
    version of this test entirely. A guard proved by a sibling guard proves nothing.
    """
    def book(channel_year: int) -> CompetitivePressureLedger:
        ledger = _book(channel_renewals=0, channel_losses=0,
                       other_renewals=800, other_losses=40, year=2019)
        for _ in range(200):
            ledger.observe_renewal_decision(channel_year, 0.05, payment_method=_METHOD)
        for _ in range(40):
            ledger.observe_competitive_loss(channel_year, payment_method=_METHOD)
        return ledger

    with pressure_ledger_scope(book(2020)):
        blind = payment_method_engagement_reading(_METHOD, 2020)
    with pressure_ledger_scope(book(2019)):
        informed = payment_method_engagement_reading(_METHOD, 2020)

    assert blind.book_decisions > 0 and informed.book_decisions > 0, (
        "the book-wide window is empty, so its own no-look-ahead guard is what answered and the "
        "channel window was never consulted"
    )
    assert blind.decisions == 0, (
        f"{blind.decisions} of the channel's open-year renewals reached the closed window"
    )
    assert blind.factor == _PRIOR and not blind.moved_from_prior, blind.basis
    assert informed.moved_from_prior and informed.factor != _PRIOR, informed.basis


def test_a_thin_channel_is_believed_less_than_a_thick_one_at_the_same_realised_ratio():
    """DEFECT: a factor that trusts twenty renewals as hard as four hundred.

    THE WEIGHTING IS ALSO THE BOUND -- there is no clamp on the ratio anywhere in this path, so if
    the sample size did not damp it a single freak channel-year would swing the belief outright.
    """
    thin = _book(channel_renewals=20, channel_losses=4, other_renewals=980, other_losses=49)
    thick = _book(channel_renewals=400, channel_losses=80, other_renewals=600, other_losses=30)

    with pressure_ledger_scope(thin):
        thin_reading = payment_method_engagement_reading(_METHOD, 2020)
    with pressure_ledger_scope(thick):
        thick_reading = payment_method_engagement_reading(_METHOD, 2020)

    # Same realised story (the channel leaves at ~4x the rest of the book), different sample size.
    assert thin_reading.ratio > 1.0 and thick_reading.ratio > 1.0
    assert thin_reading.weight < thick_reading.weight
    assert abs(math.log(thin_reading.factor / _PRIOR)) < abs(math.log(thick_reading.factor / _PRIOR))


def test_the_desk_books_the_channel_it_priced_with():
    """DEFECT: the factor applied to the estimate and the counter fed to the ledger disagreeing.

    `estimate_renewal_churn` is the company's single once-per-renewal belief site, so it is the
    only place the two can be kept in step. A passive roller is booked too -- its estimator never
    applies the factor, but it is still a renewal of an account paying this way, and the
    denominator is the book rather than the wiring.
    """
    with pressure_ledger_scope() as ledger:
        estimate_renewal_churn(RenewalObservation(
            old_rate_gbp_per_mwh=200.0, new_rate_gbp_per_mwh=240.0, tenure_years=3.0,
            annual_consumption_kwh=3100.0, renewal_year=2019,
            payment_method=_METHOD, active_renewal=True,
        ))
        estimate_renewal_churn(RenewalObservation(
            old_rate_gbp_per_mwh=200.0, new_rate_gbp_per_mwh=240.0, tenure_years=3.0,
            annual_consumption_kwh=3100.0, renewal_year=2019,
            payment_method=_METHOD, active_renewal=False,
        ))
        estimate_renewal_churn(RenewalObservation(
            old_rate_gbp_per_mwh=200.0, new_rate_gbp_per_mwh=240.0, tenure_years=3.0,
            annual_consumption_kwh=3100.0, renewal_year=2019,
        ))

    assert ledger.decisions_by_method[(_METHOD, 2019)] == 2, ledger.decisions_by_method
    assert ledger.decisions_by_year[2019] == 3, (
        "the unresolvable account was dropped from the book denominator, which biases the base "
        "rate towards whichever channel the CRM finds easiest to read"
    )

    # ...AND THE SAME FIELD REACHES THE ESTIMATE, not only the counter. Booking the channel while
    # pricing without it is the worse half of the two: the ledger would learn a factor that no
    # decision ever applied, and every published belief-vs-truth figure would be about a number
    # the company does not use.
    def priced(method: str | None) -> float:
        return estimate_renewal_churn(RenewalObservation(
            old_rate_gbp_per_mwh=200.0, new_rate_gbp_per_mwh=240.0, tenure_years=3.0,
            annual_consumption_kwh=3100.0, renewal_year=2019, payment_method=method,
        ))

    assert priced(_METHOD) < priced(None) , (
        "the desk priced a prepayment renewal identically to one with no channel on record"
    )


def test_the_engagement_channel_is_weighted_against_its_own_priors_dispersion():
    """DEFECT: the two beliefs sharing one rule and one PRIOR VARIANCE.

    `log_space_update_weight` takes the dispersion as a parameter precisely because there are two
    published series here -- DESNZ years for the market-wide multiplier, CIM banners for the
    channel -- and they differ by a factor of three (0.256 against 0.080). Passing the wrong one
    changes every weight this channel produces and no ordering assertion in this file can see it,
    because the orderings hold under either.

    Re-derived through the PUBLIC prior function rather than read off the private constant, so a
    scaled or hand-edited copy of the dispersion is what fails here.
    """
    published = [payment_method_engagement_factor(m)
                 for m in ("direct_debit", "standard_credit", "prepayment")]
    expected_variance = statistics.pvariance([math.log(f) for f in published])

    ledger = _book(channel_renewals=200, channel_losses=20, other_renewals=800, other_losses=40)
    with pressure_ledger_scope(ledger):
        reading = payment_method_engagement_reading(_METHOD, 2020)

    n_book, book_losses = reading.book_decisions, reading.book_losses
    n_effective = (reading.decisions * n_book) / (reading.decisions + n_book)
    p_book = (book_losses + 0.5) / (n_book + 1.0)
    assert reading.weight == log_space_update_weight(n_effective, p_book, expected_variance)
    assert reading.weight != log_space_update_weight(n_effective, p_book, PRIOR_LOG_VARIANCE), (
        "the channel is being weighted against the year series' dispersion, not its own"
    )


def test_the_run_loop_still_hands_the_channel_to_both_the_belief_and_the_departure():
    """WIRING TRIPWIRE, not a contract test, and labelled as one.

    A decade run is not reachable from a unit suite, so nothing else here can notice the argument
    being dropped from `run_phase2b` -- which is exactly how PB6's coefficient came to be live and
    unreached for a day. Read as an AST rather than grepped, so a mention in a comment or a
    docstring cannot satisfy it.
    """
    source = Path(__file__).resolve().parents[3] / "simulation" / "run_phase2b.py"
    tree = ast.parse(source.read_text())
    wired = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if name in {"RenewalObservation", "observe_competitive_loss"}:
            if any(kw.arg == "payment_method" for kw in node.keywords):
                wired.add(name)
    assert wired == {"RenewalObservation", "observe_competitive_loss"}, (
        f"the run books {sorted(wired)} with a payment channel; the engagement belief needs both "
        "-- a denominator without a numerator reads as a channel nobody ever leaves"
    )
