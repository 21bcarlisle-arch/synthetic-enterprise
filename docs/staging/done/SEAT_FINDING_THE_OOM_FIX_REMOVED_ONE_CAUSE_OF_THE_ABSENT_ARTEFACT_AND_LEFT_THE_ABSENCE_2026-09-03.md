**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The OOM fix removed one cause of the absent artefact and left the absence itself

**Class:** `controls_that_cannot_fail` (primary), `measurements_that_mirror` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, claim
`the-baseline-was-beaten-in-a-world-that-no-longer-exists`
**Subject:** `tools/run_value_cycle_ab.py` — `floor_run_headroom_refusal()` and its call site in
`main()`.

## What was found

`SEAT_FINDING_THE_LEG_THAT_PRODUCES_THE_PUBLISHED_BOUND_WAS_OOM_KILLED_AND_WROTE_NOTHING`
(`3ae262976`, earlier today) landed `floor_run_headroom_refusal()`. Its own diagnosis names the harm
precisely, and the harm is not the lost hour:

> The failure is silent in the only place anyone looks. `--out` names the artefact at launch; a run
> that dies at 90 minutes leaves that path absent, and **an absent path is exactly what a run still
> in progress looks like**. […] The next session sees "no artefact yet", concludes the legs are
> still going, and waits, or relaunches the same three-up configuration and loses another 1h 09m.

The fix removes the **OOM** as a cause of that absence. It does not remove the absence. The call
site was:

```python
refusal = floor_run_headroom_refusal()
if refusal and not args.ignore_headroom:
    print("noise floor REFUSED: {}".format(refusal))
    return 2
```

A refused run puts its reason on a stdout that nobody reads an hour later, and leaves `--out`
**absent** — the same state, with the same misreading, arrived at one cause earlier. A session that
finds `value_cycle_ab_s1_noise_floor_20260903.json` missing still cannot tell "refused in two
seconds" from "measuring for the next hour", which is the exact question the earlier finding exists
to make answerable.

## It is not hypothetical, and it is measured

Evaluated on this guest at 12:0xZ today, with the `only` and `except` legs running:

```
FLOOR_RUN_PEAK_MB = 6400.0
sample: total 24,032 MB · available 6,546 MB · swap free 1,382 MB
running legs: [(2969556, 5202 MB), (2969617, 5268 MB)]
REFUSAL NOW -> "a floor leg peaked at 6,400 MB ... this guest needs 19,200 MB ... can offer 17,017 MB"
```

**The refusal branch is live and reachable right now.** What keeps it from firing on the queued
`all` leg is only that `se-noise-floor-all-20260903b.service` waits for both legs to exit first, so
`running_floor_legs()` will return empty and ~10.5 GB will have come back. That is the design
working — and it is also the whole margin. Any other seat launching a leg, or the guest being
busier when the wait ends, converts a two-hour measurement into an absent file and a session that
waits for it.

**Stated plainly rather than generously: on the most likely path the queued leg will pass the
headroom check and this defect will not fire today.** It is filed because the reading it produces
is indistinguishable from the one that already cost 1h 09m, not because it is about to.

## Why this shape recurs

The earlier finding fixed the *cause* it had just paid for and keyed the control to that cause. The
property that actually matters — **the state of `--out` distinguishes refused from running** — was
never expressed anywhere, so a second cause of the same absence walked straight through. This is
`CLAUDE.md`'s "key a control to the property, not to today's answer", and the near-miss is that the
new control is *itself* correct and well-reasoned; it simply guards the wrong noun.

## The repair

**The refusal writes.** `floor_refusal_artefact()` is left at the path the run would have written,
so "refused" and "still running" are different things on disk. Two properties are load-bearing and
both are non-obvious:

**It deliberately carries no `generated_at`.** Every consumer keys freshness off that field —
`generate_value_arms_data._staleness_caveat` reads it to decide whether the bound and the point
estimate describe one world. A refusal stamped `generated_at` would be the newest artefact on disk
and the most misleading, because nothing was measured. Withholding it makes the existing consumer
fail closed on its own already-landed branch ("one of these two runs carries no timestamp"), which
was verified against the live consumer rather than assumed: `_error_bar` returns
`available: False` with a named reason and does not crash.

**It never overwrites a run that succeeded.** These legs are re-run at the same `--out` across
worlds, so the obvious unconditional write would replace a good floor with its own excuse and fail
the page closed for a reason having nothing to do with the figures — the class already filed today
as `THE_CAPTURE_TOOLS_DEFAULT_OVERWRITES_THE_ARTEFACT_TWO_OTHER_INSTRUMENTS_READ`. A refusal may
replace a refusal; it may never replace a run. Unparseable is treated as not-overwritable: if we
cannot show the file is a refusal, we do not touch it.

`decompose_floor` refuses a refusal artefact twice over — on seeds and on the absent spread — so it
can never be read as a leg. That was driven explicitly rather than assumed, because the refusal
*does* carry `world_identity` and so passes the world check on its own.

## Six controls, driven through `main()`

**Through `main()` on purpose.** A refusal wired into the helper and not into the entry point is
this repo's filed FAIL-OPEN shape; asserting on `floor_refusal_artefact()` alone would stay green
while `main` still returned 2 in silence.

Mutation-proven with `python3 -B`, observed results recorded:

| mutation | reds |
|---|---|
| M1 — `main` refuses without writing (the defect as it stood) | **3**: `..._writes_the_refusal_where_the_artefact_would_have_been`, `..._carries_NO_generated_at...`, `..._MAY_replace_an_earlier_refusal` |
| M2 — refusal stamps `generated_at` | **1**: `..._carries_NO_generated_at_so_nothing_reads_it_as_a_fresh_floor` |
| M3 — write unconditionally, no clobber guard | **2**: `..._NEVER_overwrites_a_floor_run_that_succeeded`, `..._an_artefact_that_cannot_be_read_is_not_overwritten` |
| M4 — guard keyed to mere existence (first refusal permanent) | **1**: `..._MAY_replace_an_earlier_refusal` |
| M5 — refusal shaped with seeds so the decomposition reads it as a leg | **1**: `..._refused_by_the_decomposition_rather_than_split` |

M4 is the PASS branch for M3's guard, so the no-clobber leg is a reading and not a constant verdict.
No mutation left every leg green, and no leg is an equivalence.

## What this does NOT do

It does not make the floor legs cheaper, and it does not make a refused leg run. A refused floor is
still no floor, the page still publishes no bound from it, and the remedy is still to run the legs
one at a time. The only thing repaired is that the next session can **read** which of the two
happened.
