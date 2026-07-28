<!--
MINT COVERAGE MAP (machine-authored, worker tick 2026-07-28) — DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG.
Parked in in_progress/ (multi-part; deliverables 1–3 MINTED, not yet BUILT). Blocking sub-item: the
minted GAP1/2/3 docs are RUNG-1 staged work; GAP1's BUILD half additionally needs a director BUILD_OPEN
(harness-lane demotion). Nothing here proceeds past a reserved wall.
[1] gap registers wired as planner mint sources + enumeration reporting them — MINTED: PLANNER_MINTED_gap_registers_as_mint_sources_2026-07-28.md (H_harness, 0→3; DISCOVER/design half drawable now, BUILD half blocked_on director BUILD_OPEN).
[2] proposed triage & ranking method — MINTED: PLANNER_MINTED_gap_triage_ranking_method_2026-07-28.md (DISCOVER doc-only, drawable now, returns for ratification).
[3] first ranked gap list marking deliberate-and-staying — MINTED: PLANNER_MINTED_first_ranked_gap_list_2026-07-28.md (DISCOVER doc-only, blocked_on GAP2 ratification).
[4] cohort-activation status + exit-criterion counter reading + last reset cause — COVERED by pre-existing atoms + status DISCHARGED (see §4 STATUS DISCHARGE below). NOT re-minted.
-->
# [DIRECTOR-RULING] — The published gaps ARE the backlog. Saturation was a bookkeeping artifact. (2026-07-28)

**Type:** [DIRECTOR-RULING] via advisor bridge. Written as a decision plus a problem; the triage is yours.

## 0. The contradiction, stated plainly

Overnight the draw reported *"no below-target work anywhere"* and, at 21:47Z, *"a genuine CANNOT-draw"* — then spent the last ninety minutes re-stamping cooldown timestamps on atoms already at target.

Meanwhile the project **publishes**, on its own site and in its own registers: hundreds of named simplifications each with a measured bound; fidelity cells where the model performs **worse than a naive baseline**; PARTIAL and ABSENT rows across six board-specification reconciliations; disqualification-battery items a practitioner said would make the build not credible; a carbon ledger — the company's entire reason for existing — designed and **not instrumented**; and standing sanity findings.

**Saturation was an artifact of how work is counted, not a fact about the world.** The director's verdict: *"there are loads of things it self-reports on the website as not being built or not working or containing errors or working worse than random."* He is right, and the honest reading is that the machine has been publishing its own backlog for weeks while treating it as documentation.

## 1. DECISION — the published gap registers are mint sources

**A rest or saturation claim is not defensible while any of these hold open items.** They become first-class mint sources for the planner rung, ranked alongside everything else:

- the **simplifications register** (each entry with its measured bound)
- the **fidelity ledger**, especially cells at or below a naive baseline
- **board-specification reconciliations** — every PARTIAL and ABSENT row across specs 001–006
- **disqualification-battery items** not currently met
- **claim-status placeholders** — anything published as designed-but-not-working, starting with the carbon ledger
- **standing sanity findings** adjudicated real
- **Timeframe 2 of THE_MODEL_ON_A_PAGE** — the company's own roadmap, which exists in no atom
- **registered follow-ons** from prior steers

"No below-target atoms" may still be true; it is no longer sufficient. The enumeration must report these sources too, per LAW C, from primary state.

## 2. PROBLEM — triage and ranking are yours

**Not every gap should be closed.** Many simplifications are deliberate scope choices and should remain, argued rather than silently fixed. Others are cheap and high-value. Some are blocked on director decisions. Some are genuinely not worth the complexity they would add.

**Propose the triage:** how gaps are classified, what ranks them (fidelity impact? mission relevance? board-battery weight? blast radius? cost to close?), what threshold makes one worth minting, and which should be explicitly marked *deliberate and staying*. State your reasoning and the evidence behind the ranking. You hold the registers, the ledger and the code; the advisor holds only the documents.

**And argue back where the advisor is wrong.** If some of the sources above are poor mint sources — noisy, stale, already-superseded — say so with evidence rather than working through them dutifully.

## 3. Non-negotiables

- **R12:** the number of gaps closed must never become a score, a target, or a headline. It is a diagnostic. Closing cheap gaps to move a count would be the breach the rule exists for.
- **Deliberate simplifications stay deliberate.** Closing one silently, or reclassifying it to make it closable, is a claim-status defect.
- **Reserved walls unchanged:** curriculum values (R13), one-way doors, generator ground truth. A gap whose closure needs a director decision gets escalated as one, not worked around.
- **Honest reds still credited.** A gap that is examined and *left open with a better-measured bound* is a legitimate outcome, not a failure.

## 4. Two open items, chased

**(a) Cohort assignment.** Ruled active on 2026-07-27 (`e685eb76d`); no cohort or coverage-report work has landed since. Report status: done, in flight, blocked, or counter-proposed.

**(b) The harness exit-criterion counter.** What does it currently read, and what caused the last reset? A night of HARDEN-while-content-unminted should have been resetting it. If it is not yet wired to primary state, say so plainly — a criterion that cannot observe last night is not yet a control.

## 5. Coherence

This is the actual content of the §5 backlog surface ("named-and-not-done must be enumerable and checkable"). The registers already exist; nothing read them as work. Derivation rules apply unchanged: any surface claiming completeness must derive it from these sources, never assert it.

## WORK THIS CREATES

1. Gap registers wired as planner mint sources, with the enumeration reporting them.
2. A proposed triage and ranking method, with reasoning and evidence — returned for ratification if it implies any curriculum or scope judgement.
3. The first ranked gap list, marking which are deliberate-and-staying.
4. Status on cohort activation; current exit-criterion counter reading and last reset cause.

Acceptance: a saturation claim is impossible while any published register holds an open, un-triaged item.

**Risk & proportionality:** widens the drawable set from existing published artifacts; no new scope, no curriculum change; triage returns for ratification where it implies judgement. Tag: **proceed.**

— Advisor bridge, carrying the director's correction, 2026-07-28.

---

## §4 STATUS DISCHARGE (machine-authored, worker tick 2026-07-28)

Deliverable 4 asked for status, not a build — both open items are already carried by existing map
atoms, so nothing is re-minted. Reported here from primary state (git + the map), per §4.

**(a) Cohort assignment — BUILT, awaiting director level ratification (NOT "no work landed").**
Argue-back with evidence (§2/§4 invite the correction): the advisor states *"no cohort or
coverage-report work has landed since 2026-07-27."* That is factually wrong. It landed on 2026-07-27:
- `ead9035b3` — *[BUILD CA1+CA3+CA4 cohort-activation] flip assign_cohorts live at the seam,
  untestable-at-book ledger, PROCEED verdict* — `simulation/population_draw.py`,
  `simulation/live_population.py`, seam tests.
- `84b4614bb` — *[BUILD CA2_coverage_report_realised_cohort] realised JOINT cohort coverage — the
  ~12-cell value knee, thin cells NAMED as findings.*
Map state now: `CA1_cohort_assignment_live`, `CA2_coverage_report_realised_cohort`,
`CA3_segmentation_untestable_ledger_marking`, `CA4_cohort_activation_sequencing_verdict` — all
`loop_stage: build`, code landed at build quality, `level_current: 0`, `blocked_on:
director_level_up`. **Status: DONE-pending-level-ratification** (R16 — the agent does not self-bump the
level; the level move is the director's). No further cohort *build* work is drawable; the open item is
a director level-up on ratified code, not un-started work.

**(b) Exit-criterion counter — NOT yet wired to primary state; it is not yet a control.**
Honest reading, exactly as §4(b) anticipates (*"a criterion that cannot observe last night is not yet a
control"*): the counter is **not instantiated**. `grep` finds no live counter file in `background/` or
`docs/observability/`. The mechanising atoms exist but are unbuilt: `HX1_exit_criterion_counter_mechanise`,
`HX2_stall_set_coverage_verdict`, `HX3_counter_published_and_derivable` are all `level_current: 0`,
`loop_stage: build`, `blocked_on:` the harness-BUILD demotion (H-lane off every open product front,
fronts enforcement ON → excluded from the BUILD draw; the executing BUILD_OPEN is director-console-only,
R16). **Current reading: NONE — the counter reads nothing and could not have observed last night.**
**Last reset cause: N/A — it was never instantiated.** This is disclosed plainly, not fixed in this
bounded planner tick (it is director-BUILD_OPEN-blocked, the same wall as GAP1's build half). Wiring it
to primary state IS the HX1 work; a director BUILD_OPEN / H-lane FRONT_OPEN unblocks HX1 and GAP1
together.

---

## AMENDMENT — coherence gaps the advisor left, closed; and §1's list demoted to candidates

Self-audit at the director's prompting. Where this amendment conflicts with the text above, **the amendment governs.**

**A. §1's eight sources are CANDIDATES, not the definition.** The decision is only this: **published self-reported gaps constitute real work, and a saturation claim is indefensible while they stand open.** *Which* artifacts genuinely constitute backlog is your judgement — the advisor listed what it could see from documents. Add sources it missed; discard ones that are stale, superseded or noisy, with evidence.

**B. Gap-closure versus HARDEN — they are different classes.** Re-verifying an at-target atom is demoted under WORK_DEFINITION §1. **Closing a named gap with a measured bound is real advancement and is NOT demoted.** The distinction is evidential: gap-closure moves a published bound, a fidelity row, or a claim's status; HARDEN re-verification confirms an existing control still holds. **A HARDEN pass may not be relabelled as gap-closure to escape demotion** — that would be an R12 breach, and if the boundary is genuinely blurry in a given case, say so and propose where it should sit.

**C. Gap work under PRODUCT-FIRST.** Gaps span both lanes. The existing order stands unchanged: **a machinery-lane gap may not outrank a product-lane atom.** Ranking within a lane is part of the triage you are proposing.

**D. Gap-closure and the harness exit criterion.** The ratified criterion counts *product-content* atoms — product lane **and** a moved fidelity row, a spec-tied acceptance test, or an R11-verified live surface. Therefore: **a fidelity-cell or claim-status gap closure that meets that test counts; a harness-register simplification closure does not.** Do not let the widened backlog become a route to farming the counter — that is precisely the gaming vector the content definition was written to block. If a gap closure sits ambiguously across that line, it does **not** count and gets flagged for ratification.

**E. Reserved collisions, named.** Some published ABSENT and PARTIAL rows are already under director rulings and must not be closed as ordinary gaps: the **SSP baseline recalibration is HELD** pending merit-order reconstruction (no interim tuning of any kind); **curriculum values, generator ground truth and scenario difficulty remain R13**; **company-side segmentation is recorded untestable at the current book**, not a gap to close by growing the book. Where a gap's closure would touch one of these, escalate it as a decision rather than working around it.

— Amendment by advisor bridge, 2026-07-28.
