# DIRECTOR STEER — Resource-aware scheduling: light work must never wait behind heavy work (2026-07-19)

**Type:** [STEER] — problem and requirements. The scheduling design is yours.

---

## The problem (observed live today)

Between 05:20 and 06:28 you worked genuinely in parallel — the SSP fork ran while the main seat built the decision-ledger view, absorbed the challenge rider, proposed fan-widening and batched the values-calls. **Then at 06:28 you stopped, and nothing landed for ~90 minutes** while a validation suite ran. Two advisor steers sat unconsumed in `docs/staging/` throughout; DISCOVER/FRAME work sat drawable.

The director: *"Why can't it do anything else in parallel? I still don't like the move at the pace of the slowest approach."*

**First requirement: tell us what actually blocked you at 06:28** — a foreground/blocking tool call on the suite; CPU contention judgment; tree-lock or file-scope overlap; or something else. Evidence, not reconstruction. The remedy differs entirely by cause, and if it was a blocking wait rather than a resource judgment, that is a harness flaw to fix, not a constraint to accept.

## The principle

**CPU-heavy work should only block other CPU-heavy work.** Design docs, DISCOVER/FRAME research, site content, analysis, and consuming staged steers need no core and must never queue behind a validation run. Blocking heavy behind heavy is physics; blocking light behind heavy is waste.

## Requirements

1. **Resource profile becomes a scheduling dimension.** The draw currently reads level, dial, loop_stage and deps — it has no notion of what a candidate will *cost* to run. Give it one, and use it to pack lanes: keep light work flowing while a heavy job holds the CPU.

2. **`loop_stage` is already a free proxy — start there.** DISCOVER/FRAME are document work (near-zero CPU); BUILD is code plus targeted tests (moderate); VERIFY/HARDEN are full validation (heavy). No new metadata is required to begin; refine with measured profiles later (per the test-throughput steer's measurement requirement).

3. **Reconsider the fan cap as a RESOURCE budget, not a COUNT.** `≤3` treats a design doc and a full-suite validation as equivalent units; they differ by orders of magnitude. A budget shape — e.g. at most one heavy concurrent job plus N light ones — protects the machine better AND uses it better. This is directly relevant to your pending fan-widening proposal: **widening from ≤3 buys little if the lanes serialise behind one saturating job**, so this question is arguably a prerequisite for that decision. Note it in the [ACT] when you bring the proposal.

4. **Never let a long-running validation stall the consume path.** Staged steers, [ACT] composition, and director-facing publication must remain live while heavy work runs — these are exactly the things the director notices stopping.

5. **Interleave, don't idle.** If a heavy job must be waited on, wait by polling and interleaving light work, not by blocking the seat.

## Non-negotiables

The bounded-fan SAFETY property must not be weakened by this change: whatever budget replaces the count cap must still be provably bounded, still enforce the locked-worktree reap guard, and still respect file-scope disjointness. This is a scheduling improvement, not a relaxation of the parallel-safety machinery — and R15 applies: prove the bound holds by mutation.

**Risk & proportionality:** touches the draw (the spine every atom flows through) and the fan control (safety machinery). Sequence it: report the 06:28 cause first, then propose the scheduling model, then adopt incrementally with the bound proven at each step. Do NOT change the draw and the fan cap in one turn. Tag: **contract-touching — implement with named mitigations; any weakening of the safety bound is a wall and comes back as [ACT].**

— Advisor, carrying the director's steer, 2026-07-19.
