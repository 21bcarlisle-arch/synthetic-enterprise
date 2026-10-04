**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** 2 · **Atom:** `W3_1b_intra_year_price_cap_granularity` — Lane 0 delivery

# The in-force 28AD grades a ToU tariff at its assumed split against the multi-register cap, and 15 of 27 ToU first terms sit above it

Claim `the-tou-first-bill-is-graded-against-the-cap-at-its-assumed-split`. Parent:
`WORKER_FINDING_THE_EAC_READ_ERROR_IS_UNBIASED_AND_WIDE_AND_THE_CAP_BINDS_A_TOU_TARIFF_AT_ITS_ASSUMED_SPLIT_2026-10-01.md`,
answer 2, which rested on the 2018 draft.

## The law, now in the commons

`docs/domain_artefact_library/regulatory/slc_28ad_multi_register_cap_test.md` carries the in-force
text: the consolidation to 18 July 2022, cross-checked against the April 2022 consolidation and
Ofgem's 27 August 2025 proposal, neither of which changes it. It confirms the draft and adds one
leg the draft reading missed.

- **The weighting is the tariff's Assumed Consumption Split**, never the household's realised one
  (28AD.34, .35). E7 is 42/58. Any other ToU tariff uses the supplier's declared historic split
  (28AD.36(b)).
- **A ToU tariff is graded against the MULTI-REGISTER benchmark** (28AD.4). The definition covers
  ToU rates "regardless of the metering equipment employed". **This is the leg the parent and the
  sold-rate finding both missed.** The multi-register unit-rate cap is 0.920–0.996 of the
  single-rate cap (median 0.951 over 2019–2025, ex-VAT, from Ofgem's cap model v1.31). The standing
  charges are equal to within 0.1p/day.
- **The cap binds only Evergreen, Deemed and default fixed-term contracts.** A fixed tariff the
  customer chose is not capped.

## Which comparators are wrong

| site | what it grades | against | verdict |
|---|---|---|---|
| the five ToU first-bill rows in `SEAT_FINDING_THE_SOLD_RATE_NOW_WEIGHTS_THE_TOU_DAY_..._2026-10-01.md` | the household's **realised** weighted rate | **single-rate** cap | **wrong on both legs** |
| `company/pricing/renewal_rate_chain.cap_ceiling_ex_vat` (writer 4, LIVE) | the flat strike, then split by `company/pricing/tou_desk` into a pair that is revenue-neutral at 30/70 | **single-rate** cap | **wrong for every ToU-eligible term.** The split is right, because the pair at its assumed split equals the flat strike. The benchmark is wrong. It fails open by up to 8%. |
| `company/compliance/domain_invariants.check_sold_unit_rate_within_cap` | a struck rate, with no metering arrangement argument | single-rate cap | **right for single-register only.** It cannot express the multi-register test. It has no production caller (tests only), so it moves nothing today. |
| `simulation/price_cap_enforcement.binding_cap_unit_rate_*` → `simulation/svt_rates` | the world's SVT, which a ToU SVT account is split from | single-rate cap | **the world prices a ToU SVT at the single-rate cap.** That is a fidelity defect, because a real supplier's multi-register default sits at the multi-register cap. |

## Measured at real inputs

Source: the 27 ToU accounts in `/var/tmp/se-touweight-run/rows.json` (origin/main `649112975`).

The assumed-split rate is the flat strike, recovered as `old × 14/11`. That follows the parent's
own correction; the `flat` field in that file is the uncorrected instrument and reads 1.500 on
weekend starts. The ceilings:
- single-rate: the published inc-VAT cap ÷ 1.05;
- multi-register: the single-rate ceiling × the model's MR ÷ 1R ratio for that window.

| test | above the cap ×1.001 |
|---|---|
| realised rate vs single-rate cap (what was reported) | 5 of 27 |
| assumed split vs single-rate cap | 0 of 27 |
| **assumed split vs multi-register cap (the in-force test)** | **15 of 27**, by +1.2% to +7.6% |

All five of the reported rows are in the 15. They were flagged for the wrong reason, and the
reported test missed the other 10. Eleven of the 15 sit exactly at the single-rate ceiling: the
SVT accounts, plus fixed terms that writer 4 clamped. The other four (2021-0044, 2021-0212,
2024-0349, 2025-0041) were struck 1–4% under the single-rate cap and 1–5% over the multi-register
one.

**Correction, beside the claim.** The parent says the five rows "are not breaches by that fact".
That is true of the fact cited (the realised split). It is not true of the five, because all of
them breach on the in-force test.

## Pre-registered, NOT done here: the one-variable repair

The variable is the benchmark in writer 4's ceiling, for a term `tou_desk` will sell as ToU. It
moves from single-rate to multi-register; the split, the weighting and every other writer are
unchanged.

It needs a multi-register cap series in a commons JSON artefact, read independently by
`company/pricing/ofgem_price_cap`. The `.md` table above is not something code may read.

Predictions, written before any run:
- **P1.** Non-ToU accounts move by 0 (1e-9).
- **P2.** On the same seed, ToU first terms above the multi-register ceiling ×1.001 go from 15 to
  0, unless they are SVT.
- **P3.** The ToU fixed terms that writer 4 clamps fall by the window's MR ÷ 1R, between 0.92 and
  0.996.
- **P4.** The SVT ToU accounts do not move. That is a WORLD change (`svt_rates`) and a separate
  variable, owned by the world lane and decided blind to company results.

**Open, for the practitioner side.** The company clamps chosen fixed products at the cap. 28AD does
not bind them (point 4 above), so the clamp is the company's own reading. It is over-restrictive,
not unlawful. Whether a real supplier holds a fixed ToU tariff to the default cap is a commercial
question this text cannot answer.

## Graded, 2026-10-01 (claim `land-the-in-force-28ad-and-repair-writer-4s-tou-benchmark`)

**The repair.** `docs/domain_artefact_library/regulatory/ofgem_cap_multi_register_unit_rates.json`
holds the series, generated by `tools.ofgem_cap_unit_rate_composition --multi-register`. It
reproduces the table in the commons `.md` to the hundredth. `company/pricing/ofgem_price_cap.
get_multi_register_cap_unit_rate_for_date` takes the single-rate ceiling (EPG included) and scales it
by the period's MR ÷ 1R ratio. Writer 4 uses that ceiling for any electricity term where
`tou_desk.offers_tou(customer)`, and `tou_desk`'s offer reads the same predicate. Control:
`tests/company/pricing/test_a_tou_term_is_graded_against_the_multi_register_cap.py`, mutation-proven
(dropping the ToU branch reds 2 legs; ratio forced to 1 reds 3).

**The run.** Default world, two processes from one tree. The base arm patches the chain's
`offers_tou` to `False`, which is exactly the old single-rate rule. Inputs: 3,236 chain calls per
arm, identical keys. Artefacts are in `/var/tmp/se-28ad-mr/`. The baseline reproduces the 15
named above.

| | prediction | result |
|---|---|---|
| **P1** | non-ToU accounts move by 0 | **REFUTED, narrowly.** 10 of 2,882 non-ToU calls moved. All 10 are **SVT** segments with term index ≥ 1 and an identical struck rate, all in 2022, moving both ways by ≤ 0.9%. The channel is writer 1's portfolio premium: it learns from the **book-wide** realised margin, and that margin moved when the ToU terms got cheaper. The prediction treated accounts as independent. They are coupled through the portfolio history. No non-SVT non-ToU call moved. |
| **P2** | ToU first terms above the MR ceiling ×1.001 go 15 → 0, except SVT | **HELD.** 15 → 8, and all 8 are SVT (the 7 fixed ones are now at or under the MR ceiling). |
| **P3** | ToU fixed terms writer 4 clamps fall by the window's MR ÷ 1R | **HELD, exactly**, on all 4 terms clamped in base (0.9292, 0.9372 ×2, 0.9571; diff < 1e-9). Ten more ToU fixed terms lay between the two ceilings. They fell by less, down to the MR ceiling: the four named above, plus renewals. |
| **P4** | SVT ToU accounts do not move | **HELD for the benchmark, REFUTED as worded.** The ceiling never touches an SVT term (`CAPPED_TARIFF_TYPES = ("fixed",)`), and every SVT ToU first month is byte-identical. But 5 of 299 SVT ToU calls moved, through the same portfolio-premium channel as P1. |

**Correction, beside the claim.** P1 and P4 assumed one account's ceiling could not reach another
account's rate. Writer 1 makes that false: every renewal from index 1 is priced partly off the whole
book's margin. So a "one-variable" change to the ToU benchmark is one variable at the call it
changes, and a small book-wide perturbation after that.

**Open, not established here (the world lane's, and the company's next question):**
- The 8 SVT ToU first terms still sit above the MR ceiling. That is `simulation/svt_rates` pricing a
  ToU SVT at the single-rate cap, a world fidelity question, untouched as directed.
- Writer 1 moves SVT segment rates, and writer 4 never clamps an SVT term. One SVT ToU call priced
  in December 2022 contracted at 606 £/MWh ex-VAT. That is above the EPG ceiling in force. Whether
  this chain output is what an SVT account is actually billed was **not checked here**. If it is,
  the company's SVT has no cap check at all.
