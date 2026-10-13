**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** hedging-forward-market -- no new number; both prices are the run's own

# The hedge's booking price moves only the desk's own book; settled margin is identical to the penny

**Item:** `the-hedge-books-at-the-markets-quote-lands-from-the-shared-index`. **Premise re-measured:
spent.** The change itself was already on origin at 61c122683 (08:56 today), landed without a control.
What this turn added: the control (776dfcd2e) and the before/after below.

## The control

`tests/simulation/test_the_hedge_volume_reads_only_what_the_company_holds.py::test_every_hedge_the_run_books_is_struck_at_the_markets_forward_quote`.
Mutation `forward_price_gbp_per_mwh=company_fwd` at the booking call: 1 failed. Origin: 9 passed.

## Prediction, filed before either arm ran (13:04 UTC)

From the call-site read: `run_hedged_term` has always priced the hedged share at `forward_price`, so
settled margin, treasury and the hedge-effectiveness entries never read the forward book. The collateral
book is built after the loop and takes `final_treasury` as an input.
P1 net, gross, treasury and hedge effectiveness IDENTICAL. P2 trading-book hedge P&L and bid-ask DIFFER
(sign not predicted). P3 margin-call/credit exposure DIFFER. So the item's WHY ("flatters every margin
downstream, including the cost floor") was predicted FALSE for settled margin.

## Measured

Both arms used one frozen origin worktree (d1e37f45c) and the default book seed, 20260724, **not 42**.
For an equivalence the seed is immaterial. The window was 2016-01..2018-12, which is enough to refute
P1, and it is NOT the crisis years. BEFORE wrapped the desk so that each booking took the `company_fwd`
that `decide_term_hedge` had been handed for that customer and term: 2,156 of 2,156 bookings were
swapped, 0 missing.

| Figure | Before (company's forward) | After (market quote) |
|---|---|---|
| total_net / final_treasury | £92,893.62 / £342,893.62 | **identical** |
| total_gross, capital, bad debt | £317,066.58, £3,060.29, £10,372.02 | **identical** |
| hedge effectiveness (3,149 terms: actual / naked net) | £92,893.62 / £291,769.32 | **identical** |
| every settlement record except `hedge_pnl_gbp` (sha256) | 221c5e1a30a31b3d | **221c5e1a30a31b3d** |
| trading book hedge P&L | **+£6,137.54** | **−£646.39** |
| trading book bid-ask cost | £1,844.05 | £1,712.95 |
| wholesale credit net exposure | £35,340.94 | £50,204.75 |
| gross marked exposure (margin-call book) | £66,274.71 | £90,205.84 |

All four predictions hold. The identical record digest is also the determinism control: two
nondeterministic runs could not agree on every other field. The planned repeat of the after-arm was
dropped as redundant.

## Reading

The defect the change fixed was not a flattered margin. It was a **trading book that disagreed with
the settlement it decomposes**. The desk reported +£6.1k of hedge P&L over three years that the
settlement never contained (it is −£0.6k at the price actually paid). It also understated
counterparty credit exposure by about 30% (£35k against £50k). Writer 1's cost floor (03a0b66da)
reads settled margin, so it was never flattered by this.

Open: the 2021–2022 window, where the company's forward and the market diverge most, is unmeasured
here. P1 holds by construction there too, but the size of the old book's error in those years is not
established.
