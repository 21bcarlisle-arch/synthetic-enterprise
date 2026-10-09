**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `b8-l3-what-the-run-loop-would-read`

# The run's retention offer reaches the world as a flat 20% cut to one hazard, whatever its size. The world's own response to the same discount runs from +0.018 to +0.042

B8's next level asks for a run-loop retention path to read the learned decision. Before that, I
checked what the run's world does with an offer. **The world answers a retention offer in two
ways, and the two disagree.**

- **B8's instruments** (`simulation/coin_drawn_decision_set`, `tools/decision_probe.py`) ask the
  world at the offered *rate*. The household sees a lower price through the same price response
  that sets every renewal.
- **The run** (`simulation/run_phase2b.py`, `retention_modifier_val`) never passes the discount to
  the world. The company picks 3%, 5% or 8% (`RETENTION_TIERS`), and books that as cost. The world
  is handed `min(0.95, RETENTION_EFFECTIVENESS * framing_multiplier)` with
  `RETENTION_EFFECTIVENESS = 0.20`, which scales the price-position hazard. That constant is
  unsourced (B8's L1 record and `3811342db` both declined it). **The size of the discount never
  reaches the world.** An 8% offer and a 3% offer retain identically. Only their cost differs.

## Measured, at origin `a6304bd87`

Script: `/tmp/retoffer_probe.py`. It uses B8's draw (`draw_households`, 40 per acquisition year,
2016–2024, electricity, lean records). At every renewal it asks `roll_lifecycle_event` for P(stay) at
the world's default three ways: unchanged; with the run's modifier 0.20 (framing multiplier 1); and
at the default × (1 − s) for each tier s. Only one thing varies per ask.

| seed | decisions | mean P(stay) | run's offer, any tier | 3% as a rate | 5% as a rate | 8% as a rate |
|---|---|---|---|---|---|---|
| 101 | 1,217 | 0.595 | **+0.0276** | +0.0184 | +0.0285 | +0.0416 |
| 202 | 1,189 | 0.595 | **+0.0278** | +0.0184 | +0.0286 | +0.0419 |

On average the flat 0.20 happens to land on the **5%** tier. Against the world's own curve it
**over-credits the 3% tier by about 50%** and **under-credits the 8% tier by about a third**. In the
settled run's record (`WORKER_RESULT_THE_COMPANY_CANNOT_LEARN_..._2026-10-07.md` §1), 40 of the 70
offers sit in the 0.30–0.50 belief band, which is the 3% tier. So most of the run's offers are
retaining about 1.5× what the world's own price response gives for that discount.

**What this does not establish.** These are default-tariff renewals at the world's published
default (P(stay) ≈ 0.60). The run's offers are mostly fixed-term renewals at the company's own
price, where the price-position hazard has a different size. So the ratios above are a reading of
the *shape*, not the run's book: size-blind on one side, size-graded on the other. The per-tier
magnitudes on the run's own renewals are not measured here. The framing multiplier (nudge physics
Layer 1) is held at 1.

## Why it matters to B8 now

1. **L3 would wire the learned decision into a world that answers a different question.** B8
   learns the offer's effect at a *rate*. If the run then applies a flat 0.20, then any decision
   graded in the run is graded against a response the learner never saw. So L3 must come after this.
2. **The run credits retention value to the discount the world least supports.** The tiering
   ("risk-proportional rather than flat 5%") cannot show in the run's outcomes. The world
   cannot tell the tiers apart.
3. **It is one rule with two implementations** (the VAT shape). The probe asks at a price. The run
   asks through a constant. A world fix in one is invisible in the other.

## Recommendation (reversible; no number added)

The run should offer the discount to the world **as the discounted rate on the same roll**.
`simulation/save_on_loss_notice.py` already re-asks the same household on the same roll at one other
price through the kept `_roll_kwargs`, so that route exists. Then `RETENTION_EFFECTIVENESS` retires.
The framing multiplier needs a home. The narrowest is a scale on the rate's price response,
because Layer 1 is loss-aversion to a price framing. Whether it belongs there at all is a design
question for whoever builds it.

This changes the canonical run, so it changes the world digest. Budget the value-arms re-take
(roughly 25 controls) in the same piece of work. Pre-register before running: **prediction, written
now:** the run's retained-by-offer count falls, because the commonest tier is 3% and the rate
response at 3% is about two-thirds of the flat 0.20. The company's booked retention cost does not
change, because it never depended on the world.

Until that lands, B8 L3 is better left unbuilt than built on this.
