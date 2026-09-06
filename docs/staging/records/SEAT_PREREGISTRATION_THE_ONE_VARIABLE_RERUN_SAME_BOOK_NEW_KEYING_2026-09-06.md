**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: the one-variable re-run — same book, new keying

*Delivery seat, 2026-09-06, claim `the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`.
Written BEFORE the run. Nothing below is an observation.*

---

## The question this run exists to answer

`SEAT_FINDING_THE_LEG_CONTAMINATION_NEVER_TOUCHED_THE_PUBLISHED_CEILING...` (landed `f92232d53`)
compared **two things that both moved**: the HEAD instrument on `run_output_3851553ec_20260906T175920Z.json`
against the pre-keying instrument on `run_output_23cbe058b_20260906T141424Z.json`. Different
instrument *and* different book. It said so, and refused to attribute:

> the **increases** (69 → 146, 100 → 164, 69 → 164) cannot be leg folding alone. They are either
> the later book's account-state logging, or folding giving a household a field only its gas leg
> carried — and **this run cannot separate those two**.

This run holds the book fixed at the **published** one and changes only the instrument:

```
python3 -m tools.r1_inference_ceiling --run <shared tree>/docs/reports/run_output_23cbe058b_20260906T141424Z.json
```

The comparison is against `git show 613f9bd17:docs/observability/r1_inference_ceiling.json`, which
names that same file in its own `run_output` field — confirmed before writing this. So the pair
(613f9bd17 artefact, this run) differs in the instrument alone, and the pair (this run, the
`c244b93a0` artefact now on `origin/main`) differs in the **book** alone. Together those two
comparisons decompose every number the earlier finding could not attribute.

Note the exposure the earlier finding left open has since closed by the other lane's own hand:
`c244b93a0` landed the regenerated artefact, so the page no longer publishes `+0.6127` on 213
supply points. That does not spend this measurement — the attribution question is untouched by it.

## The predictions, fixed now

**P1 — NOT ONE per-field count RISES.** Every `single_feature_ceilings[*].n` in this run is
**less than or equal to** the same field's `n` in the 613f9bd17 artefact:
`mean_recent_margin_rate` ≤ 213, `portfolio_premium_pct` ≤ 213, `unit_rate_gbp_per_mwh` ≤ 100,
`svt_rate_gbp_per_mwh` ≤ 69, `rate_vs_svt_pct` ≤ 69, `company_eac_kwh` ≤ 69,
`company_churn_estimate` ≤ 69, `resentment_score` ≤ 69, `perceived_bill_saving_gbp` ≤ 69,
`expected_term_margin_gbp` ≤ 56.

This is a **deduction, not a guess**, and I am stating the argument so the run can refute the
argument and not just the number. `observable_rows` buckets a household's legs into one vector, so
the set of households carrying field *f* is the image of the set of supply points carrying *f*
under `household_of`. A map cannot enlarge its own domain: `|image| ≤ |domain|`. **Re-keying can
therefore only fold counts down or leave them, never raise them.**

If P1 holds, the increases `69 → 146`, `100 → 164`, `69 → 164` are **the later book**, and folding
is excluded as their cause — which is exactly the disjunction the earlier finding refused to
resolve. If P1 is **refuted** — any count rises — then my reading of `observable_rows` is wrong,
there is a second mechanism in the keying change I have not found, and *that* is the finding.

**P2 — the household count falls to 149.** The `3851553ec` docstring records 213 supply points →
149 households on the book of that size. If `leg_fold_census` reports something other than
`213 → 149`, the docstring's own worked example is about a different file than I think it is.

**P3 — the pair rung is unmoved, to the last digit.** `best_pair` stays
`perceived_bill_saving_gbp × portfolio_premium_pct`, `n = 69`, `held_out = +0.6127`,
`in_sample = +0.1674`. Reasoning: all four decision-time fields were shown byte-identical across
the earlier comparison, the winner's intersection is 69 households, and `portfolio_premium_pct`
covers every household either way — so nothing in the winning cell's inputs can change. A move here
refutes the earlier finding's central mechanism (that decision-time fields were already
household-keyed) on the only test that isolates it.

**P4 — the p-value moves anyway.** The selection-corrected null shuffles traits across the WHOLE
book, and the book goes from 213 keys (82 of them legs with fabricated traits) to 149 households.
So `selection_corrected_verdict.p_value` will **not** be 0.0249, even though the observed figure is
unchanged. I predict it moves toward the new book's 0.0299 — i.e. lands in **0.02–0.05, still
`clears`**. This is the loosest prediction here and the one I would drop first.

**P5 — the full-coverage rung's p falls well below 0.8507.** The earlier finding's claim is that
this rung, and only this rung, carried the contamination. On the same book, re-keying alone must
therefore move it. I predict `full_power_selection.p_value < 0.70`. If it stays near 0.85, the
published causal story is wrong and the p-move seen earlier (0.8507 → 0.4328) was the book, not the
keying — which would be a second refutation of the same account in two days.

## The grading rule, fixed in advance

- Every prediction is graded in a finding, beside the result, whichever way it falls.
- **P1 is the one that decides the prescription.** If the increases are the book, then "coverage
  closes R1" survives as a prescription but its subject is the *world's logging*, not the
  instrument's keying — the fields grew because a later run wrote more account state, and that is
  something the world can be made to do more of on purpose. If the increases were folding, coverage
  was already there and only the reading was wrong, and the prescription would be spent.
- **No regenerated `docs/observability/r1_inference_ceiling.json` will be landed.** This run writes
  that path as a side effect and its contents describe a *superseded* book; the artefact at
  `origin/main` correctly describes the current one. The file is restored byte-for-byte after the
  run (md5 `d0127e6d08225ad5a12e4c192cf77bae`) and the numbers are carried in the finding instead.

## What this measurement CANNOT settle

It cannot say whether the ceiling is real, and it does not re-open that. It also cannot say the
*later* book's extra coverage is representative of anything: two consecutive draws of one
population at one base seed are not independent books, and a coverage increase between them is one
observation of a difference, not a rate. Whether account-state coverage keeps rising is a separate
question this run does not touch.
