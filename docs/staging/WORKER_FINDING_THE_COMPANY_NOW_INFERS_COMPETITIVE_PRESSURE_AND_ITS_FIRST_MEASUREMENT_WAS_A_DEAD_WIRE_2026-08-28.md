**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B10_competitor_switching_response`

# The company now derives its competitive-pressure belief from its own losses, and the first measurement of it was an artefact of a dead wire

Direction of 2026-08-28 (lane 0): give the company a competitive-pressure belief it DERIVES from
observables it actually receives, keeping the published year series as the prior it updates from
rather than the answer; then re-run the chase-on/chase-off pair and report whether
`believed_p_leave` now differs between the two worlds.

The channel is built, wired and mutation-proven. **The first measurement of it was worthless and
in the flattering direction, and catching that is the more useful half of this finding.**

## What was there

`company/crm/market_conditions.market_conditions_multiplier(renewal_year)` — a ten-entry table
(2016: 2.17 … 2025: 0.93) keyed on the calendar year, and the ONLY competitive signal reaching
`enriched_churn_estimate` (lines 104/139) and `churn_model.estimate_passive_churn_probability`.
A year lookup cannot respond to anything a rival does inside a year, which is why the previous
pair moved the world at every rung and moved the belief by `max |ON − OFF| = 0.0`.

## What is there now

`company/crm/competitive_pressure.py`. The published series becomes the PRIOR; the company's own
realised losses against what it predicted become the LIKELIHOOD; they combine by precision
weighting in log space, because ratios compose multiplicatively:

    posterior = prior × ratio^w,    w = V_prior / (V_prior + V_evidence)

- `ratio` = realised losses ÷ predicted losses, over renewal years **strictly earlier** than the
  one being priced. No look-ahead: an estimate informed by its own outcome is not an estimate.
- `V_prior` = 0.2442, the dispersion of the published multiplier series in log space, **computed
  from the series**, not chosen.
- `V_evidence` = the delta-method variance of a log binomial proportion at the realised sample
  size, evaluated under the null.
- No observations ⇒ `w = 0` ⇒ the posterior IS the prior. Outside a run scope the value is
  byte-identical to the table it replaces, so nothing that did not opt in sees a difference.

Two inputs, both things a real supplier reads off its own systems: what it believed at each
renewal (booked by `churn_desk.estimate_renewal_churn`, its one once-per-renewal belief site) and
that an account did not renew (booked in `run_phase2b`'s churn branch, through the existing
`company/interfaces/churn_estimation` door). Nothing about the rival crosses in either direction.
`simulation/competitor_reference.py`, `chase_per_quarter` and `COMPETITOR_AGGRESSION.yaml` are
untouched; `tools.epistemic_verifier` returns PASS.

### Two defects found by printing numbers rather than by thinking

**The weight co-varied with the answer.** The first draft used the Wald variance, evaluated at the
realised proportion. Printing the multiplier across real sample sizes before shipping the formula
showed it was **not monotone in the thing it observes**: on 200 decisions predicting 0.30,
observing 30 losses gave 0.542 and observing ZERO gave 0.594. A belief that reads more competitive
pressure from fewer departures is not conservative, it is broken. Evaluating under the null makes
the weight a property of sample size and prediction alone, and the posterior strictly increasing
in realised losses. `test_the_belief_is_MONOTONE_in_realised_losses` pins it.

**A control that could not fail.** `test_a_window_where_NOBODY_left_is_still_readable` asserted
finite-and-below-prior, and the mutation it was written for (deleting the continuity correction)
did not fire: with no correction the multiplier is exactly 0.0, which is finite and is below the
prior. Zero means no customer can ever leave at any price — the captive floor that
`_apply_market_conditions` was rewritten in survival space to remove, arrived at from the other
side. The assertion is now strictly positive.

## THE DEAD WIRE, which is the finding

The first chase-on/chase-off pair against the new channel produced a result that looked like a
success:

| rung | belief ON | belief OFF | world ON | world OFF | gap ON |
|---|---|---|---|---|---|
| 0.0 | 0.2068 | 0.2068 | 0.0582 | 0.0498 | +0.1486 |
| 0.5 | 0.3238 | 0.3239 | 0.2345 | 0.2153 | +0.0893 |
| 1.0 | 0.4535 | 0.4535 | 0.4429 | 0.3933 | +0.0106 |
| 2.0 | 0.6952 | 0.6952 | 0.5512 | 0.5414 | +0.1440 |

The published over-prediction gap appeared to collapse from the previous pair's **20.7–28.7pp to
1.1–14.9pp**. That is the number a session in a hurry writes up as the channel working.

**It was a dead wire.** `run_phase4c_on_phase2b.main` calls `run_phase2b()` with **no
`sim_interface`**, so every `notify_churn` in the run loop sits behind `if sim_interface is not
None` and none of them fired. The ledger filled its denominator from the desk and left its
numerator at zero, then read `observed = 0` as evidence that the market had gone quiet — during a
run in which the null-rung check records 16 accounts churning in the ON arm and 12 in the OFF.

This is the FAIL-OPEN shape in its purest form: **the absence of an observation channel read as an
observation of absence.** It is R15's second killer, it moved the belief a long way, it narrowed
the published gap, and every one of those numbers was an artefact. It was caught by a contradiction
the artefacts stated plainly — the world churned 16 accounts in one arm and 12 in the other, and
the company's belief was bit-identical — rather than by the tests, all 16 of which were green.

**What that costs the design.** A count of zero and an absence of reporting are different facts and
the ledger could not tell them apart. The numerator is now armed by the site that books into it
(`arm_loss_reporting`, called adjacent to the booking in `run_phase2b`'s churn branch, so deleting
one deletes the other), an unarmed ledger declines to update and returns the prior, and the
booking is no longer behind the `sim_interface` guard — a supplier knows who left it whether or not
a notification seam happens to be plumbed in.
`test_an_UNARMED_ledger_REFUSES_to_update_however_full_its_denominator` is mutation-proven against
exactly the state that produced the table above, and
`test_a_run_that_loses_NOBODY_still_arms_nothing_and_keeps_the_prior` stops the guard being a
tautology.

## The prediction I filed BEFORE reading the re-run, and it was wrong

Written into this file before the re-run finished, so it could refute me:

> **The belief will move between the two worlds by much less than the world does, and may not
> move at all.** The company's channel observes an INTEGER count of departures. The chase moves
> each decision's churn probability by 0.7–4.5pp, so across a book of this depth the expected
> difference in the number of accounts that actually leave is well under one.

**Half right and the interesting half wrong.** The sparseness was right — the belief moves at one
rung in four. The magnitude was badly wrong: where it moves it tracks **68.1%** of the world's own
move, not "much less". I had reasoned about the expected number of extra departures and concluded
the belief would barely twitch; what I had not reasoned about is that when the count DOES cross an
integer, the resulting update is large, because one account on a book this thin is ~8.5% of the
multiplier. The effect is not small-and-everywhere, it is **absent-or-substantial**. That is a
different shape from the one I predicted and it changes what the fix is: not "more signal", but
"more chances for the count to cross".

## The measurement, re-run with a live numerator

Fresh pair, one tree, identical book and seeds, differing in exactly one declared parameter, with
`chase_per_quarter` asserted to have taken its value before each run (`0.5` ON, `0.0` OFF, both
printed by the arm script). Null rung reproduces the flat-rules control exactly in both arms.
Common population 16 decisions × 4 rungs.

| rung | belief ON | belief OFF | **belief move** | world ON | world OFF | world move | gap ON | tracked |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 0.2153 | 0.2153 | +0.000000 | 0.0582 | 0.0498 | +0.0084 | +0.1571 | 0.0% |
| 0.5 | 0.3728 | 0.3597 | **+0.013156** | 0.2346 | 0.2153 | +0.0193 | +0.1382 | **68.1%** |
| 1.0 | 0.5546 | 0.5546 | +0.000000 | 0.4344 | 0.3828 | +0.0516 | +0.1202 | 0.0% |
| 2.0 | 0.8561 | 0.8561 | +0.000000 | 0.5417 | 0.5308 | +0.0109 | +0.3144 | 0.0% |

**The company's belief now responds to a rival it cannot see and never names.** `max |ON − OFF|`
was `0.0` at every rung this morning; it is `0.0132` at rung 0.5 now, in the correct direction,
tracking two-thirds of the world's move at that rung.

**Why one rung and not four**, stated as mechanism rather than inferred. The realised loss counts
inside the 16-decision intersection are identical in both arms at every rung (3/3, 6/6, 7/7, 8/8).
The ledger does not read that intersection — it reads the whole book, over years strictly earlier
than the renewal being priced. At rung 0.5 the chase moved the departure count in a year early
enough to be evidence, and the company's predicted losses differ accordingly (5.965 ON vs 5.754
OFF). At the other three rungs it did not: the null-rung check records 16 accounts churning in ON
against 12 in OFF book-wide, but those extra departures fall in 2019, the last year of the window,
where nothing is priced after them. **A departure only becomes evidence if something is priced
after it.**

## A correction to the morning finding, whose claim this contradicts

`WORKER_FINDING_THE_LADDER_RESOLVES_THE_DEFENDING_MARKET` concluded that a deeper book was "not on
the critical path for B10", because the continuous leg resolves a 0.7pp effect on 17 decisions.
That is true **of the instrument** and false **of the company**. The harness may read the world's
own probability; the company may only count departures. Book depth is not on the critical path for
DETECTING the world change and is squarely on it for the company OBSERVING one.

## B10 stays at level 2, and the reason has changed again

The coupled-triad law is that no world atom reaches L3 until the company has been tested against it
and the gap measured. `COMPETITOR_FIELD_FRAME.md` §5 says a defect is "a gap that never moves in
response to new observations", and §5's component 2 previously returned not "wrong sign" but "no
response exists".

**A response now exists, is wired to real observables, and is measured to be non-zero and in the
correct direction on a paired comparison.** §5 component 2 returns a number for the first time.
That is the structural half of B10's L3 leg and it is discharged.

**I am refusing the level move anyway, and this is the third refusal for the third reason** — which
is itself the useful record. The response fires at **one rung in four**, and the three silent rungs
are silent for a reason that has nothing to do with competition: the extra departures landed in the
final year of the window, where nothing is priced afterwards. A response measured on a single rung
of a four-rung ladder over 16 decisions is one observation, not a curve. Recording L3 on it would
be reading a single crossing of an integer threshold as a demonstrated capability.

What L3 now needs is narrow and known: **the same pair on a window long enough that departures in
the last year are not wasted, and a book deep enough that the count crosses at more than one rung.**
Both are the same `n` question as P9. There is no longer a design question here.

## WORK THIS CREATES

1. **Re-run the pair on a deeper book and a longer window.** The channel's resolution is one
   account and its evidence is only usable if something is priced after it — so the final year of
   any window contributes nothing. This is the same book-depth question as P9 and should be done
   once, for both. The pair costs ~10 minutes.
2. **The `sim_interface is not None` guard is a fail-open pattern, not an instance.** Every
   observable the company books through that guard is silently absent in every `run_phase4c` run.
   This one was found because its absence moved a published number. The others have not been
   checked, and `notify_acquisition` and `notify_retention_attempt` sit behind the same guard.
3. The §5 **ceiling gap** (component 1) remains unbuilt — the company still has no observation of
   the cheapest rival price, only of its own losses.

## Reproducing it

```
python3 -m tools._ladder_chase_arm on  docs/observability/ladder_chase_on_derived_2019.json
python3 -m tools._ladder_chase_arm off docs/observability/ladder_chase_off_derived_2019.json
python3 -m tools.compare_chase_belief docs/observability/ladder_chase_{on,off}_derived_2019.json
```

The arm script asserts `chase_per_quarter` has taken its intended value **before** the run and
refuses otherwise: an override that silently failed would report the chase as costing nothing,
which is the fail-silent shape that turns the comparison into a confident null.

`compare_chase_belief` was validated against the PREVIOUS pair, where it reproduces that finding's
published table exactly — including its `max |ON − OFF| = 0.0`. That is its null control, and it
caught a defect in itself: the verdict line originally read only the artefact's `per_decision`
block, which carries each decision's LOWEST and HIGHEST rung and nothing between, so it printed
"bit-identical" directly beneath a table showing rung 0.5 had moved. The verdict is now taken over
the per-rung table. A summary that contradicts the table above it is worse than no summary.

## WHAT LANDED AND WHAT IS HELD — read this before trusting the table above

**Landed:** `company/crm/competitive_pressure.py`, its 17 mutation-proven controls, the three
consumers now reading the derived multiplier (`enriched_churn_estimate` x2,
`churn_model.estimate_passive_churn_probability`), the desk booking what it believed, the door
mirroring the desk, both ladder artefacts, and this finding.

**HELD, and the channel is INERT until it lands:** the two hunks in `simulation/run_phase2b.py`
that open the run scope and book departures. Without them `active_pressure_ledger()` returns None
at every call, the reading is the published prior, and behaviour is byte-identical to the year
table this replaces. **So the measurement above is reproducible only with the held hunks applied,
and the landed tree does not yet reproduce it.** Saying otherwise would be the record outrunning
the code.

**Why it is held, and it is not my red.**
`tests/simulation/test_run_phase2b_event_log.py::test_sim_interface_none_still_works` fails at
**pristine HEAD** — verified against a clean `git archive HEAD` export with no working-tree
overlay — with `ValueError: day 29 must be in range 1..28 for month 2 in year 2015` at
`run_phase2b._company_eac_estimate`. A 29 February term start, taken back a year to a date that
does not exist. Another lane is already fixing exactly this in the working tree
(`simulation.customer_events.twelve_month_window_open`, helper and call site both uncommitted, so
neither is at HEAD).

Any commit touching `simulation/run_phase2b.py` selects that test and is refused. The remedy is
not mine to apply: fixing another lane's red to unblock myself is how two lanes' work ends up in
one commit and neither can be attributed. The hunks are ready and land in one commit behind theirs.

**This is also the second time today `surgical_land`'s refusal was the measurement rather than an
obstacle.** The working tree is green on that test because it carries the other lane's fix; the
tree the commit would create is not. A green shared worktree measures several lanes, not your
change.

## The bound on this measurement

**Both arms ran on the shared worktree, which carried two other lanes' uncommitted work** — the R6
acquisition-spend/collateral wire and a leap-year fix in `twelve_month_window_open`. The two arms
are internally controlled against each other (one tree, same instant, identical book and seeds, one
declared parameter differing), so the ON−OFF comparison above is sound. What is NOT sound is
comparing these absolute levels against the morning pair's, which ran on a different tree; where
this finding quotes the morning's 20.7–28.7pp gap it is to show that a number MOVED, not to
attribute the size of the move. The commit that lands this carries only this lane's hunks, so the
tree it creates is not the tree that was measured.
