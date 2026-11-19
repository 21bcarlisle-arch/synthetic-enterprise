**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# D48 on the 8a300fa561 book: billed equals metered on every read; only estimates carry a gap, and the company's gas shape is more seasonal than the world's (2026-11-18)

**Source.** `python3 -m tools.couple_d48_billing_gap --book docs/reports/run_output_8a300fa561_20261116T031305Z.json --write-ledger`.
This is harness code that holds the grader's `true_consumption_kwh` beside the bills and never imports into `company/`.
The rows are in `docs/observability/coupled_gap_ledger.json` under W2_30 and W1_14.

**Pre-registered before any split was computed** (`/tmp/d48/PREREG.md`, quoted in the commit):
- P1. Estimated bills carry the largest absolute gap; actual and smart are about 0. **Held.**
- P2. Within estimates, gas has the larger mean gap, and winter gas exceeds summer gas. **Held.**
- P3. Annual billed and metered kWh agree within 1% in every year. **Refuted.** See the third table.

**Billed minus metered per account-month, by read type.** Intervals are 95%, account-clustered bootstrap.

| read type | account-months | accounts | mean \|billed − metered\| kWh | mean signed kWh |
|---|---:|---:|---:|---:|
| actual (traditional) | 8,205 | 859 | 0.0 | 0.0 |
| smart | 6,325 | 221 | 0.0 | 0.0 |
| prepayment, actual read | 2,166 | 163 | 0.0 | 0.0 |
| prepayment, estimated read | 4,361 | 149 | 0.0 | 0.0 |
| **estimated** | 32,538 | 1,026 | **93.4** [85.3, 101.3] | +0.06 [−2.2, 2.5] |
| estimated gas, winter | 6,068 | 431 | 192.8 | **+112.4** |
| estimated gas, summer | 8,456 | 445 | 113.5 | **−83.1** |
| estimated electricity, winter | 7,524 | 519 | 58.9 | −27.9 |
| estimated electricity, summer | 10,490 | 542 | 44.5 | +22.2 |

**W2_30 ↔ D48: the gap is measured.** The belief is the company's published monthly share of annual use, the
one its unread-month estimate spreads on. The truth is each account-year's metered monthly shares. The
no-skill is a share by days.

| | gap | 95% interval | account-years | winter share, belief − truth | summer share, belief − truth |
|---|---:|---|---:|---:|---:|
| pooled | 0.386 | | 3,278 | | |
| gas | **0.329** | [0.320, 0.339] | 1,453 | **+0.0121** a month | **−0.0086** a month |
| electricity | 0.514 | [0.479, 0.549] | 1,825 | −0.0007 (n.s.) | +0.0005 (n.s.) |

The shape is worth having: it removes two thirds of a flat spread's gas error. But it is biased. The published
gas profile puts about 1.2 points more of the year into each winter month than the world's homes use. The
gas estimates follow suit: they over-bill winter by 112 kWh a month and under-bill summer by 83.

**I cannot yet say which side that bias belongs to.** *[Answered 2026-11-19: the side is the WORLD. Xoserve's published seasonal-normal ALP for domestic band 1 agrees with the proxy: DJF within ±1.5 points, Jan/Jul 7.8–9.9 against the proxy's 7.32. The world's 70/30 fallback reads about 5.0. See `docs/staging/records/SEAT_PREREG_D48_THE_GAS_ESTIMATE_SHAPE_AGAINST_XOSERVE_ALP_2026-11-19.md` and the W2_30 fallback finding.]*
- *World too flat.* The published shares are DESNZ actual-weather national domestic gas (January 17%, July 2.3%).
  A world whose gas has too large a summer base, or too weak a heating response, would read this way.
  N13 and N17 found this world's year too smooth before.
- *Proxy too peaked.* The shares are 2023–2025, the post-crisis years, laid over 2016–2025. They are also
  national, while the book has its own mix of regions and fabrics.
- One-variable test, not yet run: recompute the truth shares on the subset of premises settled on
  `fabric_physics` against the `legacy` fallback. If only the fallback is flat, the side is the world.

**W1_14 ↔ D48: the gap is undefined.** The company's estimate is seasonal-normal and "holds no weather feed for
billing" (`company/billing/unread_month_estimate.py`). There is no weather belief to grade, so any ratio would be
1.0 by construction, and the row keeps `gap: null` with that reason. The triad gate still holds W1_14, now for a
missing company capability rather than a missing measurement. The row records what was measured: the
year-specific part of the true shape is 0.0072 of annual use a month for gas and 0.0022 for electricity. That is
about half the gas shape error (0.0132). It is the most a weather-corrected estimate could recover.

**Annual billed against metered (P3, refuted).** Most years agree within 1.5%. The exceptions are 2016 gas
(−5.1%) and 2025 electricity (−3.3%), both partial years where open estimate runs straddle the book's ends, and
2022 (+2.1% electricity, +3.2% gas). The 2022 over-billing fits estimates built on pre-crisis use, while the
world's households cut back. These are timing residuals of estimated runs, which a read later trues up.
They are not N17.

**N17.** Its gap is on the **world** side. N17's pairs are actual and prepayment reads, and those bill exactly
what was metered. A dated note is appended to the N17 finding.

**What did not change.** The W2_36 ↔ D48 row and `tools/couple_w2_36_d48.py` from 2026-11-08 are still
uncommitted on the shared tree. That runner writes null W2_30 and W1_14 rows, and running it again would
overwrite these. They were not landed here. Whoever lands it must drop its `UNMEASURED_PAIRS` block.

**Landed 2026-11-19 by the delivery lane, after the executor's owner process died.** The executor's
tool, test and W2_30/W1_14 rows land with the 2026-11-08 W2_36 runner and its row. The runner's
`UNMEASURED_PAIRS` block is dropped, so running it again leaves these rows alone. *[Correction, 2026-11-19, delivery seat: this was
false when written. aca12f3a5 landed the W2_30 and W1_14 rows only. The W2_36 runner and its row stayed
untracked in the shared tree. They land in the commit that carries this correction (subject "W2_36 <-> D48:
..."; `git log -1 -- tools/couple_w2_36_d48.py`). That commit re-measures the row on the 6af7fd0bfd book: gap
0.290 [0.243, 0.342], gas 0.255, electricity 0.407. The rerun leaves W2_30 and W1_14 byte-equal, and
`tests/tools/test_couple_w2_36_d48.py` asserts that.]* Before landing, I re-split the
book with my own script. It gives the same counts: 32,538 estimated account-months, of which 18,014 are electricity
and 14,524 gas. It also gives 0.0 kWh on every actual, smart and prepayment bill. One more cut was pre-registered
before running (`/tmp/d48/PREDICTION.txt`). Signed error on traditional estimated bills is split into three sums of
squares: calendar month (shape against the estimator's profile), year-month common shock (weather and other
shocks), and the household residual.

| fuel | n | calendar month | year-month common | household |
|---|---:|---:|---:|---:|
| electricity | 17,744 | 0.041 | 0.011 | 0.949 |
| gas | 14,102 | 0.316 | 0.258 | 0.426 |

Against the predictions: P1 (the residual is over 50% for both fuels) is **refuted for gas**. P2 (for gas, the
year-month share exceeds the calendar-month share) is **refuted**. P3 (the electricity residual is over 70%) **held**.
For gas, the shape term is the largest systematic part of the error. That agrees with the W2_30 70/30-fallback
finding. W1_14 stays held by the triad gate: its gap is undefined until the company has a weather belief to grade.

**How the ledger lands.** The rows are in the shared tree's `coupled_gap_ledger.json`, which the next publish carries
with its proof door. A commit naming the ledger selects ~4,300 s of simulation tests against the gate's 3,600 s cap,
so it cannot land by the ordinary route. Until that publish, `origin` holds this tool and finding but not the rows.
