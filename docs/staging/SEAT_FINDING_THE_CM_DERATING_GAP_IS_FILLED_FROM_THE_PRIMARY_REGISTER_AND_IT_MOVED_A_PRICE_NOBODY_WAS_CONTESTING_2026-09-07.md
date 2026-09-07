**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a50-cm-derating-and-the-ic-leg

# The CM de-rating gap is filled from the publisher's own register — and it moved a price nobody was contesting

**Found:** 2026-09-07, delivery seat, claim `a50-cm-derating-and-the-ic-leg`.
**Pre-registration:** `SEAT_PREREGISTRATION_THE_CM_DERATING_FETCH_AND_THE_TWO_CONTESTED_YEARS_2026-09-07.md`, written before any price was read.

## The 403 was a 404, and that is the whole reason this was open

The v1 pass recorded: *"The EMR Delivery Body register (emrdeliverybody.com) returned HTTP 403 to
this pass on 2026-09-07, so no figure here was read from the publisher's own auction result."*

It does not return 403. **That host is retired and returns 404 to everything** — the register moved
to the NESO data portal, where it is served without authentication as CSV over a public CKAN API.
Two `curl`s got the whole thing: 801 de-rating rows across 25 auctions, and clearing prices and
awarded volumes for all 25.

A blocked host and a moved host look identical if you read only the first digit of the status class,
and they lead to opposite next actions — one is a dead end you record as a limit, the other is a
redirect nobody followed. The limit was recorded, correctly and honestly, and it was the wrong limit.
**Both URLs are now in the artefact under `source_urls` so the next pass re-fetches rather than
re-searches.**

## What the de-rating gap was actually worth

The drawn item states the overstatement as **£632/site/yr at 2024 prices on a 35 kW site**. That is
the *entire gross CM leg* for that site-year (£630.00), not the overstatement. It is what you get by
reading "overstated by the whole de-rating factor" as "overstated by 100%".

A de-rating factor is a multiplier, so the overstatement is `1/f − 1`, not `1`. At the published
DY 2024/25 T-4 DSR factor of **0.7921**:

| DY | T-4 price | DSR factor | rated £ | de-rated £ | overstated by |
|---|---|---|---|---|---|
| 2018 | 19.40 | 0.8970 | 679.00 | 609.06 | 69.94 |
| 2019 | 18.00 | 0.8680 | 630.00 | 546.84 | 83.16 |
| 2020 | 22.50 | 0.8688 | 787.50 | 684.18 | 103.32 |
| 2021 | 8.40 | 0.8634 | 294.00 | 253.84 | 40.16 |
| 2022 | 6.44 *(T-3)* | 0.8614 | 225.40 | 194.16 | 31.24 |
| 2023 | 15.97 | 0.8614 | 558.95 | 481.48 | 77.47 |
| 2024 | 18.00 | 0.7921 | 630.00 | 499.02 | **130.98** |
| 2025 | 30.59 | 0.7845 | 1,070.65 | 839.93 | 230.72 |
| **2018–2025** | | | **4,875.50** | **4,108.51** | **766.99 (18.7%)** |

**Pre-registered prediction 3 was "of order £130/site/yr, and the drawn item's £632 is off by a
factor of ~4.8". The answer is £130.98 and 4.81.** Also as predicted, the "35 kW site" is not a
35 kW site: this module's flex is 10% of peak, so 35 kW of flex is a **350 kW peak, ~2.0 GWh/yr**
consumer — essentially the module's own largest example customer.

The leg was really overstated by **12–28%**, not 100%. Still the largest known overstatement in the
subsystem, and still worth fixing; but a finding that overstates its own overstatement by 4.8x is
the kind that gets a real defect dismissed when someone checks it.

## The two contested years are settled, and a third entry that was NOT contested was wrong

Both pre-registered predictions held:

| | v1 artefact | primary register | prediction |
|---|---|---|---|
| DY 2023/24 T-1 | `null`, contested (Ofgem £60 vs Montel £45) | **£60.00** | ✅ predicted £60, Montel slipped |
| DY 2025/26 T-4 | `null`, contested (Montel £30.59 vs S&P £35.30) | **£30.59** | ✅ predicted £30.59 |

**And then the one nobody had flagged.** DY 2021/22's T-1 was carried as £60.00 on Montel alone, not
marked contested. The register says **£45.00**. The two figures had been **transposed** between two
delivery years by one source: £45.00 belongs to 2021/22 and £60.00 to 2023/24, and Montel had them
the other way round.

> **A contest flag marks one year. A transposition damages two.** The v1 pass reasoned its way to
> "the signature of a one-year attribution slip in one of them" — which was *right about the source
> and right about the year* — and then flagged only the year where the two sources visibly
> disagreed. The other half of the same single error sat in a field that looked settled, because
> nothing disagreed with it: the corroborating source simply had no entry for that year.
>
> **Where one source is uncorroborated and another source's nearby entry is contested, the
> uncorroborated one is not "settled" — it is unexamined.** The v1 artefact even said so in prose
> ("rests on a single analyst review and is NOT corroborated by the Ofgem annex") and still served
> the figure at full confidence.

My pre-registration named this hazard as the *wrong* branch: *"the shape of being wrong is: the
register says £45.00, Ofgem is the slipped source, and our DY 2021/22 T-1 entry becomes suspect
too."* The suspicion was right and the conditional was wrong — the 2021/22 entry was wrong
**regardless of which way the slip went**, because a transposition has no innocent direction.

Two further v1 entries the register corrects, both `not_applicable` — which asserts *no such auction
existed*:

- **DY 2017/18 T-1 → £6.95** over **54,433.6 MW**. The publisher's own name for it is "2017-18 (T-1)
  One Year Ahead Capacity Auction". The v1 pass called it a transitional "Early Auction", refused to
  serve a T-1 price for the year, and recorded its volume as "~1 GW" — off by **54x**.
- **DY 2026/27 T-1 → £5.00.** The v1 pass had no way to say "not yet held" and used the level that
  asserts it never happens. The artefact now carries `not_yet_held` as a distinct provenance.

Every surviving v1 figure — 2018, 2019, 2020, 2022, 2024 and the 2026–2028 T-4s — was confirmed by
the register **exactly**. The secondary pass was good work; its failures were all in the same place,
which is where it had one source instead of two.

## The sharp edge: a price and a factor from two different auctions

DY 2022/23's T-4 was suspended and replaced by a T-3. **The T-3's price sits in the row's `t4`
field**, so `clearing_price(2022, "T-4")` returns a T-3 number and nothing about that number says
so. The register publishes de-rating factors for *both* auctions and they differ: **T-3 0.8614,
suspended T-4 0.8428.**

A caller multiplying the module's own price lookup by the module's own factor lookup would have
crossed two auctions and produced a number with no auction behind it — this module's founding defect
in miniature, one function away from the code written to prevent it. So the price and the factor are
never fetched separately: `derated_price_gbp_per_kw_year()` resolves both through
`auction_actually_held()`, and crossing them is not possible rather than merely discouraged.

## Two corrections to my own claims, kept beside them

**1. I wrote the round-pairing offset as N and it is N−1.** The pre-registration asserted, as an
already-established fact, that "T-4 for DY *Y* carries the identical factor to T-1 for DY *Y−4*".
It does not: the identity is **T-4[Y] == T-1[Y−3]**, because a T-4 held in February of year *H*
delivers from October *H+3*. At Y−4, **zero** of nine pairs match; at Y−3, all of them do.

The control I wrote refuted it on its first run. The worked example in my own pre-registration
("T-4 DY2029/30 and T-1 DY2026/27 are both 0.8558") is a *three*-year gap — I had the right pair and
the wrong formula, in a paragraph warning about a four-year offset, and read it three times without
seeing it. An off-by-one inside a caution about an off-by-one is the most re-enterable trap here; it
is named in the code, the artefact and the test rather than quietly fixed.

The general rule, which the substituted T-3 also obeys (T-3[2022] == T-1[2020]): **T-N[Y] and
T-1[Y−N+1] are the same auction round.**

**2. "Duration-dependent for DSR and storage" is wrong about DSR.** Both the v1 artefact and the
drawn item say de-rating is duration-dependent for DSR *and* storage. The register says **DSR carries
one factor per auction** and only `Storage` is duration-split (0.5h → 12h). The I&C leg therefore
needs no duration model, which is the difference between this being a one-turn job and a blocked one.

## What is still not established

- **£35.30 vs £30.59 for DY 2025/26.** Same auction — S&P's "~42.7 GW" against the register's
  42,364.3 MW awarded — reported in two bases. The ratio is 1.154. The guess that this is indexation
  from a fixed price base is *still only a guess* and is recorded as one; the clearing price no
  longer depends on settling it.
- **What an aggregator passes through to a member.** Bilateral, unpublished, and still the reason
  the domestic leg refuses. The de-rating gap closing does not touch it.

## What landed

- **Artefact** (14 KB → 62 KB): every clearing price now `primary`; the full 25-auction, all-class
  de-rating register embedded; `t4_auction_actually_held`, awarded volumes, `not_yet_held`,
  `source_urls`, and `what_the_primary_pass_changed`.
- **`capacity_market_published_record`**: `derating_factor(class, year, auction)` serves real
  numbers; `auction_actually_held()`; `derated_price_gbp_per_kw_year()`; `DSR_TECHNOLOGY_CLASS`;
  `_load_derating()` fails closed. `LATEST_ESTABLISHED_T4_DELIVERY_YEAR` is now **derived** — it was
  the literal `2024` and went stale the moment DY 2025/26 was settled, which is a constant keyed to
  today's answer going wrong precisely when the record gets *better*.
- **`ic_flexibility_revenue`**: the CM leg is de-rated; `cm_derating_factor` on every record;
  `cm_established` is false if *either* leg is missing, because a price with no factor is the
  overstatement itself.
- **`tests/company/test_phase_nx_ic_flexibility.py` was RED AT HEAD** and is repaired. The v1 pass
  deleted `_CM_DELIVERY_GBP_PER_KW_YR` and left four tests importing it, so the module failed at
  **collection** — taking its other seventeen tests down silently. Two of those dark tests were also
  wrong on their merits: one asserted the `.get(year, TABLE[2025])` fallback *as the contract* after
  it had been deleted as a defect, and `test_dfs_revenue_formula` asserted a £4.50/MWh rate and 20
  events for a winter the DFS record does not establish at all.
- **Poison round before the mutation claims** (`survived` is ambiguous, so reachability first):
  baseline 41 green; no-de-rating **4 killed**; T-3 substitution ignored **3 killed**; missing factor
  → 1.0 **1 killed**; I&C back to rated flex **2 killed**; restored 41 green.
- 2,112 green across `tests/company/market/`, the NX suite, the seam and the regulatory CM suite.
  Epistemic verifier **PASS**.

## What is next

1. **`flexibility_potential.py` and `capacity_market.py` do not de-rate either.** They are not
   overstating today because the domestic leg refuses outright and the obligation leg is a different
   quantity — but `derating_factor` is now callable and they are the two places where a future
   caller re-introduces the rated-capacity error. Worth one pass to check whether either *should* be
   applying a factor.
2. **The register carries awarded volumes and a full CMU/Component list nobody reads.** It would
   settle what a real aggregated DSR CMU looks like — how many components, what size — which is the
   evidence the domestic refusal currently asserts from a threshold alone.
3. **Storage duration factors are in the commons and have no caller.** Whoever builds a battery
   revenue leg should not re-fetch them.
