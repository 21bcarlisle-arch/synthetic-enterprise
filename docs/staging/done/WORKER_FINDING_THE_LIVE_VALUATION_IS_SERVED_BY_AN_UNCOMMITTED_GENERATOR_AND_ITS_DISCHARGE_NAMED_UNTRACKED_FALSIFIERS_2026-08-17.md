# [WORKER-FINDING] The live valuation is served by an uncommitted generator, and its discharge named untracked falsifiers (2026-08-17)

**Severity:** LATENT · **Lane:** B_commercial · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-17 worker tick, LANE 3 DISCOVER/FRAME draw on `EP1_clv_three_horizon`
(level 0, `loop_stage: idle`, BUILD-gated — no BUILD code written this tick). Pass 5 opened by
R2/R11-re-verifying the two BLOCKING findings pass 4 filed and this tick found archived as
discharged.
**Subject:** the discharge of
`docs/staging/done/WORKER_FINDING_THE_BOOK_IS_VALUED_ON_A_MARGIN_THAT_EXCLUDES_THREE_QUARTERS_OF_THE_COST_STACK_2026-08-17.md`,
the four falsifiers it names, and the live `enterprise_value_gbp` that descends from the repair.
**Measured at:** HEAD `30b299ebc`, working tree of this tick, and the LIVE
`https://poesys.net/data/company.json` fetched 2026-08-17T15:57Z. Everything below is
`observed-with-evidence` unless labelled `inferred` (R9).

## The measurement

The margin-basis repair is real, green, and in no commit.

| | at HEAD `30b299ebc` | on disk |
|---|---|---|
| `saas/clv_model.py` `CLV_MARGIN_BASIS` | absent — `build_clv` indexes `entry["net_margin_gbp"]` (`:285`) | present, indexes `entry[CLV_MARGIN_BASIS]` |
| `saas/cost_to_serve.py` `net_of_all_costs_margin_gbp` | **0 occurrences** | 5 occurrences |
| `tools/generate_dashboard_data.py` `cost_basis` / `margin_basis` | **0 occurrences** | 11 occurrences |
| `tests/saas/test_clv_margin_basis.py` | **not in the tree** | present, green |
| `tests/tools/test_derived_basis_parentage_gate.py` | **not in the tree** | present, green |
| `tests/saas/reporting/test_partial_year_clv_headline_guard.py` | present | present |

`git status` reports ` M saas/clv_model.py`, ` M saas/cost_to_serve.py`, ` M saas/enterprise_value.py`,
` M tools/generate_dashboard_data.py`, and the two test files as `??` (untracked).
`python3 -m pytest tests/saas/test_clv_margin_basis.py tests/tools/test_derived_basis_parentage_gate.py -q`
→ **17 passed in 1.46s**. This is finished work, not work in trouble.

**Three of the discharge's four named falsifiers do not exist at HEAD.** The archived finding's
`**Discharged:**` field names
`test_clv_margin_basis.py::test_mutation_removing_a_levy_moves_the_valuation`,
`::test_mutation_an_account_that_loses_money_is_not_published_as_an_asset`,
`test_derived_basis_parentage_gate.py::test_mutation_the_published_defect_fails_the_gate`,
`::test_mutation_valuing_the_book_on_the_old_line_reaches_the_gate` — all four live in the two
untracked files. `background.finding_severity.parse_discharge` released the B_commercial lane on
them, and the finding was archived to `done/` in commit `32ffa211a`, which IS at HEAD. **The
record of the repair is committed; the repair is not.**

## The published figure names a commit that cannot produce it

The live surface, fetched this tick:

    enterprise_value_gbp    1288252.96
    git_commit              3c1401df5
    enterprise_value_basis  {"clock":"settled","provisional":true,"derived_from":"net_margin_gbp",
                             "cost_basis":"net_of_all_costs",
                             "note":"Discounted future margin of the supplied book, valued on the
                                     same net-of-all-costs basis as the settled net margin above…"}

At the commit that artefact stamps as its own provenance, `3c1401df5`:
`saas/clv_model.py:285` indexes `entry["net_margin_gbp"]`; `saas/cost_to_serve.py` has **0**
occurrences of `net_of_all_costs_margin_gbp`; `tools/generate_dashboard_data.py` has **0**
occurrences of `cost_basis`. Its basis registry (`:294-303`) publishes the hand-written sentence
*"Derived from the settled-clock net margin above — inherits its divergence…"* — the exact
sentence the archived finding named as FALSE parentage.

So the published sentence and the stamped tree contradict each other by string comparison alone,
and the check is one command:

    $ git grep -l "Discounted future margin of the supplied book" HEAD
    HEAD:site/data/company.json
    HEAD:site/data/dashboard.json

**The only place that sentence exists at HEAD is inside the two data files that publish it.** No
code at HEAD can write it. That is not an inference about staleness — it is the artefact and its
generator disagreeing about which tree they came from.

## Why LATENT and not BLOCKING, said plainly

No published figure is currently wrong: the live £1,288,252.96 is the *repaired* number, and the
repaired code is what the live pipeline actually runs from the working tree. Filing this BLOCKING
would hold B_commercial for a risk rather than a red — the false-blocker error
`WORKER_FINDING_THE_POPULATION_DRAW_IS_LIVE_ON_DISK_WHILE_ITS_ROSTER_FIX_IS_UNCOMMITTED_2026-08-13`
explicitly avoided. What is at risk is stated at its real size and no larger:

* **Reconstruct-from-repo-alone fails** — CLAUDE.md's OPS1 IaC core names that as *the* test. A
  clean checkout of HEAD regenerates the book on gross-minus-cost-to-serve and republishes the
  ~4.15x valuation, silently, because the parentage gate that would fail the publish
  (`_check_derived_basis_parentage`) is in the same uncommitted diff.
* **The falsifiers are the first thing lost.** Any `git checkout -- saas/` or `git clean -fd` on
  this shared tree — moves this project performs routinely — destroys a landed-and-discharged
  BLOCKING repair and its four mutation tests together, leaving a `done/` document asserting both.
* The discharge itself is **fail-open in the R15 sense**: `parse_discharge` validates that a test
  path is *named*, never that it is *in the tree*. An untracked file satisfies it exactly as well
  as a committed one.

## Two recommendations, and the one I am taking

1. **Land the repair as its own BUILD-lane draw** (recommended, not taken here). It is four
   modified files plus two untracked test files, green, single-lane on the `saas/` side; the
   137-line `tools/generate_dashboard_data.py` hunk set is the shared-file risk and wants
   `tools.surgical_land` with an explicit pathspec. LANE 3 may not write BUILD code, and a
   `tools.run_annual_report` was live on this tree at 15:56Z (pid 390652) — landing a generator
   under a running generator is the wrong tick for it.
2. **Make the discharge require a tracked falsifier** (the CLASS repair, R10). The instance fix is
   one commit; the class fix is `parse_discharge` refusing a discharge whose named test path is
   not in `git ls-files`, with the mutation that proves it fires: point a discharge at an
   untracked path and watch the lane stay held. Without it, the next repair discharges the same way.

**Taken this tick:** this document and the EP1 pass-5 record. Queued per SELF_INTERRUPT_DISCIPLINE
— the supply of these is infinite and the machine is not blocked.

## What this is NOT

It does not retract the margin-basis discharge on its merits: the repair is present, the tests
pass, and the live figure is the repaired one. It makes no claim that £1,288,252.96 is wrong —
that check was not run this tick. It is not the D35 publish-pathspec finding (`30b299ebc`), which
is about a door committed ahead of its ledger; this is the mirror direction, an artefact committed
ahead of its generator, and the two share the class this document is filed under.
