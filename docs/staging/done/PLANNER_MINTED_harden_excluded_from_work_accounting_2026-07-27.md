<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED / PROPOSE-THEN-PROCEED] — HARDEN re-verify never counts as work (deadman / utilisation / product-machinery split) (2026-07-27)

**Provenance:** RUNG-7 mint from a ratified ruling's WORK THIS CREATES block (§2+§4 mechanism, landed
6f2be1d41). Source: `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27.md`, deliverable **1**
("HARDEN demotion + rate limit + exclusion from work accounting — with the §1 R15"), as **restated by
the same-day amendment**.

**Why this is a distinct mint, not a re-mint of the landed item 1:** deliverable 1 has two separable
halves. The **draw-ordering** half is LANDED and R15-proven (`_unconsumed_director_ruling_or_steer` +
the `_self_refill_draw` guard suppress the RULE-0 HARDEN tier while an unconsumed staged ruling/steer
is present; `test_harden_suppressed_while_staged_director_ruling_unconsumed` reproduces the
2026-07-27 08:23–10:25 state as a failing test). The **accounting-exclusion** half — the amendment's
verbatim non-negotiable *"it never counts as work for the deadman clock, utilisation, or the
product/machinery split"* — is **NOT mechanised**: neither `background/deadmans_switch.py` nor
`background/daily_self_note.py` has any `harden` exclusion, so a HARDEN re-verify commit that touches
code/tests today (a) refreshes the deadman liveness clock as a "work commit", and (b) is counted as a
substantive MACHINERY commit in the daily-note product/machinery split — exactly the busywork-masks-
real-work failure the ruling forbids. Consumed ≠ absorbed ([[feedback_consumed_not_absorbed]]): this
mint carries the un-absorbed half.

**Serves:**
- **§1 (restated by amendment)** — HARDEN "must never be able to fill an idle period in place of real
  work"; the accounting exclusion is how "no below-target work" stays honest even when HARDEN is
  legitimately re-verifying (it found four real defects on 2026-07-27, so it stays *available* — it
  just must not *register as forward progress*).
- **The deadman honesty invariant** (`deadmans_switch.py`: liveness keys on MEANINGFUL progress only —
  chore/*, auto-process, planner-rest-proof already excluded; HARDEN belongs in that same non-progress
  class). [[project_eighth_class_pending_batch_deadlock_2026_07_27]] is the cost of a liveness clock
  refreshed by non-work.
- **PRODUCT-FIRST** (`daily_self_note.py` product/machinery split, DIRECTOR-RULING 2026-07-23) — a
  HARDEN pass is neither product nor forward machinery; counting it inflates the machinery tally and
  hides an all-HARDEN day.

**Robustness gained (one sentence):** a day (or window) whose only commits are HARDEN re-verifications
reads as a RESTING window to the deadman clock and shows ZERO product AND ZERO machinery forward
progress in the daily note — so "no below-target work" can never be masked by re-verification churn.

---

## Scope — BUILD (harness/observability lane)
- **Lane:** harness / observability. **Target level:** L2 (harness mechanism; not a company-layer
  capability, so no director level-up needed — but see walls).
- **Exit criteria:**
  1. A shared, single definition of "this commit is a HARDEN re-verification" (by commit-subject
     convention — decide + document the marker, e.g. a `harden(` / `[HARDEN]` subject prefix that the
     HARDEN draw path already emits or is made to emit; independence per R15 — key on the ACTUAL
     subject, never a constant).
  2. `deadmans_switch.py::_is_non_progress_commit` returns True for a HARDEN commit (joins chore/*,
     auto-process, planner-rest-proof) — a HARDEN-only window ages toward the 6h rest cap exactly as a
     genuinely idle window does.
  3. `daily_self_note.py` excludes HARDEN commits from BOTH the substantive count and the
     product/machinery split (fold into the existing mechanical-republish exclusion path, or a sibling
     class — SIMPLICITY GUARD: reuse `_is_substantive_file`'s structure, no new cathedral).
  4. **R15 both ways (binding):** (a) a window of nothing-but-HARDEN commits → deadman treats it as
     stale/resting AND daily note shows 0 product / 0 machinery; mutate the exclusion off → the test
     goes RED (a HARDEN commit wrongly refreshes liveness / counts as machinery). (b) a real
     below-target BUILD commit in the same window still counts as work both ways (no over-exclusion —
     the fail-open direction is "count real work", so prove the non-HARDEN commit is NOT swept up).
- **Deps:** none hard. Coordinates with deliverable 3 (rung-1 ordering) and 5 (backlog surface) — all
  three sharpen the same "no below-target work must be checkable, not asserted" invariant; disjoint
  file_scope (`deadmans_switch.py`+`daily_self_note.py` here vs `supervisor.py` for #3), so buildable
  concurrently per MULTI_ATOM_DRAW.

## Walls untouched (director-reserved)
- One-way doors: none — git-reversible harness change, no real market/money/secrets/safety-control.
- Curriculum values / generator ground truth: untouched.
- The HARDEN tier itself is NOT abolished (§1: "demoted, not abolished") — it stays available and
  keeps finding real defects; this mint only changes how its output is ACCOUNTED, never whether it runs.

## Window
Director-ruled mechanism (the amendment names the non-negotiable directly), so no design-ambiguity
propose window — drawable now as harness BUILD, failing test FIRST per the ruling's acceptance clause.

— Planner mint, RUNG-7 refill from ruling WORK THIS CREATES §4, 2026-07-27.
