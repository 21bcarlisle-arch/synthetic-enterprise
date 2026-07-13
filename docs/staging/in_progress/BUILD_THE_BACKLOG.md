> **[PARKED in_progress 2026-07-13]** Predicate report published (docs/observability/idle-atom-predicate-report.md). Affordability cluster + twins + A6 BUILD-opened (16 atoms). First wave of concurrent BUILD forks dispatched. OPEN until below-target FALLS + 4-6 concurrent builds sustained.

# STOP DESIGNING, START BUILDING — moratorium + open the affordability cluster (P0)

**Staged:** 2026-07-13 by advisor, **director-decided**. Disposition: INTERRUPT
(justification: the goal metric has moved the WRONG WAY all day and the cause is
diagnosable now).

## The honest diagnosis (the advisor is the main culprit)
- Map: **54 atoms this morning -> 86 now.** Below-target: **24 -> 48.**
- Cause: **we registered ~32 new atoms today** (coupled-triad twins C6-C12,
  weather physics W1_3-W1_6 + C13 + follow-ons, control-gap atoms F5-F8/H12/H15,
  BRAND1, site doors). **We have been DESIGNING faster than you can BUILD.**
- **Fan-out is weak: 5 atoms in BUILD, 55 IDLE.** The machinery for width exists
  (worktrees merging cleanly, map write-contention fixed) and is not being used
  at volume.
- Today's build-lane time went to genuinely machine-blocking defects (the tmux
  injection was corrupting the DIRECTOR'S OWN INPUT — correctly prioritised) and
  the director's brand change. Those were right. But **the company's own backlog
  did not move.**

## 1. REGISTRATION MORATORIUM (binding on the ADVISOR, effective now)
**The advisor stages NO new design work until below-target FALLS.** Ideas get
held, not staged. This is the advisor's constraint, not yours — but enforce it:
if an advisor doc arrives that registers new atoms while below-target is rising,
**QUEUE it and say so.** You are authorised to push back on the advisor. Do.

## 2. WHY ARE 55 ATOMS IDLE? REPORT THE PREDICATE (do this first)
Do not guess and do not let us guess. **Report exactly why each idle atom is not
being built**, grouped by cause:
- BUILD-gated (which gate? whose authorization is missing?)
- dependency-blocked (on what? is the dependency parked or unbuilt?)
- epoch-deferred (Epoch 3+, so FRAME/DISCOVER only — expected, and they CANNOT
  move level_current, which is fine but must be counted separately)
- dial-deprioritised (what are the current dial weights?)
- genuinely nothing-to-do (should be zero)
**Advisor's hypothesis, to confirm or refute:** the director's BUILD-open this
morning named SIX SPECIFIC ATOMS — it was not a general policy. So most of
epoch-2's remaining work, INCLUDING THE AFFORDABILITY CLUSTER, may still be
BUILD-gated. If true, that is the whole answer and it is a governance bug, not a
capacity problem.

## 3. THE AFFORDABILITY CLUSTER IS BUILD-OPEN (director-decided, now)
**W2_4 through W2_10 — household budget, life-event stream, SME distress twin,
willingness classification, self-rationing, segment debt T&Cs, DD attribution
confound — are OPEN FOR BUILD.** Seven atoms. This is the director's own domain
design and the largest body of real company work on the board, and it has sat
idle all day.
- Confirm **W2_2_population_draw**'s curriculum answer landed: the director chose
  **profile B — trickle continuation at ~1/yr**. If that did not register, it is
  registered now. Unblock anything waiting on it.
- Per THE_COUPLED_TRIAD: build them WITH their company-side twins (C6-C12) and
  measure the gap. World depth with no company response is scenery.

## 4. AND USE THE WIDTH YOU BUILT
55 idle atoms; worktree isolation proven (5 branches, zero conflicts); map
contention fixed. **Run 4-6 concurrent BUILD atoms in worktrees where
file_scopes are disjoint**, plus SITE and DISCOVERY as always. **Report
atoms-drawn-per-cycle and atoms-in-build in every digest.** If those numbers are
1-2 while 50 atoms are idle, the width has decayed again — and that is a defect,
not a preference.

## DoD
Idle-atom predicate report published (grouped by cause, with dial weights);
affordability cluster building, coupled to its twins, with gap measured; W2_2 = B
confirmed registered; 4-6 concurrent builds in flight; **below-target FALLING**
and reported every digest alongside atoms-in-build. The advisor stays quiet until
it does.