**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `measure-what-settling-each-homes-own-shape-is-worth-against-the-profile` (Lane 0 delivery)
**Knowledge:** imbalance-cashout-settlement

# Settling each home's own shape against the profile: near zero for the book, tens of pounds a year for an electrically heated home

*Delivery seat, 22 Oct 2026. This is the measurement pre-registered in
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_SETTLING_EACH_HOMES_OWN_SHAPE_IS_WORTH_AGAINST_THE_PROFILE_2026-10-22.md`
(landed 19d3c5e50). It answers the finding
`SEAT_FINDING_THE_RUN_SETTLES_EACH_HOMES_OWN_HALF_HOURS_WHERE_THE_PERIOD_SETTLED_A_PROFILE_2026-10-22.md`.*

**Order of events, stated because it matters.** The pre-registration was written first. Its first
landing attempt was refused at the staging-rooms gate (wrong room). The full-book probe started
while the second attempt was still in the gate, and a 12-home smoke test had been read before
either landing. That smoke test held no electrically heated fabric home and no PC1 legacy home, so
P1 and P2 had not been seen when the text was fixed. The PC2 arm below was predicted in writing
before it ran, but that prediction was not committed first.

## Answer

Δ is defined in the pre-registration: the cost at SSP of the home's own settled half hours, minus
the cost of its own annual volume spread over the published profile. One seed, the HEAD book (572
non-HH electricity accounts, 4,950 home-years, 2016 to 7 Jun 2025). Δ is GROSS: the run books
roughly `(1 − hedge_fraction)` of it.

| Group | Homes | Own SSP cost | Δ | Δ % | Full-year Δ mean / median | mean \|Δ\| |
|---|---:|---:|---:|---:|---:|---:|
| legacy PC1 (domestic) | 274 | £584,105 | +£2,092 | +0.36% | +£0.9 / −£0.0 | £2.2 |
| fabric, gas-heated | 243 | £449,957 | −£3,453 | −0.77% | −£1.5 / −£1.1 | £4.0 |
| fabric, no heating fuel recorded | 22 | £41,355 | −£298 | −0.72% | −£1.4 / −£0.9 | £4.2 |
| fabric, electrically heated, vs PC1 | 29 | £172,299 | −£9,292 | −5.39% | −£44.2 / −£13.8 | £71.7 |
| … of which night-heavy (≥38% of volume 00:00–07:00), vs PC1 | 19 | £122,341 | −£12,357 | −10.1% | −£91.4 / −£50.5 | £91.4 |
| … of which night-heavy, **vs PC2** | 19 | | −£2,343 | −1.9% | −£16.9 / +£1.1 | £35.7 |
| … of which day-heated (<30% overnight), vs PC1 | 9 | £49,553 | +£3,051 | +6.2% | +£37.3 / +£9.8 | £37.8 |
| … (one home, PROS-2024-0359, sits between 30% and 38% and has no full year) | 1 | | | | | |
| legacy PC3 (2 SME + 2 successors) | 4 | £61,036 | +£3,935 | +6.45% | +£100.1 / +£71.1 | £100.1 |
| **Book, every home on PC1/PC3** | 572 | £1,308,751 | −£7,017 | −0.54% | −£1.5 / −£0.0 | £7.3 |
| **Book, night-heavy homes on PC2** | 572 | £1,308,751 | **+£2,997** | **+0.23%** | | |
| **Domestic only, night-heavy on PC2** | 568 | £1,247,715 | **−£938** | **−0.08%** | | |

PC1's own overnight share is 15.2%. The night-heavy electrically heated homes put 38–85% of their
volume between 00:00 and 07:00. That is a storage-heater or Economy 7 shape. In the period such a
home was registered on Profile Class 2, not PC1, and was settled on PC2's night-loaded
coefficients. PC2 comes from the same UKERC archive as the tree's PC1
(`.../data/version_0/data/ProfileClass2.csv`, the 1997 GAD table, same layout). It was fetched
for this measurement only and has not been added to `sim/data/`.

**What it means.**

1. **For the book, the effect is not material, and its sign is not the one the finding
   predicted.** With the night-heavy homes on their right profile class, the whole-book timing
   difference is +0.23% of SSP cost. That is the run charging the company slightly more than the
   period would have, mostly through the four PC3 SME accounts. Across domestic homes only it is
   −0.08%. The finding's claim that this "leans in the thesis's favour" is not supported at book
   level.
2. **For a single electrically heated home, it is material in both directions.** Measured against
   the right profile, a night-heavy home's Δ has a mean |Δ| of £36 per year, and a day-heated home
   is +£37 per year on average, up to +£146. The SME accounts sit at about +£100 per year. A
   per-customer value test that keys on individual electrically heated homes can therefore draw
   ±£35–150 a year from timing that the period did not settle. Gas-heated and legacy domestic homes
   (517 of 572) sit within ±£4.
3. **Against PC1, the night-heavy homes would have read −£91 per year.** That is the largest
   effect in the table, and it is entirely a wrong-profile artefact. It is also a live defect, not
   only a measurement trap: **the run registers every domestic home as PC1, storage-heated ones
   included** (`profile_class` is 1 on all 567 resi accounts). On the legacy path that would settle
   a storage-heated home on a daytime shape. On the fabric path it does not matter today, because
   the fabric path settles the home's own trace.

## Grading against the pre-registration

- **P1, legacy small: HOLDS.** Mean |Δ| £2.2 < £5, and +0.36% < 2%. Its predicted sign was
  slightly negative, and it is slightly positive. Not graded on sign.
- **P2, electrically heated fabric positive at +3% to +10%: REFUTED as stated** (−5.39% vs PC1).
  The refutation is the PC2 stand-in gap the pre-registration named (stand-in 3). The day-heated
  homes P2's mechanism describes come out +6.1% and +£37 per year, which is inside the predicted
  band. The night-heavy homes it did not separate dominate the group. I lumped two populations
  under one label, and the cause split followed from the definition only after the fact.
- **P3, gas-heated small: HOLDS.** −0.77%, mean |Δ| £4.0.
- **P4, book positive at 0.5% to 5%: REFUTED** on the PC1-only reading (−0.54%). Even with the
  right profile it is +0.23%, which is positive but under the band's floor.
- **PC2 arm, night-heavy within ±5% and |Δ| < £40: HOLDS** (−1.9%, £35.7).
- **Materiality (pre-registered: book ≥ 1%, OR any group's mean |Δ| ≥ £10): MATERIAL**, on the
  per-group leg only. The book is under 1% either way. The groups over £10 are the electrically
  heated homes (both kinds) and the PC3 SMEs.

## Decision

The pre-registered rule makes this material, so done-means step 2 is triggered: a home without an
elective HH registration settles on its profiled volume. **Not built in this turn. It is K8 work
(knowledge page first), and it reaches the settlement path of every run.** Two pieces have to come
first, and the continuation carries them:

- a world-side Profile Class 2 table in `sim/data/` with its provenance note, beside PC1's;
- a registration rule that puts a storage or E7-shaped home on PC2.

Until then, the per-customer value test should treat electrically heated homes and SME accounts
as carrying a timing term of ±£35–150 per year that the period did not settle. It should also
read any value it attributes to them net of that term. For the 517 gas-heated and legacy
domestic homes, the term is under £4 a year and can be ignored.

## Stand-ins this does NOT remove (from the pre-registration)

- No group correction. No temperature regression in the profile: the 1997 GAD table has five
  seasons and three day types only. Both are GAPs of unknown size.
- One seed. Each home's span runs from acquisition to `REPORT_END`, ignoring departures. That
  moves the book total and leaves the per-home-year figures alone.
- ToU shifting, mover terms, deemed and flex paths not modelled.

## How it was measured

`python3 -m tools.profile_settlement_timing_probe --pc2-csv <ProfileClass2.csv> --json out.json`
reproduces every row above at 02659d155 in about 12 minutes. The PC2 file is UKERC's, from the
same archive as the tree's PC1, and it is not in the tree. The tool wires `run_phase2b.main`'s own
shape builders the way `main` does: `fabric_providers_for_book` over the per-cell weather store,
`fabric_shape_fn` with the battery dispatch, and `_weather_adjusted_shape_fn` with
`_base_profile_eac`. It prices both shapes at `get_cached_prices` SSP. For each home and calendar
book-year, `q_prof = own annual kWh × profile(h) / Σ profile` over the same priced periods.
Overnight share is taken over each home's whole span. A first pass computed it on 2019 alone and
put one more home (PROS-2024-0359, 28.5%) in the day-heated group. The controls are in
`tests/tools/test_profile_settlement_timing_probe.py`. Three mutations were tried (dropping the
true-up, flipping the sign, pricing unpriced periods at zero) and each one turns a control red.
