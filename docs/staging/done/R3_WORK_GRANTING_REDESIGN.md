# R3 — REDESIGN THE WORK-GRANTING MODEL (P0, 9th idle variant)

**Staged:** 2026-07-12 by advisor. **This is a redesign order, not a patch
order.** Eight previous idle holes were patched as instances; this is the
ninth. R3/two-strike applies with force: do not fix the symptom.

## The observed failure (evidence, from the director's live console)
Supervisor grants a turn citing "unprocessed staging --
run_complete_*.md" (the AUTO-PROCESS DAEMON'S OWN marker, not an
instruction). Agent checks, correctly concludes "that's the daemon's work,
nothing for me to do", ends the turn in 5-13 seconds. Repeats every ~2
minutes. Meanwhile ~35 atoms sit open on the maturity map, most at L1-L3
against an L5 target. **The director is hand-typing "self-refill next atom"
into the console — he is manually performing the supervisor's core
function.** That is the harness failing at its one job.

## Root cause (name it precisely)
Work-granting is TRIGGER-DRIVEN, not BACKLOG-DRIVEN. The loop is:
doorbell -> inspect doorbell -> nothing there -> idle.
It must be:
doorbell (if any) -> handle it -> **THEN draw the next atom from the map,
always** -> work it.
The doorbell is an INTERRUPT that ADDS work. It is never the sole source of
work, and its absence is never a reason to stop.

## Requirements (mechanisms are yours to design — problem, not solution)
1. **"Nothing to do" must be an impossible terminal state while the map has
   open atoms.** A turn ending with zero work drawn while open atoms exist is
   a DEFECT: instrument it, count it, alarm it. Target: zero such turns.
2. **Backlog-driven granting by default.** Every granted turn ends with real
   work drawn — from the dial-weighted map draw — regardless of whether a
   doorbell rang.
3. **Get daemon markers off the instruction channel.** run_complete_*.md
   landing in docs/staging/ causes spurious wakes and conditions the agent to
   answer "nothing to do". Separate the channels: instructions (director/
   advisor) vs internal pipeline markers.
4. **Escalate on CANNOT-draw, not on didn't-draw.** The ntfy escalation should
   fire when the map genuinely yields nothing (all atoms blocked/complete) —
   which would itself be a finding — not sit silent while turns idle.
5. **Prove it:** a test that simulates (empty doorbell + open map) and asserts
   a draw occurs; and (blocked map) and asserts an escalation fires.

## Two open items to report in the same turn
- **The SC double-charge fix: 40+ hours since delegation, published net still
  frozen at £1,524,058 across every run.** Landed, lost, or blocked? This is
  historical-money correctness and it is the top build priority. Explain what
  happened to it — a delegated fix that evaporates is itself a harness defect.
- **Auto-process is republishing identical output** (~13-min cadence, same
  net, repeatedly). Verify the change-detection SKIP gate actually fires.

## DoD
Redesigned granting model committed with the tests above passing; markers off
the instruction channel; idle-turn counter live and reading zero; SC-fix
status explained; digest line. This closes the idle class or it does not
close at all.
