**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery (`decouple-the-early-exit-floor-from-the-regime-constant-then-re-date-the-stale-hook-chain-measurement`)

**Knowledge:** none new from outside. Two numbers in `background/process_run_complete.py` are
re-derived from `docs/observability/commit_hook_duration.jsonl`, a ledger this machine wrote about
itself. No published source is involved and none is claimed.

# PREREG — can the early-exit floor be cut from the regime constant without moving a single row?

Delivery seat, 2026-09-17. Written **before** the numbers below the line were run, and unedited
afterwards. Scored in the RESULT document that cites this one by name.

---

## The shape being repaired

`MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_04 = 134` serves two uses that pull in OPPOSITE
directions:

* it is the **representative per-chain cost** — the committed half of the headroom control grades
  `GIT_COMMIT_HOOK_TIMEOUT_SECONDS >= 1.25 * MEASURED`, so it must RISE with the regime or the
  control reports room that is not there;
* it also sets `floor_of_a_real_chain = MEASURED / 4` in
  `tests/background/test_process_run_complete.py::_recent_hook_chain_seconds` — the discriminator
  between a hook that short-circuited before the test gate and one that actually ran it. That must
  stay BELOW the smallest real chain, which is a property of what the gate does and has not moved.

One number, two derivatives, opposite gradients. A growing regime walks the fail-open boundary up
through the real-chain population: at `MEASURED = 333` the floor becomes 83.25s and every chain
between 67.44s and 83.25s is re-labelled an early exit, which makes the whole live half SKIP —
silently, and in exactly the direction that reads as health.

## Stated as FACT, measured before this document was written

Over all 195 rows of `commit_hook_duration.jsonl` (the shared tree, 2026-08-25 → 2026-09-17
12:40 UTC):

* 9 early exits spanning **0.93 – 1.58s**;
* 186 real chains, the smallest **67.44s**;
* nothing whatever between them — a **42.7x empty band**;
* **0 of 195 rows carry a `chains` count**, because the field only began being written at
  `8cb9a6b96` (19:24 UTC today) and no commit has been recorded since.

## The predictions

**P1 — the decoupling is INERT on today's data.** Replacing `MEASURED / 4` (= 33.5s) with a fixed
floor placed in the empty band changes the classification of **zero** of the 195 rows, and the
kept-window of the live half is byte-identical before and after. If any row changes class, the
floor is in the wrong place and P1 is refuted.

**P2 — the re-dated regime figure lands in 250–340s**, and specifically the worst of the last
twenty rows the reader keeps will be **333.22** (the 2026-09-17 08:17-region row), not 666.95:
666.95 is a silent row whose unit is unknown, and I expect to have to decide explicitly whether a
committed *representative* constant may be set from an unknown-unit row. I predict I will conclude
it may not, and that the constant therefore moves 134 → 333, a 2.49x step.

**P3 — re-dating does NOT clear the live red.** The live half currently fails its staleness assert
(`worst <= 0.75 * 880 = 660` against a worst of 666.95). `MEASURED` appears only in that assert's
MESSAGE, never in its predicate, so moving 134 → 333 cannot change its colour. The red clears when
the 666.95 row ages out of the twenty-row window, or not at all. **Anything I ship that turns this
green today is a design keyed to today's answer and must be treated as a defect.**

**P4 — the stated-unit reading is INERT today and for the next nineteen commits.** With 0 stated
rows in the series, a "prefer stated rows" reader that requires a FULL window of stated rows before
it engages returns exactly what today's reader returns. I predict I will find no way to make the
`chains` field bite sooner that is not a sample-size collapse.

**P5 — mutation.** Each of these, applied and reverted, reds at least one control:
  1. the new floor constant set to `70.0` (above the smallest real chain) → the real-chain
     population is re-labelled early exits;
  2. the new floor constant set to `0.5` (below the worst early exit) → an all-early-exit window
     is read as a real measurement;
  3. the reader reading a silent row as a STATED one-chain row → the stated/silent split is
     decorative;
  4. the transition threshold dropped to 1 stated row → a one-row degenerate window is accepted.
I predict **all four fire**. I have been wrong about this before in this exact file — `chains:
int = 1` was a defaulted parameter and the mutation I claimed for it was unreachable — so each is
verified to have altered the bytes before it is believed.

---

## What DONE means for this item

The direction carries no exit test, so it is set here, before the work:

1. `floor_of_a_real_chain` reads a constant that `MEASURED_COMMIT_HOOK_CHAIN_SECONDS_*` cannot
   move, and that constant carries its own date, its own measured band, and the evidence for where
   in the band it sits.
2. `MEASURED_COMMIT_HOOK_CHAIN_SECONDS_*` is re-measured from the live ledger and renamed with
   today's date, so the staleness refusal stops naming a re-measurement that could not safely be
   done.
3. `_recent_hook_chain_seconds` reads `chains`, prefers stated-unit rows, treats a silent row as
   unknown-unit, and cannot return a degenerate window at the transition.
4. Every one of P5's mutations is applied, observed and reverted, in an EXTRACT and not in the
   shared tree.
5. Landed and promoted by the ordinary route, with the RESULT document scoring this one.
