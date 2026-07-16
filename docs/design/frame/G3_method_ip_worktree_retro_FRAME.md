# G3 — Method IP: the worktree retro, made into enforced mechanism (FRAME)

**Atom:** `G3_method_ip_worktree_retro` (lane `G_*` method/harness, epoch 2, L0→2, `dial 2`, `loop_stage: idle`)
**Stage:** FRAME (Lane-3 DISCOVER/FRAME, doc-only). **NO LEVEL MOVE** — L1+ requires BUILT harness code
(a real trigger + its test, a real template section + its check) and this atom is BUILD-gated by epoch
sequencing; a doc cannot move it off L0. Level recorded HELD via the atom_status inbox (F1 — this fork
does not edit `maturity_map.yaml`).
**Source:** `docs/staging/done/RETRO_WHY_WE_MISSED_IT.md` (director-requested "let's remember this
learning", 2026-07-13). The atom's map `simplifications` blob already carries the five findings + the
meta-finding as prose; this FRAME turns that prose into a **checkable BUILD bar** (MAKE_IT_STICK: a
finding recorded only as prose is a finding that will decay — every rule that HELD was a MECHANISM).
**Author:** H17 Lane-3 governed fork, 2026-07-16. No BUILD code; no map edit (F1).

---

## 1. The gap this atom owns (one sentence)

Five method findings + a meta-finding (director-authored IP, not housekeeping) currently live only as
**prose** — in `RETRO_WHY_WE_MISSED_IT.md` and the atom's map `simplifications` — and by this project's own
decay law (MAKE_IT_STICK: "convert policy to mechanism, or accept it will evaporate") prose-only rules
evaporate; G3 owns turning the two findings that CAN be mechanised (F1, F2) into enforced harness code +
its own mutation-proving test, and durably publishing all six as casebook IP on the live Method door, so
the learning is retained as mechanism rather than re-lost the next time the same wall appears.

## 2. Why it is distinct from its neighbours (no overlap)

- **Not `incident-retro` skill / `docs/retrospectives/`.** Those PRODUCE retros (the R-rule format).
  G3 is downstream: it takes an already-written retro's findings and makes the *mechanisable* ones fire
  automatically. The skill writes the lesson; G3 wires the lesson so it cannot be forgotten.
- **Not `H18_harness_self_mutation_audit`.** H18 audits whether the harness's *existing* controls can
  fail (R15 mutation coverage of controls already built). G3 ADDS two new controls (the F1 wall-trigger,
  the F2 review-template section) — H18 would later be one consumer that checks G3's new controls can fire,
  but G3 owns their construction.
- **Not `G4_unified_failure_register`.** G4 unifies where failures are *recorded*. G3 is about method
  *learning retention* — a different register (the casebook/Method door), a different failure mode
  (institutional forgetting of a structural lesson, not an un-tracked defect).
- **Not the site Method door itself.** `site/method/` + `site/method-casebook/` are the *surface*; G3
  owns the F1/F2 mechanisms and the casebook *content* (the six findings as durable IP entries), which
  that surface renders.

## 3. The six findings, classified by mechanisability (the honest split)

Only two of the six are *mechanisable* — the rest are judgement laws that a mechanism cannot enforce
without becoming theatre (R15's own warning: a control that cannot genuinely fail is worse than none).
Stating this split IS the FRAME's main value — it prevents a BUILD that fakes enforcement of an
unenforceable law.

| # | Finding (law) | Mechanisable? | G3's BUILD obligation |
|---|---|---|---|
| **F1** | Hit a structural wall → check published practice BEFORE theorising | **YES** | A real trigger + a test it fires (§4) |
| **F2** | A review only answers the question it asked → add "what was out of scope, and why?" to every review artefact | **YES** | A required template section + a completeness check it fails when the section is absent (§4) |
| **F3** | First-principles reasoning about a fast field is a hypothesis, not evidence (R9, advisor edition) | **NO — judgement** | Casebook entry only; cross-link R9. A "detect over-confident derivation" checker would be theatre. |
| **F4** | Bottlenecks are onions; the last layer is invisible until it is last | **NO — judgement** | Casebook entry only. |
| **F5** | The architecture work and the velocity-work are the same work | **PARTIAL** | Casebook entry + a soft prompt at epoch-boundary review: "is any deferred-as-architecture item also capping throughput?" (a review-template line under F2, not a hard gate). |
| **META** | The outside (director's naive) question is the highest-value input; protect it | **NO — cultural** | Casebook entry only; the meta-finding is a standing value, not a check. |

**Anti-theatre binding (R15):** BUILD may only claim L-promotion for the two GENUINELY mechanised
findings (F1, F2). The four judgement findings are DONE when durably published as casebook IP — they must
NOT acquire a fake "enforcement" control to inflate the mechanised count. A judgement law dressed as a
passing check is exactly the FAIL-SILENT / TAUTOLOGY pattern R15 forbids.

## 4. Proposed shape (what BUILD would build — not built here)

**F1 — the structural-wall → published-practice trigger.**
- A structural wall is an *observable harness state*, not a vibe: candidate signals already emitted to
  disk — a `_self_refill_draw()` returning empty/`map_exhausted`, a livelock/idle-turn counter tripping,
  a repeated same-atom re-hand (the H23 occurrence counter), a `two-strike redesign` (R3) firing. BUILD
  picks the smallest reliable observable (proposed: an idle/empty-feasible-set OR an R3 second-false-claim)
  and, on that transition, emits a **"SEARCH THE FIELD"** obligation (a queued finding / NTFY-eligible
  marker) BEFORE the turn is allowed to theorise a bespoke fix.
- **The point is ordering, not the search itself** (the machine has no network in autonomous runs — a
  real published-practice check is a director/interactive-session or discovery-agent action): the
  mechanism's job is to make "did we check whether this is a solved problem?" a *forced, logged step* at
  the moment of a wall, not an optional afterthought that the epoch-boundary re-check reaches too late.

**F2 — the review-artefact "out-of-scope" section.**
- Extend the review-artefact template (the `cold-eyes-walk` / phase-close review output, and any
  `*_REVIEW*.md`) with a REQUIRED `## What this review did NOT ask (and why)` section.
- A completeness check (grep-level, in the phase-close gate) that FAILS a review artefact lacking that
  section — turning F2 from a hope into a gate.

**Invariants (R15 — mutation-testable; FAIL-OPEN / FAIL-SILENT / TAUTOLOGY forbidden):**
- **G3-A1 (F1 fires):** plant a synthetic structural-wall state (empty feasible set) → the trigger MUST
  emit its obligation. Mutation: disable the emit → the test goes red. **FAIL-SILENT guard:** if the
  wall-signal source is unavailable, that is a FAILED check (obligation emitted conservatively), never a
  silent pass.
- **G3-A2 (F1 orders correctly):** the obligation is emitted BEFORE the bespoke-fix path, not after —
  a mutation that reorders (theorise-then-check) must fire the test.
- **G3-A3 (F2 fails-closed):** a review artefact missing the out-of-scope section MUST fail the
  completeness check. Mutation: feed a review with the section deleted → red. **FAIL-OPEN guard:** an
  empty or whitespace-only section counts as MISSING (not present-and-blank passing).
- **G3-A4 (no fake enforcement of judgement findings):** a test asserting F3/F4/META have *no* automated
  gate — a mutation that adds a theatre "confidence detector" and claims it enforces F3 must be caught as
  a regression (the anti-theatre binding, §3, made executable).

## 5. Scale / portability constraints touched (declare, don't retrofit)

- **C-S2 determinism:** the F1 trigger is a pure function of observable harness state → identical wall
  state emits an identical obligation on replay. No RNG.
- **Portability:** F2's out-of-scope section is a review-artefact convention, market/product-agnostic —
  it fits any review the harness produces. F1's wall-signals are named harness observables, not
  domain-coupled.
- **No new architecture (SIMPLICITY GUARD):** both mechanisms are the *simplest construct* — a
  transition-emit and a grep-level template check wired into the EXISTING phase-close gate and
  `supervisor.py` draw path; no new subsystem, no register cathedral.

## 6. The R13 wall — N/A (declared, not skipped)

G3 is a **HARNESS/method** atom, not a world/SIM or company atom: it touches neither the BASELINE world
nor the CURRICULUM, so R13's baseline/curriculum wall does not bind here. Stated explicitly so a BUILD
turn does not go looking for a wall that isn't there (an absent-wall left unstated reads as an oversight).

## 7. Coupled-triad note (A6)

G3 is not a SIM↔company coupled pair (it is pure harness/method IP, both sides internal to the builder).
Its nearest analogue to "the gap is the score": the **belief-vs-outcome gap for a method finding** — a law
recorded but not mechanised is *believed* retained while *actually* decaying; the F1/F2 mechanisms +
their mutation tests ARE the gap-closing evidence (the finding is retained iff the test still fires).
No coupling registered (BUILD-gated); no `coupled_triad.py` edit.

## 8. BUILD-unblock gate (single line)

Epoch-2 BUILD-open for this atom. Until then: **held at L0**, DISCOVER/FRAME complete. First BUILD step is
choosing F1's concrete wall-signal observable (§4) from the ones the harness already emits — a design
choice, not new instrumentation.

## 9. Ordered BUILD task list (for the eventual BUILD turn — not started)

1. Pick F1's wall-signal observable from existing emitted state (empty-feasible-set / R3-second-strike /
   H23 re-hand counter); wire a transition-emit of the "SEARCH THE FIELD" obligation BEFORE the bespoke-fix
   path in the relevant draw/turn path.
2. Mutation tests G3-A1, G3-A2 (red-then-green): disable the emit; reorder to theorise-first — each fires.
3. Add the REQUIRED `## What this review did NOT ask (and why)` section to the review-artefact template
   (cold-eyes-walk / phase-close review output).
4. Add the F2 completeness check to the phase-close gate; mutation tests G3-A3 (missing section → red;
   blank section → red).
5. Add G3-A4: assert F3/F4/META carry NO automated gate (anti-theatre binding executable).
6. Publish all six findings as durable casebook IP entries on the live Method door (`site/method-casebook/`);
   verify per R11 by fetching the rendered value on the deployed surface.
7. Record L1→L2 evidence: F1 test fires, F2 gate fails a section-less artefact, casebook entries render live.

**Proposed file_scope for BUILD:** `[background/supervisor.py (F1 emit only), .claude/skills/phase-close/*,
.claude/skills/cold-eyes-walk/*, site/method-casebook/*, tests/background/, tests/site/]` — disjoint from
the world/company lanes; touches only harness/method surfaces.
