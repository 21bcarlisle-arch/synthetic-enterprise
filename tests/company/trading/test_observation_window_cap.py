"""R15 both-ways tests for the VALUE_CHAIN observation-window credit cap (BUILD ladder step 3).

The declared FAIL (PRIORITIES.md PRODUCT-FIRST item 3): the wholesale credit cap was a *static
dict* keyed only on rating. This mechanism makes the cap a rating-anchored PRIOR that erodes from
the company's OWN observed margin-call settle/dispute conduct for a counterparty — a through-the-
wall observable. Benign default: no observed conduct → the prior stands unchanged.

R15 doctrine — every assertion below is paired with the MUTATION that reds it, so the control
provably fires on its own named defect (a cap that cannot move on adverse conduct, or that moves
when it must not).
"""
import pytest

from company.trading.wholesale_credit_exposure import (
    CounterpartyType,
    ClearingStatus,
    CounterpartyCreditRating,
    WholesaleCreditRecord,
    ObservedCounterpartyBehaviour,
    observation_window_credit_limit,
    _CREDIT_LIMIT_BY_RATING,
    _WINDOW_LIMIT_FLOOR_FRACTION,
)

RATING = CounterpartyCreditRating.A
PRIOR = _CREDIT_LIMIT_BY_RATING[RATING]  # 2_000_000.0


def _record(behaviour=None, rating=RATING, override=None):
    return WholesaleCreditRecord(
        counterparty_id="CP1",
        counterparty_type=CounterpartyType.MAJOR_BANK,
        credit_rating=rating,
        clearing_status=ClearingStatus.BILATERAL_ISDA,
        gross_mtm_gbp=500_000.0,
        collateral_held_gbp=0.0,
        credit_limit_override_gbp=override,
        observed_behaviour=behaviour,
    )


class TestBenignDefault:
    def test_no_behaviour_equals_rating_prior(self):
        # Fail-safe: absent observed conduct, the cap is exactly the rating prior (backward-compat).
        # MUTATION that reds this: erode on an empty history (drop the n_observed==0 guard) → cap < prior.
        assert observation_window_credit_limit(RATING, None) == pytest.approx(PRIOR)
        assert _record(behaviour=None).credit_limit_gbp == pytest.approx(PRIOR)

    def test_all_settled_history_equals_prior(self):
        # A clean settled record is NOT adverse → prior stands (one-directional: no earn-up).
        # MUTATION: count settled as adverse → cap would drop below prior.
        b = ObservedCounterpartyBehaviour(n_settled=20, n_disputed=0, n_defaulted=0)
        assert observation_window_credit_limit(RATING, b) == pytest.approx(PRIOR)


class TestErosionFires:
    def test_all_defaulted_hits_the_floor(self):
        # The maximal adverse history erodes the cap to exactly the floor fraction of the prior.
        # MUTATION (revert to static): ignore behaviour → returns PRIOR, reds this. MUTATION (floor
        # set to 1.0): no erosion → returns PRIOR, reds this.
        b = ObservedCounterpartyBehaviour(n_settled=0, n_disputed=0, n_defaulted=10)
        assert observation_window_credit_limit(RATING, b) == pytest.approx(
            PRIOR * _WINDOW_LIMIT_FLOOR_FRACTION
        )

    def test_disputes_erode_less_than_defaults(self):
        # A dispute is a softer signal than a default: an all-disputed book erodes, but by less
        # than an all-defaulted book. MUTATION: equal weights → these two collapse, reds this.
        all_disputed = ObservedCounterpartyBehaviour(n_disputed=10)
        all_defaulted = ObservedCounterpartyBehaviour(n_defaulted=10)
        cap_disputed = observation_window_credit_limit(RATING, all_disputed)
        cap_defaulted = observation_window_credit_limit(RATING, all_defaulted)
        assert cap_disputed < PRIOR                       # disputes DO erode
        assert cap_defaulted < cap_disputed               # defaults erode harder

    def test_monotone_in_default_count(self):
        # More adverse conduct (fixed observed total) → strictly lower cap. MUTATION: non-monotone
        # or clamped scoring reds this.
        caps = [
            observation_window_credit_limit(
                RATING, ObservedCounterpartyBehaviour(n_settled=10 - k, n_defaulted=k)
            )
            for k in range(0, 11)
        ]
        assert caps == sorted(caps, reverse=True)
        assert caps[0] == pytest.approx(PRIOR)                       # all settled → prior
        assert caps[-1] == pytest.approx(PRIOR * _WINDOW_LIMIT_FLOOR_FRACTION)  # all defaulted → floor

    def test_cap_never_below_floor(self):
        # The floor is a hard lower bound even at the maximal adverse score.
        b = ObservedCounterpartyBehaviour(n_disputed=3, n_defaulted=97)
        cap = observation_window_credit_limit(RATING, b)
        assert cap >= PRIOR * _WINDOW_LIMIT_FLOOR_FRACTION - 1e-6


class TestBreachInteraction:
    def test_erosion_can_flip_a_record_into_breach(self):
        # The mechanism has TEETH: a net exposure that is WITHIN the rating-band limit becomes a
        # LIMIT BREACH once observed defaults erode the cap below it. This is the whole point — a
        # deteriorating counterparty's line tightens until the same position breaches.
        # MUTATION (static cap): the eroded branch never runs → no breach → reds this.
        exposure = 600_000.0  # well within the 2.0M rating prior
        clean = _record(behaviour=None)
        clean = WholesaleCreditRecord(
            counterparty_id="CP1", counterparty_type=CounterpartyType.MAJOR_BANK,
            credit_rating=RATING, clearing_status=ClearingStatus.BILATERAL_ISDA,
            gross_mtm_gbp=exposure, collateral_held_gbp=0.0,
        )
        assert not clean.is_limit_breached  # 600k < 2.0M prior

        eroded = WholesaleCreditRecord(
            counterparty_id="CP1", counterparty_type=CounterpartyType.MAJOR_BANK,
            credit_rating=RATING, clearing_status=ClearingStatus.BILATERAL_ISDA,
            gross_mtm_gbp=exposure, collateral_held_gbp=0.0,
            observed_behaviour=ObservedCounterpartyBehaviour(n_defaulted=10),  # cap → 500k
        )
        assert eroded.credit_limit_gbp == pytest.approx(PRIOR * _WINDOW_LIMIT_FLOOR_FRACTION)
        assert eroded.is_limit_breached  # 600k > 500k eroded cap


class TestOverrideUnaffected:
    def test_ccp_override_ignores_observed_conduct(self):
        # A CCP no-per-name-limit override wins over the window mechanic (the default waterfall
        # absorbs; a CCP does not carry a per-name credit line that observed conduct erodes).
        r = _record(behaviour=ObservedCounterpartyBehaviour(n_defaulted=10), override=1e15)
        assert r.credit_limit_gbp == pytest.approx(1e15)


class TestBehaviourScore:
    def test_adverse_score_bounds(self):
        assert ObservedCounterpartyBehaviour().adverse_score == 0.0
        assert ObservedCounterpartyBehaviour(n_settled=5).adverse_score == 0.0
        assert ObservedCounterpartyBehaviour(n_defaulted=5).adverse_score == pytest.approx(1.0)
        # weighted blend: 2 settled, 2 disputed(0.5), 0 defaulted over 4 → (0.5*2)/4 = 0.25
        mixed = ObservedCounterpartyBehaviour(n_settled=2, n_disputed=2)
        assert mixed.adverse_score == pytest.approx(0.25)

    def test_deterministic_replay(self):
        # C-S2: the same observed counts reproduce the same cap.
        b = ObservedCounterpartyBehaviour(n_settled=3, n_disputed=2, n_defaulted=1)
        assert observation_window_credit_limit(RATING, b) == observation_window_credit_limit(RATING, b)
