# How a supplier shapes an estimate for an unread month — method and the published monthly shape

**Knowledge:** metering-and-reads

*Discovery pass, 2026-10-06. How a GB supplier turns an annual estimate (EAC/AQ) into an amount
for one unread month, and the published monthly shape each fuel uses. Builds on
`what_a_supplier_holds_to_size_a_direct_debit.md` (annual-figure precedence, TDCV) and
`how_far_a_settled_eac_sits_from_next_years_use.md` (how far that annual figure drifts). This page
is the within-year shape; those two are the annual level and its error.*

---

## 1. Electricity NHH: EAC from a meter advance, by profile class

An EAC/AA converts a meter advance into an annual figure by dividing by the **sum of the Profile
Class 1 (domestic unrestricted) coefficients over the read period**, then re-weights it across the
year by the same coefficients — the Elexon/BSC method (BSCP504, "EAC/AA calculation"). *(Corrected
2026-10-29: BSCP504 v53.0 §4.9 has now been read; it holds the process rules, and the formula is in
BSC Annex S-2 §4.3.7, quoted in §8 below.)* The mechanism is also stated by DESNZ:

> "The AA is an estimate of annualised consumption based on consumption recorded between two meter
> readings at least 6 months apart … an EAC is used where two such meter readings are not available
> … using historical information and the profile information relating to the meter."
> — DESNZ, *Subnational methodology and guidance booklet* (2026), §3.1.3

**Exact Elexon PC1 monthly/HH coefficients were not obtainable here.** Elexon's site search and
document portal returned no usable public numeric table within this session's reach; the live
figures sit in Elexon's BMRS/SVAA systems. **Named gap**, not a number guessed to fill it.

## 2. Best published GB domestic electricity monthly shape (not PC1-exact)

**DESNZ Energy Trends Table 5.5**, "Domestic sales" column — actual metered GB domestic
electricity sold monthly. Computed from the published spreadsheet (retrieved 2026-10-06,
`gov.uk/government/statistics/electricity-section-5-energy-trends`), 3-year average 2023–2025:

| month | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| share | 10.81% | 8.87% | 9.12% | 8.14% | 7.25% | 6.73% | 6.78% | 6.96% | 7.30% | 8.18% | 9.65% | 10.22% |

**Confidence: H for the figures** (primary spreadsheet, three independent years, sums to 100%) —
**M as a PC1 proxy**. It blends Profile Class 1 and Class 2 (Economy 7) households and is actual
2023–2025 weather, not a seasonal-normal construction. PC1-only would likely peak sharper in
winter and sit flatter in summer than this blend, because PC2 households shift load to off-peak
hours rather than concentrating it seasonally the same way — expectation only, not a sourced
number.

## 3. Gas NDM: AQ, EUC, ALP/DAF, "seasonal normal" — confirmed by Xoserve directly

> "Annual Quantity (AQ) — An estimate of the amount of gas (in kWh) that a supply meter point will
> use in the coming year **under 'seasonal normal' weather conditions**."
> — Xoserve, *An Introduction to Demand Estimation and DESC* (updated Oct 2023)

> "Non-daily metered sites (Classes 3 and 4): AQ is based on the consumption between two meter
> readings [9–36 months apart]. **The calculation is adjusted for the impact of the actual weather
> experienced in that period.** It's then converted to a 12-month estimate."
> — Xoserve, *Annual Quantity (AQ)* help page, retrieved 2026-10-06

So the AQ is weather-corrected **at calculation time** (actual weather in the read window stripped
out) and then expressed on a **seasonal-normal basis** going forward — not re-based to the actual
weather of the billing year until the next AQ recalculation.

The monthly shape spreading that AQ across a year is the **Annual Load Profile (ALP)**, governed by
DESC and keyed to **End User Category (EUC)**: domestic NDM sites sit in the 0–293 MWh/yr band,
which splits by domestic/non-domestic and prepayment/non-prepayment (EUC01B = domestic
non-prepayment). The **Daily Adjustment Factor (DAF)** reacts to actual day-to-day weather for
system balancing/allocation, not for re-stating a bill estimate. Source: Xoserve *Demand
Estimation* help page and the DESC introduction slides (both retrieved 2026-10-06).

**The exact EUC01B ALP table was not obtainable here.** Xoserve states the "Derived Factors (EUCs,
ALPs, DAFs and PLFs) for the current gas year" live in **"the UK Link secure area," UNC-party
access only** — a structural gap stated by the source itself, not a search failure.

## 4. Best published GB domestic gas monthly shape (not EUC01B-exact)

**DESNZ Energy Trends Table 4.2**, "Domestic" demand column — published monthly only from **2023
onward** (earlier years marked `[x]`, not available at this granularity). Computed from the
spreadsheet (retrieved 2026-10-06, `gov.uk/government/statistics/gas-section-4-energy-trends`),
3-year average, the only three complete years available:

| month | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| share | 17.05% | 13.42% | 12.30% | 7.87% | 4.10% | 2.61% | 2.33% | 2.29% | 3.43% | 7.13% | 12.24% | 15.22% |

**Confidence: H for the figures** (primary source, direct computation, three years) — **M as an
EUC01B proxy**. DESNZ's "Domestic" sector is broader than one EUC band (not filtered to
non-prepayment; DESNZ's sectoral split need not match Xoserve's EUC boundaries exactly), and —
unlike the ALP — this is **actual realised weather for 2023–2025**, not seasonal-normal. A true
seasonal-normal ALP would be smoother year-on-year than this average already shows (e.g. January
2025 ran markedly colder than January 2023–2024, visible in the per-year shares behind this table).

## 5. Do bill estimates use these industry profiles, and against what weather basis

**Established:**
- Gas AQ is explicitly built and expressed **on a seasonal-normal weather basis** (§3) — not actual
  weather for the billing year in progress.
- The registry annual figure (EAC electricity, AQ gas) ranks second, behind the supplier's own
  metered history, under SLC 27.15 — per `what_a_supplier_holds_to_size_a_direct_debit.md` §2,
  reused here, unchanged.
- Ofgem's TDCV is the explicit published fallback "in the absence of individual consumers' data"
  (Ofgem, 2023 TDCV decision §1.1, already cited in the companion document) — an annual figure, no
  published monthly breakdown found in either pass.

**Not established, named as a gap rather than assumed:**
- No supplier or Ofgem statement was retrieved confirming whether an individual domestic bill
  *estimate* is weather-corrected at issue, or is a flat annual-figure/12 split. Supplier sites
  (Centrica/British Gas and others) were not reachable through this session's JS-free fetch
  tooling; no quote is repeated here without being re-verified.
- Whether a supplier's billing engine re-derives a monthly split from the ALP/PC1 shape, or simply
  divides EAC/AQ by 12 (the director's practitioner statement already on record for the DD path),
  is **not established for the bill path** — only for direct-debit sizing.

## 6. What a supplier can and cannot know

**Can know:** the registry EAC/AQ and its vintage; its own prior meter-read history for the
account; the published *industry-average* monthly shape for the meter class (PC1/PC2 electricity,
EUC gas); the Ofgem TDCV fallback; whether the AQ in force was struck on a seasonal-normal or
actual-weather basis (§3).

**Cannot know, from the published record:** the household's own weather response, as distinct from
the EUC-average DAF; the exact Elexon PC1 or Xoserve EUC01B ALP tables (gated to settlement-system
participants); and, per §5, whether a given supplier's bill-estimate arithmetic applies any
seasonal shape at all, as opposed to a flat /12.

**Design choice, 2026-10-19: a half-hourly account is handed an EAC too.** The HH roster records
carried no registry figure, so before a first actual read the opening estimate fell to the TDCV
MEDIUM band: C7 was billed 3,100 kWh a year against 13,230 used. They now take the same figure a
fabric premise does, their own first or trailing year of metered import
(`simulation/run_phase2b.register_hh_accounts_eac`, through `registry_eac_from_own_reads`).
**GAP:** BSCP504's EAC hand-over (s3.2.6.51) is the NHH rule. What a gaining supplier receives for
an elective-HH domestic meter point is not established here. A meter that never communicates, as
C7's does in this world (42 estimates of 42), could not be HH-settled in practice, so it would
carry an NHH EAC drawn from its history. Either reading puts the figure at about the home's own
use, and never at the class average.

## 7. What a supplier estimates from when it holds one read (2026-10-28, K8 for E1)

*Nothing re-fetched; the quoted lines are §1 and §3's, read first-hand on 2026-10-06.*

**Rule / practice.** Both industry methods refuse a short advance. Electricity: "The AA is an
estimate of annualised consumption based on consumption recorded between two meter readings at
least 6 months apart … an EAC is used where two such meter readings are not available" (DESNZ on the
BSC, §1) [M: BSCP504 itself not read]. Gas: the AQ "is based on the consumption between two meter
readings [9–36 months apart]" (Xoserve, §3) [H]. Until the reads span that, the annual figure in
force is the one the supplier was handed on registration (EAC/AQ), or the TDCV where none was.

**What the design did.** The bill estimate re-levelled on the latest three read periods whatever
their span, so an occupier's first, often short, month set every estimate after it: OCC-f6813bf9f05eg
gas, 138 kWh in Oct 2016, then eight estimates totalling about 1,890 kWh against about 8,065 on the
meter (8 of 13 breached runs of `INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER`, 37abacdf42 book).

**Design choice.** The company's own reads set the estimate only once they span the same minimum the
annualised advance already uses (`MIN_ADVANCE_DAYS` 182; gas `GAS_AQ_MIN_ADVANCE_DAYS` 273 where the
bill run's switch asks for it), counted from the change-of-supply opening read to the latest actual.
Before that the estimate is the registry figure spread by the shape (`opening_estimate_kwh`), the
same one billed before the first read; where no registry figure or TDCV is established, the reads
are still used. With the annualised advance on, as the standing policy has it, the three-read window
is then reached only where neither an advance nor a registry figure exists. No new number is set.

**GAP.** Whether a supplier's *billing* estimate (as distinct from settlement) holds the registry
figure for the first six months, or blends it with early reads, is not published (§5). BSCP504's
EAC weighting of a new advance against the prior EAC was not read. *(Read 2026-10-29: §8.
The settlement EAC is NOT held for six months. It moves on every advance, so the six-month line
above describes the AA, not the EAC, and E1's citation of it for the hold is wrong.)*

## 8. How the settlement EAC takes a new advance (2026-10-29, read for the E1 finding)

**Rule (established, read first-hand).** BSC Annex S-2 §4.3.7, as conformed by Modification P40
(Elexon, *P40 Modification Report* v0.3, Jan 2002, §6) and restated in Elexon's current
*Settlement calculation hierarchy: Calculate BM Unit Allocated Demand Volume* guidance:

> "(a) AAAF_KR = max (0, min ((FYC_KR * SPAR), 1.0)); and
> (b) if (AAAF_KR * AA_KR + (1 - AAAF_KR) * PEAC_KR) >= 0, then
> EAC_KR = AAAF_KR * AA_KR + (1 – AAAF_KR) * PEAC_KR
> else EAC_KR = GGPCAEAC_HPC * AFYC_HPR"
> "SPAR is the value of the Smoothing Parameter set from time to time by the Panel applicable on the
> last Settlement Day of the Meter Advance Period"

with AA = MADV / FYC (the guidance's own box), FYC being the profile-coefficient fraction of a year
the advance covers, and PEAC being the EAC in force before it. P40 §4.1 says why: the EAC carries "an
additional element of 'smoothing' to limit the extent to which a single AA value (which may not be
representative of the customer's typical demand level) can affect the forward-looking EAC value."
BSCP504 v53.0 (effective 01 Oct 2024) §4.9 sets the process around it: AAs checked against
GSP-Group Profile Class tolerances from MDD, advances of up to fifteen months processed.

**What this settles.** Every advance, however short, moves the settlement EAC, by a weight equal to
the fraction of the year it covers times SPAR, capped at 1. There is no six-month hold. A 30-day
first month carries a weight of about 0.08·SPAR, and a 122-day span about 0.3·SPAR. So the
industry's own answer to "a short first month should not set a year of estimates" is a weight, not
a threshold. The opening EAC a gaining supplier receives is the previous one carried over the change
of supply (§6, BSCP504 s3.2.6.51).

**GAP: SPAR's value.** It is Market Domain Data, set by the Panel and "a standard positive value
common across all GSP Groups" (EAC/AA URS). No published source within reach states the number,
and MDD is behind a login. Printed at the E1 finding's own inputs (C6, a 122-day span, FYC 0.30),
the blended estimate as a multiple of the reads-only one is:

| registry ÷ reads | SPAR 0.5 | SPAR 1 | SPAR 2 | SPAR 3 |
|---|---|---|---|---|
| 1.47 (SYN-2016-538g) | 1.40 | 1.33 | 1.19 | 1.05 |
| 2.23 (C6, Nov 2016) | 2.05 | 1.86 | 1.49 | 1.12 |

So whether a BSC-shaped blend clears the 179 breaches turns entirely on SPAR. At SPAR 1, C6 still
sits 1.86 times above its own reads. No value is set here.

**Still a GAP, unchanged:** whether a supplier's *billing* estimate follows the settlement EAC, its
own reads, or something else in the first months (§5, §7). §8 is settlement. Gas AQ is a separate
rule: it is not smoothed this way, and it moves only on a 9–36-month read pair (§3).

**Design consequence (not yet built).** E1's six-month threshold has no source. The BSC shape is a
blend weighted by FYC·SPAR, and it can be built only once SPAR, or the billing practice, is
established. Until then E1 stands as the cause of the 179 excepted breaches, now with its citation
corrected.

## 9. What a bill on an actual read charges after estimates (2026-10-29, K8 for class F)

**What the rules require.** SLC 21B.1: when a customer gives a read or the supplier reads the meter,
"the licensee must take all reasonable steps to reflect the meter reading in the next Bill or
statement of account sent to the Customer" (commons, `slc_21b_21ba_reads_and_back_billing.md`, S1).
The read is reflected in full. The licence names no amount below which the read need not move the
bill. SLC 21BA limits how far back an *undercharge* may reach (12 months). It sets no lower bound.

**What published practice says.** Citizens Advice, *If you think you've been charged too much for
your energy* (read 2026-10-29): "If your estimated bill is too high you should take a meter reading
and send it to your supplier. Your supplier will send you an updated, accurate bill instead." And:
"If you've recently sent your supplier a meter reading for the first time in a while, your bill might
be higher than your old, estimated bills … They use these meter readings to give you accurate bills
based on the energy you've used." The page names no minimum correction.

**How a read-to-read bill works.** The bill on an actual read charges the closing read less the last
*billed* read. When that last billed read was an estimate, the error in the estimates is inside the
bill's own advance. Some bills print it as a separate "estimate adjustment" line, but no decision is
taken about whether to bill it: the meter's advance is the charge. A correction of a few pence is
billed or credited the same way as one of a hundred pounds. Over a run of reads, energy billed equals
the register's advance.

**GAP.** No published source we have found speaks to a materiality floor on this correction. The
£5 that `monthly_bill_assembly` once applied had no source. Its own comment borrowed the figure from
`smart_meter_reconciliation`, which models a different mechanism. Whether any supplier suppresses
the *display* of a small adjustment line as a separate line is not established. That would be a
presentation choice, not a change to what is charged.

**Design choice.** Every actual read that ends an estimate run applies the run's correction, whatever
its size, so billed kWh meets the meter. A correction that rounds to £0.00 adds no line. The £5
figure survives only as `catchup_is_material`, a display flag. Before this, 2,747 of 6,452
corrections on the 209c book were dropped, on 754 of 1,293 accounts, leaving 92,490 kWh never billed
or refunded (`SEAT_FINDING_AN_ACTUAL_READ_UNDER_FIVE_POUNDS_OFF_THE_ESTIMATES_NEVER_CORRECTS_THEM_..._2026-10-29.md`).

## Sources

- DESNZ, *Energy Trends Table 4.2*: https://www.gov.uk/government/statistics/gas-section-4-energy-trends (retrieved 2026-10-06, "Domestic" column, 2023–2025)
- DESNZ, *Energy Trends Table 5.5*: https://www.gov.uk/government/statistics/electricity-section-5-energy-trends (retrieved 2026-10-06, "Domestic sales" column, 2023–2025)
- Xoserve, *Annual Quantity (AQ)*: https://www.xoserve.com/help-centre/supply-points-metering/annual-quantity-aq/, retrieved 2026-10-06
- Xoserve, *Demand Estimation*: https://www.xoserve.com/help-centre/demand-attribution/demand-estimation/, retrieved 2026-10-06
- Xoserve/Joint Office of Gas Transporters, *An Introduction to Demand Estimation and DESC* (Oct 2023): https://www.gasgovernance.co.uk/sites/default/files/related-files/2025-07/DESC%20An%20Introduction.pdf
- DESNZ, *Subnational methodology and guidance booklet* (2026), §3.1.3 — already cited in `how_far_a_settled_eac_sits_from_next_years_use.md`
- Ofgem, *Decision on revised Typical Domestic Consumption Values*, 25 May 2023, §1.1 — already cited in `what_a_supplier_holds_to_size_a_direct_debit.md`
- Elexon, *BSCP504 Non-Half Hourly Data Collection* v53.0, effective 01 Oct 2024, §4.9 (read 2026-10-29 via the MHHS document library: https://mhhs-prod-webapp.azurewebsites.net/api/documentlibrary/Background%20Programme%20Context/P478_BSCP504_v53.1.pdf)
- Elexon, *P40 Modification Report* v0.3 (Jan 2002), §4.1 and §6 (BSC Annex S-2 §4.3.7 text): https://assets.elexon.co.uk/wp-content/uploads/sites/11/2012/02/28170318/p40_mr_v0.3.pdf, read 2026-10-29
- Elexon, *Settlement calculation hierarchy: Calculate BM Unit Allocated Demand Volume* (BSC guidance note): https://www.elexon.co.uk/bsc/documents/training-guidance/bsc-guidance-notes/settlement-calculation-hierarchy-calculate-bm-unit-allocated-demand-volume/, read 2026-10-29
- Citizens Advice, *If you think you've been charged too much for your energy*: https://www.citizensadvice.org.uk/consumer/energy/energy-supply/problems-with-your-energy-bill/energy-bill-too-high/, read 2026-10-29 (§9)
- Not read, named for the next reader: the Smoothing Parameter's MDD value; Elexon's live BMRS/SVAA profile coefficient data; the EUC01B Annual Load Profile table (UK Link secure area, UNC-party access only).
