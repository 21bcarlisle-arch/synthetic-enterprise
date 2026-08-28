**Severity:** LATENT · **Lane:** H_harness

# [SEAT] lane-zero-progress-signal-is-a-constant was claimed and has not moved for 2.0h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **2.0h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] lane-zero-progress-signal-is-a-constant was claimed and has not moved for 2.0h
NO PATHS WERE EVER BOUND to this claim, so nothing about it could be observed -- it is released on the clock, not because the work was seen to stall. Bind the paths of each landing as it lands (`delivery_lane.record_landing`) and this becomes a real signal. The claim is released and the work is drawable by any lane.
What the seat said it was doing: Fix the delivery lane's progress signal so its pass branch can be reached, per `docs/staging/WORKER_FINDING_THE_DELIVERY_LANES_PROGRESS_SIGNAL_CANNOT_FIRE_SO_EVERY_LANE_ZERO_CLAIM_IS_RECYCLED_2026-08-
```

## What is known without diagnosing anything

- Signature: `seat-claim:lane-zero-progress-signal-is-a-constant` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-26T12:02:46+00:00
- Repeats before escalation: 1 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

## Still live

---

## 2026-08-27T01:47Z — diagnosed: a RE-ISSUED claim can never bind the work it was re-issued for

**Status: DIAGNOSED, not repaired.** The repair is a design decision on a control and is left
as a drawn item below (SELF-INTERRUPT DISCIPLINE — queue, don't fix on sight).

This tick drew Lane 0 `the-world-answered-a-28x-price-rise-with-two-churns` and found the work
**already landed** at `8ac45e32e` (158 lines into `docs/design/THE_VALUE_CYCLE_REALISED_AB.md`,
already on `origin/main`). The claim's record nevertheless read `"paths": []`. That is this
alarm's condition, caught in the act, and the cause is a closed loop.

### Observed (with evidence)

| fact | value | source |
|---|---|---|
| commit time of the landed work | `1787788137` (2026-08-26 23:48:57Z) | `git show -s --format=%ct 8ac45e32e` |
| `claimed_at` on the live claim | `1787795061` (2026-08-27 01:44:21Z) | `docs/observability/.delivery_lane_claims.json` |
| delta | **commit is 6,924 s OLDER than its own claim** | arithmetic |
| bound paths | `[]` | same file |

`background/delivery_lane.py:198-201` refuses exactly this:

```python
since = float(rec.get("claimed_at", 0)) if claimed_at is None else float(claimed_at)
if when <= since:
    return []
```

Reproduced against a scratch claims file, with a **null control** — same commit, same claim id,
only `claimed_at` moved:

```
claimed_at 1787795061 (after the commit)  -> bind result: []                                  # refused
claimed_at 1787788000 (before the commit) -> bind result: ['docs/design/THE_VALUE_CYCLE_REALISED_AB.md']
```

The refusal is driven by the timestamp and nothing else, so this is not a path or gate problem.

### The loop (inferred, from the two mechanisms above)

1. Work lands at T1 and, for any reason, is not bound (tick died, index was locked, `--landed` skipped).
2. `moved == 0.0`, so staleness answers `claimed_at` (`seat_work_in_hand.py:243-246`), and the
   claim is swept at `CLAIM_STALE_SECONDS` = 100 min.
3. The seat re-issues the same focus id. `claim()` sets `claimed_at = time.time()`
   (`seat_work_in_hand.py:174`) — now **later than T1**.
4. Any tick that now tries `--landed` is refused: the commit predates the claim.
5. `paths` stays `[]` → back to step 2, **forever**.

The guard's docstring rationale ("a commit that predates the claim is somebody else's work, or
this tick's own earlier work") is right for a *first* claim and wrong for a *re-issued* one —
and the sweep is precisely the thing that manufactures re-issued claims. The alarm's own words,
"NO PATHS WERE EVER BOUND to this claim, so nothing about it could be observed — it is released
on the clock, not because the work was seen to stall", are this loop's steady state.

**The work is not stalled. The lane is blind to it.** Only a human/agent noticing the title on
HEAD and calling `--release` by hand breaks the cycle. That was done for this claim this tick.

### What the repair has to decide (drawn, not done here)

Not a one-liner — it changes what the lane treats as evidence, so it wants a decision, not a patch:

- **Option A (recommended):** on re-issuing a focus id that has been claimed before, carry the
  ORIGINAL `claimed_at` forward as a `first_claimed_at` floor and let `record_landing` bind any
  commit newer than *that*. Keeps the anti-heartbeat guard (a commit still cannot predate the
  work's first existence) while making re-issued claims bindable.
- **Option B:** at claim time, check HEAD's recent subjects for the focus id's own title and
  bind pre-emptively. Cheaper, but matches on a commit *message*, which is the weaker subject.
- **Option C:** leave it, and accept that Lane 0 progress is only ever observed for work that
  lands inside its first 100 minutes.

R15 note: the existing guard **can** fail (the null control above fires), so this is not a
control-that-cannot-fail. It is a control whose **scope is wider than its claim** — it refuses
somebody-else's-work *and* my-own-already-finished-work with the same test.
