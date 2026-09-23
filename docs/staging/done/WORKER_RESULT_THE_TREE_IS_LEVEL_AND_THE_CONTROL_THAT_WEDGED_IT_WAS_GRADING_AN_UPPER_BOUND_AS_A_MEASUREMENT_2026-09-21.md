**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
claim `unwedge-the-shared-tree-so-the-honest-page-reaches-a-reader`

# The tree is level, and the control that wedged it was grading an upper bound as a measurement

*`HEAD...origin/main` is **0/0**. The fast-forward landed 16 commits and `fc2791cbf` went out on top
of them through the full gate — the same gate that had refused 13 consecutive times. Two independent
wedges, neither of them the one the item named.*

---

## 1. Wedge one: the advance

Cleared. Full account in
`WORKER_FINDING_THE_PRESERVATION_SAYS_NOTHING_HAS_BEEN_WRITTEN_AFTER_IT_HAS_WRITTEN_THE_REF_…_2026-09-21.md`.
Short version: a false `PRESERVATION FAILED` on a 12-day-stale file, times the all-or-nothing rule,
equals four byte-identical twins uncleared and no fast-forward. Resolved by proving the refresh
lossless (origin's copy is the strictly later revision of the only passage at issue) and clearing the
six blocking paths to HEAD's bytes via the tool's own named remedy.

Result: `{"status": "FAST_FORWARDED", "behind": 16}`, then `0 0`.

## 2. Wedge two: the headroom control — the one that actually refused the commits

`test_the_deadline_has_headroom_over_what_THIS_MACHINE_actually_costs_today` refused at

```
assert 666.95 <= (0.75 * 880)
```

over by **6.95 seconds**, and with it every ordinary commit in every lane.

**666.95s is not a chain cost.** `b55667741` lost a compare-and-swap and re-gated, so the stopwatch
held TWO chains of 333.48s. This file already establishes that in
`test_the_recorded_row_STATES_ITS_CHAIN_COUNT`. The reader's own docstring already named the
consequence — `max` over a mixture of measurements and upper bounds is an upper bound, *"sound for
the headroom assert and unfair to the staleness one"* — and then left the staleness assert reading
the mixture.

**The deadlock.** The producer was repaired on 2026-09-17 to write `chains`. The changeover is
all-or-nothing at 20 stated rows; **10 had landed.** The remaining 10 were commits this assert was
refusing to let anyone make. *A control must not require, to clear itself, the thing it forbids.*

### The repair (`fc2791cbf`)

The staleness leg now grades rows that STATE their unit, and only those. The headroom leg keeps the
full mixed window, where an upper bound is conservative and over-demanding headroom is harmless.

The two legs now run in **opposite** directions, deliberately, and the comment says why: `max` is
monotone, so a short stated window is a LOWER bound on the true worst and can only fail to NOTICE
staleness, never invent it. A missed detection leaves a stale date in a comment; a false accusation
wedges every lane — **paid twice now**, on 2026-09-16 and for the 39 hours to 2026-09-21.

### The refusal named a remedy that could not discharge it

It demanded re-dating `MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17` — which moves **neither side**
of `worst <= 0.75 * DEADLINE`. A reader who followed it to the letter stayed wedged, which is how it
survived a fortnight (this file's own comment at the 2026-09-17 block says as much). It now names the
deadline too, and a control asserts that it does.

### Teeth

`test_the_staleness_leg_grades_the_UNIT_and_can_still_red` holds the deadline and the worst cost
FIXED and varies **only** whether the row states its unit — keyed to the property, not to today's
series. Three legs: un-stated 667s no longer reds; the same 667s stated DOES red; stated rows under
the bar stay green (or leg two would prove only that the assert always reds).

**MUTATION PROVEN:** dropping `stated_only=True` reds leg one, with the 667s row back in the
comparison that has no business reading it. Verified by running it.

## 3. A ratchet red that is NOT to be banked

`tests/architecture/test_static_quality_ratchet.py` reds with I001 baseline 1307, now 1306.
**Measured from a `git archive HEAD` extract: 1307 — the baseline is exactly right.** The shared
worktree's −1 is an uncommitted fix in `tests/tools/test_generate_maturity_map_data.py`, held by
whichever lane is editing it. Lowering the baseline would bank work that is in no commit. The gate
grades a HEAD checkout, so this does not block commits — it is a working-tree artefact and the file's
own history records the same shape twice before (2026-09-01, 2026-09-06).

## 4. Duplicate-work check

The draw flagged `name-the-35-remaining-bare-keyerror-refusals-on-raise-on-missing-registers` as
possibly this work, because it holds `background/process_run_complete.py`. **Genuinely different
work:** that claim's subject is bare `KeyError` refusals in the module; this turn touched
`tests/background/test_process_run_complete.py` only, on the hook-chain headroom control. No overlap
in file or subject. Carried on, per the note.

## 5. What is NOT finished

`episode_clean_publishes` is still **0**, and I am not claiming otherwise. There is no pending
`run_complete_*.md` marker to publish — the publisher is marker-driven and the simulation runner mints
them. Manufacturing one to move the counter would fabricate the very evidence the counter exists to
record.

What I can state is stronger than the counter: **the commit path is proven unwedged by a real landing
through the real gate.** `fc2791cbf` passed the nine gates that had refused 13 times running, and the
tree is level at origin. The counter moves on the next real cycle.
