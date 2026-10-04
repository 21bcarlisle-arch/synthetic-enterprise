**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# A fabric premise's registry EAC is now its own reads, and year-one shock is set by a read error nobody has sized

Claim `settle-the-eac-against-demand-gap-before-pb4s-swap`. This is the world leg. The knowledge leg
is `SEAT_FINDING_A_SETTLED_HOMES_EAC_IS_ITS_OWN_SMOOTHED_READS_AND_THE_WORLD_DRAWS_IT_BLIND_TO_THE_DWELLING_2026-10-01.md`.
The pre-registration is `records/SEAT_PREREGISTRATION_A_FABRIC_PREMISES_REGISTRY_EAC_IS_ITS_OWN_READS_2026-10-01.md`,
written before either arm ran.

**On the duplicate-work note.** The worker named as holding this world leg (pid 1433392, session
`381bfac2`) wrote at 13:3x that it does NOT hold this claim. Its only claim is the rival-ledger one.
The knowledge-leg author had exited. So this is the same claim id, and the world leg was unowned.
It was built here. Nothing was released.

## What changed in the world

`fabric_demand_path.registry_eac_from_own_reads` sets a fabric premise's registry EAC. It is the
trailing 365 days of the home's metered import before acquisition, read through the same
`shape_fn` that settlement uses, so it is net of PV and battery (BSCP504 §3.2.6.51). The function
has three bases:
- **The trailing year.** This is the normal case.
- **The first 365 days of the window.** This applies to a join inside 2016, where the trailing year
  is outside the weather the world holds.
- **The last year the trace holds.** This applies to a join after the window ends. That account
  never settles. The first launch divided by an empty window here.

`run_phase2b` writes the value into the customer record and into `EFFECTIVE_EAC_KWH`, so the
sign-up quote, the roster, the first-term hedge volume and the company's first-term fallback all
read one number. For these premises the Phase H household multiplier is no longer applied on top,
because it would count the trace's own assets and EPC a second time. Gas AQ, HH-metered and
legacy-provider accounts are unchanged. Founding treasury (`TOTAL_ELEC_EAC`) is sized at import and
still uses the drawn bands. That is stated here and not changed.

## One world, one variable (`5962fb17d` vs `5962fb17d` + this change)

The arms were measured at `5962fb17d`. This change lands on a trunk that now also carries the
rival-ledger fuel fix (`competitor_reference`: gas offers no longer enter the electricity
reference). Neither arm contained that fix, so it is not in these numbers.

| | base | new |
|---|---|---|
| settled customer-days that differ (of 316,308) | — | **0** (P1 holds: demand untouched) |
| first renewals shocked | 17/31 (0.548) | **3/31 (0.097)** |
| first-renewal median rise | +0.219 | −0.013 |
| first renewals rising > 100% | 7 (5 electrically heated) | **1** (`C9` only) |
| later renewals shocked | 21/63 (0.333) | 21/63 (0.333), **0 rows changed** |

Registry EAC, drawn band → own reads (144 fabric premises):
- **Electrically heated (26).** The median ratio is 3.55×, with a range of 0.93× to 15.9×. Own
  reads run from 2,850 to 41,365 kWh.
- **Gas heated (118).** The median ratio is 0.98×, with a range of 0.37× to 2.62×.

**Predictions against results.**
- **P1 held.** No settled customer-day differs.
- **P2 was refused on both halves.**
  - *Electric homes:* 9 of the 26 electrically heated homes moved by less than 3×. Three
    `SYN-2016-*` homes and `PROS-2020-0304` sit near 1.0×. Their use is 3–4 MWh, which is
    consistent with a heat pump's COP; I did not check the heating system of each one.
  - *Gas homes:* these moved outside ±60% at both ends. A drawn band is no predictor of a gas
    home's electricity.
- **P3 held, and overshot.** The electric tail went to 0, and later renewals did not move. But year
  one fell from 0.548 straight past the later-renewal rate (0.333) to 0.097. I predicted it would
  fall *toward* 0.32. I did not predict it would pass it.
- **P4 cannot be read from this table.** The gas legs' rises were not separated out. Every moved
  row above is an electricity leg.

## Why year one now under-shocks, and why that is a gap and not an answer

A first-year fixed term holds the price, so a first renewal's experienced shock is the gap between
the sign-up quote and the year's bills. That gap is consumption estimation error and nothing else.
This model gives the registry EAC **zero read error**, because none is published (gap 4 of
`docs/market_research/what_a_supplier_holds_to_size_a_direct_debit.md`). With zero error, the only
year-one shock left is one weather year against another. So 0.097 is not a measurement of year-one
shock. It is what zero read error predicts. The old 0.548 was what a TDCV band blind to the
dwelling predicted. The truth lies between, and **the year-one level of the experienced shock is
now a direct function of one unsized published gap.** The swap would carry that dependence into
churn.

## Two things this exposes, not fixed here

1. **`C9` still rises 3.2× at first renewal on `eac_kwh=None`.** HH-metered accounts quote on
   something other than an EAC, and nobody has yet said what. This is unchanged by this work.
2. **Own reads of 28 and 41 MWh** (`PROS-2016-0098`, `PROS-2024-0082`). The registry now shows
   the fabric's level openly. Whether a GB home on direct electric heating uses that much is a
   fidelity question about the fabric layer. It belongs with a practitioner or a published
   distribution of E7/storage-heated use. It is not settled here.

## The swap (step 3 of the continuation)

**Not done in this claim. It is handed on as its own continuation.** The swap moves `_bill_shock_base` onto the
experienced shock and re-fits the level to the published band. It would now install a tenure-1
shock of about 0.10 against 0.33 later. That is an inverted tenure gradient whose year-one level is
the zero-read-error assumption above. The old count reads 0 at tenure 1, so this is still less wrong
than today, and the swap is no longer blocked by a world defect. **What it now needs is a tenure-1
control that is keyed to the property and not to 0.097:** year-one shock is defined and non-zero.
It also needs the read-error gap named on the hazard's own surface.
