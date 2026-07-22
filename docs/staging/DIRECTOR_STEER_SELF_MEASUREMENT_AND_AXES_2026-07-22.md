# DIRECTOR STEER — Self-measurement, director axes, and the always-drawable lane (2026-07-22)

**Type:** [STEER] — establishes how the system measures its own performance and how the director's judgment enters it. **The intent below is fixed; the mechanism is explicitly yours to design.** The director, verbatim: *"make sure it has some say in how best to do this, as it sees more than you."* Where you see a better construction than anything specified here, propose it with reasoning and build that instead — the advisor's shapes are defaults, not walls.

## Context anchor (fresh-session safe)

The goal this serves, in the director's words: **stable, autonomous, continuous, parallel velocity.** The mechanical layer is now stable (scheduled worker, draw self-recovery, R16 commit-time level gate). The remaining failure class is authority/attention: work stalls when it exhausts granted authority or when finished work awaits a grant (last night: ~11h stranded in the cwd-fix worktree, deadman at 637 min). Two prior steers on resource sensing sit un-built in `in_progress/` (TOKEN_RESOURCE_DIMENSION, HEARTBEAT_TOKEN_BURN) — **fold them into this rather than leaving three competing measurement designs.**

## 1. The daily self-note (machine-computed, no director input)

Each morning, publish one short note to the site (and NTFY digest), computed from the ledger, alarms, and origin:

- **Verified autonomous hours** — hours with gate-verified, ledger-backed work landing on origin without director input in the prior hour. *Verified* means it passed the existing gates (level gate, epistemic verifier, tests) — raw commits do not count. The existing enforcement machinery IS the anti-gaming layer; do not build a parallel one.
- **Longest stall and its cause** — the biggest gap between verified work, classified honestly (mechanical / drained / authority-gated / stranded-awaiting-grant).
- **One proposed fix** — the morning retro names the worst number and proposes ONE class-level improvement (R10 discipline). Fixes within standing authority: just do them. Genuine walls: into the next batched [ACT].

Resource inputs (tokens/rate-limits/context-fill from the `rate_limits` sensor you step-zero-proved) belong in this same note as the input half — un-park those two steers into it, or state why a different shape is better.

## 2. HARD LAW — diagnostic, never a target

Inherited verbatim from the utilisation ruling and LAW A/R12: **no scorecard number may ever feed draw priority, reward, selection, scheduling, or any optimisation mechanically.** The note is read by reasoning entities (your morning retro, the director, the advisor) — never consumed by allocation machinery. Definitions of the metrics are ledger-governed: changing what a number means is a director-ratified act, not a quiet edit. Honest reds are credited in the retro format — a surfaced failure (C13 wind-chill class) is the culture; concealment is the perverse incentive underneath all others.

## 3. The always-drawable lane (the "something always progresses" guarantee)

Wire the forward-discovery register (F1 conversations, F2 plain-language, F3 volunteer mechanics, F4 international, F5 competitor field) as the **standing fallback lane**: when core work is drained or authority-gated, the draw falls through to DISCOVER work here instead of resting. Optional-class discipline applies (yields instantly to core; respects token headroom once the sensor exists). Rest becomes legitimate ONLY when core is gated AND the discovery backlog is genuinely empty — which should be rare by construction.

## 4. Director axes (the judgment only he can give)

Create a small versioned file (e.g. `docs/design/DIRECTOR_AXES.md` — name/shape yours) holding what the director currently cares about most, v1:

1. **Website** — usefulness to him as an operational window + simplicity/clarity as a marketing tool.
2. **Segmentation** — efficiency (value per segment) + sophistication (real coupled structure, discoverable through the wall).
3. **Believability** — weather, wholesale products and prices, premise demand shape: does it feel like the real UK market to a 20-year veteran.

Roadmap encoded in the file: once these stabilise → billing + CRM rotate in; then advice + product journeys.

**The verdict loop:** the director gives one-line scores (e.g. "site 2/5 — still can't follow the customer panel") on his cadence — weekly or at milestones, via console or NTFY. Each verdict is recorded as data. **Before each expected verdict, the twin pre-scores the same axes and logs its prediction.** The director's verdict then scores the twin's prediction — belief-vs-truth applied to the director himself. Over time the prediction gap shrinking = the system internalising his taste. The twin exists and has live-exercised; this is a natural extension of its §3a role, but the wiring is yours to design.

## 5. The advisor's column

Include in the daily note, computed from origin facts (not self-assessment): advisor false status calls (claims contradicted by origin), staged docs that required a clarification loop before being actionable, and stalls attributable to an empty pre-staged queue. The director scores the advisor; the machine just computes the evidence.

## Your say — explicitly invited

Propose back, in your first pass: (a) anything above that is the wrong shape given what you can see from inside (existing organs to reuse, simpler constructions, things that will thrash); (b) any metric you believe will mislead or invite gaming despite §2, with the failure mode named; (c) what YOU would measure that the advisor and director have not thought of. The intent is the wall: self-measuring, drives the four goals, director judgment enters only where only he can judge, Goodhart-proof by severed wiring. Everything else is negotiable with reasoning.

**Risk & proportionality:** the note and axes file are additive (own commits, reversible). The always-drawable wiring touches the draw — sequence it, R15-prove core work always preempts discovery, own commit. Nothing here weakens a gate. Tag: **narrow/reversible for the note + axes; contract-touching for the draw wiring — implement with named mitigations.** Report the first daily note and your propose-back within the first pass.

— Advisor, carrying the director's steer, 2026-07-22.
