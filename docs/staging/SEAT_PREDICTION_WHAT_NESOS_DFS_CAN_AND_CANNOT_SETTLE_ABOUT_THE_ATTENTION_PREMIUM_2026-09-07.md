**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — A49, the attention premium against DFS)

# PREDICTION — what NESO's DFS can and cannot settle about the called-day attention premium

**Written 2026-09-07, BEFORE any published DFS figure has been read.** No NESO source has been
fetched. `docs/market_research/` holds no DFS anchor — the only greps that hit are unrelated
substrings in `ESTATE_GAP_ANALYSIS.md`. Filed separately from the result so the result cannot be
read as a prediction made after its own answer.

## The question, and what each side of the ratio counts

`SEAT_RESULT_THE_SKEW_IS_ENTIRELY_IN_THE_TROUGH...` (landed `8f5239deb`) returned **MERELY RARER**
for an extreme-day-only TOU tariff and named one number that could overturn it: a called-day
**attention premium of 2.53×** (2.47× / 2.48× / 2.53× across the three episodes — a property of the
price *shape*, not the level, so it will not move on its own).

Before dividing two numbers, say what each counts. This ratio's two sides are:

- **Denominator — standing-tariff response.** The Arcturus 2.0 slope: how much load a household
  shifts in response to a *persistent, published, unannounced* price differential it lives under
  every day.
- **Numerator — called-day response.** How much load a household shifts on a day it is *told* to,
  with an explicit call, a window, and a payment.

**These are only a "premium" if they are compared at a COMMON price signal.** DFS's signal is
enormous (its guaranteed acceptance price is quoted in £/kWh, not £/MWh — see P1) and a TOU
differential is tens of pence per kWh. A raw ratio of turn-down percentages across those two would
be measuring **signal size**, not attention, and that is this project's named recurring failure.
The honest comparison is of **elasticities** — fractional turn-down per unit of price signal faced —
or an explicit refusal if the published record will not carry one.

## What is already established before the research, and is NOT predicted

From the tree, not from any source:

- `company/market/flexibility_potential.py:30` and `company/market/ic_flexibility_revenue.py:28`
  both carry `_DFS_RATE_GBP_PER_MWH = 4.5`, commented "NESO DFS average 2022-24".
- `flexibility_potential.py`'s own module docstring (line 10) says suppliers "can earn **£3-6/kWh**".
  £3/kWh is £3,000/MWh. **One file disagrees with itself by a factor of about 1,000.** That is read
  off the source, not predicted.
- `_DISPATCH_EVENTS_PER_YR = 20` / `_DFS_EVENTS_PER_YR = 20`, commented "~20 events per winter".
- `docs/design/W1_9_DSR_FLEX_MARKETS_DISCOVER.md` establishes both are company-authored with no
  world behind them, and that `company/interfaces/sim_interface.py` has zero mentions of flex.

## The predictions

| | claim | band |
|---|---|---|
| **P1** | DFS's guaranteed acceptance price is quoted per kWh, so the correct £/MWh figure is ≥ £1,000/MWh — i.e. `4.5` is wrong by roughly three orders of magnitude, and the *direction* of the error is that the code massively **understates** DFS revenue. | ≥ £1,000/MWh; point estimate £3,000/MWh for 2022/23 |
| **P2** | Live (system-need) DFS events per winter are **fewer than 20**; the ~20 figure will turn out to conflate live events with *tests*. | live 2022/23: 5–15. Live+test: 15–30. |
| **P3** | Per-household delivered turn-down per event is small in absolute terms, and a whole winter of DFS earns a domestic household single-digit pounds. | median < 0.5 kWh/event; winter revenue < £10/household |
| **P4** | **The load-bearing one.** Converted to an elasticity at a common signal, called-day response is **not** 2.53× the standing-tariff response — it is *lower*, because DFS's signal is 100–1000× a TOU differential while its turn-down is a few tens of percent. The MERELY RARER verdict therefore stands. | implied premium at common signal < 1.5×; verdict unchanged |
| **P5** | Per-event participation among *registered* households is well under 100%, and decays across a winter. Attention is the binding constraint, not capability. | 30–70% of registered accounts deliver in a given event |
| **P6** | The published record **will** support a sourced event count and rate, but will **not** support a *world-derived* event rate — DFS calls were NESO-discretionary against system margin, and `W1_6_physics_price_signal` is unbuilt (`level_current: 0`). So the honest outcome for W1_9's two constants is *sourced*, not *derived*, and the derivation stays a named gap. | — |

## What would refute each

- P1 fails if NESO's published DFS price really is order £4.5/MWh — then the constant is right and
  the docstring is the defect.
- P2 fails if ≥20 live events ran in a single winter.
- P4 fails if the published per-household turn-down, normalised by signal, exceeds the standing
  response by more than 2.53× — in which case **the extreme-day product's verdict flips** and the
  A49 result must be corrected beside its claim.
- P6 fails if NESO published a deterministic call rule against an observable margin series, in which
  case the event rate *can* be derived and W1_9's constant should become a function, not a number.

## What this pass will NOT do

It will not re-cut the TOU panel. Two instruments have closed on the same answer from opposite
directions and a third cut says nothing new. If DFS refutes P4, the correction is written beside the
A49 result; if it holds P4, the break-even is retired as *settled against the real product* rather
than carried as an open hedge.
