# ARCHIVED LEGS of tests/company/pricing/test_the_arm_reaches_its_own_segment.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/company/pricing/test_the_arm_reaches_its_own_segment.py.
"""R15 proofs that the renewal arm can reach every segment its own churn model branches on.

THE DEFECT (2026-08-26,
`docs/staging/done/WORKER_FINDING_THE_VALUE_ARMS_WHOLE_LOSS_IS_ONE_INDUSTRIAL_ACCOUNT_PRICED_AS_A_HOUSEHOLD_2026-08-26.md`).
`renewal_margin_uplift` computed `segment = "resi" if is_domestic else "SME"` and handed the
result to BOTH the cost tables and the churn model. The stated reason was sound about costs --
`cost_to_serve_for_period` accepts exactly two segments, so one vocabulary beats two that can
disagree -- and wrong about churn: `estimate_churn_probability` branches THREE ways, and its I&C
arm exists precisely to switch bill-size-driven churn OFF for industrial customers.

So the branch was unreachable from the only production caller, and on a 3.9 GWh account the SME
path returns P(leave) = 1.0000 at EVERY candidate margin -- including margins below what the
company already charges. With `p_retain` flat at zero the optimiser has nothing to maximise and
falls to the floor, £0.50/MWh under the control's £2.00. Realised cost: -£94,314 on C_IC3, which
was 99.5% of the value arm's entire measured loss.

WHAT THESE TESTS PIN, and the order matters:

  1. the SATURATION is real and is a property of volume, not of the account being industrial --
     otherwise "use the I&C branch" is a preference rather than a correction;
  2. the segment REACHES the model through every link (run -> chain -> arm -> estimator);
  3. the fallback still works, so a caller that does not know a segment is unchanged;
  4. and a vocabulary MISMATCH cannot be silent, which is how this happened -- there are THREE
     segment vocabularies in this company and nothing checked that a caller's matched a callee's.

These are not tests that the arm earns more. Whether the repair moves the A/B is a measurement,
taken separately, with the expected direction recorded before the run (R12).

**CLAIM 1 IS SUPERSEDED AS OF 2026-09-23, corrected here beside it rather than over it.** The
saturation was REAL when it was measured and it is now GONE, and neither the routing repair nor
this file caused that: `bill_stress` was unbounded in consumption, so a 3.9 GWh account carried a
£236,166 previous-year bill and the term alone asserted 19.5 of churn uplift. That is what pinned
the SME path at 1.0000 at every candidate margin. `BILL_STRESS_MAX_RATIO` now bounds the term to
the only published measurement of distress-driven switching (Ofgem CIM w6 Table 56, arrears
1.28x), and at that bound the SME path at C_IC3's volume spreads 0.063 -> 0.968 across the same
margins. **Three tests in section 1 were keyed to the literal 1.0 and went red when the model
became more honest, which is exactly backwards; they are re-keyed to the property below.**

AND THE CORRECTION GOES FURTHER THAN THE NUMBER: claim 1 said the saturation was *a property of
volume, not of the account being industrial*. Measured under the bound, that is no longer true.
The SME/I&C gap at C_IC3's volume (-0.085 at a £8/MWh margin) is essentially the same as the gap
at a household's volume (-0.101), so what now separates the two branches is the SEGMENT LABEL --
the I&C arm's higher rate sensitivity -- and not the volume at all. **The routing repair is still
correct and its mechanism has changed**: an industrial account on the SME branch is no longer
given an uninformative curve, it is given one that materially UNDERSTATES its price response, and
an arm that underestimates churn overprices. What has NOT been re-measured is whether the
£94,314 realised loss is still attributable to the routing rather than to the runaway; that is an
A/B, it is not this file, and it is filed with the ceiling's own record.
"""

import inspect

import pytest

from company.crm.churn_model import (
    CHURN_SEGMENTS,
    IC_BILL_STRESS_SENSITIVITY,
    IC_SEGMENT,
    RESI_SEGMENT,
    SME_SEGMENT,
)
from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.pricing.renewal_rate_chain import decide_renewal_rate
from company.pricing.value_based_renewal import renewal_margin_uplift, segments_for

#: C_IC3's actual consumption, the account that carried the loss.
INDUSTRIAL_KWH = 3_936_105.0
DOMESTIC_KWH = 4_004.0
BASE_RATE = 60.0


def _p_leave(segment, margin, kwh):
    return enriched_churn_estimate(
        BASE_RATE, BASE_RATE + margin,
        tenure_years=4.0, annual_consumption_kwh=kwh,
        bill_shock_count=0, renewal_year=2021, segment=segment,
    )


# ---------------------------------------------------------------------------
# 1. the defect itself, characterised
# ---------------------------------------------------------------------------













# ---------------------------------------------------------------------------
# 2. the segment reaches the model through every link
# ---------------------------------------------------------------------------









# ---------------------------------------------------------------------------
# 3. the fallback, so an uninformed caller is unchanged
# ---------------------------------------------------------------------------







def test_the_vocabulary_the_arm_checks_against_is_the_one_the_model_branches_on():
    """THE FAILURE MODE THAT MADE THIS SUBTLE. There are THREE segment vocabularies in
    this company: the churn model's (`resi`/`SME`/`I&C`), `segment_profitability`'s
    (`residential_credit`/`residential_ppm`/`sme`/`i_and_c`), and the cost tables' two.
    An arm that validated against the wrong one would match NOTHING and fall back for
    every account -- indistinguishable from the original defect, and silent.

    So the arm imports its vocabulary from the module that BRANCHES on it, and this test
    holds those two together.
    """
    from company.pricing import segment_profitability

    assert IC_SEGMENT in CHURN_SEGMENTS
    assert set(CHURN_SEGMENTS).isdisjoint(segment_profitability.KNOWN_SEGMENTS), (
        "the churn vocabulary and the profitability vocabulary now overlap; if they are "
        "being unified that is fine, but this test is the place that has to say so"
    )
    source = inspect.getsource(segments_for)
    assert "CHURN_SEGMENTS" in source, (
        "the mapping must validate against the churn model's own vocabulary; validating "
        "against any other set matches nothing and falls back silently"
    )
    # And the behavioural half, so this does not rest on reading source text: every value
    # the churn model branches on must survive the mapping unchanged.
    for known in CHURN_SEGMENTS:
        churn_segment, _ = segments_for(known, is_domestic=(known == RESI_SEGMENT))
        assert churn_segment == known




