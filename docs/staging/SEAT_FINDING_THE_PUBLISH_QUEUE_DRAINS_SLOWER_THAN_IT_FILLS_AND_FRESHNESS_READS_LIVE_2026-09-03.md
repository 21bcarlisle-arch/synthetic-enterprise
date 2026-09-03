**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The publish queue drains slower than it fills, and every freshness instrument reads `live`

Measured 2026-09-03T01:07Z at HEAD `a082be80b`, from the **shared** tree
`/home/rich/synthetic-enterprise`. Pre-registration:
`PREREG_THE_PUBLISH_REFUSAL_NAMES_GREEN_TESTS_2026-09-03.md`, graded below.

## The measurement

Of the run-complete markers **produced** in the 24 hours 2026-09-02T01:00Z → 2026-09-03T01:00Z:

| | count |
|---|---|
| produced | **62** |
| archived to `docs/staging/done/` (processed) | **27** |
| still queued in `docs/staging/` (never processed) | **35** |

The whole queue *is* that window's backlog: its oldest member is `20260902T160532Z` and **zero**
queued markers predate the window. So the numerator and denominator count the same population,
which is the only reason the ratio means anything — the processor consumed **44%** of what the
runner produced, and the shortfall is the queue.

Two numbers name the mechanism, both from `docs/observability/sim-runner-log.md`:

- a `process_run_complete` cycle takes **~15 min** (`00:10` start → `00:25`
  `Moved run_complete_20260902T210757Z.md to done/`), and it drains **exactly one** marker;
- `background/sim_runner.py` emits one every **~13.5 min** (735–755 s run + 60 s wait).

Drain period > fill period, so the backlog is not a spike to wait out. **115 lock-skips** in the
window are the observable: `Another process_run_complete instance is already running -- skipping
run_complete_<stamp>.md`. Every one of the last four markers ends that way.

## Why this is BLOCKING and not LATENT

*A control or instrument in this area is untrustworthy.* Throughout the window above:

- `background.publish_freshness.describe()` reads
  `content publishing: live -- figures reached origin 0.7h ago`, `state: publishing`;
- `site/data/publish_provenance.json` reads
  `last_verified.generated_at: 2026-09-03T00:25:50Z`, `git_commit: 9d841e7c3`;
- the operational-layer signal reads `green (consecutive_green=41)`.

All three are **true statements about the wrong subject** — the module's own docstring names that
failure and attributes eighteen hours of silence to it. `snapshot()` computes `state` from
`pub_age` and `com_age` only; the depth of the queue behind the publisher is not an input to any
of them, so a pipeline consuming 44% of its input is indistinguishable from a healthy one. The
site is serving run `run_output_9d841e7c3_20260902T210757Z.json` — **four hours** stale at the
time of measurement, with 35 completed runs behind it that will never be published at all.

`background/supervisor.py:162` is explicit that `run_complete_*.md` markers "coming and going
both reset the unchanged counter", i.e. marker churn is deliberately excluded there as noise. The
backlog is therefore not the subject of the freshness verdict, nor of the supervisor's. That is
the gap, and it is the same shape as this project's own rule: **a gate slower than the tree's
landing cadence can never converge.**

## What this is NOT

It is not the drawn brief's wedge. Both halves of that brief — (a) the staged, unfrozen
`tools/artefact_rerun_diff.py`, and (b) the classifier that could not name a non-test refusal —
were **already finished in the shared tree and being landed while this was measured** (PID
1977366, `python3 -m tools.surgical_land`, started 02:08 local, pathspec covering
`tools/artefact_rerun_diff.py`, `docs/design/orphan_baseline.json`,
`background/process_run_complete.py`, `background/publish_cause.py` and
`tests/background/test_a_non_test_gate_refusal_is_named.py`). `ps` showed it; `origin` could not.
It landed at `19f226e46` — *"the refusal that named five green tests now names the gate, and the
orphan it was is frozen"* — while this document was being written. **This seat did not rebuild any
of it**, which is the only reason the two lanes did not collide on the same pathspec.

That landing is correct and it does not touch this defect. Its own commit message verifies "by
the subject" against three conditions — freshness live, origin carrying a later content publish,
the ratchet silent — and all three hold. **The fourth condition the brief named, that the count of
`docs/staging/run_complete_*.md` is falling, is not satisfied and cannot be satisfied by naming a
refusal better.** Naming the blocker correctly does not make the drain faster than the fill.

## Grading the pre-registration

- **P1 — "the five cited blocking tests are green at HEAD": CONFIRMED, and it splits.** All 20
  tests in `tests/background/test_a_staged_document_no_longer_blocks_every_landing.py` pass at
  `a082be80b` (`20 passed in 0.10s`). But the gate's own throwaway checkout
  `/var/tmp/publish-gate-head-7d6otfqf/` recorded
  `FAILED ...::test_a_fork_is_closed_automatically` with `NOT_ADVANCED != RECONCILED`. So the
  register named tests that are green *where any reader would run them* and red *only* inside a
  detached checkout whose origin has moved. Reported as a split rather than a pass: the second
  clause is a real, separate environment-dependence, not a flake to dismiss.
- **P2 — "the live refusal is not a test": REFUTED.** For the cycle I could observe, the gate's
  output carried a genuine pytest `FAILED` summary line, so `kind: test_regression` was an
  observation and not the default I predicted. The default *is* wrong on other cycles — that is
  what the landing in flight repairs — but it was not wrong on the one I measured, and I recorded
  the opposite in advance.
- **P3 — "the orphan ratchet is not the current cause": CONFIRMED.** `tools/orphan_ratchet.py`
  exits 0 and prints nothing in both trees, for two different reasons: at HEAD neither the module
  nor its baseline entry exists; in the shared tree both exist, staged together.

## What is owed next

An instrument whose subject is the **backlog**, not the last publish: the count of queued
`run_complete_*.md` and the age of the oldest, on the freshness surface, failing closed. Without
it every existing signal reads `live` while more than half of all completed runs are discarded
unpublished. Sizing the drain to the fill (or collapsing a backlog to its newest member, which is
the only marker whose figures anyone wants) is the *fix*; measuring the gap is the precondition,
and it is what this seat did not have time to land.

## Re-measured after the wedge cleared (worker tick, 2026-09-03 01:38 UTC)

The drain half of the mechanism was measured **while the gate was wedged**, and the wedge is the
thing that has since cleared. Re-measured at `eb0fae2fc`, it does not survive in that form:

- `sim-runner-log.md` records `[01:26 UTC] [process_run] Publish gate recovered -- cleared wedge
  state, re-armed alarm.` In the **same minute**, 20 markers landed in `docs/staging/done/`
  (`stat` mtimes, 20 files at `02:26` BST = `01:26` UTC). One cycle drained twenty, not one.
- So "a cycle takes ~15 min and drains exactly one marker" describes a cycle spending its time
  being *refused*, not the drain. The 00:10→00:25 observation behind it sits inside the wedge
  window. The healthy-state drain rate is **not yet measured** — one recovery burst is not a rate.
- Queue depth fell 35 → 17 across that instant. **That fall is the bulk archive, not a drain
  outpacing the fill**, and reading it as recovery is the mirror this finding's own class warns
  about. The doorbell's done-condition "the count of `run_complete_*.md` is falling" is satisfied
  and means less than it appears to.
- Fill is unchanged and healthy: `sim_runner` (pid 495) alive, ~4 markers/h by filename hour,
  newest `20260903T011355Z` produced 12 min before this reading.

**The instrumentation half stands, and is untouched by the above.** At this reading
`publish_freshness.describe()` says `live -- figures reached origin 1.2h ago` while 17 completed
runs sit unpublished, the oldest produced `20260902T212239Z` — **4.3 hours** before the "live"
verdict. `snapshot()` still computes `state` from `pub_age` and `com_age` only, so backlog depth
remains an input to no signal. That is what "What is owed next" asks for and it is still owed.

**Not graded here, deliberately:** whether drain exceeds fill *in the healthy state* is now an
open question rather than a confirmed mechanism, and it needs a window that starts after 01:26 UTC.
This note corrects the claim; it does not re-file the finding, which stays BLOCKING on the
instrumentation half alone.

## The owed instrument landed (worker tick, 2026-09-03)

**Discharged:** the two numbers this finding said were owed are on the freshness surface in `background/publish_freshness.py`, proved by `tests/background/test_publish_freshness.py::test_a_live_line_names_the_queue_behind_the_publisher` and `tests/background/test_publish_freshness.py::test_the_oldest_queued_run_is_aged_from_its_utc_name_not_its_mtime`.

The count of queued run markers and the age of the oldest, with four mutation-proved legs:

- **queue_depth()** -- count of the publisher's input queue. None, never 0, when uncountable.
- **queue_oldest_age_seconds()** -- aged from the marker's UTC NAME, never its mtime. The names are
  UTC and this box runs local BST, and the retirement path rewrites mtimes, so an mtime-based age
  would both gain a phantom hour and reset the clock on a marker that had not moved.
- Both ride the line a human reads, including the `live` branch -- which is the whole point, since
  the failure was a reader being told `live` with 35 completed runs queued behind it.

**And one half of this finding is REFUTED, recorded beside the claim rather than quietly dropped.**
The heading says *every* freshness instrument reads `live`. That is too strong. The backlog WAS
observed and WAS paged on, by `background_worker._check_zero_progress`, which alarms when the
oldest marker survives three sweeps and NTFYs through the one contract. The worker log carries it
firing and closing episodes right through the window, including `[2026-09-03 01:26 UTC] ... episode
CLOSED` and `[01:56] Retired 17/17 superseded run_complete marker(s)`. The queue measured 35 is
now **0**.

So the true residue is narrower than the heading: `publish_freshness` -- the module three surfaces
quote -- had no backlog input, so a reader consulting it got a true statement about the wrong
subject. That is what landed. What did NOT land, and is deliberately not built:

**No new verdict and no new threshold.** Depth is an OBSERVATION. The queue is a stack, not a FIFO
-- every marker describes the same world after a run, so the drain clears a burst by RETIRING the
superseded ones -- so a depth threshold would alarm on the mechanism working correctly. And the
property worth paging on already has an owner. A second control over the same subject would be a
control guarding a control, which this project's own rule says is usually not worth having; the
leg `test_a_deep_queue_does_not_change_the_publish_verdict` exists to keep it that way, and fails
if a later hand folds depth into `state`.

**Severity drops to LATENT.** The instrument gap is closed and the queue is drained. What remains
is not an untrustworthy instrument but an open question: whether drain capacity is sized to fill
rate, which the wedge made unmeasurable (a rate measured inside a wedge times a refusal, not a
drain). That needs a clean window, and it is nobody's emergency now that the depth is visible.
