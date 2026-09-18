"""The product gate's reach over the found book is counted on the TERM, and says which ratio binds.

THE DEFECT THESE FIRE ON (2026-09-18)
-------------------------------------
`site/data/value_arms.json` published, under the `reached` verdict:

    "The gate that used to refuse every won household is passable, so what limits this experiment
     now is book size, not eligibility."

inferred from a non-empty priced-account list. On the run carrying it, 1,475 of the 1,975 renewals
the world offered found accounts stopped at that same product gate, and the artefact said so two
keys away. A priced-account list establishes that the gate is PASSABLE; the eligibility question is
a ratio over TERMS and an account list is not a term count.

`renewal_funnel.product_label_by_account_class` was the only per-class reading of the gate on that
block, and its unit is the RECORD -- the product a record's own schedule builder stamps on its
OPENING term. Every boundary after the opening one is settled by the household's engagement roll,
and a passive roll settles `svt`, which the guard refuses. So the census that looked like the
gate's own reading structurally could not see it.

Filed: `docs/staging/SEAT_FINDING_THE_PRODUCT_GATE_CENSUS_ANSWERS_ON_THE_OPENING_TERM_WHILE_THE
_GUARD_REFUSES_PER_TERM_AND_ONE_ARTEFACT_SAYS_BOTH_2026-09-18.md`.

WHAT IS AND IS NOT ASSERTED HERE
--------------------------------
Nothing below pins today's answer. No control asserts that the found book's decision population is
small, that its priced share is high, or that the product mix is the binding constraint. Every leg
asserts a PROPERTY: that both readings are reachable, that a non-partition is refused rather than
divided, that an absent input fails closed, and that a share is never published over a population
whose membership is unknown. A run in which the method becomes the binding constraint turns the
first control's other branch green and none of them red.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.decisions_by_account_class import decisions_by_account_class

PROJECT = Path(__file__).resolve().parents[2]
#: The promoted run, read for ONE property only -- that the real feed reaches this module at all.
#: No figure from it is asserted: a control pinned to a published number goes red when the next
#: run is honestly different, which is the class this whole file was written out of.
THREE_ARM = PROJECT / "docs" / "observability" / "value_cycle_ab_s1_three_arm.json"


def _funnel(*, classes: dict, labels: dict | None = None) -> dict:
    """A funnel block in the producer's own shape, built from per-class stage counts.

    BOUND, NOT FOUND. The discriminating pairs below -- a run bounded by the product mix and one
    bounded by the method -- cannot both exist on one live roster, and a control that looked for
    them there would lose its subject to the next world repair. That has happened three times to
    the sibling controls in `test_the_renewal_funnel.py` and is recorded in their docstrings.
    """
    return {
        "by_account_class": {
            "available": True,
            "classes": {
                name: {
                    "renewals_the_world_offered": sum(stages.values()),
                    "accounts": row.get("accounts", 1),
                    "stages": stages,
                }
                for name, row in classes.items()
                for stages in [row["stages"]]
            },
        },
        "product_not_upliftable_by_tariff_type": labels if labels is not None else {},
    }


def _stages(**counts) -> dict:
    """Stage counts with every unnamed stage zero, so a fixture states only what it means to."""
    from company.pricing.value_based_renewal import FUNNEL_STAGES

    out = {stage: 0 for stage in FUNNEL_STAGES}
    for stage, count in counts.items():
        assert stage in out, "no such funnel stage: {}".format(stage)
        out[stage] = count
    return out


# ── the reading names WHICH ratio binds, and both answers are reachable ───────────────────────

def test_MUTATION_which_ratio_binds_is_read_off_the_numbers_and_both_answers_are_reachable():
    """NULL RUNG, and the reason this module is a reading rather than a restated conclusion.

    MUTATION: hardcode either branch of `_reading`'s `which` clause -> one half of this reds.

    The two halves differ ONLY in where the refusals sit. Same found book, same 1,000 boundaries
    offered, same 100 priced. In the first, 900 stop at the product gate and the decisions that
    existed are few, so the book's PRODUCT MIX binds and no book size moves it. In the second the
    decisions were nearly all there and the arm declined most of them, so the METHOD binds and it
    is ours. A page that reported the small reach without saying which of those it was is the
    sentence this replaces.
    """
    mix_bound = decisions_by_account_class(_funnel(classes={
        "won_by_the_funnel": {"stages": _stages(
            product_not_upliftable=900, priced=100)},
    }, labels={"'svt'": 900}))
    assert mix_bound["found"]["decisions_that_existed"] == 100
    assert mix_bound["found"]["priced_share_of_the_decisions_that_existed"] == 1.0
    assert mix_bound["found"]["decisions_share_of_the_renewals_offered"] == 0.1
    assert "PRODUCT MIX and not its size" in mix_bound["reading"]
    assert "METHOD" not in mix_bound["reading"].split("PRODUCT MIX")[0]

    method_bound = decisions_by_account_class(_funnel(classes={
        "won_by_the_funnel": {"stages": _stages(
            declined=900, priced=100)},
    }))
    assert method_bound["found"]["decisions_that_existed"] == 1000
    assert method_bound["found"]["priced_share_of_the_decisions_that_existed"] == 0.1
    assert method_bound["found"]["decisions_share_of_the_renewals_offered"] == 1.0
    assert "bounds this experiment is the METHOD" in method_bound["reading"]
    assert "PRODUCT MIX and not its size" not in method_bound["reading"]


def test_a_founder_only_run_carries_no_reading_about_the_found_book():
    """MUTATION: aggregate `found` over every class in the funnel instead of the found ones.

    Every founder renewal here is priced, so a `found` aggregate that swept the founder class in
    would report a fully-reached found book on a run that has no found account at all -- the
    flattering answer, produced by deleting one filter. The control asserts the honest shape
    instead: the classes it counted are NAMED, and the reading says it is a statement about the
    run rather than a result.
    """
    out = decisions_by_account_class(_funnel(classes={
        "founder_hand_authored": {"stages": _stages(priced=50)},
    }))
    assert out["available"] is True
    assert out["found"]["classes_counted"] == []
    assert out["found"]["priced"] == 0
    assert out["found"]["priced_share_of_the_decisions_that_existed"] is None
    assert "no class the company WON or DREW" in out["reading"]
    # ...and the founder class is still measured, because refusing to report it would be a
    # different defect: its 50 priced renewals ARE the run's only evidence the arm works at all.
    assert out["classes"]["founder_hand_authored"]["priced"] == 50


def test_a_found_book_offered_no_decision_at_all_is_not_read_as_the_method_failing():
    """MUTATION: report `priced_share_of_the_decisions_that_existed` as 0.0 for an empty population.

    A share over an empty population is undefined, and `0.0` reads as "the arm priced none of the
    decisions it was offered" -- a claim about the METHOD over a population that never existed.
    This is the fail-closed leg on the division itself.
    """
    out = decisions_by_account_class(_funnel(classes={
        "drawn_by_the_curriculum": {"stages": _stages(product_not_upliftable=400)},
    }, labels={"'svt'": 400}))
    assert out["found"]["decisions_that_existed"] == 0
    assert out["found"]["priced_share_of_the_decisions_that_existed"] is None
    assert "NOT ONE of them presented" in out["reading"]
    assert "NOT evidence the method fails" in out["reading"]


# ── fail closed: a non-partition, an absent input, an unattributable population ───────────────

def test_a_class_whose_stages_do_not_sum_to_its_own_total_is_named_and_withheld():
    """MUTATION: drop the partition check, or rescale to whichever total is larger.

    The stage counts are meant to partition the class's renewals. If they do not, every share over
    them is a share over a denominator that is not a quantity -- the "before dividing two numbers,
    say what each one counts" rule, applied to a population rather than to a rate. The class is
    NAMED and excluded; it is not silently divided and it is not folded into an "other" bucket.
    """
    funnel = _funnel(classes={
        "won_by_the_funnel": {"stages": _stages(priced=10)},
        "drawn_by_the_curriculum": {"stages": _stages(priced=10)},
    })
    funnel["by_account_class"]["classes"]["drawn_by_the_curriculum"][
        "renewals_the_world_offered"] = 999
    out = decisions_by_account_class(funnel)
    assert list(out["classes_excluded_and_why"]) == ["drawn_by_the_curriculum"]
    assert "not a partition" in out["classes_excluded_and_why"]["drawn_by_the_curriculum"]
    assert "drawn_by_the_curriculum" not in out["classes"]
    assert out["found"]["classes_counted"] == ["won_by_the_funnel"]
    # The exclusion reaches the READER, not just the field. A withheld class that is invisible in
    # the sentence is a silent cap, and a silent cap reads as full coverage.
    assert "drawn_by_the_curriculum" in out["reading"]
    assert "not a partition" in out["reading"]


@pytest.mark.parametrize("by_class", [
    None,
    {},
    {"available": False, "reason": "the roster would not import"},
    {"available": True},
    {"available": True, "classes": {}},
    # AVAILABLE AND PRESENT BUT NOT THE CLASSES BLOCK -- the shape an older artefact carries, and
    # the one a naive `.get("classes")` on a truthy parent would read as an empty population.
    {"available": True, "priced_accounts_by_class": {"won_by_the_funnel": ["PROS-1"]}},
])
def test_an_absent_per_class_split_refuses_rather_than_reconstructing_one(by_class):
    """MUTATION: fall back to the book-wide stage counts when the per-class split is missing.

    Every artefact before 2026-08-30 has no `by_account_class`. Reconstructing a per-class figure
    from a book-wide one would publish the book's shape as the found book's shape -- and the whole
    subject of this module is that those two differ. The refusal NAMES its reason, which is how a
    reader learns to go and measure rather than stopping.
    """
    funnel = {"by_account_class": by_class, "stages": [
        {"stage": "priced", "count": 100}], "renewals_the_world_offered": 1000}
    out = decisions_by_account_class(funnel)
    assert out["available"] is False
    assert "no per-class stage counts" in out["reason"]
    assert "NOT reconstructed" in out["reason"]
    assert "found" not in out and "classes" not in out


def test_refusals_carrying_no_decided_product_cannot_be_attributed_to_a_class_and_it_says_so():
    """MUTATION: drop `the_per_class_unresolved_bucket_is_not_established`, or set it from an
    empty breakdown.

    The funnel publishes the product-gate label breakdown BOOK-WIDE. When some of those refusals
    are our own record defect -- a term the world settled without deciding what product it was --
    those renewals are neither established inside the decision population nor outside it, and
    nothing in the artefact says whose class they belong to. Publishing the per-class shares
    without saying so states them as exact when they are lower bounds.

    BOTH DIRECTIONS. A run whose refusals are all real products the world settled owes no such
    caveat, and emitting one anyway would train a reader to ignore it.
    """
    classes = {"won_by_the_funnel": {"stages": _stages(
        product_not_upliftable=300, priced=100)}}

    owed = decisions_by_account_class(_funnel(
        classes=classes, labels={"'svt'": 150, "None": 150}))
    caveat = owed["the_per_class_unresolved_bucket_is_not_established"]
    assert caveat is not None and caveat["renewals"] == 150
    assert "BOOK-WIDE only" in caveat["why_it_cannot_be_split"]
    assert "lower bound" in owed["reading"]

    not_owed = decisions_by_account_class(_funnel(
        classes=classes, labels={"'svt'": 300}))
    assert not_owed["the_per_class_unresolved_bucket_is_not_established"] is None
    assert "lower bound" not in not_owed["reading"]


def test_the_unit_is_stated_on_the_block_and_names_what_it_is_not():
    """MUTATION: delete `unit`, or let it say "the account".

    The whole defect was two blocks of one artefact counted over different units with neither
    saying which. A block that states its unit and names the block holding the other one is what
    stops a reader inferring it -- "before measuring a thing, say what it is".
    """
    out = decisions_by_account_class(_funnel(classes={
        "won_by_the_funnel": {"stages": _stages(priced=5)}}))
    assert "the renewal TERM" in out["unit"]
    assert "NOT the record" in out["unit"]
    assert "product_label_by_account_class" in out["unit"]


def test_the_membership_rule_is_not_re_implemented_here():
    """MUTATION: replace the `decisions_that_existed` call with a slice of `FUNNEL_STAGES`.

    A slice at the product gate is a control pinned to today's guard ORDER -- the shape
    `decisions_that_existed`'s own docstring refuses, and this module's first draft. It was caught
    by reading that docstring, not by a test, which is why one exists now.

    The property: a class whose funnel carries a stage no membership rule places must be EXCLUDED
    here, with `decisions_that_existed`'s own reason, because it is the same denominator one level
    down. A local slice would keep answering, over a population silently missing a guard.

    AND THIS CONTROL FOUND THAT DEFECT RATHER THAN CONFIRMING ITS ABSENCE. `_class_funnel` built
    its stage list from `FUNNEL_STAGES` alone, so an unrecognised stage was dropped before
    `decisions_that_existed` could refuse it -- and the class's counts still summed, so the
    partition check was blind to it too. The fix passes every key the producer wrote.

    NO MONKEYPATCH OF `FUNNEL_STAGES`. Both this module and `decisions_that_existed` bind it with
    `from ... import`, so rebinding it on `value_based_renewal` reaches neither -- the first draft
    of this leg did exactly that and proved nothing. The stage is planted in the DATA, which is
    where a real producer would grow one.
    """
    funnel = _funnel(classes={"won_by_the_funnel": {"stages": _stages(priced=5)}})
    assert decisions_by_account_class(funnel)["available"] is True

    funnel["by_account_class"]["classes"]["won_by_the_funnel"]["stages"]["a_new_guard"] = 7
    funnel["by_account_class"]["classes"]["won_by_the_funnel"][
        "renewals_the_world_offered"] = 12
    out = decisions_by_account_class(funnel)
    assert list(out["classes_excluded_and_why"]) == ["won_by_the_funnel"], (
        "a stage with no membership rule left this module answering anyway -- it is counting over "
        "the stages it recognised, which is the defect `decisions_that_existed` refuses one level "
        "down")
    assert "a_new_guard" in out["classes_excluded_and_why"]["won_by_the_funnel"], (
        "the class is excluded but the reason does not name the stage that caused it, so the "
        "reader cannot tell a producer defect from a missing membership rule")
    assert out["found"]["classes_counted"] == []


# ── the real feed reaches it ──────────────────────────────────────────────────────────────────

def test_the_promoted_run_reaches_this_module_and_gets_a_reading():
    """MUTATION: any signature or key change that stops the real artefact being readable here.

    ONE property, and no published figure. The promoted artefact is the thing the page is built
    from; a module that works only on fixtures is the unreachable-witness shape. What is asserted
    is that it produces a reading over a non-empty population and that the reading names which
    ratio binds -- never which answer it gave, because the next honest run may give the other.
    """
    # ONE LOADER, NOT A TEXT READ. `path.read_text()` here made this function a row in
    # `tools/substring_source_scan_census` -- the census cannot tell a JSON read from a read of
    # Python source once any `.py` literal appears elsewhere in the file, and this file names
    # several in its docstrings. It was invisible locally because the census walks `git ls-files`
    # and the file was untracked; the pre-commit gate, which reads the tree the commit WOULD
    # create, found it. `json.load` over the handle is the honest shape and the remedy.
    with THREE_ARM.open(encoding="utf-8") as handle:
        funnel = json.load(handle)["renewal_funnel"]["value_arm"]
    out = decisions_by_account_class(funnel)
    assert out["available"] is True, out.get("reason")
    assert out["found"]["classes_counted"], "the promoted run names no found class"
    assert out["found"]["renewals_the_world_offered"] > 0
    assert out["classes_excluded_and_why"] == {}
    assert ("PRODUCT MIX and not its size" in out["reading"]
            or "bounds this experiment is the METHOD" in out["reading"])
