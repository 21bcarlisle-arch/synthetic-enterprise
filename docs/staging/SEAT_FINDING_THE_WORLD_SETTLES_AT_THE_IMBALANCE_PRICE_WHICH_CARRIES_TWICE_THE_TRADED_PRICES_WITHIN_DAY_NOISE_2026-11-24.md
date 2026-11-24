**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_6_physics_price_signal`

# The world settles at the imbalance price, and it carries twice the traded price's within-day noise

Found by the delivery seat, 24 Nov 2026, grading the world's power record against the electricity
page (`docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md`). Numbers:
`docs/staging/records/SEAT_RESULT_GRADING_THE_WORLDS_POWER_RECORD_AGAINST_THE_ELECTRICITY_PAGE_BY_REGIME_2026-11-24.md`.

**What.** The world's power record is Elexon's System Sell Price, the imbalance cash-out price, and the
forward-year chain is calibrated to it. Against Elexon's traded short-term price (MID), by regime:

- the monthly level agrees: MAE £2.03, £4.57 and £1.76, with bias under £1.20;
- the within-day SD is 2.12, 1.95 and 1.83 times the traded price's;
- negative half-hours run about 2× the traded price's in most years (1,073 against 495 in 2024);
- half-hours above £500: 62 against 14 before the crisis.

**Why it matters.** A supplier hedges forward and buys day-ahead. It pays the imbalance price only on
its imbalance. Anything the world values on within-day SHAPE is valued on a price no supplier's energy
cost carries, and the gap is large. That includes a ToU spread, a load shift, flex and the cost of a
peaky household. The monthly level is not affected.

**Why LATENT, not BLOCKING.** The level-driven figures (bills, the cap and hedged cost) are within £2 a
month outside the crisis. Some shape work already reads MID (`tools/tou_price_shape_episode.py`).
This becomes BLOCKING the day a published value of shifting or flexing is read off SSP's within-day
shape.

**What would answer it.** Not to be decided here. Either settle the supplier's non-imbalance volume at a
traded price (MID, or a day-ahead series if one is licensed) and only its imbalance at SSP, which is
what a real supplier faces. Or keep SSP and publish the shape overstatement beside every shape-valued
figure. Either way this is a baseline fidelity change, decided blind to company results. It belongs
with the chain rebuild, item 4 of the BLOCKING steer finding, because the chain is fit to SSP too.

**Done means** that the price the world uses for a supplier's hedged and day-ahead volume has a
within-day SD within ±20% of the traded price's in every regime, graded by the probe in the result
record, or that every shape-valued published figure carries the measured overstatement.
