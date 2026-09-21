**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the status page states two net margins and T6 now fires on every tick"

# Pre-registration: which of the two net margins is stale, and why the writer stopped

**Delivery seat, 2026-09-19, claim
`the-status-page-states-two-net-margins-and-t6-now-fires-on-every-tick`. Written before the
cause was traced, and left uncorrected beside the result.**

---

## What was already measured before this was written

Two reads, both cheap, both already done and recorded here so the predictions below cannot be
read as covering them:

1. `docs/status/LATEST.md` states **£1,521,070** (twice, inside dated `## PREVIOUS` entries of
   2026-07-23 and 2026-07-24) and **£158,278.48** (once, in the auto-written *"Latest simulation
   results"* block at the foot of the file).
2. `docs/observability/run_history.json` — the artefact `detect_t6` names in its own
   `evidence_refs` as *"raw data"*, and whose **last** entry is the comparator — has 100 entries,
   the last written **2026-07-17T09:57Z**, value **1521069.65**.

So T6's `computed` is **£1,521,070**, and the single trigger it fires every tick reads
*"claim says 158278, raw data says 1521070"*.

**This inverts the drawn item's stated motive.** The item reasoned that the page contradicts
itself and that T6 therefore cannot agree with it whatever the computed figure is. True — but the
direction is the finding: the figure T6 calls **raw data** is 64 days old, and the figure it
denounces as the **false claim** is the fresher of the two. The remedy the item proposes ("delete
the one that is not the book") would, applied naively to the £1.5M, delete the only claim that
agrees with the comparator and leave the alarm firing exactly as loudly.

## The predictions

**P1 — one writer, two sinks, one sink silently dead.** I predict `background/process_run_complete.py`
writes *both* the LATEST.md run block *and* the `run_history.json` append, and that the append is
guarded (a conditional on a key in the run artefact, or a `try/except`) which has been taking the
silent branch since 2026-07-17, while the LATEST.md write next to it kept succeeding.

*Alternative I am predicting AGAINST:* a separate process owns `run_history.json` and simply
stopped being scheduled. If that is what I find, P1 is refuted and I will say so here.

**P2 — the two figures are the same quantity, not two quantities.** I predict `net_margin_gbp` in
run_history and `total_net_gbp`/`net_margin_gbp` in the LATEST.md block are the same measure of
the same book, and that the ~10x gap is a **change in the world or the cohort between July and
now**, not a definitional difference. If instead the July run was a 19-account teaching cohort and
the current run a larger book, then they ARE two quantities sharing a name and the page owes each
a name — which is the item's own reading, and P2 is refuted.

**P3 — no control asserts the comparator is fresh.** I predict nothing in the tree reds when
`run_history.json` stops being appended to, because staleness of an append-only artefact has no
natural failing edge: the file is present, parses, and returns a number.

## What would make each prediction wrong

P1 is refuted by finding the append in a module `process_run_complete` does not call. P2 is
refuted by the account counts differing materially between the July entry and the current block.
P3 is refuted by any existing test naming `run_history` freshness.

---

## RESULTS — written after, beside the predictions, which are left as they stood

**P1 — PARTLY REFUTED, and the refutation is the better finding.** The writer is not broken and no
guard is taking a silent branch. `process_run_complete` calls `generate_insights.append_run_history`
on every run and it **works** — the shared tree's working copy of `run_history.json` has a last
entry of `2026-09-19T21:39:56Z`, git `52f572916`, **£158,278.48**, which agrees with LATEST.md's
live block exactly.

What is broken is that **`run_history.json` has been `M` — modified and uncommitted — on the shared
tree since 2026-07-17**, so `HEAD`'s copy of the project's run ledger is 64 days old. The append is
committed by nobody. I predicted a dead writer and found a live writer whose output never lands.

**And that inverts my own reading of the alarm, which I had already written above as settled.** The
direction of T6's trigger depends on which copy of `run_history.json` the reader has:

| comparator | computed | T6 fires |
|---|---:|---|
| shared working copy (live, 2026-09-19) | £158,278 | *claim says 1521070, raw data says 158278* |
| `HEAD` / any fresh checkout (2026-07-17) | £1,521,070 | *claim says 158278, raw data says 1521070* |

The "what was already measured" section above reports the second of those as though it were the
live state. It was the state of **this isolated worktree**, whose `HEAD` copy is the stale one. The
organ running on the shared tree sees the first. Both rows are one trigger per tick; the sentence
that needed correcting is *which figure the director is being told is false*.

**P2 — CONFIRMED on the quantity, and that settles the remedy.** Both figures are `net_margin_gbp`
as emitted by `generate_insights` from the same field of the same run artefact. They are **one
quantity at two vintages**, not two quantities sharing a name. The cohort did move materially
between them (1,588 bills / N=19 in July, 9,892 bills now), which is why the figures differ by ~10x
— but a different cohort does not make a different measure. **So the page owed each figure a CLOCK,
not a name**, and the drawn item's first remedy is the right one of the two it offered.

**P3 — CONFIRMED, and by a route I did not predict.** Nothing reds on a stale comparator. I
predicted the reason would be that an append-only artefact has no failing edge; the actual reason
is that the artefact is never committed at all, which no test anywhere asks. Filed as its own
finding — see `SEAT_RESULT_ONE_QUANTITY_TWO_VINTAGES_...`, §5.
