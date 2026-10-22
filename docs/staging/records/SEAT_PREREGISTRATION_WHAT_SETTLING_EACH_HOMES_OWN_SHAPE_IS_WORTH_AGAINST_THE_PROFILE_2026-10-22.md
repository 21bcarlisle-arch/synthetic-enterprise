**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `measure-what-settling-each-homes-own-shape-is-worth-against-the-profile` (Lane 0 delivery)
**Knowledge:** imbalance-cashout-settlement

# Pre-registration: what settling each home's own shape is worth against the profile

*Delivery seat, 22 Oct 2026. Written and committed BEFORE the probe was run. The finding it answers:
`SEAT_FINDING_THE_RUN_SETTLES_EACH_HOMES_OWN_HALF_HOURS_WHERE_THE_PERIOD_SETTLED_A_PROFILE_2026-10-22.md`.*

## What is being measured, said before it is differenced

For one electricity home over one book-year (the calendar year, clipped to its supply from
acquisition), the **timing difference** is

    Δ = Σ_hh q_own(h) · SSP(h)  −  Σ_hh q_prof(h) · SSP(h)

- `q_own` is the half-hourly volume the run settles for the home. The probe builds it with the same
  shape builder the run uses: `fabric_shape_fn` plus battery dispatch for a fabric premise, and
  `_weather_adjusted_shape_fn` over the PC1/PC3 base for a legacy one.
- `q_prof` is what a 2016–2025 NHH supplier was charged for: the home's OWN annual volume for that
  book-year multiplied by the published Profile Class base shape, normalised over the same days.
  This is **EAC × profile coefficient, with the annual volume trued up**, which is what
  reconciliation did. It corrected volume and never shape.
- `SSP` is the run's own price record, `systemSellPrice` by (date, period). It is the price the run
  charges unhedged volume at.

Positive Δ means the home's own shape costs MORE than the profile would have. That is the run
charging the company for timing that the period never charged a supplier for. Negative Δ means the
run hands the company timing value the period could not bank. Only negative Δ favours the thesis.

**Δ is the GROSS exposure.** `settle_hedged_period` prices `hedge_fraction × q` at the term's flat
forward and only `(1 − hf) × q` at SSP. So what the run actually books per term is roughly
`(1 − hf) · Δ`, and |Δ| is an upper bound on it. Network and levy costs are flat per MWh, so timing
does not move them.

### Stand-ins, stated as such

1. **Group correction** is not modelled. GC scales every NHH half hour in a GSP group by one
   factor, so a supplier with a small share bears roughly its profiled share of the residual. That
   is close to neutral to first order for one home, and it is NOT neutral for a whole book whose
   shapes differ from the group's. That second-order term is out of scope.
2. **The profile is the 1997 PC1 GAD base table**: five seasons × three day types, from
   `sim/profile_class_1.py`. Elexon's live coefficients also regress on daily temperature and
   sunset time. The stand-in therefore shifts less volume into cold days than the real profile
   did, which overstates Δ for electrically heated homes. That is a GAP, and its size is not known.
3. **PC2 (Economy 7) is not in the tree.** `SHAPE_LOADERS` carries PC1 and PC3 only, and every
   domestic home in the book is PC1. An E7 or storage-heated home would really have been settled
   on PC2, which puts ~40% of volume overnight. Measured against PC1, its Δ will read as cheaper
   than the period was, which flatters the thesis. A home like this is reported but cannot be
   graded.

## Scope

- One seed: the book that `simulation.run_phase2b`'s module state draws at HEAD (569 electricity
  accounts: 567 PC1 resi, 2 PC3 SME, 3 HH-metered).
- Each account's own supply span within 2016-01-01 to `REPORT_END`, by calendar book-year.
- Split by provider: `fabric` and `legacy`. HH-metered (`metered`) accounts are excluded because
  elective HH settlement was real for them. Fabric is further split by heating commodity
  (electric vs gas).
- Not modelled: ToU demand shifting (`make_shifted_shape_fn`), mover carry-over terms, and the
  deemed and flex paths. Each one only moves the shape further from the profile.

## Predictions, before the number

- **P1 — legacy is small.** The legacy shape IS the profile, plus overlays: HDD heating uplift,
  overnight EV, solar, battery. Mean |Δ| per legacy home-year < **£5**, and |Δ| / own SSP cost
  < **2%**. Sign: slightly negative, because overnight EV and battery are cheap and solar offsets
  the shoulder.
- **P2 — electrically heated fabric homes are positive, not negative.** Annual true-up keeps the
  volume and leaves the profile's seasonal split alone. A heated home's own winter share is well
  above PC1's, and winter SSP (above all 2021–22) is high. So the own shape costs MORE: mean Δ
  **+3% to +10%** of own SSP cost, **+£20 to +£150** per home-year. **If this holds, the finding's
  stated direction (favours the thesis) is wrong for the biggest group.**
- **P3 — gas-heated fabric homes are small and of uncertain sign.** |Δ| < 3% of own SSP cost, mean
  |Δ| < £15 per home-year.
- **P4 — book-year.** The book total is positive (the run over-charges timing compared with the
  period), driven by P2, and |book Δ| is **0.5% to 5%** of the book's own SSP cost.

**Material** means: |book Δ| ≥ 1% of the book's own SSP cost, or any provider group's mean
|Δ| ≥ £10 per home-year. Material triggers the finding's done-means step 2 (settle a
non-HH home on its profiled volume). Not material closes the finding with the measured bound.

**Refutation.** P2 is refuted if the electrically heated fabric mean Δ is ≤ 0. In that case the
finding's direction holds, and the per-customer value test has to subtract it. P1 is refuted if
legacy mean |Δ| ≥ £5.
