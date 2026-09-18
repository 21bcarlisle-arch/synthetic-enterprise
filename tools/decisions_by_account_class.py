"""The decision population split by how each account joined the book — the PER-TERM unit.

WHY THIS EXISTS (2026-09-18)
----------------------------
`renewal_funnel.product_label_by_account_class` answers "what does the arm's product gate read for
each class of account" over the **RECORD**. The guard is applied per **TERM**. Those are different
censuses and one artefact published both under one verdict field:

    product_not_upliftable_by_tariff_type   {"'svt'": 2490}    <- 2,490 of 2,824 terms refused
    product_label_by_account_class.legs     all 232 legs "fixed", the_guard_admits_it: true
    ...a_found_account_can_reach_the_product_gate              true, 145 found accounts

All three computed correctly. The record's schedule builder stamps the product on its **opening**
term, and since the 2026-09-16 gas repair that is `"fixed"` for every record on the roster; every
term boundary AFTER the opening one is settled by the household's own engagement roll, and a
passive roll settles `svt`, which the guard refuses. So a census over records cannot see the gate
that stops 88% of the terms — and the derived verdict, read as though it were about the gate's
own unit, licensed "grow the book" when the honest claim is that the reachable surface is about a
third of a domestic book and that is market structure
(`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`, its closing paragraph).

Filed as `docs/staging/SEAT_FINDING_THE_PRODUCT_GATE_CENSUS_ANSWERS_ON_THE_OPENING_TERM_WHILE_THE
_GUARD_REFUSES_PER_TERM_AND_ONE_ARTEFACT_SAYS_BOTH_2026-09-18.md`.

WHAT THIS COUNTS, SAID BEFORE ANYTHING IS DIVIDED
-------------------------------------------------
The unit is the **renewal TERM**, and the population is the one the funnel itself counts — one row
per call of `decide_renewal_rate`. For each class of account it reports the terms at which a
per-customer renewal decision EXISTED, and the share of those the arm priced.

THE MEMBERSHIP RULE IS NOT RE-IMPLEMENTED HERE. `decisions_that_existed` owns it, and this module
calls it once per class over that class's own stage counts. The first draft of this module sliced
`FUNNEL_STAGES` at the product gate and counted "stages after it" — which is a control pinned to
today's guard ORDER, the exact shape `decisions_that_existed`'s own docstring refuses. One name,
one answer: if a stage moves or is added, one membership rule moves with it.

THE TWO RATIOS THIS EXISTS TO KEEP APART, because they license opposite decisions:

  priced / decisions_that_existed       -- about the METHOD. Did the arm price the decisions that
                                           were there to be made, for the households it FOUND?
  decisions_that_existed / offered      -- about the BOOK'S PRODUCT MIX. How much of what the
                                           world put in front of the arm was a decision at all?

A book twice the size scales both sides of the second ratio equally and cannot move it. That is
why "what limits this experiment is book size, not eligibility" cannot be concluded from a large
priced count, and it is the clause this module was written to delete from the live page.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here asserts that the found book's decision
population is small, or that its priced share is high. Feed it a funnel whose found classes reach
the arm at the founder classes' rate and the reading says the product mix is not what bounds this;
feed it one where the arm declines most decisions it was offered and the reading says the method
is what bounds it. The verdict changes when the run changes and nobody edits a sentence.

FAIL CLOSED, IN THREE PLACES, EACH NAMED
----------------------------------------
1. No `by_account_class`, or it is unavailable -> `available: False` with the reason. NOT
   reconstructed from the book-wide totals: a per-class figure guessed from a book-wide one is the
   fail-silent shape this whole family of repairs exists to close.
2. A class whose stage counts do not sum to its own `renewals_the_world_offered`, or whose funnel
   carries a stage no membership rule places, -> the class is NAMED in `classes_excluded_and_why`
   WITH ITS OWN REASON and every share it would contribute is withheld. A share over a denominator
   that is not a partition is not a quantity; and the two exclusion causes ask for opposite work,
   so they are not folded into one bucket.
3. The funnel publishes `product_not_upliftable_by_tariff_type` BOOK-WIDE only. When that
   breakdown carries refusals that are our own record defect, those terms are neither established
   inside the decision population nor outside it, and they cannot be attributed to a class at all.
   The block then carries `the_per_class_unresolved_bucket_is_not_established` with the count,
   rather than publishing per-class shares as though the ambiguity were resolved.

R12: a diagnostic. No class's decision population is a target, and specifically this is not a cue
to relax the product gate so the found book's population gets bigger.

REUSE
-----
REUSE: tools/decisions_by_account_class.py
CLASS: CUSTOM
INDEX: searched "decisions by account class", "account class", "decision population", "per term",
       "product gate", "found account", "priced share", "funnel by class".
       `tools/decisions_that_existed.py` owns the membership rule and IS CALLED here, once per
       class, never restated. It cannot do this job itself: it takes ONE funnel's stage list and
       has no notion of an account class, and giving it one would put the roster's vocabulary
       inside a module whose whole subject is the arm's stage vocabulary.
       `tools/product_gate_refusal.py` is reached TRANSITIVELY through the above for the
       defect/structural split; imported directly here only to establish whether a per-class
       unresolved bucket is owed.
       `tools/run_value_cycle_ab.funnel_by_account_class` is the PRODUCER of the per-class stage
       counts this reads and deliberately interprets nothing; `product_label_by_account_class`
       beside it is the RECORD-unit census this one exists to be distinguished from, and both now
       ship, each naming its own unit.
       `tools/generate_value_arms_data._who_the_method_has_priced` is the PUBLISHER and calls this
       too, for the reason `product_gate_refusal` records: the page renders artefacts weeks old,
       so a reading computed only at run time reaches the reader stale or not at all.
"""
from __future__ import annotations

from company.pricing.value_based_renewal import FUNNEL_STAGES
from tools.decisions_that_existed import decisions_that_existed
from tools.product_gate_refusal import refusal_breakdown

#: The classes that mean the company FOUND this account rather than started with it. Spelled from
#: the world's own `acquisition_type` vocabulary, which `run_value_cycle_ab` writes into the
#: artefact — a prefix test on the id would read a renamed id as a founder account without saying
#: so, which is the reason that module keyed on the field in the first place.
#:
#: NOT imported from `run_value_cycle_ab`: this module is on the site publisher's import graph and
#: that one drags `simulation` onto it. The pairing is held by
#: `tests/tools/test_the_found_classes_have_one_spelling.py`, which compares the two tuples rather
#: than trusting either.
FOUND_ACCOUNT_CLASSES: tuple[str, ...] = ("won_by_the_funnel", "drawn_by_the_curriculum")


def _class_funnel(row: dict) -> dict:
    """One class's stage counts, in the shape `decisions_that_existed` reads.

    EVERY KEY THE PRODUCER WROTE IS PASSED THROUGH, not just the stages this module's import of
    `FUNNEL_STAGES` happens to know. A first draft built the list from `FUNNEL_STAGES` alone and
    therefore DROPPED a stage the producer had grown — silently, and the class's renewals still
    summed, so the partition check could not see it either. `decisions_that_existed._unknown_stages`
    is the one place that refusal belongs, and it can only fire on a stage it is shown. Caught by
    `test_the_membership_rule_is_not_re_implemented_here`, which was written to assert that the
    refusal propagates and found that it did not.

    `product_not_upliftable_by_tariff_type` is deliberately ABSENT: the funnel publishes that
    breakdown book-wide only, and handing a class the book's copy would attribute the whole
    book's unlabelled refusals to every class in turn. The consequence — that no per-class
    unresolved bucket can be computed — is published at the top level instead, where it is one
    statement about the run rather than a wrong number repeated per class.
    """
    stages = row.get("stages") or {}
    names = list(FUNNEL_STAGES) + [s for s in stages if s not in FUNNEL_STAGES]
    return {
        "stages": [{"stage": stage, "count": stages.get(stage, 0)} for stage in names],
        "renewals_the_world_offered": row.get("renewals_the_world_offered"),
        "priced_share_of_renewals_offered": row.get("priced_share_of_its_own_renewals"),
    }


def decisions_by_account_class(funnel: dict) -> dict:
    """Per-TERM decision population and priced share, split by how the account joined the book.

    Takes the `renewal_funnel.<arm>` block. Returns, always:
      available            -- False when the funnel carries no usable per-class stage counts
      reason               -- why, when unavailable
      unit                 -- what one row of the population IS, stated rather than implied
      classes              -- per class: offered, decisions_that_existed, priced, declined, shares
      found                -- the same aggregated over `FOUND_ACCOUNT_CLASSES`
      classes_excluded_and_why -- class -> reason, and their shares withheld
      the_per_class_unresolved_bucket_is_not_established -- the fail-closed caveat, or None
      reading              -- the sentence, composed from the counts above
    """
    by_class = funnel.get("by_account_class") or {}
    rows = by_class.get("classes") if by_class.get("available") else None
    if not isinstance(rows, dict) or not rows:
        return {
            "available": False,
            "reason": (
                "this run's funnel carries no per-class stage counts "
                "(`renewal_funnel.<arm>.by_account_class.classes`), so the decision population "
                "cannot be split by how each account joined the book. It is NOT reconstructed "
                "from the book-wide totals: those are true of the book as a whole and say nothing "
                "about which population sits behind each stage, which is the whole question."),
        }

    # EXCLUDED CLASSES CARRY THEIR OWN REASON, not one shared bucket. "its stage counts are not a
    # partition" and "the arm grew a guard no membership rule places" ask for opposite work -- the
    # first is a producer defect, the second is a rule owed in
    # `decisions_that_existed.STAGE_PRESENTED_A_DECISION` -- and a single list would tell the
    # reader neither.
    excluded: dict[str, str] = {}
    classes: dict[str, dict] = {}
    for name, row in sorted(rows.items()):
        if not isinstance(row, dict):
            excluded[str(name)] = (
                "this class's entry is not a mapping, so it carries no stage counts to read")
            continue
        offered = row.get("renewals_the_world_offered")
        stages = row.get("stages") or {}
        staged = sum(v for v in stages.values() if isinstance(v, int))
        if not isinstance(offered, int) or staged != offered:
            # A SHARE OVER A NON-PARTITION IS NOT A QUANTITY. Named and withheld, never rescaled
            # to whichever of the two totals happens to be bigger.
            excluded[str(name)] = (
                "its stage counts sum to {staged} and it reports {offered!r} renewals offered, so "
                "they are not a partition of its own population and no share over them would be a "
                "quantity".format(staged=staged, offered=offered))
            continue
        population = decisions_that_existed(_class_funnel(row))
        if not population.get("available"):
            excluded[str(name)] = population.get("reason") or (
                "the decision population could not be derived for this class and no reason was "
                "recorded")
            continue
        classes[str(name)] = {
            "renewals_the_world_offered": offered,
            "decisions_that_existed": population["decisions_that_existed"],
            "priced": population["priced"],
            "declined": population["declined"],
            "priced_share_of_the_decisions_that_existed": population[
                "priced_share_of_the_decisions_that_existed"],
            "decisions_share_of_the_renewals_offered": (
                round(population["decisions_that_existed"] / offered, 4) if offered else None),
            "accounts": row.get("accounts"),
        }

    found_names = [n for n in FOUND_ACCOUNT_CLASSES if n in classes]
    found_offered = sum(classes[n]["renewals_the_world_offered"] for n in found_names)
    found_population = sum(classes[n]["decisions_that_existed"] for n in found_names)
    found_priced = sum(classes[n]["priced"] for n in found_names)
    found = {
        # NAMED, not inferred from what happened to be in `classes`: a run whose roster carries no
        # won or drawn account at all and one whose classes were dropped as non-partitions are the
        # same empty sum and opposite facts.
        "classes_counted": found_names,
        "classes_expected": list(FOUND_ACCOUNT_CLASSES),
        "renewals_the_world_offered": found_offered,
        "decisions_that_existed": found_population,
        "priced": found_priced,
        "priced_share_of_the_decisions_that_existed": (
            round(found_priced / found_population, 4) if found_population else None),
        "decisions_share_of_the_renewals_offered": (
            round(found_population / found_offered, 4) if found_offered else None),
    }

    breakdown = refusal_breakdown(funnel.get("product_not_upliftable_by_tariff_type"))
    undecided = breakdown["defect_count"] if breakdown["available"] else 0
    unresolved = {
        "renewals": undecided,
        "why_it_cannot_be_split": (
            "{:,} of this run's product-gate refusals carry no decided product at all, which is "
            "OUR record defect rather than the market's shape -- but the funnel publishes that "
            "breakdown BOOK-WIDE only, so not one of them can be attributed to a class. The "
            "per-class decision populations above therefore EXCLUDE a population of unknown "
            "class-membership, and the shares are lower bounds on the classes that own them."
        ).format(undecided),
    } if undecided else None

    return {
        "available": True,
        "unit": (
            "the renewal TERM -- one row per call of `decide_renewal_rate`, which is the "
            "population the funnel itself counts. NOT the record: a record's schedule builder "
            "stamps a product on its OPENING term and the household's own engagement roll settles "
            "every boundary after it, so a census over records cannot see the gate that refuses "
            "most terms. `product_label_by_account_class` beside this block is the RECORD-unit "
            "census and its verdict field is named for that unit."),
        "what_this_is": (
            "The renewals at which a per-customer renewal-pricing decision actually EXISTED, "
            "split by how each account joined the book, and the share of them the arm priced. "
            "Membership comes from `tools/decisions_that_existed`, called once per class over "
            "that class's own stage counts -- never re-derived here."),
        "classes": classes,
        "found": found,
        "classes_excluded_and_why": dict(sorted(excluded.items())),
        "the_per_class_unresolved_bucket_is_not_established": unresolved,
        "what_each_ratio_counts": {
            "priced_share_of_the_decisions_that_existed": (
                "about the METHOD. Of the decisions the world put in front of the arm for this "
                "class, how many did it price?"),
            "decisions_share_of_the_renewals_offered": (
                "about the BOOK'S PRODUCT MIX. Of the term boundaries the world offered this "
                "class, how many were a renewal decision at all? A larger book scales both sides "
                "of this ratio equally and cannot move it."),
        },
        "reading": _reading(found, unresolved, excluded),
    }


def _reading(found: dict, unresolved: dict | None, excluded: dict[str, str]) -> str:
    """The sentence, composed from the counts. Every clause is a number a reader can check.

    THE TWO CAUSES ARE KEPT APART because they license opposite decisions. A found book the arm
    barely prices because the decisions were not there is bounded by the market's product mix and
    no book size changes it; one the arm barely prices because it declined the decisions it WAS
    offered is bounded by the method. A sentence that reported the small reach without saying
    which is the clause this module was written to replace.
    """
    if not found["classes_counted"]:
        return (
            "This run's funnel names no class the company WON or DREW, so nothing here is a "
            "reading about the method's reach over the customers it found. That is a statement "
            "about the run: the classes expected are {}.".format(
                ", ".join("`{}`".format(n) for n in found["classes_expected"])))
    if not found["decisions_that_existed"]:
        return (
            "The world offered the found book {offered:,} term boundaries and NOT ONE of them "
            "presented a per-customer renewal decision. So this run cannot say anything about the "
            "method over the customers the company found -- there was nothing to price -- and it "
            "is specifically NOT evidence the method fails. What bounds this is the product the "
            "world settled on those households, and no book size changes it."
        ).format(offered=found["renewals_the_world_offered"])

    method = 100.0 * found["priced"] / found["decisions_that_existed"]
    mix = 100.0 * found["decisions_that_existed"] / found["renewals_the_world_offered"]
    out = (
        "Over the accounts the company FOUND, the arm priced {priced:,} of the {population:,} "
        "renewals at which a decision existed -- {method:.1f}%. Those {population:,} are "
        "{mix:.1f}% of the {offered:,} term boundaries the world offered the found book; at the "
        "rest there was no rate this supplier had struck for that household, or no prior term to "
        "move one from."
    ).format(priced=found["priced"], population=found["decisions_that_existed"],
             method=method, mix=mix, offered=found["renewals_the_world_offered"])
    # THE CLAUSE THIS MODULE EXISTS FOR, and it is DERIVED. Which of the two ratios is the binding
    # one is read off the numbers; neither answer is written into the code.
    out += (
        " READ BOTH BEFORE CONCLUDING ANYTHING ABOUT BOOK SIZE: a book twice this size offers "
        "twice the boundaries and twice the decisions, so it scales the first number and leaves "
        "the second where it is. {which}"
    ).format(which=(
        "The second is the smaller share here, so what bounds this experiment is the book's "
        "PRODUCT MIX and not its size -- a fact about how much of a domestic book per-customer "
        "renewal pricing can reach, which is market structure and not a defect to repair."
        if mix < method else
        "The first is the smaller share here, so what bounds this experiment is the METHOD: the "
        "decisions were in front of the arm and it did not price them. That is ours to fix."))
    if unresolved:
        out += (
            " A further {n:,} refusals carry no decided product at all and cannot be attributed to "
            "any class, so every share above is a lower bound.".format(n=unresolved["renewals"]))
    if excluded:
        # THE EXCLUSION REACHES THE READER, with its reason. A withheld class that is invisible in
        # the sentence is a silent cap, and a silent cap reads as full coverage.
        out += " EXCLUDED: " + "; ".join(
            "`{}` -- {}".format(name, why) for name, why in sorted(excluded.items())) + "."
    out += (
        " R12: a diagnostic. No class's population is a target and this is not a cue to relax the "
        "product gate so the found book gets counted.")
    return out
