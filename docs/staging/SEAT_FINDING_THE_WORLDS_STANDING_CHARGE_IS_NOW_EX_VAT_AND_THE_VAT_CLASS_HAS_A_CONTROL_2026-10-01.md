**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The world's standing charge is now ex-VAT, and the VAT class has a control

Claim `close-the-vat-basis-class-in-the-world`. The results below are against
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_STORING_THE_WORLDS_STANDING_CHARGE_EX_VAT_MOVES_2026-10-01.md`,
which was written before either arm ran.

**Disposition of the draw's duplicate-work note.** The claim it saw "already held under this very
id" was this draw's own write. The holder was this session (pid 1797877), and no rival seat or
`surgical_land` was running. So there was nothing to take a disposition on.

## What was already on origin, and was not redone

- The switching reference is on one VAT basis: `b5ae7c3af` (`household_price_inc_vat`).
- The ToU sold rate is consumption-weighted: `e9b79073d`, with its run in
  `SEAT_FINDING_THE_SOLD_RATE_NOW_WEIGHTS_THE_TOU_DAY_...`. That was item (2) of this direction.
  It landed under another claim before this draw, so this claim did no work on it.

## (1) The standing charge: knowledge first, then the change

**Is it inc-VAT? Yes, and this is established, not inferred.** Ofgem's cap level model v1.31 (in the
commons cache, the same edition `tools/ofgem_cap_unit_rate_composition` reads) gives the standing
charge as the nil-consumption allowance, ex-VAT. Gas in October 2022 is 27.13p, and 27.13p × 1.05 =
28.49p, which is Ofgem's published inc-VAT figure to the penny. The world's 2022+ rows (46/53/61p,
28/29/31p) were the published inc-VAT numbers, and every reader adds them to `revenue_gbp`.

**What was changed:** both tables are re-read from the model, ex-VAT. Each figure is the
direct-debit sheet, the regional median per cap period, and the day-weighted mean per calendar year.
Two parts of this are carried as gaps:
- **2016–2018** are the model's back-cast to before the cap began in 2019. They are a notional cap
  level, not an observed market tariff.
- **2025** is not tabled and still clamps to 2024.

The pre-2022 "typical market averages" had no source, and they are gone. The landing is
`policy_costs.py`, under this claim.

**Results:** one default world per arm, same base, same script (`/var/tmp/se-sc-exvat/`).

| | Predicted | Measured | Verdict |
|---|---|---|---|
| P0 placebo | `n_customers` equal | 256 / 256; records 319,176 both; churned 89 both | **holds** |
| P1 | per year/fuel ratio = table ratio to 1e-3 | e.g. 2017 elec 0.7592 (18.98/25), 2020 gas 1.0236 (25.59/25), 2024 elec 0.9362 | **holds** on every row |
| P2 | SC revenue falls 8–16% | £106,129.54 → £95,124.07, **−10.4%** | **holds** |
| P3 | Δmargin within 0.75–1.25× ΔSC | Δmargin −£9,651.39 = **0.877×** ΔSC (−£11,005.47); Δrevenue 0.877× too | **holds** |
| P4 | the 8 accounts from 2023 that opened higher than the 53p fallback now open lower; the 20 from 2024–25 stay higher, about £1.24/month less | 8/8 now lower (median −£0.11); 20/20 still higher, median shift **−£1.24** | **holds** |
| P5 | every opening lower or equal | 227 lower, 3 equal, **17 higher** | **FAILS** |

**Correction, beside the claim.** The P5 miss is mine and sits in my own pre-registration table. The
Ofgem figure for gas in 2019 is *above* the old one (ratio 1.006), and 2020 gas is 1.024. I wrote
the 2019 ratio into the table and then predicted "all lower" anyway. The 17 accounts are exactly the
2019 gas cohort (+£0.04–0.05/month) and the 2020 gas cohort (+£0.18–0.19). Nothing else rose.

**The un-attributed 12% in P3.** The account population is identical across arms, yet revenue fell
by only 0.877 of the standing-charge fall. Something else added £1,356. The candidate is renewal
pricing reading the observed standing charge (`value_based_renewal._observed_standing_charge_gbp`):
a lower fixed recovery would raise the struck unit rate. That is **consistent with the result but
not established**. The one-variable test is to freeze the renewal path to old-arm SC observations.
*Correction, 2026-10-01: that candidate was unreachable. The default world runs `flat_rules` and never calls it (0 calls). The £1,356 is the portfolio premium (+£1,040.51) and the margin surcharge (+£320.63) pricing the lower realised margin into renewal unit rates; see `SEAT_FINDING_THE_12_PERCENT_IS_THE_COMPANY_PRICING_ITS_LOWER_MARGIN_BACK_INTO_RENEWAL_UNIT_RATES_2026-10-01.md`.*
DD review and balance books move by noise: increases 489 → 490, mean held credit £826.93 → £831.00.

**For the company figures this means:** about £11k of what the world booked as supplier revenue
over the run was VAT, plus unsourced level, and it is no longer counted as value created.

## (3) The class: one control, on origin at `78f1cc756`

`tests/architecture/test_a_price_crosses_vat_only_through_a_named_rate.py` has four legs:
- No price under `simulation/` or `company/` is multiplied or divided by a bare `1.05`, `1/1.05`
  or `(1 + 0.05)`.
- Every `(1 ± VAT)` factor names a sanctioned rate imported from its home. The sanctioned rates are
  `price_cap_enforcement.DOMESTIC_VAT_RATE`, `tariff_comparison.VAT_RATE_DOMESTIC` and
  `domain_invariants.vat_rate_for_segment`.
- The detector can fire, and the scan reaches real factors in both trees.
- The three homes agree.

At landing the census found 0 bare factors and 9 sanctioned ones across 7 modules. Three mutations
were run and each was reverted: a bare `* 1.05`, a local `_VAT = 0.05`, and a detector that never
fires. Each one turned its own leg red.

**What it does not catch, written down so that green is not over-read:**
- `x + x*0.05`
- a factor assembled in one statement and applied in another
- invoice VAT lines, which read the commons `uk_vat_rates` artefact

**Three homes for one 5% is still a debt.** The agreement leg stops them drifting into three
different answers, but it does not merge them. That merge is the next piece of the class.

## Still open

- ~~The 12% feedback in P3~~: attributed, see the correction under P3.
- ~~2025 standing-charge row~~: tabled from the model with its own run, see
  `done/SEAT_FINDING_THE_2025_STANDING_CHARGE_IS_TABLED_FROM_THE_CAP_MODEL_2026-10-01.md`.
- ~~Merge the three VAT-rate homes into one~~: landed `ed7b4666f`.
