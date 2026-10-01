**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# PRE-REGISTRATION — EP1's remaining over-valuation: the margin term or the lifetime term

Filed 2026-10-01 at `7e2503507`, before any per-row split has been computed. Claim id
`ep1-remaining-overvaluation-decomposed`.

## The population and the inputs (unchanged from the life-table measurement)

These are the 69 graded rows of `tools.couple_clv.measure` over
`docs/reports/run_output_latest.json`, with the book's records from `/tmp/ep1bk/run.pkl`. The
belief is the life-table arm of `/tmp/se_ep1_measure_lt.py`, at gap 1.275 with 52 of 69 rows
having |belief| > |realised|. Nothing in the company code changes for this measurement.

## What each side is (said before differencing)

- **Belief** B = m_b · L_b.
  - m_b is the **belief annual margin**. It is the H1 contract-term value divided by the one-year
    survival-discounted unit (`h1 / sdv(1, h, r, 1)`), exactly as the measurement script recovers it.
  - L_b is the **believed discounted remaining life-years**, `sdy(1, forward_hazards, r)`. That is
    the survival- and discount-weighted count of FORWARD years from the snapshot (31 Dec of the
    belief year). It is the factor H2 multiplies the margin by.
- **Realised** R is `net_margin_after_cost_to_serve_gbp` over the account's WHOLE life. Its
  tenure T_r is the years from the `acquisition_date` month to the last settled month, inclusive,
  over 12. The realised annual margin is m_r = R / T_r.
- **The split** is exact and order-free (Shapley over the two factors):
  B − R = (m_b − m_r)·(L_b + T_r)/2  [margin term]  +  (L_b − T_r)·(m_b + m_r)/2  [lifetime term].
  This is sign-safe for negative realised margins. The one-variable arms are reported beside it:
  margin swapped only (m_r·L_b) and lifetime swapped only (m_b·T_r).
- **The lifetime term is three things, and they are reported separately:**
  1. the **window**: T_r counts months BEFORE the snapshot, which L_b never covers (the declared
     truth-window caveat), so the remaining realised tenure T_rem from the snapshot is reported too;
  2. **discounting**: L_b is discounted and T_r is not, so L_b at r = 0 is reported;
  3. **selection on exit**: every graded row is a LEAVER, ceased by the end of 2025. A tenure
     belief that is right on average for everyone still over-states for the subset that left
     inside the window. The life table's own expectation of remaining tenure, CONDITIONAL on exit
     before the run's last settled month, is computed from the same forward hazards. Its gap to
     the unconditional L_b(r=0) is the part of the "over-valuation" that is the grading
     population's, not the belief's.

## Predictions (written before the numbers)

- **P1.** The lifetime term carries more than half of the summed signed error Σ(B − R) over the
  69 rows. *Confidence: moderate.*
- **P2.** The margin term is positive in sum (m_b > m_r on balance) and smaller than the lifetime
  term. *Confidence: low.* I have no reading of m_b against m_r at all.
- **P3.** Of the lifetime term, selection on exit (L_b(r=0) unconditional minus the conditional
  expectation) is larger than discounting and larger than the window. *Confidence: moderate.*
  If so, much of the residual 1.275 is the grading population, not a defect of the belief, and
  the next build is the HARNESS (grade survivors as censored) rather than H2.
- **P4.** Spearman on margin-swapped-only (m_r·L_b) is well above 0.10, and Spearman on
  lifetime-swapped-only (m_b·T_r) is also above 0.10. Both factors carry rank information, so
  neither swap alone reproduces the ranking. *Confidence: low.*

Refutation of any of these is recorded beside it in the result, not revised here.

## Addendum, filed after the split and before the follow-up (2026-10-01)

The split ran first, and its result is in the finding. The margin term dominates: m_b averages
£139 and m_r £55. `saas/clv_model.py` annualises as cumulative `net_of_all_costs_margin_gbp`
divided by `len(churn_risk[account])`, which is the count of renewal points, not elapsed years.

- **P5.** N/P (cumulative margin to the snapshot over the renewal-point count) reproduces m_b to
  within 1% on every decomposed row. *Confidence: moderate.* If it does not, I have the wrong
  mechanism.
- **P6.** On the 2017 rows the renewal count is smaller than the elapsed settled years. Dividing
  by elapsed years instead lowers mean m_b by at least 30%. *Confidence: low-moderate.*

## Second addendum: the two candidate fixes as one-variable arms (filed before they run)

The run so far established two opposing defects: the margin is divided by renewal points, and H2
double-applies survival. The fix arms on the true belief (66 rows, gap 1.173) are:
A = settled-years margin × L_b; B = m_b × untruncated discounted Σ S(t)/(1+r)^t; C = both.

- **P7.** A: the gap falls below 1.0 and Σ(b − t) turns negative, so the belief under-states once
  the margin is fixed alone. *Confidence: moderate.*
- **P8.** B: the gap rises above 1.173, because it adds life to an already over-stated margin.
  *Confidence: moderate-high.*
- **P9.** C: the gap is below 1.173 but above A. Spearman stays under 0.25 in all three, because
  neither fix adds per-account information. *Confidence: low.*

## Result (2026-10-01), graded against the predictions above

**The population changed before anything was split, and that is a finding in its own right.**
`/tmp/se_ep1_measure_lt.py` recovers the margin as `h1 / sdv(1, rec['hazard'], r, 1)`. H1 is
priced on the account's LATEST churn probability over its CONTRACT term, so that divisor is the
wrong one. The recovered margin is off by up to 7.1× on one row (mean £139 against a true £115).
The hazard side of that script is exact: H2 ÷ true margin equals `sdy(1, forward_hazards, r)`
to 0.0. So the measurement here uses the belief HEAD's code actually produces. Each snapshot was
rebuilt with `build_customer_value_view`, and `annual_margin_gbp` and H2 were read off it. That is
**66 rows** (the three 2016 rows have no life table) at **gap 1.173**, Spearman +0.097, with
45/66 rows having |b| > |t|. The 1.275 on 69 rows was a reconstruction, not the belief.

| arm (66 rows, g0 356.62) | gap | Spearman | \|b\|>\|t\| | Σ(b−t) £ |
|---|---|---|---|---|
| true life-table belief m_b·L_b | 1.173 | +0.097 | 45 | +2,908 |
| margin swapped only m_r·L_b | 0.534 | +0.917† | 18 | −7,476 |
| lifetime swapped only m_b·T_r | 1.233 | +0.359† | 49 | +11,811 |
| margin → book-mean m_r, L_b kept | 1.004 | +0.007 | 24 | −6,901 |
| A: margin ÷ settled years, L_b kept | 1.036 | +0.125 | 30 | −4,925 |
| B: m_b · untruncated Σ S(t)/(1+r)^t | 1.310 | +0.090 | 49 | +7,177 |
| C: A and B together | 1.066 | +0.122 | 37 | −2,421 |

† Not a skill. m_r = R/T_r, so this arm carries the realised value itself. The two swaps
attribute the error; neither is a predictor.

Shapley split: Σ(B−R) +2,908 = **margin +11,097** + **lifetime −8,190**. Σ|margin term| is
24,004 against Σ|lifetime term| 11,170. Of the 45 over-stating rows, the margin term is the
larger in **43**.

The lifetime term, chained and priced at (m_b+m_r)/2 (positive = belief over-states):
discounting −4,309; truncation at E[T] (labelled "convention" in the script) −11,669; selection on
exit +13,614; belief error on leavers +3,679; window (pre-snapshot months) −9,505.

- **P1 — REFUTED.** The lifetime term is net NEGATIVE (−8,190): on these rows the belief
  UNDER-states life. The margin term carries the whole over-statement and more.
- **P2 — CONFIRMED in sign, refuted in size.** m_b > m_r (£115 against £55 mean, medians 106
  against 58.5), and the margin term is the LARGER term, not the smaller.
- **P3 — CONFIRMED in ranking only.** Selection on exit (+13,614) is the largest step in the
  lifetime chain. But it is outweighed by three under-stating steps, so the residual is not the
  grading population's. The harness-first next build that P3 named does not follow.
- **P4 — ILL-POSED as written.** Both swapped arms carry truth (†). Measured directly,
  Spearman(m_b, m_r) = 0.12 and Spearman(L_b, T_r) = 0.23. Neither factor ranks.
- **P5 — CONFIRMED** against the true margin: N/P reproduces `annual_margin_gbp` on 66/66 rows
  (max deviation 0.0). P5 first read "refuted" because it was compared against the reconstructed
  margin. That was my error, corrected here.
- **P6 — CONFIRMED.** P = 1 renewal point on all 66 rows, against 1.67 settled years mean.
  Dividing by settled years lowers mean m_b by 41% (£115 → £68).
- **P7 — HALF-REFUTED.** Σ(b−t) does turn negative (−4,925), but the gap is 1.036, not below 1.0.
- **P8 — CONFIRMED** (1.310). **P9 — CONFIRMED** (C 1.066: between A and the belief; Spearman
  ≤ 0.125 everywhere).

Scripts (not landed, /tmp): `/tmp/ep1dec/{decompose,truebelief,denominator,decompose_true,check2,fixarms}.py`.

## Third addendum: the built arm C (filed before it runs)

Claim `ep1-margin-per-settled-year-and-untruncated-h2`. Both changes are now code:
`customer_value_view.settled_year_margins`, and `survival_discounted_value_by_year_gbp`
untruncated. The measurement rebuilds each snapshot with `build_customer_value_view` and reads
`annual_margin_gbp` and H2 off it, as the true-belief run did.

- **P10.** The built code reproduces arm C: 66 rows, gap 1.066 ± 0.002, Σ(b − t) −£2.4k ± £0.1k,
  37/66 over. *Confidence: high.* If it does not, the build and the arm do not define the same
  thing, and the gap is reported as a defect of one of them, not of the belief.

**P10 — CONFIRMED exactly.** Built code on the rebuilt snapshots: 66 rows, gap **1.066**,
Spearman +0.122, 37/66 over, Σ(b − t) **−£2,421**. Script `/tmp/ep1dec/built.py`. The ledger row
is not re-measured here; the next run's `couple_clv` reading is the real one.
