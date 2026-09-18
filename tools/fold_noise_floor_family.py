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
from tools.run_value_cycle_ab import _book_declared, _spread, distance_to_a_sign

_REPO = Path(__file__).resolve().parent.parent

#: `noise_floor` computes this inline as `abs(mean) > 2 * sem`. It is restated here rather than
#: imported because it is one line inside a three-hundred-line run function with no seam to import
#: -- and it is pinned to the producer's answer on the real artefact by
#: `test_the_fold_reproduces_the_producers_own_summary_on_the_family_already_on_disk`, so the two
#: cannot drift silently. If that test ever goes red, the producer moved and this must follow it.
_DISTINGUISHABLE_SEMS = 2


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
                raise FoldRefused(
                    "seed {} appears in both `{}` and `{}`. Folding it would count one draw "
                    "twice: `n` rises and the standard error shrinks by a factor that measures "
                    "nothing, and the artefact that comes out is well-formed, so no consumer "
                    "could tell.".format(seed, where[seed], path))
            where[seed] = str(path)
            rows.append(row)
    return rows


def _leg(rows: list, key: str) -> dict:
    """One leg's spread, standard error and sign verdict, under the bar BOTH legs are judged at.

    THE BAR IS `_DISTINGUISHABLE_SEMS` AND NOT A SECOND ONE. The whole use of a level leg beside a
    selection leg is the CONTRAST between their verdicts -- "one leg's sign is stateable and the
    other's is not" is a claim about the two legs, and it is only a claim about the legs if both
    were asked the same question. Judging the level leg at a different bar would make the contrast
    an artefact of the rule rather than of the data, which is this project's most expensive shape
    wearing a statistic's clothes.
    """
    spread = _spread([r.get(key) for r in rows])
    sem = None
    distinguishable = None
    if spread["stdev"] is not None and spread["n"] > 1:
        sem = spread["stdev"] / math.sqrt(spread["n"])
        distinguishable = abs(spread["mean"]) > _DISTINGUISHABLE_SEMS * sem
    values = [r.get(key) for r in rows if isinstance(r.get(key), (int, float))
              and not isinstance(r.get(key), bool)]
    positive = sum(1 for v in values if v > 0)
    return {
        "spread": spread,
        "sem_gbp": sem,
        "distinguishable_from_zero": distinguishable,
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
        # The legs, each carrying its own verdict under the same bar. `selection_leg` restates the
        # four above rather than replacing them -- a consumer reading either gets one answer.
        "selection_leg": selection,
        "level_leg": level,
        "value_leg": value,
        "discrimination_auc_across_seeds": _auc_across_seeds(rows),
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
    import subprocess

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

    diffs, failed = set(), None
    for other in stamped[1:]:
        try:
            done = subprocess.run(
                ["git", "-C", str(_REPO), "diff", "--name-only", stamped[0], other, "--",
                 *_VALUE_ARM_PATHS],
                capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError) as exc:
            failed = "git could not be run here ({})".format(exc)
            break
        if done.returncode != 0:
            failed = "git refused the diff {}..{} ({})".format(
                stamped[0][:9], other[:9], (done.stderr or "").strip()[:200])
            break
        diffs.update(p for p in done.stdout.splitlines() if p.strip())

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
    print("  distinguishable from zero at {} sems: {}".format(
        _DISTINGUISHABLE_SEMS, folded["selection_distinguishable_from_zero"]))
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
