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
# WHAT MAKES THIS ONE FALSIFIABLE AND NOT DECORATION: `populations_coincide` is
# False and the declared containment is EXACT, so the control fires the moment
# either side moves -- including, deliberately, when
# `D16_ageing_negative_population_is_unexcluded` lands and aligns them. That is
# the intent: the atom's completion should break its own declaration and force
# it to be rewritten, not slip past a control phrased loosely enough to cover
# both worlds.
SHARED_QUANTITY_CONTRACT: Dict[str, Dict[str, object]] = {
    "wrongful_dunning_exposure": {
        "phrase": "wrongful-dunning exposure",
        "published_by": {
            "detection": {
                "numerator_key": "n_false_flags",
                "denominator_key": "n_negatives",
                "rate_key": "false_flag_rate",
                "population": (
                    "NEVER-FLAGGABLE: cash arrived on or within the "
                    "reconciliation grace. Late-past-grace successes, unresolved "
                    "disputes and records with no `days_late` truth are EXCLUDED "
                    "and counted in `n_excluded` (D11's rule -- an invoice paid "
                    "three weeks late really WAS unpaid past grace, so flagging "
                    "it was correct)."
                ),
            },
            "ageing": {
                "numerator_key": "false_ageings",
                "denominator_key": "n_truly_current",
                "rate_key": "overstated_arrears_rate",
                "population": (
                    "TRULY-CURRENT AT as_of: every case whose truth bucket is "
                    "`current`. NO exclusion band at all -- D11's rule was "
                    "applied to the detection dimension only, so a payment that "
                    "arrived past grace is 'current' here and a flag on it "
                    "counts against the company."
                ),
            },
        },
        "populations_coincide": False,
        # The two denominators stand in an EXACT containment, and this is the
        # falsifiable half: ageing's population is detection's negatives plus
        # precisely the band detection excludes.
        "relationship": "ageing_denominator == detection_denominator + detection_n_excluded",
        "why_they_differ": (
            "MEASURED case by case, seed 7 / 400 customers (H27 Expert Hour "
            "2026-08-09), not inferred: 1062 == 782 + 280 exactly, and the two "
            "numerators share SEVEN cases. 94 of ageing's 101 false ageings land "
            "in the 280-case excluded band -- i.e. 93% of the ageing dimension's "
            "published wrongful-dunning exposure is composed of cases the "
            "detection dimension of the SAME instrument holds the company was "
            "RIGHT to flag -- and 14 of detection's 21 are not in ageing's "
            "numerator at all (the belief sides differ too: detection is "
            "EVER-FLAGGED, 439 cases; ageing is the `as_of` snapshot, 229)."
        ),
        "which_to_read": (
            "NEITHER ALONE, until D16. Detection's is the exposure after D11's "
            "exclusion rule; ageing's is the exposure if every past-grace "
            "payment is treated as current. They bound the answer rather than "
            "state it."
        ),
        "alignment_atom": "D16_ageing_negative_population_is_unexcluded",
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

    A registered dimension missing from `result` RAISES: a quantity that quietly
    stops being published from one side would otherwise turn this contract into
    a control that cannot fail."""
    out: Dict[str, Dict[str, object]] = {}
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
            per_dim[dim] = {
                "numerator": comp.get(keys["numerator_key"]),
                "denominator": comp.get(keys["denominator_key"]),
                "rate": comp.get(keys["rate_key"]),
                "n_excluded": comp.get("n_excluded"),
            }
        out[name] = per_dim
    return out
