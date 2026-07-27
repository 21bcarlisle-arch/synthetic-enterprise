<!-- SUPERVISOR_DRAW: blocked -->
<!-- DISPOSITION 2026-07-27 (RUNG-7 planner): this ruling's three laws + the R10 sweep are DECOMPOSED
     into four drawable RUNG-1 mints in docs/staging/ (the drawable work lives THERE, this doc is the
     authority they reference):
       - PLANNER_MINTED_failure_bias_law_a_suppression_rearm_2026-07-27.md   (LAW A)
       - PLANNER_MINTED_failure_bias_law_b_lane_isolation_2026-07-27.md      (LAW B)
       - PLANNER_MINTED_failure_bias_law_c_independent_verification_2026-07-27.md (LAW C)
       - PLANNER_MINTED_failure_bias_r10_suppression_sweep_2026-07-27.md     (R10 sweep, drawable now)
     Moved to in_progress/ (open sub-items = the mechanisation, not yet built). blocked_on: the four
     mints drawing + landing with R15 both-ways. Ruling itself is NOT independently drawable. -->

# [DIRECTOR-RULING] — Three failure-bias laws, and the suppression audit. Why one held assumption stopped everything. (2026-07-27)

**Type:** [DIRECTOR-RULING] via advisor bridge. The director's challenge, verbatim: *"I don't get why one assumption caused the whole process to fail. If the assumption can be improved of course do it. But don't ignore why stuff went wrong when it shouldn't."* He is right: the λ contradiction was the trigger, not the disease. This ruling addresses the disease.

## The diagnosis: five defences failed in the same direction

A single director-held decision (population λ vs N) stopped work that had nothing to do with it — the site campaign, the merit-order build, premise-demand publish, the DD cash-flow FRAME. Five independent mechanisms each failed, all toward quiet:

1. **Rule-0 fallback** drew HARDEN, then exhausted the HARDEN targets and had nowhere else to go.
2. **The pending-batch gate** blocked minting **globally** when the pending batch was all-blocked, instead of per-lane.
3. **The enumeration** published *"whole authorized set empty"* while open mints existed in `in_progress/`.
4. **The watchdog's STALL page** was suppressed by the tick's own declaration of legitimate rest — the watched component silencing its own supervisor.
5. **The daily note** reported the law's *status* ("always-drawable lane WIRED") rather than its *effect*, over a window containing eighteen dead hours.

**The common cause, stated plainly:** every one of those five mechanisms was introduced to suppress a false positive. The pending-batch gate stopped mint-spam. The rest-legitimacy suppression stopped false STALL alarms — **the advisor requested that one on 2026-07-22.** Each was individually defensible. The accumulated bias is a system whose default response to confusion is silence. A week of optimising against noise made quiet the failure mode.

## The three laws (harness-level; mechanise with R15)

**LAW A — Failure modes bias to noise, never to silence.** Every suppression, throttle, fold or gate is **time-bounded and re-arms**, regardless of any self-declaration. No component may indefinitely silence an independent check. A false page costs a glance; a silent stall cost a weekend.

**LAW B — Lane isolation.** A block in one lane may never suppress drawing or minting in another. Gates are **per-cluster, never global**. A director-held population decision must leave site, price-engine, billing and discovery lanes fully drawable. R15: hold one lane artificially, prove every other lane still draws.

**LAW C — Independent verification.** The watchdog and the daily note derive their verdict from **primary state** — the actual contents of `in_progress/`, the campaign registers, the defect ledger, the maturity map — never from the tick's published enumeration. Two sources that can disagree, so that a false claim in one is visible from the other. R15: falsify the enumeration in a test and prove the watchdog still pages.

## The R10 sweep (do this, not just the three laws)

**Audit every gate, throttle, suppression and fold introduced in the last fourteen days and classify each by failure direction: noisy or silent.** Publish the table. Anything that fails toward quiet gets either a time-bound (Law A) or an independent counterpart (Law C). Report the list with its verdicts — this is the class fix; the three laws alone are exhortation without it.

## Standing consequence

From now on, when a false positive is suppressed, the fix must state **what will still page if the underlying condition is real.** A suppression proposed without that answer is rejected.

**Risk & proportionality:** touches watchdog, gate and reporting logic — failing tests first, own commits, shadow rails on scanner changes. Tag: **priority after the current MC-2 draw completes; sweep is analysis and proceeds in parallel.**

— Advisor bridge, carrying the director's challenge — and recording that the 2026-07-22 suppression the advisor requested is one of the five failures named above. 2026-07-27.
