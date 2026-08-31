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
    `MAX_CHURN_PROBABILITY` is 1.0 in `company/crm/churn_model` and 0.95 in `saas/churn_model`,
    and nothing anywhere says which a given call site gets.
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
#: Both are recorded in their own finding.
KNOWN_NAME_COLLISIONS = frozenset({"VAT_RATE", "MAX_CHURN_PROBABILITY"})

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
