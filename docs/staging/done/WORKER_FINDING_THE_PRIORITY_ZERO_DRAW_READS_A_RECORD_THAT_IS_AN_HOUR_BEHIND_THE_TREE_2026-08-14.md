# WORKER FINDING — the priority-zero draw reads a record that is up to an hour behind the tree, so a fixed red keeps outranking every lane

**Severity:** LATENT · **Lane:** H_harness
**class:** a record that answers a draw is not required to be current — second instance, machine-kept copy
**found:** 2026-08-14, on the RUNG-1b PRIORITY-ZERO draw itself (the tick immediately after `fb1493702`)
**Rank requested:** backlog. Nothing here is blocking; it costs ticks, not correctness.
**Disposition:** mechanism landed in `background/supervisor.py` this tick, R15-proven three mutations.

## What the draw handed me (observed-with-evidence)

This tick's doorbell was the priority-zero rung:

> OPERATIONAL-LAYER PERSISTENT-RED self-refill (RUNG 1b, PRIORITY ZERO): the operational-layer
> signal … has been RED for 9 consecutive hourly checks — past paging, so paging did NOT get it
> fixed. … OUTRANKS every product/HARDEN lane.

It had already been fixed. Three timestamps, all read off disk and git, not inferred:

| | value |
|---|---|
| `.operational_layer_signal.json` `last_run_ts` | `1786718334.97` = **15:38:54** |
| `fb1493702` *"the 9-hour red was the deadman flushing its own digest into the suite that tests it"* | **16:11:31** |
| this tick's draw | **16:15** |

`supervisor._self_refill_draw()` re-derived the same message live at 16:15, verbatim, 4 minutes
after the commit that discharged it. The signal is re-read on an **hourly** cadence
(`OPERATIONAL_LAYER_CHECK_INTERVAL_SECONDS`), so the record would keep saying RED until ~16:38 —
and every tick in that window draws **priority zero**, above every product, SITE, HARDEN and
DISCOVER lane, for work that is done.

The detector is `_operational_red_persistent_draw()`. It reads `last_result` and `consecutive_red`
and nothing else; it already accepted a `now` parameter and **never used it**. There was no clock
anywhere in the predicate.

## Why the obvious fix is wrong

The tempting repair is "if the record is stale, don't draw". That rebuilds the exact fail-silent
this rung exists to kill. The rung's own docstring states its fail-safe direction — *toward*
drawing — and the reason is structural: **the record freezes RED precisely when the deadman dies.**
A dead writer and a fixed-but-unread red produce the *same* stale record. Suppressing on staleness
would go quiet on the overnight-stall case (13 consecutive reds, nobody home) to save a few minutes
on the already-fixed case. That trade is backwards, and it is the third mutation below.

## What landed

`_operational_red_stale_record_prefix()` — factored out so it can be put on trial directly. The
draw **always still fires**; only the instruction at its head changes. When HEAD was committed
strictly *after* the record was written, the message leads with:

> RE-RUN THE SIGNAL FIRST — this RED record was written 33 min BEFORE the current HEAD
> (`fb1493702`) was committed, so a fix may already have landed and the record simply has not been
> re-read (the check is HOURLY). Run `run_operational_layer_signal(force=True)` and, if it comes
> back GREEN, the draw is discharged … Only if it is STILL RED does the diagnosis below apply.

Re-running the signal is ~10 minutes. A fresh diagnosis of an already-fixed red is a whole tick.
The clause buys the cheap act instead of the expensive one, and it can never buy silence.

Supplier: `_head_commit_epoch()`, in the same defensive shape as the neighbouring
`_current_head_hash()` — any git error returns `None`.

## R15 — both ways, and the UNKNOWN branch is the point

Three mutations, each caught by a test that names it:

1. **clause removed** (revert to the record-only draw) → `test_a_record_written_before_head_leads_with_re_run_first` fails.
2. **fail-open** — an unusable `last_run_ts` or an unavailable git treated as *"a fix landed"* → 4 tests fail. An unavailable check is a **failed** check; the safe unknown here is *diagnose from scratch*, never *assume it is fixed*, so the base draw prints unsoftened and git is proven not to be consulted at all on that path.
3. **suppression instead of prefix** — the wrong fix above → `test_a_record_written_before_head_leads_with_re_run_first` fails on `None`.

Plus: a strict boundary (equal stamps are not evidence anything landed afterwards); proof the clause
is a prefix on an *already-decided* draw and cannot resurrect a green or below-threshold record;
and a test that the default supplier is wired to **real** git — a clause whose supplier is only ever
a stub is theatre. The pre-existing overnight-state test was pinned hermetic in passing: it carries a
`last_run_ts` and would otherwise have read the live repo, making the weather its subject.

`tests/background/test_operational_red_persistent_draw.py`: **20 passed** (was 11).

## Class

This is the second recorded instance of *the record that answers the draw is not required to be
current* — the first (`WORKER_FINDING_THE_RECORD_THAT_ANSWERS_THE_DRAW_IS_NOT_REQUIRED_TO_BE_CURRENT`,
2026-08-12, atom D41) was a **hand-kept** hold note running three Expert Hours behind. This one is
**machine-kept** and merely slow, which is why no freshness rule caught it: nobody thinks of an
hourly daemon's own output as a second copy. It is. The general shape is *any draw predicate whose
input is written on a cadence slower than the draw*, and this repo has more than one.

## Queued, not fixed (SELF_INTERRUPT_DISCIPLINE)

The same shape is available on every other cadence-written draw input — `.publish_gate_state`,
`.pull_loop_health.json`, the gap-ledger reconcile — none of which compare their record against the
tree either. Not swept in: each needs its own judgement about what "a fix may have landed" means for
that predicate, and the supply of these is infinite.

## R12

No published number moved. This touched the draw ladder, not the instrument.
