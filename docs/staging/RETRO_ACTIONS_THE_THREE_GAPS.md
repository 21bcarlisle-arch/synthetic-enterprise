# RETRO ACTIONS — the three CLASS-level gaps the instance-fixes missed (QUEUE)

**Staged:** 2026-07-15 by advisor, director-approved. Disposition: **QUEUE** —
draw in dial order BEHIND the transport migration and the flag-flip; none is
machine-blocking. Source: WEEKEND_ROOT_CAUSE_RETRO. Audit finding: the
instance-level theme fixes (H12, H15, commit-clock deadman, Rule-0 mechanism,
pull loop) are in place; these three CROSS-INCIDENT / CLASS actions are not — and
they are the ones that determine whether we learn ACROSS failures or merely log
them. (Note the irony, and put it in the casebook: our own action list had
fixed the instances and missed the class — the retro's own thesis, reproduced.)

## ATOM 1 — Unified Failure Register (the structural hole; rank highest of the three)
**Problem:** 11 honest retros exist, but nothing indexes ACROSS them. No
strike-counter spans incidents. Direct evidence: two files six days apart
(`wake-doorbell-third-strike`, `tmux-injection-third-strike`) BOTH independently
reached "third strike" for the same class — because strikes were counted within
a retro, never across the register. **This is why two-strike redesigns fired
years late: the rule existed; the counting substrate did not.**
**Requirements (mechanism yours):**
- One append-only register over all retrospectives: date, one-line root cause,
  THEME TAG (T1 fail-silent / T2 shared-domain / T3 local-vs-global / T4
  prose-decay / T5 transport-vs-content, extensible), the fix, and
  instance-vs-class.
- **Strike-count is computed GLOBALLY per class, across the register** — so
  "Nth strike" is a property of the class, not the individual retro. When any
  class hits 2, the two-strike/R3 redesign obligation fires automatically and
  is surfaced, not left to be noticed.
- Every new retro appends here (make it part of the retro ritual/skill, so it
  cannot be skipped).
- Surface on the Method door: the pattern IS the IP.

## ATOM 2 — Harness-Self Mutation Audit (point R15 inward)
**Problem:** H12 mutation-tested the SIM/compliance controls. The controls that
actually failed and cost six hours — the deadman, the idle/liveness detector,
the pull loop's continue-guard, the kill switch — are HARNESS controls, and they
were never mutation-tested. The doctrine exists; it was never aimed at the
machinery that runs the company.
**Requirements:**
- Enumerate every HARNESS control (liveness/deadman, idle detection, wedge/H15,
  the pull-loop continue-guard, the kill switch, the send-keys grep-guard, the
  echo/flood guard).
- Mutation-test each: inject its own named defect; it MUST fire; else it is
  theatre and is rebuilt. (The C.7 #6 kill-switch test — flag off -> next
  boundary refuses — is the first entry.)
- Apply the three killer patterns (tautology / fail-open / fail-silent) to each.
  Publish a harness kill-list beside the compliance one.

## ATOM 3 — Name the EXTERNAL-TRUTH WALL (constitutional)
**Problem:** all five themes are one failure at different altitudes — *a
component's self-report was trusted over an external check*. The stack has been
rediscovering this principle one incident at a time and applying it one instance
at a time. It lives today as five separate rules (R1, R9, R15, the epistemic
wall, the naive organ) with nothing holding them as ONE wall — which is exactly
why each theme had to be relearned.
**Requirements:**
- Add to CLAUDE.md as a **WALL, not a dial**:
  *No component's self-report counts as evidence of its own success. Every
  success claim — a turn ran, a check passed, an alarm can fire, a rule is
  enforced, work advanced — must be verifiable by a signal the component cannot
  generate itself (git commits, level transitions, mutation tests,
  independent-clock alarms, consumer re-fetch). A self-certified success is a
  theatre control by construction.*
- Cross-reference R1 / R9 / R15 / epistemic-wall / naive-organ AS FACETS of this
  one wall, so the principle is found by the next incident rather than joining
  the pattern.
- Add trigger #9 to the naive organ: **a success claimed without an external
  signal** -> question it.

## DoD
Failure register live and appended by the retro ritual, with global per-class
strike counts surfaced on the Method door; harness controls mutation-tested with
a published harness kill-list; External-Truth Wall in CLAUDE.md with its
cross-references and naive-organ trigger #9. All three drawn in dial order — the
transport migration and the director's flag-flip come first.
