# METHOD LENS AUDIT — mature delivery disciplines vs. this repo's own mechanisms

**Atom:** `G6_method_lens_audit` (maturity_map.yaml, epoch 2, L0→1, lane H_harness).
**Source brief:** `docs/staging/done/METHOD_AUDIT_AGAINST_DELIVERY_DISCIPLINES.md`
(director-raised, disposition QUEUE).
**Status:** DISCOVER pass, doc-only. Surfaced on the Method door
(`site/method-casebook/index.html`, section "Method Lens"), data wired through
`tools/generate_method_casebook_data.py`.

---

## 0. The diagnosis, restated once

Every best-practice review this project ran scoped itself to "best practice for
AI agent harnesses" — the TOOLING layer (worktrees, hooks, headless
orchestration, context management). Most of what actually bit us lives one
layer down, in the PROCESS layer — sizing, decomposition, WIP limits, flow,
estimate-vs-actual, readiness/done gates — which is decades old and
**independent of what does the work**. We kept re-deriving named disciplines by
injury instead of reading them. This is a deliberate pass the other direction:
map our hard-won mechanisms against the disciplines that already solved this
class of problem, so the remaining gaps are found **proactively**, not by the
next incident.

Two questions this audit must answer (per the brief):
1. Which of our "novel" findings are named patterns with known refinements —
   so we adopt the mature version, not our injured first draft?
2. What does mature delivery do that we haven't reached yet?

**Guardrails, both non-negotiable (restated from the brief, recorded once more
here because they gate every row below):**
- **Adopt the PRINCIPLE, reject the CEREMONY.** We are one director + AI
  executors, not many human teams coordinating across time zones. Every
  refinement below is filtered through "does this survive translation to a
  single-principal, AI-executor shop" — the ceremony built for human
  coordination overhead (stand-ups, sprint planning theatre,
  story-points-as-currency, formal SLA contracts between teams) is explicitly
  **rejected**, row by row, in §2.
- **Dial, not target (R12 anti-goal-seek, extended).** Every metric this audit
  proposes adopting — WIP count, cycle time, error budget, toil %,
  estimate-vs-actual — is a **diagnostic**, never a target or a completion
  gate. The moment a cycle-time number becomes "must ship in N", or a WIP limit
  becomes a thing to game rather than a signal to investigate, it reintroduces
  exactly the deadline pressure that manufactures self-certified false-L3s
  (the same failure mode R12 was written to stop, applied here to process
  metrics instead of margin).

---

## 1. The mapping table

Format per row: **our lesson/mechanism** → **established pattern it already is**
→ **the refinement we're missing** (or "none — already at parity", where true).

| # | Discipline | What we already have (this repo's real mechanism) | Established pattern name | Refinement we're missing |
|---|---|---|---|---|
| 1 | **Lean** (flow, waste, pull, build-measure-learn) | The atom loop itself — DISCOVER→FRAME→BUILD→HARDEN is a pull system (an atom is drawn when capacity exists, never pushed); `COMPOUNDING_WORK_FIRST.md`'s "shortens-the-feedback-loop work goes first" is Lean's waste-elimination instinct applied to sequencing. | Lean's **pull system** / **single-piece flow** / kaizen (build-measure-learn). | No named **waste taxonomy**. Lean's seven wastes (overproduction, waiting, transport, over-processing, inventory, motion, defects) would let us classify *why* an atom stalls instead of writing a fresh incident narrative each time (e.g. the CANNOT-draw incidents were textbook "waiting" waste; a stale re-run of an already-answered DISCOVER question is "over-processing"). No first-class **WIP inventory metric** — atoms sitting at `loop_stage: idle` vs. genuinely in-flight is knowable from the map today but isn't surfaced as a number anywhere. |
| 2 | **Kanban** (WIP limits, flow metrics, cycle time, classes of service) | The multi-atom concurrent draw (`supervisor.py::_maturity_map_draw_concurrent`, N atoms/cycle when `file_scope` is disjoint) caps *parallelism* by disjointness; `PER_ATOM_INTEGRATION_NOT_WAVES.md` (2026-07-16, the first concrete finding this lens itself predicted, before this doc was even written) is Kanban's founding insight verbatim — integrate at the smallest independently-verifiable unit, a slow atom blocks only itself, never the wave. | Kanban's **WIP limits**, **single-piece flow**, and **cumulative flow diagram**. | Three concrete gaps: (a) `THREE_LANES.md`'s "1–3 concurrent on disjoint file_scopes" is a *rule*, not a **measured WIP limit** tied to observed cycle-time data — Kanban tunes the number from the cumulative flow diagram, we picked it once and haven't revisited it against actuals; (b) no per-atom **cycle-time / age-in-stage** metric surfaced (we *have* the raw material — G5's `tools/effort_calibration.py` already mines git-timestamped level transitions — but nothing turns that into a live "how long has this atom sat at `loop_stage: X`" figure on the Method door); (c) no named **classes of service** — one-way-door escalations, P-2's director-repeat auto-escalation, and Rule-0's dial-yielding are all de-facto "expedite" lanes today but none is tracked as a distinct class with its own (diagnostic, not target) SLA. |
| 3 | **Theory of Constraints** (Five Focusing Steps: identify/exploit/subordinate/elevate/repeat) | "Bottlenecks are onions" — the real CANNOT-draw incident (2026-07-12) traced through a stale-process constraint (R2) to a genuine gating-logic constraint (`D2_three_clocks`); Rule 0's dial-yielding ("automatically yield dials in reverse priority order until work exists") is literally **subordinate everything to the constraint** applied to the whole harness. | Theory of Constraints' **Five Focusing Steps** + Drum-Buffer-Rope pacing. | We do steps 1 (identify) and 3 (subordinate) *reactively*, per-incident. There is no **standing** mechanism that continuously re-asks "what is the current constraint" the way a ToC practice would — no periodic query over per-lane cycle-time data that names *this week's* bottleneck before it causes a stall. There is also no **elevate → repeat** ritual: once a constraint breaks (H9's map-write serialisation removed the map-contention bottleneck), nothing formally re-asks "what's the *next* constraint now that this one is gone" — it's discovered by the next incident rather than by design. |
| 4 | **SRE / incident practice** (blameless postmortems, error budgets, toil reduction) | `G4_unified_failure_register` (cross-retro, GLOBAL per-class strike-counting) *is* SRE's blameless-postmortem-plus-repeat-cause-register, independently re-derived; R3 ("a second false claim on the same component means redesign, not patch") is SRE's "if it breaks the same way twice, it's a systemic issue" almost word for word. `background/sanity_daemon.py` (F2) and the supervisor/ntfy_responder daemons are pure toil-automation, just not named as such. | SRE's **blameless postmortem register**, **error budgets**, and **toil-reduction target**. | No formal **error budget**. R12's plausibility bands are diagnostics that trigger investigation, but SRE's error budget is a *quantified allowance* that, once burned, triggers a **standing policy change** (freeze feature work, invest in reliability) — we have the diagnostic half, not the budget-triggers-a-different-mode half. No **toil metric**: the background daemons are real toil-elimination but nobody tracks "% of turns spent on repetitive manual triage" to know whether the automation is actually winning or whether new toil (e.g. staging-file triage volume) is growing faster than it's automated away. |
| 5 | **Agile / INVEST** (story sizing, Definition of Ready / Definition of Done, backlog refinement) | `G5_effort_sizing_discipline`'s calibration half (`tools/effort_calibration.py`, L0→1) mines real git-timestamped level-transition durations per lane — this *is* #NoEstimates-style calibration against actuals rather than argued sizing. The L0–L5 maturity ladder is an implicit Definition-of-Done chain per level (a level isn't banked without Expert Hour + evidence). | Agile's **INVEST** criteria (Independent, Negotiable, Valuable, Estimable, Small, Testable) and explicit **DoR/DoD** gates. | (a) No explicit **Definition of Ready** check at FRAME time — nothing currently verifies an atom has a stated, checkable exit test *before* it's opened for BUILD (some atoms have historically been vague until someone hit the ambiguity mid-build). (b) INVEST's **Independent** property is checked only via the `file_scope`-disjointness proxy for concurrent draw, not via an explicit dependency-graph validation step. (c) The **Small** property (EFFORT_SIZING_DESIGN.md's `size: S/M/L/XL` field + XL-decompose soft gate) is *designed* but not yet wired onto real atoms — G5's own honest partial says so; this audit does not re-open that gap, it is already tracked. |
| 6 | **Queue theory / flow** (utilization vs. throughput, Little's Law) | "GPU at 2% isn't the constraint" and "don't force width onto the build lane" *are* queue theory's founding, counter-intuitive result — high utilization does not mean high throughput; a nearly-idle resource can still be the wrong place to add width if it isn't where the queue is building. | **Little's Law** (L = λW — WIP equals arrival rate times time-in-system) and the utilization-vs-throughput relationship (Kingman's formula: queue length explodes as utilization approaches 1, it does not fall). | We have the *qualitative* lesson (utilization isn't the goal) but not the *quantitative* triangle. G5's calibration tool computes duration distributions per lane but does not compute an arrival rate (atoms authored/proposed per day) or a live WIP count, so we cannot yet forecast "at current arrival rate and current WIP, how long will the backlog take" the way Little's Law would let us — the qualitative insight is banked, the forecasting instrument built on top of it is not. |

---

## 2. Reject-ceremony / adopt-principle — explicit, so it doesn't creep back in

For each discipline above, the **ceremony explicitly rejected** (built for
human-team coordination overhead we don't have) vs. the **principle adopted**:

| Discipline | Ceremony rejected | Principle adopted |
|---|---|---|
| Lean | Formal kaizen workshops, andon-cord physical signalling | Waste-naming as a diagnostic label on a stall, WIP-as-a-number |
| Kanban | Daily stand-up board walks, physical/virtual card-wall ritual | WIP limits and cycle-time as live metrics, smallest-verifiable-unit flow (already adopted) |
| Theory of Constraints | Formal DBR scheduling meetings, buffer-management dashboards for human shift planning | The Five Focusing Steps as a standing *query*, not a meeting |
| SRE | On-call rotations, paging/escalation policy theatre, formal SLA review boards | Error budget as a quantified diagnostic trigger, toil as a tracked percentage |
| Agile/INVEST | Sprint ceremonies, story-point poker, velocity-as-commitment, retrospective theatre with no register | INVEST criteria as a FRAME-time checklist, sizing calibrated from actuals (already adopted via G5) |
| Queue theory | N/A — queue theory has no ceremony, it's math | Little's Law as a forecasting instrument fed by data we already collect |

None of these ceremonies fit a one-principal, AI-executor shop — there is no
team to synchronise, no shift to hand off, no human capacity to protect from
burnout via SLA review boards. What every one of these fields worked out that
*does* transfer is the **flow mathematics and the failure-classification
discipline** — the parts that are true regardless of who or what is doing the
work.

---

## 3. Proposal-atoms generated (for the orchestrator to register)

Four genuine gaps surfaced above that are not already tracked by an existing
atom. **These are proposals only** — not registered into
`docs/design/maturity_map.yaml` by this fork (out of `file_scope`); the
orchestrator registers the real ones with `provenance: proposal`,
`loop_stage: idle`, and ranks them per P-1/PRIORITIES.md.

1. **G7_wip_and_cycle_time_dashboard** (Kanban row 2 + queue-theory row 6). Turn
   the raw material G5's `effort_calibration.py` already mines into a live
   WIP-count + per-atom age-in-stage + Little's-Law-style
   arrival-rate/throughput forecast, surfaced on the Method door. Dial, never a
   target — the number is read, not gamed.
2. **G8_constraint_identification_ritual** (Theory of Constraints row 3). A
   standing "what is the current constraint" query over per-lane cycle-time
   data, re-run at each digest/retro, replacing purely-reactive bottleneck
   discovery with the Five Focusing Steps' elevate→repeat loop.
3. **G9_error_budget_and_toil_tracking** (SRE row 4). A quantified error-budget
   instrument built on top of R12's existing plausibility bands (burn triggers
   a named policy response, not just an investigation), plus a toil-percentage
   metric for the background-daemon lane so automation-vs-new-toil growth is
   visible.
4. **G10_definition_of_ready_gate** (Agile/INVEST row 5). An explicit
   Definition-of-Ready check at FRAME time — a stated, checkable exit test and
   an explicit independence/dependency check — wired into the director twin's
   existing BUILD-open call (canon v2 §3a) rather than a new approval layer.

Each of these is DISCOVER/FRAME-workable immediately per epoch gating
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md`); none is BUILD-opened by this doc.

---

## 4. Finding 1 amendment — deferred, orchestrator follow-on

The brief's DoD calls for amending CLAUDE.md's Finding 1 ("search published
practice when you hit a wall") to explicitly include non-AI delivery
disciplines, not just published agent/AI-harness practice. **Not done in this
fork**: CLAUDE.md is at 34,766 characters against the documented 35,000-char
hard limit (`Read` confirmed before starting this atom), and this fork's
`file_scope` explicitly excludes `CLAUDE.md` edits per the task brief. This is
recorded here as the orchestrator's follow-on, matching the identical
precedent G5 already set for its own CLAUDE.md-adjacent guardrail line
(`EFFORT_SIZING_DESIGN.md` §6). The exact amendment text proposed, for the
orchestrator to place when space is freed at the next CLAUDE.md trim:

> Finding 1 ("search published practice when you hit a wall") extends to
> **non-AI delivery disciplines** (Lean, Kanban, Theory of Constraints, SRE,
> Agile/INVEST, queue theory) — not only published AI-agent-harness practice.
> Most of what bites this project lives in the process layer, which predates
> AI and is independent of who does the work (`docs/design/METHOD_LENS_AUDIT.md`).

---

## 5. Relationship to already-landed work (not re-litigated here)

- `G5_effort_sizing_discipline` — the sizing instance of Agile/INVEST row 5,
  calibration half already built. This audit does not duplicate it.
- `H9_map_write_serialisation` — already solves half of Kanban's WIP-limit
  problem structurally (removes the map-write contention that capped
  parallelism); this audit's WIP-dashboard proposal (G7) is additive, not
  a re-ask.
- `G4_unified_failure_register` — already is the SRE blameless-postmortem
  register named in row 4; G9's proposal is the *error-budget* half only,
  not a re-implementation of G4.
- `PER_ATOM_INTEGRATION_NOT_WAVES.md` — already landed the Kanban
  single-piece-flow finding this lens itself would have predicted; recorded
  in the map's own `G6_method_lens_audit.simplifications` history as
  "the first concrete Kanban/flow finding this lens predicted."

## 6. DoD checklist (self-audit against the brief)

- [x] Audit run as a DISCOVER pass (doc-only, no BUILD/level-move beyond this
      atom's own L0→1).
- [x] Mapping table (lesson/mechanism ↔ established pattern ↔ refinement
      missing) produced — §1.
- [x] Surfaced on the Method door — `site/method-casebook/index.html` "Method
      Lens" section, data wired through
      `tools/generate_method_casebook_data.py`.
- [x] Proposal-atoms generated for genuine gaps, clearly labelled, queued for
      director/orchestrator rank — §3 (not written into the map by this fork).
- [x] Reject-ceremony / adopt-principle recorded — §2.
- [x] Dial-not-target guardrail recorded — §0.
- [ ] Finding 1 amended in CLAUDE.md — **deferred**, char-limit + out of
      `file_scope`; exact text staged in §4 for the orchestrator.
