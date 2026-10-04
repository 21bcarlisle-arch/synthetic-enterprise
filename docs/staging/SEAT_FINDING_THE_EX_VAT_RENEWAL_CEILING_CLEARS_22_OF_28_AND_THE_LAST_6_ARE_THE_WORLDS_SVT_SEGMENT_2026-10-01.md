**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** 2 · **Atom:** `W3_1b_intra_year_price_cap_granularity` — Lane 0 delivery

# The ex-VAT renewal ceiling clears 22 of the 28, and the last 6 are the world's SVT segment

Claim `ceiling-the-renewal-strike-at-the-ex-vat-cap`. This records results against
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_EX_VAT_RENEWAL_CEILING_MOVES_IN_THE_BOOK_2026-10-01.md`,
which was filed and landed before the run finished.

## What changed

`company/pricing/renewal_rate_chain.cap_ceiling_ex_vat` is the published cap divided by
`1 + tariff_comparison.VAT_RATE_DOMESTIC`. The single `cap_ceiling` site now reads it. That site
feeds both writer 4's clamp and the value arm's `max_offered_rate_gbp_per_mwh`. The new control is
`test_a_strike_once_VAT_is_added_never_exceeds_the_PUBLISHED_cap`. It recomputes the ceiling from
the published figure, not from the helper, and drives both arms. With the division dropped, the
control reds.

## The measurement: one variable

The baseline is the same world as the parent finding, run at `7c872f2d0`. Its rows are in
`/var/tmp/se-dd-books-rate-sold/rows28.json`. The new run is `7c872f2d0` plus only this file's
change, in the extract `/var/tmp/se-exvat` using the same script (`measure_exvat.py`). Rows are in
`/var/tmp/se-exvat/rows.json`, and the comparison script is `compare.py` in the same directory.

| | baseline | ex-VAT ceiling |
|---|---|---|
| accounts priced (N) | 120 | 120 |
| first-month rate above the ex-VAT cap | **28** | **6** |
| above the inc-VAT cap | 0 | 0 |

**The fixed 22.** Each now sits at sold ÷ inc-VAT cap = **0.9524**, which is 1/1.05, and its DD
opening ratio is 1.0000. They include PROS-2023-0014g, the EPG-window gas account the parent
finding used to identify the writer: 103.2 → 98.29. All 4 of the parent's "in-between" strikes
are among them.

**The 6 left.** They are PROS-2019-0024, PROS-2020-0132, PROS-2021-0168, PROS-2021-0279,
PROS-2022-0063 and PROS-2024-0294. **All six are electricity, all six have customer `tariff_type ==
"svt"`, and all six are sold at exactly the published inc-VAT Ofgem cap** (sold ÷ cap = 1.0000).
That is `simulation/renewals.py`'s SVT-origin first stint. It is electricity-only, and through
`simulation/svt_product.build_svt_schedule` it writes `svt_rates`' inc-VAT rate into
`unit_rate_gbp_per_mwh`. `simulation/settlement.py` bills that field as ex-VAT revenue and applies
no cap clamp to terms. The world's `hedged_settlement` clamp, fixed on 2026-08-25, covers only
deemed periods.

## Pre-registration verdict

- **H1 (0 of N above the ex-VAT cap): REFUTED, 6 of 120.** This is the branch the pre-registration
  named: another writer puts an inc-VAT rate into the strike. It is the world's SVT segment, and the
  parent finding left that unmeasured. Its tie-breaking account, PROS-2023-0014g, was gas. So the
  parent's "the writer is the company's" was true of 22 accounts and false of 6.
- **The 24 at the inc-VAT cap move to 0.9524: HOLDS for 18 of 24.** The other 6 are the SVT
  accounts above, which this change cannot reach.
- **The 4 in-between strikes clamp to the ex-VAT cap: HOLDS, 4 of 4.**
- **No more than 5 of the 88 lawful first terms move: HOLDS, 3 moved.** The three are PROS-2021-0383,
  PROS-2024-0256 and PROS-2024-0263. None crossed the ex-VAT cap. I cannot yet say why a first term
  moved. One possibility is book-level feedback through the portfolio premium, because the change
  moves renewal revenue and the premium reads settled margin. That is unmeasured.
- **N stays 120 ± 3: HOLDS, 120.**

## The world's side, read and NOT changed (the item's instruction)

Unlike the company's renewal desk, the world is allowed its own reading of the cap.
`svt_rates` declares its figure inc-VAT on purpose, because a downstream reader differences it
against bills. But `unit_rate_gbp_per_mwh` is the field settlement bills as ex-VAT revenue. So
an SVT household's unit revenue is 5% high, and so is every reader that grosses it up again: the DD
opening, `experienced_bill_shock._inc_vat`, and the bill. That defect is in the world's own
arithmetic, not in a reading. The likely fix is to write `rate / (1 + DOMESTIC_VAT_RATE)` into
`unit_rate_gbp_per_mwh` and the household-charged leg, using `price_cap_enforcement`'s own
constant, and to leave `svt_rates` inc-VAT as it is. It touches every SVT segment in both fuels.
Gas SVT segments come from anniversary rolls, not first stints, which is why none appear in these
first-month rows. So it needs its own pre-registration and its own run. It is handed on as a
continuation.

**Also unexplained:** 8 other SVT-origin electricity accounts sit at 0.79–0.87 of the cap, not at
it, for example PROS-2022-0010 at 163.43 against 208.0. `sold_unit_rate` may be reading a record
from after the first stint for them. Read this before the SVT fix is measured, or it will be
mistaken for an effect of that fix.
