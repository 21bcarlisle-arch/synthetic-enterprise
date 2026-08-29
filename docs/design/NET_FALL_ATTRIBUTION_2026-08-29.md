# The £10,378 fall in published net, attributed — and R6's headroom re-measured on today's book

**Lane 0 delivery direction, 2026-08-29.** Two measurements on the post-allocation run.

The two runs compared throughout are the two consecutive published runs across the transition, each
identified by the code hash it ran at and its own artefact:

| | before | after |
|---|---|---|
| code hash | `d5d58da62` | `a9e3e18dc` |
| artefact | `docs/reports/run_output_d5d58da62_20260829T055257Z.json` | `docs/reports/run_output_a9e3e18dc_20260829T072659Z.json` |
| published net | £164,541.78 | £154,164.43 |
| campaign spend | £46,408 | £60,839 |

Seven commits sit between them (`git log d5d58da62..a9e3e18dc`).

---

## PART 1 — THE PREDICTION, WRITTEN BEFORE THE MEASUREMENT

Filed before opening either `run_output` file. **What I had already seen when I wrote it** is stated
here rather than left implicit, because a prediction made with the answer half-visible is worth less
than one made blind and must not be presented as the latter: I had read
`docs/observability/run_history.json`'s `headline_metrics` for both runs, which publishes the trading
block but **not** revenue, gross, fixed cost, cost to serve, bad debt or acquisition spend.

From that block alone, two things were already visible:

- whole-run actual trading net: £134,170.92 → £112,561.47 — **£21,609.45 worse**
- hedging cost vs naked: −£384,471.87 → −£410,595.00 — **£26,123.13 worse**

**The direction's hypothesis is that the £14,431 spend rise alone accounts for most of the £10,378
fall. I predict that is WRONG, and in an interesting direction.**

Specifically:

1. The spend rise (−£14,431) is **not** the largest single mover. The trading result is, at
   −£21,609.
2. Those two together are −£36,040 against an observed fall of only −£10,378. Therefore something
   moved **in the company's favour by roughly +£25,700**, and it is almost certainly gross margin on
   a larger book — the 45 new accounts earning.
3. So the honest shape of the answer is *not* "growth cost us £10,378". It is "the book grew and
   earned, the campaign cost more, and a worse trading year swamped both" — and if that is right,
   the fall is **mostly not attributable to the growth loop at all**.
4. The residual after spend + trading + gross margin will be small but non-zero, and I expect the
   named remainder to be cost to serve on the new accounts, which is the one growth cost the
   direction explicitly asks about.

**If instead gross margin is flat or down**, prediction 2 is refuted and the fall is a genuine cost
of the machine, which would be the more serious reading. Recorded so it can refute me.

**A refusal is a permitted outcome.** More than one thing moved across seven commits. If the
decomposition does not close to within a materiality bar, this document says so and names what is
unattributed rather than allocating a plug.

---

## PART 2 — THE MEASUREMENT. IT CLOSES, TO £0.00

### 2.1 First, the two spend figures are not the same quantity

The direction quotes campaign spend as £46,408 → £60,839. The run artefacts say
£47,150.95 → £61,547.12. Both are right and they count different things, so they are named here
before anything is divided by either:

| | what it counts | before | after | Δ |
|---|---|---:|---:|---:|
| `settlement_ceiling_probe.json` `spend_gbp` | the campaign's **planned** buy — 2,089 → 2,737 quotes at the sourced unit cost | £46,408.25 | £60,839 | +£14,431 |
| `run_output.total_acquisition_spend_gbp` | the **realised** spend the run booked, over 2,130 → 2,777 attempts | £47,150.95 | £61,547.12 | +£14,396.17 |

Everything below uses the realised figure, because the realised figure is the one on the same book
as the net.

### 2.2 The identity the published net is actually built from

`total_net_gbp` is `sum(net_margin_gbp)` over the settlement records, and folding the per-year
lines shows it obeys exactly one identity, on both runs, to the penny:

```
net = gross − capital − bad_debt − (policy + gas_policy) − (network + gas_network)
```

Reproduced (run A): 595,468.99 − 7,417.78 − 15,562.49 − 149,326.56 − 258,620.39 = **164,541.77**
against a published 164,541.78. Run B: 614,439.82 − 9,031.24 − 11,039.61 − 160,143.70 − 280,060.84
= **154,164.43**, exact.

**Those five drivers are exactly the five `saas/reporting/margin_attribution._build_bridge` already
uses** — this measurement reuses that module's decomposition rather than inventing one, and the
`margin_bridge_series` shipped in the run confirms it: nine year-on-year bridges, every residual
below £0.003. What the bridge does year-over-year within one run, this does run-over-run.

### 2.3 THE FIRST RESULT: acquisition spend is not a line in the published net

**Acquisition spend, fixed cost and flexibility revenue do not appear in the identity at all.**
Subtracting acquisition spend from the run-A total gives £117,390.82, not £164,541.78.

So the direction's hypothesis — *the spend rise alone accounts for most of the £10,378* — is not
merely small. **It is structurally impossible.** A £14,396 rise in a line the published net does not
contain cannot account for any part of a fall in it. The campaign's money leaves the treasury and
leaves no mark on the headline figure, which is worth knowing on its own.

My own prediction is refuted too, and more embarrassingly. I predicted the largest mover was "the
trading result, −£21,609". That figure is `provisioned_net_gbp` — the company's own net **after bad
debt provisions** — which `run_history.headline_metrics` files under a key named `trading`. I read a
label and not a definition. It is not a trading line and it is not a driver of anything below.

### 2.4 THE ATTRIBUTION, closing exactly

Signed as effect on net (positive = helped the company):

| driver | Δ effect on net |
|---|---:|
| gross margin | **+£18,970.83** |
| bad debt | +£4,522.88 |
| capital cost | −£1,613.46 |
| policy levies (elec + gas) | −£10,817.14 |
| network costs (elec + gas) | **−£21,440.46** |
| **sum of named drivers** | **−£10,377.35** |
| observed Δ published net | **−£10,377.35** |
| **RESIDUAL** | **£0.0005** |

Against `margin_attribution`'s own £5,000 materiality floor, this reconciles. **Nothing is
unattributed and no plug was inserted.**

Underneath the gross line: revenue **+£86,313.95**, wholesale cost **+£67,343.12**. The book got
substantially bigger and bought substantially more energy.

### 2.5 THE SECOND RESULT: the fall is in the years the campaign cannot reach

Per year, the sign flips cleanly at 2021:

| | Δ revenue | Δ net | Δ active accounts (2016 / 2025) |
|---|---:|---:|---|
| 2016–2020 | **−£108,149.65** | **−£22,788.20** | 2016: 124 → 87 |
| 2021–2025 | **+£194,463.60** | **+£12,410.86** | 2025: 119 → 215 |

**The growth half added £12,411 of net. The early half removed £22,788.** The fall is not the cost of
growth; it is the pre-2021 book being *smaller* in the new run — 37 fewer active accounts in 2016, in
a year whose acquisition wins are **identical in both runs** (24 and 24, 32 and 32 in 2017).

And the marginal economics of the growth half are not dilutive: over 2021–2025, incremental gross
margin is **44.5%** of incremental revenue against **37.7%** for incremental network + policy
pass-through. New volume covers its own pass-through with margin left over. (The whole-window
equivalents — 22.0% and 37.4% — invert that, and are an artefact of averaging a shrinking book
against a growing one. They are the ratio it would be easiest to publish and the one that would be
wrong.)

### 2.6 WHICH COMMIT — closed structurally, without a re-run

Seven commits sit in the range. A full one-variable re-run at each is beyond one tick, so the
one-variable question was answered by reachability instead, which is stronger where it applies:

**Static import closure from `simulation.run_phase2b`** (129 first-party modules) versus the files
each commit touches:

| commit | touches run-reached code? |
|---|---|
| `248a6368e` the ceiling spent the whole budget on its most expensive cohort | **YES** — `net_new_acquisition`, `live_population`, `growth_mandate` |
| `20a375921` our prospect pool was published as the growth mandate | yes, but **3 non-comment lines**, all assigning the reported `binding` label on the capacity note |
| `a9e3e18dc` widening the market … is the one thing R13 names as never mine | yes, but **0 non-comment lines** — its own message says "nothing behavioural changes", and the diff agrees |
| `703e4dbb7` 28 months was DF, the dispute run | no — `settlement_timetable` / `settlement_reconciliation` are **not in the run's import closure** |
| `431cba42a`, `d108fa2d4`, `e09303c29` | no — documents and `tools/settlement_ceiling_probe.py`, which the run does not import |

**So `248a6368e` is the only commit in the range that can have moved the book**, at 132 non-comment
lines in the acquisition path. The settlement-finality work of the same morning, which looked like
the obvious suspect for a book whose early years shrank, cannot have touched it: the run never
imports either module.

**The limit of this argument, stated rather than left to the reader.** It is static. A closure walk
cannot see a dynamic import, and it proves *reachability*, not that the 132 lines produced this exact
£10,377. Grepping the run-reached modules for a string-keyed import of the settlement modules found
none. What would settle it completely is a run at `248a6368e^` with nothing else changed; that is
owed, and it is the only part of Part 1 that does not close here.

### 2.7 What this leaves standing

The direction offered two readings — "the growth loop working exactly as the thesis says" or "a cost
the machine imposed". **It is the second, and not in the place either of us was looking.** The growth
loop earned £12,411. The £10,377 fall is a **£22,788 loss in the pre-2021 book**, produced by a
budget-allocation change inside `248a6368e`, in years the campaign spend of 2021-2025 cannot reach.

Whether that early-book change is a repair or a regression is a separate question and is not
answered here. It is filed, not fixed on sight.

---

## PART 3 — R6's HEADROOM, RE-MEASURED ON TODAY'S BOOK

Measured, not projected: every figure below is read out of the published run artefact's own
`margin_call_book` and `wholesale_credit_exposure` blocks, not recomputed.

### 3.1 The figures, beside the ones they replace

| | R6 finding, as published | run A `d5d58da62` | **today, `9c626f05d`** |
|---|---:|---:|---:|
| net assets (treasury at the mark) | £337,305.65 | £364,800.92 | **£331,361.47** |
| accounts the code multiplies £130 by | 13 *(quoted)* / 24 *(used)* | 24 | **24** |
| MCR claim | £1,690 *(quoted)* | £3,120 | **£3,120** |
| **free equity** | **£335,615.65** | £361,680.92 | **£328,241.47** |
| gross marked exposure at 2025-06-07 | — | £66,017.62 | **£66,963.44** |
| independent amount demanded | £0.00 | £0.00 | **£0.00** |
| basis | `free_equity_covers_exposure` | same | **same** |
| **distance to the first collateral demand** | **£316,008.84** | £295,663.30 | **£261,278.03** |
| outstanding margin calls | — | 8 | **11** |
| peak NET exposure (2021-12-31) | £19,606.81 | £40,949.92 | **£41,513.41** |

**The mechanism still does not fire, and nothing was tuned to make it.** The distance is the answer.

### 3.2 Two exposures, and what each one counts

Said out loud because the trigger uses one of them and the headline quotes the other:

- **Gross marked exposure, £66,963.44** — the sum of what the book is worth against each
  counterparty at the mark date, un-netted. **This is the figure the trigger compares free equity
  against**, so it is the one the £261,278 distance is measured to.
- **Peak net exposure, £41,513.41 at 2021-12-31** — from the credit register's semi-annual
  point-in-time samples, *netted* per counterparty, and a peak over the decade rather than a reading
  at the mark. It is not the trigger's input and must not be subtracted from free equity.

### 3.3 THE RESULT: the headroom moved, and it moved the right way

**This is the first time the R6 channel has shown any signal at all.**

| | run A | today | Δ |
|---|---:|---:|---:|
| realised acquisition spend | £47,150.95 | £61,547.12 | **+£14,396.17** |
| free equity | £361,680.92 | £328,241.47 | **−£33,439.45** |
| distance to first demand | £295,663.30 | £261,278.03 | **−£34,385.27** |

The company spent £14,396 more on growth and its distance to the first collateral demand fell
£34,385. That is the CMA's sign. At this step size the company is roughly **7.6 further steps** from a
demand — an illustration, not a forecast, since the step is not a rate.

**What I cannot yet claim.** The distance fell by 2.4× the spend rise, so the spend rise is not the
whole of it — net assets are the treasury at the mark, and the same allocation change that moved the
book moved that too. Part 2's owed one-variable run at `248a6368e^` is what would separate
"acquisition spend weakened the balance sheet" from "the book changed and the balance sheet followed".
Until then this is a co-movement with the right sign, not an attributed mechanism, and it is written
that way on purpose.

### 3.4 The £248,798 figure is NOT published, and why this says so

The R6 finding's own correction (§4a) gives a corrected basis — 120 domestic billing accounts on
supply rather than 24 per-commodity legs — and quotes **free equity £315,761.47, distance
£248,798.03** on this same run.

**Neither that selector nor its census document is in any commit.** `saas/capital/solvency.py`'s
`mcr_accounts_on_supply` is uncommitted working-tree work, and
`docs/design/ACCOUNT_POPULATION_CENSUS_2026-08-29.md` is untracked. The live artefact this morning
published **£328,241.47 / £261,278.03**, on 24.

Both are recorded here, labelled. The published number is the one on the 24-leg basis because that is
what the shipped code computed; the corrected number is £12,480 worse and belongs in the record the
moment its selector lands. Quoting the corrected figure as though the site carried it would be the
same defect this repository committed twice this week — a bound generated by code in no commit — and
that is why the table in §3.1 uses 24.

---

## What this creates

1. **Owed: a one-variable run at `248a6368e^`.** It closes the last leg of Part 1 and separates the
   growth channel from the allocation change in Part 3.
2. **The pre-2021 book lost £22,788 of net and 37 accounts in 2016 on unchanged wins.** Repair or
   regression is unestablished. Not fixed on sight.
3. **`mcr_accounts_on_supply` is unlanded.** Every MCR figure the site publishes is on the 24-leg
   basis until it lands.
