---
name: phase-close
description: The phase-close checklist for this project — freshness check, evidence-on-business-surfaces, epistemic verifier, CLAUDE.md size discipline, test-count phrasing, retro/archive triggers, commit+push. Use whenever a phase/atom/build increment is being closed out (level moved, staged instruction actioned, capability landed) — this is the procedure that was previously duplicated as prose in CLAUDE.md every session.
when_to_use: Invoke before claiming any phase/atom/staged-instruction complete, before bumping a maturity-map level, or when the user says "close this phase" or "is this done".
---

# Phase-close checklist (in order)

0. **PRIORITIES.md freshness:** "Next" must have ≥1 real roadmap item outbidding self-generated work. If stale, refreshing it IS the next task — before all else.
0a. **Board sections are NOT phases (permanent rule):** A new board/report/Observatory section alone never counts as a phase. Reporting is a byproduct of building capability. Any "add X Observatory / X report section" proposal is automatically outbid by PRIORITIES.md P1-P3.
0b. **Evidence lands on business surfaces, not specs (2026-07-04, EVIDENCE_IN_BUSINESS_SURFACES.md):** every capability phase must show, generated from the latest run: (1) the signal graphed over time + one correlation panel (Sim tab); (2) one named customer where it manifests, real dates/amounts (Customers tab); (3) the changed decision process that consumes it (Supplier tab); (4) both sides of the epistemic wall + the divergence, where applicable. Project tab spec is the archive, never the evidence. A spec page alone does not close a phase.
0c. **Read one instance as a human (2026-07-09, BILL_CORRECTNESS_ADDENDUM.md):** for any customer-facing artefact (a bill, an invoice, a statement), definition-of-done includes rendering one real instance and inspecting it against domain law by eye, alongside whatever automated invariants exist. Automated tests catch what they were written to check; a human-legible read catches the class the tests never anticipated (found this way: a real SME account rendering as "Household / Residential" with residential-implausible consumption — no automated invariant existed to catch it because nobody had written one for "does the label match the segment").
1. Update test count + latest run figures in PROJECT_OVERVIEW.md Section 10.
2. Add build history entry in PROJECT_OVERVIEW.md Section 4.
2a. **Qwen skeptic pass (2026-07-09, DOMAIN_SENSE_AND_COMPLIANCE.md Phase 7):** for any phase touching a customer-facing or business-surface artefact, sample 2-3 randomly rendered ones via `company/compliance/internal_audit.py::run_phase_close_audit()` (grumpy-UK-energy-auditor prompt, local Qwen). Findings are ADVISORY, not confirmed defects — verify by eye before acting (a live run flagged a bill's correct VAT and a real 3GWh/yr I&C customer's normal monthly consumption as "implausible"; both were false positives on manual check).
3. **Run epistemic verifier:** `python3 -m tools.epistemic_verifier` — must PASS before committing. If FAIL: fix violations first.
4. **`wc -c CLAUDE.md` — hard limit 35,000 chars / 200 lines.** If over: move to `docs/claude/phase-history.md`. Never accumulate phase details in CLAUDE.md. Recurring procedure that belongs only in prose, not the whole codebase's history, moves to a skill like this one.
5. Add one-line phase completion entry to CLAUDE.md "Current state" — **must include the true full-suite count phrased as "N tests collected" (not just "N tests passing")** (two build-derivation parsers, `tools/generate_phases_json.py`/`tools/generate_dashboard_data.py`, both mechanically scan this exact section for a test-count figure and cannot distinguish an entry's own partial/scoped count from the true running total; "collected" is the one phrase this project's tooling treats as authoritative).
6. **Retro check:** if this phase closed a multi-day/multi-false-claim problem, or ~50 phases/2 weeks have passed since the last retro, or a harness rule changed — run the `incident-retro` skill before closing.
6a. **Harness pruning ritual (HARNESS_BEST_PRACTICE_ADOPTION.md item 6):** after each model upgrade, disable one harness piece at a time and observe what's still load-bearing; retire what isn't. Run this alongside the retro check above, not as a separate cadence.
6b. **Archive on completion (director-caught, recurring class):** if this phase closes a staged instruction fully, move it to `docs/staging/done/` in THIS SAME commit — never leave a fully-built file sitting in the scanned staging root (re-grants a supervisor turn every ~2min indefinitely with nothing new to do). If only PART of a staged instruction is done, move it to `docs/staging/in_progress/` instead — never leave a partially-done file in the root either. State the specific blocking sub-item and what unblocks it at the top of the parked file.
7. Commit and push (see the `staging-protocol` skill for the tree-lock/re-fetch discipline on a shared working tree).

`PROJECT_OVERVIEW.md` is updated at phase close. Run-complete pipeline does NOT update it.

## Level-promotion evidence bar (maturity-map atoms)

Cells move only at phase close, only with evidence, only having passed the Hardening Loop
(DISCOVER → FRAME → BUILD → VERIFY → HARDEN — see `docs/design/MATURITY_MAP.md` §2-3 for the full
level ladder). Concretely:

- **Never bump a level on fixture/unit-test evidence alone if a live consumer exists.** R1
  (consumer-verified completion) and R11 (verify to the rendered value) both apply: if the atom's
  evidence trail cites a live data file (`run_output_latest.json`, a generated site JSON), the level
  bump waits until that live artefact is regenerated and inspected — not claimed the moment the code
  merges. Example: a bridge/reconciliation mechanism that "returns None gracefully against the
  current cached run" is not yet done; it's proven once a fresh run produces a real, sane, non-null
  result and that result is read by eye.
- **The honest-hold discipline:** if you genuinely can't verify against live data yet (a long-running
  process hasn't caught up), say so explicitly in the atom's own simplifications entry and leave
  `level_current` where it is — do not round up "should work" to "works." A held level with a
  precise, named blocker is not a failure; a level bumped on hope is (R3: two-strike redesign follows
  a second false claim on the same component).
- Every level-up entry names: what was built, what evidence proves it (with real numbers, not
  placeholders), and what the NEXT level still requires — so the next reader never has to re-derive
  the gap from scratch.
