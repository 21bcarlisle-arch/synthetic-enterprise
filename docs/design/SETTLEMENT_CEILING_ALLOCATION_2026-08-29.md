# The ceiling caps volume; the ALLOCATION is what books zero from 2018

*2026-08-29, delivery seat. Predictions in §3 were written before any code changed — see
`git log -S` on this file.*

**How to re-run every number below, and why there is no new probe tool for it.** The §1 table came
from a throwaway script that called `live_population._resolve_campaign` with the record path
redirected into a scratchpad — the producer writes `book_growth_campaign.json` absolutely from every
process that assembles a book, and that is how the 2026-08-29 mirror happened. It is not committed,
because after the change **the campaign's own record carries the evidence**: `funnel_wins` and `wins`
per year, `settlement_sample_rate` and `customer_years_all_wins_would_cost` per campaign. The one
figure not in it is cost-per-win by year, and that is `(2026-01-01 − win date) / 365.25` over the
`spend` rows — arithmetic, not an instrument. A tool with one caller and one use is the register this
project keeps deleting.

Direction (2026-08-29): *"from 2018 the settlement engine books zero of every year's wins, so
acquisition spend cannot weaken a balance sheet through a book nothing reaches. Fix the settlement
ceiling so the campaign's wins actually reach the book."* And, from the same message: the time
argument the ceiling is defended with is circular, and needs a non-circular basis rather than a
bigger number.

**I am not raising the ceiling, and this document is why.** The ceiling is not what empties
2018–2025. The rule that spends it is.

---

## 1. What a win costs, which is the whole of the mechanism

`_customer_years` charges a won account for its settlement tail — win date to the 2026-01-01
horizon. So the price of a win is a function of WHEN it was won, and it varies by more than
twelve-fold across the campaign:

| year | funnel wins | booked | refused | cy per win | cy for all of them |
|---|---|---|---|---|---|
| 2016 | 24 | 24 | 0 | 9.83 | 236.0 |
| 2017 | 32 | 21 | 11 | 8.76 | 280.2 |
| 2018 | 43 | **0** | 43 | 7.69 | 330.6 |
| 2019 | 42 | **0** | 42 | 6.70 | 281.5 |
| 2020 | 44 | **0** | 44 | 5.75 | 252.9 |
| 2021 | 33 | **0** | 33 | 4.70 | 155.0 |
| 2022 | 30 | **0** | 30 | 3.80 | 113.9 |
| 2023 | 41 | **0** | 41 | 2.66 | 109.1 |
| 2024 | 53 | **0** | 53 | 1.71 | 90.8 |
| 2025 | 38 | **0** | 38 | 0.78 | 29.8 |
| **all** | **380** | **45** | **335** | | **1,879.8** |

82 founders commit 778.2 of the 1,200, leaving **421.8 customer-years for the campaign**. Settling
all 380 wins would cost 1,879.8. So the machine can settle **22.4%** of what this company wins, and
no allocation rule escapes that — it is a real resource limit.

**But the rule that spends it is first-come, and the earliest cohort is the most expensive one.**
421.8 customer-years buys 45 accounts if you buy 2016's, and it buys the whole of 2025 four times
over. The current rule spends the entire campaign budget on the two most expensive years and has
nothing left the moment 2018 opens. That is not a resource limit; it is a censoring rule, and it
produces exactly zero variance in eight of ten years.

The tell that this is allocation and not scale: **raising the budget does not change the shape.**
Any budget B is exhausted at some year, and every year after it books zero. B only moves where the
cliff is.

## 2. What it costs downstream, which is more than the book

- **P9 (book depth).** Every account carrying five or more renewals was won in 2016–17, because
  those are the only years on the book. Depth and cohort are the same variable, so nothing that
  needs one can be separated from the other.
- **PB3's coupled-triad gap is scored on n=1.** `tools/couple_pb3_book_growth.py` excludes
  machine-bound years from its headline, which is right. Its docstring states *"the excluded
  partition is EMPTY — no year of the shipped run is settlement-bound."* On the shipped record nine
  of ten years are excluded and **2016 is the only year scored**. 2016 plans on the founding belief,
  so `abs_error == abs_error_no_skill` and the published `gap = 1.0` is an identity, not a
  measurement. The claim went stale when the founder book made the ceiling taut, and nothing
  reported it — the partition was written as a control and became the population.
- **The company's own plan.** `accounts += 1` fires only on a BOOKED win, so `accounts_held` — which
  sets both the Ofgem capital headroom and the 33% growth-rate cap — freezes from 2018. This is the
  same wall breach that was fixed at `wins_to_date` on 2026-08-28, still live nine lines below it.
  The supplier cannot see the settlement refusal, so it cannot be what its balance sheet is sized
  from.

## 3. Predictions, filed before the change

**Change 1 — `accounts` counts funnel wins, not booked wins.**
Booked wins stay at **exactly 45** and every published book figure is unchanged: 2016 and 2017 plan
from an account count the two rules agree on, and the budget is exhausted inside 2017 either way.
Funnel wins and refusals rise from 2018. *If booked moves at all, something else is coupled to
`accounts` and I have not found it.*

**Change 2 — uniform sampling at a rate derived from the ceiling.**
At HEAD's funnel volume, f = 421.8/1,879.8 = 0.224 books **≈85 accounts across all ten years** for
**416.2 customer-years** — fewer than the 421.8 the current rule spends on 45. Accounts carrying
five or more customer-years of settlement fall from 45 to **≈41**. PB3's scored partition goes from
1 year to 10.

## 4. The rule, and the three I rejected

**Chosen: one sampling fraction, applied to every year alike.** `f = (budget − already committed) /
(customer-years all funnel wins would cost)`, selected systematically over the campaign's win
sequence. Booked wins are then proportional to funnel wins in every year, so `booked / f` estimates
what the company won without bias anywhere, and the ceiling decides the SCALE of the book instead of
deciding which years exist. When `f ≥ 1` nothing is refused and the campaign is byte-identical to
today — the null result that shows the change is aimed at the artefact.

Rejected:

- **A bigger ceiling.** Its time argument is circular (`PUBLISH_CADENCE_SECONDS` is defined as a
  measurement of how often runs arrive, so raising the ceiling raises its own bound) and the second
  probe point was contaminated. There is no evidence to raise it on, and it would not fix the shape
  anyway — see §1.
- **Equal customer-years per year.** Every year gets budget/10. Books more accounts (~111) but
  loads them into cheap recent years, so the book's cohort mix becomes a fact about the horizon
  rather than about the campaign.
- **Equal accounts per year.** Books 7 a year. Every year identical by construction, which destroys
  the year-over-year signal the campaign exists to produce.
- **Cheapest-first.** Maximises the account count and books almost nothing before 2023. The
  mirror image of the bug being fixed.

## 5. What this does NOT do, said rather than left to be assumed

**It does not put more revenue on the P&L.** 416.2 settled customer-years against 421.8 today: the
book's aggregate depth is the same, because that is what the ceiling caps. What changes is coverage
— 85 accounts across ten cohorts instead of 45 across two. Every comparison keyed on year gets a
population; none of them gets a bigger company.

**The published book is a sample and must say so.** At f = 0.224 the company serves 380 won accounts
and 85 reach the book. That artefact is not new — today it is 45 of 380 — but it is now uniform, so
a reader can divide by f. It goes on the page, not in a footnote.

---

## 6. Results, beside the predictions

**Change 1 — `accounts` counts funnel wins. Prediction held exactly.** Booked wins stayed at 45,
2016 and 2017 came back byte-identical (135/24/24 and 191/32/21), and the two rules only diverge
from 2018 because the budget is exhausted inside 2017 either way. Funnel wins 380 → 505, quotes
2,089 → 2,737, spend £46,408 → £60,839. The company now plans against the 587 accounts it holds
rather than the 127 our wall clock let it settle.

**Change 2 — uniform sampling. Direction and magnitude held; the level did not, and the reason is
mine.** Filed prediction: ≈85 booked, 416.2 customer-years, ≈41 accounts at five-plus years, PB3
scored on ten. Measured: **90 booked, 1,195.4 of 1,200 committed, 43 deep, PB3 on ten**, and the
producer's own record agrees once the tree stops moving under it (see below). The
prediction was written against HEAD's 380 funnel wins and change 1 landed first, so the realised
sample is 0.1789 of 505 rather than 0.224 of 380. **The prediction should have been stated for the
composite, because that is the order I had already chosen to run them in.** Kept as filed rather
than revised.

| | HEAD | after both changes |
|---|---|---|
| funnel wins | 380 | 505 |
| booked | 45 | **90** |
| years booking > 0 | 2 | **10** |
| accounts ≥ 5 customer-years | 45 | 43 |
| customer-years committed | 1,199.9 | 1,195.4 |
| PB3 years scored | 1 | **10** |
| PB3 gap | 1.0 *(an identity)* | **0.830** |

**A RANGE THAT RESOLVED TO A NUMBER, AND THE WRONG READING IS KEPT BESIDE IT.** For about ninety
minutes I could not reconcile two runs of the same code at the same seed: my in-process
`_resolve_campaign` gave rate 0.1789 / 90 booked, and the producer's record of 06:32Z gave
0.1834 / 92. The campaign was byte-identical on every leg — 505 funnel wins, 2,358.4 customer-years
to settle them all, 587 accounts held — so the whole difference was in the OPENING book: 778.2
customer-years against a derived 767.5, propagating through `rate = (budget − opening) / campaign
cost`.

I wrote that up as possible **curriculum non-determinism** — two processes building the published
book from different versions of a director-authored artefact — and flagged it as the worse of the
two possibilities.

**It was neither. It was me.** The producer's next cycle (07:50 local) reads **0.1789 / 90**, exactly
matching three separate in-process runs whose sorted acquisition dates hash identically. The 0.1834
has not recurred. The producer executes the WORKING TREE, and at 06:32 that tree was being edited —
by this session and by at least one other lane at the same time. **A figure read off the producer's
artefact while the tree is under edit is not a measurement of anything.**

That is the mirror finding of 2026-08-29 §1 one level out. There, a probe adopted the producer's
book because both wrote the same path; here, the producer adopted a half-written tree because I was
the one writing it. Same question, asked of the other direction: *who else is touching the thing you
are measuring* — and "me, right now" is an answer that has to be checked too.

**The shipped figures are 90 booked, rate 0.1789, book 172, and every table above uses them.**

## 6a. What it costs to run, which is the one thing a ceiling change must not get wrong

The book doubled in ACCOUNTS (45 → 90 campaign wins, 127 → 172 on the book) at essentially
unchanged CUSTOMER-YEARS (1,199.9 → 1,195.4). Those two scale different costs, so the question is
which dominates.

**Estimated at +0% to +3%, and it is an estimate, labelled as one.** From the probe's own two cost
points — 796.1 customer-years at 746.8s (2026-08-24) and 1,200.0 at 1,018.7s (2026-08-29) — the
marginal cost is ≈0.67 s per customer-year and the fixed component is ≈215s, so settlement is ~80%
of the run and roughly linear in customer-years. Customer-years fell 0.4%. The 45 extra accounts pay
per-account setup only, which sits inside that fixed component; at a plausible 0.5s each that is
+22s on a ~1,000s run.

**It is NOT measured, and this section says so rather than quoting a number.** The box currently has
three heavy Python processes on it — this session's regression suite, another lane's suite, and
`process_run_complete` — and a wall clock taken under contention measures the contention. That is
the same class as the probe mirror of 2026-08-29 §1: *ask who else is touching the thing you are
measuring.* The live producer runs this code every cycle and will price it for free on a quiet box;
the number belongs here when it is clean, and the baseline to beat is the stable ~1,000s of the
eight runs before the change.

## 7. The ceiling's basis, which is the second half of the direction

Both legs were examined and **neither of them sets 1,200**:

- **Memory** is non-circular — a slower run does not make the box bigger — and it is **slack by
  4.5×**: the clean point peaks at 4,193 MB against a guest holding 24,032 MB with 19,009 MB
  available. Real evidence, but not what this number came from.
- **Time** is the binding leg and **has no valid basis today**. The circular argument is removed from
  the constant. What would replace it is a publish interval somebody *chose* and named in a file —
  and the non-circular anchor for that choice is external: how often the inputs this site reports
  actually change, which is a fact about Elexon and NESO rather than about our own run.

So 1,200 stands on no current evidence, and the constant now says so. **The allocation fix is what
makes that survivable and is why the number was not moved instead.** The ceiling used to decide
which years existed, so its exact value was decisive; it now sets a sample rate, so getting it wrong
costs the book's precision rather than its coverage. It can wait for a real answer instead of forcing
an invented one.

## 8. What this creates

1. **A director decision, priced:** the publish interval. Memory would support roughly 4× today's
   ceiling; wall clock is what stops it, and there is no named interval to check wall clock against.
2. **The next engineering ceiling in the same chain.** Three of the ten years are now MARKET-BOUND at
   `PROSPECTS_PER_YEAR = 400` — in 2024 the company could afford 861 quotes and only 400 prospects
   exist. Our number, not the GB switching market's.
3. **Two controls that went quiet, both repaired, both re-keyed to properties.** The growth page's
   headline (`binding == settlement_engine` → the sample rate) and its learned-rate caveat
   (positional latch → does the planned-on rate equal the funnel's own history). That flag had
   failed in *both* directions inside four days without going red once.
