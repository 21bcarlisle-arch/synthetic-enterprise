# A3: GO. Plus: the map file is the concurrency bottleneck (QUEUE)

**Staged:** 2026-07-13 by advisor. Two items.

## 1. A3_approval_interface: BUILD IT NOW (director said "go")
The twin's approval stands and the director has confirmed it. Reasoning on
record, in case the self-reference ever needs defending: A3 is an INTERFACE, not
a grant of power; the twin is read-only and gains nothing from A3 existing; the
work is inside an open epoch, reversible, and not a one-way door. **Your instinct
to flag the self-reference was right and is commended — flag, then proceed, is
exactly the behaviour we want.** The director will review
director_twin_log.jsonl (07:33:20) at his convenience and may overturn; that is
the design, not a hedge.

Build A3. Expect ~2 transitions: A3 itself, plus A2's L3 unblock (it gives
A2's submit/resolve its first real caller). Note A2 also wants an INDEPENDENT
Expert Hour — run it with a fresh-context evaluator, not a self-review.

## 2. STRUCTURAL FINDING — maturity_map.yaml is the write-contention bottleneck
Disposition: **QUEUE** (register as an atom; do not interrupt the A3 build).

You reported: the supervisor grants up to 4-6 concurrent BUILD atoms, but you
service them **one at a time**, because every atom's build writes
`maturity_map.yaml` and true concurrency would risk lost updates.

**That is the real reason the width has not paid off on BUILD work.** The draw is
6-wide; the writes serialise behind a single YAML file. We fixed the draw, the
gating, the livelock and the epoch gate — and the actual bottleneck turns out to
be a shared file.

Register it and design the fix (mechanism is yours; the requirement is):
- Concurrent builds must not contend on one file. Options to weigh: per-atom
  status files merged into a view; an append-only status journal; a lock/queue
  for map writes only (short critical section); or atoms writing evidence to
  their own file with the map generated from them.
- Whatever the mechanism: **the map remains the single source of truth for the
  draw**, and no update may be lost.
- Prove it: two disjoint BUILD atoms progressing genuinely in parallel, both map
  updates landing, no lost writes, under test.

This is the last known structural cap on velocity. Rank it high.

## 3. Reporting
Keep atoms-below-target in every digest, but ALSO report **level-transitions
banked** (including L0->L1 on two-level atoms). The count alone understates real
progress on two-level atoms whose L2 needs live-pipeline integration — you were
right to name that, and the metric should reflect it.
