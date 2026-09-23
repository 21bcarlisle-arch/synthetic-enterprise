"""The knee that decides whether consumption reaches the churn belief at all must say where it came from.

REUSE: tests/company/test_the_bill_stress_threshold_carries_its_origin.py
CLASS: TEST
INDEX: searched "origin", "cited", "constant", "churn", "bill_stress", "threshold", "provenance".
       `tests/architecture/test_a_domain_constant_carries_its_origin.py` is the nearest and is a
       COUNT over 293 constants with a ceiling of 255 and a floor of 208 — its own docstring says
       so. A total can be paid anywhere: documenting two constants in `company/billing/` buys back
       the headroom to strip this one, and the ratchet stays green throughout. That hole is why
       this file is named for ONE constant. The three churn test modules
       (`test_phase_my_churn_model.py`, `test_phase_nk_churn_model_performance.py`,
       `test_phase_nq_churn_recalibration.py`) all exercise the estimator's OUTPUT and none asks
       anything about provenance.
EVALUATED: no library. The scan already exists in `tools.domain_constant_origins` and is imported
       rather than re-implemented — a second parse of the same comments is a second artefact that
       can drift from the first, which is the failure `_published_departure_rates` names.

WHAT EACH TEST NAMES AS ITS OWN DEFECT (CONTROLS_THAT_CANNOT_FAIL)

  * `test_the_bill_stress_threshold_DECLARES_AN_ORIGIN` — the defect is the £150-CAC shape on the
    one constant in this repository best placed to repeat it. `BILL_STRESS_THRESHOLD_GBP` is the
    ONLY place `annual_consumption_kwh` reaches `estimate_churn_probability`, and 235 of 244
    supply legs sit below it, so it decides whether 96% of the book gets a churn belief with any
    size term at all. Until 2026-09-22 it carried an empirical claim — *"the threshold where
    empirically customers start actively switching"* — and cited nothing.
  * `test_the_named_gap_POINTS_AT_A_READING_THAT_EXISTS` — the defect is a gap filed and then
    orphaned. This repository's own recurring shape is a sourced anchor that reaches no code and a
    gap declared in two places that do not point at each other (`saas/opex_ledger.py`'s £55; the
    household-amplitude gap declared twice before 2026-09-03). A comment naming a finding file is
    worth exactly as much as the file being there and still being about this constant.

WHAT THIS DELIBERATELY DOES NOT DO: check that the citation is TRUE. No scan can —
`tools/domain_constant_origins.py` says so in terms. The finding itself is the reading, and it is
`docs/market_research/is_there_a_bill_level_at_which_switching_rises.md`.

NOT KEYED TO 3000.0. The value may move the moment someone sources one, and neither test here goes
red when it does — a control pinned to today's answer reds when the code becomes more honest, which
is exactly backwards. What may not happen is the number losing its provenance again.

HOW LEG 2 READS THE BLOCK, AND WHY IT IS NOT A REGEX OVER THE MODULE (re-done 2026-09-23). This
leg first re-read `company/crm/churn_model.py` and regexed for the `#:` run above the constant.
That is a substring scan over Python source, and `tests/architecture/test_a_control_reads_python_as_code.py`
refused the commit for it — correctly: it was a SECOND parser of the same comments, beside the one
in `tools.domain_constant_origins`, and the EVALUATED note above already said not to write one.
The usual remedy, `tools/python_code_text.py`, does not apply here and saying why matters:
`searchable()` blanks comments, and the comment IS this leg's subject. So the fix was to give the
existing AST-anchored reader a `comment` field and ask it. `_comment_block` is anchored to the
assignment's own `lineno`, which also retires the hazard recorded below by construction.

R15 MUTATIONS, re-run 2026-09-23 against the new mechanism, each applied to a COPY in a temp root
handed to `scan(root)` — never to the shared tree, because a killed sweep leaves its mutation
behind in a tree three lanes write. `(leg1, leg2)`:
  * baseline → `(True, True)`.
  * delete the `#:` block above `BILL_STRESS_THRESHOLD_GBP` → `(False, False)`, both RED.
  * replace the block with a bare `# picked` → `(False, False)`, both RED.
  * repoint the finding path INSIDE that block → `(True, False)`. **This is the pair's whole
    justification**: leg 1 cannot see it, because `_CITED` matches any `docs/` path and the
    repointed one is still a `docs/` path. A constant can cite *a* reading while pointing at the
    wrong one, and only leg 2 fires on that.

ONE MUTATION SURVIVED AND IT IS AN EQUIVALENCE, NOT A HOLE — established rather than assumed,
because the flattering reading was available. Stripping the block down to `#: see <the finding>`
leaves `(True, True)`. Leg 1 stays green because `_CITED` is `docs/|Ofgem|DESNZ|...`, so a comment
naming a reading under `docs/` IS a citation by that classifier's own definition; there is nothing
left to detect. The mutation does not express a defect.

SUPERSEDED, kept because it is why the path is named in two places. The 2026-09-22 record said the
repoint mutation survived its first run and that the control was not the reason: it was written as
a first-occurrence replace over the whole module, and the first occurrence is in the module
docstring rather than in the constant's block, so leg 2 was right to stay green and the mutation
had missed its target. Under the AST-anchored read that trap no longer exists — the block is
located by lineno, not by ordinal — but the lesson stands for any control that greps a file for
something that lives in one part of it.
"""
from __future__ import annotations

from pathlib import Path

from tools.domain_constant_origins import ORIGINS, scan

PROJECT = Path(__file__).resolve().parent.parent.parent

CONSTANT = "BILL_STRESS_THRESHOLD_GBP"
MODULE = "company/crm/churn_model.py"

#: The reading the constant's own comment names. Held here as well as there so that the two can
#: disagree — a path that exists in the comment and nowhere else is the orphan this leg is for.
FINDING = "docs/market_research/is_there_a_bill_level_at_which_switching_rises.md"


def _row() -> dict:
    """The scan's row for the constant, or a failure naming what the scan found instead.

    FAIL-CLOSED ON AN EMPTY SCAN. A scan that breaks returns nothing, and `next(..., None)` would
    then read as "no row" rather than as "the instrument is broken" — the population-floor lesson
    from `test_a_domain_constant_carries_its_origin.py`, one control down.
    """
    found = scan()
    assert found, "the origin scan returned NOTHING — the instrument is broken, not the code"
    rows = [r for r in found if r["name"] == CONSTANT and r["path"] == MODULE]
    assert len(rows) == 1, (
        f"expected exactly one {CONSTANT} in {MODULE}, found {len(rows)}. Either the constant has "
        f"moved (update this control and say where it went) or it now carries two values, which "
        f"`test_no_domain_constant_NAME_carries_two_values` is the one to read."
    )
    return rows[0]


def test_the_bill_stress_threshold_DECLARES_AN_ORIGIN() -> None:
    """The one constant deciding whether consumption reaches the churn belief at all.

    The architecture ratchet counts 293 constants against a ceiling; a total can be paid elsewhere
    while this one is stripped. This leg cannot be.
    """
    row = _row()
    assert row["origin"] in ORIGINS, (
        f"{MODULE}::{CONSTANT} declares no origin. It is the ONLY route by which "
        f"`annual_consumption_kwh` reaches `estimate_churn_probability`, and on the 2026-09-22 "
        f"book 235 of 244 supply legs sit below it — so it decides whether 96% of the book carries "
        f"any size term in its churn belief. A citation, a labelled belief something grades, or a "
        f"named simplification with what it would take to do properly. Not a bare number, and not "
        f"an empirical claim with no source: it carried one of those until 2026-09-22 and "
        f"{FINDING} is the pass that refuted it."
    )


def test_the_named_gap_POINTS_AT_A_READING_THAT_EXISTS() -> None:
    """A gap filed and then orphaned is a gap nobody can act on.

    Both directions are asserted: the constant's comment names the finding, and the finding is on
    disk and still about this constant. Either half alone passes while the pair has come apart.
    """
    block = _row()["comment"]
    assert block.strip(), (
        f"{CONSTANT} has no comment block immediately above it. `_comment_block` walks UP "
        f"from the assignment and stops at the first non-comment line, so a constant declared "
        f"directly beneath another shares nothing and reads as undocumented."
    )
    assert FINDING in block, (
        f"{CONSTANT}'s origin block no longer names {FINDING}. The block is where a reader is sent "
        f"for the evidence; a gap that names no reading is the £150-CAC shape with a comment on it."
    )

    finding = PROJECT / FINDING
    assert finding.is_file(), (
        f"{MODULE}::{CONSTANT} names {FINDING} as its evidence and that file is not on disk. This "
        f"repository's recurring shape is a sourced anchor that reaches no code and a gap declared "
        f"in two places that do not point at each other; this is the same shape inverted."
    )
    assert CONSTANT in finding.read_text(encoding="utf-8"), (
        f"{FINDING} exists but no longer mentions {CONSTANT}. The constant cites a reading that is "
        f"no longer about it, which reads to a scanner exactly like a discharged debt."
    )
