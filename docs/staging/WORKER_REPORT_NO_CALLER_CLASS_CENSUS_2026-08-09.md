# [WORKER-REPORT] The no-caller class: the count, the names, the one page (2026-08-09)

**Answers:** `DIRECTOR_TASK_NO_CALLER_CLASS_CENSUS_2026-08-09.md`. **Report only** — nothing was
fixed, no gate/hook/mechanism added, no level moved, no parked class-fix item archived.
Every row below is `observed-with-evidence` (R9); inferences are labelled.

## Headline

The director's framing said "at least five". **The honest count is 13 instances in 13 days**
(2026-07-28 → 2026-08-09). **Eight of the 13 were found by accident.** It is **one class by shape**
— *something exists, is green, and nothing consumes it* — but **two classes by detector**, which is
precisely why it keeps being filed as unrelated incidents. **No single mechanism covers the set.
The smallest number is two**, and §2 states why they cannot be one.

## 1. Every instance to date

Shape A — **the artefact is in git; reachability over committed source can decide it.**

| # | Instance | Found | How | Evidence |
|---|---|---|---|---|
| 1 | `check_scenario_fidelity` — 6 R15-proven moments, **zero production callers** | 2026-07-28 | deliberate (fail-silent audit) | caller built in `7dd481858`; blade found a real defect the instant it swung |
| 2 | `generate_evidence_data.generate()` — evidence-page generator, no production caller | 2026-08-03 | accident (SITE draw) | `ad7486aac`, `8f108bf15` |
| 3 | `write_fabric_gap_entries` / `fabric_settlement_gap.py` — measurement fn, no caller | 2026-08-03 | deliberate (orphan-transition audit) | `8cfe10997` |
| 4 | `TenancyChangeCoupler` — no production caller, **and load-bearing for another atom's park reason** | 2026-08-03 | accident (DD_seasonal draw) | built `f2fe0bde1`; `life_events.py` emitted no move event at all |
| 5 | `comfort_constraint_for(prior_year_bill_gbp=None)` — live mechanism, **permanently dead input**; every household heated to full SAP comfort regardless of running cost | 2026-08-03 | accident (wiring it into a real path) | `66d73d1e0` |
| 6 | `CLONE_CEILING = 223` — **constant never compared**; `clone_count: 267` sat beside it in primary state, a 44-instance breach firing nothing | 2026-08-03 | accident (SP3 draw) | `81a43bd9c` |
| 7 | `append_warn_log`'s `if not findings: return` — **guard unreachable from its only caller**; mutating it fired no test in a suite of 28 written for R15 | 2026-08-03 | deliberate (mutation run) | SP3 |
| 8 | Capability index counted **a tool's own docstring path as its own caller** | 2026-08-08 | deliberate (mirror-defect check during AO1) | `7e5a727d4`, guard is `mod != own` at `tools/capability_index.py:474` |
| 9 | `PUBLISH_GATE_MARKER_EXPR` complement drift — a deselected test tier **covered by no gate at all** | 2026-08-08 | deliberate (existing complement test held) | `e7cfb0f39` |
| 10 | `forward_attachment_register --write`, `pull_forward_proposal --write` — **regeneration step nothing ever runs**; ordinary staging hygiene silently invalidates a committed artefact a blocking test checks | 2026-08-09 | accident (publish wedge, 5-cause episode over 3 ticks) | `96bdad98a` |

Shape B — **the artefact is not in git at all; no analysis over the repo can see it.**

| # | Instance | Found | How | Evidence |
|---|---|---|---|---|
| 11 | `D_money_boundary_reconciliation` self-certified L0→L2 on "0/1603 non-footing" measured on the working tree; `saas/money.py` + both test files still `??` | 2026-08-03 | accident (live re-add) | re-add of live `poesys.net/data/customers/*.json` returned **625/1603 still not footing** |
| 12 | `C_supply_start_semantic_separation` — map committed at `level_current: 2`, `gate_authorizations.jsonl` carrying a detailed self-certification citing 5 mutations and 2,574 tests, while `company/crm/supply_start.py` + its 407-line R15 file were **untracked** | 2026-08-08 | accident | `10e8ca6a7`; a clone got a map and a ledger asserting a mechanism absent from git |
| 13 | `W2_16` green build (77 tests) died uncommitted; `premise_trace.py` +322 lines (51 tests) left at risk the same evening | 2026-08-08 | accident (gate happened to need the same file) | adopted as `14e00c2ba`, `46422b0d6` |

**Corrections to the framing, as asked.** All five disguises the director named are real and confirmed
(#2/#3 mechanism-with-no-caller, #5 dead input, #8 self-caller, #11–13 uncommitted green work, #10
regeneration nobody runs). The list **extends** by three further disguises he did not name — a
**constant nobody compares** (#6), a **guard unreachable from its own caller** (#7), and a
**complement pair drifting apart so a tier is covered by nothing** (#9) — and the uncommitted-work
disguise is **three** instances, not one. It does **not** contract: no row here dissolves on inspection.

**New evidence produced for this page (mutation, run today).** Removing the own-guard at
`capability_index.py:474` in-process flips **29 module statuses**, and `background.run_rotation`
flips **orphan → wired** — i.e. a genuine orphan is certified live purely by naming its own path in
its own docstring. Also observed: `tests/tools/test_capability_index.py` contains **no test of the
own-guard**, so #8's fix is currently unprotected by R15. Filed as observation; not fixed (reserved).

**The cumulative cost, which nothing on the board has stated.** 13 instances / 13 days; 8 by
accident; at least three with measured downstream damage — 625/1603 live customer records not
footing while the map read L2 (#11); a 44-instance ceiling breach live in primary state (#6);
publishing wedged across three ticks by a five-cause episode of which three causes were this class
(#10). **Inferred (not observed):** the class fix keeps being outranked because each *instance* is
an hour's work, so every draw closes the instance and the class fix never wins a single comparison.
The count is the argument, and until this page no artefact carried it.

**On the deferred per-commit evidence record.** The director's read is confirmed and is stronger than
stated: **10 of 13 sit downstream of a green commit.** A per-commit record would have caught #11–13
only — exactly the sub-class he already credited it with. The deferral is correct.

## 2. What one mechanism would have caught all of them

**None. The smallest number is two.**

**M1 — a reachability census from declared production entrypoints, at symbol granularity.**
Covers #1–10. Four requirements, each forced by a specific row above:
- **The entrypoint set must be the committed schedule/IaC, not `if __name__ == "__main__"`.** This is
  the load-bearing design point and the one the current index gets wrong: #10's `--write` has a main
  block, so it reads as a legitimate `entrypoint` and can never be reported as an orphan. A CLI
  nothing schedules is an orphan.
- **It must descend below the function** — optional parameters no caller supplies (#5), constants
  never compared (#6), guards unreachable from their only caller (#7), complement pairs (#9).
- **Path-references count as callers; self-references must not** (#8, mutation-proven above).
- **It is itself a fail-open control** — an index that under-reports looks like a small codebase and
  *authorises* the thing it existed to prevent. Needs a vacuity floor proven alone and an independent
  coverage oracle (`git ls-files`, not the same filesystem walk).

**M2 — a VCS-state check at tick exit and at level-up.** Covers #11–13: every path in the atom's
`file_scope` is tracked and clean before a level self-certifies, plus a tick-exit report of
uncommitted tracked changes *outside* the tick's own `file_scope`, naming the owning atom —
reporting only, never auto-committing.

**Why they cannot be one.** They read different substrates and fail in opposite directions. M1 reads
*committed source* and answers "is this reached?" — it structurally cannot see uncommitted work,
because an untracked file is either absent from its graph (invisible) or present in a working-tree
walk and looking perfectly wired. M2 reads *git state* and answers "does this exist for anyone but
me?" — and says nothing about whether committed code is ever reached. Note the two even disagree
about #12: M1 would have read that tree as healthy. A single mechanism would have to carry both a
reachability model and a VCS model, and would be these two wearing one name.

**Existing partial coverage (so neither is a from-scratch build).** `tools/capability_index.py`
(2026-08-08) is roughly 60% of M1 already — it derives 837 rows and reports 266 orphans today; what
it lacks is the schedule-derived entrypoint set, the sub-function granularity, and an R15 test on its
own-guard. `tools/level_promotion_gate.py` refuses an *unrecorded* level move but does not check that
`file_scope` is tracked and clean — that named gap is already the R3 two-strike finding and is the
natural home for M2's first half.

## 3. Selection under the pre-authorised veto (per `DIRECTOR_INSTRUCTION_PROCEED_WITH_VETO_PAIR`)

**Selected class fix: M2's level-up half** — extend `level_promotion_gate.py` so a recorded level move
whose `file_scope` contains an untracked or dirty path fails at commit time.

**Case.** It is the cheapest of the two (one gate, one predicate, mutation-testable by dirtying a real
path); it is the only one already at R3 two-strike, where the rule says stop hand-checking and build
the gate; it closes the sub-class with the highest measured damage (#11's 625 live records); and it is
reversible and touches no true door. M1 is the larger prize but is a sized build, not a veto-window
item — it should be minted as its own atom and drawn on its own priority. Announced with a **12-hour
objection window**; proceeding after it unless objected. This selection is filed with this page as
the instruction requires.

**Not done this turn, deliberately:** the `value_chain_observation_window_cap` mechanism (item 1 of
the same instruction) remains queued — it is a separate sized build, not this drawn tick's work.
