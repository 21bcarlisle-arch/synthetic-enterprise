<!-- SUPERVISOR_DRAW: blocked -->
<!-- REGISTRATION ONLY. This document mints nothing, opens no front, and does not grant a turn.
     It amends the HELD docs/staging/in_progress/PARALLEL_RUNG_HARNESS_PRUNING_EVALUATION.md.
     It is explicitly SUBORDINATE to DIRECTOR_RULING_HARNESS_INVESTMENT_AND_ITS_EVIDENCE_2026-07-27:
     harness investment terminates on evidence. If actioning this would compete with content work
     or pre-empt the pending exit criterion, it waits. -->

# [ADVISOR-ADDENDUM] — The harness-pruning trigger has fired. Registration only; nothing to action now. (2026-07-28)

**Type:** [ADVISOR-ADDENDUM] via advisor bridge. Amends a held doc; does not replace it.

## 0. Why this is an addendum and not a programme

A canon-first check before staging found the shape already exists and is director-decided. `PARALLEL_RUNG_HARNESS_PRUNING_EVALUATION.md` (staged 2026-07-17, **HELD — DO NOT ACTION DURING OPS1**) already carries the ADOPT/ADAPT/REJECT standard, the ritual trigger ("re-check first-party practice at every epoch boundary / major release"), the governance-layer exclusion, and the verdict honesty bar ("argue each REJECT against the first-party baseline, not alongside it; every adoption deletes the bespoke path it replaces").

The advisor's initial framing duplicated that. It has been withdrawn. This document does exactly three things:

1. Records that the trigger fired, with the dated inventory, so the fact is not lost.
2. Adds items the 2026-07-17 list **predates**.
3. Separates the one item that does not belong in the harness lane at all.

**Recording is not actioning.** The hold stands.

## 1. The trigger (fact, recorded)

An Anthropic product release dated on or before 2026-07-28 announced: an **in-app browser** in the desktop app (sandboxed, configurable session persistence); **Claude Code artifacts** (session-built interactive pages, publishable, able to call MCP connectors); **iOS simulator support**; a **Linux desktop app** (Ubuntu/Debian) with parallel sessions under Git isolation, CI monitoring with auto-fix/auto-merge, inline diff review, sharing the CLI's `CLAUDE.md`/MCP/skills config; plus guidance on **model and effort-level selection** and on the **seven steering surfaces** (`CLAUDE.md`, rules, skills, subagents, hooks and others).

**Provenance caveat (R9):** the above is marketing copy relayed by the director, not documentation and not observed behaviour. Nothing in it is a fact about this machine until step-zero verifies it, as was done once before for the statusline `rate_limits` payload.

## 2. Additions to the held list (items 1–5 of the 07-17 doc stand unchanged)

- **6. Effort levels ↔ our resource-class scheduling.** A dial the 07-17 list predates. Candidate consumer already exists and is inert: `executor_governor.py::max_tokens_per_window`, alongside `RESOURCE_AWARE_SCHEDULING_PROPOSAL`'s ≤1-heavy/N-light class model and `G5_effort_sizing_discipline`. R12 applies: a dial, never a target.
- **7. Skills ↔ `CLAUDE.md` bulk.** No `.claude/skills/` appears in canon. Every fresh seat pays for all of `CLAUDE.md`; a skill loads on demand. Steering *and* token-economy question, not either alone.
- **8. Native Git-isolated parallel sessions ↔ our fork machinery.** Items 1 and 3 of the held list now have a concrete first-party form. Relevant bespoke surface: `tree_lock`, merge-or-reap, the fork-lifecycle reconciler, the reap-guard — machinery whose cost is on record (33 salvage-tagged stranded branches; three live forks destroyed before the reap-guard landed). Likely ADAPT, not ADOPT: the governance layer above it is excluded by the 07-17 doc and stays.

## 3. The one item that is not harness pruning

**The in-app browser closes a documented verification ceiling, not a bespoke-vs-first-party question.** There is nothing to prune; nothing bespoke would be deleted. It belongs wherever SITE/R11 work lives, and its justification is independent of the parallel rung.

Evidence already in canon: phase entries repeatedly state *"no browser is available in this execution environment"* and name that honestly as the verification ceiling rather than claiming a pixel check. Every render-harness proof (`test_home_door.py`, `test_proof_door.py`, `test_world_door.py`, `test_company_door.py`) executes the page's real inline JS **in Node against published JSON** — genuinely load-bearing and R15-mutation-proven, but not pixels. And the axis-1 front-door verdict **FAIL 1/5, "It still looks awful"** is a visual judgement no Node harness can produce or catch.

**Open, not decided — and the first step is a fact-check, not a build:** the browser ships in the *desktop app*; the seat is a WSL2 CLI on Skynet. Whether it is reachable at all from this seat, and at what cost, is unknown to the advisor. No plan should be written on the assumption that it is.

## 4. The director's three questions, answered as requirements

Transmitted as requirements, not mechanisms. Where a mechanism is named it is a candidate to beat.

**(a) Cadence.** Requirement: the trigger must be a **sensed fact from primary state**, never a calendar interval — a second scheduler outside the draw is a known failure class in both directions (HARDEN doorbell thrash; RC1 starvation), and ONE_FRAMEWORK holds the draw as sole arbiter. Candidate to beat: a seat-version delta, already read once at step-zero (2.1.215). Epoch boundaries remain the second trigger per the 07-17 doc.

**(b) Not breaking everything.** Requirements: **one item, one verdict, one level** — never a bundle; REJECT must remain a real outcome (precedent: HARNESS_BEST_PRACTICE item 3 rejected — *"no new setting needed beyond the already-shipped `fallbackModel`"*); pilot before adopt and adapt before take (precedent: `phase-close-evaluator` written against the studied pattern rather than taking the generic built-in, because the bar here is specific). **Non-negotiable:** harness changes carry the highest blast radius in the project because the thing being changed is the thing that would catch the breakage — the seam that let three site wedges through was exactly this shape. R15-failable **both ways** on any adopted mechanism, one change per draw, with a named revert.

**(c) Not forgetting.** Requirement: every studied item carries a **recorded verdict** — adopt / adapt / reject / hold-until-X — in a form something reconciles, and **both HOLDs and REJECTs carry a re-check condition**. This is the idle-hole class (#8, E2): a correct decision going stale with nothing watching the ground underneath it, fixed each time by a machine-readable field plus a reconciler. Two live instances: **ULTRACODE**, held for post-OPS1; and item 3's REJECT above, which was true against the harness as it then was and has no re-check attached.

**The split that reconciles (a) with (b):** studying is read-only and cheap; adopting is gated and expensive. They should run at different rates. Sensing and recording a verdict fits the forward-discovery register's existing shape (DISCOVER-only, optional, preemptible). Only the adopt half needs a gated turn.

## 5. Proposed adoption bar — argue back

**An item qualifies for adoption only if it closes a gap already logged as costing us something.** "It is new" does not qualify. The browser passes easily (a documented verification ceiling and a real failed director verdict). Effort levels pass on the standing token-headroom finding. Artifacts-for-the-site does **not** — the site is a published product under SITE_CONSTITUTION with render-not-author discipline, and an artifact channel would sit outside it. The one plausible artifacts fit is `A3_approval_interface` (director decision packs, registered and unbuilt).

**R12:** the number of practices adopted is a diagnostic, never a score, target or headline.

## RISK

- **What it touches:** nothing executable. Doc-only registration in `in_progress/`. No map edit, no front, no gate.
- **Blast radius — attention, not code.** The probable failure mode is that this reads as licence to reopen the H lane the day after a ruling that harness work must terminate on evidence, and the day of a ruling that the published gap registers are the backlog. Mitigated by the draw-blocked marker and the explicit subordination in the header. **If that marker is insufficient to keep it out of the draw, say so and move this to `fyi/`** — that is the correct outcome, not a defect in the finding.
- **Second failure mode:** the browser item is the most appealing thing here ("we could finally see the site"), which is exactly how a genuine content-blocking gap becomes a harness detour. Mitigation: it is scoped in §3 as a SITE/R11 capability question with a **fact-check as its first step**, not a build.
- **Third:** §2 item 8 could be read as authorising deletion of fork machinery. It is not. Any ADAPT verdict there is gated behind the parallel rung exactly as the 07-17 doc has it.
- **Proportionality:** reversible / narrow — registration only.

## WHAT THIS CREATES

Nothing drawable. Two facts on record (the trigger fired; its inventory) and three additions to a held list. The next action on any of it is the director's, or the parallel rung's — whichever comes first.
