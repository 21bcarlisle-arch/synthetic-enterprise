# How a supplier shapes an estimate for an unread month — method and the published monthly shape

**Knowledge:** metering-and-reads

*Discovery pass, 2026-10-06. How a GB supplier turns an annual estimate (EAC/AQ) into an amount
for one unread month, and the published monthly shape each fuel uses. Builds on
`what_a_supplier_holds_to_size_a_direct_debit.md` (annual-figure precedence, TDCV) and
`how_far_a_settled_eac_sits_from_next_years_use.md` (how far that annual figure drifts). This page
is the within-year shape; those two are the annual level and its error.*

*A new account's first months (opening estimate, first DD, opening read, and the pain points with
their ranges): `a_new_accounts_first_months_2026-10-30.md`, from the director's 30 Oct evidence pack.*

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

*[Correction, 2026-11-19, delivery seat: the paragraph above is wrong for the ALP and DAF values.
Xoserve's public readme for the Derived Factors says: "Following a request in 2019, DESC agreed that
the above output [ALPs, DAFs and PLFs] could be shared in the public domain. ... Note the underlying
demand models and supporting files are available to UNC parties on the secure area" (*End User
Categories and Derived Factors*, July 2019, p.2, `xoserve.com/media/7945/readme_euc_df_19_public.pdf`).
The approved files for gas years 2024/25, 2025/26 and 2026/27 can be downloaded from
`xoserve.com/media/0cgkbagq/derived-factors.zip` (retrieved 19 Nov 2026, SHA-256 de7827d8…3e5d). Each
row is `"LDZ:EUC",dd/mm/yyyy,ALP,DAF`, and domestic band 1 non-prepayment is `xx:E2401BND`. The UK Link
secure area holds the models, and the Seasonal Normal 2025 restated history for 2018/19–2024/25.
**Two limits remain.** First, gas years before 2024/25 are not in the public zip. Second, the
licence is "for your use only": no part may be "copied, reproduced, ... stored in a retrieval
system, publicly displayed, republished". This public repository can therefore hold
comparisons made against the ALP, but not its values or a table derived from them. Embedding the
ALP in the company's estimator needs Xoserve's written permission. The comparison made with these
files: `docs/staging/records/SEAT_PREREG_D48_THE_GAS_ESTIMATE_SHAPE_AGAINST_XOSERVE_ALP_2026-11-19.md`.]*

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

**Partly established, 2026-11-19 (D48): one supplier bills an unread month from the settlement
EAC.** OVO's help library (staff-written, updated 2026) says: "If we use an estimated reading on
your monthly summary, it will come from the last actual reading you provided and your Estimated
Annual Consumption (EAC)" (Darran_OVO, updated 03/09/26). It also says "Whenever a new reading is
submitted to the energy industry, a new EAC is calculated for us to use", and that regular readings
"gradually change the EAC until it matches the member's usage" (Tim_OVO, updated 14/07/26). That
is the D0019 EAC (`what_a_supplier_holds_to_size_a_direct_debit.md` §2), not a figure the
supplier re-derives from its own reads. [M]: one supplier, in its own customer help pages. A
secondary consumer guide (Energy Bill Toolkit, checked 2026-11-08) says "Your actual bill is based
on your EAC". It also says new occupants get a TDCV default, which conflicts with OVO's "might
cover the time before you moved in", so it is not relied on. Still unestablished: whether this is
industry practice or one supplier's, and whether the monthly split is profiled or /12.

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
*(2026-11-19: §5 now has one supplier, OVO, billing unread months from the D0019 EAC, which
blends with no hold. So the hold matches neither settlement nor the one billing practice found. It
stays only because every alternative needs SPAR (§8).)*

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

**SPAR: what was searched, 2026-11-19 (D48), and it is still a GAP.**
- *EAC/AA URS* v13.0 (Elexon, 2019) §6.2.6 and assumption 5: the value "must be a positive number",
  is "a standard positive value common across all GSP Groups", "can change over time", and is
  maintained with an Effective From Settlement Date. No value is given.
- *EAC/AA Logical Data Design* v16.0, data item 5.67: "A standard, positive factor, supplied by the
  Market Domain Data Agent, which determines how much weight is given to an Annualised Advance and
  how much is given to the previous EAC". No value is given.
- *EAC/AA Technical Specification* v18.3 (2015): the field holds "a maximum of 6 digits, including
  3 decimal places". **The only number found anywhere is `Smoothing Parameter: 1.100`, effective
  01/01/1997, in §10.5.3's sample "Report on Archived Data" layout**. That layout is printed for
  "Organisation: An Electricity Company", user SYSMAN, with toy coefficients. It illustrates the
  report and is NOT the value: do not cite it as SPAR.
- *EAC/AA System Management Guide* v17.3; *P40 Modification Report* (full text); Elexon's *Market
  Domain Data* page; the bscdocs *Estimation of Annual Consumption System* v15.0 contents (its
  §6.6.12, §7.3.18 and §9.1.7 name the parameter). None states a value.
- **Where the value is:** MDD Online on the BSC Portal (login), or the D0269/D0270 flows "upon
  request" under P30 licence arrangements (Elexon, *Market Domain Data* page). Licensed access is a
  real-world commitment (G5), so it is not open to this project. Supplier help pages (§5) describe
  the blending ("gradually change the EAC") but give no number.

**What it would take, and where SPAR would live.** A real supplier never needs SPAR. Its data
collector sends the recalculated EAC on the D0019 after each read, and per §5 at least one supplier
bills from it. So the faithful build is the world's data collector applying §4.3.7 and handing the
EAC across the seam as an observable. SPAR would then be a world parameter, not a company constant.
It is still the same GAP: at SPAR → 0 the blend is the 182-day hold's opening leg, and at SPAR → ∞
it is reads-only, which re-opens E1's short-first-month breaches (§7). The D48 pre-registration
(`docs/staging/records/SEAT_PREREG_D48_THE_ELECTRICITY_RESIDUAL_BY_ESTIMATE_ROUTE_2026-11-19.md`)
shows the electricity gap improving at every SPAR from 0.5 to ∞. But the E1 breach count at each
SPAR was not measured, so no value is safe to pick from the gap alone.

**Design consequence (not yet built).** E1's six-month threshold has no source. The BSC shape is a
blend weighted by FYC·SPAR, and it can be built only once SPAR, or the billing practice, is
established. Until then E1 stands as the cause of the 179 excepted breaches, now with its citation
corrected.

**Design choice, 2026-11-19 (D48): the blend is built behind a switch, with SPAR as a range.** This
supersedes "can be built only once SPAR is established" above. SPAR is still a GAP, and nothing
here sets it. What changed is the E1 pre-registration
(`docs/staging/records/SEAT_PREREG_D48_E1_BREACHES_AT_EACH_SPAR_2026-11-19.md`). On the 6af7fd0bfd
book the electricity gap fell at every SPAR from 0.5 to 4 (0.407 → 0.379 at 0.5, 0.289 at 3). At
each of those values E1's breach set and flag set were identical to the hold's. The first new
breach appears between SPAR 4 and 6. So across that range the choice between the hold and the
blend does not depend on SPAR's value. It would depend on it only if the real SPAR were about 5 or
more.

- **What is built.** The company bills a hold-route month from a blended EAC: the registration
  EAC (or TDCV MEDIUM), with each of its own read advances blended in by §4.3.7,
  `EAC ← w·(advance/FYC) + (1−w)·EAC`, `w = min(1, FYC·SPAR)`. It spreads that EAC on the profile,
  in the same way as `opening_estimate_kwh`. The hold route is a month with an actual read held but
  reads spanning under 182 days. Electricity on profile classes 1 and 3 only. Unchanged: months
  before the first read (the blend there is the registration EAC itself), route 1 (the annualised
  advance once reads span 182 days), PC2 (per register, a separate question per the D48 prereg),
  and gas (the AQ is not smoothed this way, §3). A zero advance does not move the EAC. That is the
  company's existing rule: a zero advance is a missing measurement. This is the pre-registered
  single-variable change, and no other route moves.
- **Why the company computes it, not the world's data collector.** The faithful shape is the NHHDC
  applying §4.3.7 and sending the EAC on the D0019. The NHHDC is the supplier's appointed agent, and
  its only inputs are the supplier's own reads and the profile. So computing it company-side reads
  nothing a real supplier could not hold. It is a stand-in for the agent. It is not a new view of
  the world. The same SPAR GAP would sit on either side of the seam. Building it company-side keeps
  the change to one variable and lets it be switched off.
- **Why a range and not a value.** A point inside [0.5, 3] would be the invented constant the
  knowledge-first rule forbids: read as established within a week, and unattributable within a month. The range is the
  part the evidence supports: the span over which the decision is the same at every value. 0.5 is
  the lowest pre-registered non-zero column. 3 is the highest pre-registered column, below the
  SPAR 4–6 point where E1 re-opens. The code refuses any SPAR outside the range and names its
  reason. Every grade is reported at both ends, and published as a range, never at a midpoint.
- **The switch.** `DecisionPolicy.bill_estimate_blends_the_eac_at_spar` was `None` (the hold) on
  every standing policy until 2026-11-20. It is now **0.5 on every standing policy**, the low end of
  the range. That is the end that claims least (F11): the smaller pull from the registration
  figure toward the company's own reads. It beat the hold on both books read so far
  (6af7fd0bfd 0.379 against 0.407; 67d454905c 0.361 against 0.388), and E1's breach and flag sets
  were unchanged. Choosing 0.5 does not state SPAR's value. 3.0 stays the other published bound, read
  off each new book by `tools.d48_spar_blend_counterfactual --ends --book-spar 0.5`. The hold
  (`None`) stays reachable as an arm. The first book built with the switch on is pre-registered in
  `docs/staging/records/SEAT_PREREG_D48_THE_ELECTRICITY_RESIDUAL_BY_ESTIMATE_ROUTE_2026-11-19.md`
  ("Switched on").

**GAP, unchanged:** SPAR's value; whether billing follows the settlement EAC as industry practice
(§5: one supplier); and whether the registration EAC this world hands over is a fair stand-in for
the industry figure (the D48 prereg's C6 caveat).

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

## 10. A new account's baseline estimate: the quote's consumption (2026-10-30, the director's ruling)

**Standing.** This is the director's stated understanding of standard practice, not a published
rule (`docs/staging/advisor/done/DIRECTOR_RULING_A_NEW_ACCOUNTS_ESTIMATE_STARTS_AT_STANDARD_PRACTICE_AND_THE_SUPPLIER_EXPERIMENTS_2026-10-30.md`,
07:26 GMT: "The billing estimate should be based on the consumption used in the quote shouldn't it?
… Let's start with what happens today. But the idea should be that the supplier figures out ways to
improve this."). It answers the §7 and §8 GAP for the baseline only. No primary source has yet been
found that refines it; one that does goes here, beside this paragraph.

**The baseline.**
- The billing estimate and the first direct debit both come from the consumption used in the quote:
  the customer's declared annual use where the channel takes one, otherwise the industry figure
  available at quote (the registry or DC EAC for electricity, the AQ for gas, the TDCV where none
  is held).
- Settlement runs separately on the DC's EAC, which takes every advance by the BSC blend (§8). SPAR
  stays a named assumption with no value set.
- The gap between what is billed and what is settled is a measured quantity, reported, not hidden.
  **GAP: not yet measured.** No figure exists on any book.

**What the design already does, and what it lacks.** E1's registry branch (`opening_estimate_kwh`,
§7) is this baseline for the registry half: the quote's figure spread by the shape until the
supplier's own reads span an advance. The declared rung is a world gap, already named in
`company/billing/annual_consumption_estimate.py` (`CUSTOMER_DECLARED`): no supply point the world
draws carries a declaration, so a quote can never be wrong about a home's use, and the supplier has
nothing to learn. Closing it means the world holding a declared figure as a draw with an error
against the home's true use, by channel and by new tenant against established occupier. That is a
world build, filed on the customer-outcomes list, not here.

**The 182-day switch is a policy, not a rule.** When the company's own reads replace the quote's
figure is the supplier's choice. §8 shows the industry blends from the first advance, and §7's six
months has no source. So the switch point is a lever for the supplier's experiments (an early check
at the first read, an early review the customer can see), graded against this baseline. It is not a
fact for a control to enforce.

**Consequence for the controls.** `INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS` grades an estimate
against the estimation policy the supplier declares for that account, plus the duty rules, which
have their own rows (`INV_READ_DUTY_ANNUAL`, `INV_BACK_BILLING_12M`). It does not grade against one
method chosen in advance.

## 11. Does a supplier's estimate follow the home's own seasonal shape? (2026-11-21, E2 (a))

**Read first-hand, 2026-11-21.** British Gas, *If you think your energy bill isn't correct*, under
"Estimated billing": "To estimate your gas usage we will normally use information on how much energy
you used in the same period the previous year, or for electricity we will use the previous
month/billing period." "If we don't hold this information we will use an industry estimation based
on your previous meter readings." [M]: one supplier's customer help page, no date shown.

**What this settles, with OVO's §5 statement beside it.** Two suppliers' published practice is now
on record, and they differ:
- **Gas (British Gas):** the home's own consumption over the same period a year earlier. That is the
  home's own seasonal shape, and it is not the EUC01B average this estimator uses.
- **Electricity:** British Gas uses the previous month or billing period, which is the home's own
  recent rate with no seasonal shape. OVO uses the settlement EAC, which is spread on the class
  profile. **Neither shapes an electricity estimate by the home's own year.** The GAP the E2 (a)
  exception named ("whether a GB supplier does so") is answered for electricity: in the two
  practices found, it does not.

**Design consequence for E2 (a).** The seven electrically heated homes estimated at three to five
times their summer meter are billed the class shape on an annualised advance. That is OVO's
practice, and settlement's. A supplier using British Gas's electricity rule would estimate a June
from May's period. That would be nearer for a heated home in summer, but further off at the turn of
the heating season, which is the flat-window bias slice 3 measured and removed (+10% of billed kWh at
December for electricity). So (a) is the row's lawful tail under a published practice, not a defect
of the method. Keeping it errs against our own thesis: an over-estimate is cash the customer
advances until the next read corrects it (F11). The exception now says so.

**Not built, named for the next reader.** British Gas's gas rule (same period last year, where the
account holds an actual-read window over it) is a sourced alternative to the EUC01B shape. It would
estimate SYN-2016-396g, E2 (b), from its own year. It is a route for the D48 estimate-route
comparison, behind a switch, and graded on a fresh run before it is chosen. Whether British Gas's
rule is industry practice or one supplier's is still a GAP.

## 12. Does any published practice weather-correct what an unread month used? (2026-11-24, D48)

**Why this is asked.** The coupled-triad wall holds W1_14 (the world's weather cells for heat load)
at L2. The gap ledger's row for W1_14 against D48 reads "none: the company holds no belief to
grade". The company's unread-month estimate is seasonal normal and holds no weather feed for
billing (`company/billing/unread_month_estimate.py`). So the question is whether a real supplier
holds a weather-aware belief about what a home used, and if it does, what that belief is built from.
No new source was read for this section. It reads §3, §5 and §11 together.

**Established, from the sources above:**
- **The bill estimate is weather-blind in every published practice found.** British Gas estimates
  gas from the same period a year earlier (§11). That carries last year's weather, not this year's.
  It estimates electricity from the previous period. OVO bills from the settlement EAC on the class
  profile (§5). Neither states any correction for the weather of the month being estimated. A
  seasonal-normal bill estimate is therefore a real supplier's practice, and the error it carries in
  a cold or mild month is a real supplier's error too.
- **Settlement is weather-aware, and a supplier can see the weather it uses.** The gas AQ is
  struck with "the impact of the actual weather experienced in that period" removed (Xoserve, §3).
  The DAF moves the daily NDM allocation with actual weather. The approved ALP and DAF files are
  public (§3 correction, licence "for your use only"). Regional weather is published. So the inputs
  to a weather-corrected belief about what a home used are things a real supplier can observe: the
  home's own reads, the AQ method's weather adjustment, and the weather itself.

**What this means for D48.** The missing belief is not a billing route. It is a separate estimate,
"what this home probably used in this unread month, given the weather that month", built from the
home's reads and published weather. It would sit beside the billed estimate, not replace it. That
is the form the gas AQ already takes in settlement (weather stripped out at calculation, then
restored against actual weather). Grading it against W1_14's cell weather is the gap the ledger
row cannot define today.

**GAP: whether any GB supplier weather-corrects a domestic bill estimate.** §5's GAP stands. The
two practices found do not do so, and none found does. Two suppliers are not the industry.

**GAP: what a shipper receives per meter point.** Whether a supplier receives a daily NDM
allocation for each domestic MPRN, or only the aggregate by LDZ and EUC, is not established here.
If it receives one per MPRN, that allocation is already a weather-aware belief the supplier holds,
and D48 could grade it directly.

**GAP: the electricity side.** Whether Elexon's NHH profile coefficients respond to actual daily
temperature is believed, not read here. Until it is read, the D48 weather belief is built for gas
first, where §3 establishes the method from Xoserve's own text.

**Design choices, made here and why.** (1) The belief is a diagnostic beside the bill, so the
customer is never billed on a method no published supplier uses. (2) It is built from the AQ
method's own form (a weather-normal annual figure re-expressed against actual weather), not from a
fitted constant, because that form is published. (3) The heating sensitivity it needs comes from
the home's own read history. Where the history cannot separate weather from use, the belief is
`None` with that reason, not a class-average stand-in. Filed as its own item:
`docs/staging/WORKER_FINDING_D48_HOLDS_NO_WEATHER_AWARE_BELIEF_ABOUT_WHAT_AN_UNREAD_MONTH_USED_2026-11-24.md`.

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
- Elexon, *EAC/AA URS* v13.0 (P367 redline): https://www.elexon.co.uk/bsc/documents/change/releases/2019-releases/june-release/eac_aa_urs_v13-1_redlined_p367/; *EAC/AA Logical Data Design* v16.0: https://www.elexon.co.uk/bsc/documents/bsc-codes/eac-aa-logical-data-design/; *EAC/AA Technical Specification* v18.3: https://assets.elexon.co.uk/wp-content/uploads/sites/11/2015/04/28163005/EACAA_TechnicalSpec-v18.3.pdf; *EAC/AA System Management Guide* v17.3: https://assets.elexon.co.uk/wp-content/uploads/sites/11/2015/04/28163123/EACAA_SystemManagement-v17.3.pdf; *Market Domain Data*: https://www.elexon.co.uk/bsc/data/market-domain-data/ (all read 2026-11-19, §8 SPAR search)
- OVO Energy help library, *Estimated Annual Consumption (EAC)*: https://forum.ovoenergy.com/charges-payments-refunds-142/estimated-annual-consumption-eac-diy-tutorial-series-8615, and *I give meter readings each month, why is my bill still based on estimates?* (staff answer): https://forum.ovoenergy.com/my-account-140/i-give-meter-readings-each-month-why-is-my-bill-still-based-on-estimates-190/index3.html, read 2026-11-19 (§5)
- Energy Bill Toolkit, *Estimated Annual Consumption (EAC) on an energy bill*: https://energybilltoolkit.co.uk/guides/estimated-annual-consumption-eac-uk/, read 2026-11-19 (§5, secondary, not relied on)
- British Gas, *If you think your energy bill isn't correct* (Estimated billing): https://www.britishgas.co.uk/help-and-support/bills-and-payments/if-your-bills-wrong, read 2026-11-21 (§11)
- Not read, named for the next reader: the Smoothing Parameter's MDD value (licensed access only); Elexon's live BMRS/SVAA profile coefficient data; the EUC01B Annual Load Profile table (UK Link secure area, UNC-party access only).
