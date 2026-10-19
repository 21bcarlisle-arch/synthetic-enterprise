**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `how-many-synthetic-households` -- the fuel claims on the fuel-split page are about who is in the world, and this asks which routes into the world they are checked on

# The fuel claims are measured on the founders only, and the campaign route may win every gas home dual

*Delivery seat, 2026-10-19, direction item `one-low-carbon-table-from-a-fetched-source`, second
part: "tools/world_claims.py measures the founder book only. Extend drawn_book to the trickle and
campaign routes, or say in the code why not."*

## Pre-registration (written before the measurement)

`tools/world_claims.drawn_book` pools `_drawn_founder_pairs` over 8 seeds. The trickle
(`_drawn_trickle`, through `_trickle_records`) and the campaign (`_campaign` winners, through
`_won_customer_dicts`) are the other two ways a home enters the book.

Predictions, per route, against the five fuel claims and the DD claim on the two pages:

1. **Campaign: `dual_share_of_gas_homes` = 1.000, a GAP against [0.81, 0.96].** `_gas_leg_for`
   attaches a gas leg to every won home whose premise has gas, with no draw. So a campaign gas home
   is always dual, and `gas_only_share_of_homes` = 0.
2. **Campaign: `gas_home_share` holds** (the premise is drawn from the same stock).
3. **Trickle: every claim holds**, or is UNCHECKABLE for want of homes. The trickle draws its fuel
   arrangement through the same `iter_acquisition_events` coin as the founders since 17 Oct.
4. I cannot say in advance whether the campaign's `dual_share_of_homes` holds. It equals
   `gas_home_share` if every gas home is dual, so it holds if that share is within [0.70, 0.85].

## Result

Measured 2026-10-19 with `tools.world_claims.drawn_book(route=...)` over the 8 seeds:

| route | accounts | homes | dual of homes | dual of gas homes | gas homes | gas-only of homes | DD |
|---|---|---|---|---|---|---|---|
| founders | 3,056 | 1,732 | 76.4% | 90.0% | 84.9% | 3.9% | 72.1% |
| trickle | 54 | 31 | 74.2% | 88.5% | 83.9% | 3.2% | 74.1% |
| campaign | 3,180 | 1,750 | 81.7% | **100.0% GAP** | 81.7% | 0.0% | 71.2% |

Each prediction, graded:
1. **Confirmed.** The campaign's `dual_share_of_gas_homes` is 100.0%, a GAP against [81%, 96%],
   and its gas-only share is 0.
2. **Confirmed, narrowly.** The campaign's `gas_home_share` is 81.7% against a floor of 81.5%. The
   campaign wins slightly fewer gas homes than the stock holds. I cannot yet say whether that is
   selection (who switches) or noise.
3. **Confirmed**, on 31 homes only: about 2 arrivals a seed. A trickle verdict is a coarse check.
4. The campaign's `dual_share_of_homes` holds at 81.7%, equal to its gas-home share, as it must be
   when every gas home is dual.

## What this means

The campaign route wins no split homes. Published practice (§5a of the fuel-split page) puts the
share of gas homes taking both fuels from one supplier at 0.83 for the market stock and 0.94 for
challengers built by switching. It is never 1.0. So the campaign's book has no gas-only accounts and
no electricity-only accounts on a gas home. The director's 26 Aug ruling ("real suppliers win both
together far more often than not") says *more often than not*, not *always*. `_gas_leg_for` built
it as always.

## Disposition

- **In code:** `tools/world_claims.py` now measures all three routes. The campaign gap is named in
  `KNOWN_ROUTE_GAPS`, which may only shrink, and `tests/tools/test_world_claims.py` reds on a new
  gap or a fixed one still listed (mutation-proven: emptying the register reds the campaign case).
- **Not built here:** the world change. That is the campaign drawing a won gas home's fuel
  arrangement through the founders' P(dual | gas) coin rather than attaching the gas leg always. It
  moves the published book and the value arms, so it is handed on as its own item. It is a fidelity
  change and does not touch a ruling's intent.
