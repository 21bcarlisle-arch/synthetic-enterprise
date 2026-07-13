**IN PROGRESS (2026-07-13). Actioned as INTERRUPT (accepted the justification).** DoD status:
(1) Self-interrupt discipline codified — CLAUDE.md + `.claude/skills/staging-protocol/SKILL.md` (QUEUE
by default, INTERRUPT only when machine-blocked). DONE. (2) Daemon markers off the instruction channel:
**verified NOT regressed** — `supervisor.py::_is_daemon_marker()` excludes `run_complete_*.md` from
instruction grants (proven: recent "unprocessed staging" grants were all real instructions, never
markers), and `staging_watcher.py:349` silently registers markers with no notification. The 045611
marker sitting in staging was a routine leftover awaiting `background_worker`'s sweep, NOT an
instruction-channel item. Not "fixing" a non-bug. (3) Dial weights reported: Lane H is **2%** of the
below-target draw weight (1 atom, H8, dial 1) — it does NOT dominate; the draw is already company-
weighted (W2 41%, A 17%, W1 14%, C 8%). No rebalance needed — the grooming was a self-discipline
failure, not a dial problem. (4) **Atoms below target = 25, and it is STRUCTURALLY FROZEN, not slow:**
25/25 below-target atoms are `loop_stage=idle` (BUILD-gated), 0 buildable; DISCOVER/FRAME (all the draw
can grant on idle atoms) does NOT move `level_current`. **The count cannot fall until BUILD is opened —
a director-reserved epoch-sequencing decision. Escalated as [ACTION NEEDED] `open-build-epoch2-atoms`**
with six ready-to-build epoch-2 candidates. This is the "structural thing preventing level transitions"
the directive itself said to hunt. **BLOCKING sub-item: the director's BUILD-open decision** — the
moment it lands, I build immediately and the count moves.

# THE TREADMILL — your own findings need the same discipline as ours (INTERRUPT, P0)

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

## DoD
Self-interrupt discipline in CLAUDE.md and the staging skill (QUEUE by default,
INTERRUPT only when machine-blocked); daemon markers provably off the
instruction channel; current dial weights reported; and — the only success
criterion that matters — **atoms below target FALLING.** Report the number in
every digest from now on. If it does not move in the next two hours with an
empty advisor queue, escalate: something is structurally preventing level
transitions and we will hunt that instead.