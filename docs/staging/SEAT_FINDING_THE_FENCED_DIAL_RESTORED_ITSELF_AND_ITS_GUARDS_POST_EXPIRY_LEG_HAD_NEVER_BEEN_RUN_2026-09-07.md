**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The fenced dial restored itself on time, and the fence red anyway — its post-expiry leg had never been run

**Found:** 2026-09-07, delivery seat, RUNG 1b operational-layer persistent-red draw (5 consecutive
hourly reds, past paging). Fixed in the same turn; filed because the shape is a class, not this
instance.

## What was red

`tests/background/test_supervisor.py::test_live_fork_ceiling_matches_its_dated_fence_and_expires_with_it`
— the sole failure in a 1240-test operational signal.

```
E  AssertionError: assert '<=1 concurrent Agent forks' in
   'self-refill from maturity map (dial-weighted): B0'
```

## Two defects, and I had the first one wrong until the gate refused me

`MAX_CONCURRENT_FORKS` was widened 1 → 2 by director decision on 2026-09-06 for one allowance
window, ending 02:50Z 2026-09-07, and fenced by a guard keyed to that window's own clock so the
dial could not quietly stay wide.

**Written first, and wrong: "the restore ran and the constant is back at 1."** That was true of the
working tree and false of the record. Kept here rather than revised, because the route by which it
was caught is the point.

```
HEAD (7d92b54dd)   MAX_CONCURRENT_FORKS = 2      <- the window is over; the dial is still wide
working tree       MAX_CONCURRENT_FORKS = 1      <- restored, uncommitted, never landed
```

The restore edited the working tree and stopped there. The constant's own comment at HEAD says how
it was supposed to finish — *"the restore lands through surgical_land and moves this constant AND
its guard test together"* — and that half never ran. So **defect (a): the dial has been wide in
every committed tree since the window expired**, and no local test run could see it, because every
local run reads the working tree. I only found it because `surgical_land` gates the tree the commit
*would* create, and it refused me with the guard's own message: *"the window has EXPIRED and the
dial was not restored."* The message was right. I had read it as a false accusation.

Defect (b) is the guard's *second* half. `2e3fab091` (the widening commit) replaced an existing
width-1 test with a two-legged one and hoisted this line above the branch:

```python
assert f"<={expected} concurrent Agent forks" in draw   # doorbell STATES the live ceiling
if widened:  ...
else:        ...
```

True at width 2, where the draw takes the THREE-LANE sections path. **Unreachably false at width
1**, where a lone BUILD atom takes the byte-preserved single-atom fast path (`supervisor.py:5584`),
which states no fork budget at all — because existing NTFY parsing and five other tests pin that
string byte-for-byte.

The test it replaced said so explicitly, and the widening commit deleted the line that said it:

```python
-    assert "THREE-LANE" not in draw and "CONCURRENT" not in draw
-    assert "one Agent fork per atom" not in draw
```

So between 08:11Z on 2026-09-06 and 02:50Z on 2026-09-07 the else-leg was dead code, and it went
live for the first time at the expiry — reading, in its own failure message, as though the restore
had not happened. It had.

**The two hid each other.** In the working tree only (b) fires, and its failure reads as a broken
restore timer. At HEAD only (a) fires, and it reads as the fence working. Neither vantage shows
both, and the hourly signal only ever runs the first one.

## Why this is a class and not a slip

**A dated fence's post-expiry leg is a rare branch by construction — it cannot be exercised at the
moment it is written, and the one time it runs is the one time it is load-bearing.** CLAUDE.md
already names the rule it breaks: *when a branch exists to be taken rarely, assert it CAN be taken
before asserting what it does.* Here the branch could be taken; what could not be satisfied was one
assertion inside it, hoisted above the branch precisely because it looked width-independent.

The cost is not the red. It is that **the red accused the wrong subject.** The failure message the
author wrote for this case reads:

> "the 2026-09-06 window has EXPIRED and the dial was not restored. `tick-cadence-restore.timer` did
> not run; this is a defect, not a decision."

That message never printed — but a seat reading the failing line number without running it would
have gone hunting a restore timer that had worked correctly. The signal was red for 5 hours pointing
at a healthy mechanism.

**The generalisable move:** when writing a leg that cannot run until a future date, run it now by
forcing the clock, or the leg is a draft. A one-line poison at authorship time (`WINDOW_ENDS` set to
the past, confirm green) costs seconds and is the only evidence the post-expiry expectation was ever
true of the code.

## The fix, and its poison round

**(a)** The dial restore is landed — the half that never ran. `background/supervisor.py` in the
shared tree carries three lanes at once (this restore, another lane's pass-ceiling mirror in
`_idle_discover_frame_draw_concurrent`, and their publish-gate window fix in
`_publish_gate_wedge_active`), so a pathspec would have swept both of theirs into this commit.
Landed instead as HEAD-plus-one-line via `surgical_land --content`: diffed against HEAD it is the
single line `MAX_CONCURRENT_FORKS = 2` → `= 1`, and an AST symbol-set comparison against the working
tree shows the only symbol not carried is their `_in_window`, which stays theirs and stays dirty.

**(b)** The ceiling sentence now sits inside the `widened` leg where the sections path emits it; the
width-1 leg asserts what the fast path actually states, restoring the three lines `2e3fab091`
deleted. The mutation leg (`MAX_CONCURRENT_FORKS = 99`) still proves the doorbell states the live
ceiling wherever the sections path is taken, so nothing was traded away.

Poisoned both restored assertions independently — inverting `"CONCURRENT" not in draw`, and swinging
the tail from `B0` to `D5` — each red, then green on restore. The leg is reachable and falsifiable,
which is the thing the original never established about itself.

Operational signal: **1240 passed, 1 xfailed, 0 failed** (556s).

## What is NOT claimed

That the widening was wrong, or that the fence was the wrong design — it is the right design and it
is why the dial came back at all. Only that half of it had never been executed.
