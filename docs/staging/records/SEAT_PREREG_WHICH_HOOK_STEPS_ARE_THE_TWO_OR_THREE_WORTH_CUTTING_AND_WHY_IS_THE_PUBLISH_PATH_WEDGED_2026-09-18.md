**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
(`cut-the-hook-chain-because-the-only-remaining-move-when-the-floor-meets-the-ceiling-is-a-cheaper-chain`)

# Pre-registration: which hook steps are worth cutting, and why is the publish path wedged

Delivery seat, 2026-09-18, **written before running `tools/time_the_commit_hook_chain.py` a second
time and before reproducing the publish gate failure.** Nothing below is edited after the fact; the
result document scores it line by line and records refutations beside their replacements.

## What is already known and is therefore NOT predicted

From the single existing run (2026-09-17, commit `54e5a5c87`, its message is the only record —
no readings JSON was committed):

| Step | Reading then |
|---|---|
| `startup_anchor_freshness` / `discover_maintained_surfaces` | 42.19s → **2.01s after that turn's cut** |
| `site_lane_gate` | **142.9s** (854 tests in 171s; its own docstring claimed ~6s / ~164 tests) |
| always-run control set | **185.4s** across 38 files |

Those three are the only per-step figures that exist. There is no committed table of the other
eighteen steps, so everything else below is a genuine prediction.

## Predictions

**P1 — the shape of the bill.** The two dearest steps will be `site_lane_gate` and the always-run
control set, in that order or the reverse, and together they will be **over half** the chain's
measured total. No third step will be within a factor of two of either.

**P2 — growth is in the test sets, not the gates.** Every step whose cost is a `pytest` invocation
will have grown since 2026-09-17; every step that is a static scan of the tree will be **flat to
within ±30%**. Specifically `site_lane_gate` reads **> 142.9s** and the control set reads
**> 185.4s**. (This is the mechanism the +6.3%/day fit could not attribute: if it is true, the
chain grows because the tree gains tests, and a cut has to change *which* tests run, not make a
scan faster.)

**P3 — the cheap-gate block is nearly free.** The ten smallest steps will sum to **under 30s**,
i.e. under 5% of the total. Cutting any of them is not available as a remedy and I will say so
rather than cutting something visible-but-cheap.

**P4 — the total on an empty index will be between 250s and 700s**, and will NOT reconcile with the
~330s real-commit chain, because the FLOOR steps read near-zero here and are the bulk of a real
commit. I predict I will be able to say which side of the gap the difference lives on.

**P5 — the wedge.** The 13 consecutive publish-gate failures since 2026-09-17T12:40 will have a
**single** cause, not thirteen. I predict the cause is NOT the seven-second headroom red named in
`WORKER_RESULT_…_COUNTED_TWO_CHAINS_AS_ONE_2026-09-17.md` §3 (that was fixed at `387798957`) but is
a **second, newer** red, and that it is visible in the publisher's own log without running the
suite.

**P6 — the wedge and the growth are the same incident from two ends.** I predict the failures are
*not* caused by the chain being slow (the gate rows show ~35s durations, far under the 3800s
ceiling), so cutting the chain will NOT unwedge the publisher, and I will have to say so plainly
rather than claiming one fix bought both.

**P7 — what a cut is allowed to be.** Whatever I cut, the *set of tests that run* must not shrink
without the refusal that shrinks it being visible. I predict at least one of the two dear steps is
expensive because it re-runs work a sibling step already did, and that the cut is a de-duplication
rather than a deletion. If it is not — if the only available saving is running fewer controls —
**I will not take it silently**; that is a coverage decision and it goes to the director.

## How each is scored

P1–P4 by the second run's own readings, printed in full in the result document including the steps
that are cheap. P5–P6 from `docs/observability/.publish_gate_state.json`, the publisher's log, and
one re-run of the named tests in an extract. P7 by the diff.

## What would make this turn worthless

A cut measured only by the timer that wrote it. Any saving claimed below is measured the same way
twice — the timer before, the timer after, same machine, same index — and if the two readings
straddle a different machine load I will say the reading is not attributable rather than quoting
the difference.
