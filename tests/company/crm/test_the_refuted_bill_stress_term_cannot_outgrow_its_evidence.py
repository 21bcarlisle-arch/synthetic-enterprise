"""The refuted `bill_stress` term may not assert more than the evidence for it.

REUSE: tests/company/crm/test_the_refuted_bill_stress_term_cannot_outgrow_its_evidence.py
INDEX: searched "bill_stress", "churn", "ceiling", "cap", "bound", "saturation", "arrears",
"distress", "CIM", "Table 56". What exists and why none of it is this control:
  * `tests/company/crm/test_churn_model.py` — the term's OWN arithmetic and its knee. Asks what
    the term computes, never whether what it computes is allowed to be that large.
  * `tests/company/test_the_bill_stress_threshold_carries_its_origin.py` — asks whether the
    constant DECLARES an origin. A declared gap and an unbounded magnitude are different defects;
    that test stayed green through every value this term ever produced, including 5.37.
  * `tests/company/crm/test_the_churn_belief_hears_household_size.py` — the SOURCED size term. It
    deliberately picks a LOW RATE DECK so this knee is INERT across its whole sweep, which is
    exactly why it cannot see this.
  * `tests/simulation/test_phase24a_ic_customer.py` — saturation for I&C, where the term's
    sensitivity is already 0.0.
No existing control asks whether an unsourced term can outgrow every sourced term beside it.

THE DEFECT EACH TEST NAMES
--------------------------
`bill_stress = sens * max(0, prev_annual_bill / threshold - 1)` was UNBOUNDED in consumption. It
is refuted in SHAPE (a knee) and in VARIABLE (bill level) —
`docs/market_research/is_there_a_bill_level_at_which_switching_rises.md` — and it was nonetheless
free to grow without limit: at 100,000 kWh on the Jan–Mar 2023 cap it returned 5.37 and pinned the
estimate at the 1.0 ceiling with NO RATE MOVE AT ALL.

That is not a tail inaccuracy. It is the refuted term overwhelming every sourced term in the
model, and it has already cost a real diagnosis: it is what made the neighbouring (sourced,
saturating) size term's saturation control red and read exactly like the NEW term running away.

  * `test_the_term_cannot_assert_more_distress_than_the_published_measurement_of_distress`
    — delete the `min(...)` in `estimate_churn_probability` → RED at every consumption above the
    knee. This is the whole claim.
  * `test_the_ceiling_both_binds_and_releases_across_the_record`
    — ONE control over the WHOLE partition, because a ceiling that binds on EVERY input passes
    every "is it bounded" assertion while having silently deleted the term, and a ceiling that
    binds on NONE passes them too while bounding nothing.
  * `test_the_ceiling_is_the_published_ratio_and_scales_with_each_segments_own_base`
    — replace the derivation with a literal, or drop the `base_rate` factor → RED. Keys to the
    SOURCE, not to 0.0283.
  * `test_the_refuted_term_can_no_longer_reach_the_probability_ceiling_unaided`
    — the live defect, keyed to the model's own declared elbow rather than to today's number.

MUTATION SWEEP, RUN RATHER THAN PROMISED, and reported as it came back rather than as it was
designed. Five mutations, five kills, in an isolated copy of the tree so a mutated
`churn_model.py` could not red another lane's live gate run:

    M1  remove the `min(...)` entirely        KILLED by 1, 4
    M2  ratio 100.0   (never binds)           KILLED by 2, 3, 4
    M3  ratio 1.0     (always binds, zero)    KILLED by 1, 2, 3
    M4  ceiling returns the literal 0.0283    KILLED by 3, 4
    M5  ratio 1.0001  (always binds, nonzero) KILLED by 2, 3

**The first draft of leg 2 was near-vacuous and the sweep is what said so.** It partitioned on
`raw > ceiling` versus everything else, and "everything else" included the zero-consumption case
whose raw term is 0.0 — so the release side stayed non-empty under every mutation that shrank the
ceiling to nothing, and M3 was killed by leg 1's vacuity guard instead, which is the flattering
reading. The release side now requires an input where the term is **both non-zero and below the
ceiling**, and M5 exists to prove that leg can fail on its own: a ceiling of 1e-5 is positive, so
leg 1's guard passes it, and only leg 2 catches it.
"""
from __future__ import annotations

import pytest

from company.crm.churn_model import (
    BASE_CHURN_RATE,
    BILL_STRESS_MAX_RATIO,
    BILL_STRESS_SENSITIVITY,
    BILL_STRESS_THRESHOLD_GBP,
    CHURN_SATURATION_ELBOW,
    GAS_BASE_CHURN_RATE,
    bill_stress_uplift_ceiling,
    estimate_churn_probability,
)

#: THE PUBLISHED PRICE DECK, not a swept range. Electricity £/MWh at the edges and the peak of the
#: cap record, read from `docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`
#: as quoted in the research note. 674.7 is the Jan–Mar 2023 cap — the highest level in the book,
#: and the one the runaway was measured on.
_CAP_RECORD_ELEC_GBP_PER_MWH = (165.2, 208.0, 263.5, 340.0, 674.7)

#: Consumptions spanning Ofgem's own benchmark household (3,100 kWh) to the 100,000 kWh account
#: that produced the 1.0 reading. Not a calibration — the domain over which the bound must hold.
_CONSUMPTION_SWEEP_KWH = (0.0, 2500.0, 3100.0, 5000.0, 10000.0, 20000.0, 45000.0, 100000.0)


def _uncapped_bill_stress(rate_gbp_per_mwh: float, kwh: float) -> float:
    """The term as it stood before the bound — the quantity under test, stated independently."""
    prev_annual_bill_gbp = rate_gbp_per_mwh * kwh / 1000.0
    return BILL_STRESS_SENSITIVITY * max(0.0, prev_annual_bill_gbp / BILL_STRESS_THRESHOLD_GBP - 1.0)


def test_the_term_cannot_assert_more_distress_than_the_published_measurement_of_distress() -> None:
    """No input anywhere in the record lets the term exceed CIM w6's arrears ratio.

    Measured as the uplift over the SAME account with no consumption on record, which isolates
    this term: every other term in the model is identical between the two calls.
    """
    ceiling = bill_stress_uplift_ceiling(BASE_CHURN_RATE)
    assert ceiling > 0.0, "a zero ceiling would make every assertion below vacuously true"

    for rate in _CAP_RECORD_ELEC_GBP_PER_MWH:
        baseline = estimate_churn_probability(rate, rate, tenure_years=0.0, annual_consumption_kwh=0.0)
        for kwh in _CONSUMPTION_SWEEP_KWH:
            p = estimate_churn_probability(rate, rate, tenure_years=0.0, annual_consumption_kwh=kwh)
            uplift = p - baseline
            assert uplift <= ceiling + 1e-12, (
                f"bill_stress asserted {uplift:.4f} of churn uplift at {kwh:,.0f} kWh and "
                f"£{rate:.1f}/MWh — more distress-driven switching than the only published "
                f"measurement of distress-driven switching ({ceiling:.4f}, CIM w6 Table 56)"
            )


def test_the_ceiling_both_binds_and_releases_across_the_record() -> None:
    """ONE control over the whole partition: the bound must be reachable AND escapable.

    A ceiling that never binds bounds nothing; a ceiling that always binds has deleted the term.
    Asserting only "the term is bounded" cannot tell those apart from the working mechanism, and
    this project has entered that trap through three separate doors in one afternoon.
    """
    binds: list[tuple[float, float]] = []
    operates: list[tuple[float, float]] = []
    ceiling = bill_stress_uplift_ceiling(BASE_CHURN_RATE)

    for rate in _CAP_RECORD_ELEC_GBP_PER_MWH:
        for kwh in _CONSUMPTION_SWEEP_KWH:
            raw = _uncapped_bill_stress(rate, kwh)
            if raw > ceiling:
                binds.append((rate, kwh))
            elif raw > 0.0:
                # THE RELEASE SIDE MUST BE A TERM STILL DOING SOMETHING, NOT MERELY A ZERO. An
                # earlier draft of this leg counted `raw <= ceiling` and was near-vacuous: the
                # sweep contains a zero-consumption case whose raw term is 0.0, so "something
                # released" stayed true under every mutation that shrank the ceiling toward zero,
                # and the partition looked intact while the term was gone.
                operates.append((rate, kwh))

    assert binds, "the ceiling never binds anywhere in the published record — it bounds nothing"
    assert operates, (
        "there is no input in the whole published record where the term is BOTH non-zero AND "
        "below the ceiling — the bound has stopped bounding and started replacing, which is the "
        "term deleted while still looking present"
    )

    # And a benchmark-consumption household is below the knee in every window, so the refuted term
    # is untouched by the ceiling exactly where the record says it never fired in the first place.
    for rate in _CAP_RECORD_ELEC_GBP_PER_MWH:
        assert _uncapped_bill_stress(rate, 3100.0) == 0.0


def test_the_ceiling_is_the_published_ratio_and_scales_with_each_segments_own_base() -> None:
    """Keyed to the source, not to 0.0283 — and to a RATIO, which is why it can cross at all."""
    # Ofgem CIM wave 6, Table 56: arrears "getting harder" 6.8% against a 5.3% population base.
    assert BILL_STRESS_MAX_RATIO == pytest.approx(0.068 / 0.053)
    assert 1.0 < BILL_STRESS_MAX_RATIO < 1.4, (
        "the published distress effect is the WEAKEST association in Table 56 — a ratio outside "
        "this band is not that banner any more"
    )

    # It is an uplift ceiling on each segment's OWN base rate, because 1.28x is a ratio on a
    # switching rate and `base_rate` is what this model calls that. Gas and electricity therefore
    # do not share a ceiling; a bound that dropped the base_rate factor would give them one.
    assert bill_stress_uplift_ceiling(GAS_BASE_CHURN_RATE) < bill_stress_uplift_ceiling(BASE_CHURN_RATE)
    assert bill_stress_uplift_ceiling(BASE_CHURN_RATE) == pytest.approx(
        BASE_CHURN_RATE * (BILL_STRESS_MAX_RATIO - 1.0))
    assert bill_stress_uplift_ceiling(0.0) == 0.0


def test_the_refuted_term_can_no_longer_reach_the_probability_ceiling_unaided() -> None:
    """The live defect, keyed to the model's own declared elbow rather than to today's number.

    100,000 kWh at the peak of the cap record, with NO rate move and no tenure: every sourced term
    in the model is neutral, so whatever comes out is this term alone. It used to be 1.0000.
    """
    p = estimate_churn_probability(674.7, 674.7, tenure_years=0.0, annual_consumption_kwh=100_000.0)
    assert p < CHURN_SATURATION_ELBOW, (
        f"the refuted term alone carried the estimate to {p:.4f}, past the elbow the model "
        f"declares as the start of its ceiling region — with no price move to justify it"
    )
    # And it lands where the evidence says it may: base x the published arrears ratio.
    assert p == pytest.approx(BASE_CHURN_RATE * BILL_STRESS_MAX_RATIO)
