#!/usr/bin/env python3
"""The delivery record the director can open: what the machine did, decided, got wrong, next.

REUSE: tools/generate_delivery_page.py
CLASS: PATTERN-REUSE
INDEX: searched "generate_", "site/data", "director", "delta", "harness", "status". The
       GENERATOR pattern is `tools/generate_director_data.py` and its siblings -- read the
       committed record, write one JSON under `site/data/`, never compute a second version of a
       number that already exists. `generate_director_data.py` is the nearest neighbour and is
       NOT the same thing: it answers "what changed since you last looked" against a stamp, and
       this answers "what has the machine been doing and deciding", against the delivery seat's
       own record. Both feed the SAME page and neither recomputes the other.

WHY IT EXISTS
-------------
Director, 2026-08-25: *"I can't see any of this without someone reading git logs to me. I want to
open one page and know what the machine did, what it decided, what it got wrong, and what it's
doing next. Harness was meant to be that and isn't."*

Four questions, in that order, and this file produces exactly those four keys. Anything that is
not one of the four belongs somewhere else on the page.

WHAT IT DOES NOT DO, and the restraint is the design: it computes nothing. Every figure is read
from a committed record -- git, `docs/direction/decisions.jsonl`, `DIRECTION.yaml`. A generator
that derives its own numbers becomes a second opinion, and the first time it disagrees with the
record nobody can tell which is wrong.

Run:  python3 -m tools.generate_delivery_page
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from background import direction as direction_mod

# THE GATE DECLARATION, IMPORTED RATHER THAN RESTATED. `A49_GATING_RUNG` and `the_a49_gate` live in
# the instrument beside `OBSERVABLE_FIELD_SCOPE`, which is what decides them; this module calls the
# same function on the artefact it reads so the page and the record cannot come to disagree about
# which rung is the gate. That is still a LIFT and not a computation -- the readings are the
# artefact's and the choice is the instrument's constant; nothing here derives a number.
from tools.r1_inference_ceiling import the_a49_gate

# THE OTHER TWO INSTRUMENTS A49 EXISTS FOR, imported for the SAME reason as the line above: each
# module owns where its artefact lives, and a generator that restated those paths would be a second
# opinion about which file is the record. Importing `OUT_PATH` also wires both modules to something
# that actually runs -- until 2026-09-07 they were reachable from no committed schedule and read as
# orphans, which is the honest description of an instrument whose reading nobody ever sees.
from tools.r3_carbon_score_ceiling import OUT_PATH as R3_ARTEFACT
from tools.r4_product_ceiling import OUT_PATH as R4_ARTEFACT

PROJECT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT / "site" / "data" / "delivery.json"

#: How many recent commits the "what it did" panel carries. Enough to see a stretch, few enough
#: that the page is a record and not a log -- a log is what the director said he cannot read.
COMMIT_WINDOW = 40


def _git(*args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=str(PROJECT), capture_output=True,
                             text=True, timeout=60)
        return out.stdout if out.returncode == 0 else ""
    except Exception:
        return ""


def what_it_did(limit: int = COMMIT_WINDOW) -> dict:
    """The commits, split substantive vs mechanical by the SAME classifier the daily self-note
    uses. The split is the honest half: an auto-process republish is not work, and a page that
    counts it as work flatters exactly the way that note's design warns about."""
    try:
        from background.daily_self_note import _is_substantive_file
    except Exception:
        return {"available": False,
                "why": "the substantive-commit classifier could not be imported, and guessing "
                       "would flatter"}
    raw = _git("log", f"-{limit}", "--pretty=format:%H%x00%aI%x00%s", "--name-only")
    rows, current = [], None
    for line in raw.splitlines():
        if line.count("\x00") == 2:
            if current:
                rows.append(current)
            sha, when, subject = line.split("\x00")
            current = {"sha": sha[:9], "at": when, "subject": subject, "_files": []}
        elif line.strip() and current is not None:
            current["_files"].append(line.strip())
    if current:
        rows.append(current)
    for row in rows:
        row["substantive"] = any(_is_substantive_file(f) for f in row.pop("_files"))
    return {
        "available": True,
        "commits": rows,
        "substantive": sum(1 for r in rows if r["substantive"]),
        "mechanical": sum(1 for r in rows if not r["substantive"]),
        "what_the_split_means": (
            "A mechanical commit republishes an unchanged net -- the report, the dashboard, the "
            "state files. Counting those as work would make a quiet day look busy, so they are "
            "separated rather than filtered: they happened, they are just not progress."
        ),
    }


def what_it_decided() -> dict:
    """The live direction and the decisions behind it, verbatim from the seat's own record."""
    live = direction_mod.read_direction()
    rows = direction_mod.read_decisions(limit=20)
    oriented = [r for r in rows if r.get("outcome") == "oriented"]
    if live is None:
        return {
            "available": False,
            "why": (
                "there is no valid direction record right now. The draw is unaffected -- direction "
                "biases it and never gates it -- so this means the machine is working from its "
                "standing priorities, not that it has stopped."
            ),
            "recent": rows[:5],
        }
    return {
        "available": True,
        "oriented_at": live.oriented_at.isoformat(),
        "age_hours": round(live.age_hours(), 1),
        "expires_after_hours": direction_mod.FOCUS_MAX_AGE_HOURS,
        "live": live.is_live(),
        "thesis_read": live.thesis_read,
        "focus": [dict(r) for r in live.focus],
        "not_now": [dict(r) for r in live.not_now],
        "for_the_director": [dict(r) for r in live.for_the_director],
        "orientations_recorded": len(oriented),
        "skips_recorded": sum(1 for r in rows if r.get("outcome") == "skipped"),
        "refusals_recorded": sum(1 for r in rows if r.get("outcome") == "refused"),
    }


def what_it_got_wrong() -> dict:
    """Errors the seat recorded, and whether they were corrected.

    THIS PANEL IS ALLOWED TO BE EMPTY AND IS NOT ALLOWED TO BE ABSENT. A machine that reports no
    mistakes is either not looking or not saying, and both read identically from outside -- so
    when there is nothing here the page says which of the two it is.
    """
    rows = direction_mod.read_decisions(limit=40)
    wrong = []
    for row in rows:
        # THE CORRECTION STATE IS HALF THE RECORD AND WAS SERVED ON NONE OF IT until 2026-09-03.
        # `direction_mod.wrong_rows` reads both stored shapes and returns `corrected: None` for
        # the rows written before the field survived the hop -- and `None` is published as
        # "not recorded", never folded into "not corrected", because a panel that reports an
        # unknown as a failure is making a claim the record does not carry.
        for item in direction_mod.wrong_rows(row):
            wrong.append({"at": row.get("at"), "what": item["what"],
                          "corrected": item["corrected"]})
    refused = [{"at": r.get("at"), "problems": r.get("problems") or []}
               for r in rows if r.get("outcome") == "refused"]
    graded = [w for w in wrong if w["corrected"] is not None]
    return {
        "entries": wrong,
        "refused_own_records": refused,
        "outstanding": sum(1 for w in graded if not w["corrected"]),
        "corrected": sum(1 for w in graded if w["corrected"]),
        "correction_not_recorded": len(wrong) - len(graded),
        "empty_means": (
            "no orientation has recorded an error yet" if not wrong and rows else
            "nothing has been recorded here at all, which means the seat has not run -- not that "
            "nothing went wrong" if not rows else ""
        ),
    }


def what_next() -> dict:
    """The focus, and -- the part that matters -- whether the LAST focus actually got drawn.

    A steer that quietly does nothing looks identical from outside to a steer that was taken.
    `d7d36b46a` records two soft guards composing into a no-op while an atom sat through 1,307
    unchanged draws. So the page reports the steer's own effectiveness beside its content, and a
    run of `steered: false` is the page telling on itself.
    """
    rows = direction_mod.read_decisions(limit=10)
    checks = [r.get("previous_focus_drawn") for r in rows if r.get("previous_focus_drawn")]
    with_focus = [c for c in checks if c.get("focus")]
    return {
        "focus": list(direction_mod.current_focus()),
        "steer_checks": checks[:5],
        "steered_recently": any(c.get("steered") for c in with_focus),
        "why_this_is_here": (
            "Direction multiplies the draw's existing weights and can never zero one, so it can "
            "only ever be ignored -- never obeyed by force. Whether it was actually followed is "
            "therefore a measurement, not an assumption."
        ),
    }


def _redraw_panel(stability: dict | None) -> dict:
    """The stability rung, rendered for a reader — or an explicit statement that it was not run.

    A49 gates R3 and R4 on the figure this panel carries, so the question a reader most needs
    answered is not "what is the number" but "would it be the same number tomorrow". On this book it
    would not: the verdict is constant within a coverage regime and opposite between two of them.
    That is the single most decision-relevant fact about the figure and it lived only in a staged
    finding until now.
    """
    if not stability:
        return {"measured": False,
                "why": "the stability rung has not been run in this tree, so whether this verdict "
                       "survives a different draw of the book is UNKNOWN — which is not the same "
                       "as it being stable. Run `python3 -m tools.r1_inference_ceiling "
                       "--stability` in a tree holding the run outputs."}
    return {
        "measured": True,
        "runs_measured": stability.get("runs_measured"),
        "verdict_is_the_same_on_every_run": stability.get("unanimous"),
        "clears_count": stability.get("clears_count"),
        "cannot_tell_count": stability.get("cannot_tell_count"),
        "p_value_range": stability.get("p_value_range"),
        "households_range": stability.get("households_range"),
        "ceiling_range": stability.get("ceiling_range"),
        "verdict_is_a_step_function_of_coverage": stability.get(
            "verdict_is_a_step_function_of_coverage"),
        "coverage_regimes": stability.get("coverage_regimes"),
        "what_these_runs_are": stability.get("what_these_runs_are"),
    }


def the_number_the_programme_rests_on() -> dict:
    """R1's inference ceiling, READ from the instrument's committed artefact.

    WHY THIS PANEL EXISTS AND WHY IT IS ON THIS PAGE. `A49` makes this one figure the gate on
    whether R3 and R4 can pay at all, and for two days it was published as a bound while being the
    winner of a 45-way search graded against the null of a single comparison. The number moved when
    the null was corrected to run the same selection, and a page that carried the first figure and
    not the second would be the machine reporting its own best draw.

    IT COMPUTES NOTHING, which is this generator's whole discipline: every value is lifted from
    `docs/observability/r1_inference_ceiling.json`, written by `tools/r1_inference_ceiling.py`. If
    the artefact is absent the panel says so rather than showing an old figure -- an ABSENT bound
    and an UNCLEARED one are different claims and both are different from a stale one.
    """
    path = PROJECT / "docs" / "observability" / "r1_inference_ceiling.json"
    if not path.is_file():
        return {"available": False,
                "why": "the inference-ceiling instrument has not been run in this tree, so no "
                       "bound is shown. That is not the same as the bound being zero."}
    try:
        got = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"available": False,
                "why": "the inference-ceiling artefact could not be read, so no bound is shown."}
    if "selection_corrected_verdict" not in got:
        # AN ARTEFACT FROM BEFORE THE CORRECTION IS NOT A HALF-FILLED PANEL. Rendering it would put
        # the selected maximum back on the page with every corrected field blank, which is the
        # exact publication this repair exists to undo.
        return {"available": False,
                "why": "the inference-ceiling artefact in this tree predates the selection "
                       "correction, so its figure is the winner of a 45-way search graded against "
                       "the odds of one comparison. It is withheld rather than shown: re-run "
                       "`python3 -m tools.r1_inference_ceiling` to publish a corrected bound."}
    headline = got.get("we_cannot_tell") or {}
    verdict = got.get("selection_corrected_verdict") or {}
    null = got.get("selection_corrected_null") or {}
    best = got.get("best_pair") or {}
    controls = got.get("controls") or {}
    magnitude = got.get("magnitude_three_way_split") or {}
    full_magnitude = got.get("magnitude_three_way_split_full_coverage") or {}
    # THE RUNG THAT CAN ACTUALLY BE POWERED ON THIS BOOK, and it reached no surface for a day.
    # `whole_book_pair_rung` landed on 2026-09-06 carrying the only unbiased magnitude this book
    # buys -- the same pair search restricted to the observables the company holds for EVERY
    # account on supply, so its population is the book's 164 and not the winning pair's 69. The
    # instrument computed it, printed it to stdout and wrote it to the artefact; this generator
    # lifted the two rungs beside it and not this one, so the panel A49 reads published
    # `magnitude: null` while the artefact held +0.2513 at p=0.01. Lifted, never computed.
    book_rung = got.get("whole_book_pair_rung") or {}
    book_magnitude = book_rung.get("magnitude_three_way_split") or {}
    book_best = book_rung.get("best_pair") or {}
    return {
        "available": True,
        "run_output": got.get("run_output"),
        "households_in_the_rung": best.get("n"),
        # THE BOOK THE RUNG SITS IN, and it is here because it was WRONG on the page for two days.
        # A run output's `customer_id` is a supply point, and a household's gas leg is registered
        # under its electricity point's id plus a suffix -- so the instrument counted 64 dual-fuel
        # households twice, mis-keyed 18 gas-only ones, reported 213 where there were 149, and
        # graded all 82 gas-leg rows against an elasticity the lookup invented by hashing a leg id.
        # A reader given "69 households in the rung" and no denominator cannot see that at all.
        "households_in_the_book": got.get("households"),
        "supply_point_legs_folded": (got.get("leg_fold_census") or {}).get(
            "supply_point_legs_folded_into_a_household"),
        "reported_ceiling": best.get("held_out"),
        "in_sample": best.get("in_sample"),
        "candidates_searched": got.get("pairs_scored"),
        "uncorrected_verdict": got.get("ceiling_clears_the_null_uncorrected_per_pair"),
        "corrected_verdict": got.get("ceiling_clears_the_null"),
        "p_value": verdict.get("p_value"),
        "alpha": verdict.get("alpha"),
        "bound_p95": verdict.get("bound_p95"),
        "margin_over_bound": verdict.get("margin_over_bound"),
        "shuffled_worlds": null.get("draws"),
        # THE TELL THAT WAS INSIDE THE PUBLISHED FIGURE while the control named for it read green,
        # because that control asks about MOST pairs and the page carries the WINNER. It is lifted
        # like everything else here and it is NOT a verdict: the p-value already contains the
        # selection, and a shuffled world's winner overshoots its own fit too.
        "winner_outscores_its_own_fit": controls.get(
            "held_out_exceeds_in_sample_on_the_reported_winner"),
        "winner_held_out_over_in_sample": controls.get(
            "reported_winner_held_out_over_in_sample"),
        "statement": headline.get("statement"),
        "what_it_does_not_say": headline.get("what_it_does_not_say"),
        # HOW BIG, WHICH IS NOT THE SAME CLAIM AS WHETHER, and the panel carried only the second.
        # `reported_ceiling` above is the largest of a 45-way search ranked on the fold it is then
        # reported from, so it is biased UP as an estimate even on a book where it clears. These
        # fields are the de-biased reading, and `magnitude` is `None` whenever the rung cannot buy
        # one -- which is the state A49's gate has to be able to see. Lifted, never computed.
        "magnitude": magnitude.get("estimate"),
        "magnitude_refused": magnitude.get("refused"),
        "magnitude_under_powered_reading": magnitude.get("under_powered_reading"),
        "magnitude_noise_floor": magnitude.get("bound_abs_p95"),
        "magnitude_at_full_coverage": full_magnitude.get("estimate"),
        # THE NARROWER RUNG, PUBLISHED BESIDE THE ONE ABOVE AND NEVER INSTEAD OF IT. It answers a
        # DIFFERENT question over a DIFFERENT population -- "what can be recovered from what the
        # company holds about every account" rather than "about the accounts that renewed" -- and
        # the reason its numbers differ is the population, not the estimator. Its own ceiling
        # verdict travels with it because the two disagree on this book: the selected-maximum
        # verdict cannot tell (p=0.47) while the de-biased magnitude clears its floor (p=0.01), and
        # a magnitude published without that beside it would read as a bound the rung has not
        # earned. `whole_book_magnitude` is `None` whenever this rung cannot buy one either.
        "the_whole_book_rung": {
            "fields": book_rung.get("fields"),
            "pairs_scored": book_rung.get("pairs_scored"),
            "households": book_best.get("n"),
            "reported_ceiling": book_best.get("held_out"),
            "corrected_verdict": book_rung.get("clears_the_selection_corrected_null"),
            "p_value": (book_rung.get("selection_corrected_verdict") or {}).get("p_value"),
            "magnitude": book_magnitude.get("estimate"),
            "magnitude_noise_floor": book_magnitude.get("bound_abs_p95"),
            "magnitude_p_value": book_magnitude.get("p_value"),
            "magnitude_refused": book_magnitude.get("refused"),
            "households_per_cell_on_the_fit_fold": book_magnitude.get(
                "households_per_cell_on_the_fit_fold"),
        } if book_rung else None,
        # WHICH OF THE TWO RUNGS ABOVE A49 ACTUALLY GATES R3 AND R4 ON, which until 2026-09-07 was
        # nobody's: both rungs reached this panel, they answer different questions over different
        # populations, and the reader was left to pick. Choosing whichever one had a number would
        # have been the outcome-driven selection the scope mechanism exists to prevent, so the
        # choice is a constant in the instrument -- read `A49_GATING_RUNG` for the argument -- and
        # this field carries it together with whatever that rung says today, INCLUDING a refusal.
        "the_a49_gate": the_a49_gate(got),
        # WHAT THE SEARCH ALONE WAS WORTH, at a fit fold held the same size so it is attributable to
        # the selection and to nothing else.
        "selection_inflation": (got.get("magnitude_three_way_split_detail") or {}).get(
            "selection_inflation"),
        "on_the_magnitude": headline.get("on_the_magnitude"),
        # DOES THIS VERDICT DESCRIBE THE WORLD, OR THE FILE THE INSTRUMENT HAPPENED TO READ?
        # Lifted, never computed, like everything else on this panel. `measured: False` is rendered
        # as UNMEASURED and never as agreement -- an unrun stability rung and a stable one are
        # different claims, and only one of them is evidence about the number above it.
        "does_the_verdict_survive_a_redraw": _redraw_panel(got.get("verdict_stability")),
        "why_both_figures_are_shown": (
            "The first number is what a search of "
            f"{got.get('pairs_scored')} candidate pairs returned, compared against the odds of ONE "
            "of them coming up by chance. The second compares it against the odds of the BEST OF "
            "ALL of them coming up by chance, which is the thing that actually happened. Both are "
            "shown because deleting the flattering one would hide that it was ever published."
        ),
    }


def _read_artefact(path: Path, subject: str, required_field: str, stale_why: str) -> tuple:
    """Read one instrument's committed artefact, or say WHY there is nothing to show.

    THREE ABSENCES THAT ARE NOT THE SAME CLAIM, and a panel that collapses them lies in the reader's
    favour: NOT RUN (no bound has been measured), UNREADABLE (a bound may exist and we cannot see
    it), and STALE (a bound exists and is from before a correction that moved it). Only the last of
    those is a reason to withhold a number that is sitting right there, so it is the one that has to
    name the correction it is missing. None of them is the same as the bound being zero.
    """
    if not path.is_file():
        return None, {"available": False,
                      "why": f"the {subject} instrument has not been run in this tree, so no bound "
                             f"is shown. That is not the same as the bound being zero. Run "
                             f"`python3 -m {path.stem} --save` in a tree holding the run outputs."}
    try:
        got = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None, {"available": False,
                      "why": f"the {subject} artefact could not be read, so no bound is shown."}
    if required_field not in got:
        return None, {"available": False, "why": stale_why}
    return got, None


def the_most_a_carbon_score_could_be_worth() -> dict:
    """R3's timing ceiling, READ from the instrument's committed artefact.

    WHY IT IS ON THIS PAGE. A49 required a ceiling per side before either programme is built, and
    R3's landed on 2026-09-07 into a file nobody opens. A bound that reaches no reader cannot retire
    a candidate programme, which is the entire thing ceilings are for -- EP13 ran twelve passes and
    the discipline arrived at pass seven, retiring five programmes that would otherwise have been
    built first and measured afterwards.

    THE SHAPE OF THE ANSWER MATTERS MORE THAN THE NUMBER, so the panel carries both. The headline is
    at a shiftable share of 1.0 -- every kWh in the home moved -- because NO PUBLISHED SOURCE
    ESTABLISHES A DOMESTIC SHIFTABLE SHARE, and a number invented for that slot would be load-bearing
    within a week. The curve is published instead, and the reader scales it themselves.

    IT COMPUTES NOTHING, like every panel here. Two implementations of one quantity is how a figure
    comes to have two values and no owner; this repository has already paid for that once.
    """
    got, absent = _read_artefact(
        R3_ARTEFACT, "carbon-timing-ceiling", "corrected_headline",
        "the carbon-timing artefact in this tree predates the within-day correction, so its figure "
        "is the raw forecast ceiling with the feed's own measured overstatement still inside it. It "
        "is withheld rather than shown: re-run `python3 -m tools.r3_carbon_score_ceiling --save`.")
    if absent:
        return absent
    headline = got.get("corrected_headline") or {}
    verdict = got.get("verdict") or {}
    world = got.get("world") or {}
    trend = got.get("typical_day_cross_check") or {}
    return {
        "available": True,
        "run_output": (got.get("book") or {}).get("source_run"),
        "households": (got.get("book") or {}).get("households"),
        "bound_kind": got.get("bound_kind"),
        "bound_kind_reason": got.get("bound_kind_reason"),
        # WHAT THIS BOUND DOES NOT COVER, carried beside it and never behind it. R3 bounds the
        # TIMING lever on ELECTRICITY; the instrument names six levers it says nothing about, and a
        # reader shown "91.7 kg" without them would read a bound on the whole carbon programme.
        "bound_scope": got.get("bound_scope"),
        "not_bounded_by_this": got.get("not_bounded_by_this"),
        "kg_co2e_per_household_year": headline.get("kg_co2e_per_household_year"),
        "gbp_per_household_year": headline.get("gbp_per_household_year"),
        "g_co2e_per_shifted_kwh": headline.get("g_co2e_per_shifted_kwh"),
        "at_shiftable_share": 1.0,
        # THE HANDICAPS, PUBLISHED AS SEPARATE STEPS rather than folded into one corrected figure.
        # Perfect foreknowledge -> what the published forecast actually captures -> divided by the
        # feed's own measured within-day overstatement. A reader who cannot see the ladder cannot
        # tell which step they disagree with.
        "hindsight_g_per_kwh": ((got.get("rungs") or {}).get("hindsight_ceiling") or {}).get(
            "g_co2e_per_shifted_kwh"),
        "forecast_capture": (got.get("forecast_capture") or {}).get("capture_mean"),
        "within_day_overstatement": (got.get("within_day_overstatement") or {}).get("mean"),
        "null_g_per_kwh": ((got.get("rungs") or {}).get("null_ceiling") or {}).get(
            "g_co2e_per_shifted_kwh"),
        "clears_the_null": verdict.get("clears_the_null"),
        "hindsight_over_null": verdict.get("hindsight_over_null"),
        "retires_time_shifting": verdict.get("retires_time_shifting"),
        # THE CURVE, BECAUSE THE HEADLINE'S DENOMINATOR IS NOT ESTABLISHED. This is the honest
        # `None` made useful: we cannot say what share of a home's load is shiftable, so we publish
        # what the bound is at every share and refuse to pick one.
        "shiftable_share_curve": got.get("shiftable_share_curve"),
        # AND IT IS SHRINKING, which is the fact that decides WHEN rather than WHETHER. A programme
        # worth less every year it is not built is a different decision from a small one.
        "trend_change_pct": trend.get("change_pct"),
        "trend_first_year": trend.get("first_year"),
        "trend_last_year": trend.get("last_year"),
        "trend_reads": trend.get("reads"),
        "carbon_value_gbp_per_tonne": (got.get("carbon_value") or {}).get("gbp_per_tonne"),
        "carbon_value_basis": (got.get("carbon_value") or {}).get("basis"),
        "days_measured": world.get("days"),
        "years_measured": world.get("years"),
        "named_gaps": got.get("named_gaps"),
        "caveats": got.get("caveats"),
        "statement": got.get("headline"),
    }


def the_most_the_products_beyond_price_could_be_worth() -> dict:
    """R4's product ceiling, READ from the instrument's committed artefact.

    THE SPLIT IS THE DELIVERABLE AND THE PANEL IS BUILT AROUND IT. Three of R4's six products are
    true CEILINGS -- a negative retires them outright -- and three are FLOORS, which retire nothing,
    because the company holds no property attribute to target on. Conflating those two is the error
    EP13's tenth pass made and its eleventh corrected, so this panel never renders an arm without
    the kind of bound beside it.

    AND THE ANSWER A49 WAS MINTED FOR IS ONE SENTENCE: the part of R4 this book can bound is the
    part that CANNOT ABATE, and the part that abates is the part we cannot bound. That is the
    canon's own charge -- "the company can make a household cheaper and never greener" -- as
    arithmetic rather than as a worry, and it belongs where the director can read it.

    IT COMPUTES NOTHING. The `refuses_to_total` line is the instrument's, not this generator's: the
    arms are not disjoint (advice is the channel for the others) and summing them would double-count.
    """
    got, absent = _read_artefact(
        R4_ARTEFACT, "product-ceiling", "verdict",
        "the product-ceiling artefact in this tree predates the ceiling/floor split, which IS the "
        "finding. It is withheld rather than shown as a list of numbers whose kind is unstated: "
        "re-run `python3 -m tools.r4_product_ceiling --save`.")
    if absent:
        return absent
    verdict = got.get("verdict") or {}
    arms = got.get("arms") or {}
    census = got.get("fabric_eligibility") or {}
    time_shifting = arms.get("time_shifting") or {}
    return {
        "available": True,
        "run_output": (got.get("book") or {}).get("source_run"),
        "households": (got.get("book") or {}).get("households"),
        "bound_kind": got.get("bound_kind"),
        "bound_kind_reason": got.get("bound_kind_reason"),
        "ceilings": verdict.get("ceilings"),
        "floors": verdict.get("floors"),
        # THE TWO-SIDED SENTENCE, LIFTED AS TWO FIELDS SO NEITHER CAN BE DROPPED. `abates` is the
        # arm with carbon and no bill saving; `does_not` is the arm with pounds and carbon of
        # exactly zero by the director's standing rule -- discounting changes no kWh and no hour.
        "the_arm_that_abates": verdict.get("the_bounded_arm_that_abates"),
        "the_arm_that_does_not": verdict.get("the_bounded_arm_that_does_not"),
        "arms": [
            {
                "product": name,
                "bound_kind": arm.get("bound_kind"),
                "gbp_per_household_year": arm.get("gbp_per_household_year"),
                "kg_co2e_per_household_year": arm.get("kg_co2e_per_household_year"),
                "carbon_value_gbp_per_household_year": arm.get(
                    "carbon_value_gbp_per_household_year"),
                "why": (arm.get("why_a_ceiling") or arm.get("why_a_floor_and_not_a_ceiling")
                        or arm.get("why") or ""),
                "missing_data": arm.get("missing_data"),
                "carbon_is_zero_by_rule": arm.get("carbon_is_zero_by_rule"),
                "households_above_the_reference": arm.get("households_above_the_reference"),
            }
            for name, arm in arms.items()
        ],
        "refuses_to_total": got.get("refuses_to_total"),
        # WHAT STANDS BETWEEN R4 AND A REAL BOUND, and it is the finding that changes the shape of
        # the programme: a DATA ACQUISITION, not a model. Three floors become three ceilings the day
        # the book holds a floor area, a wall construction and a heating system.
        # BOTH SIDES OF THE CENSUS, AND SAY WHAT EACH COUNTS. `logs_scanned` is how hard we looked;
        # `attributes_found` is what we found. A single field carrying 29 under a name like
        # "attributes" would publish the OPPOSITE of the finding -- the finding is ZERO, and the 29
        # is what makes the zero worth believing rather than a shallow search.
        "property_logs_scanned": (got.get("property_attribute_census") or {}).get("logs_scanned"),
        "property_attributes_found": len(
            (got.get("property_attribute_census") or {}).get("attributes_found") or {}),
        "fabric_eligible": census.get("eligible"),
        "fabric_rows": census.get("rows"),
        "fabric_share": census.get("share"),
        # THE GAP NEITHER INSTRUMENT WAS LOOKING FOR, and the reason it is on this panel rather than
        # only in a staged finding: R3 measures value CREATED and this book has no instrument of
        # SHARING it. A shifted kWh is cheaper only on a time-of-use tariff and there is none here,
        # so time-shifting has a carbon ceiling and NO bill-saving ceiling at all. That is the
        # mission's own two-sidedness showing up as a missing product.
        "why_time_shifting_has_no_pounds": time_shifting.get("why_the_gbp_column_is_None"),
        "named_gaps": got.get("named_gaps"),
        "statement": got.get("headline"),
    }


def build() -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seat": "delivery",
        "what_it_did": what_it_did(),
        "what_it_decided": what_it_decided(),
        "what_it_got_wrong": what_it_got_wrong(),
        "what_next": what_next(),
        "the_number_the_programme_rests_on": the_number_the_programme_rests_on(),
        "the_most_a_carbon_score_could_be_worth": the_most_a_carbon_score_could_be_worth(),
        "the_most_the_products_beyond_price_could_be_worth": (
            the_most_the_products_beyond_price_could_be_worth()),
        "how_to_read_this": (
            "The delivery seat wakes on a timer, reads the last stretch, and writes direction -- "
            "never code. What it decides biases which work the ticks draw and can never block "
            "any of it. Everything on this page is read from a committed record; nothing here is "
            "computed a second time."
        ),
    }


def generate(out_path: Path | None = None) -> dict:
    data = build()
    dest = OUT_PATH if out_path is None else out_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    return data


def main(argv=None) -> int:
    data = generate()
    did = data["what_it_did"]
    print("delivery record: {} substantive / {} mechanical commit(s); focus {}".format(
        did.get("substantive"), did.get("mechanical"), data["what_next"]["focus"] or "(none)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
