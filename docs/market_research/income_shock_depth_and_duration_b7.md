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
**GAP:** the completed-spell distribution from LFS flows (X02) has not been read. *(Read 2026-10-18,
§6. The flows bound the median but do not give the distribution. "About one in four" is a share of
the stock, not of new spells; see §6.)*

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
   **Corrected 2026-10-18 (§6):** the 25% is the share of the *stock* out of work over a year. A
   build that draws one spell per job loss needs the share of *new* spells that last over a year,
   which is about 4-15%. Drawing 25% per event would roughly double the long tail. The scar fades:
   Bedük's abstract says the household loss "gradually diminish[es] and disappear[s] over the long
   run", so `scarred` needs an exit too.
2. Draw the replacement rate per household on its own substream (`income_shock_magnitude`, kept
   separate from the onset stream, as the FRAME requires). Give it to the W2_4 budget as income, not
   as a new payment probability.
3. **GAP:** the replacement-rate distribution by household type. UC taper, savings and partner
   earnings decide it. IFS publishes terciles, not a distribution, so the build carries terciles.
4. **Prediction for that build:** with HIGH split this way, households out of work at any date fall
   by about three quarters (same inflow, mean spell 24 months to about 6), while years spent below the old income rise. The world's arrears from job loss
   move earlier (in the spell) and get smaller per event. The book's total arrears change by less than
   ±15%. If they fall by more than that, the scar is too light.

## 6. The two GAPs, read (2026-10-18, worker tick; the world build is still held to the publish)

### 6.1 The exit hazard, from LFS flows

**Source:** ONS X02, LFS flows estimates, sheet "Labour market flows hazard rate" (published 18 Aug
2026, data to Apr-Jun 2026). It gives the share of people unemployed in one quarter who are still
unemployed, in work, or inactive in the next. People aged 16-64, UK, seasonally adjusted.
Annual means of the quarterly rates:

| year | still unemployed | to work | to inactive | median of a constant hazard, any exit | the same, exit to work only | still out after 12m, constant hazard |
|---|---|---|---|---|---|---|
| 2016 | 53.1% | 28.2% | 18.6% | 3.3 months | 6.3 months | 7.9% |
| 2019 | 48.2% | 31.5% | 19.7% | 2.9 | 5.5 | 5.4% |
| 2021 | 46.8% | 32.8% | 20.0% | 2.7 | 5.2 | 4.8% |
| 2022 | 44.4% | 31.9% | 23.4% | 2.6 | 5.4 | 3.9% |
| 2023 | 42.2% | 34.4% | 22.8% | 2.4 | 4.9 | 3.2% |
| 2025 | 50.9% | 28.7% | 20.1% | 3.1 | 6.2 | 6.7% |

**What this counts.** It covers every person unemployed at the first quarter, whatever their elapsed
duration, so it is a hazard over the stock. Two exits are different experiences for a household
budget. Exit to work restores earnings. Exit to inactivity (sickness, caring, giving up the search)
usually does not. So the "any exit" median is a floor for the income shock, and the "to work only"
median is closer to it.

**The flows and the duration stock do not reconcile.** Both are ONS LFS, 2016-2025. About half the
stock leaves each quarter (flows), yet 21-28% of the stock has been out over a year (§2). A
constant hazard predicts only 3-8% over a year. That is the duration dependence §2 inferred, and it
is large. A two-type mixture fitted to three moments (stock share up to 6 months 0.60, share over
12 months 0.245, quarterly still-unemployed 0.485) does not converge to an interior solution. The
short type hits its bound (a monthly exit of 0.99). The long type is about **6-15% of new spells**,
with a monthly exit of about **0.06-0.08** (a median of about 9-11 months). The three-year fits
(2016, 2022, 2023) bracket the same range. **I cannot yet say** which source the gap comes from.
One candidate is response error in the flows: a person recorded as unemployed, then inactive, then
unemployed again counts as two exits and two entries. That would make the flows' exit rate an upper
bound. Another is that geometric types are the wrong shape. Neither is established here.

**What the build can rely on, as a stated belief with a range:**
- Median time from job loss to work: **3 to 6 months** (unchanged from §2, now bounded on both sides
  by two ONS sources).
- Share of new spells still out of work at 12 months: **about 4-15%**, not the stock's 25%. A long
  type of about a tenth of job losers carries almost all of the long-term unemployment.
- The 2022-23 crisis did not lengthen spells. Exit to work was at its decade high (34.4% a quarter
  in 2023). So the crisis reaches a household through the bill and the benefit uprating
  (`household_budget_w2_4.md`, 2026-10-17), not through longer unemployment.

### 6.2 The scar's depth and shape, from Bedük et al.

**Source re-read:** the abstract (Bristol Research Portal, CC BY; DOI 10.1093/ser/mwaf066). Every
full-text copy refused the fetch (OUP and utupub.fi, HTTP 403), so the year-by-year UK estimates are
still unread. The abstract says "survey and administrative data" for the four countries, 1990-2018,
and a dynamic difference-in-differences model. Which UK survey is used is unread.
- "Job loss reduces household income by about 17% in the UK and 5–6% in other countries during the
  first year. **These losses gradually diminish and disappear over the long run.**"
- "Market compensation (i.e., re-employment) is the main source of compensation." Household
  compensation, such as a partner working more, "largely substitutes for weaker market and state
  protections".

**Corrected beside §3 and §5:** §3 says the cumulative loss over five years was about 35%. That
figure is from the press release, and it fits a loss that fades. For example, 17%, 10%, 5%, 2% and
1% over five years add up to 35% of one year's income. That path is an illustration, not a reading. §5 said "below the old level for
years", which reads as permanent, and that is wrong. The press release's "jobs paying 40% less" is
quoted by excerpt only, and its unit (hourly pay, earnings, or the job loser's own income) is
unknown. **It is not load-bearing.**

**What the build can rely on:** `scarred` is a state with an exit. Household income starts about 17%
under its old level in year one and returns to it over about five years. **GAP:** the year-by-year
UK path (years 2-5) needs the full text, and a reader whose fetch is not refused.

### 6.3 What changes in §5's prediction

Prediction 4 assumed the stock's 25% as the per-event tail. With the per-event tail at 4-15%, the
out-of-work stock after the build falls by more than three quarters against today's 19-month median
coin. **Restated, before any build:** the stock of households in `out_of_work` falls by 75-90%. The
book's total arrears change by less than ±15%. If they fall by more than that, the fading scar is
too light or fades too fast. That is the side to check first, because a shorter shock errs for the
thesis (F11).

## 7. Built (2026-10-20, worker tick): the spell and the scar, in one build

`simulation/life_events.py`. A job loss draws its spell on its own substream, `reemployed`,
from §6.1's two types: a long tenth at 0.07 a month, and a short type whose hazard is derived so
the median to work is 4 months. A new spell is then still running at 12 months 13.7% of the time.
4 months is the longest median the 3-6 band allows before the 12-month tail leaves 4-15%, so it is
the admissible spell that errs against the thesis. The spell ends on its date (`reemployed`) into
MODERATE, the scar, and the scar ends (`income_scar_ended`) five years later, unless the home
retired in the meantime. Illness and a household already HIGH at the draw keep the annual coin.
No illness-spell length has been read, and the opening stock's elapsed spell is unknown.

Printed on 4,000 homes from a LOW opening, 2016-2025, old against new: the spell median falls from
16.5 to 4.0 months. Spells over 12 months fall from 70% to 12%. HIGH household-months fall 44%
(illness is unchanged inside that), and MODERATE household-months rise 46%. Births fall 3%,
because a scarred home is not LOW and the birth gate asks for LOW.

**Not identified by the evidence:** with the long type set to zero, the derived short type still
lands inside both bands (median 4, tail 12.5%). The bands cannot tell one type from two, so the long
type is carried as this page's belief and nothing grades it.

**Prediction, filed before any run carries this (restating §6.3 for the point built):** job-loss
HIGH time falls about 74% (mean spell 24 months to 6.2). That is just under §6.3's 75-90%, because
4 months is the long end of the band. The book's total arrears change by less than ±15%. If they
fall by more, the scar is too light first. The magnitude leg (§5 choice 2, the replacement rate as
W2_4 income) is not built. Until it is, a scar and a spell differ only in which stress state they
hold.

**How it is graded.** The next published run also carries the leaver fixes (legs (b) and (d) of the
D-lane leaver finding), so the run alone cannot attribute an arrears move to this change. The grade
is a paired, world-only capture with this commit and its parent, on one seed. The W2 BLOCKING
crisis bad-debt finding is about the same arrears. Its cause, the under-water household's exit, is
its own continuation, and this slice does not take it.

## Sources

- ONS, X02: Labour Force Survey flows estimates, `x02aug2026.xls`, sheet "Labour market flows hazard rate" (https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/labourforcesurveyflowsestimatesx02), fetched 2026-10-18.
- Bedük, Fasang, Harkness et al. (2025), Insurance against risk?, Socio-Economic Review, mwaf066, abstract via https://research-information.bris.ac.uk/en/publications/insurance-against-risk-cost-and-compensation-of-job-loss-in-diffe/ (full text refused, 403), read 2026-10-18.
- ONS, LFS unemployment by duration: YBWF, YBWG, YBWH, YBWL (`/employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/<cdid>/lms`), fetched 2026-10-17.
- IFS, Unemployment benefits and household spending: new evidence from UK bank account data, https://ifs.org.uk/publications/unemployment-benefits-and-household-spending-new-evidence-uk-bank-account-data (read via search excerpt; fetch refused 403).
- IFS press release, https://ifs.org.uk/news/newly-unemployed-see-living-standards-fall-and-financial-distress-increase-despite-benefits (read via search excerpt).
- University of Oxford, 27 Oct 2025, https://www.ox.ac.uk/news/2025-10-27-uk-families-lose-nearly-fifth-income-after-job-loss-oxford-research-shows (Bedük, Socio-Economic Review; read via search excerpt).
