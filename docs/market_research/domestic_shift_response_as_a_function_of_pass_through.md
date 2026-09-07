# Domestic shift response as a function of tariff pass-through

**Knowledge:** how-households-choose

*(§3's bridge — what price ratio a household actually faces once the wholesale shape is diluted
through the retail stack — also feeds `the-price-a-household-is-shown`. The response itself is a
choice a household makes, so it lands here.)*

**Read and measured 2026-09-07.** Claim `a49-shift-response-as-a-function-of-pass-through`.
**Subject:** the first named gap in `docs/observability/tou_sharing_ceiling.json` — *"THE SHIFT
RESPONSE as a function of pass-through ... nothing in the knowledge layer, the commons or the
market research establishes one. A question to research."*

Pre-registration, filed before a single source was opened:
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_THE_PUBLISHED_RECORD_WILL_SAY_ABOUT_DOMESTIC_SHIFT_RESPONSE_2026-09-07.md`.
It is graded at the foot of this file, including where it was wrong.

---

## THE HEADLINE, AND IT IS NOT THE ONE THE ITEM EXPECTED

**The shift response function IS established. What is NOT established — and what this measurement
found instead — is that this book's own price panel cannot produce a price signal inside the range
where that function was estimated.**

There is a fitted, published, multi-pilot function relating domestic peak reduction to the
peak-to-off-peak price ratio: the **Arcturus 2.0 arc** (§1). It reproduces its own paper's stated
points exactly (§1.2) and it is corroborated at GB ratios by the two large GB trials (§2).

But when the frontier's pass-through α is carried through to the price ratio a household on this
book would actually face (§3, measured on the same 1,483-day Elexon MID panel the ceiling is
computed on), the answer at **full** pass-through is a ratio of **1.26:1** at the median day. The
Arcturus arc is estimated on ratios from about **2:1 to 35:1**. Ofgem's own reading of the GB trial
evidence is that *"a price difference of a factor of about three is required to produce a material
behavioural response"*.

So the honest published answer to "where is the interior optimum" is a **refusal with a named
reason**: on the 2016–2020 panel, **no pass-through puts the household inside the range where the
response is established**, and the arc's value there is an extrapolation below its own sample.

**This does not retire the time-of-use product.** It says the binding constraint is the *within-day
wholesale spread on this panel*, not the household's willingness — and the panel deliberately ends
2020-12, before the episode when spreads were widest. That is a testable next step, not a verdict.

---

## 1. The function

### 1.1 Arcturus 2.0 — the fitted arc

Faruqui & Sergici, *"Arcturus 2.0: A Meta-Analysis of Time-Varying Rates for Electricity"*, The
Electricity Journal, 2017. **337 pricing treatments from 63 pilots in nine countries on four
continents.** Presented to the CPUC 2017 Electric Rate Forum; that copy is the one read here.

    y = a + b·ln(price ratio) + c·ln(price ratio)·tech

`y` = peak demand reduction as a proportion; `price ratio` = peak to off-peak; `tech` = 1 when
enabling technology is supplied with the price.

| Term | Primary (Fig. 12) | With opt-out control (Fig. 13, col. 2) |
|---|---|---|
| ln(peak/off-peak ratio) | **−0.065*** (0.007) | **−0.058*** (0.007) |
| ln(ratio) × technology | **−0.046*** (0.008) | **−0.047*** (0.008) |
| Opt-out binary | — | **+0.039*** (0.009) |
| Constant | −0.011 (0.007) | **−0.028*** (0.009) |
| Observations | 335 | 335 |
| R² | 0.569 | 0.588 |

Robust MM-estimation (`robustbase` in R), which down-weights outlying pilots. Two pilots testing
ratios above 35:1 were dropped as extreme. `***` is p<0.01.

**THE OPT-OUT COEFFICIENT IS THE ONE THIS BOOK NEEDS AND IT IS THE ONE NOBODY QUOTES.** 84% of
Arcturus treatments are **opt-in** — self-selected volunteers. A supplier moving its existing book
onto a time-of-use tariff is doing the **opt-out** thing, and the published penalty for that is
**+3.9 percentage points of peak usage retained**, which at the ratios in play roughly *halves* the
response. Every headline figure from a ToU trial is an opt-in figure unless it says otherwise.

### 1.2 It reproduces its own paper's points — checked before it was used

CLAUDE.md: *print the numbers at real inputs before you ship a formula*. Run before anything was
written down:

| Input | Model | The paper's own sentence |
|---|---|---|
| ratio 2:1, no tech | 5.61% reduction → consumes 94.4% | "drop his or her demand by 5% and consume 95%" |
| ratio 4:1, no tech | 10.11% → consumes 89.9% | "will consume 90%" |
| ratio 2:1, with tech | 8.79% → consumes 91.2% | "will consume 91%" |
| ratio 4:1, with tech | 16.49% → consumes 83.5% | "will consume 84%" |

Four for four. The coefficients as transcribed are the coefficients that produced the paper's arc.

### 1.3 The arc across the range

Peak reduction, %. Opt-out columns use the Fig. 13 specification including its own constant.

| ratio | opt-in, no tech | opt-in, +tech | **opt-out, no tech** | opt-out, +tech |
|---|---|---|---|---|
| 1.25 | 2.6 | 3.6 | 0.2 | 1.2 |
| 1.50 | 3.7 | 5.6 | 1.3 | 3.2 |
| 2.00 | 5.6 | 8.8 | **2.9** | 6.2 |
| 2.88 | 8.0 | 12.8 | **5.0** | 10.0 |
| 4.00 | 10.1 | 16.5 | 6.9 | 13.5 |
| 5.71 | 12.4 | 20.4 | 9.0 | 17.2 |
| 8.00 | 14.6 | 24.2 | 11.0 | 20.7 |
| 16.80 | 19.4 | 32.4 | 15.3 | 28.5 |
| 35.00 | 24.2 | 40.6 | 19.5 | 36.2 |

Rows below 2:1 are **outside the estimation range** and are printed so the extrapolation in §3 is
visible rather than hidden.

---

## 2. The GB evidence, and it brackets the arc

### 2.1 CLNR — a static ToU tariff at a ratio the arc covers

Customer-Led Network Revolution (Northern Powergrid / British Gas / Durham University), closedown
2015. Domestic ToU test cell: **628 participants**, three-band static tariff with an in-home
display. Rates relative to the flat tariff: **peak (16:00–20:00) +99%**, day (07:00–16:00) −4%,
**off-peak (20:00–07:00) −31%**.

That is a peak-to-off-peak ratio of **1.99 / 0.69 = 2.88:1** — inside the arc's range.

- **Observed: ~10% average peak load shift**; annual maximum household peak lower by **261 W of
  4,188 W = 6.2%**.
- **Arc at 2.88:1 — opt-in 8.0%, opt-out 5.0%.**

The observed 6.2%–10% **brackets** the arc's 8.0%. This is the single strongest corroboration in
this file: a GB static ToU tariff, at a ratio the international meta-analysis covers, lands on the
international meta-analysis's own prediction.

### 2.2 Low Carbon London — a dynamic tariff at a much higher ratio

UK Power Networks / EDF Energy / Imperial College, closedown 2015. **1,119 households** recruited
to a dynamic ToU tariff for the whole of 2013; 185 price events called; day-ahead notification via
in-home display and optional SMS.

Rates: **high 67.20 p/kWh, default 11.76 p/kWh, low 3.99 p/kWh** → high/default **5.71:1**,
high/low **16.84:1**.

- **Observed: 56 W mean load reduction per household during high-price events in winter, 34 W in
  summer.** The closedown report states the response in **watts, not as a percentage** — it does
  not publish the denominator.
- Converting requires a winter-evening demand denominator this source does not give. At 0.7–1.3 kW
  the 56 W is **4.3%–8.0%**.
- **Arc at 5.71:1 — opt-in 12.4%.**

**LCL sits at roughly half the arc, and I am recording that as a disagreement rather than
smoothing it.** Candidate reasons, none of which this file establishes: LCL's response is measured
against events rather than a persistent peak period; the 56 W is a mean over all recruits including
non-responders; and a dynamic tariff's *notified* events are not the *habitual* peak a static ToU
trains. The direction matters and is the conservative one — GB at or below the international arc.

### 2.3 Ofgem's own elasticities, and why they are not the function

Ofgem, *Distributional impact of time of use tariffs*, 2017 — the GB regulator's own modelling,
with elasticities **derived from the LCL trial data** (Annex D). Ofgem rejected a control-group
price elasticity as inconsistent and used an **elasticity of substitution** between LCL's price
points, resolved to each half hour (Table D.1): magnitudes **0.03 to 0.16**, peaking at **0.16 at
15:00** and **0.14–0.15 across 14:30–17:00**, falling to 0.03–0.05 overnight and late evening.

**These are a LOCAL elasticity and they are not a function of pass-through.** Ofgem's form is
linear in the relative price change, so `reduction = ε × (ratio − 1)`; at ε = 0.15 that reaches
100% by a ratio of 7.7:1 and exceeds it beyond. It cannot be extrapolated and Ofgem does not
extrapolate it. Ofgem's own cautions, quoted because they are load-bearing:

> "even the largest elasticities indicate relatively modest price responsiveness" · "one should
> concentrate on the broad shape rather than specific values" · the LCL basis "limits the external
> validity of the results, which cannot systematically be generalised to the entire population" ·
> "We embedded short-term elasticities only."

**The sentence from this source that most changes the answer**, and it is independent of Arcturus:

> "In experiments with two prices, it is generally found that **a price difference of a factor of
> about three is required to produce a material behavioural response.**"

Ofgem also finds responsiveness **highest among middle-income groups** and **lower at both ends** —
wealthy households and, importantly, the vulnerable groups ('Struggling Estate', 'Young Hardship',
'Difficult Circumstances'), for whom Ofgem's stated reason is that discretionary consumption has
already been squeezed out. A response function applied uniformly across a book will therefore
over-predict for exactly the households whose bills we most want to move.

### 2.4 Octopus Agile — read, and deliberately not used as a level

Octopus's own report on Agile claims **28.19% of peak use shifted** after six months. This is the
most-cited GB number and it is **not usable as this book's response**: it is a self-selected,
opt-in, high-engagement population that actively chose a half-hourly wholesale-tracking tariff,
with heavy EV representation (Octopus's own report identifies EV drivers as showing the greatest
behaviour change). Under Arcturus's own decomposition that is the **opt-in, with-enabling-technology,
high-price-ratio** corner — the top of the top column of §1.3. It is recorded here as the
**upper witness** and is not carried into any figure.

---

## 3. The bridge — from pass-through to the ratio a household actually faces

**This is P0 of the pre-registration and it was right: no source measures response against
pass-through.** The literature is keyed on a **price ratio**; the frontier is keyed on a **share of
created value**. The two are joined by arithmetic on this repository's own price series, not by a
number picked to fill the slot.

A revenue-neutral pass-through tariff sets the household's unit rate in half-hour *t* to

    rate(t) = R · [ 1 + α · s · ( P(t)/P̄ − 1 ) ]

where α is the pass-through, `s` is the **commodity share of the unit rate**, P(t) the half-hourly
wholesale price and P̄ the day's mean. At α = 0 the rate is flat; at α = 1 the household sees the
full wholesale shape, diluted by the non-commodity part of the rate it is embedded in. So

    ratio(α, s) = [1 + α·s·(peak_rel − 1)] / [1 + α·s·(off_rel − 1)]

### 3.1 What the panel's own price shape offers

Measured on the **same 1,483 whole days of Elexon MID (2016-09 → 2020-12)** and the **same
6-half-hour shift window** the sharing ceiling uses:

| within-day wholesale ratio (dearest 6 HH / cheapest 6 HH) | p10 | p25 | **median** | p75 | p90 |
|---|---|---|---|---|---|
| | 1.44 | 1.56 | **1.77** | 2.27 | 3.36 |

Median dearest-window / day-mean **1.330**; median cheapest-window / day-mean **0.761**.

**The raw wholesale spread on this panel is 1.77:1 at the median day** — already below the 2:1 that
is the lowest ratio Arcturus illustrates, and well below Ofgem's factor of three, *before any
retail dilution at all.*

### 3.2 The ratio the household faces, day by day

Response computed **per day and then averaged** — not the response at the average ratio, which
would be a different quantity through a concave function.

| s | α | faced ratio p50 | p90 | days ≥ 2:1 | mean response, opt-in | mean response, **opt-out** |
|---|---|---|---|---|---|---|
| 0.40 | 0.50 | 1.12 | 1.25 | 0.1% | 1.98% | **0.07%** |
| 0.40 | 1.00 | 1.26 | 1.56 | 2.0% | 2.86% | **0.53%** |
| 1.00 | 0.50 | 1.33 | 1.75 | 5.3% | 3.31% | **0.89%** |
| 1.00 | 1.00 | 1.77 | 3.36 | 34.4% | 5.80% | **3.10%** |

`s = 1.00` is the unphysical bound where the *entire* unit rate tracks wholesale; it is carried to
show the ceiling of the bridge itself. Even there, at full pass-through, only a third of days reach
2:1.

### 3.3 `s` was already half-answered in the knowledge layer

I wrote §3.2's grid expecting `s` to be an open gap, then followed the thread. **It is partly
here already.** `docs/institutional/knowledge_map.md`, "Cap formula" row, confidence H:

> "Bottom-up: **wholesale (~40%)** + network (~23%) + policy (~13%) + opex (~17%) + EBIT (~2%) +
> VAT (5%)."

So **`s = 0.40` is the best-supported row of the grid**, not an arbitrary middle one, and the
figures to read in §3.2 and §4 are its two.

**It is not the whole answer, and the residual error has a known sign.** That 40% is wholesale as a
share of the **cap as a whole**, and `s` is the commodity share of the **unit rate alone**. The
standing charge carries network residual and other fixed costs that the unit rate then does not,
so the commodity share *of the unit rate specifically* is **higher than 40%** — which pushes the
faced ratio, and every figure in §4, **up**. The `s = 0.55` row is carried for that reason and is
the conservative-against-my-own-conclusion direction. Reading the cap's unit-rate composition
directly, rather than inferring it from the bill-level split, is gap 1 in §5 and it is a small job.

This is the CLAUDE.md rule paying out exactly as written: *the answer is usually already here.* The
grid above remains the honest publication — publish the curve, name the residual gap — but it is
now an anchored grid rather than an unanchored one.

---

## 4. Where the optimum sits, and why that is still a refusal

Company take at pass-through α, at shiftable share 1.0, against the landed ceiling of **£51.36 per
household-year**:

    company(α) = £51.36 · response(α) · (1 − α)

| s | recruitment | **argmax α** | company £/hh-yr | household £/hh-yr | response at optimum |
|---|---|---|---|---|---|
| 0.30 | opt-in | 0.090 | 0.570 | 0.056 | 1.22% |
| 0.30 | **opt-out** | 0.765 | 0.013 | 0.043 | 0.11% |
| 0.40 | opt-in | 0.190 | 0.598 | 0.140 | 1.44% |
| 0.40 | **opt-out** | 0.740 | 0.032 | 0.091 | 0.24% |
| 0.55 | opt-in | 0.270 | 0.659 | 0.244 | 1.76% |
| 0.55 | **opt-out** | 0.715 | 0.075 | 0.187 | 0.51% |
| 1.00 | opt-in | 0.375 | 0.883 | 0.530 | 2.75% |
| 1.00 | **opt-out** | 0.645 | 0.266 | 0.483 | 1.46% |

**The optimum is interior in every case, which is what the ceiling already proved without an
elasticity — so that column is a confirmation, not news.** What is news is the two things beside it:

1. **The LOCATION is not established.** α* ranges from **0.09 to 0.77** across assumptions nobody
   has settled — a factor of eight on the one number the item wanted. It is not a modelling
   detail: it is the difference between a tariff that shares a tenth of what it creates and one
   that shares three quarters.
2. **The LEVEL is negligible on this panel.** £0.01–£0.88 per household-year against a £51.36
   ceiling, and that is still **at shiftable share 1.0** — R3's gap, which multiplies. A realistic
   shiftable share takes it below a penny in the opt-out cases.

**A tautology I nearly published, recorded because it looked like a result.** Scaling the whole arc
by any constant leaves α* exactly unchanged — I ran it across ×0.25 to ×4 and got 0.190 every time,
and it reads like a robustness finding. It is arithmetic: `argmax k·f = argmax f` for any k > 0. It
says nothing about the world and it is not evidence that the location is stable. The location's
real sensitivity is to the arc's **curvature**, to `s`, and to **opt-in versus opt-out** — and the
table above shows it is not stable in any of them.

**And the whole table is an extrapolation below the evidence.** Every faced ratio in §3.2 except the
tail of the last row is under 2:1, where Arcturus has no observations and where Ofgem says no
material response should be expected. These figures are what the fitted arc *says* down there. They
are not what anybody has measured.

---

## 5. What is established, and what the gap now is

**ESTABLISHED and citable:**
- The response function against price ratio: Arcturus 2.0, coefficients in §1.1, verified in §1.2.
- The opt-out penalty of +3.9pp, which applies to this book and to almost no published headline.
- GB corroboration at 2.88:1 (CLNR, §2.1); a GB reading at roughly half the arc at 5.71:1 (LCL, §2.2).
- The direction of the sociodemographic gradient: response is lowest among the most constrained.
- **This book's own within-day wholesale spread: median 1.77:1 over 1,483 days (§3.1).**

**THE GAP HAS CHANGED SHAPE, and this is the part to carry forward.** It is no longer "what is the
shift response" — that is answered. It is now three things, in this order:

1. **`s`, the commodity share of the domestic electricity UNIT RATE.** Now **partly anchored**
   (§3.3): the knowledge map already carries wholesale ≈ 40% of the cap at confidence H, which
   makes `s = 0.40` the row to read. What is still owed is the cap's **unit-rate** composition
   rather than its bill-level split — the standing charge carries fixed costs the unit rate does
   not, so the true `s` is **above 0.40** and every §4 figure is understated. Read directly from
   Ofgem's cap component breakdown. **A half-day's reading, and it is the cheapest thing on this
   list.**
2. **Does the 2021–2023 episode put the ratio inside the evidence range?** The panel ends 2020-12
   by construction and the ceiling already names this. If within-day spreads in those years reach
   3:1 after retail dilution, every figure in §4 is superseded and the product is a different
   question. This is the highest-value measurement named in this file.
3. **Persistence.** P4 of the pre-registration, and it survives: LCL ran one year, and 70% of its
   participants reported *some* practices persisting past the trial — a stated-preference figure,
   not a measurement. Ofgem embedded short-term elasticities only and said so.

**NOT established and deliberately left empty:** any response to a carbon signal at zero
pass-through. The ceiling names carbon as the one thing that still moves at α = 0; no source read
here measures a money-free domestic carbon shift response, and none is invented.

---

## 6. The pre-registration, graded

| | Predicted | Outcome |
|---|---|---|
| **P0** | No source measures response against pass-through; the deliverable is a bridge plus a response function, and the bridge is computable from our own data | **BORNE OUT**, and it was the whole difficulty. §3. |
| **P1** | No continuous GB function; one international meta-analysis with a concave saturating arc split by enabling technology; GB points below the international central case; Octopus unrepresentative upward | **BORNE OUT in full.** Arcturus 2.0; LCL at ~half the arc; Octopus at 28% and set aside. I did *not* predict the opt-out coefficient, which turned out to be the most important single number for this book. |
| **P2** | 3%–10% without tech, 15%–30% with, at a ratio of 2–3x | **BORNE OUT for the with-tech band** (8.8%–13.3% at 2–3:1 is under my 15–30%, so partly wrong) **and too high for without-tech**: 5.6%–8.2% opt-in, 2.9%–5.3% opt-out. My band was an opt-in band and I did not know to say so. |
| **P3a** | Composing a real response brings the figure down by roughly one order of magnitude to single-digit pounds | **WRONG, and wrong in the direction that matters.** It is £0.01–£0.88 — one to *three* orders of magnitude down, and single-digit pounds only in the unphysical `s = 1` corner. |
| **P3b** | The interior optimum sits nearer α = 0.6 than α = 0.3 | **REFUTED as a single answer.** α* is 0.09–0.77 depending on `s` and recruitment. It is near 0.6–0.77 for opt-out and near 0.09–0.27 for opt-in, and I gave one number where the evidence supports a range. Held weakly and correctly so. |
| **P3c** | *(implied)* the reason the reachable figure falls is the household's limited willingness | **REFUTED, and this is the finding I did not predict at all.** The binding constraint is the **panel's own within-day spread**, not the household. Even a perfectly willing household is offered 1.26:1. |
| **P4** | Persistence, carbon-signal response and the shiftable share will not be establishable | **BORNE OUT.** All three are still open and are filed as gaps, not filled. |

---

## Sources

- Faruqui, A. & Sergici, S., *Arcturus 2.0: A Meta-Analysis of Time-Varying Rates for Electricity*,
  The Electricity Journal, 2017 — [CPUC 2017 Electric Rate Forum copy](https://www.cpuc.ca.gov/-/media/cpuc-website/divisions/energy-division/documents/electric-rates/2017-electric-rate-forum/2017-arcturus-2-0-10122017.pdf)
- Ofgem, *Distributional Impact of Time of Use Tariffs*, 2017 —
  [ofgem.gov.uk](https://www.ofgem.gov.uk/sites/default/files/docs/2017/07/distributional_impact_of_time_of_use_tariffs_1.pdf)
  (elasticities in Annex D, Table D.1)
- UK Power Networks, *Low Carbon London Project Closedown Report*, 2015 —
  [ofgem.gov.uk](https://www.ofgem.gov.uk/sites/default/files/docs/2015/04/lcl_close_down_report_0.pdf)
- Northern Powergrid, *Customer-Led Network Revolution Project Closedown Report*, 2015 —
  [ofgem.gov.uk](https://www.ofgem.gov.uk/sites/default/files/docs/2015/05/clnr-g026_project_closedown_report_final_v2.pdf);
  ToU tariff structure via [CLNR domestic customer trials](http://www.networkrevolution.co.uk/customer-trials/domestic-customer-trials/)
- Octopus Energy, *Agile Octopus — A consumer-led shift to a low carbon future*, 2018 —
  [octopus.energy](https://octoenergy-production-media.s3.amazonaws.com/documents/agile-report.pdf)
  (recorded as an upper witness only, §2.4)
- Price panel: Elexon MID via `sim/market_index_history.py`, 1,483 whole days 2016-09 → 2020-12 —
  the same panel and the same 6-half-hour window as `docs/observability/tou_sharing_ceiling.json`.
