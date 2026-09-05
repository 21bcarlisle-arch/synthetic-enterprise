"""W2_sme_segment_case_normalisation -- the case defect, and the trap in fixing it.

Two things have to be true at once, and the second is why this atom needed a
new outcome model before the one-line case fix was safe:

  1. A real SME bill -- stored by `saas/customers.py` as "SME" -- must reach
     the CORPORATE payment rail, not the residential one.
  2. Fixing (1) must NOT delete SME bad debt. Before `sme_payment_behaviour`
     existed, an SME bill reaching the corporate rail fell through
     `payment_outcome`'s bacs/chaps arm to a bare `("success", 0)`: it could
     never be late, fail, or dispute. Normalising the case ALONE would have
     silently zeroed SME arrears while looking like a bug fix.

The tests below assert (2) at population scale, because that is the only scale
at which "bad debt still exists" is a meaningful claim.
"""
from __future__ import annotations

import random
from collections import Counter

import pytest

from simulation.arrears_engine import payment_method, payment_outcome
from simulation.payment_behaviour_source import generate_payment_event
from simulation.segment_vocabulary import (
    INDUSTRIAL_AND_COMMERCIAL,
    RESIDENTIAL,
    SME,
    UnknownSegmentError,
    is_business,
    normalise_segment,
)
from simulation.sme_payment_behaviour import SME_TARGET_LATE_RATE

#: Every spelling of the SME segment that has actually reached this code.
SME_SPELLINGS = ["SME", "sme", "Sme", " SME ", "microbusiness"]

#: Every spelling of the I&C segment that has actually reached this code --
#: "IC" is `saas/smart_meter_rollout`'s, "ic" was `arrears_engine`'s own.
IC_SPELLINGS = ["I&C", "i&c", "ic", "IC"]


class TestTheDefect:
    """The mis-route itself: the canonical spelling took the wrong branch."""

    def test_canonical_sme_reaches_the_corporate_rail(self):
        # THE defect. Before the fix this returned a residential method,
        # because "SME" matched neither `== "sme"` nor `("ic", "I&C")`.
        assert payment_method(SME, 850.0, "C5") == "bacs"

    def test_canonical_ic_reaches_the_corporate_rail(self):
        assert payment_method(INDUSTRIAL_AND_COMMERCIAL, 850.0, "C1") == "bacs"
        assert payment_method(INDUSTRIAL_AND_COMMERCIAL, 50000.0, "C1") == "chaps"

    @pytest.mark.parametrize("spelling", SME_SPELLINGS)
    def test_every_sme_spelling_routes_identically(self, spelling):
        assert payment_method(spelling, 850.0, "C5") == "bacs"

    @pytest.mark.parametrize("spelling", IC_SPELLINGS)
    def test_every_ic_spelling_routes_identically(self, spelling):
        assert payment_method(spelling, 850.0, "C1") == "bacs"
        assert payment_method(spelling, 50000.0, "C1") == "chaps"

    def test_residential_is_untouched(self):
        # The fix must not drag households onto a corporate rail. Without a
        # customer_id the long-standing flat default is preserved exactly.
        assert payment_method(RESIDENTIAL, 850.0) == "direct_debit"

    def test_the_corporate_rail_is_reached_via_the_bill_default(self):
        # Call sites read `bill.get("segment", "resi")`; an absent segment
        # must stay residential rather than raising mid-run.
        assert payment_method(None, 850.0) == "direct_debit"


class TestTheTrap:
    """Fixing the case must not delete SME bad debt."""

    def _sme_outcomes(self, n_customers=2000, bills_each=12, seed=7):
        rng = random.Random(seed)
        counts = Counter()
        not_on_time = 0
        for i in range(n_customers):
            cid = "SME%05d" % i
            for _ in range(bills_each):
                method = payment_method(SME, 850.0, cid)
                outcome, days_late = payment_outcome(
                    method, "LOW", rng, SME, False, None, cid
                )
                counts[outcome] += 1
                if outcome != "success" or days_late > 0:
                    not_on_time += 1
        return counts, not_on_time, n_customers * bills_each

    def test_sme_bad_debt_survives_the_case_fix(self):
        """The regression this atom exists to prevent.

        A naive fix routes SME onto the corporate rail, where the old code
        returned `("success", 0)` unconditionally -- every one of these
        assertions would read zero.
        """
        counts, _, _ = self._sme_outcomes()
        assert counts["failed"] > 0, "SME payment failures were deleted by the case fix"
        assert counts["dispute"] > 0, "SME disputes were deleted by the case fix"

    def test_sme_bills_can_be_late(self):
        counts, not_on_time, total = self._sme_outcomes()
        assert not_on_time > 0, "no SME bill was ever late -- the corporate fall-through is back"

    def test_sme_aggregate_matches_the_dbt_anchor(self):
        """The population rate is pinned to a published figure, not to a
        number that makes the company look a particular way (R12/R13)."""
        _, not_on_time, total = self._sme_outcomes()
        observed = not_on_time / total
        assert observed == pytest.approx(SME_TARGET_LATE_RATE, abs=0.01), (
            "SME not-on-time rate %.4f is off the DBT 2024 anchor %.2f"
            % (observed, SME_TARGET_LATE_RATE)
        )

    def test_sme_is_not_modelled_as_ic(self):
        """SME and I&C share a payment RAIL but not an outcome model.

        If SME were simply added to the I&C tuple -- the other obvious naive
        fix -- these two distributions would coincide.
        """
        rng_sme = random.Random(11)
        rng_ic = random.Random(11)
        sme = Counter()
        ic = Counter()
        for i in range(4000):
            cid = "X%05d" % i
            sme[payment_outcome("bacs", "LOW", rng_sme, SME, False, None, cid)[0]] += 1
            ic[payment_outcome("bacs", "LOW", rng_ic, INDUSTRIAL_AND_COMMERCIAL, False, None, cid)[0]] += 1
        assert sme != ic, "SME is being modelled as I&C -- they are not interchangeable"


class TestIandCUnchanged:
    """The I&C model is calibrated and must not move as a side effect."""

    def test_ic_outcome_distribution_is_stable(self):
        rng = random.Random(3)
        counts = Counter()
        for _ in range(5000):
            counts[payment_outcome("bacs", "LOW", rng, INDUSTRIAL_AND_COMMERCIAL)[0]] += 1
        # ~92% on time, ~0.7% dispute -- the pre-existing anchored figures.
        assert counts["dispute"] / 5000 == pytest.approx(0.007, abs=0.005)
        assert counts["failed"] == 0, "the I&C model has never produced failures"


class TestSecondReader:
    """`payment_behaviour_source` had its own copy of the case-sensitive test."""

    @pytest.mark.parametrize("spelling", SME_SPELLINGS + IC_SPELLINGS)
    def test_business_segments_reach_the_corporate_core(self, spelling):
        event = generate_payment_event(
            customer_id="C5",
            period_index=0,
            due_date=__import__("datetime").date(2023, 6, 30),
            amount_gbp=850.0,
            stress="LOW",
            payment_method="bacs",
            segment=spelling,
            seed=42,
        )
        # The corporate core never emits a DD failure reason; a residential
        # mis-route is observable as a direct-debit-shaped outcome.
        assert event.dd_failure_reason is None


class TestVocabularyFailsClosed:
    """An unrecognised segment must raise, never quietly become a household."""

    def test_unknown_segment_raises(self):
        with pytest.raises(UnknownSegmentError):
            normalise_segment("wholesale")

    def test_cohort_id_is_rejected_not_guessed(self):
        # `simulation/segments.py` is a different vocabulary; coercing
        # "sme_smart" to SME would be the silent collision the module exists
        # to prevent.
        with pytest.raises(UnknownSegmentError):
            normalise_segment("sme_smart")

    def test_absent_segment_takes_the_documented_default(self):
        assert normalise_segment(None) == RESIDENTIAL
        assert normalise_segment("") == RESIDENTIAL

    def test_absence_can_be_made_an_error(self):
        with pytest.raises(UnknownSegmentError):
            normalise_segment(None, default=None)

    @pytest.mark.parametrize(
        "not_a_string", [0, 7, 3.7, True, ["resi"], {"segment": "resi"}, object()]
    )
    def test_a_non_string_segment_raises_rather_than_being_coerced(self, not_a_string):
        """Nothing in the tree drove this branch until now.

        Measured 2026-09-05 by the convergence-evidence battery: mutating the
        guard to `return default` SURVIVED all nine suites that name this module
        or call it -- and a tree-wide search finds `None` as the only non-string
        ever passed, which the *absence* branch catches one line earlier. So the
        `isinstance` guard was correct and held in place by nothing.

        The branch is genuinely reachable, which is what makes it worth a test
        rather than a note: every call site reads `bill.get("segment", "resi")`,
        a bill is built from JSON, and a malformed feed hands this a number or a
        list. Were the guard ever traded for `return default`, every one of them
        would quietly become a household -- the C5/C6 mis-route this module
        exists to close, arriving through the one door nothing was watching.
        """
        with pytest.raises(UnknownSegmentError):
            normalise_segment(not_a_string)

    def test_a_non_string_raises_even_when_a_default_is_available(self):
        """Absent and WRONG are different, and only the first has a defensible
        default. Deferring to `default` here collapses that distinction, which
        is exactly what the surviving mutation did -- so the refusal is asserted
        with a default in hand, not only in the bare call above."""
        with pytest.raises(UnknownSegmentError):
            normalise_segment(1234, default=RESIDENTIAL)

    @pytest.mark.parametrize("spelling", SME_SPELLINGS + IC_SPELLINGS)
    def test_is_business_is_case_insensitive(self, spelling):
        assert is_business(spelling) is True

    def test_residential_is_not_business(self):
        assert is_business(RESIDENTIAL) is False
        assert is_business("Residential") is False
