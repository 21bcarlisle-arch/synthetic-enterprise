**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `W1_9_dsr_flex_markets`

# FINDING — £75/kW is a CAPPED T-1 for delivery year 2022/23, and a household cannot hold a CM agreement at all

Settles `SEAT_FINDING_THE_CAPACITY_MARKET_PRICE_HAS_TWO_HOMES_THAT_DISAGREE_BY_4_POINT_7X...`
(`cf61d32a6`). The price now has one home, the domestic leg refuses, and **£930/household/year
comes off the book.** Three of that finding's own claims were wrong and are corrected below beside
the claim, because the corrections are more useful than the settlement.

## What the number actually is

`_CAPACITY_MARKET_GBP_PER_KW_YR = 75.0  # T-4 auction 2023` is the **T-1 clearing price for
delivery year 2022/23**, which **cleared at the auction price cap** on a small volume (~5.8 GW).
It is not a T-4, not 2023, and not a rate anybody earns for "committed flexibility". Two
independent sources agree: Ofgem Annex 9 v1.8's notes column ("T-1 cleared at £75/kW cap but small
volume") and Montel's T-1 auction review (DY 2022/23 → £75.00). The same delivery year's T-4 was
suspended and its replacement T-3 cleared at **£6.44/kW, the lowest price in the record** — so the
two numbers the two homes carried for one delivery year differ by **11.6×, and both are correct**,
because they are two different auctions. Conflating T-4 and T-1 was the whole defect.

**A capped clearing price is a censored observation.** It records where the cap sat, not where
supply and demand crossed. A model reading it as a market price has read a regulatory ceiling as a
market outcome — which is what both homes did.

## CORRECTION 1 — "Nothing in `docs/market_research/` establishes it" was false

It was established, in `docs/market_research/capacity_market_levy_2016_2024.md` — **the very file
`ic_flexibility_revenue.py` cites as its source.** That note carries a T-4 column and a T-1 column;
the sourced table read the first and nobody read the second. The research question the finding
posed as open had been answered in the repo for weeks, one column to the right of the number
already being used. *This is the knowledge-map failure again, and the same shape as the £55/£150
acquisition cost: the answer was here, and nothing told the reader to look.*

## CORRECTION 2 — there were THREE homes, not two, and the third was worse

`company/market/capacity_market.py` held `_CM_CLEARING_PRICE_GBP_PER_KW_PER_YEAR`, **keyed by the
year the AUCTION WAS HELD, under a lookup whose parameter was named `delivery_year`.** A T-4
procures four years ahead, so the two keys are four years apart and nothing said so.
`get_cm_price(2023)` returned **£63.00** — the price the 2023 auction set for delivery year
2026/27 — to a caller asking about delivery year 2023/24, whose T-4 cleared at £15.97. **3.9×,
silently, and the value was not wrong: the KEY was.** Two entries were invented outright:
`2022: 75.00 # Crisis year spike` (the capped T-1 again) and `2021: 0.0 # No T4 cleared in some
years`, which asserted the opposite of what happened — DY 2021/22's T-4 cleared at £8.40/kW. Its
miss default was `50.0`, a price **no GB capacity auction has ever cleared at**.

## CORRECTION 3 — the duplicate gate's blindness is structural, and the finding's proposed fix would not have worked

The finding said `test_no_concept_is_declared_in_more_than_one_module` was blind because
`CAPACITY_MARKET` and `CM_DELIVERY` strip to different concepts, and proposed widening `_concept()`.
**Widening it would not have caught this.** The gate keys on `(concept, repr(value))` pairs, so it
can only see a concept declared twice **with the same value**. Three homes holding *different*
values for one publication is a contradiction rather than a duplication, and **the gate is blind
to the strictly worse case by construction.** No renaming fixes that.

Measured while establishing this: grouping the whole tree by concept alone, **ignoring value**,
finds exactly one further pair — and it is also a disagreement, not a duplication:

| concept | | |
|---|---|---|
| `BASE_CHURN_RATE` | `company/crm/churn_model.py:49` = **0.1** | `saas/clv_sensitivity_model.py:30` = **0.18** |

**Filed, not fixed** — it is a different subject and a 1.8× disagreement in a driver deserves its
own pass rather than a ride on this one. The census is cheap (one pair tree-wide), so the
concept-only strengthening is affordable whenever someone takes that on.

## What DID see it, three weeks ago, and was not acted on

`tests/architecture/test_year_keyed_rate_table_census.py`'s own docstring, since 2026-08-19:

> "…and **three of the Capacity Market auction results — each pair of which is two tables of the
> same law with different numbers**."

and its register entry: *"a third CM table reading one publication, **which is what pinning it once
would collapse**."* The control named the defect, named the count, named the fix, and sat at
`published_unpinned` for three weeks. **A census makes a gap visible and monotone; it does not
close it, and nothing in the architecture was going to.** That is the interconnection review's job
and this is what it looks like when it runs.

The census could not see the *third* home either: it discovers year-keyed **dicts**, and
`_CAPACITY_MARKET_GBP_PER_KW_YR = 75.0` is a **scalar copy of one row of a published series** —
invisible to it, and the one doing the damage at £930/household/year. *Discovery must not be
narrower than the thing it governs; here it was narrower in a dimension nobody had named.*

## The product question: can a domestic household hold a CM agreement? **No.**

The minimum Capacity Market Unit is **1 MW** (reduced from 2 MW). A whole flexible house in this
book is 3.0–15.4 kW, so it takes **80.6 households** at the largest asset combination (EV +
battery, 12.4 kW) — and 334 ASHP-only households — to reach the smallest unit that can prequalify.
A household reaches the CM only inside an aggregator's DSR CMU, and **no publication states what an
aggregator passes through to a member**: those terms are bilateral.

So `_estimate_capacity_revenue` now **refuses**, returning `None` with
`DOMESTIC_PARTICIPATION_REFUSAL` carried to any surface that prints the row. This is the finding's
own option 2, chosen over a derating-and-participation model because two of the three factors that
model needs are unestablished and the third is unpublished.

| EV + battery household, 12.4 kW rated | £/household/year |
|---|---|
| CM leg as it stood (`12.4 × 75.0`) | **£930.00** |
| CM leg at the repo's own sourced 2023 T-4 (15.97) | £198.03 |
| **CM leg now** | **refused — no agreement exists to be paid under** |
| DFS leg (2024/25, established) | £6.22 |
| **Total booked, before → after** | **£936.22 → £6.22** |

## What landed

* `docs/domain_artefact_library/regulatory/capacity_market_auction_results.json` — the commons
  artefact: T-4 and T-1 **held separately** per delivery year 2016–2028, native units (£/kW/yr of
  **de-rated** capacity), honest `null` with a named reason where unestablished.
* `company/market/capacity_market_published_record.py` — the one company-side home. Loads the
  commons, **no fail-open path**, and there is deliberately **no default auction**: asking for "the"
  CM price for a delivery year is refused, because that question had an 11.6× answer in 2022/23.
* The three homes collapse onto it. `capacity_market.py`'s lookup now takes the auction it is
  pricing (`add_obligation` had the `auction_type` in hand and was ignoring it — a T-1 obligation
  priced off the T-4 table at £6.44 against a real £75.00).
* Census: both dict homes leave `published_unpinned` and are held by a no-relapse leg.

## Honest gaps, named rather than filled

1. **No entry is `primary`.** The EMR Delivery Body register returned **HTTP 403** to this pass, so
   every figure is an Ofgem annex's or an analyst's restatement. The artefact says so in
   `primary_not_reached` and a test asserts it keeps saying so.
2. **DY 2023/24's T-1 is CONTESTED** — Ofgem's annex says £60, Montel says £45 and puts £60 at DY
   2021/22. They agree on the flanking years, which is the signature of a one-year slip in one of
   them; *which* is not established, so the value is `null` and both are named. Averaging would
   produce £52.50, a number no publication states.
3. **DY 2025/26's T-4 is CONTESTED** — £30.59 (Montel's stated range maximum) against £35.30 (S&P
   Global). Plausibly the same auction in different price bases; plausibly is not established.
4. **DE-RATING IS UNFETCHED AND THE I&C LEG IS STILL OVERSTATED BY IT.** The CM pays on de-rated
   capacity; `ic_flexibility_revenue` multiplies the clearing price by **rated** flex.
   `derating_factor()` returns `None` for every class rather than a plausible 0.2. **This is the
   same rated-vs-delivered error the DFS pass settled, still live in the I&C leg** — it is the
   largest remaining known overstatement in this subsystem and the obvious next pass.

## Two things found in passing, both pre-existing

* **`tests/company/interfaces/test_flexibility_revenue_seam.py` had two reds at `cf61d32a6`**, from
  the DFS pass immediately upstream: winter 2023/24 is unestablished, so the fixture's post-launch
  year paid £0.00 and the file's own vacuity guard fired correctly — with both fixture years at
  zero, control 2 could no longer see the DFS launch gate. Fixture moved to 2024 (established).
  *A pass landed leaving the seam's own vacuity guard red, and a red vacuity guard is a control
  nobody is reading.*
* **The DFS launch gate is now an EQUIVALENCE, not a missing control.** Established rather than
  assumed: for every winter before `FIRST_WINTER` the record has no row, so the ungated arithmetic
  returns the identical figure. The mutation test that named that defect can no longer fail, and
  now asserts the record's refusal — the property the gate leans on — with a leg that goes red if a
  pre-2022 winter is ever added, which is the signal to restore the mutation form.

## Evidence

Mutation battery on the new record, **baseline green and target-presence proven for each patch**
(a patch that never applied reads as a survivor): refusal→number **killed**; derating→0.2
**killed**; `price()` defaulting instead of raising **killed**; `_load` failing open **killed**.
Suites green: `tests/company/market/` (2071), the seam file, `tests/architecture/`.
