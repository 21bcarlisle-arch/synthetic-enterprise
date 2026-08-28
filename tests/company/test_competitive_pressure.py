"""Controls on the company's competitive-pressure belief.

EVERY TEST HERE NAMES THE DEFECT IT EXISTS TO CATCH, and each was mutation-proven by making the
named defect and watching this file go red. The headline one is
`test_the_belief_MOVES_when_the_book_loses_more_than_it_predicted`: reverting
`derived_market_pressure_multiplier` to the year table -- which is exactly what the code did
until 2026-08-28 and is the single most likely way this channel dies -- reds it.
"""
from __future__ import annotations

import math

import pytest

from company.crm.competitive_pressure import (
    PRIOR_LOG_VARIANCE,
    CompetitivePressureLedger,
    active_pressure_ledger,
    derived_market_pressure_multiplier,
    pressure_ledger_scope,
)
from company.crm.market_conditions import (
    MARKET_SWITCHING_MULTIPLIER_BY_YEAR,
    market_conditions_multiplier,
)


def _book(year: int, decisions: int, believed: float, losses: int) -> CompetitivePressureLedger:
    """A ledger that has seen a run: departures ARE being reported to it."""
    ledger = CompetitivePressureLedger()
    ledger.arm_loss_reporting()
    for _ in range(decisions):
        ledger.observe_renewal_decision(year, believed)
    for _ in range(losses):
        ledger.observe_competitive_loss(year)
    return ledger


class TestTheChannelIsNotAConstant:
    """THE ATOM. B10's L3 leg is that a rival's move can reach the company at all."""

    def test_the_belief_MOVES_when_the_book_loses_more_than_it_predicted(self):
        """DEFECT: the multiplier is a year lookup and no observation can change it.

        This is the state the code was in until 2026-08-28 and the reason B10 could not reach
        L3: a chase-on/chase-off pair moved the world at every rung and moved the company's
        `believed_p_leave` by `max |ON - OFF| = 0.0`. Wiring
        `derived_market_pressure_multiplier` back to `market_conditions_multiplier` reds this.
        """
        prior = market_conditions_multiplier(2019)
        quiet = _book(2018, decisions=26, believed=0.30, losses=4).reading(2019)
        pressed = _book(2018, decisions=26, believed=0.30, losses=12).reading(2019)

        assert quiet.multiplier != pressed.multiplier
        # Direction, not merely difference: a book that lost MORE than it predicted believes the
        # market is competing HARDER. A channel wired backwards would pass a bare `!=`.
        assert pressed.multiplier > quiet.multiplier
        # And both are genuinely displaced from the published table, not just from each other.
        assert quiet.multiplier < prior < pressed.multiplier

    def test_ONE_extra_realised_loss_is_enough_to_move_the_belief(self):
        """DEFECT: the channel exists but is quantised so coarsely it can never fire.

        The instrument this replaces failed exactly this way -- a binary flip count on 17
        decisions whose smallest expressible change was 5.9 percentage points, which is why a
        real 0.7-4.5pp world effect read as a null. A channel whose resolution is coarser than
        the effect it is built to see is not a channel. On a 26-decision book one account is
        worth ~8% of the multiplier; this pins that it is non-zero and material.
        """
        base = _book(2018, decisions=26, believed=0.30, losses=8).reading(2019)
        one_more = _book(2018, decisions=26, believed=0.30, losses=9).reading(2019)

        moved = abs(one_more.multiplier - base.multiplier) / base.multiplier
        assert moved > 0.01, f"one account moved the belief only {moved:.4%}"

    def test_the_belief_is_MONOTONE_in_realised_losses(self):
        """DEFECT: the weight co-varies with the answer, so more losses can mean less pressure.

        This is not hypothetical -- it is what the FIRST draft of this module did, found by
        printing the table at real inputs rather than by reasoning. Evaluating the evidence
        variance at the realised proportion (Wald) instead of the predicted one (score) gave a
        multiplier of 0.542 on 30 losses and 0.594 on ZERO losses out of 200. Restoring
        `(1 - p_observed) / (n * p_observed)` reds this.
        """
        seen = [_book(2018, decisions=200, believed=0.30, losses=k).reading(2019).multiplier
                for k in range(0, 130, 10)]
        assert seen == sorted(seen), f"not monotone in realised losses: {seen}"


class TestItFailsSoftToThePublishedPrior:
    """A channel that fabricates pressure from no evidence is worse than no channel."""

    def test_with_NO_run_scope_it_is_byte_identical_to_the_year_table(self):
        """DEFECT: the new channel changes answers for callers that never opted in.

        Every consumer outside a run -- reports, tests, the site's own readers -- must see
        exactly the behaviour that shipped before this module existed. Making
        `active_pressure_ledger()` default to a shared module-level ledger reds this.
        """
        assert active_pressure_ledger() is None
        for year in list(MARKET_SWITCHING_MULTIPLIER_BY_YEAR) + [None, 1999, 2031]:
            assert derived_market_pressure_multiplier(year) == market_conditions_multiplier(year)

    def test_an_OPEN_but_EMPTY_ledger_returns_the_prior_and_says_so(self):
        """DEFECT: an empty window is treated as evidence that nobody is leaving.

        `observed = 0` and `decisions = 0` are different facts. Reading the first from the
        second would make every run's opening year believe the market had stopped competing --
        the FAIL-OPEN shape, arrived at by dividing by a population that is not there.
        """
        with pressure_ledger_scope() as ledger:
            # Armed, so the refusal below is the EMPTY-WINDOW one and not the unarmed one --
            # two different refusals that would otherwise be indistinguishable through a
            # `multiplier == prior` assertion, which both satisfy.
            ledger.arm_loss_reporting()
            reading = ledger.reading(2019)
            assert reading.multiplier == market_conditions_multiplier(2019)
            assert reading.moved_from_prior is False
            assert "no closed renewal years" in reading.basis

    def test_a_window_predicting_ZERO_losses_refuses_a_ratio(self):
        """DEFECT: dividing by a zero prediction makes one departure infinite evidence."""
        reading = _book(2018, decisions=26, believed=0.0, losses=3).reading(2019)
        assert reading.multiplier == market_conditions_multiplier(2019)
        assert reading.ratio is None
        assert "predicted zero losses" in reading.basis

    def test_a_window_where_NOBODY_left_is_still_readable(self):
        """DEFECT: zero realised losses gives log(0) and the reading dies or refuses.

        Nobody leaving is a real and highly informative observation -- it must lower the belief,
        not crash it and not be discarded.

        THE STRICTLY-POSITIVE ASSERTION IS THE ONE THAT MATTERS and it was added because the
        first version of this test DID NOT FIRE against the mutation it was written for.
        Deleting the continuity correction sends `p_observed` to exactly 0, so `ratio` is 0 and
        the multiplier is 0 -- which is finite, and which is below the prior, so both original
        assertions passed. A multiplier of zero means NO CUSTOMER CAN EVER LEAVE at any price:
        the captive floor `_apply_market_conditions` was rewritten in survival space to remove,
        arrived at from the other side. A control that accepts it is a control that cannot fail.
        """
        reading = _book(2018, decisions=26, believed=0.30, losses=0).reading(2019)
        assert math.isfinite(reading.multiplier)
        assert reading.multiplier < market_conditions_multiplier(2019)
        assert reading.multiplier > 0.0, (
            "a book that lost nobody believes NO customer can ever leave at any price -- "
            "the captive floor, reached from the other side")


class TestWhatMayCountAsEvidence:

    def test_the_company_CANNOT_see_the_year_it_is_pricing(self):
        """DEFECT: look-ahead -- an estimate informed by its own outcome.

        A renewal priced in 2019 may only learn from years that have closed. Widening
        `_closed_window` from `y < renewal_year` to `y <= renewal_year` reds this.
        """
        ledger = _book(2019, decisions=26, believed=0.30, losses=12)
        assert ledger.reading(2019).multiplier == market_conditions_multiplier(2019)
        assert ledger.reading(2020).moved_from_prior is True

    def test_an_UNARMED_ledger_REFUSES_to_update_however_full_its_denominator(self):
        """DEFECT: 'nobody told us' is read as 'nobody left'. THE FAIL-OPEN, and it happened.

        This is not a hypothetical. The first live measurement of this channel ran the whole
        chase-on/chase-off pair through `run_phase4c_on_phase2b.main`, which calls
        `run_phase2b()` with NO `sim_interface` -- so every `notify_churn` sat behind an
        `if sim_interface is not None` and none fired. The ledger filled its denominator from
        the desk, left its numerator at zero, and concluded the market had gone quiet during a
        run in which a sixth of the book left. The published over-prediction gap appeared to
        narrow from 20.7-28.7pp to 1.1-14.9pp and every one of those numbers was an artefact of
        a dead wire -- the flattering direction, which is why it nearly survived.

        Deleting the `loss_reporting_armed` guard in `reading()` reds this.
        """
        ledger = CompetitivePressureLedger()
        for _ in range(200):
            ledger.observe_renewal_decision(2018, 0.30)
        assert ledger.loss_reporting_armed is False

        reading = ledger.reading(2019)
        assert reading.multiplier == market_conditions_multiplier(2019)
        assert reading.moved_from_prior is False
        assert "not being reported" in reading.basis

        # And the SAME ledger, once something undertakes to report, does update -- so the guard
        # is not simply switching the channel off.
        ledger.arm_loss_reporting()
        assert ledger.reading(2019).moved_from_prior is True

    def test_a_run_that_loses_NOBODY_still_arms_nothing_and_keeps_the_prior(self):
        """DEFECT: arming is unconditional, so the guard above is a tautology.

        Arming is done by the booking site itself (`run_phase2b`'s churn branch), so a run in
        which no account ever leaves never arms -- and that is correct, because such a run has
        produced no evidence either way. A guard armed at run START would pass this test while
        catching nothing.
        """
        ledger = CompetitivePressureLedger()
        for _ in range(50):
            ledger.observe_renewal_decision(2018, 0.30)
        assert ledger.reading(2019).multiplier == market_conditions_multiplier(2019)

    def test_the_prior_variance_is_DERIVED_from_the_published_series(self):
        """DEFECT: the shrinkage strength becomes a constant somebody picked.

        A number invented to fill this slot would be load-bearing within a week and
        unattributable within a month. It is the dispersion of the published multiplier series
        in log space, recomputed here from the series rather than quoted.
        """
        import statistics

        expected = statistics.pvariance(
            [math.log(m) for m in MARKET_SWITCHING_MULTIPLIER_BY_YEAR.values()])
        assert PRIOR_LOG_VARIANCE == pytest.approx(expected)

    def test_more_evidence_moves_the_belief_further_from_the_prior(self):
        """DEFECT: sample size is ignored, so thirty renewals and three weigh the same.

        The whole reason the published series is kept as a prior is that a thin book should not
        overturn a national statistic. Replacing the precision weight with a constant reds this.
        """
        ratios = [
            _book(2018, decisions=n, believed=0.30, losses=round(n * 0.6)).reading(2019)
            for n in (5, 26, 200)
        ]
        weights = [r.weight for r in ratios]
        assert weights == sorted(weights)
        displacement = [r.multiplier / r.prior for r in ratios]
        assert displacement == sorted(displacement)


class TestTheLedgerIsRunScoped:

    def test_one_run_cannot_inform_the_next(self):
        """DEFECT: a module-level ledger leaks belief between the arms of an A/B.

        On a comparison whose entire subject is the difference between two arms, a shared
        ledger is not a leak -- it is a fabricated result. Making `_ACTIVE_LEDGER` default to a
        shared instance reds this.
        """
        with pressure_ledger_scope() as first:
            first.observe_renewal_decision(2018, 0.30)
            first.observe_competitive_loss(2018)
        with pressure_ledger_scope() as second:
            assert second.decisions_by_year == {}
            assert second.losses_by_year == {}
        assert active_pressure_ledger() is None

    def test_a_failed_arm_does_not_contaminate_the_next(self):
        with pytest.raises(RuntimeError):
            with pressure_ledger_scope() as ledger:
                ledger.observe_competitive_loss(2018)
                raise RuntimeError("arm died mid-run")
        assert active_pressure_ledger() is None


class TestItReachesTheChurnEstimate:
    """A belief nothing reads is not a belief. This is the wiring, not the formula."""

    def test_the_derived_multiplier_CHANGES_a_real_churn_estimate(self):
        """DEFECT: the module exists and is imported but no estimate is scaled by it.

        The unwired-module shape: `derived_market_pressure_multiplier` could be correct in
        every respect and reach nothing. This drives the real
        `enriched_churn_estimate` on identical customer inputs under two different loss books
        and requires the ESTIMATE to differ.
        """
        from company.crm.enriched_churn_estimate import enriched_churn_estimate

        args = dict(old_rate_gbp_per_mwh=180.0, new_rate_gbp_per_mwh=210.0,
                    tenure_years=3.0, annual_consumption_kwh=3100.0, renewal_year=2019)

        with pressure_ledger_scope(_book(2018, decisions=26, believed=0.30, losses=2)):
            quiet = enriched_churn_estimate(**args)
        with pressure_ledger_scope(_book(2018, decisions=26, believed=0.30, losses=16)):
            pressed = enriched_churn_estimate(**args)

        assert pressed > quiet, (
            f"a book that lost 16 of 26 believes no more pressure than one that lost 2 "
            f"({pressed} vs {quiet}) -- the channel does not reach the estimate")

    def test_the_desk_BOOKS_what_it_believed(self):
        """DEFECT: the denominator is never populated, so the ratio has nothing to divide by.

        `estimate_renewal_churn` is the company's once-per-renewal belief site. If it stops
        booking, `decisions_by_year` stays empty, every reading refuses, and the channel dies
        silently back to the prior -- passing every test that only checks the formula.
        """
        from company.crm.churn_desk import RenewalObservation, estimate_renewal_churn

        with pressure_ledger_scope() as ledger:
            estimate = estimate_renewal_churn(RenewalObservation(
                old_rate_gbp_per_mwh=180.0, new_rate_gbp_per_mwh=210.0,
                tenure_years=3.0, annual_consumption_kwh=3100.0, renewal_year=2018))
            assert ledger.decisions_by_year == {2018: 1}
            assert ledger.expected_by_year[2018] == pytest.approx(estimate)

    def test_the_PASSIVE_branch_books_too(self):
        """DEFECT: booking is on one branch only.

        Passive SVT rollers are 65% of resi renewals in most years and 100% of them in crisis
        years, so a denominator missing that branch would be missing most of the book -- and
        would be missing it in exactly the years the belief matters most.
        """
        from company.crm.churn_desk import RenewalObservation, estimate_renewal_churn

        with pressure_ledger_scope() as ledger:
            estimate_renewal_churn(RenewalObservation(
                old_rate_gbp_per_mwh=180.0, new_rate_gbp_per_mwh=210.0,
                tenure_years=3.0, renewal_year=2018, active_renewal=False, segment="resi"))
            assert ledger.decisions_by_year == {2018: 1}
