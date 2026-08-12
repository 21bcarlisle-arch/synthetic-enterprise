# D22 built — the ageing headline counts both error directions

**Severity:** RECORDED · **Lane:** D_billing_metering

**Atom:** `D22_ageing_ordinal_is_one_directional` (D_billing_metering, epoch 3, L0 → L2)
**Date:** 2026-08-10 (worker tick)
**Origin:** `WORKER_FINDING_THE_AGEING_ORDINAL_HEADLINE_COUNTS_ONE_DIRECTION_2026-08-10.md`
(H27 Expert Hour #6, found by the `HEADLINE_DIRECTION_COVERAGE` class control)

## What was wrong

`gap_metric.ageing_gap` published `mean_bucket_displacement` as `GapResult.gap` — a mean
over the **truly-overdue** invoices alone. The ordinal term is the whole of what this
dimension adds over an error rate ("distinguish off-by-one from stone-blind, which an error
rate cannot"), and that claim held in one direction only.

`observed-with-evidence`, seeds 7/11/23 at n=4000: a company that dates every truly-overdue
invoice perfectly and dumps its **entire** truly-current book into `90+` scored **0.000000** —
bit-identical to a perfect dater, with 10,758 cases changed. So did one that over-aged every
current invoice by exactly one bucket. `overstated_arrears_rate` counted the direction; the
*severity* in that direction was invisible, so a 30-60 and a 90+ wrongful ageing — different
collections paths in a real supplier — arrived as the same number.

## The reshape, and the repair that was measured and rejected

    balanced_bucket_displacement = (mean_bucket_displacement           # truly-overdue
                                    + mean_overstatement_displacement) / 2   # truly-current

This is the shape `detection_measures` already uses (D11), in ordinal units, with D7's
denominator rule: each term on the population it is about.

The obvious alternative — average displacement over the **whole** population — also counts
both directions and was rejected on a measurement, not a preference. Its denominator counts
the truth's class balance, so it re-imports D6 Defect 2. With company behaviour held
*literally fixed* (every overdue invoice one bucket out, 5% of the current book over-aged by
two buckets) it swings **0.1089 → 0.5500** as arrears prevalence moves 1% → 50% — a factor of
**5.05**. The balanced form is flat at 0.5500 across the same sweep (**×1.00**). That shape is
pinned as `_MUTANT_headline_is_the_pooled_mean` and the prevalence property must reject it.

## Evidence

| | before | after |
|---|---|---|
| perfect dater → over-ageing degenerate (seeds 7/11/23) | 0.0 → 0.0 | 0.0 → **1.5** |
| off-by-one vs stone-blind over-ageing | 0.0 vs 0.0 | 0.5 vs 1.5 |
| published offline headline, seed 7 | 0.178744 | 0.095732 |
| prevalence sweep, company fixed | — | ×1.00 (pooled: ×5.05) |

* **The class control that found the debt measured the fix.** The register's second rule
  ("a debt entry that DOES tell its degenerate apart has been fixed and must be re-derived")
  fired on the stale entry the moment the reshape landed, before the entry was re-derived to
  `headline_counts_both_directions: True`. It is still differential — `detection_latency`
  remains the conditional-population entry — so it is not a register whose every row lands on
  one side.
* **R15 both ways, with mutants that are real historical shapes, not invented ones.**
  `_MUTANT_headline_is_the_overdue_term_only` *is* the scorer that shipped until today, and
  the direction property must reject it naming the over-ageing direction. In the pair's suite
  a `_pre_d22_ageing_scorer` context manager restores it so the register's lying-declaration,
  cover-claim-covering-nothing and unowned-hole mutations still have a genuinely
  one-directional dimension to fire on — **stronger** than before, when they reinstated the
  defect as a *declaration* over an already-blind scorer.
* **Vacuity widened** (the fail-open this reshape could have introduced): the headline is
  `None` if **either** truth class is empty — never the surviving half, which would silently
  restore the one-directional headline on exactly the populations where nobody could check it.
* **Non-comparability stamped at source.** Every gap-ledger entry before 2026-08-10 carries
  the truly-overdue-only figure. `ordinal_direction_caveat` now says in words that the two are
  different measurements and must not be quoted as one, and `format_ageing_summary` prints
  both halves beside the headline (the D7 anti-decay mechanism, extended).
* **Suites:** 259 green in `tests/tools/test_d7_ageing_measures.py` +
  `tests/tools/test_couple_w2_11_d5.py` (11 new/reshaped); 2,239 green across every suite
  touching the ageing dimension (live triad, billing, W2_11, the D6 characterization, the
  misapplication call-site register).

## Declared limit

The balanced headline cannot say **which** direction the displacement came from: a company one
bucket out on every overdue invoice and one over-ageing half its current book score alike.
Both terms are published beside it and interpolated into the caveat from the measurement.
Declared here rather than discovered by the next Hour.

## Open and registered, not fixed here

`background/live_payment_triad.py::_ATTRIBUTED_MEASURES` attributes the D8 remittance
counterfactual over `ageing.mean_bucket_displacement` and the two rates. The over-ageing
**severity** term did not exist when that list was written and now does. Whether the
ambiguous-remittance channel explains any of it is a D8 question this build declined to answer
on its owner's behalf — and adding a measure moves that pair's published `n_fully_attributed`
count. Same disposition D19 took for the belief dimension one atom over.
