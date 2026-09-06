# The elasticity fail-open is closed, and a full run asks for sixty-nine ids, none off the roster

**Date:** 2026-09-06
**Lane:** W2_customer_generator
**Severity:** result
**Subject:** `simulation.population_draw.price_elasticity_for_customer`

## The premise, re-measured at draw time

The doorbell's premise check reported that the cited commit `3b54d89a7` is already an ancestor of
`origin/main` and warned the work may have landed by another route. **It had not.** That commit is
the LEG half of the fix; the fail-open underneath it was live and was measured before starting:

```
price_elasticity_for_customer('NOT_A_REAL_ID', 20260724) -> 1.4222932629753158
```

In range, right shape, drawn from nothing. The premise was not spent, so the work proceeded.

## What was wrong

`household_of` is a STRING TRANSFORM (strip a trailing `g`), so the guard that landed at
`3b54d89a7` caught the supply-point-leg class and nothing else. Any other string was its own
household by that rule and was answered with a plausible, fabricated elasticity. That is how R1 came
to publish a ceiling over a target column where 87 of 264 rows belonged to no household — nothing
downstream can tell, because a fabricated elasticity has the right range and the right distribution.

## What changed

Two guards, in order, in `price_elasticity_for_customer`:

1. **Leg guard** (unchanged, from `3b54d89a7`) — `household_of(cid) != cid` → refuse.
2. **Roster guard** (new) — not on this run's live book → refuse.

The roster is reached through a new `simulation.live_population.is_on_the_live_book`, NOT through
the seam directly. `tests/simulation/test_population_draw.py::test_module_does_not_import_company_or_saas`
is a wall control forbidding `population_draw` from naming `company` or `saas` at all — the first
draft violated it and was rewritten. The dependency now runs draw → sim → seam, the same layering
`customer_events` already uses for `run_base_seed`.

## The trap, and why the roster is the LIVE book

The other lane documented it in `tools/r1_inference_ceiling.true_traits`: a plain book-membership
test is WRONG, because a successor registration after a home move (`C3_2`) is a household this run
created that the drawn book has never heard of.

Measured, and it settles which roster is correct:

| id | on `live_population()` | on the live BOOK |
|---|---|---|
| `C_IC1` (I&C site) | **absent** | present |
| `C3_2` (successor) | **absent** | present |
| `SYN-2021-001` (drawn) | present | present |

Keying the guard to `live_population()` would refuse two classes of real household. The live book
(`get_customer` over registered + successors + acquired + drawn) is right, and two of its four
registers are runtime accumulators — which is what makes it the run's LIVE population rather than
the initial draw.

## The prediction that was wrong, kept beside its refutation

Reading the call sites, I predicted prospects never reach this draw: `net_new_acquisition` has no
reference to the symbol, and the one live call site passes a billing account. **That was wrong.**
A full instrumented `run_phase2b` logging every ask:

```
ASKS: 110      unique ids asked: 69      ASKS NOT IN ROSTER: 0
```

Most of the 69 are `PROS-*` ids. A won prospect keeps its prospect-shaped id and is registered onto
the acquired book, so it is a household by the time anything asks. The call sites would have told
me the wrong thing; only the run told me the right one.

**The column that matters is the second: zero asks were outside the roster.** The guard refuses
nothing a real decade-long run does today.

## Controls, and the poison round

Five mutations, all killed — reachability proved before survival was claimed:

| # | mutation | killed by |
|---|---|---|
| M1 | roster predicate always `True` | leg/roster independence |
| M2 | roster predicate always `False` | leg/roster independence |
| M3 | roster = `live_population()` not the book | the on-book leg (`C_IC1`, `C3_2`) |
| M4 | roster check removed from the draw | both roster controls |
| M5 | leg guard removed | refusal-naming + independence |

M3 is the design error that was avoided; it is caught by the control, not by the reviewer.

Three new controls in `tests/simulation/test_population_draw.py`:
- `test_normalising_an_id_is_not_enough_the_household_must_also_be_on_the_live_book` — replaces
  `test_a_household_normalised_id_can_never_trip_the_elasticity_guard`, whose property (any
  normalised id is answered) WAS the fail-open stated as a guarantee. The old property is written
  out in the docstring rather than deleted.
- `test_the_elasticity_roster_guard_and_the_leg_guard_are_each_independently_reachable` — R15's
  two-sequential-guards shape. `C1g` IS on the book, so the roster guard alone would answer it;
  `NOT_A_REAL_ID` is its own household, so the leg guard alone would answer that. Neither subsumes
  the other.
- `test_a_household_this_run_registers_mid_run_is_answered_not_refused` — the successor trap as a
  live property: refused before registration, answered after, book left as found.

`tests/tools/test_value_cycle_ab_noise_floor.py` registers its forty stand-in accounts on the
acquired book (module fixture) rather than being exempted from the guard. Exempting them would have
reopened the fail-open for every caller to keep one suite green. All 36 pass, and because that suite
pins the spread and floor figures, their passing is the evidence the numbers are unchanged.

## Reds NOT caused by this work, proved in a clean HEAD extract

- `tests/tools/test_r1_inference_ceiling.py` — the shared tree's copy is **behind HEAD**: it calls
  `price_elasticity_for_customer("C1g")` expecting a value, which HEAD's leg guard already refuses.
  HEAD's own copy of that suite passes 25/25 against these modules. **Not landed; not mine.**
- Six `tests/simulation/test_dd_level_collection_book.py` controls — red at clean HEAD, already
  tracked by `SEAT_FINDING_SIX_DD_LEVEL_COLLECTION_CONTROLS_ARE_RED_AT_HEAD_IN_BOTH_TREES...`.
- `tests/architecture/test_static_quality_ratchet.py` I001 `1319 → 1318` — another lane's
  working-tree improvement to `tests/tools/test_generate_maturity_map_data.py`. The working tree is
  BETTER than HEAD; banking the baseline would wedge every lane, so it was left alone.

## What this does NOT close

The larger half of the drawn direction is untouched: the R1 harness page still asserts the gating
verdict is a STEP FUNCTION OF COVERAGE, grouping runs by counts that are supply points rather than
households. That grouping may survive the re-keying and nothing yet establishes that it does. The
re-run that settles it is `r1_inference_ceiling --stability` over the same window with household
counts that read as household counts. It is not attempted here: `tools/r1_inference_ceiling.py`
carries 1075 changed lines from another lane in the shared tree, and two BLOCKING findings record
two lanes having each built R1's magnitude estimator. Running it now would measure a contested file.
