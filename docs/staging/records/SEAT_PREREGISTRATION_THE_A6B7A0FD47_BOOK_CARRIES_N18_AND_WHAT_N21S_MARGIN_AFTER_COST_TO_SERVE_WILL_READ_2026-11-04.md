**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** none — focus `a-fresh-book-carrying-n18-and-the-margin-decomposed`

# Pre-registration: the a6b7a0fd47 book carries N18, and N21's margin after cost to serve will read about 15.4% on it, up from 14.5% (2026-11-04)

Written after the launch and before any output. Under the correctness stretch
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`).

**The run.** `launch_long_job` job `fresh-run-a6b7a0fd47`, launched 2026-11-04T17:36:49Z in the locked worktree
`/var/tmp/fresh-run-wt-a6b7a0fd47` at origin HEAD a6b7a0fd47. It writes
`docs/reports/run_output_a6b7a0fd47_20261104T173649Z.json` (log `/var/tmp/fresh-run-a6b7a0fd47.log`).
A second unit, `promote-fresh-run-a6b7a0fd47`, waits for it to end and then runs
`python3 -m background.sim_runner --promote` on that file, which writes the run_complete marker the publisher reads.
So the book is offered for the Mon 9 Nov publish without this session having to survive.

- It carries N18 (6a026b67d), the DD spells (4669d77dd) and the desk fix (ba868134c). All three are ancestors of
  a6b7a0fd47, checked with `git merge-base --is-ancestor`.
- No other run was in flight: there were no active `longjob-*` units, and sim-runner had deferred every cycle since
  16:31Z behind pending landings.

## What the quantity is, before dividing

**Numerator:** Σ over the 1,291 per-fuel account legs of `per_customer_lifetime[...].net_margin_after_cost_to_serve_gbp`.
For each leg that is Σ settlement-record `net_margin_gbp` minus `cost_to_serve_gbp`. A record's net is:
- its revenue,
- less wholesale cost,
- less the modelled policy levies (RO, CfD, CCL, CM, FiT, mutualisation; GGL and CCL on gas),
- less network cost and capital cost.

Cost to serve is the flat `saas/cost_to_serve.py` £55 per leg per year, pro rata.

**Denominator:** Σ settlement-record `revenue_gbp`. This is ex-VAT revenue at the rates the company billed, unit
rate plus standing charge, 2016 to June 2025.

The two are the same population and the same clock, so the ratio is a quantity. It is **not** an EBIT margin:
- bad debt, acquisition spend, fixed cost and back-billing write-offs are in the ledger but not in it;
- the opex it does carry is a placeholder.

The decomposition is on the N21 finding and in `docs/market_research/supplier_financial_reporting.md` §1a.

## The baseline, measured

| book | revenue | net after CTS | ratio |
|---|---:|---:|---:|
| b3ce2a4e73 (20261103T175203Z) | £3,464,489 | £501,559 | 14.48% |
| 4669d77ddd (20261104T132452Z) | £3,464,489 | £501,559 | 14.48% |

The DD spells and the desk fix leave this figure unchanged to the penny, because neither touches a settlement
record. The only change between 4669d77ddd and a6b7a0fd47 under `company/ saas/ simulation/ sim/` is the
`simulation/svt_rates.py` move in N18. Everything else is invariant-runner and grading tools. So this is a
one-variable comparison.

## The prediction

N18 moves four pre-cap SVT unit rates. On 4669d77ddd's bills, the unit revenue billed at the old rate (commodity
plus non-commodity amount, bills at that rate ±0.15 £/MWh ex VAT) is:

| year, fuel | old → new p/kWh | SVT unit revenue on the old rate | Δ at the new rate |
|---|---|---:|---:|
| 2017 electricity | 14.00 → 15.50 | £81,199 | +£8,700 |
| 2018 electricity | 15.25 → 16.30 | £112,852 | +£7,770 |
| 2017 gas | 2.80 → 4.00 | £28,705 | +£12,302 |
| 2018 gas | 3.75 → 4.20 | £69,537 | +£8,344 |
| **total** | | | **+£37,117** |

Wholesale, levies, network and cost to serve are per kWh or per leg and do not see the price. So, to first order,
every pound drops through.

1. **The ratio reads 15.4%, band 15.0–16.0%. Yes, N18 raises it.** If all of it drops through:
   (501,559 + 37,117) / (3,464,489 + 37,117) = 15.38%.
2. **Settlement revenue rises by about £37k, band £25k–£55k, all of it in 2017 and 2018.** 2016 and 2019 onward
   move by under £5k each, from churn and renewal knock-ons only.
3. **The direction can only be up.** Two things pull the other way, and neither can reverse the sign:
   - more SVT departures at the higher price (fewer leg-years, which loses both revenue and CTS);
   - any renewal or competitor reference that reads the SVT.
4. **Falsifiers:**
   - exactly 14.48% means N18 did not reach the company's SVT billing;
   - below 14.48%, or above 16.5%, means this reasoning is wrong about what the price reaches.
5. **The decomposition's conclusion does not move.** The gap to the library's 2–5% stays dominated by operating
   cost (about 9–10 points) and by the ledger lines the page omits (about 5.7 points). N18 widens it by about one
   point, as the drawn item expected.

## Result (graded 2026-11-04 19:12Z; the predictions above are unrevised)

**The book.** `run_output_a6b7a0fd47_20261104T173649Z.json` finished at 19:07Z (Result=success).
- sim-runner made its own run at the same commit, `..._20261104T173613Z.json`. That run started 36 s earlier, once
  the landings had cleared, and finished in the same minute.
- The two agree on every figure below.
- sim-runner promoted its copy. `run_output_latest.json` is byte-identical to it, and its marker
  `run_complete_20261104T173613Z.md` is held for the Monday publish window. So the book is offered to the 9 Nov
  publish.

| | predicted | measured | grade |
|---|---|---|---|
| 1. ratio | 15.4%, band 15.0–16.0%, up | **15.50%** (£548,926 / £3,540,583) | **held** |
| 2. settlement revenue | +£37k, band £25k–£55k, all in 2017–18; later years under £5k each | **+£76,094**. 2017 +£25,864 and 2018 +£20,611 (+£46,475 together). Every later year moved £2.1k–£6.9k (+£29,619), and 2022 and 2023 were over £5k. | **missed** |
| 3. direction up; churn and renewal pull the other way | | Up. The book holds **10 more legs**, not fewer (1,301 against 1,291; +7 to +22 per year from 2018). | **direction held; the named counter-pull was wrong in sign** |
| 4. falsifiers (14.48%, or outside 14.48–16.5%) | | not met | **not falsified** |
| 5. the conclusion of the decomposition does not move | | The ledger lines the page omits are within £2k of 4669d77ddd: bad debt £69,620, acquisition £74,230, write-offs £45,196, fixed £5,700. Cost to serve is £240,607. | **held** |

**What the miss says.**
- 2017–18 is a quarter above the sized £37k. Of that £46.5k of revenue, about 92% (£42.6k) dropped through to net.
- The later-year revenue comes with more legs. So the higher pre-cap price kept or added accounts rather than
  losing them.
- **I cannot yet say** through which path. The candidates are the SVT departure decision, the renewal reference, or
  a different draw sequence downstream of a changed treasury. Each is measurable by diffing the two books'
  `svt_departures` and `acquired_customers` by year.
- The bill-basis sizing also undercounts settlement revenue on SVT periods, by about a quarter here.

**A defect in this run's own plumbing.** The follow-on `promote-fresh-run-a6b7a0fd47` failed:
`python3 -m background.sim_runner --promote` raises at import, `SE_NTFY_TOPIC is not set`.
- The documented hand-promotion route needs `background/.env.ntfy` loaded first, and nothing says so at the call.
- It cost nothing here, because sim-runner's own book was promoted.
- A hand-launched run that is the only book at its commit would not be offered.

**Reverse.** Delete this record. Stop or let finish the two `longjob-*` units. Remove the worktree with
`git worktree unlock` + `git worktree remove /var/tmp/fresh-run-wt-a6b7a0fd47`. If the promote has fired, the
next sim-runner cycle replaces `run_output_latest.json`.
