<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED / DRAWABLE NOW] — R10 suppression sweep: audit 14 days of gates/throttles/folds by failure direction, publish the table (2026-07-27)

**Provenance:** RUNG-7 planner refill (director ruling `WORK_IS_THE_DEFAULT_2026-07-23`). Minted from `docs/staging/in_progress/DIRECTOR_RULING_FAILURE_BIAS_LAWS_2026-07-27.md`, whose "R10 sweep" section is explicit: *"the three laws alone are exhortation without it."* This is the **class fix**; the three law-mints are the per-instance mechanisms.

**Serves:**
- **DIRECTOR_RULING_FAILURE_BIAS_LAWS — the R10 sweep + standing consequence.** Ruling: "Audit every gate, throttle, suppression and fold introduced in the last fourteen days and classify each by failure direction: noisy or silent. Publish the table. Anything that fails toward quiet gets either a time-bound (Law A) or an independent counterpart (Law C)." Standing consequence: a future suppression proposed without stating *what will still page if the condition is real* is rejected.
- **R10 (absurdity/defect class closes by extending the invariant library, never an instance fix)** — this sweep is the R10 discharge for the silence-bias class.

**Fidelity/robustness gained (one sentence):** every gate, throttle, suppression and fold added in the trailing 14 days is classified by failure direction and the silent-biased ones are each assigned a Law-A time-bound or a Law-C independent counterpart, converting three exhortation-laws into an enumerated, verified class fix — and installing the standing gate that no new suppression lands without naming what still pages.

---

## Scope — ANALYSIS + a standing gate (drawable NOW; the ruling says the sweep "proceeds in parallel")

1. **Enumerate.** `git log --since=2026-07-13` over `background/**` + the daily-note/deadman code; extract every gate/throttle/suppression/fold introduced. Cross-check the five named in the ruling and the memory ledger ([[project_eighth_class_pending_batch_deadlock]], [[project_eighth_class_pending_batch_deadlock_2026_07_27]], [[project_harden_cooldown_rotation]], [[feedback_fail_silent_control_patterns]]).
2. **Classify each: NOISY or SILENT** on failure. For each SILENT one, assign the remediation: **Law A** (time-bound + re-arm) or **Law C** (independent counterpart) — cross-reference the three law-mints so the assignments are drawable, not just tabulated.
3. **Publish the table** — a committed artefact (`docs/observability/suppression_audit_2026-07-27.md` or the defect ledger), with columns: mechanism, commit, purpose, failure direction, remediation, status. Report the list with verdicts in the next digest.
4. **Standing gate (mechanise the consequence — R15):** add a check that a new suppression/gate/fold must declare `what_still_pages` (a non-empty rationale of the independent check that fires if the underlying condition is real). A suppression added without it fails the check. R15: add a suppression with an empty `what_still_pages` and prove the gate REDS; add one with a real answer and prove it passes.

## Walls untouched (director-reserved)
- One-way doors: none — analysis + a git-reversible harness gate.
- L3 level moves stay `blocked_on: director_level_up`.

## Window
Drawable NOW (analysis proceeds in parallel per the ruling). The table is the artefact that makes the three law-mints an enumerated class fix rather than three isolated patches.

— Planner mint, RUNG-7 refill, 2026-07-27.
