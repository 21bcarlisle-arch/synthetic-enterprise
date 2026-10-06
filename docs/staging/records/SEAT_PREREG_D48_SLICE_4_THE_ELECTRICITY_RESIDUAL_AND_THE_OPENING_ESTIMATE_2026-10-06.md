**Severity:** RECORDED · **Lane:** D_billing_metering · **Claim:** `d48-slice-4-retire-the-worlds-estimator-and-attribute-the-electricity-residual`

# Pre-registration: D48 slice 4. The electricity residual, and an opening estimate taken from the registry

Filed 2026-10-06 01:15 BST. At that point no barred run had been listed, no household's
winter/summer ratio had been computed, and no opening-estimate code had been written. The world is
the slice 3 capture (`/tmp/d48s3/world.pkl`: 261,066 settled records, 87 leavers). The arms are the
feed's flat estimate ("flat") and the company's shaped estimate ("shaped"). Each arm builds bills
on that one world.

## Part B1: why electricity barred kWh rose from 1,230 to 2,078

The published electricity profile puts 1.49 times as much use on a winter day (December to
February) as on a summer day (June to August). A household whose own ratio is flatter than that is
estimated too low in summer under the shaped estimator when its last reads fell in winter. If that
under-billing runs on past 12 months, the back-billing limit bars it.

| | Prediction |
|---|---|
| B1a | The barred runs differ between the two arms in **5 or fewer** runs. At least **70%** of the +848 kWh increase sits in **3 or fewer** runs |
| B1b | The runs that carry the increase belong to households whose own winter/summer ratio is **below 1.49**, and their estimate window ends in October to March |
| B1c (refutation) | If the increase is spread across more than 5 runs with no ratio pattern, the household-shape account is wrong for K3. The next candidate is a change in **which** bills are estimated through the opening-period path. That is not tested here |

## Part B2: why electricity June gross rose from 12.9% to 15.6%

The household's own ratio is its Dec–Feb kWh per day over its Jun–Aug kWh per day. It is taken
only from that household's **actual-read** bills of 28 days or more. A household with no actual
read in one of the two seasons goes in an "unknown" group, which is reported and not dropped.
Households are split into terciles by that ratio.

| | Prediction |
|---|---|
| B2a | In the flattest tercile, June gross is **higher** shaped than flat |
| B2b | In the steepest tercile, June gross is **lower** shaped than flat |
| B2c | The flattest tercile carries **most (>50%)** of the increase in June absolute true-up kWh |
| B2d (refutation) | If all terciles rise by similar shares, household shape does not explain the rise, and the slice 3 hypothesis is wrong |

## Part A: retiring the world's estimator

Today the feed estimates the opening period (before the company holds any read) as
`true_consumption_kwh`. That is the household's real use crossing the wall as an "estimate", so
those bills carry zero error by construction. After this change the company estimates the opening
period as registry EAC/AQ (or the Ofgem TDCV MEDIUM band when there is none) times the period's
profile weight. Everywhere else it keeps its own shaped estimate.

| | Prediction (shaped arm, before vs after) |
|---|---|
| A1 | Every bill whose amount changes is an opening-period estimated bill or a later bill in the same run. No bill after an account's first actual read moves, except through that run's catch-up |
| A2 | Electricity per-bill \|error\| / billed kWh **rises** (opening estimates lose their zero error): by more than 0.5 pp |
| A3 | December and June net bias move by **less than 2 pp** for either fuel. Opening periods are a small share of the run-billed kWh |
