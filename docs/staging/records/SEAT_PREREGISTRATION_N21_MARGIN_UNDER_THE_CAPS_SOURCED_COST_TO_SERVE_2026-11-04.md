**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** none — claim `the-company-is-charged-its-real-cost-to-serve`

# Pre-registration: under the cap's sourced cost to serve, N21's margin on the a6b7a0fd47 book falls from 15.50% to about 9.7% (2026-11-04)

Written before `saas/cost_to_serve.py` changed. The charge is defined in
`docs/market_research/the_caps_operating_debt_and_industry_allowance_per_cap_period.md` §3.

**Quantity.** The same as N21's: Σ `net_margin_after_cost_to_serve_gbp` over Σ settlement revenue, on the a6b7a0fd47 book
(`docs/reports/run_output_a6b7a0fd47_20261104T173649Z.json`). It is a contribution, not EBIT.

**How the prediction was made.**
- Every leg-month present in `years[y].per_customer_monthly` was priced at the period's charge over 12 for its fuel.
  SME and I&C stay flat.
- The flat £55 priced the same way gives £245,943, against the book's actual £240,607. Leg-months over-count partial
  months by about 2%.
- So the actual cost to serve was scaled by the ratio, new over flat: ×1.859.

**Prediction.**
1. Portfolio cost to serve: £240,607 → **about £447k** (band £420k–£475k).
2. Margin: 15.50% → **9.67%** (band 9.2%–10.2%).
3. By year, the multiple rises from about 1.5× (2016) to about 2.2× (2024–25). The 2017 SMNCC and the CPIH
   indexing drive it.

**Falsifiers.**
- A recomputed margin outside 9.2–10.2% means the leg-month proxy is wrong about how the module counts days.
- An unchanged figure means the date never reached the charge.

**How it is graded.**
- The run JSON carries no settlement records, so the changed module cannot be run over this book.
- The grade is the next fresh book.
- Until then the offline repricing above is the only number, and it is labelled that way wherever it is printed.

## Re-based before the grading book exists (2026-11-05 00:43Z, worker)

**Why a re-base.** The grading book is `longjob-fresh-run-fd91027799` at origin fd91027799. It was launched at 00:40Z
and is still queued, and nothing of it has been read. The book before it, 5200cd6239, already moved off a6b7a0fd47
while still on the flat £55: revenue £3,187,582, cost to serve £241,774, margin **15.85%**. So 15.50% is no longer
the baseline the grading book is measured from.

**What else changes from 5200cd6239 to fd91027799**, so the delta cannot be attributed to the charge alone:
- the renewal desk and the value-based arm read the new charge;
- the arrears engine;
- the DD level collection book;
- household segments.

**Prediction on the fd91027799 book.** The same ×1.859 repricing, applied to 5200cd6239's cost to serve:
1. Cost to serve **about £449k** (band £420k–£480k).
2. Margin 15.85% → **about 9.3%** (band 8.8%–9.9%), if revenue stays within ±3% of £3.19M.

**Falsifiers.**
- A margin above 9.9% with cost to serve in its band means revenue moved. The renewal desk pricing to the higher
  charge is the first suspect.
- A cost to serve outside its band refutes the leg-month proxy, as in the original falsifier.

## Graded on the fd91027799 book (2026-11-05 02:30Z)

**Book.** `docs/reports/run_output_fd91027799_20261105T004022Z.json`, origin fd91027799, no imports off commit.
`/var/tmp/n21-gap6/grade.py` computes Σ `net_margin_after_cost_to_serve_gbp` over Σ settlement revenue; it reads
15.50% on a6b7a0fd47 and 15.85% on 5200cd6239.

| | a6b7a0fd47 | 5200cd6239 (flat £55) | **fd91027799 (the cap's charge)** | Predicted (re-based) |
|---|---|---|---|---|
| Settlement revenue | £3,540,583 | £3,187,582 | **£3,171,687** | within ±3% of £3.19M |
| Cost to serve | £240,607 | £241,774 | **£449,258** | about £449k (£420k–£480k) |
| Contribution after cost to serve | £548,926 | £505,120 | **£294,859** | |
| Margin | 15.50% | 15.85% | **9.30%** | about 9.3% (8.8%–9.9%) |

- **Prediction 1 held.** Cost to serve is £449,258. The leg-month proxy was right to within 0.1%.
- **Prediction 2 held,** re-based: 9.30%, inside the band. Against the original a6b7a0fd47 band (9.2–10.2%) it
  is also inside.
- **Revenue moved −0.5%.** The renewal desk reading the higher charge did not visibly move pricing.
- **Prediction 3, ungraded.** The run JSON carries no cost to serve per year, only per book and per customer
  lifetime, so the 1.5× → 2.2× multiple cannot be read from it.
- **The original "15.50% → 9.67%" baseline.** It was overtaken by the 5200cd6239 book before any grade existed. The
  re-base is filed and landed (b5b1129a6) before this book was read.
