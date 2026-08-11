# WORKER FINDING — a register whose gate checks every row still published three wrong numbers in its own heading

**Found:** 2026-08-12, worker tick, `KNIFE3_wall_crossing_paydown` (L0→2, `loop_stage: build`) draw
**Class:** prose-with-no-falsifier sitting on a gated artefact · **Disposition:** instance fixed at
`9ef7d5d6e`; the CLASS is unaudited and is what this finding registers
**Answer to the draw:** still **L0→2, in build.** Step 18 landed; 34 crossings remain owed.

## What was found

`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §4 is the register that
`tools/wall_crossing_dispositions.py` gates: every live crossing must carry a ruling, in both
directions, rc 2 otherwise. That gate is real and it works — it is the reason this atom's rows are
honest.

Its own section heading read **"all 91 examined crossings, 41 of them still live"**. The paragraph
under it read **"FORTY-THREE have since been CUT"** and **"the tree carries 45"**.

Measured by the walker the same document names as its source of truth: **34 live, 57 cut.**

Three hand-typed numbers, disagreeing with the measurement *and with each other* — 41 live against
45 in the tree, in adjacent clauses. Sitting four lines above:

> The live count is not maintained by hand here — `tools/wall_crossing_dispositions.py` prints it
> from the walker on every run, and the two numbers disagreeing is itself the failure the tool
> exists to raise.

The sentence describing the property was true of the ROWS and false of the PROSE directly above it.

## Why nothing could fail

The tool compares **rulings to walker**. Nothing in this repo compares **prose to walker**. So the
gated part of the document was continuously verified while the summary a reader actually takes away
from it — the only part of a 1,700-line register most readers will read — was the one quantity in it
with no falsifier at all, drifting by seven, fourteen and eleven respectively across steps 11–18.

This is the shape already in the ledger as *[prose inventory needs a falsifier]* and *[the record
can outrun the code]*, but with a sharper edge worth naming separately: **the presence of a working
gate on an artefact is itself what made the unfalsified prose credible.** An ungated design doc
carries no authority; a doc whose header says "read by `tools/…`, rc 2 on disagreement" does. The
gate laundered the ungated part of the same file.

## The distinction the fix draws

Not "re-type the numbers" — that is the instance fix, and it rots again at step 19 by construction.
What landed instead:

- a **dated step record** (§3m's "36 → 34 live", stamped with the step that measured it) is a
  historical claim, true when written, and stays;
- a **standing summary** of the present tree is not writable in the document at all. `python3
  tools/wall_crossing_dispositions.py` prints live/cut/owed/grandfathered from the walker, and that
  is now the only place those numbers exist.

## What is NOT done, and is the actual ask

Per R10 an absurdity-class defect may not be closed with an instance fix, and this finding does not
claim otherwise. **The class is unswept.** The candidate population is every document that cites a
tool or test as its verifier and also states a standing count in prose — the design docs under
`docs/design/`, the maturity-map atom records, and the observability registers are all in it.

Two shapes worth separating in the sweep:

1. **Standing counts that a tool already measures** — delete them, as here; the tool is the answer.
2. **Standing counts nothing measures** — these are worse, because there is no tool to point at.
   Either mint the measurement or date-stamp the claim into a historical record.

Not attempted in this tick: this was a `build`-stage draw on the crossing paydown, and per
SELF_INTERRUPT_DISCIPLINE a finding of my own gets queued, not fixed on sight. The supply of these
is plausibly large, which is the argument for a census before any repair.

## Evidence

- Instance fix + the cut it rode with: `9ef7d5d6e`, on `origin/main`, gate rc 0
  (`python3 -m tools.surgical_land --verify 9ef7d5d6e` → `receipt consistent … gate-rc 0`).
- The measurement contradicting the old prose, at HEAD:
  `python3 tools/wall_crossing_dispositions.py --at-head` →
  `34 live crossings (32 direct, 2 indirect); 91 ruled (cut 57, owed 34, grandfathered 0)`, rc 0.
- The superseded text is recoverable at `ecbbc083a:docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`
  §4 rather than quoted from memory.
