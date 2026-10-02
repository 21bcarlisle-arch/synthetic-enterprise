**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `the-value-arms-churn-belief-calls-a-x2-renewal-optimal` (Lane 0 delivery)

# The value arm's churn belief prices the move from its own last price. The world prices the gap to the market

Follow-on 2 of `SEAT_FINDING_A_CHOSEN_FIXED_RENEWAL_IS_OUTSIDE_THE_CAP_AND_A_FIRST_TERM_IS_HELD_BY_THE_ACQUISITION_RULE_2026-10-02.md`.
It narrows `WORKER_FINDING_THE_RETENTION_BELIEFS_ANTI_RANKING_IS_ALL_IN_THE_RATE_TERM_AND_PB7_CANNOT_REACH_IT_2026-10-01.md`
from "the rate term" to one input of it. Measured only. No behaviour changed.

## Answer

**The belief's input is wrong, not its curve and not only its extrapolation.**
`churn_model.estimate_churn_probability` takes the offer's move from the household's **own previous
rate**, net of the market's move. The world (`customer_events.roll_lifecycle_event`) takes the
offer's **gap to the market reference**, in pounds. These two numbers are different things. A
household the arm already over-priced last term starts from a high old rate, so the next rise reads
small to the belief. The world sees the whole cumulative gap.

- Over the 18 rolled, repriced renewals with every field present, belief P(leave) and world P(leave)
  at the struck price correlate at **r = −0.12**.
- The world's price differential follows the household's old rate over the market reference at
  **r = +0.87**. The belief cannot see that ratio.
- Example: SYN-2016-001, 2019. The old rate was already 1.69× the market reference. The arm offered
  2.20× the capped rate. The belief read a +23% move and P(leave) 0.225. The world read +119% over
  the market and P(leave) 0.464.

The arm's own uplifts feed this. Each term's uncapped price becomes the next term's reference, so
the belief's reference ratchets upward with the arm's own prices. SYN-2016-008 shows it: 2020 old
160.8 → offered 208.6; 2021 old 209.5 → offered 283.0, at 1.94× the cap. The world churned it.

**The curve's shape also departs, but neither side is evidenced there.** At small gaps (×1.0–1.2) the
belief's churn rises 0.117 between capped and uncapped prices; the world's rises 0.011. At gaps of
70–120% over the market the belief stays at 0.22–0.44 and the world goes to 0.46–0.99. The world's
response above £400 of annual shortfall is its own continuation of the last informed slope
(`market_switching_propensity.churn_position_multiplier`, "WHAT IS ASSUMED"). That is not evidence
either. **The belief's +83.1% support bound** is the cap's own Oct-2022 step: a market-wide move,
which the belief nets out by construction. So it bounds the belief with evidence about a quantity
the belief has removed. 3 of 44 decisions hit it.

## The runs

Paired value-arm runs at HEAD `ed7e89d0e`, same commit, one variable: `fixed` in
`renewal_rate_chain.CAPPED_TARIFF_TYPES`. *capped* re-adds it. *uncapped* is HEAD as committed
(renewals uncapped, first terms held), which is the cited finding's *value landed*. The harness keeps
the world's full renewal events, which the cited runs had dropped. Harness:
`/var/tmp/se-churn-belief-out/measure.py`, `analyse.py`. Worktree `/var/tmp/se-churn-belief`.

| | capped | uncapped |
|---|---|---|
| renewal-chain calls | 2,249 | 2,215 |
| renewal-point events | 93 | 89 |
| churned billing accounts | 80 | 81 |
| total net £ | 91,626 | **93,913** |

**The cited headline does not reproduce at HEAD, and I correct it here beside the claim.** At
`db2184ec9` uncapping cost £3,587 and 7 accounts. At `ed7e89d0e` it earns £2,287 and costs 1
account. Two commits sit between (`6aa3653d7`, the SVT-conversion logging; `ed7e89d0e`, the
campaign quote before the win), and the book moved: 3,132 calls became 2,249. I cannot yet say which
moved the sign. Both are single-seed figures. Neither should be quoted as the value of uncapping.

## Where the 44 repriced decisions go

44 fixed decisions moved between arms (the cited finding counted 46 on its book). **The world can
respond to the price in 21 of them.**

| occasion | n | world response to price |
|---|---|---|
| rolled renewal | 21 (18 with every field) | yes: belief Δ +0.163, world Δ +0.134; churned 11 → 13 |
| SVT conversion (anniversary, `departure_rolled_at_renewal` False) | 19 | **none**. Mean ×1.42, max ×1.66 |
| gas leg riding the electricity decision | 4 | **none**. Up to ×2.25; the decision reads the electricity rate only |

**23 of 44 repriced decisions are priced where nothing in the world can press back.** On those, the
uncapped price is transfer the world cannot refuse. This is the same class as the price-blind first
term that `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES` holds. It is the likeliest reason the HEAD net is
positive, but that is a prediction (P4 below), not a result.

### Rolled renewals, sorted by the world's differential (uncapped arm)

`old/ref` is the old rate over the world's market reference. `own%` is the belief's input (move from
the old rate). `dif%` is the world's input (gap to the market).

| account | term | ×capped | old/ref | own% | dif% | belief | world | belief − world |
|---|---|---|---|---|---|---|---|---|
| SYN-2016-001 | 2019-01-01 | 2.20 | 1.69 | 23 | 119 | 0.225 | 0.464 | −0.240 |
| SYN-2016-007 | 2019-01-26 | 2.13 | 1.27 | 58 | 111 | 0.444 | 0.966 | −0.522 |
| SYN-2016-013 (gas) | 2020-02-24 | 2.08 | 1.41 | 37 | 102 | 0.329 | 0.985 | −0.656 |
| SYN-2016-060 | 2019-08-24 | 1.91 | 1.21 | 45 | 84 | 0.351 | 0.967 | −0.616 |
| SYN-2016-008 | 2021-01-25 | 1.94 | 1.22 | 35 | 73 | 0.243 | 0.979 | −0.736 |
| SYN-2016-019 | 2019-03-11 | 1.46 | 1.06 | 25 | 39 | 0.396 | 0.445 | −0.049 |
| SYN-2016-030 | 2020-04-13 | 1.28 | 1.09 | 8 | 23 | 0.267 | 0.890 | −0.623 |
| SYN-2016-063 | 2019-08-31 | 1.18 | 0.94 | 16 | 14 | 0.317 | 0.383 | −0.066 |
| PROS-2019-0240 | 2020-08-10 | 1.16 | 0.76 | 41 | 12 | 0.440 | 0.659 | −0.220 |
| PROS-2020-0188 | 2021-06-10 | 1.08 | 0.60 | 70 | 8 | 0.546 | 0.572 | −0.026 |
| C8 | 2020-03-31 | 1.24 | 1.07 | −5 | 6 | 0.068 | 0.848 | −0.780 |
| PROS-2016-0042 | 2019-02-09 | 1.08 | 0.90 | 11 | 6 | 0.472 | 0.479 | −0.007 |
| PROS-2019-0213 | 2020-07-15 | 1.05 | 0.68 | 46 | 5 | 0.475 | 0.789 | −0.314 |
| PROS-2018-0002 | 2019-01-02 | 1.04 | 0.75 | 31 | 3 | 0.957 | 0.420 | +0.537 |
| SYN-2016-034 | 2019-05-03 | 1.09 | 0.89 | 7 | −0 | 0.266 | 0.366 | −0.100 |
| C8 | 2019-04-01 | 1.10 | 0.91 | 5 | −0 | 0.247 | 0.336 | −0.089 |
| C9 | 2020-06-30 | 1.04 | 0.93 | −5 | −7 | 0.072 | 0.661 | −0.589 |
| C9 | 2019-07-01 | 1.00 | 0.82 | 2 | −13 | 0.152 | 0.313 | −0.160 |

The belief is below the world in 17 of 18. Where the gap to market is near zero (C8, C9, PROS-2019-0213)
the belief still misses by 0.3–0.8, so the level gap is not all price. It is the other world factors
the previous finding named. The anti-correlation is in the price input.

### SVT conversions and riding gas legs (no world response)

| account | fuel | term | ×capped | belief P(leave) |
|---|---|---|---|---|
| PROS-2017-0081 | elec | 2021-03-04 | 1.66 | 0.480 |
| SYN-2016-014 | gas | 2024-02-25 | 1.66 | 0.409 |
| SYN-2016-050 | gas | 2021-06-21 | 1.61 | 0.292 |
| PROS-2020-0177 | elec | 2024-05-30 | 1.61 | 0.378 |
| SYN-2016-050 | gas | 2019-06-22 | 1.55 | 0.366 |
| SYN-2016-060 | elec | 2021-08-23 | 1.54 | 0.374 |
| SYN-2016-057 | elec | 2024-08-14 | 1.53 | 0.448 |
| SYN-2016-055 | elec | 2023-08-03 | 1.52 | 0.037 |
| SYN-2016-057 | elec | 2021-08-15 | 1.52 | 0.480 |
| PROS-2019-0024 | elec | 2024-01-28 | 1.50 | 0.392 |
| SYN-2016-013 | gas | 2019-02-24 | 1.49 | 0.384 |
| SYN-2016-048 | elec | 2024-06-18 | 1.41 | 0.388 |
| SYN-2016-014 | gas | 2019-02-26 | 1.39 | 0.468 |
| SYN-2016-008 | elec | 2020-01-26 | 1.39 | 0.453 |
| PROS-2017-0064 | elec | 2024-02-14 | 1.26 | 0.281 |
| SYN-2016-030 | elec | 2019-04-14 | 1.17 | 0.484 |
| SYN-2016-020 | elec | 2020-03-10 | 1.07 | 0.297 |
| PROS-2016-0098 | elec | 2020-03-22 | 1.02 | 0.171 |
| SYN-2016-055 | elec | 2020-08-03 | 1.01 | 0.120 |
| PROS-2017-0064 | gas (rides elec) | 2024-02-14 | 2.25 | 0.440 |
| PROS-2020-0177 | gas (rides elec) | 2024-05-30 | 1.85 | 0.431 |
| PROS-2017-0081 | gas (rides elec) | 2021-03-04 | 1.84 | 0.206 |
| PROS-2019-0024 | gas (rides elec) | 2020-01-29 | 1.32 | 0.349 |

## The published evidence at large gaps

Searched first: `docs/market_research/churn_price_elasticity.md` §4 (the DESNZ savings curve:
saturates at 22% switching at ≥ £400 saved), `household_switching_response_amplitude.md`,
`svt_rates_active_passive_2016_2025.md` (CMA 2016: 70%+ stayed on the SVT with the cap £200–£350
above the cheapest fix), and the knowledge map's *Switching rates* and *world's departure LEVEL*
rows. **Nothing published measures one household's response to its own supplier pricing it 70–120%
above the market.** Every published figure is market-level, and the gaps it covers stop near
£300–£400 a year. That gap is unchanged, and this finding does not fill it. A remedy that
needs a number for the large-gap response is not licensed.

## A frame question for the director (practitioner side), not built on

In GB, a household that declines its supplier's renewal fix does not leave. It rolls onto that
supplier's default tariff, at or under the cap. So a fix offered at 2× the cap mostly goes unsold:
the household stays on the SVT and pays the cap. In this world an active fixed renewal has two
outcomes, stay at the offered fix or leave. An SVT conversion has one, accept the fix. If the
real third outcome (decline and stay on the SVT) is the dominant one, uncapped fix prices are
neither a churn risk nor a gain. They are mostly a no-sale. That would change what the value arm is
optimising. **My recommendation:** the world gets a price-aware *decline-the-fix, stay on default*
outcome at both the active renewal and the SVT conversion, sized from the published tariff-status
stock. Until then, the value arm's uncapped fixed prices are graded on outcomes the world cannot
produce. That is a world change, so it goes to the world lane blind to these results. It is not
done here.

## Pre-registered remedy (one variable, for the next run — written before it is run)

**Variable:** the reference the belief's rate term reads. `estimate_churn_probability` gets the
offer's position against the company's own reading of the published default tariff
(`published_svt_gbp_per_mwh`, already read at the renewal desk; public, so wall-safe). It no longer
reads the move from the household's previous rate net of the market. Same `RATE_SENSITIVITY`, size
scale and saturation. No new constant. The support bound stays as it is (a separate defect, listed
below). Same harness, same HEAD apart from that change, paired capped/uncapped value arms.

Predictions, graded on the uncapped arm against this record's table:

- **P1.** Across the rolled repriced renewals, corr(belief P(leave), world P(leave)) is **≥ +0.30**
  (from −0.12).
- **P2.** Fewer rolled renewals priced ≥ 1.5× capped: **≤ 2** (from 5). The max rolled ratio is
  **≤ 1.6** (from 2.20).
- **P3.** Churned accounts, uncapped minus capped: **≤ +1** (now +1). The repriced count may fall.
- **P4.** SVT-conversion repricings fall too: mean ratio **≤ 1.20** (from 1.42), because the belief
  now sees the offer's gap to the default tariff. Because those prices were transfer the world could
  not refuse, **uncapped net falls** against this record's £93,913. If net *rises*, P4's reading of
  where the HEAD gain came from is wrong.
- **Refutation shape.** If P1 holds and P2 fails, the input was right and the shape is binding:
  then the large-gap response is the open question, and it needs evidence, not a fit.

## Handed on

1. **The support bound** (`max_supported_rate_increase_pct`, +83.1%) is evidence about a market-wide
   move applied to a supplier-specific one. Re-key it to the largest *supplier-vs-market* gap with
   published switching evidence, or declare it a named gap. Do not pick a number.
2. **Uncapped fixed prices are graded where the world cannot answer**: 23 of 44. That is the frame
   question above (world lane). The riding gas leg is the existing "rival ledger sees only
   electricity" finding, reached from the pricing side.
3. **The −£3,587 headline** in the cited finding and in `THE_VALUE_CYCLE_REALISED_AB.md` is a
   single-seed figure that changes sign at HEAD. Any reader citing it needs this record.

## Addendum 2026-10-02 07:40Z: the remedy is built and held. P1–P4 are NOT graded yet

Claim `the-belief-reads-the-gap-to-the-published-default` (DIRECTION item four). The code and its
controls are in
`docs/staging/records/SEAT_HELD_THE_BELIEF_READS_THE_GAP_TO_THE_PUBLISHED_DEFAULT_BUILT_AT_FDABAA5A9_2026-10-02.md`,
as a diff against `fdabaa5a9`. Six mutations bite. It is not on main.

**Why it is held, not landed.** Item four is ordered after items two and three. Item two (the world-D
retake at `f18e8b5dc`) is still on the box, and item three (decline-and-stay) is pre-registered but
not built. The value-arms page withdraws any reading whose `company/` paths differ from the
publishing HEAD unless an exemption is argued. This change moves the arms by design, so no honest
exemption exists. Landing it now would withdraw the retake that item two is about to publish. The
graded runs need the change on main, but not before item two lands.

**A static check, not the graded run.** The company's reading of the published default
(`cap_ceiling_ex_vat`, single-rate, EPG-net, ex-VAT) was printed against this record's own 21
rolled renewals. It reproduces the world's `price_differential_vs_market_reference` exactly on all
21 (r = 1.00, the same value on every row). So the input is the world's quantity on the world's VAT
and EPG basis. Correlation of the input alone with world P(leave) is +0.47 for the gap and +0.31 for
the old move. The old belief's output correlates at −0.03 over these 21 (−0.12 over the 18 with
both arms present). This is a replay of prices the old belief chose. It does not grade P1, because
the arm will set different prices once it reads the new input.

**The run that grades it, when it can.** After item two's unit exits and item three lands, apply
the diff on that HEAD and land it. Then run paired capped and uncapped value arms serially on that
one commit, with `measure.py` and `analyse.py` re-pointed at a worktree of it. Grade P1–P4 against
this record's table, and the net against the floor's spread from item two's 3-seed floor. **One
caveat to the one-variable reading:** on item three's world, the SVT-conversion rows can answer
price, so P4's "uncapped net falls" compares against a baseline on a different world. Re-run the
uncapped arm WITHOUT the diff on the same commit as the baseline, which makes three runs, not two.
The predictions above are unchanged.
