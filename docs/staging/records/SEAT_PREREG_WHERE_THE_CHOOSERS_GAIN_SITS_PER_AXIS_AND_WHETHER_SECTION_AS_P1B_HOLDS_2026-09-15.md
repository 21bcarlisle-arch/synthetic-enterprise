**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# PRE-REGISTRATION — where the chooser's gain sits per axis, and whether §A's P1b holds

**Filed 2026-09-15, delivery seat, BEFORE the arms below were run.** This grades exactly one
prediction: **§A's P1b**, left `UNGRADEABLE` by
`SEAT_RESULT_SECTION_A_OF_THE_MERGED_PREREGISTRATION_REGRADED_AGAINST_ITS_OWN_NUMBERING_2026-09-15.md`
because the filed evidence reports **worst-axis** KS and P1b is a claim about **per-axis** KS.

That file named this as unrun work rather than carrying it as a hold. This is the run.

---

## 0. The prediction being graded, verbatim

> *"I predict the gain is concentrated on the fabric axes (floor area, heat-loss coefficient,
> remaining insulation ceiling) rather than on cost."*

Two things about its wording are already established and are **not** re-litigated here:

* **"remaining insulation ceiling" is not an axis and never was.** The shipped `CHOICE_AXES` are
  `floor_area_m2`, `fabric_w_per_k`, `raw_infiltration_ach`, `customer_years`. The phrase belongs
  to `tools/settlement_choice_probe.py`'s six-axis draft (`insulation_ceiling_w_k`), which is what
  §A was written against. A third of P1b's fabric set has no column and cannot be graded. Recorded,
  not repaired — the pre-registration stays verbatim.
* **`customer_years` is the cost axis.** It is what "rather than on cost" names.

## 1. What is measured, and the one variable

**ONE candidate list, two selection rules.** The live campaign is resolved once at the shipped seed
and its candidate list captured at `settle_within_budget`'s own boundary (the technique in
`tools/settlement_choice_probe.capture_candidates` — a spy, not a new production parameter). Both
arms are then produced by calling the **shipped** `settle_within_budget` on that one list:

* **ARM A — the cull.** `simulation.settlement_choice.choose_settled_sample` patched to return
  `None`, which is exactly the refusal the shipped fallback exists for. The systematic
  `int((i+1)*r) > int(i*r)` rule runs, and every weight is the scalar `1/sample_rate`.
* **ARM B — the chooser.** Unpatched: the shipped path, `fit_weights(groups=candidate_years)`.

Positions are recovered from the returned `winners` by **object identity** against the candidate
list, so no selection logic is replicated in the harness and the arms cannot drift from the shipped
rule. Weights come from `settlement_weights`, which is parallel to `winners`.

**The statistic.** For each axis *j*, `tools.demand_vector_coverage.weighted_ks` of that arm's
settled sample against the **full candidate population's** marginal on *j* — the same function and
the same reference the 1.553× came from. The per-axis **gain** is

    g_j = KS_A(j) / KS_B(j)          ( > 1 means the chooser is closer to the population on j )

## 2. The self-check that can refuse the whole run, declared first

Arm A must reproduce **90 settled / 1195.4 cy** and arm B **84 settled / 1197.0 cy**, and
`max_j KS_A(j) / max_j KS_B(j)` must reproduce **1.553×** to three decimals (0.12798 / 0.08241).

**If it does not, nothing below is graded and the disagreement is the finding.** A per-axis reading
from a harness that cannot reproduce the filed scalar is a different measurement wearing its name.

## 3. The grading rule, pre-committed before any number is seen

The **fabric set** is the three physical axes — `floor_area_m2`, `fabric_w_per_k`,
`raw_infiltration_ach`. Infiltration is a fabric quantity and is in the set on that ground even
though §A did not name it; §A's named-and-existing pair (`floor_area_m2`, `fabric_w_per_k`) is
reported **beside** the primary verdict so the reading can be checked either way. The primary
verdict is the three-axis one.

| verdict | condition |
|---|---|
| **HOLDS** | every fabric axis gains more than cost: `min_fabric g_j > g_customer_years` |
| **FAILS** | cost is where the gain is: `g_customer_years >= max_fabric g_j` |
| **SPLIT** | otherwise — some fabric axes beat cost and some do not, and P1b **as written is false**, because "concentrated on the fabric axes" is a claim about the set and not about its best member |

**SPLIT is a failure of the sentence, not a draw.** Naming it separately is so that the *reason* it
failed is on the record, not so that it can be read as a pass.

## 4. The numeric predictions, with bands

* **N1 — P1b HOLDS.** I predict `min_fabric g_j > g_customer_years`. Stated because the chooser
  picks medoids in the standardised fabric space and `customer_years` is additionally pinned by the
  year-group constraint, which should leave it less room to improve.
* **N2 — the cost axis gains least, and barely.** I predict `g_customer_years` in **[0.85, 1.20]**
  — i.e. the chooser is roughly neutral on cost, and **may be worse than the cull on it**. The cull
  is systematic over a year-ordered list, which is nearly a stratified draw on `customer_years`;
  it should be hard to beat there. **Kill line: if `g_customer_years > 1.45`, N2 is wrong and the
  "rather than on cost" clause is refuted even if N1 survives.**
* **N3 — the worst axis in arm B is a fabric axis, not `customer_years`.** The 0.08241 that graded
  P1a belongs to a fabric axis. *If it turns out to be `customer_years`, then P1a's headline number
  and P1b's subject are the same column, and that is worth more than P1b's verdict.*
* **N4 — the spread is real.** `max_j g_j / min_j g_j >= 1.5`. A flat per-axis profile would mean
  "concentrated" has no referent and P1b is unfalsifiable rather than true.

## 5. The secondary arm, and why it is secondary

The regrade observed that `customer_years` **became a constraint rather than an axis** in §B's P3
repair, and that "a per-axis grading run before and after that repair is the honest way to take it".
So a third arm — **ARM B0**, `fit_weights(groups=None)`, the pre-repair fit — is run and reported.

* **N5 — the repair costs the cost axis and pays the fabric axes.** I predict `g_customer_years` is
  **higher** in B0 than in B (the unconstrained fit was free to spend mass on the `customer_years`
  CDF), and that at least one fabric axis gains **less** in B0 than in B.

**N5 does not change P1b's verdict.** P1b is graded on arm B, the shipped rule, because that is the
selection the published book actually comes from. B0 is evidence about the repair's cost, filed
beside it.

## 6. What this pre-registration does NOT claim

* It does not re-grade P1a. 1.553× stands; this run reproduces it as a check on the harness, not as
  a new reading.
* It does not revise §A. Both arms of the merged pre-registration stay verbatim; this file adds a
  grading for a clause that was recorded as ungradeable, and the grading is filed separately.
* It does not claim a per-axis KS profile is the right instrument for "concentration". It is the
  instrument P1b's own wording implies, and if the profile is flat (N4 fails) the honest reading is
  that P1b was never falsifiable — which is a finding about §A, not about the chooser.
* It does not touch the selection rule, the axis list, or `fit_weights`. No arm here is a change.
