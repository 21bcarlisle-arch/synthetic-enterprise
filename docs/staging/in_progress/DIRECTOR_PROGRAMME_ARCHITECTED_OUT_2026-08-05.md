<!-- SUPERVISOR_DRAW: available -->
> **[IN-PROGRESS — 2026-08-08 worker tick] ABSORBED INTO THE MAP. §4 DEFECT: this programme arrived
> with NO "WORK THIS CREATES" block** — verified, not assumed: `supervisor.work_this_creates_deliverables()`
> returns `[]` for this file. That is why it sat **three days CONSUMED but not ABSORBED** (staged and read,
> but no atom, therefore not drawable) — the exact R17 failure the programme itself is about.
>
> **Done this tick — 9 atoms minted into `docs/design/maturity_map.yaml`** (203 atoms total, no id
> collisions, every `depends_on` resolves):
>
> | Atom | Programme step | Drawable now? |
> |---|---|---|
> | `AO1_capability_index` | MAP — the reuse surface | **YES** |
> | `AO2_write_time_reuse_gate` | MAP — the write-time gate (index + ecosystem, 3 part classes) | after AO1 L1 |
> | `AO3_join_test_tier` | NET — the five system tests | after AO1 L1 |
> | `AO4_scale_constraints_executable` | NET — C-S1..C-S5 made executable | after AO3 |
> | `AO5_hotspot_consolidation` | KNIFE — the four named hotspots | after NET |
> | `AO6_consolidation_rhythm` | RHYTHM — consolidation as epoch duty | after AO1+AO7 |
> | `AO7_target_design_doc` | §2 — `docs/design/TARGET_DESIGN.md` | after AO1 L1 |
> | `AO8_board_batteries_executable` | §3a — batteries become checks | **YES** (independent) |
> | `AO9_blind_review_by_restricted_context` | §3b/3c — blindness by construction | after AO1 L1 |
>
> **The ruled order is MECHANISED, not exhorted.** MAP→NET→KNIFE→RHYTHM is carried by `depends_on`, so
> the draw *cannot* take a KNIFE pass before the NET that protects it. Proven against the live
> `supervisor._dependencies_met` gate rather than asserted: with nothing built, only AO1 and AO8 are
> drawable and AO5 is blocked; simulating AO1→L1 opens AO2/AO3/AO7/AO9 and AO5 **stays blocked**.
> Titles + gain statements follow the plain-words naming law (`DIRECTOR_RULING_H_LANE_CUT_AND_PLAIN_NAMING_2026-08-05`
> Ruling 2). Retrofitting titles to the other 194 atoms is that ruling's own work, not this one's.
>
> **OPEN SUB-ITEMS (this file stays here until they close):**
> 1. ~~**Nothing is BUILT yet**~~ — **AO1 (MAP step 1) is BUILT, L0→L2, 2026-08-08** (`7e5a727d4`,
>    `tools/capability_index.py`, 24 tests, five R15 source mutations each firing its own guard;
>    837 rows, 268 orphans of which 260 in `company/`). Addendum A1 is answered by construction —
>    the index never reads `maturity_map.yaml`, so no field sweep touched the draw. **Open draws now:
>    AO8** (still untouched, independent) **and AO2/AO3/AO7/AO9**, which AO1 unblocks. The index is a
>    demo until AO2 spends it — the director's own framing, so AO2 is the next MAP draw, not a later one.
>
>    **[2026-08-08, later ticks] AO8 and AO7 are now BUILT too.** AO8 L0→L2 (`008df0306`): 76 battery
>    lines registered, 3 running; the mutation pass caught one check that could not fail. AO7 L0→L2
>    (§2, this tick): `docs/design/TARGET_DESIGN.md` + `tools/target_design_delta.py` + 36 tests —
>    7 targets, each with a probe, **1 met**. The anti-wish-list property is structural, not
>    exhortative: a target naming an unimplemented probe is rc 2, so aspirational prose cannot be
>    written into the document. Per §2 the delta is REPORTED and does not gate (R12) — the gate is
>    on measurability. Its mutation pass also caught two guards that could not fail, both now closed.
>    **MAP is COMPLETE — verified against the live map, not from this file's own history.** AO2 (the
>    write-time reuse gate) is L2 and RUNNING: it refused this very commit for a missing REUSE record
>    on `tools/target_design_delta.py`, which is the index being *spent* rather than demoed, and is
>    the strongest evidence available that the gate is real. AO9 and AO11 are L2 as well. An earlier
>    draft of this note called AO2 and AO9 unbuilt; that was read from this document's own stale
>    prose instead of `maturity_map.yaml`, and the gate firing is what caught it — the same
>    consumed-not-absorbed error §4 is about, committed inside the note recording it.
>    **Remaining unbuilt: AO3/AO4** (NET — now the next draws), **AO5** (KNIFE, still correctly
>    blocked behind NET), **AO6** (RHYTHM, which AO7 now unblocks and which is what keeps the target
>    document current), **AO10**.
> 2. **The author's own WORK THIS CREATES block is still owed** (same ask as the three rulings in
>    `WORKER_MINTED_THREE_RULINGS_WORK_BLOCK_DEFECT_2026-08-08.md`). **UNBLOCKS ON:** the block arriving —
>    then diff it against the nine atoms above; anything in the author's block and absent here is a gap
>    in the worker's reading, not a change of scope.
> 3. **`AO9` must RECONCILE with `COLD_EYES_PROTOCOL.md`** (in_progress/) — the director required ONE
>    mechanism, so shipping it beside the existing cold-eyes skill fails the atom.
>
> Moved out of the staging root so the scanner reflects **minted + drawable** rather than "unprocessed".
> Not silently absorbed, and not written back into this file as if the author had enumerated it.

# [DIRECTOR-PROGRAMME] — Architected out, organic in (2026-08-05)

**Type:** Programme statement. Director-commissioned, director-ratified 2026-08-05. Amended same day (director): build-vs-buy added to the write-time gate; standing production-readiness constraints added to NET as executable checks. Problems and outcomes; mechanisms are the worker's to design.

## 0. The problem, in the director's words

The process in is organic and stays organic — that is by design. The product out must be architected: slick code, clean structure, simple to describe, demo and test. Today the gap between the two is real and evidenced, not imagined: duplicate mechanisms built independently (two DD mandate registers, one with zero callers), built-and-unwired modules discovered by collision (back-billing), parameters no caller ever supplied, one convention change breaking three parsers, four named orphan-transition instances, and harness effort running 5x estimate (9.2h est / 45.7h actual). The cause is named precisely: **write-time blindness** — each turn's cheapest move is to write fresh, because discovering what exists costs more than creating it. This programme changes that economics.

## 1. Programme shape: MAP -> NET -> KNIFE -> RHYTHM

Strictly in this order. Each step is the safety condition for the next.

**MAP — the reuse surface (first, lowest risk).**
Deliver the capability index (per `ADVISOR_PROPOSAL_CAPABILITY_INDEX_AND_DEMO_2026-08-04.md`): one derived row per capability — plain words, status, evidence, empty rows visible. Its second job is the point here: **the builder consults it before minting anything new.** Write-time gate: before a new module/function, check the index; extend an existing mechanism or record in the commit why not. The rule is *know, then choose* — forced reuse that couples two purposes is the mirror error of duplication and is equally a defect. This extends `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` from primitives to all capability.

The gate asks two questions, not one: *do we already have this?* (the index) and *does the ecosystem already have this?* Three part classes govern the second: **catalogue parts** — calendars, timezones, money arithmetic, statistical fitting, solvers — are always taken from mature libraries, never hand-rolled (evidence class: the from-scratch working-day calculator of 2026-08-03 built while `holidays`/`workalendar` exist, and the BST/UTC settlement block the same day); **custom tooling** — GB market mechanics, licence conditions, behavioural archetypes, the wall, the harness — is always built, because it is the product; **subsystems** (dispatch, ledgers and similar) may be built custom, but only with a recorded build-vs-buy note naming the library evaluated and the reasons rejected — silence is a gap. Recreating the physics of the GB market is the job; recreating the mathematics underneath it is waste. Dependency discipline still applies: deterministic decade replays mean every new library is pinned and its determinism stated.

**NET — the join tier (second, before any knife).**
Build the five system tests from `ADVISOR_FINDINGS_MISSING_TEST_TIER_2026-08-04.md` (work loop, physical chain, money chain, market chain, customer lifecycle). Rationale: every serious failure to date has been parts-pass-system-fails; those are also exactly the failures refactoring causes. No structural refactor lands before the joins it crosses are watched.

The net also makes canon's standing production-readiness constraints executable — event-arrival tolerance, idempotent/deterministic replay, asynchronous wall contracts, persistence behind the event-log interface, declared time-scale invariance (per `PRODUCTION_READINESS_SCALE_ADDENDUM.md`). These are currently aspirational, and there is measured drift: the billing ledger existing as two identical 2.3MB copies (FINDING 2, `ADVISOR_FINDINGS_STRUCTURAL_AUDIT_2026-08-04.md`) is the persistence constraint not holding. Each constraint gets a standing check, or is listed as not-mechanisable rather than dropped; same report-only-first, gate-after-a-stable-week promotion as the join tests.

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

**Decided (director, 2026-08-05):** the goal — organic in, architected out; the MAP->NET->KNIFE->RHYTHM sequence; the write-time gate; the target-design document; board shape 3a-c; the board scales by mechanism, manual relay reserved for the exceptional; archive-never-delete stands. Also decided (same-day amendment): the write-time gate asks both questions — index and ecosystem — under the three part classes above; canon's standing production-readiness constraints become executable checks in NET.
**Open to the worker:** all mechanisms — index derivation, join-test design, hotspot order within the named set, battery conversion, the COLD_EYES reconciliation.
**Reserved:** any change to epistemic-law enforcement or safety controls; REPO_PRIVATE untouched.

## 5. Risk and proportionality

**Blast radius:** MAP low (derived artefact, no behaviour change). NET medium — join tests may be brittle at first; a red join test blocks publish, so first landing is report-only, promoted to gating after a stable week. KNIFE high — hotspots include money paths; mitigations: sequence position (after NET), one hotspot per pass, behaviour-preserving moves only, byte-identical output checks where they exist (established pattern). RHYTHM low. **Proportionality:** programme-level, multi-epoch; MAP and NET are ordinary-turn work; each KNIFE pass is its own sized draw. Nothing here blocks current lanes; the write-time gate is the only immediate behaviour change.

— Director programme, ratified 2026-08-05; amended same day (build-vs-buy gate; executable constraints) on the director's instruction. Advisor-staged.
