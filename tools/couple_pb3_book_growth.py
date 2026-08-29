"""COUPLED-TRIAD runner for PB3 — book growth as an EARNED outcome.

PB3 exit criterion (d): "the company's own belief about its book and the world's
truth are measured against each other and the gap reported, per the coupled-triad
rule that the gap is the score."

This is HARNESS code. It sits OUTSIDE the epistemic wall by design and is the only
layer permitted to hold the company's belief and the world's outcome side by side
(COUPLED_TRIAD_DESIGN.md 1.3; identical role to `tools/couple_w2_4_c6.py`). It
lives in `tools/` — NOT under `company/` or `saas/` — so it is not scanned by the
epistemic verifier and may legitimately read both sides.

THE COUPLED LOOP (3 loops, COUPLED_TRIAD):

  1. SIM adds depth   -- `simulation/net_new_acquisition.py::plan_growth_campaign`
                         runs the campaign: each year's affordable quotes meet the
                         acquisition funnel and the real switching market, and some
                         are won. The world decides who is won.
  2. COMPANY copes    -- `saas/growth_mandate.py` (reached only through
                         `company/interfaces/growth_desk.py`) sizes next year's
                         quote budget by INVERTING its own belief about the win
                         rate: year one on its founding belief, every year after on
                         what its own quote book has since said. It never reads the
                         funnel.
  3. HARNESS measures -- this module: for each year, the rate the year was PLANNED
                         ON against the rate the year actually ACHIEVED.

WHAT MAKES THIS A BELIEF-VS-TRUTH PAIR AND NOT A TAUTOLOGY. `realised_win_rate_used`
is booked by `plan_growth_campaign` BEFORE the year's own wins are added to the
running book (`quotes_issued_to_date`/`wins_to_date` are incremented after the row
is written), so the belief carried into year Y is built from years < Y only. The
truth it is scored against is year Y's own `wins / quotes_issued`. Point-in-time
correct: the belief cannot contain the outcome it is being graded on.

THE NO-SKILL ARM (g0), and it is the mechanism's OWN null control rather than a
constant invented here. g0 is the SAME company with the learning loop disabled —
the founding belief (`believed_win_rate`) held for every year, which is literally
what `plan_growth_campaign` uses in any year whose `planning_on` is "belief". So
`gap = raw_gap / g0` reads as: did learning from its own quote book buy this
supplier a better forecast than never updating would have?

  gap < 1  -- learning helped.
  gap > 1  -- the learned belief is WORSE than the founding constant.

READ THE >1 CASE WITH ITS CAVEAT, which is stated here because the Proof door
renders `worse_than_blind` in red and a reader is owed the reason. This company's
founding belief (0.20) sits very close to its long-run realised rate (~0.18), so
"blind" is an unusually strong arm here — an artefact of where the founding
parameter was set, not evidence that the learning mechanism is broken. What a
gap > 1 does say, and says correctly, is that a cumulative rate dragged down by
small unlucky early years under-forecasts the later ones. R12: a DIAGNOSTIC, never
a target — nothing in this repo may be tuned to move this number.

THE PARTITION, and why an unpartitioned number would be the R15 FAIL-OPEN here.
Some years can be stopped by `SETTLEMENT_CUSTOMER_YEAR_BUDGET` — THIS MACHINE's
customer-year ceiling, not a commercial limit. A year the box truncated has an
outcome the market did not decide, so scoring the company's forecast against it
charges the supplier for our engine. Those years are EXCLUDED from the headline and
reported separately with their own count. The open LATENT finding
`WORKER_FINDING_THE_COMPANY_NOW_LEARNS_A_WIN_RATE_FROM_YEARS_AN_ENGINEERING_CAP_DECIDED_2026-08-24.md`
refused to fix this company-side and was right to: a company that could see which of
its own losses were artefacts would be reading the simulation. That refusal binds
the COMPANY. It does not bind the HARNESS, and this is the harness.

THAT SENTENCE USED TO SAY THE PARTITION WAS EMPTY, AND IT WAS FALSE FOR A DAY.
Written when the ceiling was slack, it read "no year of the shipped run is
settlement-bound". The founder book then made the ceiling taut, nine of the ten
years became machine-bound, the scored partition collapsed to {2016}, and this
ledger published `gap = 1.0` — which is what a single belief-planned year yields by
identity — under a docstring asserting there was nothing to exclude. Nothing
reported the change, because the partition was written as a control and had quietly
become the population. A note about today's answer decays; that is why the two
things guarding this measurement are now properties rather than states: the floor at
`n_scored_planning_on_learned_rate` in `measure`, and the fix below.

WHY THE PARTITION IS NOW EMPTY FOR A REASON INSTEAD OF BY LUCK (2026-08-29). The
year's truth is `funnel_wins / quotes_issued` — what the MARKET gave the company —
not `wins / quotes_issued`, which is what this machine could afford to settle. The
funnel's count is untouched by the ceiling, so there is no longer a population for
the exclusion to remove; and the belief it is scored against is built from the same
funnel count, so the two legs of the ratio finally count the same thing. The
partition is kept and tested anyway: it is load-bearing the moment a future ceiling
truncates something the funnel can see, and a control that only exists once it is
needed does not exist.

DETERMINISM (C-S2). No RNG, no wall clock in the measurement. `measured_at` /
`run_git_commit` are gathered in `main()` and passed in, never called by `measure()`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

from background.gap_metric import (
    NORMALISATION_DIVISOR,
    GapResult,
    write_gap_entry,
)

WORLD_ATOM_ID = "PB3_book_growth_as_earned_outcome"

#: PB3 holds BOTH sides of this pair inside its own loop — the campaign that wins
#: the book and the plan the book was won against — so it is its own twin. This is
#: `EP1_clv_three_horizon`'s shape in the same ledger, not a new convention. The
#: belief organ itself (`saas/growth_mandate.py`, behind
#: `company/interfaces/growth_desk.py`) is owned by NO atom in the maturity map;
#: that absence is recorded in the entry's note rather than papered over by naming
#: a neighbouring atom that does not hold this belief.
TWIN_ATOM_ID = "PB3_book_growth_as_earned_outcome"

#: The campaign's own record of the run, written by
#: `simulation.live_population._resolve_campaign`. Read rather than recomputed:
#: re-resolving the campaign means `live_population()` at the shipped
#: configuration, which is the call the 2026-08-24 OOM finding attributes twelve
#: sim-runner kills to on this box. The record carries every field this
#: measurement needs.
CAMPAIGN_RECORD = (
    Path(__file__).resolve().parents[1]
    / "docs" / "observability" / "book_growth_campaign.json"
)

#: Binding reasons whose year was decided by THIS MACHINE rather than by the
#: market or by the company's own balance sheet. `settlement_engine` is set by
#: `plan_growth_campaign` when the customer-year budget refuses to settle a win
#: the company actually won. `capital` is NOT here: running out of money is a
#: commercial outcome and the supplier owns it.
MACHINE_BINDINGS = ("settlement_engine",)


class CampaignRecordUnusable(RuntimeError):
    """The campaign record is missing, malformed, or carries no scoreable year.

    RAISED, never degraded to a zero gap. `gap = 0.0` on this ledger means "the
    observables leaked theta" and the Proof door renders it red as `leak`; a
    measurement that silently published 0.0 because it could not read its input
    would be claiming a wall breach it never observed. Fail closed, loudly.
    """


#: The key the read's own provenance is filed under. Underscore-prefixed to say it was added by
#: the READER and is not part of what `_resolve_campaign` wrote.
READ_PROVENANCE_KEY = "_read_provenance"


def load_campaign_record(path=None) -> dict:
    """Read the campaign record, refusing anything unusable, and NAME the bytes it read.

    FAIL-CLOSED ON ALL FOUR (R15): absent file, unreadable bytes, non-object JSON,
    and an object whose `by_year` is missing/not-a-list/empty. Each is a state in
    which no measurement exists, and each one is a `CampaignRecordUnusable`.

    WHOSE BOOK IS THIS? (2026-08-29.) `CAMPAIGN_RECORD` is an absolute path that
    `simulation.live_population._resolve_campaign` rewrites from EVERY process that
    assembles a book, and the live producer assembles one about every 1,500s. This
    reader therefore measures whatever the last writer left, and until now recorded
    nothing about which run that was. `tools/settlement_ceiling_probe.py` had the
    identical shape and it was not hypothetical: producer pid 3859950 rewrote the file
    mid-probe and the probe published the producer's campaign as its own 2,000-budget
    result, with a coherent and false verdict attached.

    THE FIX IS NOT A REFUSAL, DELIBERATELY. Refusing while a producer is in flight
    would refuse most of the time -- the producer is running for roughly two-thirds of
    every cadence -- and a control that cannot clear gets bypassed rather than obeyed.
    Instead the read NAMES ITS SUBJECT: the bytes' sha256, the file's mtime, and
    whether a producer was in flight at the start and end of the read. A divergence is
    then REPORTED rather than silently adopted, and two measurements can be compared to
    see whether they read the same book at all.

    The one thing that IS refused is the file changing DURING the read, because then
    there is no single record to name.
    """
    p = Path(path) if path is not None else CAMPAIGN_RECORD
    if not p.is_file():
        raise CampaignRecordUnusable(
            f"no campaign record at {p}. It is written by "
            "`simulation.live_population._resolve_campaign` on a real run; there "
            "is nothing to measure until a run has produced one."
        )
    producer_at_start = _producer_in_flight()
    try:
        mtime_before = p.stat().st_mtime_ns
        raw = p.read_bytes()
        mtime_after = p.stat().st_mtime_ns
    except OSError as exc:
        raise CampaignRecordUnusable(f"campaign record at {p} is unreadable: {exc}")
    if mtime_before != mtime_after:
        raise CampaignRecordUnusable(
            f"campaign record at {p} was rewritten WHILE being read "
            f"(mtime {mtime_before} -> {mtime_after}). A producer assembling a book "
            "shares this path; there is no single record here to measure."
        )
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise CampaignRecordUnusable(f"campaign record at {p} is unreadable: {exc}")
    if not isinstance(data, dict):
        raise CampaignRecordUnusable(
            f"campaign record at {p} is {type(data).__name__}, not an object."
        )
    rows = data.get("by_year")
    if not isinstance(rows, list) or not rows:
        raise CampaignRecordUnusable(
            f"campaign record at {p} carries no `by_year` rows. A campaign with no "
            "years is not a campaign whose forecast was perfect."
        )
    data[READ_PROVENANCE_KEY] = {
        "path": str(p),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "mtime_utc": datetime.fromtimestamp(
            mtime_before / 1e9, tz=timezone.utc).isoformat(),
        "producer_in_flight_at_start": producer_at_start,
        "producer_in_flight_at_end": _producer_in_flight(),
    }
    return data


def _producer_in_flight() -> Optional[str]:
    """The pid of a live producer run, or None -- and None on ANY failure to tell.

    The opposite default to `settlement_footprint_probe.a_run_is_in_flight`, which it
    delegates to, and the difference is deliberate: there the answer gates whether to
    launch a second heavy job, so not knowing must refuse. Here it is a provenance
    ANNOTATION on a measurement that goes ahead either way, so an unavailable check
    must not be recorded as a producer that was never observed.
    """
    try:
        from tools.settlement_footprint_probe import a_run_is_in_flight

        pid = a_run_is_in_flight()
    except Exception:
        return None
    return pid if pid and pid.isdigit() else None


def _planned_on_rate(row: dict) -> Optional[float]:
    """The win rate this year was actually PLANNED ON — the company's belief.

    `planning_on` is the campaign's own declaration of which of the two rates it
    inverted for this year's budget, so it is read rather than re-derived: a
    measurement that decided for itself which number the company used would be
    grading a plan the company never made.

    Returns None when the declared rate is missing or not a usable number. The
    caller drops the year and COUNTS it — it never substitutes a default, because
    a defaulted belief is a forecast nobody made and it would score as skill.
    """
    key = ("realised_win_rate_used" if row.get("planning_on") == "realised"
           else "believed_win_rate")
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _founding_belief(row: dict) -> Optional[float]:
    """The no-skill arm for this year: the founding belief, never updated."""
    value = row.get("believed_win_rate")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _realised_rate(row: dict) -> Optional[float]:
    """The year's OUTCOME: wins per quote issued, as the world decided it.

    THE FUNNEL'S WINS, NOT THE BOOK'S (2026-08-29). `wins` is what this machine
    settled; `funnel_wins` is what the market gave the company. The belief this
    number is scored against is built from the funnel — `plan_growth_campaign`
    carries `wins_to_date += funnel_wins_this_year` and has since the wall fix of
    2026-08-28 — so scoring it against BOOKED wins compares a belief formed on one
    population with a truth measured on another. It is the ratio-of-two-populations
    defect, and it was invisible only because the settlement ceiling had reduced the
    scored partition to 2016, the single year in which the two counts are equal.

    Under the uniform sample the two differ in EVERY year and by a factor of five
    and a half, so a booked-win rate would have read as a supplier converting 3%
    when its funnel converted 18%.

    Falls back to `wins` when `funnel_wins` is absent, which is what a record
    written before 2026-08-28 looks like. That fallback is not silent: those
    records are also the ones with no `settlement_sample_rate`, and `measure`
    reports the count it scored either way.

    A year that issued no quotes has an UNDEFINED win rate, not a zero one — a
    supplier that never quoted did not lose every quote. Returns None and the
    caller counts the year out.
    """
    quotes = row.get("quotes_issued")
    wins = row.get("funnel_wins")
    if isinstance(wins, bool) or not isinstance(wins, (int, float)):
        wins = row.get("wins")
    if isinstance(quotes, bool) or not isinstance(quotes, (int, float)):
        return None
    if isinstance(wins, bool) or not isinstance(wins, (int, float)):
        return None
    if quotes <= 0:
        return None
    return float(wins) / float(quotes)


def is_machine_bound(row: dict) -> bool:
    """True iff this year's outcome was decided by our engine, not the market."""
    return row.get("binding") in MACHINE_BINDINGS


def measure(record: dict) -> Tuple[GapResult, dict]:
    """Measure PB3's belief-vs-truth gap over the MARKET-DECIDED years.

    Returns `(GapResult, stats)`. `stats` carries the per-year working so a
    reviewer can re-add the arithmetic by hand — the numbers behind the headline
    are published, not just the headline (R15 independence is only checkable if
    the parts are visible).
    """
    rows = record["by_year"]

    scored: list[dict] = []
    excluded_machine: list[dict] = []
    dropped_undefined: list[dict] = []

    for row in rows:
        if not isinstance(row, dict):
            dropped_undefined.append({"year": None, "why": "row is not an object"})
            continue
        year = row.get("year")
        truth = _realised_rate(row)
        belief = _planned_on_rate(row)
        naive = _founding_belief(row)
        if truth is None or belief is None or naive is None:
            dropped_undefined.append({
                "year": year,
                "why": ("no quotes issued — win rate undefined" if truth is None
                        else "declared belief missing or non-numeric"),
            })
            continue
        entry = {
            "year": year,
            "binding": row.get("binding"),
            "quotes_issued": row.get("quotes_issued"),
            "wins": row.get("wins"),
            "planned_on": row.get("planning_on"),
            "belief": belief,
            "truth": truth,
            "founding_belief": naive,
            "abs_error": abs(belief - truth),
            "abs_error_no_skill": abs(naive - truth),
        }
        if is_machine_bound(row):
            excluded_machine.append(entry)
        else:
            scored.append(entry)

    n_scored = len(scored)
    # THE POPULATION FLOOR, and it is keyed to the question rather than to a count.
    #
    # This gap asks ONE thing: did learning from its own quote book buy this supplier a
    # better forecast than never updating would have? In a year the company planned on its
    # founding BELIEF, the learned arm and the no-skill arm are the same number, so that
    # year contributes `abs_error == abs_error_no_skill` and pulls the ratio toward exactly
    # 1.0 for a reason that has nothing to do with learning. A partition containing ONLY
    # such years yields gap = 1.0 by identity.
    #
    # That is not hypothetical. On the record shipped 2026-08-29 the settlement ceiling had
    # made nine of ten years machine-bound, the scored partition was {2016} alone, 2016 plans
    # on belief, and this ledger published `gap = 1.0` — a tautology wearing a measurement's
    # clothes, under a module docstring asserting the excluded partition was empty. No count
    # threshold would have caught it honestly; this one does, and it is a floor on the
    # PROPERTY the number needs rather than on how many rows happen to be present.
    # IT GATES THE RATIO, NOT THE COMPONENTS. `raw_gap` and `g0` are the mean absolute
    # errors of the two arms and they are honest numbers whatever the partition contains --
    # a reviewer re-adding the arithmetic is entitled to them. What the floor refuses is the
    # normalised HEADLINE, because that is the number read as a verdict on learning.
    n_learned = sum(1 for e in scored if e["planned_on"] == "realised")
    if n_scored:
        raw_gap = sum(e["abs_error"] for e in scored) / n_scored
        g0 = sum(e["abs_error_no_skill"] for e in scored) / n_scored
        # g0 == 0 is the degenerate branch `gap_metric._normalise` documents: a
        # no-skill arm that was exactly right leaves nothing to divide by, and the
        # honest headline is UNDEFINED rather than an infinity or a zero.
        gap = (raw_gap / g0) if (g0 and n_learned) else None
    else:
        # EVERY year excluded or undefined, OR no scored year in which the company
        # actually planned on a learned rate. There is no measurement, and None is
        # the ledger's designed representation of that -- `gap_measured()` reads
        # it as unmeasured and the L3 draw stays blocked, which is correct: a
        # campaign the box decided every year of has not been scored against a
        # market, and a partition of belief-only years has not scored learning.
        raw_gap, g0, gap = 0.0, 0.0, None

    stats = {
        "n_years_in_record": len(rows),
        "n_scored": n_scored,
        # WHY THE HEADLINE IS OR IS NOT A MEASUREMENT, as a number a reader can check.
        # `n_scored` alone cannot say it: ten belief-only years score exactly as
        # vacuously as one does.
        "n_scored_planning_on_learned_rate": n_learned,
        "n_excluded_machine_bound": len(excluded_machine),
        "n_dropped_undefined": len(dropped_undefined),
        "scored_years": scored,
        "excluded_machine_bound_years": excluded_machine,
        "dropped_years": dropped_undefined,
        "customer_year_budget": record.get("customer_year_budget"),
        "customer_years_committed": record.get("customer_years_committed"),
    }

    components = {
        "n_years_in_record": len(rows),
        "n_scored_market_decided": n_scored,
        "n_scored_planning_on_learned_rate": n_learned,
        "n_excluded_machine_bound": len(excluded_machine),
        "excluded_machine_bound_years": [e["year"] for e in excluded_machine],
        "n_dropped_undefined": len(dropped_undefined),
        "mean_abs_error_learned": round(raw_gap, 6),
        "mean_abs_error_no_skill": round(g0, 6),
        "customer_year_budget": record.get("customer_year_budget"),
        "belief_organ": "saas/growth_mandate.py via company/interfaces/growth_desk.py",
        "belief_organ_atom": None,
    }
    if not n_scored:
        components["vacuity"] = (
            "NO market-decided year in this campaign: every year was either "
            "machine-bound or had no quotes. The gap is UNDEFINED (None), not "
            "0.0 -- a forecast nothing was scored against is not a perfect one."
        )

    return GapResult(
        metric="belief",
        gap=gap,
        raw_gap=raw_gap,
        g0=g0,
        normalisation=NORMALISATION_DIVISOR,
        baseline=(
            "the SAME company with its learning loop disabled -- the founding "
            "`believed_win_rate` held for every year instead of the rate its own "
            "quote book has since said. gap = mean|learned belief - realised| / "
            "mean|founding belief - realised|, over MARKET-DECIDED years only."
        ),
        components=components,
        note=(
            "PB3 exit (d): the company's belief about its win rate against the "
            "rate the world actually granted it, year by year. The belief is "
            "point-in-time correct by construction -- `plan_growth_campaign` books "
            "each year's running quote book AFTER writing that year's row, so the "
            "belief carried into year Y is built from years < Y and cannot contain "
            "the outcome it is scored on. Years stopped by "
            "SETTLEMENT_CUSTOMER_YEAR_BUDGET (this machine's customer-year "
            "ceiling, not a commercial limit) are EXCLUDED and counted separately: "
            "scoring the supplier's forecast against a year our engine truncated "
            "charges it for our box. gap > 1 means the learned belief did worse "
            "than never updating -- read it with the caveat in this module's "
            "docstring, because this company's founding 0.20 sits close to its "
            "long-run realised rate and is therefore an unusually strong blind "
            "arm. R12: a diagnostic, never a target."
        ),
    ), stats


def _git_head() -> Optional[str]:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description="PB3 belief-vs-truth gap (exit d)")
    ap.add_argument("--record", default=None,
                    help="path to book_growth_campaign.json (default: shipped)")
    ap.add_argument("--write-ledger", action="store_true",
                    help="persist the measured gap into coupled_gap_ledger.json")
    args = ap.parse_args()

    record = load_campaign_record(args.record)
    result, stats = measure(record)

    print("PB3 -- book growth as an earned outcome: belief vs truth")
    prov = record.get(READ_PROVENANCE_KEY) or {}
    if prov:
        # WHICH BOOK. Printed first because every figure below is a property of these
        # bytes and of no others, and the path is shared with the live producer.
        print(f"  record read              : {prov['path']}")
        print(f"    sha256                 : {prov['sha256'][:16]}  mtime {prov['mtime_utc']}")
        if prov["producer_in_flight_at_start"] or prov["producer_in_flight_at_end"]:
            print("    NOTE: a producer run was in flight during this read "
                  f"(start={prov['producer_in_flight_at_start']}, "
                  f"end={prov['producer_in_flight_at_end']}). The record may be a "
                  "different run's book than the one this measurement is attributed to.")
    print(f"  years in record          : {stats['n_years_in_record']}")
    print(f"  scored (market-decided)  : {stats['n_scored']}")
    print(f"  EXCLUDED (machine-bound) : {stats['n_excluded_machine_bound']}"
          f"  {[e['year'] for e in stats['excluded_machine_bound_years']]}")
    print(f"  dropped (undefined)      : {stats['n_dropped_undefined']}")
    print(f"  customer-year budget     : {stats['customer_year_budget']}"
          f"  (committed {stats['customer_years_committed']})")
    print()
    print("  year  binding        planned_on  belief   truth    |err|   |err_no_skill|")
    for e in stats["scored_years"]:
        print(f"  {e['year']}  {str(e['binding']):13s} {str(e['planned_on']):10s} "
              f"{e['belief']:.4f}  {e['truth']:.4f}  {e['abs_error']:.4f}  "
              f"{e['abs_error_no_skill']:.4f}")
    for e in stats["excluded_machine_bound_years"]:
        print(f"  {e['year']}  {str(e['binding']):13s} EXCLUDED -- decided by the "
              f"engine, not the market")
    print()
    print(f"  mean |err| LEARNED       : {result.raw_gap}")
    print(f"  mean |err| NO-SKILL (g0) : {result.g0}")
    print(f"  GAP (normalised)         : {result.gap}")
    if result.gap is not None and result.gap > 1:
        print("  -> WORSE THAN BLIND: learning from its own quote book cost this "
              "supplier forecast accuracy against never updating. See the caveat "
              "in this module's docstring before reading that as a broken loop.")

    if args.write_ledger:
        ledger = write_gap_entry(
            WORLD_ATOM_ID, TWIN_ATOM_ID, result,
            measured_at=datetime.now(timezone.utc).isoformat(),
            run_git_commit=_git_head(),
        )
        print(f"  ledger written: {WORLD_ATOM_ID} -> "
              f"gap={ledger[WORLD_ATOM_ID]['gap']}")


if __name__ == "__main__":
    main()
