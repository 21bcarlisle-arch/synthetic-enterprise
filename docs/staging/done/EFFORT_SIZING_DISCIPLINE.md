# EFFORT SIZING — estimate before building, calibrated against actuals (QUEUE, director-raised)

**Staged:** 2026-07-15 by advisor, **director-raised**. Disposition: QUEUE (draw
in dial order; does not jump the ARCH1 build or the loop work). Register as an
atom (proposal), draw for FRAME/DISCOVER now — thinking is never gated.

## The gap the director identified
Our loop/timer/repeat machinery is RUNTIME TOLERANCE for unknown duration — a
turn takes as long as it takes, boundaries catch it, the deadman alarms on hang.
Necessary and good. But it is COPING, not PLANNING. Nothing estimates effort
BEFORE work starts. The maturity levels (L0-L5) describe MATURITY, not EFFORT —
an L0->L2 atom could be 20 minutes or 3 days and the map cannot tell you which.
So we cannot answer the questions a real backlog answers: is this atom too big
and should be split? which work is cheap-and-high-value? how much effort is
actually left? (The `--once` unit exposed this: one turn, with no notion of how
many turns an atom SHOULD take.)

This is the standard pre-discovery / discovery sizing discipline (T-shirt
sizing), and it is missing.

## Why it fits THIS project unusually well
We have something most teams sizing by guesswork do not: **ACTUALS.** Every
level transition is timestamped in git. So sizing here can be CALIBRATED, not
argued:
- Each atom gets a pre-build estimate: **S / M / L / XL** (in expected turns or
  wall-clock bands — choose the unit).
- Because past atoms' real costs are measurable per size, estimates get checked
  against reality and the calibration improves over time.

## The three uses (this is why it earns its place)
1. **Decomposition trigger:** anything sized **XL is a signal to DECOMPOSE
   BEFORE building** — "sensible chunks," mechanised. Several of this weekend's
   stalls were one atom being far too big (ARCH1, the executor). An XL atom
   should be split into sized children, not started whole.
2. **Honest "how much is left":** below-target counts atoms as if equal. Sized,
   you get REMAINING EFFORT — the number that actually forecasts. Report it
   alongside the count.
3. **Estimate-vs-actual as a learning signal:** the gap between sized and
   measured is itself a finding. Chronic underestimates in a lane mean that lane
   is poorly understood — surface it. (This also directly feeds loop throughput:
   the executor loop stalls when the draw offers oversized or half-done atoms,
   so accurate sizing + accurate map state are what KEEP THE LOOP FED — the
   finding from tonight's --once runs.)

## THE GUARDRAIL (non-negotiable — same law as every other diagnostic here)
**Sizing is a DIAL, not a WALL.** It informs decomposition and prioritisation;
it is NEVER a target or a completion gate. The moment "estimated M" becomes
"must finish in M," it reintroduces the deadline pressure that manufactures
self-certified L3s. Size to DECIDE and DECOMPOSE, never to JUDGE completion.
This is the anti-goal-seek principle (margins/cycle-time/plan are diagnostics,
not targets) applied to effort. Encode that constraint explicitly.

## Requirements (mechanism is the builder's)
- A size field on atoms (S/M/L/XL), set at FRAME time, with a one-line basis.
- Calibration from git-timestamped actuals: compute observed cost distributions
  per size, per lane; surface when an atom's actual blows past its size band
  (as a SIGNAL, not an alarm-to-optimise-against).
- XL -> decomposition-required before BUILD (a soft gate on size, not on time).
- Remaining-effort reported in the digest beside below-target.
- Estimate-vs-actual tracked and surfaced per lane.

## Pitch note
"The company estimates its own work and calibrates its estimates against
outcomes" is a strong, investor-legible sentence — process maturity, not just
capability. Worth surfacing on the Method door once real.

## DoD
Size field live and set at FRAME; calibration computed from actuals; XL->
decompose soft-gate; remaining-effort in the digest; estimate-vs-actual per
lane surfaced; the dial-not-a-gate guardrail recorded in CLAUDE.md. Drawn in
dial order — it does not preempt current build work.
