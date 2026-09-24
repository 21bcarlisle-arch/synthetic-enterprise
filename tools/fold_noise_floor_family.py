"""Fold several noise-floor runs of ONE world into one family, or refuse and say which question failed.

WHY THIS EXISTS. A noise floor's whole value is its `n`: the selection leg's sign is stated from
`mean / (stdev / sqrt(n))`, and on 2026-09-10 the family on disk was nine draws wide with the mean
1.79 standard errors from zero against the 1.96 a sign needs. The only way to move that is more
seeds, and a floor run costs three full passes per seed -- so the seeds arrive in BATCHES, hours
apart, from different sessions and therefore from different code trees. Nothing here could join two
batches, so the choice was between re-drawing the whole family from scratch every time (13 hours to
add nine seeds to nine) and joining them by hand.

BY HAND IS THE ONE OPTION THAT MUST NOT HAPPEN, and not because it is laborious. Every failure mode
of this join produces a WELL-FORMED ARTEFACT that no consumer downstream can tell from a good one:

  * TWO WORLDS JOINED. A spread measured over one departure level is not an error bar on a figure
    measured over another. The rows look identical -- same fields, same magnitudes -- and the
    folded artefact would publish a bound on a world it never measured.
  * A SEED COUNTED TWICE. The same row twice raises `n` and shrinks the standard error by a factor
    that measures nothing. `run_arms_rerun.check_seeds` refuses this WITHIN one run and had no way
    to see ACROSS two, which is exactly where a second batch reusing a seed would land.
  * TWO CLOCKS JOINED. `run_value_cycle_ab.noise_floor` refuses a mixed-clock spread outright,
    because the bad-debt gap between this run's two clocks is larger than every contrast the
    spread bounds -- a mixed floor publishes that gap as seed noise.

Each of those is a fail-open: the artefact is consistent, its arithmetic checks out, and it is
wrong. So the join is a tool with refusals rather than a habit with a checklist.

THE ARITHMETIC IS THE PRODUCER'S, NOT A SECOND COPY OF IT. `_spread` is imported from
`run_value_cycle_ab` rather than reimplemented here. This project's most expensive recurring shape
is one rule with several implementations -- the VAT rule had five, and a defect fixed in one of
them in July was still live in another in August. A folded family whose mean is computed by
slightly different code from the family it extends is that shape with the two copies one import
apart. `test_fold_noise_floor_family.py` pins it against the real nine-seed artefact on disk: the
fold's recomputation of a single source must reproduce that source's own published summary exactly.

WHAT THIS DELIBERATELY REFUSES TO CLAIM. A folded family has NO single producing commit, and the
temptation is to write the newest batch's commit into the field because the field wants a value.
`generate_value_arms_data._floor_tree_pairing` reads exactly that field to tell a reader whether the
bound and the figure it bounds were drawn by the same code, and it is explicit that a missing stamp
"is not evidence the trees agree". So the fold writes `commit: None` with a reason naming the fold,
which routes that control to its `unstamped` branch and publishes an honest unknown -- and it writes
every member's commit into `folded_from`, so what was lost from the summary field is still on disk
for a reader who wants it. An honest `None` with a named reason is worth more than a plausible
value, because the value would be read as established and the `None` cannot be.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

#: The producer's OWN estimator, imported and never copied. See the module docstring: a second
#: implementation of one rule is this project's most expensive recurring defect, and a folded
#: family whose mean is computed differently from the family it extends is that defect with the
#: two copies one import apart.
from tools.run_value_cycle_ab import (
    _book_declared,
    _spread,
    distance_to_a_sign,
    priced_decision_fingerprint,
    sems_to_state_a_sign,
)

_REPO = Path(__file__).resolve().parent.parent

# `_DISTINGUISHABLE_SEMS = 2` LIVED HERE AND IS DELETED (2026-09-18). Its own comment said it was
# "restated here rather than imported" because the producer's copy was one line inside a
# three-hundred-line run function with no seam -- and a restatement pinned by a test is still a
# second implementation, which is the shape this project pays for most. The producer now derives
# its bar from the family size too, so there is a seam and the bar has one home:
# `run_value_cycle_ab.sems_to_state_a_sign`, imported above and never re-spelled.
#
# THE VALUE WAS ALSO WRONG, AND THAT IS THE HALF THAT REACHED A READER. A fixed 2 grades a standard
# error that was estimated from the same `n` draws as the mean it bounds, so it is short of the
# honest t(n-1) at every family this instrument has drawn -- 2.306 at nine seeds, 2.201 at twelve,
# 2.110 at eighteen -- and short by MORE as the family shrinks. On 2026-09-18 the live feed carried
# `distinguishable_from_zero: true` under a page saying "we cannot tell", and the gap between the
# two bars is where that disagreement lived.


class FoldRefused(RuntimeError):
    """A fold that did not happen, carrying WHICH question failed. Never raised after a write."""


def _read(path: Path) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FoldRefused("no floor artefact at `{}`".format(path)) from None
    except json.JSONDecodeError as exc:
        raise FoldRefused("`{}` is not readable JSON: {}".format(path, exc)) from None


def _agree_on(sources: list, label: str, get) -> object:
    """The one value every source carries for `label`, or a refusal naming the disagreement.

    ABSENCE IS A REFUSAL AND NOT A PASS. A source that carries no value for a question the fold
    must answer cannot be shown to agree with the others, and treating `None` as "agrees with
    anything" is how the oldest artefact in a family becomes the one that joins to everything.
    """
    seen = {}
    for path, data in sources:
        value = get(data)
        if value is None or (isinstance(value, str) and not value.strip()):
            raise FoldRefused(
                "`{}` carries no {}, so it cannot be shown to describe the same measurement as "
                "the others. A fold joins families that are demonstrably one population; an "
                "absent field is an unknown, never an agreement.".format(path, label))
        seen.setdefault(value, []).append(str(path))
    if len(seen) > 1:
        detail = "; ".join(
            "{} -> {}".format(value, ", ".join(paths)) for value, paths in sorted(
                seen.items(), key=lambda kv: str(kv[0])))
        raise FoldRefused(
            "the sources report {} different values for {} ({}). Their rows are not draws of one "
            "quantity, so no spread over the union bounds anything.".format(
                len(seen), label, detail))
    return next(iter(seen))


def _seed_rows(sources: list) -> list:
    """Every source's rows in source order, refusing a seed that appears twice.

    THE ONE THAT WOULD HAVE BEEN BELIEVED. A duplicated seed is the same row twice: `n` rises, the
    standard error falls by sqrt of a lie, and every field downstream reads as a better-resolved
    measurement. The artefact is well-formed and internally consistent, so nothing further down can
    tell -- which is precisely why the refusal has to be here.

    BUT THE REFUSAL USED TO NAME A CAUSE IT HAD NOT ESTABLISHED (2026-09-19, measured). It said
    "folding it would count one draw twice" on EVERY duplicate. That sentence is true only when
    both rows came off the same pricing code. Seeds 3100001-3100012 have now been drawn TWICE --
    once at `a178b56d6` and once at `18327d977` -- and those trees differ on
    `company/pricing/value_based_renewal.py`, a `_VALUE_ARM_PATHS` member and the very file the
    splice finding named. Those rows are not one draw twice. They are two instruments drawing the
    same seed, and the remedy the old sentence implies -- drop the duplicate, keep either -- would
    silently discard a whole family and publish the survivor as if the choice had not been made.

    SO THE REFUSAL ASKS WHICH IT IS, AND SAYS ONLY WHAT IT ESTABLISHED. Same value arm: the
    original sentence, which is then earned. Different value arm: a different defect, named, with
    "fold each family alone" as the remedy instead of de-duplication. Cannot tell: fail closed and
    say BOTH are open, because an unasked diff is not evidence the arms agree -- the error
    `_value_arm_pairing` exists to stop making, one field earlier.

    IT STILL REFUSES ON EVERY BRANCH. Which defect it is changes the remedy, never the verdict: no
    fold that double-counts a seed id is well-defined, whichever tree drew it.
    """
    rows, where = [], {}
    for path, data in sources:
        got = data.get("seeds") or []
        if not got:
            raise FoldRefused(
                "`{}` carries no seed rows, so there is nothing in it to fold.".format(path))
        for row in got:
            seed = row.get("seed")
            if seed in where:
                raise FoldRefused("seed {} appears in both `{}` and `{}`. {}".format(
                    seed, where[seed], path, _why_a_duplicated_seed_refuses(
                        where[seed], str(path), sources)))
            where[seed] = str(path)
            rows.append(row)
    return rows


def _why_a_duplicated_seed_refuses(first: str, second: str, sources: list) -> str:
    """The half of the duplicate-seed refusal that depends on WHICH tree drew each row.

    Split out so the three branches are separately reachable and separately testable: a refusal
    that can only be provoked through one door gets its other doors pinned by nothing.
    """
    by_path = {str(p): d for p, d in sources}
    commits = []
    for path in (first, second):
        commit = ((by_path.get(path) or {}).get("producing_commit") or {}).get("commit")
        commits.append(commit.strip() if isinstance(commit, str) and commit.strip() else None)

    if None in commits:
        return (
            "One of those two runs carries no producing commit, so this cannot tell whether they "
            "are the same draw recorded twice or two instruments that drew the same seed. BOTH "
            "are open and they need opposite remedies -- de-duplicate, or fold each family alone "
            "-- so neither is applied here. Stamp the unstamped run and ask again.")

    if commits[0] == commits[1]:
        return (
            "Both runs name `{}`, so this is one draw recorded twice: `n` rises and the standard "
            "error shrinks by a factor that measures nothing, and the artefact that comes out is "
            "well-formed, so no consumer could tell. Drop one copy.".format(commits[0][:9]))

    diffs, failed = _value_arm_diff(commits)
    if failed:
        return (
            "They name different commits (`{}`, `{}`) and the value-arm diff could not be taken "
            "({}). This may be one draw twice or two instruments drawing one seed; those need "
            "opposite remedies, so neither is applied here. A diff that could not be run is not "
            "evidence the arms agree.".format(commits[0][:9], commits[1][:9], failed))

    if diffs:
        return (
            "They were drawn by DIFFERENT PRICING CODE -- `{}` and `{}` differ on {}, under {}. "
            "These are not one draw twice; they are two instruments that drew the same seed id, "
            "and their rows are different measurements that happen to share a label. Do NOT "
            "de-duplicate: dropping either silently discards a whole instrument's family and "
            "publishes the survivor as though no choice was made. Fold each family alone and "
            "report them side by side.".format(
                commits[0][:9], commits[1][:9], ", ".join(sorted(diffs)),
                ", ".join(_VALUE_ARM_PATHS)))

    return (
        "They name different commits (`{}`, `{}`) but no path under {} differs between them, so "
        "the same pricing code drew both and this is one draw recorded twice. Drop one copy."
        .format(commits[0][:9], commits[1][:9], ", ".join(_VALUE_ARM_PATHS)))


def _leg(rows: list, key: str) -> dict:
    """One leg's spread, standard error and sign verdict, under the bar BOTH legs are judged at.

    THE BAR IS `sems_to_state_a_sign(n)` AND NOT A SECOND ONE. The whole use of a level leg beside
    a selection leg is the CONTRAST between their verdicts -- "one leg's sign is stateable and the
    other's is not" is a claim about the two legs, and it is only a claim about the legs if both
    were asked the same question. Judging the level leg at a different bar would make the contrast
    an artefact of the rule rather than of the data, which is this project's most expensive shape
    wearing a statistic's clothes. Every leg here shares one `n`, so they share one bar by
    construction rather than by anyone remembering to pass the same number twice.

    IT IS PUBLISHED BESIDE THE VERDICT, which is what makes the bar checkable from the artefact
    instead of from this docstring. A verdict whose threshold is not on the surface is a verdict
    the reader has to take on trust, and this bar moves with the family -- so the day it moves, the
    number that moved it is on the page next to the answer it changed.
    """
    spread = _spread([r.get(key) for r in rows])
    sem = None
    distinguishable = None
    bar = sems_to_state_a_sign(spread["n"])
    if spread["stdev"] is not None and spread["n"] > 1 and bar is not None:
        sem = spread["stdev"] / math.sqrt(spread["n"])
        distinguishable = abs(spread["mean"]) > bar * sem
    values = [r.get(key) for r in rows if isinstance(r.get(key), (int, float))
              and not isinstance(r.get(key), bool)]
    positive = sum(1 for v in values if v > 0)
    return {
        "spread": spread,
        "sem_gbp": sem,
        "distinguishable_from_zero": distinguishable,
        #: THE BAR THE VERDICT ABOVE WAS TAKEN AT, on the artefact. Derived from this family's own
        #: size and written down nowhere, so a consumer can re-run the comparison rather than
        #: assume which rule produced the boolean beside it. This is the key that makes
        #: `generate_value_arms_data`'s reconciliation a comparison of two ANSWERS rather than of
        #: one answer and a guess at the threshold that produced it.
        "sems_needed_to_state_a_sign": bar,
        #: THE SAME QUESTION ASKED WITHOUT AN ESTIMATOR, because the two can disagree and a reader
        #: who can see both learns something a reader given only one cannot. The count is
        #: distribution-free: it does not care whether the leg is normal, and on a leg whose values
        #: repeat (this book's level arm returns a handful of discrete nets) it is the more
        #: conservative of the two readings.
        "positive_seeds": positive,
        "negative_or_zero_seeds": len(values) - positive,
        "seeds_with_a_figure": len(values),
        #: HOW FAR FROM A SIGN AND WHAT WOULD CLOSE IT -- the producer's own function, imported.
        "distance_to_a_sign": distance_to_a_sign(
            spread["mean"], spread["stdev"], spread["n"]),
    }


def _auc_across_seeds(rows: list) -> dict:
    """The discrimination AUC's spread over the family, or a named refusal.

    WHY THIS IS HERE AT ALL. The advantage and the AUC answer the two halves of one question -- how
    much the arm won, and whether it won by knowing anything -- and the project has published the
    first without the second before (`site/data/value_arms.json` carries the retraction: the same
    estimator scored 0.646, 0.672, 0.465, 0.465 and 0.130 across five runs in four days, and a
    corroboration argument was built on one of them). A floor family is nine or more draws of the
    advantage and is therefore the ONE instrument in this repo that could put an error bar on the
    AUC. Until 2026-09-17 it discarded the AUC entirely, so the bound could not be computed from
    any artefact on disk however many seeds were drawn.

    FAILS CLOSED, AND NAMES HOW MANY ROWS COULD NOT ANSWER. Every floor written before the producer
    carried the field has rows with no AUC at all, and a spread over the subset that HAS one would
    be a bound on a different family from the one whose advantage is published beside it. So a
    single row without an AUC makes the whole block an unavailable with a count, never a spread
    over whoever happened to answer.
    """
    present = [r.get("discrimination_auc") for r in rows
               if isinstance(r.get("discrimination_auc"), (int, float))
               and not isinstance(r.get("discrimination_auc"), bool)]
    if len(present) != len(rows):
        return {
            "available": False,
            "seeds_carrying_an_auc": len(present),
            "seeds_in_family": len(rows),
            "unavailable_because": (
                "{} of this family's {} seed rows carry no `discrimination_auc`. Floors produced "
                "before 2026-09-17 did not record it, so the advantage figures in this family "
                "have no discrimination reading beside them and none can be recovered without "
                "re-running the seeds. A spread over only the {} rows that DO answer would bound "
                "a different family from the one whose advantage is published here, so this "
                "states an unknown instead.".format(
                    len(rows) - len(present), len(rows), len(present))),
        }
    return {
        "available": True,
        "spread": _spread(present),
        #: 0.5 IS THE NO-INFORMATION POINT, and the distance from it is the reading -- not the
        #: distance from zero, which is what a leg-shaped helper would have computed.
        "distance_from_no_information": _spread([v - 0.5 for v in present]),
        "retained_and_left_by_seed": [
            {"seed": r.get("seed"), "auc_population": r.get("auc_population")} for r in rows],
    }


def _fingerprint_of(row: dict) -> tuple:
    """`(fingerprint, where it came from, why it is unknown)` for one seed row.

    TWO ROWS THAT BOTH SAY NOTHING SAY DIFFERENT THINGS, which is the whole reason this returns a
    provenance beside the value. A row written before 2026-09-24 has no such field and no roster
    either: its decision set was never recorded and cannot be recovered without re-running the
    seed. A row written after it, whose run measured no belief, carries the field AS `None` -- the
    producer's own "unknown", deliberately distinct from the real digest an empty roster gets. Both
    are unknowns to the count below and neither may be read as agreement, but a reader deciding
    whether to re-run needs to know which one they are holding.

    IT DERIVES RATHER THAN GIVING UP, and only from the producer's own function over the row's own
    roster. `noise_floor` builds that roster ONCE and uses it twice -- publishes it as
    `scored_decisions` and fingerprints it -- so a row carrying the roster carries everything the
    digest was taken over, and deriving it here is the same call on the same input rather than a
    second rule. Without this, the only family on disk whose rows record their decision sets at all
    (`..._five_seed_head_20260924.json`, written hours before the field landed) would count as five
    unknowns, and the count this block exists to publish would be unavailable on every artefact
    this repo has ever drawn.

    A ROW CARRYING BOTH, DISAGREEING, IS A REFUSAL. The digest and the roster are two recordings of
    one thing; if they part company then one of them is not what it claims and every count below is
    taken over a fiction. Nothing on disk can reach this branch today, which is exactly when it is
    cheap to write.
    """
    published = row.get("priced_decision_fingerprint")
    has_field = "priced_decision_fingerprint" in row
    has_roster = "scored_decisions" in row
    derived = priced_decision_fingerprint(row.get("scored_decisions")) if has_roster else None

    if published is not None and derived is not None and published != derived:
        raise FoldRefused(
            "seed {}: the row's `priced_decision_fingerprint` (`{}`) is not the digest of the "
            "row's own `scored_decisions` (`{}`). One of the two is not what it claims, so a "
            "count of distinct decision sets over this family would be taken over a fiction. "
            "Re-run the seed rather than choosing between them.".format(
                row.get("seed"), published, derived))

    if published is not None:
        return published, "the row's own `priced_decision_fingerprint`", None
    if derived is not None:
        return derived, "derived from the row's own `scored_decisions`", None
    if has_field or has_roster:
        return None, None, (
            "this seed's run measured no belief, so it priced no decision set to fingerprint -- "
            "an unknown, and NOT the real digest a run that scored an empty roster gets")
    return None, None, (
        "this row predates the decision-set fields (2026-09-24): it carries neither a fingerprint "
        "nor the `scored_decisions` roster one could be derived from, so what this seed's "
        "residual was taken over is unrecoverable without re-running the seed")


def _priced_decision_draws(rows: list) -> dict:
    """How many DRAWS this family is entitled to, as against how many seeds it ran.

    THE DEFECT THIS PUBLISHES, and it reads as a result rather than as a fault. `selection_gbp` is
    `value_arm_net - level_arm_net`: the control arm cancels algebraically and the two surviving
    arms differ by the renewal-margin rule and by nothing else, so every pound the elasticity
    re-draw moves OUTSIDE the renewals the value arm priced lands in both nets identically and
    cancels. A seed pair whose priced decisions did not change reports its residual not moving at
    all -- not a small dispersion, a structural zero. A family's sd is therefore part dispersion
    and part pinning, and the sem is REWARDED by the pinning: a family that pinned every draw would
    report a spread of zero and declare itself infinitely confident. `n` distinct decision sets,
    not `n` seeds, is the count a spread over this instrument is entitled to.

    UNTIL THIS BLOCK, THE FIELD WAS RECORDED AND UNREAD. `run_value_cycle_ab` began stamping
    `priced_decision_fingerprint` on every seed row at `526aa4f70`, and nothing anywhere counted
    them -- so the page still reported n seeds as n draws. A field nobody reads is not a control.

    THE ANSWER IS A BOUND AND NOT ALWAYS A NUMBER, because the family that is actually published
    records no rosters at all. Two things are known about any family:

      * EXACT, when every row has a fingerprint: the count of distinct ones. Nothing is inferred.
      * A FLOOR, always: two seeds whose residuals DIFFER cannot have been taken over the same
        decision set, so the count of distinct `selection_gbp` values is a floor under the count of
        distinct decision sets. This is the contrapositive of a coextension that was MEASURED and
        not proved -- ten seed pairs on `..._five_seed_head_20260924.json`, where identical rosters
        and pinned residuals were exactly coextensive with no exceptions in either direction -- so
        it is published as a floor, named as such, and never as the answer. Two genuinely different
        decision sets can land on one residual and this count would read them as one draw.

    AND THE FLOOR CARRIES ITS OWN FALSIFIER. If any two rows share a fingerprint and disagree about
    the residual, the measured coextension is refuted on THIS family -- the floor is then unsound
    and is withdrawn, while the exact count is untouched, because the fingerprint is the definition
    of a distinct draw and the residual was only ever a proxy for it. Keyed to the property rather
    than to today's answer: the day the coextension stops holding, this says so on the artefact
    instead of quietly publishing a floor above the ceiling.

    UNKNOWN IS NEVER AGREEMENT. An unrecorded seed could have repeated a decision set the family
    already holds or could have drawn a new one, so it widens the bound at the top and adds nothing
    at the bottom. Folding every unknown into one bucket and calling it one repeated draw would
    shrink a spread that is already too narrow, which is the exact direction this instrument errs.
    """
    seeds_in_family = len(rows)
    by_seed, known = [], []
    for row in rows:
        fingerprint, source, why_not = _fingerprint_of(row)
        by_seed.append({
            "seed": row.get("seed"),
            "priced_decision_fingerprint": fingerprint,
            "known_from": source,
            "unknown_because": why_not,
            "selection_gbp": row.get("selection_gbp"),
        })
        if fingerprint is not None:
            known.append((fingerprint, row.get("selection_gbp")))

    distinct_known = len({f for f, _ in known})
    unknown = seeds_in_family - len(known)
    residuals = [r.get("selection_gbp") for r in rows]
    distinct_residuals = len({r for r in residuals if r is not None})

    #: THE FLOOR'S OWN FALSIFIER, run before the floor is used. See the docstring.
    grouped = {}
    for fingerprint, residual in known:
        grouped.setdefault(fingerprint, set()).add(residual)
    refuted_by = sorted(f for f, values in grouped.items() if len(values) > 1)

    floor = None if refuted_by else distinct_residuals
    at_least = max(distinct_known, floor) if floor is not None else distinct_known
    at_most = distinct_known + unknown
    exact = distinct_known if unknown == 0 else None

    return {
        "seeds_in_family": seeds_in_family,
        "seeds_with_a_known_decision_set": len(known),
        "seeds_with_an_unknown_decision_set": unknown,
        "distinct_known_decision_sets": distinct_known,
        #: THE COUNT THE SPREAD IS ENTITLED TO, or an honest unknown with the reason on the same
        #: row. Never the seed count wearing a draw count's name.
        "draws_the_spread_is_entitled_to": exact,
        "at_least": at_least,
        "at_most": at_most,
        #: NULL IS NOT THE SAME AS "NOTHING IS KNOWN", and the two get different sentences. When
        #: the floor and the ceiling coincide the draw count IS determined -- every seed met a
        #: fresh decision set -- but it is determined by the measured coextension rather than
        #: recorded on any row, and this field holds only what the rows recorded. A reader who
        #: cannot tell which of the two produced a number will treat a deduction as a record.
        "unavailable_because": None if exact is not None else (
            "{} of this family's {} seed rows record no decision set, so the number of distinct "
            "draws under this spread is not recorded anywhere. {}".format(
                unknown, seeds_in_family,
                "It is nonetheless PINNED to {} by the residual floor: {} distinct residuals over "
                "{} seeds leaves no room for a repeat, so no seed here is a second draw of a set "
                "the family already held. Read it as a deduction from the coextension, not as a "
                "record.".format(at_most, distinct_residuals, seeds_in_family)
                if at_least == at_most else
                "It is between {} and {}: an unrecorded seed may have repeated a set already in "
                "the family or drawn a new one, and reading those unknowns as one repeat would "
                "shrink a spread that is already too narrow.".format(at_least, at_most))),
        #: A FLOOR AND NOT THE ANSWER -- the contrapositive of a measured coextension, available
        #: on families that recorded no roster at all, which is every family published to date.
        "distinct_selection_residuals": distinct_residuals,
        "the_residual_floor_holds": not refuted_by,
        "the_residual_floor_is_refuted_by": refuted_by or None,
        "how_to_read_this": (
            "`seeds_in_family` is how many times the instrument was RUN. "
            "`draws_the_spread_is_entitled_to` is how many distinct priced-decision sets those "
            "runs actually met, and it is the n a standard error over `selection_gbp` is earned "
            "at -- the residual cannot move unless a priced decision moves, so two seeds over one "
            "decision set are one draw recorded twice however differently the rest of the book "
            "was re-drawn. Where it is null, read `at_least` and `at_most` and treat the published "
            "sem as an upper bound on this family's confidence, never as its confidence."
            + ("" if not refuted_by else
               " THE RESIDUAL FLOOR IS REFUTED ON THIS FAMILY: {} fingerprint(s) appear on seeds "
               "whose residuals differ, so the coextension between an unchanged decision set and "
               "a pinned residual does not hold here. The exact count above is unaffected -- the "
               "fingerprint is what a distinct draw IS -- but the floor derived from distinct "
               "residuals is withdrawn.".format(len(refuted_by)))),
        "by_seed": by_seed,
    }


def summarise(rows: list) -> dict:
    """The producer's own summary block, recomputed over the folded rows.

    Split out from `fold` so a control can run it against an artefact already on disk and check it
    reproduces that artefact's published figures -- which is the only evidence that this fold and
    the producer agree about what a mean is.

    BOTH LEGS SINCE 2026-09-17, AND THE ONE THAT WAS MISSING IS THE ONE THE THESIS TURNS ON. Until
    then this block summarised `selection_gbp` alone, while `level_advantage_gbp` sat in every seed
    row of every floor ever written and was read by nothing. The consequence was not a rounding
    error: the level leg's sign had been determined and POSITIVE on the nine-seed floors since
    2026-09-09, at 18 of 18 draws once two of them are folded, and the surface went on publishing
    "the split cannot be read" -- which was true of the selection half and false of the level half.
    A leg nobody summarises reads exactly like a leg with nothing in it.
    """
    selection = _leg(rows, "selection_gbp")
    level = _leg(rows, "level_advantage_gbp")
    value = _leg(rows, "value_advantage_gbp")
    share = _spread([r.get("level_share_of_advantage") for r in rows])
    return {
        # The four fields the producer published before 2026-09-17, unchanged in name and value so
        # every consumer keyed to them keeps working and the pinning control keeps its subject.
        "selection_gbp_spread": selection["spread"],
        "level_share_spread": share,
        "selection_sem_gbp": selection["sem_gbp"],
        "selection_distinguishable_from_zero": selection["distinguishable_from_zero"],
        # THE BAR THAT VERDICT WAS TAKEN AT, hoisted beside it (2026-09-18). The key above is the
        # one every consumer outside this file reads, and until now it arrived bare -- so
        # `generate_value_arms_data` had to name the producer's threshold itself to reconcile it,
        # which is how a page came to publish a bar the artefact was never graded at. A verdict and
        # its threshold travel together or the reader is reconciling one of them against a memory.
        "selection_sems_needed_to_state_a_sign": selection["sems_needed_to_state_a_sign"],
        # The legs, each carrying its own verdict under the same bar. `selection_leg` restates the
        # four above rather than replacing them -- a consumer reading either gets one answer.
        "selection_leg": selection,
        "level_leg": level,
        "value_leg": value,
        "discrimination_auc_across_seeds": _auc_across_seeds(rows),
        #: HOW MANY DRAWS THE THREE LEGS ABOVE ARE ENTITLED TO, beside the seed count they were
        #: taken at. Every `n` above is a seed count; this is the only field that says how many
        #: of those seeds met a decision set the family had not already seen, and the selection
        #: leg's sem is the figure it bears on. See `_priced_decision_draws`.
        "priced_decision_draws": _priced_decision_draws(rows),
        "how_to_read_the_two_legs": (
            "`value_leg` is what the arm beat the control by. `level_leg` is what a FLAT rule "
            "charging the same median margin, with no per-customer inference at all, beat the "
            "control by. `selection_leg` is the difference -- what the inference itself was "
            "worth -- and it is the only one of the three that bears on whether the advantage "
            "came from knowing something rather than from charging more. A level leg with a "
            "stateable sign and a selection leg without one is the unflattering reading and is "
            "reported as such: it says the demonstrable advantage is the price level. Read "
            "`discrimination_auc_across_seeds` beside it, and when that says unavailable, the "
            "advantage in this family has no discrimination reading beside it at all."),
    }


def _book_identity(sources: list) -> dict:
    """The book the folded family was drawn over, or a stated unknown.

    NOT `_agree_on`, ON PURPOSE. `book_identity` arrived on floor artefacts on 2026-09-09, so every
    family that spans that date has members that predate the field. Refusing the fold for it would
    make the tool useless exactly when it is needed; claiming the newest member's book for all of
    them would be worse. So a member without one turns the whole block into an unknown that names
    which member could not answer, and a consumer meets a `None` it must fail closed on rather than
    a book identity that covers half the rows.

    PAIRED ON `declared`, AND IT USED TO ASK FOR A `digest` NOBODY WRITES. Until 2026-09-17 the
    agreement below was taken over `book_identity.digest`, and `floor_book_identity` -- the only
    producer of a floor's book block -- has never emitted that key in its life. So the branch was
    unreachable in the flattering direction: every fold of every real pair fell through to the
    disagreement arm and published `the folded runs name 1 different books (None)`, a sentence
    whose own count contradicts it. Measured on the two members of the served 18-seed family,
    both of which declare `['resi', 'SME']` resolved from the curriculum: the fold returned that
    unknown and dropped `declared` entirely -- and `declared` is the ONLY key the consumer reads
    (`generate_value_arms_data._floor_book_admission`, which falls back to a date-ordering stamp
    proxy when it is absent). The published page therefore admitted its own bound on a PROXY while
    the book was sitting, agreed, in both members. That is why the drawn item read as "the family
    states no book it can show it was drawn over"; the seeds named one all along and this join
    threw it away.

    So the comparison is `run_value_cycle_ab._book_declared` -- the producer's own comparable form,
    imported and not re-copied, for the reason the module docstring gives -- and the success path
    returns the producer's OWN block shape. It does not mint a digest to fill the field it just
    stopped reading: an invented identity would be read as established, and the honest answer is
    that a floor's book IS its declared half. `floor_book_identity.how_a_consumer_should_pair_this`
    says so on every artefact, and this is that instruction obeyed rather than paraphrased.
    """
    missing = [str(path) for path, data in sources if not (data.get("book_identity") or {})]
    if missing:
        return {
            "digest": None,
            "unavailable_because": (
                "this family is folded from runs that do not all name their book: {} carr{} none. "
                "The book identity of the members that do have one does not cover the rows of the "
                "members that do not, so this family states no book rather than one it cannot "
                "show it was drawn over.".format(
                    ", ".join("`{}`".format(m) for m in missing),
                    "ies" if len(missing) == 1 else "y")),
        }
    # A block that EXISTS but declares nothing is the producer's own fail-closed for "some seed in
    # that run recorded no book", and it is a different state from an absent block -- so it is
    # named separately rather than collapsed into the branch above. Both are unknowns; only one of
    # them is about a member that predates the field.
    silent = [str(path) for path, data in sources
              if _book_declared((data.get("book_identity") or {}).get("declared")) is None]
    if silent:
        return {
            "digest": None,
            "unavailable_because": (
                "this family is folded from runs that carry a book block declaring no population: "
                "{} do{} not name a served book. `floor_book_identity` writes that state when a "
                "seed inside the run recorded no book, so the rows it contributes are not known "
                "to be drawn over the same population as the rest and this family states "
                "none.".format(", ".join("`{}`".format(m) for m in silent),
                               "es" if len(silent) == 1 else "")),
        }
    declared = {_book_declared((data.get("book_identity") or {}).get("declared"))
                for _, data in sources}
    if len(declared) > 1:
        return {
            "digest": None,
            "unavailable_because": (
                "the folded runs were drawn over {} different books ({}), so no single book "
                "identity describes these rows.".format(
                    len(declared),
                    ", ".join(sorted("`{}`".format(list(d)) for d in declared)))),
        }
    first = dict(sources[0][1].get("book_identity") or {})
    # The two halves behave in OPPOSITE directions across a fold, exactly as they do across seeds
    # (see `BOOK_DECLARED_FIELDS`): the declared half is what agreement was just proven over and
    # carries forward unchanged, while the realised counts are per-run outcomes of different seed
    # streams. Re-publishing the FIRST member's realised range as the family's would state a range
    # measured over a third of the rows as though it covered all of them, so it is dropped and the
    # members keep their own in `folded_from`.
    first.pop("realised_across_seeds", None)
    first["realised_across_seeds_unavailable_because"] = (
        "a fold does not reconcile the realised half: each member measured its own range over its "
        "own seeds. Read them per member in `folded_from`, and pair on `declared` -- which is the "
        "instruction this artefact's own members carry.")
    first["seeds_reconciled"] = sum(
        (data.get("book_identity") or {}).get("seeds_reconciled") or 0 for _, data in sources)
    first["seeds_that_recorded_no_book"] = sum(
        (data.get("book_identity") or {}).get("seeds_that_recorded_no_book") or 0
        for _, data in sources)
    first["folded_over_members"] = len(sources)
    return first


#: THE BYTES THAT CAN MOVE A FLOOR'S NUMBERS. `simulation/` draws the world and the households,
#: `company/` and `saas/` price the two arms, and `run_value_cycle_ab.py` is the harness that sets
#: the level arm from the value arm's own realised median margin. A member drawn with any of these
#: different is a member drawn by a different instrument. Everything else a commit can touch --
#: site, docs, tests, tooling -- cannot reach a seed row, which is the whole reason this asks about
#: a PATH SET and not about the commit: the two members of the single-arm fold landed on 2026-09-17
#: are two distinct commits three minutes apart whose value arms are byte-identical, and pooling
#: them is correct.
_VALUE_ARM_PATHS = ("simulation/", "company/", "saas/", "tools/run_value_cycle_ab.py")


def _value_arm_diff(commits: list) -> tuple:
    """Paths under `_VALUE_ARM_PATHS` that differ across `commits`, or why it could not be asked.

    Returns `(differing_paths:set, failed:str|None)`. Exactly one of the two is meaningful: on
    failure the path set is empty and MEANS NOTHING, because an empty diff and an unasked diff are
    the same bytes here and only one of them is evidence the arms agree. Every caller must branch
    on `failed` BEFORE reading the set -- collapsing them is the flattering reading.
    """
    import subprocess

    diffs = set()
    for other in commits[1:]:
        try:
            done = subprocess.run(
                ["git", "-C", str(_REPO), "diff", "--name-only", commits[0], other, "--",
                 *_VALUE_ARM_PATHS],
                capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError) as exc:
            return set(), "git could not be run here ({})".format(exc)
        if done.returncode != 0:
            return set(), "git refused the diff {}..{} ({})".format(
                commits[0][:9], other[:9], (done.stderr or "").strip()[:200])
        diffs.update(p for p in done.stdout.splitlines() if p.strip())
    return diffs, None


def _value_arm_pairing(sources: list) -> dict:
    """WHETHER THE MEMBERS OF THIS FOLD WERE DRAWN BY THE SAME PRICING CODE.

    THE DEFECT (2026-09-17, measured). `value_cycle_ab_s1_noise_floor_folded18_20260917.json` --
    the eighteen-seed family the level-vs-selection split publishes -- pools nine seeds drawn on
    `c066c114` with nine drawn on `9f0ab066`. Those two trees do not price the value arm the same
    way. The tree holds the artefact that proves it: `..._20260910.json` re-runs A's OWN nine seeds
    on a tree whose value arm is byte-identical to B's, and every one of the nine returns a
    `selection_gbp` between GBP588.63 and GBP855.45 LOWER -- paired mean -671.31, stdev 98.87,
    sem 32.96, 20.4 sems from zero. That is not noise and the family publishes it as noise.

    WHAT IT COSTS THE FIGURE. Folded across the two arms the family reads mean -624.13, sem 347.16,
    1.80 sems -- no stateable sign, and a price of 23 seeds to get one. Folded so every member sits
    on ONE value arm it reads mean -959.78, sem 384.62, 2.50 sems: the sign IS stateable, it is
    NEGATIVE, and the price is 12 seeds against 18 in hand. The pool is what was standing between
    the page and a sign it had already earned.

    WHY THE EXISTING REASONING SAILS PAST IT. `c21d9209e` refused the AUC fold for this same class
    -- "it would average two operating points and publish the step between them as redraw noise" --
    keyed on `level_gbp_per_mwh`, 38.50/36.25 against 20.00, visible in one column. Here the level
    arm agrees to GBP4.27 across the same paired comparison while the value arm moves GBP671.31.
    The column that caught the AUC fold reads identical on both sides of this one.

    IT ASKS ABOUT A PATH SET, NOT A COMMIT, AND COMMIT IDENTITY IS TOO COARSE IN BOTH DIRECTIONS.
    `producing_commit` already says "N distinct code tree(s)" and has said so on every fold ever
    written, including the good ones -- so that sentence cannot separate the benign case from the
    defect, and a reader who has seen it be harmless learns to skip it. Two commits with identical
    value arms are poolable; two commits one `simulation/` byte apart are not. See
    `_VALUE_ARM_PATHS`.

    STATED UNCONDITIONALLY, ON EVERY BRANCH, for the reason `_floor_tree_pairing` gives at length:
    a reader told nothing when the arms match cannot tell that silence from the tool never having
    asked. So `why_this_rule` is always a sentence and `caveat` carries the amber only when there is
    something to be amber about.

    FAIL-CLOSED WHEN IT CANNOT ASK. No `.git` (a clean `git archive` extract has none), a commit
    that is not in this repository, an unstamped member -- each returns `same_value_arm: None` with
    a named reason, never `True`. A missing answer is not evidence the arms agree, which is exactly
    the error `_floor_tree_pairing` was written to stop making one field earlier.

    KEYED TO THE PROPERTY, NOT TO TODAY'S MEMBERS. Nothing here asserts that today's fold is mixed.
    It asserts that a folded family states whether its members share a value arm -- so the day the
    eighteen are re-drawn on one tree this goes quiet with nobody editing a string, and the day a
    batch arrives from a moved tree it speaks up on its own.
    """
    stamped, unstamped = [], 0
    for _, data in sources:
        commit = (data.get("producing_commit") or {}).get("commit")
        if isinstance(commit, str) and commit.strip():
            if commit not in stamped:
                stamped.append(commit)
        else:
            unstamped += 1

    rule = (
        "A folded family states whether its members were drawn by the same pricing code, over {}. "
        "Two members whose value arms differ are two instruments, and their spread is the step "
        "between them published as redraw noise.".format(", ".join(_VALUE_ARM_PATHS)))
    out = {
        "same_value_arm": None,
        "member_commits": [c[:9] for c in stamped],
        "members_without_a_commit": unstamped,
        "value_arm_paths": list(_VALUE_ARM_PATHS),
        "differing_paths": None,
        "unavailable_because": None,
        "caveat": None,
        "why_this_rule": rule,
        "measured_cost_when_it_last_differed": (
            "GBP671.31 paired on nine identical seeds, 20.4 sems from zero, between `c066c114` and "
            "`9f0ab066` (2026-09-17). Pooling across it moved the selection leg from 2.50 sems and "
            "a stateable NEGATIVE sign to 1.80 sems and no sign at all."),
    }

    if unstamped:
        out["unavailable_because"] = (
            "{} of this fold's {} members carry no producing commit, so the question cannot be "
            "asked of them. An unstamped member was drawn by a tree nobody wrote down -- that is "
            "an unknown and never evidence the arms agree.".format(unstamped, len(sources)))
        out["caveat"] = (
            "This family may pool two pricing instruments and there is no way to tell from disk.")
        return out

    if len(stamped) < 2:
        out["same_value_arm"] = True
        out["differing_paths"] = []
        out["why_this_rule"] = (
            rule + " Every member of this fold names the same commit, so there is one value arm by "
            "construction and no diff to take.")
        return out

    diffs, failed = _value_arm_diff(stamped)

    if failed:
        out["unavailable_because"] = (
            "{}. This repository may be a clean extract with no `.git`, or a member's commit may "
            "not be present here. The arms are NOT assumed to agree: a fold whose provenance "
            "cannot be checked carries an unknown.".format(failed))
        out["caveat"] = (
            "This family may pool two pricing instruments and the check could not be run.")
        return out

    out["same_value_arm"] = not diffs
    out["differing_paths"] = sorted(diffs)
    if diffs:
        out["caveat"] = (
            "THIS FAMILY POOLS {} DISTINCT VALUE ARMS. {} path(s) under {} differ between its "
            "members, so its spread carries the step between two instruments as well as the "
            "redraw. Read `measured_cost_when_it_last_differed` before publishing any bound from "
            "it.".format(len(stamped), len(diffs), ", ".join(_VALUE_ARM_PATHS)))
    return out


def fold(paths: list) -> dict:
    """One floor artefact over the union of several, or a refusal naming the failed question."""
    if len(paths) < 2:
        raise FoldRefused(
            "a fold joins at least two runs; got {}. Folding one run is a file copy wearing a "
            "measurement's name, and this repo already has a census for those.".format(len(paths)))
    resolved = [Path(p) for p in paths]
    duplicated = sorted({str(p) for p in resolved if [str(q) for q in resolved].count(str(p)) > 1})
    if duplicated:
        raise FoldRefused(
            "path(s) {} given more than once. Every seed in them would be counted twice.".format(
                ", ".join("`{}`".format(d) for d in duplicated)))
    sources = [(p, _read(p)) for p in resolved]

    world = _agree_on(sources, "world identity digest (`world_identity.digest`)",
                      lambda d: (d.get("world_identity") or {}).get("digest"))
    mode = _agree_on(sources, "redraw mode (`redraw_scope.mode`)",
                     lambda d: (d.get("redraw_scope") or {}).get("mode"))
    clock = _agree_on(sources, "clock (`clock`)", lambda d: d.get("clock"))
    rows = _seed_rows(sources)

    folded = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "folded": True,
        #: FAIL-CLOSED ON PURPOSE -- see the module docstring. A folded family has no one tree,
        #: and `_floor_tree_pairing` is explicit that a missing stamp is not evidence the trees
        #: agree. The members' commits are in `folded_from` and nothing is lost from disk.
        "producing_commit": {
            "commit": None,
            "resolved_at": None,
            "unavailable_because": (
                "this family is FOLDED from {} runs drawn by {} distinct code tree(s); no single "
                "commit produced these rows. Each member's own producing commit is in "
                "`folded_from`. A bound reading this field gets an unknown rather than the "
                "newest member's commit, because that value would be read as the tree that drew "
                "the whole family and it drew part of it.".format(
                    len(sources),
                    len({(d.get("producing_commit") or {}).get("commit") for _, d in sources}))),
            "resolved_when": (
                "not applicable to a folded family -- the members resolved their own commits at "
                "their own process starts, hours and sometimes days apart"),
            "why_this_is_here": (
                "A consumer that publishes counts from this family needs to know which code drew "
                "them. For a fold the honest answer is `several, listed in folded_from`, and the "
                "field that can only hold one says so rather than picking."),
        },
        "world_identity": dict(sources[0][1].get("world_identity") or {}),
        "book_identity": _book_identity(sources),
        #: THE PAIRING QUESTION `producing_commit` ABOVE CANNOT ANSWER. It says how many trees
        #: drew these rows; this says whether those trees priced the arms the same way, which is
        #: the only half of the provenance that can reach a seed row. See `_value_arm_pairing`.
        "value_arm_pairing": _value_arm_pairing(sources),
        "report_end": sources[0][1].get("report_end"),
        "what_this_is": (
            "The three-arm A/B re-run once per seed with ONLY the per-household elasticity "
            "assignment re-drawn, FOLDED across {} runs of the same world into one family of {} "
            "seeds. The spread below is the error bar on `selection_gbp` -- the figure the "
            "level-vs-selection split publishes.".format(len(sources), len(rows))),
        "clock": clock,
        "redraw_scope": dict(sources[0][1].get("redraw_scope") or {}),
        "symbol_patched": sources[0][1].get("symbol_patched"),
        "symbol_resolution": sources[0][1].get("symbol_resolution"),
        "seeds": rows,
        #: WHAT WAS JOINED, so the fold is reversible by reading and never only by re-running. A
        #: reader who distrusts the join can take any member out and recompute.
        "folded_from": [
            {
                "path": str(Path(path).relative_to(_REPO)
                            if Path(path).is_absolute() and str(path).startswith(str(_REPO))
                            else path),
                "generated_at": data.get("generated_at"),
                "producing_commit": (data.get("producing_commit") or {}).get("commit"),
                #: THE DECLARED HALF, for the reason `_book_identity` gives at length: this read
                #: asked for a `digest` no producer of a floor block has ever written, so every
                #: member of every family recorded `null` here and the per-member record could not
                #: contradict a family-level unknown it was the evidence for.
                "book_identity": (data.get("book_identity") or {}).get("declared"),
                "n": len(data.get("seeds") or []),
                "seeds": [r.get("seed") for r in (data.get("seeds") or [])],
            }
            for path, data in sources
        ],
        "how_to_read_this": (
            "If the spread is WIDER than the published `selection_gbp`, the level-vs-selection "
            "instrument cannot yet resolve the question being asked of it, and every reading "
            "built on it carries that caveat. That is a finding about the INSTRUMENT and not "
            "about the pricing arm -- it is not a cue to re-run until a seed agrees (R12). THIS "
            "FAMILY IS FOLDED: the rows come from {} runs of world `{}` in redraw mode `{}`, and "
            "the members are named in `folded_from`. What a fold does NOT remove is that runs "
            "made by different trees can return different values for the same seed; the spread "
            "below carries that difference and `producing_commit` states it as an unknown rather "
            "than naming one tree for rows several trees drew.".format(
                len(sources), world, mode)),
    }
    folded.update(summarise(rows))
    return folded


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fold several noise-floor runs of one world into one seed family.")
    parser.add_argument("sources", nargs="+",
                        help="two or more floor artefacts to join; every one of them must name "
                             "the same world, redraw mode and clock, and no seed may repeat")
    parser.add_argument("--out", required=True,
                        help="where the folded family is written. REQUIRED and never defaulted: "
                             "a fold that overwrites a source by default would destroy the "
                             "evidence it was folded from")
    args = parser.parse_args(argv)

    out = Path(args.out)
    try:
        if str(out.resolve()) in {str(Path(s).resolve()) for s in args.sources}:
            raise FoldRefused(
                "`--out {}` is one of the sources. A fold that overwrites a member destroys the "
                "family it was folded from, and `folded_from` would then point at a file that no "
                "longer holds those rows.".format(args.out))
        folded = fold(args.sources)
    except FoldRefused as exc:
        print("REFUSED: {}".format(exc))
        return 2

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(folded, indent=1) + "\n", encoding="utf-8")
    sel = folded["selection_gbp_spread"]
    sem = folded["selection_sem_gbp"]
    print("folded {} run(s) -> {} seeds -> {}".format(
        len(folded["folded_from"]), sel["n"], out))
    print("  selection_gbp: mean {:.2f}  stdev {:.2f}  sem {:.2f}  sems from zero {:.3f}".format(
        sel["mean"], sel["stdev"], sem, abs(sel["mean"]) / sem))
    # THE BAR IS READ BACK OFF THE ARTEFACT THIS CALL JUST WROTE, never recomputed for the print.
    # An operator deciding whether to publish reads this line, not the JSON, and a bar computed a
    # second time here could differ from the one the verdict beside it was actually taken at.
    print("  distinguishable from zero at {} sems (this family's own bar, t on {} df): {}".format(
        folded["selection_sems_needed_to_state_a_sign"], sel["n"] - 1,
        folded["selection_distinguishable_from_zero"]))
    #: THE DRAW COUNT BESIDE THE SEED COUNT, on the same surface as the sem it qualifies. An
    #: operator reading "18 seeds, sem 603, sign stateable" and deciding to publish is reading a
    #: confidence the family may not be entitled to; the line below is the one that says so, and
    #: it prints on every branch so silence means "asked and every seed was a fresh draw".
    draws = folded["priced_decision_draws"]
    if draws["draws_the_spread_is_entitled_to"] is not None:
        print("  distinct priced decision sets: {} over {} seeds ({} repeated draw(s))".format(
            draws["draws_the_spread_is_entitled_to"], draws["seeds_in_family"],
            draws["seeds_in_family"] - draws["draws_the_spread_is_entitled_to"]))
    elif draws["at_least"] == draws["at_most"]:
        print("  distinct priced decision sets: {} over {} seeds -- no row records one, but the "
              "residual floor leaves no room for a repeat (deduced, not recorded)".format(
                  draws["at_most"], draws["seeds_in_family"]))
    else:
        print("  distinct priced decision sets: BETWEEN {} AND {} over {} seeds -- {} row(s) "
              "record none. The sem above is an upper bound on this family's confidence.".format(
                  draws["at_least"], draws["at_most"], draws["seeds_in_family"],
                  draws["seeds_with_an_unknown_decision_set"]))
    if not draws["the_residual_floor_holds"]:
        print("  RESIDUAL FLOOR REFUTED on this family: {} fingerprint(s) appear on seeds whose "
              "residuals differ.".format(len(draws["the_residual_floor_is_refuted_by"])))
    #: ON THE SURFACE, NOT ONLY IN THE FILE. The operator who runs this is the one deciding whether
    #: to publish the family, and a caveat they have to open the JSON to find is a caveat they will
    #: publish without. Printed on every branch, so silence here means "asked and matched" and
    #: never "never asked".
    pairing = folded["value_arm_pairing"]
    if pairing["caveat"]:
        print("  VALUE ARM: {}".format(pairing["caveat"]))
        for path in (pairing["differing_paths"] or [])[:10]:
            print("    differs: {}".format(path))
    else:
        print("  value arm: one instrument across all {} member(s)".format(
            len(folded["folded_from"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
