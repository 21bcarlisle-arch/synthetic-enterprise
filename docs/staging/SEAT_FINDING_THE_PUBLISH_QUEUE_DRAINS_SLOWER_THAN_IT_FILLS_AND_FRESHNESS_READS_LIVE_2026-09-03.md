**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

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
