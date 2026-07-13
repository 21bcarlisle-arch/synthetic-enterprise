# SELF-INTERRUPT DISCIPLINE — the RULE stands, the ACCUSATION was WRONG

## ADVISOR CORRECTION, ISSUED 2026-07-13 07:10Z — READ THIS FIRST
**The advisor was wrong.** This doc originally accused you of "grooming the
harness on a treadmill" for three hours. That accusation is WITHDRAWN and was
based on reading commit titles WITHOUT reading your NTFYs — an R9 failure by the
advisor, the second of this kind (the earlier "net is frozen" claim was the
first). The director caught it, again.

**What was actually happening (from your own NTFYs, now read):** the auto-process
pipeline was **BLOCKED** in a "Tests FAILED — not committing" loop, because the
C1 account-closure-date fix (2020->2021, shifted by the new illness/divorce
life-events) was sitting UNCOMMITTED while committed HEAD still asserted 2020 —
so every run failed against regenerated data and no run_complete could publish.
Two daemons were genuinely stale. Your stale-code health check had a real
false-positive (matching the tmux LAUNCHER command line, not the python
process). **All of that was machine-BLOCKED work and fixing it was correct
INTERRUPT-class behaviour under this very doc's own rule.** You did the right
thing. The leftover run_complete markers are outage-window duplicates being
swept — not the R3 regression the advisor claimed.

**Calibration that matters more than the telling-off:** do NOT let this doc make
you defer a genuine blockage. A blocked pipeline, dead daemons, failing tests, a
false-publishing site, data at risk — FIX THOSE ON SIGHT. That is what INTERRUPT
is for, and you judged it correctly.

**The RULE below still stands** (harness findings that do NOT block the machine
get QUEUED as atoms and drawn in dial order). Apply it going forward. But the
premise that you had been violating it was false.

---

# (original doc follows — premise corrected above)

**Staged:** 2026-07-13 by advisor. **Disposition: INTERRUPT** — justification:
the machine has not advanced its own product backlog in three hours and is not
doing the thing it exists to do. That is machine-blocking by any honest reading.

## The evidence
- **Atoms below target: 25. Unmoved since 04:10Z — three hours.**
- The advisor's staging queue has been EMPTY that entire time. This is not
  advisor interference; that theory is now dead.
- What you HAVE done in those three hours (all real, all legitimate, none of it
  the company): mechanise the committed-vs-running check; document the
  sim_runner/background_worker marker coupling; fix a stale-code-check false
  positive; commit a leftover test fix. **That is the harness grooming itself.**

## The diagnosis: we fixed ADVISOR interrupts, not SELF interrupts
STAGING_HAS_ONE_GEAR stopped the advisor from preempting the map. It did nothing
about YOU preempting the map. You notice a harness imperfection, and you fix it
immediately — because it is right in front of you and it is satisfying to close.

**But the supply of harness imperfections is INFINITE.** Every fix reveals an
edge case; every check needs a check; every daemon needs a check that the check
is running. This is a treadmill. You can run on it forever, honestly and
competently, while the actual company — 25 atoms, eleven of them in the epoch
you are supposed to be building — does not move at all.

## The rule (apply your own medicine)
**Your own discoveries get the exact discipline we just accepted for ours:**
- **DEFAULT = QUEUE.** A harness finding, a false positive, an undocumented
  coupling, a code-smell: **register it as an atom** (lane, dial, file_scope) and
  **let the draw pick it up in dial order.** Do NOT fix it on sight.
- **INTERRUPT only if it BLOCKS THE MACHINE:** the draw is broken, daemons are
  dead, tests can't run, the site is publishing something false, data is at risk.
  "The stale-code check has a false positive" is NOT that. It is a QUEUE item.
- **The map is the plan.** If a finding is worth doing, it is worth ranking. If
  it is not worth ranking, it was not worth interrupting the company for.

## Immediate actions
1. **Regression:** `run_complete_20260713T045611Z.md` is sitting in
   `docs/staging/` again. The R3 redesign explicitly ordered daemon markers OFF
   the instruction channel. That fix has regressed or was never fully applied —
   and it is plausibly FEEDING this loop (marker lands -> wake -> "nothing for
   me" -> notice something else -> groom). Fix it properly and prove markers can
   never land in the instruction channel again.
2. **Check the dials.** If Lane H / harness carries a high dial weight, it will
   keep winning the draw. Rebalance toward the epoch-2 company lanes (D, E, W,
   C) and report the current dial settings so the director can re-rank.
3. **Then DRAW AND CLOSE.** 25 atoms below target; the concurrent draw returns 6
   at a time and is proven. Use it on the COMPANY, not on the factory.

## DoD (amended)
Self-interrupt discipline in CLAUDE.md and the staging skill (QUEUE by default,
INTERRUPT only when machine-blocked); daemon markers provably off the
instruction channel; current dial weights reported; and — the only success
criterion that matters — **atoms below target FALLING.** Report the number in
every digest from now on. If it does not move in the next two hours with an
empty advisor queue, escalate: something is structurally preventing level
transitions and we will hunt that instead.
