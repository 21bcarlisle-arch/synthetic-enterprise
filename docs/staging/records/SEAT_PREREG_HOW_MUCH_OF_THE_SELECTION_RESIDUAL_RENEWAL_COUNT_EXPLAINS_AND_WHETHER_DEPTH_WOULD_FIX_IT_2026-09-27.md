**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`
**Class:** `measurements_that_mirror`

# Pre-registration: how much of the selection residual renewal count explains, and whether a deeper book would let selection be measured at all

**Written before any of the numbers below was computed.** The director's ask, verbatim
(2026-09-26 09:29): *"how much of the residual variance is explained by renewal count, and tell me
whether a deeper book would let selection be measured at all"*. Root cause for
`SEAT_FINDING_THE_SERVED_SELECTION_SIGN_DOES_NOT_REPRODUCE_AT_HEAD_AND_THE_DECISION_FINGERPRINT_DOES_NOT_DETERMINE_THE_RESIDUAL_2026-09-26.md`.

**Subject artefact, no new run:** `/var/tmp/se-floor18-head-20260925/shards/folded18_head_20260925.json`
— 18 seeds, all naming producing commit `ba9bc673309bad9d46478cee3f1954aae5e066a8`, world digest
`39a192ce04c1eda8`, clock `settled-realised`, `redraw_key=elasticity`, `mode=all`.

## What I looked at before writing this, so the predictions are not cheating

The shard's SCHEMA, not its answers: the per-seed field list, that `scored_decisions` holds
`{account, term_start, believed_p_retain, retained}`, that the per-seed decision counts are 121 or
122, that `billing_accounts_settled_in_window` is 164 in every seed, that four distinct
`priced_decision_fingerprint` values occur, and the already-published family spread
(mean **+£169.60**, sd **£2,311.64**, sem **£544.86**, min −£4,317.39, max +£1,548.26).
Account ids are of three visible shapes: `C<n>`, `SYN-<year>-<n>`, `PROS-<year>-<n>`.

## Say what the thing is, first — "renewal count" has three readings and they answer differently

The ask names one phrase; the artefact supports three quantities, and the cause split must follow
the definition, never the reverse.

* **D1 — decisions per seed.** How many priced renewal decisions the seed scored at all. A
  SEED-level scalar. Already known to be 121 or 122, i.e. all but constant.
* **D2 — depth per account (the BOOK's property).** For one account, how many priced renewal
  decisions it faces across the 2016–2025 window. Near-identical in every seed, because the term
  calendar is not what the elasticity re-draw moves. **This is the quantity the director's "few
  accounts have enough renewals" hypothesis is about.**
* **D3 — renewals SURVIVED (the compounding property).** For one account in one seed, how many
  consecutive `retained: true` decisions it strings together before it leaves. This is what a
  pricing choice needs in order to compound, and it is the only one of the three that the
  elasticity re-draw moves freely.

**The residual** here is not a regression residual: it is the per-seed `selection_gbp`
(`value_advantage_gbp − level_advantage_gbp`) and its seed-to-seed dispersion across the 18. That
dispersion IS what stopped the sign being stateable, so its variance is the thing to decompose.

## The regressor list, fixed here so the multiple-comparison count is not chosen after the fact

Eleven seed-level regressors, no others, no transformations beyond those named:

| # | Regressor | Reading |
|---|---|---|
| X1 | `len(scored_decisions)` | D1 |
| X2 | distinct accounts appearing in `scored_decisions` | D1 |
| X3 | count of `retained: true` decisions | D3 |
| X4 | retained SHARE of decisions | D3 |
| X5 | mean over accounts of that account's decision count | D2 |
| X6 | count of accounts with ≥ 5 decisions | D2 |
| X7 | count of accounts whose LONGEST retained streak is ≥ 3 | D3 |
| X8 | mean over accounts of longest retained streak | D3 |
| X9 | total retained streak length summed over accounts | D3 |
| X10 | mean `believed_p_retain` over decisions | belief, not count — the control arm for X3/X4 |
| X11 | `discrimination_auc` | the instrument's own scored field |

and, separately from the eleven, a **concentration arm**: the per-seed retention indicator of each
`C<n>` account (the handful of non-synthetic, presumably largest, accounts), one regressor each.

**Bound and multiplicity, both fixed now.** Every R² is reported with its exact 90% interval from
the F distribution at n=18, df=(1,16). A permutation test shuffles `selection_gbp` 20,000 times and
reports the null distribution of the MAXIMUM R² over the eleven, so the headline is graded against
the right null and not against a single-regressor null.

## Predictions

| # | Question | Prediction |
|---|---|---|
| P1 | R² of X1 (decisions per seed) on `selection_gbp` | **< 0.05** — the regressor is all but constant, so it cannot carry anything |
| P2 | Median D2 depth per account, and share of accounts with ≥ 5 priced renewals | **median ≤ 3**, **share ≥5 renewals < 20%** — the director's "too shallow to compound" picture is right about the BOOK |
| P3 | Best R² among the D3 regressors (X3, X4, X7, X8, X9) | **in [0.05, 0.40)** — real but a minority, and not enough to call a cause |
| P4 | Does the 90% interval on that best D3 R² exclude zero? | **No** — at n=18 an R² needs to clear roughly 0.20 before its interval clears zero, and I do not expect a clean clear |
| P5 | Permutation p-value of max R² over X1–X11 | **> 0.05** — no single renewal-count statistic survives its own multiplicity |
| P6 | Best single `C<n>` retention indicator vs best renewal-count regressor | **the C-account indicator wins, R² > 0.25** — concentration, not depth, is what moves £6,000 between two runs of the same decisions |
| P7 | Share of total variance lying BETWEEN the four fingerprint groups | **< 0.30** — re-derivation of the published "same decisions, different residuals"; a control on the harness, not a new claim |
| P8 | Can "would a deeper book let selection be measured" be answered from this artefact? | **No.** One book depth was run (164 settled accounts), so depth has no variance to regress against. The scaling argument — seeds needed ∝ (sd/\|mean\|)², and sd/\|mean\| ∝ 1/√k for a k-fold deeper book **only if per-account contributions are i.i.d.** — is exactly the assumption P6 tests. If P6 holds, the i.i.d. premise fails and depth does NOT buy √k. |

**P6 is the prediction that can cost something.** If it holds, the director's hypothesis is right
that luck dominates and wrong about the remedy: deepening a book of small households would leave
the variance where it is, because the variance lives in a few large accounts' coin-flips. If P6
fails and a D3 regressor wins instead, depth IS the lever and the remedy is book growth.

## What done means

A fraction of variance with the interval eighteen seeds earns, for each reading of "renewal count"
separately; or a refusal that names the per-run field that would have to be recorded instead.
Either outcome lands with the predictions above kept beside it, right or wrong.
