> **PARKED — in_progress (2026-07-22, autonomous worker).** DISCOVER→FRAME done →
> `docs/design/WHOLESALE_VALUE_CHAIN_FRAME.md` (shaped-cost benchmark, unified product ladder, cover fan
> + value-add ledger, tariffs-from-stack; reconciled with THE_VALUE_CYCLE_FRAMING / W1_6 / EPOCH2_BC —
> extend/unify, don't fork; folds the companion `ADVISOR_DISCOVERY_WHOLESALE_ANCHORS` sourced anchors per
> R9; candidate atoms WVC_1–WVC_5; R10/R15-failable invariants WVC-1/2/3).
> **OPEN SUB-ITEM (the only genuinely-open, contract-touching decision):** `WVC_5_tariff_from_stack` —
> whether the constructed shaped cost stack *replaces* or *sits behind* the published Ofgem cap (FRAME
> §8.1), plus confirmation no billed-history mutation path exists. **Unblocks when:** the director's 2h
> veto window on the FRAME lapses without objection → BUILD proceeds `WVC_1→WVC_5` on standing authority
> (WVC_5 last, behind the bill-immutability guard); `WVC_1`–`WVC_4` are extensions of existing trading
> organs and need no further gate once framed. A board blind-spec of a competent GB trading function is
> incoming — reconcile it with the FRAME + primary-source DISCOVER at BUILD (disagreements are findings).

# DIRECTOR STEER — The wholesale value chain: products, shaped cost, and where trading value is created (2026-07-22)

**Type:** [STEER] — a material Epoch-2 correction from the director's 20 years in this industry. DISCOVER→FRAME first; mechanism yours; the *construct* below is the wall.

## Fresh-session anchor

The mission is carbon abatement via personalisation (£/tCO₂e), Epoch 2 is the commercial brain. The weather→spot cascade is settled and the spot record is real (168k Elexon half-hours). This steer addresses what sits ABOVE spot.

## The director's verdict (verbatim, and he is right)

*"We still have really simplistic wholesale products. Really just a day or spot, with a largely static view of contango vs backwardation… The data needs to drive the actions we know are done to create value. I'm not convinced what we have does that."*

Evidence from our own surfaces: the company forward is a **120-day trailing mean + risk premium** (world.json wall crossing); no product ladder exists; no shaped annual cost; no cover ledger; no fixed/variable book split; tariffs are not derived from a visible cost stack.

## The construct that must become the spine

**1. The annualised shaped energy cost is the benchmark.** For a residential book: take the annual demand shape (seasonal × within-day, from the premise demand machinery), price that shape against the wholesale curve, and get the annual energy cost per customer / per MWh shaped. This is the standard supplier view (it is also how the price-cap wholesale allowance is constructed — a public anchor). **Everything the trading function buys must roughly add up to this number.**

**2. A real product ladder, with real term-structure dynamics.** Seasonal baseload (Winter-N/Summer-N), quarters, months, day-ahead — distinct products with evolving prices, contango/backwardation that *moves* (season, storage, crisis), anchored to the real record and to public curve evidence where obtainable. The current static spot-derived forward is explicitly insufficient.

**3. The value-creation loop, as activities:** demand forecasting for the book's shape → a hedge program buying products against forecast → **cover % by product and horizon over time** (the fan) → residual + forecast error settling at the single imbalance price → **achieved cost vs the shaped benchmark = the trading value-add ledger.** Weather drives demand; balancing closes out. These are the actions that create or destroy supplier value; the sim must make them real and scoreable.

**4. Tariffs derive from the stack.** Fixed tariffs lock the shaped forward cost at acquisition (plus network/policy/operating/margin); variable reprices cap-methodology-like. The retail prices we expect must be *driven by* this data, not asserted beside it.

**5. The epistemic wall holds throughout:** SIM owns true curves and outturn; the company forecasts, trades, and is scored on belief-vs-truth — its naive 120-day estimator becomes its *starting* belief that trading experience must improve.

## Sequence (propose, then build)

DISCOVER: real GB product/curve anchors (cap wholesale-allowance methodology, published curve indices, DA history), and what "annual shape" the book implies from existing premise machinery. FRAME: the product ladder + benchmark + ledgers design, reconciled with THE_VALUE_CYCLE_FRAMING and the W1_6 engine (extend, don't fork). BUILD on your standing authority once framed; **the desk-pack surfaces (curve evolution, cover fan, fixed/variable split, peak/base, value-add ledger) are outputs of this organ, not cosmetics** — they are what the director will judge believability on (his axes).

**Risk & proportionality:** touches pricing/hedging organs and eventually tariffs — the commercial spine. Extend the existing engine and ledgers; no silent change to billed history; propose the FRAME before build. Tag: **contract-touching — propose-then-proceed, 2h veto per standing model.**

— Advisor, carrying the director's correction, 2026-07-22.
