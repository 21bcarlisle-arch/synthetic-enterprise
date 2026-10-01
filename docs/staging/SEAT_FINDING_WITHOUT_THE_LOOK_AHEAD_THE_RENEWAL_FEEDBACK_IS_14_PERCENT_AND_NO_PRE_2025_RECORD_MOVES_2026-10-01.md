**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# Without the look-ahead the renewal feedback is 14%, and no pre-2025 record moves

Claim `retake-the-renewal-feedback-attribution-without-the-look-ahead`. Graded against
`docs/staging/records/SEAT_PREREGISTRATION_THE_STANDING_CHARGE_PAIRS_RETAKEN_WITHOUT_THE_LOOK_AHEAD_2026-10-01.md`
(landed `fb80f4b68`, before any arm returned).

**Disposition of the draw's duplicate-work note.** "Already held under this very id" was this
draw's own write. The only seat process on the id was this session's executor (pid 3154337), and
no rival `surgical_land` was running.

## Set-up

There were three default worlds, one per arm, on `cd0c7c39c`. The `old` arm ran on `fb80f4b68`,
which adds only the pre-registration document, so its code is identical. Every arm produced
n = 316,175 records and 3,236 renewals. Before the fix these were 319,176 and 3,250, so the fix
changed the book itself. The script is `/var/tmp/se-retake/measure.py`. Both comparison scripts
reproduced the earlier pairs' figures exactly (12 moved keys; £1,040.51 / £320.63) before they
were used on the new arms.

## Pair A: the 2025 row (`exvat` vs `new25`), the whole-run leak test

| | prediction | result | |
|---|---|---|---|
| A1 | 0 account-term-years before 2025 move | **0** (was 12) | holds |
| A2 | elec −£665 ± 30, gas +£91 ± 10 | elec −£646.22, gas +£88.05 | holds |
| A3 | 2025 unit revenue moves by less than £15 | **+£41.70** (elec +£46.81, gas −£5.11) | **MISSED** |
| A4 | kWh identical on every key | identical | holds |

**A1 is the result the item asked for.** The as-of bound in `cd0c7c39c` holds across a whole run,
not only in its unit control.

**A3 missed.** The direction of the miss is not a leak. Portfolio premium carries +£45.09 of the
+£41.70, on 102 renewals. Every one of those renewals starts in January to April 2025. That is the
only window in which a term with 2025 days has ended before a renewal starts and been read by it.
I predicted the feedback would shrink from +£10.43, and it grew. I cannot yet say why. The book
changed and the timing of each entry changed together, so the two cannot be told apart from this
pair. The revenue-to-standing-charge ratio is 0.925 (it was 0.98).

## Pair B: the attribution retaken (`old` vs `exvat`)

| writer | before the fix | **without the look-ahead** | renewals moved |
|---|---|---|---|
| `portfolio_premium` | +£1,040.51 | **+£1,153.72** | 965 (was 876) |
| `margin_surcharge` | +£320.63 | **+£363.40** | 155 (was 222) |
| `price_cap` clamp | −£9.20 | −£1.51 | 2 (was 10) |
| `profitability_uplift` | £0.00 | £0.00 | 0 |
| **unit revenue Δ** | +£1,356.19 | **+£1,518.25** | |
| standing charge Δ | −£11,005.47 | −£10,893.04 | |
| **feedback fraction** | 12.3% | **13.9%** | |

- **B1 holds.** First terms move by £0.00, kWh is identical on every key, and `struck` is identical
  on all 3,236 renewals.
- **B2 MISSED.** I predicted the portfolio premium would carry less than £1,040.51, because the
  lag would delay the reading. It carries £1,153.72. Its share of the total is about unchanged
  (76%, was 77%).
- **B3 holds** (+£363.40, inside £250–£400).
- **B4 MISSED.** The total was +£1,518.25, against a predicted ceiling of £1,400.
- The median last-observed portfolio margin rate went from 0.2462 to 0.2315 (it was 0.2669 to
  0.2496).

## What this changes

- **The 12% finding's mechanism stands, but its numbers do not.** The figures to cite are 14% and
  portfolio premium £1,154 of £1,518. The figures £1,040 of £1,356 were measured on foresight. A
  correction now sits beside the claim in
  `docs/staging/done/SEAT_FINDING_THE_12_PERCENT_IS_THE_COMPANY_PRICING_ITS_LOWER_MARGIN_BACK_INTO_RENEWAL_UNIT_RATES_2026-10-01.md`.
- **Both size misses go the same way: removing foresight made the feedback larger.** This fits
  `cd0c7c39c`'s own refuted sign: book margin rose £7,331 when the foresight was removed. Neither
  is attributed. The one-variable test would be to hold the book fixed and change only the timing
  of each entry. It is not filed as a defect, because nothing here is wrong; what is missing is an
  explanation.
