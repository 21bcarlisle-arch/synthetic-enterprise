<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- BLOCK_RELEASE: propose_then_proceed -- was 'director_level_up', an act abolished 2026-07-29 and swept 2026-08-03: propose, record, act. Original note: shared-primitive ensuring-activity gate; level move director-reserved (R16) -->
<!-- DESIGN half CLOSED 2026-07-28: docs/design/SHARED_PRIMITIVE_ENSURING_ACTIVITY_DISCOVER.md (5.1 plugs in as register #9 of the GAP1 mint-source contract, ranked by GAP2 method not special-cased; 5.2 exact phase-close item 0d specified; 5.3/5.4 ride existing retro cadence + phase-close-evaluator; R15 fail-closed). BUILD half remains blocked_on director_build_open. -->
# [PLANNER-MINTED] — Shared-primitive ensuring activity: census-as-gap-register + phase-close question + standing structural review (2026-07-28)

**Source:** `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` §5 (5.1–5.4) + Acceptance
items 5 & 6 (committed `29361d1c2`). The ruling names §5 as **the real gap**: everything in §2–§4 is a
*gate* (fires on a diff, pass/fail); **no gate ever asks "should this have been shared?" or notices "this
is the 92nd register."** This atom builds the *ensuring activity* — the standing look at the codebase as a
whole that gates cannot provide.

**Provenance:** RUNG-7 planner mint — one of the six the §4-DEFECT ruling's body creates. Plugs into the
existing gaps-as-mint-sources mechanism (`PLANNER_MINTED_gap_registers_as_mint_sources_2026-07-28`,
`DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28`) rather than opening a competing campaign
(ruling §1). grep-confirmed net-new.

**Serves:** the incentive fix — the same context that wrote the 91 registers is least able to see them as a
problem, so drift must enter the backlog automatically and be reviewed by a fresh context.

**Fidelity gained (one sentence):** none directly — a **standing ensuring mechanism** so shared-primitive
drift enters the backlog the same way every other published gap does and is reviewed by a context with no
investment in defending the duplication.

---
## The three sub-mechanisms (all from §5)
- **5.1 Census → standing gap register.** Publish the census (clone count, register count, shared-primitive
  inventory, quantity-registry coverage) as a **gap register**, and enumerate it as a **planner mint
  source** under the 2026-07-28 gaps ruling. Rank drift by the GAP2 triage method — **do NOT special-case
  it** (ruling §1). This register also supplies the **223 clone ceiling** the size ratchet (§3 mint)
  consumes.
- **5.2 Phase-close question.** Add ONE line to the phase-close skill/checklist at the exact point where 91
  registers became 91: *"Does this capability already exist elsewhere — did I search before building?"*
- **5.3 Standing structural review** on the existing retro cadence (~50 phases / 2 weeks): re-run the
  census, report drift, give a verdict.
- **5.4 Route 5.3 through the fresh-context evaluator** already run at phase close (`phase-close-evaluator`)
  — the load-bearing part: a fresh context has no investment in defending the registers.

## Lane / level / deps
- **Lane:** `H_harness` + phase-close skill + planner mint-source wiring. The census-publish + phase-close
  question + review-scheduling are doc/harness edits; **5.1's gap-register publish is drawable NOW**
  (doc-only, plugs into the existing published-gaps mint mechanism). Wiring the review onto the retro
  cadence + fresh evaluator is a small harness build.
- **Target level:** `level_current 0 → 2` (ensuring/harness wiring), `blocked_on: director_level_up` (R16).
- **Deps:** soft — the census generator (AST clone detection) must be re-runnable; the ratchet (§3) and the
  quantity registry (§4) each surface a column the register reports (coverage), reconciled on landing.

## Exit criteria
- Census published as a gap register **and enumerated as a planner mint source** (Acceptance item 5).
- Phase-close question added (Acceptance item 6, part 1).
- Standing structural review **scheduled on the retro cadence and routed through the fresh-context
  evaluator** (Acceptance item 6, part 2).
- **R15 (where applicable):** the mint-source wiring reds if the census register is unreadable
  (fail-**closed** = treat as drawable/open, per the GAP1 reader-contract fail-safe), not fail-open-empty.

## Anti-Goodhart (ruling §7): the census numbers are reported facts, never scores; the review gives a
verdict, it does not minimise a metric.

## Walls untouched
- **No level self-bump (R16); no safety/auth/curriculum change.** Harness + checklist + mint-source wiring.

## Block requested from the ruling author
WORK-THIS-CREATES block requested via NTFY (bundled with the other five mints).
