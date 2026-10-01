**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# PRE-REGISTRATION — EP1's tenure horizon on the book's own all-cause exit frequency

Filed 2026-10-01 at `d8ae8c2e7`, before the change has run on any book. It serves
`docs/staging/SEAT_FINDING_THE_WORLD_DECIDES_A_RENEWAL_AT_ONE_ANNIVERSARY_IN_FIVE_SO_A_PER_RENEWAL_HAZARD_HAS_NO_AGREED_DENOMINATOR_2026-10-01.md`.

## What the thing is (said before it is measured)

H2 `tenure_expected` asks how long this customer stays. A tenure ends at ANY exit: a switch at
renewal, a switch mid-term, a home move. So the hazard it needs is the book's **all-cause annual
exit probability**, and NOT a per-renewal rate. Whatever the director answers about which
anniversaries are real decision points, that answer changes the renewal reading and not this one.
This is why the build does not wait on that answer.

- **Exposure** is account-years observed. Per billing account, it runs from the first settled month
  to the last, inclusive, divided by 12. It is truncated at each snapshot's cutoff, and read only
  from the company's own settled records.
- **Exits** are billing accounts in `ceased_billing_accounts` over the same window, whenever they
  ceased.
- **Hazard**: λ = exits / account-years is a rate. H2's annuity takes a per-YEAR departure
  probability (`retention^t`), and under a constant hazard that probability is `1 − exp(−λ)`. This
  is a unit conversion, not a picked constant.
- Blanks are named. No exposure gives `no_book_exposure`. Exposure with no exit gives
  `no_book_exits`, because a zero rate is no evidence of an infinite tenure. The first-renewal
  prior is still `None`, and nothing is shrunk toward a number.

The per-anniversary `BookRenewalRecord` stays published beside H2 as a diagnostic, and H2 no longer
reads it. `tools/clv_gap_selection.lifetime_level` must read the exit hazard on new snapshots, or it
publishes the renewal hazard as "the hazard EP1 used". That is the downstream consumer this change
breaks unless it is repaired in the same commit.

## Predictions, on the fresh `run_phase2b` pickled at `/tmp/ep1bk/run.pkl` (81977a312 world)

1. **Exits at the 2025 cutoff = 89**, matching the finding's cessation count (49 at an anniversary
   plus 40 off one). If the count is not 89, the two readings define "ceased" differently, and I
   say which.
2. **Exposure is 560–700 account-years.** That is the ~531 anniversaries passed plus a partial
   year per account. **λ is 0.13–0.16, and the annual probability is 0.12–0.15.** It is lower than
   the finding's back-of-envelope 0.17, because that figure divided by anniversaries and left out
   the partial years.
3. **The 2016 snapshot**: low confidence. I predict H2 is blank under `no_book_exits`, because no
   account ceased inside the acquisition year.
4. **Gap.** This is a one-variable arm. The same run artefact gets two substituted snapshot series,
   one from HEAD's code (per-anniversary hazard, ~0.09) and one from this change. The CLV gap
   strictly decreases from the HEAD arm, and stays above pass 20's 1.076 (which took the hazard to
   0.358). Spearman between belief and realised moves by at most ±0.02, because one pooled number
   per date carries no per-account ranking.

If (1) fails by more than a handful, the exit count is the defect, and it is fixed before anything
lands.

## RESULT, 2026-10-01, written beside the predictions and not over them

Counted with `observed_book_exits` on the pickled run at each year-end cutoff (script
`/tmp/se_ep1_measure.py`):

| cutoff | account-years | exits | rate | annual hazard | per-anniversary (HEAD's H2) |
|---|---|---|---|---|---|
| 2016 | 60.7 | 1 | 0.017 | 0.016 | 0/0/None (blank) |
| 2017 | 139.1 | 16 | 0.115 | 0.109 | 83/12/0.145 |
| 2019 | 270.1 | 50 | 0.185 | 0.169 | 215/28/0.130 |
| 2021 | 386.6 | 78 | 0.202 | 0.183 | 330/44/0.133 |
| 2025 | 606.0 | 89 | 0.147 | 0.137 | 531/49/0.092 |

1. **HELD.** There were 89 exits at 2025, the same as the finding's cessation count.
2. **HELD.** Exposure was 606 account-years, λ 0.147 and the annual probability 0.137.
3. **FAILED.** The 2016 snapshot is not blank. One account ceased inside the acquisition year, so
   H2 is valued on 1 exit over 61 account-years (hazard 0.016, tenure ~61 years). A hazard resting
   on one event is publishable only beside its n. It now has its n (`book_exits` on every
   snapshot), but no bound.
4. **FAILED, and the direction is the finding.** The one-variable arm takes run_output_latest
   (`b1b4c284e`, 69 graded rows) and recomputes H2 from each row's own margin, changing only the
   hazard. The hazards are counted on the pickled run, the same in both arms, so this is
   attributable but is not the ledger figure.

   | arm | gap | Spearman | \|b\|>\|t\| |
   |---|---|---|---|
   | published (0.05 belief) | 2.364 | +0.110 | 60/69 |
   | per-anniversary (HEAD) | 1.437 | +0.077 | 55/69 |
   | all-cause exit (this) | **1.558** | +0.096 | 54/69 |

   By belief year (mean absolute error, £): 2017 (n=51) is 464 per-anniversary against 532
   all-cause. 2016 (n=3) is 745 against 1117. Every later year IMPROVES: 2018 is 447 against 377,
   2019 552 against 395, 2020 417 against 283, 2021 1093 against 997, and 2022 766 against 696.
   The gap rises because 51 of 69 graded rows are 2017 beliefs. At that cutoff the all-cause
   hazard (0.109) sits BELOW the per-anniversary one (0.145): a one-year-old book's exposure is
   mostly first-year, in-term time when almost nobody leaves. A constant hazard averages that
   quiet time with the renewal spike.

**What this does and does not change.** The definition came first: a tenure ends at any exit. The
gap is a diagnostic and never a target (R12), so a worse gap is not a reason to choose the hazard
that scores better. The change lands. What the arm exposes is the next defect: **EP1's tenure model
assumes a constant hazard, and the book's exits depend on tenure.** The company can count that
dependence with no new observable: exits in tenure year k over exposure in tenure year k. That is
the handed-on build.
