**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`fit-the-hook-chain-growth-series-because-the-deadlines-room-halved-in-a-fortnight-and-nothing-watches-it`)

**Knowledge:** none new from outside. Every figure below is fitted from this machine's own
`docs/observability/commit_hook_duration.jsonl` and `publish_gate_duration.jsonl`. No published
source is involved and none is claimed.

# The hook chain is growing at +6.3%/day, and the instrument goes blind exactly when the publish path wedges

Delivery seat, 2026-09-18. Scores
`docs/staging/records/SEAT_PREREG_IS_THE_HOOK_CHAIN_GROWING_OR_STEPPING_AND_IS_ANYTHING_STILL_FEEDING_THE_SERIES_2026-09-18.md`,
written before any fit was run and unedited. **P0, P0b, P1, P2, P4 and P5 hold. P3 is REFUTED —
I predicted the trend would not be establishable from this series and it is, comfortably.**

---

## The answer to the question that was asked

**GROWTH, not a step.** Over the 89 real chains since the 2026-08-31 regime step, a log-linear
trend fits at **+6.30%/day, 95% CI [+5.19, +7.43]**, and beats a best-single-breakpoint
piecewise-constant model by **ΔAIC 19** (−252.0 vs −232.6; a flat model is −173.1). The two moves
in this series have genuinely different shapes, which is what P1 predicted:

| Move | Shape | Evidence |
|---|---|---|
| 2026-08-31 | **STEP**, sharp and downward | 395s median → ~108s median within hours; ±4% either side |
| 2026-09-01 → now | **GROWTH**, continuous | +6.3%/day, ΔAIC 19 over the best step model |

The slope survives every re-cut of the window, which is the check that matters given a four-day
data hole (2026-09-10 → 2026-09-15):

| Window | n | slope | 95% CI |
|---|---|---|---|
| from 08-31T19:00 (all) | 89 | +6.30%/day | [+5.19, +7.43] |
| from 09-01 (skip the step day) | 82 | +5.99%/day | [+4.82, +7.17] |
| from 09-06 (the climb only) | 33 | +7.11%/day | [+4.10, +10.21] |
| from 09-08 (the item's own window) | 22 | +9.75%/day | [+6.36, +13.24] |
| **drop the 09-15+ tail entirely** | 79 | **+4.78%/day** | **[+2.90, +6.70]** |

The fifth row is the one that decides it. The obvious objection is that the whole trend is the
post-hole tail pulling a line; delete that tail and the slope is still **+4.8%/day with a CI
clear of zero**. The growth is not an artefact of the hole.

**P3 refuted, recorded beside its replacement rather than quietly dropped.** I predicted the slope's
interval would include zero or come within a factor of three of doing so, and that the honest
answer would be *"I cannot yet say"*. It does not and it is not: the central estimate sits **10
standard errors** from zero. I was calibrating off the constant's own note that the last regime was
"9 runs over three days" and did not check that the segment being fitted is 89 rows, not 9. The
prediction was wrong for a reason worth keeping: **n for a regime is not n for a trend through
several regimes.**

### What that buys, in dates

The live half grades `max` of its window, so the operative anchor is the committed worst (333s at
2026-09-17), not the fitted mean line:

| Bar | What it is | central +6.3%/d | across the robust range |
|---|---|---|---|
| **660s** | `worst <= 0.75 * 880` — the existing staleness assert reds | **2026-09-28** | 2026-09-24 → 2026-09-30 |
| **720s** | `1.25 * worst = 900` — floor meets ceiling, **no deadline satisfies both controls** | **2026-09-30** | 2026-09-25 → 2026-10-02 |

**The wedge is real, it is the same wedge as 2026-09-04 and 2026-09-16 reached a third way, and on
this trend it closes in under a fortnight.**

---

## The part I was not looking for, and it is the more urgent half

**The series is COLD and no control can tell.** (P0, P0b — both held.)

The last row is `2026-09-17T12:40:51`. The sibling ledger wrote at `2026-09-17T23:17` and the
shared tree committed at `2026-09-18T00:21`. **Zero of the 195 rows carry the `chains` key that
`_record_commit_hook_duration` gained at `bfbc2b4e9` — not one row has been written since that
repair landed**, while the machine kept working for 27 hours.

The mechanism is not a broken recorder. It is structural:

- `publish_gate_duration.jsonl` gets a row **every** publish cycle, whatever the gate returns.
- `commit_hook_duration.jsonl` gets a row only from `_land_publish_commit`, which a cycle reaches
  only **after its gate has PASSED**.
- All **13** publish gate runs since 12:40 returned `outcome: "fail"`.

**So the chain is only ever timed on a cycle that succeeds, and the instrument therefore goes dark
at the start of any incident in which cycles stop succeeding.** The headroom control's window is
bounded by row count alone — `_recent_hook_chain_seconds` escapes only on "no file" and "no
readable duration" — so it keeps grading the same twenty pre-wedge rows forever and reads exactly
like a healthy machine.

**And the direction of that error is the fail-open one.** Because the chain is growing at +6.3%/day,
a frozen window under-states the current cost, and the live half's job is to demand headroom *over*
the worst. Staleness here does not withhold a judgement — **it invents room.** That is why the
remedy below refuses rather than skips: a skip is the same colour as a pass.

---

## The decision the item asked for: does the floor need a watcher?

**No — and the item's "nothing currently watches the room" is wrong, which is worth stating plainly
because it changed the answer.** `test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today`
already carries `worst <= 0.75 * GIT_COMMIT_HOOK_TIMEOUT_SECONDS`, i.e. **660s — which fires about
two days BEFORE the 720s wedge**, with a refusal that already names re-measurement as the remedy.
The room is watched. Building a second, trend-keyed watcher beside it would be keying a control to
today's slope, which CLAUDE.md names as exactly backwards, and would be the 118th harness atom
guarding a control we already have.

**What that watcher lacks is any defence against its own evidence going stale.** So that is the one
thing built, and it is one assertion.

### What was built

`tests/background/test_process_run_complete.py`:

- `_publisher_runs_since_the_last_timed_chain()` — counts publish cycles that ran with no chain
  timed, by differencing the two ledgers on the newest timed stamp.
- `test_the_live_headroom_half_cannot_grade_a_machine_that_STOPPED_RECORDING` — reds at
  `HOOK_CHAIN_WINDOW_ROWS` (20) unrecorded cycles.

Three properties it was designed around, each of which is a way it could have been worthless:

1. **A count, not an age.** An age cannot tell a quiet machine from a blind one, and redding the
   tree because nobody committed overnight is the failure this file already carries two scars from.
   A count of *sibling runs* is silent on an idle machine by construction.
2. **The bound is the control's own window, not a picked number.** At 20 unrecorded cycles, a full
   window's worth of behaviour has happened with none of it observed — by the live half's own
   sampling rule there is no current evidence left in the sample it grades. 5 or 50 would be picked.
3. **It is self-clearing**, which is what separates it from the shape this file warns about. It is
   discharged by one timed chain: the cycle that lands writes the row. It asks for the publish path
   to work, not for paperwork.

**Green as shipped, and close.** On the shared tree right now the count is **13 of 20** — so it
passes today and reds if the wedge persists another ~7 cycles (~5 hours). That is the control
working, not a control mis-set.

**P5 held — the mutations fire.** `test_the_blindness_control_ACTUALLY_REDS_and_is_silent_on_a_quiet_machine`
proves three legs independently: a full window of unrecorded cycles trips the bound; an idle
machine counts **zero**; and a malformed ledger returns the inapplicable value rather than a zero
that would read as health. The second leg is the one that matters — a control that reds on quiet
would be withdrawn within a day, and the first leg alone cannot tell me it does not.

---

## What is still owed, and what I am NOT claiming

- **I have not fixed the publish wedge.** The 13 consecutive gate failures since 2026-09-17T12:40
  are a live incident with its own cause, untouched here. This turn makes it *visible to the
  headroom control*; it does not diagnose it.
- **I cannot attribute the +6.3%/day to anything.** It is spread over a fortnight of ordinary
  growth across many lanes, as the constant's own note already says of the earlier climb. Naming a
  cause would need the per-step timings from `tools/time_the_commit_hook_chain.py` run at two dates,
  and only one such run exists.
- **The forecast assumes the trend continues.** The 2026-08-31 step proves this series can move
  4x in hours in either direction. The dates above are what today's evidence implies, not a
  prediction that nothing will intervene — and the 660s control does not depend on them.
- **The re-dating collision is not resolved.** When `MEASURED_COMMIT_HOOK_CHAIN_SECONDS` next needs
  re-taking above ~720s there is no deadline satisfying both controls, and since the director ruled
  the 900s allowance may not grow, **the only remaining move is to make the chain cheaper.**
  `tools/time_the_commit_hook_chain.py` exists for exactly that and its output is the next item.
