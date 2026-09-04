**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The producer ran 6.8x faster than any consumer, and two thirds of the compute was discarded

**Found:** 2026-09-04, autonomous worker (scheduled tick), working the lane 0 throughput
direction. Measured from the committed ledgers, not inferred.

**Status:** lever CHOSEN and LANDED — `background/sim_runner.py`. RECORDED rather than BLOCKING:
the defect it names is fixed in the same commit, and what remains owed is an observation that
needs ~90 min of wall clock (see "What this does NOT fix").

---

## What the direction asked

"Choose and land the throughput lever that lets the run_complete queue reach zero", with three
uncosted candidates: (a) lengthen the sim-runner marker cadence, (b) shorten the gate cycle —
named in the direction as *"the only lever with headroom in it"* — or (c) a newest-marker sweep.
It said MEASURE FIRST: `publish_gate_duration.jsonl` against marker interarrival. That is what
this did, and the measurement refuses the direction's own preferred candidate.

## The measurement

Marker interarrival, `docs/staging/` stamps, 28 runs since 06:00Z 2026-09-04:

| | median | mean |
|---|---|---|
| marker interarrival | **13.2 min** | 15.0 min |

Publish cycle, `docs/observability/publish_gate_duration.jsonl`, gaps between gate completions,
n=34 over 2026-09-03..04 — **separated by outcome, which is the whole finding**:

| cycle following a… | n | p50 | p90 |
|---|---|---|---|
| **PASS** (a publish that published) | 22 | **88.9 min** | 90.3 min |
| FAIL (aborts early) | 12 | 26.7 min | — |

**Arrival 4.55/h against service 0.66/h — a 6.8x oversupply.**

## Candidate (b) is refused by measurement

The direction's premise for (b) was a 2026-08-25 note saying the publisher pays for *two full
suite runs* per cycle, "its own scoped gate then a comparable chain again inside git commit".
Both halves are instrumented and neither supports it:

- scoped gate: **616s** mean (`publish_gate_duration.jsonl`, 14 runs today)
- commit hook: **~110s** (`commit_hook_duration.jsonl`, 107–134s recent passes)

They are not comparable — the hook is about 1/6th of the gate, not a second full suite. Together
they are **12 min of an 89-min cycle (14%)**. Halving the gate returns ~5 min and cannot bridge
4.55/h against 0.66/h. **(b) has no headroom in it; the note that said it did was never measured.**

## The cost was already being paid and thrown away

Markers retired `## Superseded (not published)` — overtaken before the publisher could reach them:

- since 2026-08-28: **152 of 272 (55.9%)**
- all time: **972 of 1504 (64.6%)**

Those runs cost full simulation compute and reached **no reader**. This is the argument for (a)
and it is what makes it free: the reader currently sees a fresh publish every ~89 min because
that is the consumer's rate, and slowing the producer to that rate **does not cost the reader a
single published figure**. It returns ~6x of discarded simulation compute on a machine where OOM
kills have already destroyed a published bound.

## The lever, and why it is derived rather than picked

`BETWEEN_RUN_PAUSE_SECONDS` was `60` — not a cadence at all, but "run flat out". It is now
derived from the two measured quantities:

```python
PUBLISHER_CYCLE_P90_SECONDS  = 5417   # p90 gap after a passing gate
SIM_RUN_DURATION_P50_SECONDS = 732    # 13.2 min interarrival less the 60s pause
BETWEEN_RUN_PAUSE_SECONDS = max(60, PUBLISHER_CYCLE_P90_SECONDS - SIM_RUN_DURATION_P50_SECONDS)
```

→ 4685s (78.1 min); producer period 90.3 min; rho = 0.98.

p90 rather than p50 deliberately: the distribution is tight (88.9 → 90.3), so p90 buys real
margin for ~1.5 min. **Parity is not drainage** — at rho = 1 a queue random-walks and never
reliably empties. The margin is what leaves a window in which `pending == 0` is observable.

## Correction recorded beside the claim

The first derivation in this turn used the median cycle over **today alone (39 min)** and produced
a 1608s pause at exactly rho = 1.0. That was wrong twice: 39 min was skewed by a run of *failing*
cycles that abort early at ~27 min, and parity is not drainage. Separating the gaps by outcome is
what produced the real figure of 88.9 min and the real oversupply of 6.8x rather than 3x. Kept
here because a wrong intermediate next to the result is the evidence the method was applied.

## The control

`test_between_run_pause_is_60` asserted today's answer. It stayed green for the entire period the
queue was undrainable and would have gone red on the fix — exactly backwards, and a textbook
instance of the rule in CLAUDE.md. Replaced with two:

- `test_one_producer_period_covers_one_publisher_cycle` — keyed to the property. Red if anyone
  shortens the pause back, **and** red if the publisher's measured cycle grows without the
  cadence following it.
- `test_the_busy_loop_floor_is_not_what_sets_the_pause` — the reachability null for `max(60, …)`.
  Without it, a degenerate measurement collapsing to the 60s floor would restore the original
  defect while the property control still passed on the floor.

## What this does NOT fix, and what is owed

1. **`pending == 0` is not yet observed.** This makes it reachable; it does not prove it happened.
   The acceptance test is a `pending == 0` sighting in `.publish_gate_state.json` after one full
   producer period (~90 min). Not verifiable inside this bounded tick.
2. **Candidate (c) was not built and should not be** until (a) is observed, per the direction's own
   instruction to measure the existing drain-supersede mechanism before building a fourth thing.
   It is already retiring correctly ("Retired 7/7", 12:49Z) — the queue depth was arrival rate,
   not a broken sweep.
3. **The 2026-08-25 "two full suite runs" note in `process_run_complete.py` is now known false**
   and still sits there uncorrected. Left as a separate finding rather than smuggled into this
   commit.

## Separately observed, NOT actioned here — an armed silent revert

`background/process_run_complete.py` is **staged in the shared index** (`M `) in a state that is
neither HEAD nor origin/main: it carries `episode_clean_publishes` (9 occurrences, matching
origin) but has **`_clear_two_rooms_before_commit` removed** (0 occurrences; both HEAD and
origin/main have 3). It is a stale draft of work that already landed properly on origin as
79e009c81, and it silently reverts the two-rooms repair landed at HEAD as 411648ddf.

It is **not imminent** — the publish commit is pathspec-scoped (`_commit_pathspec`) and will not
carry it — but it is what the daemon **imports on next restart**, and any lane committing that
path would revert the repair. HEAD is 0 ahead / 3 behind origin/main, so the correct resolution is
a **pure fast-forward**, not a hand edit. Not done here: a publisher was live in this tree
(pid 2153582) for the whole tick and a checkout under it is not a bounded-tick act.
