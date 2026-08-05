# [DIRECTOR-PROGRAMME] — Architected out, organic in (2026-08-05)

**Type:** Programme statement. Director-commissioned, director-ratified 2026-08-05. Problems and outcomes; mechanisms are the worker's to design.

## 0. The problem, in the director's words

The process in is organic and stays organic — that is by design. The product out must be architected: slick code, clean structure, simple to describe, demo and test. Today the gap between the two is real and evidenced, not imagined: duplicate mechanisms built independently (two DD mandate registers, one with zero callers), built-and-unwired modules discovered by collision (back-billing), parameters no caller ever supplied, one convention change breaking three parsers, four named orphan-transition instances, and harness effort running 5x estimate (9.2h est / 45.7h actual). The cause is named precisely: **write-time blindness** — each turn's cheapest move is to write fresh, because discovering what exists costs more than creating it. This programme changes that economics.

## 1. Programme shape: MAP -> NET -> KNIFE -> RHYTHM

Strictly in this order. Each step is the safety condition for the next.

**MAP — the reuse surface (first, lowest risk).**
Deliver the capability index (per `ADVISOR_PROPOSAL_CAPABILITY_INDEX_AND_DEMO_2026-08-04.md`): one derived row per capability — plain words, status, evidence, empty rows visible. Its second job is the point here: **the builder consults it before minting anything new.** Write-time gate: before a new module/function, check the index; extend an existing mechanism or record in the commit why not. The rule is *know, then choose* — forced reuse that couples two purposes is the mirror error of duplication and is equally a defect. This extends `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` from primitives to all capability.

**NET — the join tier (second, before any knife).**
Build the five system tests from `ADVISOR_FINDINGS_MISSING_TEST_TIER_2026-08-04.md` (work loop, physical chain, money chain, market chain, customer lifecycle). Rationale: every serious failure to date has been parts-pass-system-fails; those are also exactly the failures refactoring causes. No structural refactor lands before the joins it crosses are watched.

**KNIFE — hotspot consolidation (third, never uniform).**
Targets are already named by the July dependency analysis, not to be re-derived: the reporting module (~9k lines, mutual-import cycle with the main run), the customer module straddling the wall, the 100+ SIM->company crossings bypassing the empty seam, and the zero-import company modules (~320) which are candidates for wiring or retirement — archive, never delete. Each move: behaviour-preserving, test-protected, one hotspot per pass. The Epoch-3 adapter programme is the boundary half of this knife and is not duplicated here.

**RHYTHM — consolidation as a standing duty (permanent).**
Canon already prunes the harness and advisor memory at epoch boundaries. Extend the same duty to code: every epoch close includes a consolidation pass — duplicates found, orphans wired or retired, the target-design document (below) updated. Organic growth between boundaries; deliberate pruning at them.

## 2. The target-design document

"Drawing the map of A to B is easier once you got there." The worker maintains `docs/design/TARGET_DESIGN.md`: the architecture we would build today knowing what we now know. It is a **direction, not a rewrite mandate** — the codebase encodes hundreds of fixed defects each protected by a test; a rewrite discards exactly that value. Every KNIFE pass and every RHYTHM pass moves the code one step toward the target or amends the target with reasons. Delta between target and actual is reported, not hidden.

## 3. The board, made scalable

Constraint (director): the blind board has run only a few times because every run is manual cut-and-paste. That does not scale. Ratified shape:

- **a. Batteries become executable.** The disqualification batteries already purchased (Specs 001-006 + the five 2026-08-04 scope briefs) are prose. Convert each testable line into a standing check that runs with the suite; lines that cannot be mechanised are listed as such, not dropped. External judgement already paid for stops sitting inert.
- **b. Blind review by restricted context, not by relay.** The property that made the board work is *what the reviewer could not see*, not the human courier. New reviews: a fresh-context agent given **only** the plain-words capability description and the domain — never code, design docs, or prior findings — produces the practitioner battery. Blindness enforced by construction; the transcript of what the reviewer was shown is committed alongside the findings so the blindness is auditable.
- **c. Honest limit, stated.** Restricted context gives blindness, not independence — the reviewer is still the same model family. Genuinely external review (the director relaying to a different model or human) is reserved for the few highest-stakes verdicts per epoch, at the director's choosing. This is a narrowing of the manual channel to where it is irreplaceable, not its elimination.

The worker must reconcile 3b with `COLD_EYES_PROTOCOL.md` (in_progress/) — one mechanism, not two beside each other.

## 4. Decided vs open

**Decided (director, 2026-08-05):** the goal — organic in, architected out; the MAP->NET->KNIFE->RHYTHM sequence; the write-time gate; the target-design document; board shape 3a-c; the board scales by mechanism, manual relay reserved for the exceptional; archive-never-delete stands.
**Open to the worker:** all mechanisms — index derivation, join-test design, hotspot order within the named set, battery conversion, the COLD_EYES reconciliation.
**Reserved:** any change to epistemic-law enforcement or safety controls; REPO_PRIVATE untouched.

## 5. Risk and proportionality

**Blast radius:** MAP low (derived artefact, no behaviour change). NET medium — join tests may be brittle at first; a red join test blocks publish, so first landing is report-only, promoted to gating after a stable week. KNIFE high — hotspots include money paths; mitigations: sequence position (after NET), one hotspot per pass, behaviour-preserving moves only, byte-identical output checks where they exist (established pattern). RHYTHM low. **Proportionality:** programme-level, multi-epoch; MAP and NET are ordinary-turn work; each KNIFE pass is its own sized draw. Nothing here blocks current lanes; the write-time gate is the only immediate behaviour change.

— Director programme, ratified 2026-08-05. Advisor-staged on the director's explicit instruction.
