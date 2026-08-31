"""A rate, price, probability, threshold or cap must say where it came from.

Director, 2026-08-30, after reviewing the constants in `company/` and `saas/`:

    "A number you need is a question to research, never a value to pick. ... Every rate, price,
    probability, threshold or cap in company/ and saas/ carries its origin -- a citation, or a
    labelled belief the company holds and something grades, or a named simplification with what it
    would take to do properly. A constant with none of those is refused, the way an unsourced money
    constant already is. Same name may not carry two values anywhere; a duplicated constant is
    refused too. Baseline the existing ones as debt that only shrinks, and work it down."

WHAT EACH TEST HERE NAMES AS ITS OWN DEFECT (CONTROLS_THAT_CANNOT_FAIL):

  * `test_the_unsourced_domain_constant_debt_only_SHRINKS` — the defect is a number picked because
    a number was needed. £150 CAC, a 0.95 churn cap, a standing charge matching neither fuel: each
    looked reasonable alone and was wrong in the whole. A ratchet cannot fix the 197 that exist,
    but it makes the 198th impossible.
  * `test_no_domain_constant_NAME_carries_two_values` — worse than an unsourced constant, because
    a reader who has met one of them believes they know what the other means.
    `MAX_CHURN_PROBABILITY` was 1.0 in `company/crm/churn_model` and 0.95 in `saas/churn_model`,
    and nothing anywhere said which a given call site got. Struck 2026-08-31 by renaming the saas
    side to `MAX_BILL_SHOCK_CHURN_PROBABILITY`; the set below is now empty, and an empty set is the
    only state in which this control is a statement about the code rather than about a register.
  * `test_the_scan_has_not_lost_its_SUBJECTS` — the population floor. A control that counts
    violations goes GREEN when its scan breaks, which is how this project's scanning controls have
    failed four times. If the scan stops finding constants at all, the debt reads as paid.
  * `test_an_UNPARSEABLE_file_is_reported_and_not_silently_skipped` — the same fail-quiet one level
    down. A file that will not parse contributes no constants, so it can only make the debt look
    smaller.

WHY A COUNT AND NOT A REGISTER, and why the scan lives in `tools/` rather than here: see
`tools/domain_constant_origins.py`. The short version is the standing instruction to build the
smallest mechanism that can fail, and the precedent of
`test_a_cited_constant_has_a_caller.py`, which retired its own register before writing it.

R15 MUTATIONS. THE FIRST RUN OF THESE FOUND THAT THIS FILE COULD NOT FAIL, and that is the most
useful thing in it. Written as two ratchets -- `debt <= 197`, `collisions <= 2` -- **three of four
mutations survived**, because a ratchet only catches increases and every one of those mutations
drives the count DOWN. A classifier that breaks open reports the debt paid and the gate goes green
forever. That is the "control goes quiet rather than loud" class this repository has been caught by
repeatedly, and I built one while writing the control against it.

Repaired two ways: a FLOOR under the debt (197 constants cannot become documented in one commit),
and the collision ratchet replaced by an EXACT SET, which fires in both directions and forces a fix
to be recorded. Observed after the repair, each applied in place and reverted:

  * `_classify` returns `"cited"` unconditionally -> **1 red** (debt floor). Was 0 red.
  * `DOMAIN_NAME` narrowed to `r"(NOTHING_MATCHES_THIS)"` -> **3 red** (debt floor, the collision
    set, the population floor). Was 1 red.
  * `duplicates()` never reports a collision -> **1 red** (the collision set). Was 0 red.
  * `_comment_block` returns the WHOLE file rather than the block above -> **1 red** (debt floor),
    since every constant in a module citing anything anywhere reads as cited. Was 0 red.
  * `scan()` walks no files at all -> **3 red**. Added after the repair, as the null rung: the
    cheapest possible way for this whole file to become decorative.
"""
from __future__ import annotations

from tools.domain_constant_origins import (
    _classify,
    duplicates,
    promoted,
    scan,
    unreadable,
    without_origin,
)

#: THE DEBT, MEASURED 2026-08-30 AT COMMIT e707b0cb7. 223 domain constants in scope, of which 197
#: declare no origin at all. It may fall and it may never rise.
#:
#: THIS IS NOT THE DIRECTOR'S 263, AND THE DIFFERENCE IS RECORDED RATHER THAN SPLIT. His review
#: counted "263 uncommented ones"; this scan's definition -- his own five words (rate, price,
#: probability, threshold, cap), module-level, upper-case, numeric literal or a container of them,
#: across `company/` and `saas/` -- finds 223 constants and 197 without an origin. Four narrower
#: and wider variants were measured and none lands on 263, so the populations are genuinely
#: different rather than one being a miscount. Baselining a number I can reproduce beats matching
#: one I cannot: a ratchet nobody can re-derive is a ratchet nobody can trust. If his 263 is the
#: better population, this constant moves and the definition above moves with it.
UNSOURCED_DEBT_CEILING = 197

#: NAME COLLISIONS REMAINING, AS AN EXACT SET AND NOT A COUNT — and the difference is the whole
#: lesson of this file. A count ratchet (`<= 2`) passes when `duplicates()` returns nothing at all,
#: which is the third mutation that survived here. An exact set fires in BOTH directions: a new
#: collision reds, and so does a FIXED one, which forces the entry to be removed in the commit that
#: fixed it. That removal is the record the work happened, and a count could never demand it.
#: Five were found. Three are pure renames of private thresholds that mean different things in
#: different modules and were fixed in the same commit as this file. The two left are not renames:
#:
#:   * `VAT_RATE` -- `company/billing/invoice.py` holds a flat 0.05 while `saas/non_commodity.py`
#:     holds a per-segment table. There turn out to be FIVE implementations of one legal rule in
#:     this repository, one of which knows the de minimis threshold the others do not, so choosing
#:     the authority is a decision about which is right and not a rename.
#:   * `MAX_CHURN_PROBABILITY` -- 1.0 against 0.95, one on each side of the SIM/company seam.
#:
#: Both are recorded in their own finding. BOTH ARE NOW STRUCK; the notes below are the record.
# `VAT_RATE` STRUCK 2026-08-31 — the register asked for this edit and it is the record the work
# happened. `company/billing/invoice.py` declared its own `VAT_RATE = 0.05` ("5% VAT on domestic
# energy") while `saas/non_commodity.py` held {'resi': 0.05, 'SME': 0.2, 'I&C': 0.2}: a LEGAL rate
# with two homes, which is the director's own example of the class. The company side now asks
# `domain_invariants.vat_rate_for_segment`, which reads the published commons artefact, so there is
# no constant left to collide.
#
# `MAX_CHURN_PROBABILITY` STRUCK 2026-08-31 — the register asked for this edit too, and it was the
# last collision of the five. It was never a reconciliation: 1.0 in `company/crm/churn_model` is the
# COMPANY BELIEF model's ceiling, deliberately raised from a hard clamp so genuinely different
# elevated risks stay distinguishable; 0.95 in `saas/churn_model` capped a bill-shock model. Two
# concepts, one name. The saas side is now `MAX_BILL_SHOCK_CHURN_PROBABILITY` and the company side
# keeps the plain name. An earlier blunt pass was REVERTED because a file-level replace rewrote
# company-side references inside test modules that touch BOTH models; this one was done per
# reference, and the modules that read both (`test_phase_nc_enriched_churn_estimate`,
# `test_churn_ceiling`) are what made that necessary. Note `tests/simulation/test_churn_ceiling.py`
# monkeypatches the saas name as a STRING — a rename that missed it would have raised, not passed.
KNOWN_NAME_COLLISIONS: frozenset[str] = frozenset()


#: ONE VALUE UNDER SEVERAL NAMES — the same rule as the collision above, with the halves swapped.
#:
#: The check above asks "does one NAME carry two values?". It cannot see one CONCEPT declared in
#: several modules under different names, and that is the half that had actually gone wrong: on
#: 2026-08-31 the CLV discount rate was 0.10 in `company/analytics/clv_three_horizon` as
#: `DISCOUNT_RATE` and 0.10 again in `saas/clv_model` and `saas/home_move_win_rate` as
#: `DISCOUNT_RATE_ANNUAL`. Three homes for one number, invisible to a name-keyed check.
#:
#: WORSE THAN INVISIBLE: `clv_three_horizon`'s own comment said *"ONE discount rate for the whole
#: seam… stated once here rather than five times in five callers"*, and named `saas/clv_model` as
#: the module whose value it had adopted — without removing it. **A consolidation that added a home
#: instead of removing one**, documented as a consolidation.
#:
#: THE SUFFIXES STRIPPED are the ones that describe UNITS or PERIOD rather than the concept, so
#: `DISCOUNT_RATE` and `DISCOUNT_RATE_ANNUAL` collapse together. Deliberately short: a longer list
#: would start merging genuinely different quantities, and a false positive here sends someone to
#: delete a constant that should exist.
_CONCEPT_SUFFIXES = ("_ANNUAL", "_PER_YEAR", "_PCT", "_PERCENT", "_FRACTION",
                     "_GBP", "_KWH", "_PER_MWH")

#: Concept+value pairs living in more than one module TODAY, each with why it is still there.
#: Same discipline as `KNOWN_NAME_COLLISIONS`: when one is fixed it comes off this list in the
#: commit that fixed it, and that edit is the record the work happened.
KNOWN_CONCEPT_DUPLICATES = frozenset({
    # 4.5 GBP/MWh, `origin=cited` on BOTH sides -- the lowest-severity case here, since neither is
    # an invented number. Still two homes for one published rate.
    ("DFS_RATE_GBP", "4.5"),
})


def _concept(name: str) -> str:
    n = name.lstrip("_").upper()
    for suffix in _CONCEPT_SUFFIXES:
        if n.endswith(suffix):
            n = n[: -len(suffix)]
    return n


def test_no_concept_is_declared_in_more_than_one_module():
    """One concept, one home -- checked the way round the name-keyed test cannot see.

    MUTATION: re-declare `DISCOUNT_RATE_ANNUAL = 0.10` in `saas/clv_model.py` and this fires,
    naming both modules. That mutation is the code as it stood this morning.
    """
    import collections

    groups = collections.defaultdict(list)
    for row in scan():
        groups[(_concept(row["name"]), repr(row["value"]))].append(row)

    found = {key for key, rows in groups.items()
             if len({r["path"] for r in rows}) > 1}
    new = found - KNOWN_CONCEPT_DUPLICATES
    assert not new, (
        "{} concept(s) are declared in more than one module. One concept, one home:\n".format(len(new))
        + "\n".join(
            "  {} = {}\n".format(c, v)
            + "\n".join("      {}:{} as {}".format(r["path"], r["line"], r["name"])
                         for r in groups[(c, v)])
            for c, v in sorted(new)
        )
    )

    gone = KNOWN_CONCEPT_DUPLICATES - found
    assert not gone, (
        "{} no longer duplicated, which is good -- remove it from KNOWN_CONCEPT_DUPLICATES in the "
        "same commit that fixed it. That edit is the record the work happened.".format(
            sorted(c for c, _ in gone))
    )

#: A FLOOR UNDER THE DEBT ITSELF, and it exists because the ratchet above could not fail.
#:
#: Three of this file's four mutations SURVIVED the first time it was run. `_classify` returning
#: `"cited"` unconditionally, and `_comment_block` returning the whole file, both drive the debt to
#: ZERO — and `0 <= 197` passes. **A ratchet only catches increases.** A classifier that breaks
#: open, or a comment walker that reads too far, makes this gate green forever and reports the debt
#: paid. That is the "control goes quiet rather than loud" class, and I built one.
#:
#: 197 constants cannot become documented in one commit. A reading far below today's is a broken
#: scan, not progress. Set with room to work the debt down genuinely; when real progress crosses
#: it, this constant moves DELIBERATELY and the movement is the record that progress happened.
UNSOURCED_DEBT_FLOOR = 150

#: POPULATION FLOOR, dated 2026-08-30, measured at 223 constants across `company/` and `saas/`.
#: Set below the measurement with headroom, never AT it: a floor pinned to today's count reds on
#: any lane that lands one constant. A control that counts violations reports SUCCESS when its
#: scan loses its subjects, which is how five separate controls in this repository went quiet in a
#: single day.
CONSTANT_POPULATION_FLOOR = 190

#: THE WHOLE DOMAIN-NAMED POPULATION, literals AND non-literals, and it exists because the debt
#: count alone could not see the best repair (2026-08-31). `scan()` only sees constants whose value
#: is a numeric LITERAL. The first unit of debt actually paid --
#: `SME_VAT_THRESHOLD_KWH_PER_DAY = 33.0` becoming a read from a cited commons artefact -- left the
#: scan entirely, and the debt fell by one **for the same reason a deletion would have.**
#:
#: Measured the same day: **29 constants were ALREADY promoted and invisible**, so the 197 baseline
#: was never the whole population — it excluded the ones that had been done properly. A count that
#: can only see unfixed-shaped things can never show progress made the right way, and would have
#: rewarded leaving a literal in place with a comment over replacing it with the authority.
#:
#: Floor set below 222 + 29 = 251 with headroom, for the reason on CONSTANT_POPULATION_FLOOR above.
DOMAIN_NAMED_POPULATION_FLOOR = 235


def test_the_whole_domain_named_population_is_still_in_scope():
    """Neither half of the population may quietly leave, and a fall in one must show in the other.

    The debt ceiling ratchets violations down; this floors the SUBJECT. Renaming a constant out of
    the name regex, deleting it, or promoting it to a computed value all reduce the debt, and only
    this can tell "the scan lost its subject" from "the work was done".

    MUTATION: make `promoted()` return `[]`, or narrow `DOMAIN_NAME` so a package's constants stop
    matching, and this fires where the debt ceiling alone reads GREEN and calls it progress.
    """
    literals = scan()
    lifted = promoted()
    total = len(literals) + len(lifted)
    assert total >= DOMAIN_NAMED_POPULATION_FLOOR, (
        f"{len(literals)} literal + {len(lifted)} promoted = {total} domain-named constants, below "
        f"the floor of {DOMAIN_NAMED_POPULATION_FLOOR}. Constants have left the SCOPE of this "
        "control rather than gained an origin — check for a rename out of the name regex, a "
        "narrowed DOMAIN_NAME, or a package dropped from SCOPE. If they were genuinely deleted, "
        "lower this floor in the commit that deleted them.")
    assert lifted, (
        "no domain constant reads from an authority any more. Promotion is the BEST outcome the "
        "origin rule can produce; zero of them means `promoted()` has broken shut, and the debt "
        "count would then read every future proper repair as a deletion.")


def test_the_unsourced_domain_constant_debt_only_SHRINKS():
    """The 198th unsourced constant cannot land.

    A number picked because a number was needed is invisible at the moment it is written and
    expensive when it meets the rest of the system. This cannot repair the 197 that exist; what it
    does is make the next one impossible, and make the count a thing that has to be argued down.
    """
    debt = without_origin()

    # THE FLOOR FIRST, because the ceiling below cannot fail on its own. See UNSOURCED_DEBT_FLOOR.
    assert len(debt) >= UNSOURCED_DEBT_FLOOR, (
        f"only {len(debt)} domain constants read as having no origin, below the floor of "
        f"{UNSOURCED_DEBT_FLOOR}. 197 constants do not become documented in one commit, so the "
        "likely cause is that `_classify` or `_comment_block` has broken OPEN and is discharging "
        "constants it should not. If the debt was genuinely worked down past this floor, lower "
        "the floor in the same commit that did the work — that edit is the record that it "
        "happened.")

    assert len(debt) <= UNSOURCED_DEBT_CEILING, (
        f"{len(debt)} domain constants declare no origin, above the ratchet of "
        f"{UNSOURCED_DEBT_CEILING}. A rate, price, probability, threshold or cap must carry ONE "
        "of: a citation (a docs/ path or a named publisher), a labelled BELIEF the company holds "
        "that something grades, or a NAMED SIMPLIFICATION saying what it would take to do "
        "properly. New since the baseline:\n  "
        + "\n  ".join(f"{r['path']}:{r['line']} {r['name']}" for r in debt[-12:]))


def test_no_domain_constant_NAME_carries_two_values():
    """One name, one number, anywhere in scope.

    Worse than an unsourced constant: a reader who has met one of them believes they know what the
    other means, and no call site says which it got.

    AN EXACT SET, NOT A CEILING. Two of the five found are decisions about which implementation is
    correct rather than renames, so this cannot be zero tonight — but a `<= 2` ceiling passes when
    the scan finds nothing, which is a mutation that survived here. Equality fires both ways: a new
    collision reds, and so does a fixed one, which is how the fix gets recorded.
    """
    collisions = duplicates()
    found = frozenset(collisions)

    def _detail(names):
        return "\n".join(
            f"  {name}\n" + "\n".join(f"      {r['path']}:{r['line']} = {r['value']!r}"
                                       for r in collisions.get(name, []))
            for name in sorted(names))

    new = found - KNOWN_NAME_COLLISIONS
    assert not new, (
        f"{len(new)} constant name(s) newly carry more than one value. One name, one number:\n"
        + _detail(new))

    gone = KNOWN_NAME_COLLISIONS - found
    assert not gone, (
        f"{sorted(gone)} no longer collide, which is good — remove them from "
        "KNOWN_NAME_COLLISIONS in the same commit that fixed them. That edit is the record the "
        "work happened; a count could not have asked for it. (If instead the SCAN broke and is "
        "finding nothing, the population floor below says so.)")


def test_the_scan_has_not_lost_its_SUBJECTS():
    """THE POPULATION FLOOR, and it is the reason the two ratchets above can be believed.

    Both count violations, so both go GREEN when the scan finds nothing — a moved package, a
    changed naming convention, a regex that stops matching. That failure is silent and it is the
    one this repository has actually suffered, five times in one day.

    A HOLE THIS FLOOR DOES NOT CLOSE, and I walked into it within minutes of writing the file.
    Fixing the `_GREEN_THRESHOLD`/`_AMBER_THRESHOLD` collisions, my first rename produced
    `_GREEN_ADVERSE_PCT_OF_MONTHLY_REVENUE` and `_GREEN_LIMIT_UTILISATION_FRACTION` — names that
    no longer contain `RATE|PRICE|PROBABILITY|THRESHOLD|CAP`. Four constants left the population,
    the debt fell from 197 to 193, and **not one number had become more honest**. The floor did
    not fire, because 219 is comfortably above 190.

    So: **the debt can be paid down by renaming a constant out of scope, and no control here can
    tell that from a deletion.** The floor catches gross scan breakage and nothing finer. It is
    recorded rather than papered over, because the alternative — a floor pinned tight enough to
    catch four — reds on any lane that legitimately deletes a handful. The names were changed to
    keep `THRESHOLD` in them and the debt went back to 197.
    """
    found = scan()

    assert len(found) >= CONSTANT_POPULATION_FLOOR, (
        f"the scan found only {len(found)} domain constants in company/ and saas/, below the "
        f"floor of {CONSTANT_POPULATION_FLOOR} measured on 2026-08-30. The debt ratchets above "
        "are counted against this population, so they are meaningless until this is explained: "
        "either the packages moved, the naming convention changed, or the scan is broken.")


def test_an_UNPARSEABLE_file_is_reported_and_not_silently_skipped():
    """A file that will not parse contributes no constants, so it can only make the debt LOOK
    smaller. The scanner cannot fail closed without letting one bad file close the whole tree, so
    it reports instead — and this asserts the report is empty, which is the same protection with
    the blast radius of one test rather than of every commit."""
    bad = unreadable()

    assert not bad, (
        "these files in company/ or saas/ could not be parsed, so any constants they hold are "
        f"absent from the debt count and the count is not trustworthy: {bad}")


def test_a_word_ending_in_ons_is_not_a_CITATION():
    """An English plural may not discharge a constant's debt.

    THE DEFECT, found live 2026-08-31 while giving `MAX_BILL_SHOCK_CHURN_PROBABILITY` an origin:
    `_CITED` listed the short publisher abbreviations as `CMA\\b` and `ONS\\b` — a TRAILING word
    boundary and no LEADING one — so `ONS` matched inside "comparisons", "commons", "reasons",
    "seasons". The classifier then returned `"cited"` for a comment that names no publisher and no
    path, and `_classify` checks CITED first, so the mislabel also outranks the honest origins
    behind it.

    IT WAS NOT HYPOTHETICAL. `company/regulatory/seg_book.py::_SEG_RATE_P_PER_KWH_BY_YEAR` says
    "Based on publicly available SEG rate comparisons 2020-2024" over an illustrative table, and
    was counted among the 26 cited. Fixing the anchors moved exactly two constants: that one, back
    into the debt where it belongs, and the new simplification above, which had said "the
    regulation commons" and been read as citing the ONS.

    THE DIRECTION MATTERS. This is FAIL-OPEN: a false CITED shrinks the debt, and the debt ratchet
    only catches increases — so the whole register could have been discharged, one plural at a
    time, with the gate green throughout.

    MUTATION (must fire): drop either leading `\\b` from `_CITED`.
    """
    assert _classify("# based on published rate comparisons across suppliers") is None, (
        "a comment whose only match is a word ENDING in 'ons' reads as a citation — the leading "
        "word boundary has been dropped from `ONS` in tools.domain_constant_origins._CITED")
    assert _classify("# the same rule the commons artefact carries") is None
    # `CMA`'s leading boundary is DEFENSIVE, not evidenced: no ordinary English word contains
    # "cma", so unlike `ONS` it has never mislabelled anything. Anchored anyway because the two
    # were written as a pair and leaving one half-anchored invites the next reader to copy it.

    # THE VACUITY GUARD: the abbreviations must still match when they are the real thing, or this
    # test would pass against a `_CITED` that matches nothing at all.
    assert _classify("# ONS, Consumer price inflation time series") == "cited"
    assert _classify("# CMA Energy Market Investigation, final report") == "cited"
