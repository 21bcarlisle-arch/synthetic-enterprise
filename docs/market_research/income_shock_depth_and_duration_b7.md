# How deep a GB household's income shock goes, and how long it lasts

**Knowledge:** debt-and-collections

**2026-10-17, worker tick (B7 drawn; K8 knowledge before build).** This is for B7's open item (d),
income-shock depth (`docs/design/simplifications/B7_customer_state_layer_moves_and_shocks.yaml`, record
of 2026-10-10). The world build waits for the 2026-10-19T03:00Z publish (`docs/direction/DIRECTION.yaml`).
Its lane also carries the BLOCKING crisis bad-debt finding, whose cause is the world's non-payment
(`docs/market_research/household_budget_w2_4.md`, 2026-10-16 design). So only the knowledge moves this
tick. No code changes here.

## 1. What an income shock is, before any figure

The world has one flag, `IncomeStress.HIGH` (`simulation/life_events.py`). A job loss sets it, an
annual coin flip clears it, and illness reuses the same recovery. That one flag covers **two
different experiences**, and the published evidence measures them separately:

1. **The spell out of work.** Earnings stop, and benefits replace part of them. This lasts months.
   It is what the recovery constant's own comment says it models ("median UK unemployment spell ~6
   months").
2. **The scar after re-employment.** The household works again but on lower pay. This lasts years.

A supplier sees neither, only the payments. Spell 1 is a sharp liquidity shock and shows up as
missed bills. Spell 2 is a lower income level and shows up as a tighter household budget (W2_4).
**The build should model them as two states, not one longer flag.**

## 2. The spell: how long GB unemployment lasts

**Source:** ONS Labour Force Survey, unemployed by duration, UK, all aged 16+, thousands, seasonally
adjusted, annual. Series YBWF (up to 6 months), YBWG (6-12 months), YBWH (over 12 months) and YBWL
(over 24 months), fetched 2026-10-17 via `ons.gov.uk/generator?format=csv`.

| year | up to 6m | 6-12m | over 12m | over 24m | total | share up to 6m | share over 12m |
|---|---|---|---|---|---|---|---|
| 2016 | 948 | 248 | 438 | 242 | 1,634 | 58.0% | 26.8% |
| 2019 | 793 | 196 | 322 | 164 | 1,311 | 60.5% | 24.6% |
| 2020 | 1,006 | 241 | 323 | 167 | 1,570 | 64.1% | 20.6% |
| 2021 | 815 | 292 | 438 | 210 | 1,545 | 52.8% | 28.3% |
| 2022 | 804 | 163 | 336 | 176 | 1,303 | 61.7% | 25.8% |
| 2023 | 924 | 196 | 287 | 165 | 1,407 | 65.7% | 20.4% |
| 2025 | 1,018 | 312 | 412 | 178 | 1,742 | 58.4% | 23.7% |

**What this counts.** It is the **elapsed** duration of spells still in progress, for the people
unemployed at the survey date. It is not the length of completed spells. If the monthly exit rate
were constant, the two would have the same distribution. A 58% share at up to 6 months then gives an
exit rate of 0.145 a month and a **median spell of about 4.8 months** (3.9 to 5.5 across 2016-2025).
That rate predicts 18% still out of work after 12 months. The observed share is 21-28%, which is
more. So exit slows as a spell lengthens (duration dependence). Because long spells are
over-represented in a stock, the median of spells **as they start** is at or below the stock
figure. **Stated belief, with a range:** median completed spell 3 to 6 months. About one in four
people out of work have been out more than a year. Duration dependence is real but unmeasured here.
**GAP:** the completed-spell distribution from LFS flows (X02) has not been read.

## 3. The depth: how much income falls

Both studies below were read through search-engine excerpts, because their pages refused the fetch
(HTTP 403). Before either number becomes load-bearing, re-read the original.

**IFS, "Unemployment benefits and household spending: new evidence from UK bank account data"**
(ifs.org.uk). Anonymised bank-account data covering more than 10,000 job losses, 2018-2023.
- Claimants earned about **£1,800 a month after tax** before the job loss. Benefits rose by about
  **£600 a month**, so income fell by about **£1,200**. Benefits replaced about a third of lost
  earnings. Spending fell by about **£550 a month, about 20%**, in the first months.
- The fall depends on the replacement rate. For the third of people with the lowest replacement,
  income fell about **90%** and spending **26%**. For the third with the highest, income fell about
  **30%** and spending **6%**.
- **Energy bills directly.** For the least-protected third, the share making an energy bill payment
  each month fell about **17-20%** below its level before the job loss. For the most-protected third
  it fell **3%**. The least protected also ran down savings harder and for longer.
- **Unit:** the income here is the claimant's own income, not the household's. The sample is people
  who claimed benefits.

**Bedük et al., "Insurance against risk? Cost and compensation of job loss in different welfare
states", Socio-Economic Review** (Oxford DSPI news, 27 Oct 2025).
- **Household** income fell **17% in the first year** after a job loss in the UK, against 5-6% in
  Denmark, Finland and Germany.
- The **cumulative loss over five years was about 35%**. Most people found work within a year, but
  at lower pay. The excerpts did not give the pay penalty on re-employment reliably, so no figure is
  quoted for it.

**How the two studies fit.** The spell (§2) is short and deep: a third or less of the earnings is
replaced, energy payments fall by up to a fifth, and it lasts months. The scar is long and shallow:
household income stays well below its old level for years. A 17% fall in the first year is about
what a few months at -60 to -70% of one earner's pay, plus a lower wage after return, would give.

## 4. What our code does, set against the evidence

- `_INCOME_RECOVERY_ANNUAL_PROB = 0.50`, cited "median UK unemployment spell ~6 months". As written
  (recovery is not tried in the year of the job loss, then once a year at a random date), the HIGH
  spell that follows a job loss has a **median of 19.1 months, a mean of 24.0 months, 6.2% ending
  within 6 months and 75% lasting more than 12** (simulated 200,000 draws, 2026-10-17). The comment's
  own median of 6 months would need a spell about 4x shorter. The ONS stock in §2 says the same.
  **Corrected here, beside the claim. The constant is not changed this tick** (world build held to
  the publish). The bounding test (`tests/sim/test_phase_mv_economic_life_events.py`, 0.2 to 0.8)
  accepts both the defect and the fix, so it decides nothing.
- The flag has no **magnitude**. The IFS result is that the replacement rate decides whether the
  energy bill is paid: about 20% fewer payments in the bottom third, 3% in the top. That gradient is
  the payment-draw input the W2_4 build needs. The flag cannot carry it.
- The flag has no **scar**. If the spell were shortened to the evidence without adding a scar state,
  the world would lose the years of lower income that Bedük measures. That would err *for* our
  thesis, because it understates arrears (F11). **So the spell fix and the scar must land in one
  build, not the spell fix alone.**

## 5. Choices for the B7 slice (d) build, and the prediction to file with it

1. Split HIGH into `out_of_work` (monthly exit hazard; median 3-6 months; about 25% still out after
   12 months) and `scarred` (income below the old level for years; level from Bedük, re-read first).
2. Draw the replacement rate per household on its own substream (`income_shock_magnitude`, kept
   separate from the onset stream, as the FRAME requires). Give it to the W2_4 budget as income, not
   as a new payment probability.
3. **GAP:** the replacement-rate distribution by household type. UC taper, savings and partner
   earnings decide it. IFS publishes terciles, not a distribution, so the build carries terciles.
4. **Prediction for that build:** with HIGH split this way, households out of work at any date fall
   by about three quarters (same inflow, mean spell 24 months to about 6), while years spent below the old income rise. The world's arrears from job loss
   move earlier (in the spell) and get smaller per event. The book's total arrears change by less than
   ±15%. If they fall by more than that, the scar is too light.

## Sources

- ONS, LFS unemployment by duration: YBWF, YBWG, YBWH, YBWL (`/employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/<cdid>/lms`), fetched 2026-10-17.
- IFS, Unemployment benefits and household spending: new evidence from UK bank account data, https://ifs.org.uk/publications/unemployment-benefits-and-household-spending-new-evidence-uk-bank-account-data (read via search excerpt; fetch refused 403).
- IFS press release, https://ifs.org.uk/news/newly-unemployed-see-living-standards-fall-and-financial-distress-increase-despite-benefits (read via search excerpt).
- University of Oxford, 27 Oct 2025, https://www.ox.ac.uk/news/2025-10-27-uk-families-lose-nearly-fifth-income-after-job-loss-oxford-research-shows (Bedük, Socio-Economic Review; read via search excerpt).
