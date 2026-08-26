**Severity:** LATENT · **Lane:** H_harness

# The producer OOMs because the book grew, and the only two clean repairs are the director's

**Rank: TOP.** This is what is keeping the site at 05:27Z, which is the director's own stated
first priority for 2026-08-24 ("Publishing paused at 07:52 and the site is showing 05:36. Clear
that first.").

**Why LATENT and not BLOCKING, deliberately.** BLOCKING refuses every level raise in this lane on
the grounds that the lane's own instruments may be wrong, and H_harness holds 117 atoms. An
outage does not make those instruments wrong, and freezing the lane would be a blanket halt of
exactly the kind Rule 0 refuses — priority is carried by the rank line above, not by taking
hostages. **One narrower consequence is real and does bind:** while the site is stale, no level
move anywhere may cite R11 verification against the live surface, because that evidence cannot
currently be obtained. Cite the repo and say so, or wait.

This is the THIRD pass over the same failure today. The first two each stopped one step short, and
both were right to file rather than guess. This one adds the mechanism and, more usefully, the
reason it has no cheap repair.

## Observed, with evidence

- **Fourteen OOM kills**, kernel log, from uptime 604268 to 619417 — i.e. beginning ≈09:20 UTC and
  continuing to 13:40. `anon-rss` at kill rises across the sequence: 9.5 → 12.4 → 13.9 → **14.2 GB**.
- **The last successful run output is 09:07** (`run_output_26afdac4f_20260824T090747Z.json`).
  The kills begin immediately after it. Nothing has published since.
- **The guest has ~15 GB**, not the 32 GB on the host — corrected in CLAUDE.md earlier today by the
  pass that first found this.
- Runs reach ~12 GB at 38 minutes and are killed at ~39. They are not failing; they are being
  killed before they can finish.

## The mechanism, `inferred` but tightly constrained

Settlement memory scales with **book × years**. The book grew today from ~13 accounts to **81**
(PB1's population draw and PB2's earned opening book, both landed this morning), against an
unchanged 10-year run window to a 2026 horizon. `net_new_acquisition`'s own note sizes the campaign
half of this at "600 customer-years ≈ 7 million periods, roughly 18 minutes"; the resident book is
settled on top of that. A 6× book against a fixed horizon is the only thing that changed at 09:07,
and it is sufficient to explain a run that used to fit and now does not.

**This is not a regression in anyone's code.** It is the cost of the growth the director asked for
arriving before the machine was sized for it.

## Why there is no cheap repair, which is the part worth recording

Three candidate repairs, and the two clean ones are both reserved:

1. **Shrink the world.** The population size is set by
   `docs/design/curriculum/population_draw_activation.json` — a director-authorised R13 CURRICULUM
   artefact ("Tell me before any published figure moves, and re-baseline honestly"). Tuning it to
   fit memory is adjusting a curriculum value to make a machine problem go away. **Reserved.**
2. **Give the guest more memory.** A `.wslconfig` change on the Windows host requiring a WSL
   restart, which would terminate every running process — the supervisor, the seat, the publisher,
   and any in-flight landing. **Reserved**, and disruptive rather than merely out of scope.
3. **Reduce the run's footprint in code.** NOT reserved, and the right answer — stream or aggregate
   settlement periods rather than materialising all of them. But note the trap: **validating it
   requires repeatedly running the 40-minute, 14 GB job that cannot currently complete.** The fix's
   own test loop is blocked by the defect. Anyone taking this needs a short-horizon closed-loop
   harness FIRST (R4: build the smallest closed-loop test), not a direct attempt.

## What NOT to do

- Do not restart the producer. That has now happened ~14 times and is what the RUNG-1d doorbell
  keeps prescribing; the process is healthy and the runs are real.
- Do not read the flat growth curve as a commercial result. It is separately capped by the
  settlement engine — see `site/data/book_growth.json`, which now states that six of ten years were
  bound by our own engine.
- Do not run a gate suite or a second heavy job while a run is in flight. It does not cause this
  (the run reaches 14 GB alone) but it converts a marginal run into a certain kill.

## Immediate mitigation available without any ruling

Serialise: hold heavy work while a run is live. This does not make a 14 GB run fit in 15 GB, so it
is a palliative, not a repair — recorded so nobody mistakes it for one.
