**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`fit-the-hook-chain-growth-series-because-the-deadlines-room-halved-in-a-fortnight-and-nothing-watches-it`)

**Knowledge:** none new from outside. Every figure below comes from this machine's own
`docs/observability/commit_hook_duration.jsonl`. No published source is involved and none is
claimed.

# Pre-registration: is the hook chain GROWING or STEPPING, and is anything still feeding the series?

Delivery seat, 2026-09-18. **Written before any fit was run.** The descriptive regime table in
`background/process_run_complete.py:400-412` was already in the tree when this was written and is
NOT re-predicted here — it is the input. What is predicted is what a fit says about it, and what
the series' own liveness turns out to be.

---

## What the drawn item asked, and the one claim of its own I have already refuted

The item cites `docs/observability/commit_hook_duration.jsonl` as the subject. **That path does
not exist in this worktree and is in no commit**: the series is an UNTRACKED machine-local
artefact, present only at `/home/rich/synthetic-enterprise/`. A drawn item's paths are
un-re-asked predictions and this one is wrong in a way that matters — see P0.

The premise commit `bfbc2b4e9` is an ancestor of `origin/main`, as the draw said. That is expected
and does not spend the item: `bfbc2b4e9` is the commit that SET
`MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_17 = 333` and explicitly declined to claim a trend.
The question it left open is the one asked here, and it is still open.

---

## P0 — the series is COLD, and the control cannot tell cold from healthy

Observed before any fit: the last row is `2026-09-17T12:40:51` (`b55667741`, 666.95s). The
sibling ledger `publish_gate_duration.jsonl` wrote at `2026-09-17T23:17` and the shared tree
committed at `2026-09-18T00:21`. **The machine kept committing for ~27 hours and the hook-chain
series recorded none of it.**

> **P0.** No row in the series carries the `chains` key that `_record_commit_hook_duration` gained
> at `bfbc2b4e9` on 2026-09-17. If that holds, then not one row has been written since the repair
> landed, and the cause is a property of the landing path rather than a quiet machine.

> **P0b.** `_recent_hook_chain_seconds` has no freshness clause. I predict its window is defined
> by ROW COUNT alone, so a series frozen at its last twenty rows grades the deadline forever and
> reads exactly like a healthy machine. **This is the fail-silent half of the wedge and it is a
> worse defect than the growth the item asked about**, because the growth is at least visible.

**P0 is the one I expect to matter.** If it holds, a watcher over the series' VALUES would be a
watcher over a corpse.

---

## P1 — GROWTH or STEP

The fit is over real chains only: rows with `duration_seconds >= REAL_CHAIN_FLOOR_SECONDS_2026_09_17`
(10.0s), excluding the two rows the publisher's own record names as multi-chain landings
(`2c89bd534` 1381.52s, `b55667741` 666.95s), over 2026-08-25 → the last row.

> **P1.** The 2026-08-31 move is a STEP and the 2026-09-08 → now move is GROWTH. Concretely: a
> piecewise-constant model with a breakpoint at 2026-08-31 beats a single log-linear trend on the
> 08-25→09-08 segment; and on the 09-08→now segment a log-linear trend beats a piecewise-constant
> model. I am predicting the two moves have **different shapes**, which is the claim the item's
> "GROWTH or a regime STEP like 2026-08-31's" poses as an either/or.

> **P2.** The 09-08→now growth rate, fitted log-linear, is between **+4%/day and +12%/day**. At
> the midpoint the per-chain cost reaches the 720s bar (`0.75 * 880`, the staleness assert) within
> **10 to 35 days** of 2026-09-17.

> **P3 (the one I most expect to be wrong).** n on the 09-08→now segment is small — the constant's
> own comment says 9 runs over three days for the last regime. I predict the segment has **fewer
> than 40 real-chain rows**, and that the log-linear slope's 95% interval **includes zero or comes
> within a factor of three of doing so**. If that holds, then "the trend is real" is NOT
> establishable from this series and the honest answer to the item is *"I cannot yet say"* — which
> is a result, not a failure, and it changes what the watcher must be.

---

## P4 — what the watcher must therefore be

> **P4.** If P0 holds, the smallest control that can fail is NOT a trend watcher. It is a
> **freshness refusal on the series itself** plus the standing room check. A watcher keyed to
> today's slope would be keyed to today's answer, which CLAUDE.md names as exactly backwards.

> **P5.** Whatever is built, I predict its mutation fires: mutating the freshness bound must red
> it, and mutating the room arithmetic must red it, independently. If either mutation does not
> fire I will record whether it was a missing test or an equivalence rather than assume the
> flattering one.

---

## What would refute the whole frame

If a row HAS been written since `bfbc2b4e9` and I simply read a stale copy, P0 collapses and the
item's original growth question is the whole of the work. I check that against the shared tree's
live file, not this worktree's, before anything else.
