"""The SHARED-QUANTITY CONTRACT: a real-world quantity published by more than
one dimension must DECLARE the relationship between those dimensions'
populations, and the declaration must be MEASURED against a real scored run.

Lifted out of `tools/couple_w2_11_d5.py` on 2026-08-09, the tick that minted it,
for the reason the register exists at all: it is a CLASS register (R10), and a
class register living inside the one triad that happened to trip the defect is
how the previous ones ended up triad-local. Any coupled pair that publishes a
named quantity from two dimensions registers here.

R15 note for anyone adding an entry: `populations_coincide` and `relationship`
are DECLARATIONS, and a declaration nothing measures is a switch, not a control.
The control lives in `tests/tools/test_couple_w2_11_d5.py` and derives both sides
from the two SCORERS' own components -- it never recomputes either, which would
be a harness copy checking a harness copy.
"""

from typing import Dict, Mapping

# ---------------------------------------------------------------------------
# THE SHARED-QUANTITY CONTRACT (H27 Expert Hour 2026-08-09, the R10 half)
# ---------------------------------------------------------------------------
# WHY THIS EXISTS. The instance: this triad publishes "the wrongful-dunning
# exposure" TWICE, in one output block, as two numbers 3.5x apart --
# `detection.false_flag_rate` 0.0269 (21 of 782) and `ageing.
# overstated_arrears_rate` 0.0951 (101 of 1062), sharing SEVEN cases -- while
# `background.gap_metric` asserted in prose that they were "literally the same
# numerator". Nothing compared them, so nothing could notice. A reader who takes
# either as "what this company's wrongful dunning costs" is misled by whichever
# one they read first.
#
# THE CLASS is every real-world quantity this repo publishes from MORE THAN ONE
# dimension. Two dimensions measuring the same thing over different populations
# is not itself a defect -- here it is the correct consequence of D11's exclusion
# rule, which detection has and ageing does not -- but an UNDECLARED, UNMEASURED
# divergence is, and so is a declaration that says "the same" when the cases say
# otherwise. R10: the fix is not to reword the two notes.
#
#     a quantity published by two or more dimensions must DECLARE the
#     relationship between their populations, and the declaration must be
#     MEASURED against a real scored run -- not asserted in a comment
#
# The control in `tests/tools/test_couple_w2_11_d5.py` derives each side from the
# components the two SCORERS actually returned (`gap_metric.ageing_gap` and
# `gap_metric.detection_measures` -- two independent measurements over
# independently built populations, so this is not a value checked against
# itself), and it also sweeps the RENDERED summaries for the quantity's own
# phrase, so a third dimension that starts publishing it without registering
# here fails rather than joining the ambiguity silently.
#
# WHAT MAKES THIS FALSIFIABLE AND NOT DECORATION: every declaration below is
# measured against a real scored run, in both directions. The first version of
# this entry declared `populations_coincide: False` and an EXACT containment
# precisely so that `D16_ageing_negative_population_is_unexcluded` landing would
# BREAK its own declaration and force this rewrite rather than slipping past a
# control phrased loosely enough to cover both worlds. D16 landed on 2026-08-09
# and it did break; what follows is the rewrite, and it carries the same
# property -- it is exact, so the next move on either side fails it.
#
# WHAT D16 SETTLED, AND THE HALF IT DID NOT SETTLE THE EASY WAY. Carrying D11's
# exclusion across made the two DENOMINATORS the same population -- not merely
# the same size: the identical set of cases, measured. It did NOT make the two
# rates one number, and that residual is the finding rather than leftover work:
# the two BELIEF sides ask different questions and always did.
#
#   * detection asks: did the company EVER chase this invoice? Wrongful dunning
#     is an EVENT. A customer chased in month one and dropped from the report by
#     month three was still wrongly chased, so the population is EVER-FLAGGED.
#   * ageing asks: does the company's open-item report STILL show this invoice
#     overdue at `as_of`? That is a MISSTATEMENT question -- what a provision, a
#     board pack or a bad-debt charge is built from -- and the `as_of` snapshot
#     is the right population for it.
#
# Aligning the belief sides too would have destroyed one of the two measures to
# manufacture agreement between two numbers. So the DENOMINATORS are aligned and
# the NAME is not shared: "the wrongful-dunning exposure" has exactly ONE
# publisher, and the ageing rate is renamed to what it measures. `phrase_
# published_by` is the declaration; the sweep in
# `tests/tools/test_couple_w2_11_d5.py` measures it against the RENDERED text a
# reader actually sees, and a dimension that starts printing the phrase without
# registering fails.
SHARED_QUANTITY_CONTRACT: Dict[str, Dict[str, object]] = {
    "wrongful_dunning_exposure": {
        "phrase": "wrongful-dunning exposure",
        # THE NAME HAS ONE OWNER (D16). A second dimension printing this phrase
        # affirmatively is the defect this register was minted for.
        "phrase_published_by": ["detection"],
        # A dimension may MENTION the phrase to disclaim it -- and the ageing
        # dimension must, because a reader who remembers the old label needs to
        # be told it moved. A bare substring ban would refuse that honest
        # sentence: the AO2 "none" shape, which this repo has now been bitten by
        # twice. The disclaimer's FORM is therefore registered and checked.
        "phrase_disclaimed_by": {
            "ageing": "NOT the wrongful-dunning exposure",
        },
        "published_by": {
            "detection": {
                "quantity_name": "the wrongful-dunning exposure",
                "numerator_key": "n_false_flags",
                "denominator_key": "n_negatives",
                "rate_key": "false_flag_rate",
                "numerator_cases_key": "detection_false_flags",
                "denominator_cases_key": "never_flaggable",
                "population": (
                    "NEVER-FLAGGABLE: cash arrived on or within the "
                    "reconciliation grace. Late-past-grace successes, unresolved "
                    "disputes and records with no `days_late` truth are EXCLUDED "
                    "and counted in `n_excluded` (D11's rule -- an invoice paid "
                    "three weeks late really WAS unpaid past grace, so flagging "
                    "it was correct). BELIEF SIDE: EVER-FLAGGED."
                ),
            },
            "ageing": {
                "quantity_name": "the ageing-report overstatement at as_of",
                "numerator_key": "false_ageings",
                "denominator_key": "n_truly_current",
                "rate_key": "overstated_arrears_rate",
                "numerator_cases_key": "ageing_false_ageings",
                "denominator_cases_key": "ageing_truly_current",
                "population": (
                    "THE SAME never-flaggable set, since D16: a case is scored "
                    "here only if it truly failed or its cash arrived within "
                    "grace, and the band in between is EXCLUDED and counted in "
                    "`n_excluded` under the same rule the detection dimension "
                    "applies. BELIEF SIDE: the `as_of` open-item SNAPSHOT, which "
                    "is why this is a different quantity and not the same one "
                    "measured twice."
                ),
            },
        },
        # DENOMINATORS: the same population, and the control checks SET identity
        # rather than equal counts -- two different 782-case populations would
        # pass a count check and be exactly the defect this register exists for.
        "populations_coincide": True,
        # NUMERATORS: a STRICT subset, in the direction the belief sides imply.
        # An invoice the ageing report shows overdue at `as_of` was necessarily
        # chased at some point up to `as_of`; the converse fails for every case
        # the company chased and then dropped from the report.
        "relationship": (
            "ageing_denominator_cases == detection_denominator_cases (identical "
            "sets) AND ageing_numerator_cases STRICT SUBSET OF "
            "detection_numerator_cases"
        ),
        "why_they_differ": (
            "MEASURED case by case at seeds 7/11/23 and grace windows 5 and 12 "
            "(atom D16, 2026-08-09), not inferred. Seed 7 / 400 customers: the "
            "denominators are now the identical 782-case set (they were 1062 vs "
            "782 before the alignment), and the numerators are 7 of ageing's "
            "inside detection's 21 -- every case the ageing report still "
            "overstates was chased, and 14 more were chased and then dropped "
            "from the report before `as_of`. The residual is ENTIRELY the belief "
            "side: EVER-FLAGGED vs the `as_of` snapshot. Before the alignment "
            "the gap was 3.5x and mostly denominator: 94 of ageing's 101 false "
            "ageings sat in the 280-case band detection excludes as legitimately "
            "chaseable."
        ),
        "which_to_read": (
            "READ DETECTION'S for wrongful dunning -- it is the only publisher "
            "of that quantity, and an event that happened to a customer does not "
            "un-happen because the report moved on. READ AGEING'S for the "
            "report's overstatement TODAY, which is what a provision or a board "
            "pack is built from. They are two questions, and since D16 they are "
            "two names."
        ),
        # No atom owns an alignment any more: the denominators ARE aligned and
        # the numerator divergence is declared, measured and deliberate. `None`
        # is the honest value and the control requires it to be one or the other
        # -- an unowned, undeclared divergence is what this register forbids.
        "alignment_atom": None,
    },
}


def shared_quantity_measurements(result: Mapping) -> Dict[str, Dict[str, object]]:
    """Derive, from ONE scored triad result, every `SHARED_QUANTITY_CONTRACT`
    quantity as it was actually published by each dimension: numerator,
    denominator and rate, side by side.

    This exists so the comparison is a MEASUREMENT a control (and a reader) can
    make, rather than a sentence in a note. It reads only the components the
    dimension's own scorer returned -- it never recomputes either side, which
    would be a harness copy checking a harness copy (R15's tautology pattern).

    Where the result carries the scorers' own case SETS (`result["sets"]`, which
    `score_triad` returns for exactly this purpose), each side also gets the
    actual CASES behind its numerator and denominator. Counts alone cannot tell
    two different 782-case populations apart from one shared one -- and "the
    same size" passing for "the same population" is the shape of the very defect
    this register was minted for (D16).

    A registered dimension missing from `result` RAISES: a quantity that quietly
    stops being published from one side would otherwise turn this contract into
    a control that cannot fail. A declared case key missing from `result["sets"]`
    RAISES for the same reason -- silently degrading to a count comparison would
    weaken the control precisely when a set stopped being published."""
    out: Dict[str, Dict[str, object]] = {}
    sets = result.get("sets") if hasattr(result, "get") else None
    for name, spec in SHARED_QUANTITY_CONTRACT.items():
        per_dim: Dict[str, object] = {}
        for dim, keys in spec["published_by"].items():   # type: ignore[union-attr]
            if dim not in result:
                raise KeyError(
                    f"SHARED_QUANTITY_CONTRACT[{name!r}] names dimension {dim!r}, "
                    "which this result does not publish. Either the dimension was "
                    "removed and the register is stale, or the result is partial "
                    "-- comparing what is left would be a control that cannot fail."
                )
            comp = result[dim].components
            side: Dict[str, object] = {
                "numerator": comp.get(keys["numerator_key"]),
                "denominator": comp.get(keys["denominator_key"]),
                "rate": comp.get(keys["rate_key"]),
                "n_excluded": comp.get("n_excluded"),
                "quantity_name": keys.get("quantity_name"),
                "numerator_cases": None,
                "denominator_cases": None,
            }
            if sets is not None:
                for role in ("numerator", "denominator"):
                    set_key = keys.get(f"{role}_cases_key")
                    if set_key is None:
                        continue
                    if set_key not in sets:
                        raise KeyError(
                            f"SHARED_QUANTITY_CONTRACT[{name!r}]/{dim} declares "
                            f"its {role} cases as {set_key!r}, which this "
                            "result's `sets` does not carry. Falling back to a "
                            "count comparison would quietly downgrade a set "
                            "identity check into one two different populations "
                            "of the same size would pass."
                        )
                    side[f"{role}_cases"] = frozenset(sets[set_key])
            per_dim[dim] = side
        out[name] = per_dim
    return out
