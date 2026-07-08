# UK Meter-Read Arrival Delay, Estimation & Failure — Research Findings

Commissioned for Phase 3 of `docs/design/CORE_FIDELITY_PHASES.md` (meter-read arrival/
estimation/failure module — currently zero code in the codebase; settlement records are
treated as instantly and perfectly available). Live web fetch was available this session
(unlike the prior `acquisition_funnel_benchmarks.md` session) — the smart-meter figures below
are pulled directly from the primary DESNZ PDF, not recalled from training knowledge.

---

## 1. Smart meter "not communicating" / estimation-exposure rate (H confidence)

**Source:** DESNZ, *Smart Meter Statistics in Great Britain: Quarterly Report to end December
2024* (Official Statistics, published 20 March 2025). PDF fetched directly:
`https://assets.publishing.service.gov.uk/media/67d95f7c4ba412c67701ed58/Q4_2024_Smart_Meters_Statistics_Report.pdf`,
retrieved 2026-07-08.

A smart meter that has lost WAN connectivity, is with a supplier that can't yet operate it in
smart mode, or is an uncommissioned new-build install reverts to **"traditional mode"** —
Ofgem/DESNZ's own term for exactly the "estimated read" failure mode this phase models
(definition quoted verbatim from the report, p.15): *"When a smart meter loses smart
functionality and needs to be read manually it is in 'traditional mode'."*

Great Britain, end 2024, all meters (domestic + smaller non-domestic), by operating mode:

| Category | Count | % of all meters |
|---|---|---|
| Smart (smart mode) + advanced | 34.32m | 60% |
| Smart (**traditional mode** — lost comms, manual read needed) | 3.67m | 6.4% |
| Non-smart (dumb) meters | ~19.9m | 34% |
| **Total meters** | **57.9m** | 100% |

Of smart meters specifically, **over 90% were operating in smart mode at end 2024** (up 1.3pp
from 89% at end 2023) — i.e. **~10% of installed smart meters were not sending automatic
reads** and required manual reading like a traditional meter.

Domestic breakdown (electricity and gas modelled separately in the SIM, so both given):

| Fuel | Total domestic meters | Smart, smart-mode | Smart, traditional-mode (comms failure) | Non-smart (dumb) |
|---|---|---|---|---|
| Electricity | 29.9m | 19.1m (63.9%) | 1.4m (**4.7%**) | 9.3m (31.1%) |
| Gas | 24.3m | 13.3m (54.7%) | 2.2m (**9.1%**) | 8.8m (36.2%) |

**Read-estimation-exposed population** (dumb meters + smart-in-traditional-mode — i.e. every
meter that cannot deliver an automatic actual read this billing cycle): **~35.8% of domestic
electricity meters, ~45.3% of domestic gas meters** (end 2024). This is the best available
real-world anchor for the proportion of meter-points that are estimation-exposed at any given
time, and it is fuel-differentiated (gas noticeably worse — consistent with gas SMETS
communication being historically less reliable than electricity).

Large suppliers operate 99% of the domestic market; among their domestic smart meters, 90%
were in smart mode at end 2024 vs 86% for small suppliers (a 4pp gap — smaller suppliers have
a worse comms-failure rate, a plausible input if the SIM ever differentiates by supplier
scale). PPM (prepay) meters: 12.1% of domestic smart meters were in prepayment mode, a
plausible extra confounder for read/estimation behaviour (not modelled here, noted for later).

## 2. Traditional (non-smart) meter read cadence — self-read vs estimate (M confidence)

No single DESNZ/Ofgem table publishes an exact "X times per year an actual read is obtained
for dumb meters" statistic in a form this session could directly fetch (several candidate URLs
on ofgem.gov.uk and citizensadvice.org.uk 404'd or redirected to non-matching pages; Wikipedia,
MoneySavingExpert and the Commons Library briefing PDF were also inaccessible this session —
403/blocked). What is directly confirmed:

- Suppliers must take "all reasonable steps" to obtain actual meter readings periodically for
  traditional meters (industry-standard practice is roughly **every 6 months**, with bills in
  the interim based on customer self-submitted reads where provided, or estimates modelled
  from historic consumption where not) — this is well-established industry practice but this
  session could not pull the exact Ofgem Standard Licence Condition (SLC 21A) text live to cite
  a precise number; **flagged as a genuine research gap**, not fabricated.
- Citizens Advice's live consumer-advice page (see §3 below) independently corroborates the
  mechanism: suppliers "estimate [future usage] based on your past usage" whenever an actual
  read isn't available, and explicitly tell customers to "give them regular meter readings to
  make this more accurate" — i.e. self-read submission is the primary alternative to a
  supplier-collected actual read between periodic visits.

**Recommendation for SIM calibration:** use the DESNZ operating-mode proportions in §1 as the
primary calibration anchor (they are real, dated, fuel-split, and directly answer "what
fraction of the book cannot deliver an actual read this period"), and treat traditional-meter
read cadence as illustrative (~6-monthly actual read cycle, self-read/estimate in between)
pending a follow-up session with access to the Ofgem SLC text.

## 3. Ofgem back-billing 12-month rule (H confidence)

**Source:** Citizens Advice, *"If you haven't received an accurate energy bill in a while"*,
`https://www.citizensadvice.org.uk/consumer/energy/energy-supply/problems-with-your-energy-bill/you-havent-received-a-gas-or-electricity-bill-in-a-while/`,
retrieved 2026-07-08 (live fetch, full page text pulled).

Direct quote: *"Under back billing rules, your supplier cannot usually send you a bill for
energy you used more than 12 months ago. The back billing rules don't apply if the supplier
sent you a bill before the year passed and you didn't pay. In this case, the supplier can
still charge you."*

This reflects the industry Back-Billing Code of Practice that Ofgem-regulated suppliers
operate under (originally a 2007 domestic-only voluntary code, later given regulatory teeth
and extended to microbusinesses) — confirmed via this secondary source; this session could not
fetch the underlying Ofgem Standard Licence Condition PDF directly (404s on every guessed
ofgem.gov.uk URL), so the precise SLC number is not independently confirmed, only the 12-month
substantive rule and its one named exception (a timely-but-unpaid bill remains chargeable in
full).

**Relevance to Phase 3:** any meter-read-arrival-delay/estimation-failure module needs a hard
ceiling — an estimated bill that goes uncorrected must resolve (true-up or write-off) within
12 months of the underlying usage, not accumulate indefinitely. This is a real, citable
regulatory constraint the module should encode as a correction deadline.

## 4. Genuine gaps (not found this session)

- No single published "% of all UK domestic bills are estimated" headline figure was found
  despite multiple search attempts (Citizens Advice, Ofgem, Parliament Commons Library,
  MoneySavingExpert, uSwitch were all either 404, blocked, or didn't surface the specific
  historical campaign statistic). The DESNZ operating-mode data in §1 is used as the best
  available proxy instead — it is arguably a *better* anchor for a simulation (real, quarterly,
  fuel-split, dated) than an aging single campaign headline figure would have been.
- Exact non-smart meter read cadence (Ofgem SLC 21A text) not independently fetched — see §2.
- No separate SME/I&C-specific estimation-failure rate found; DESNZ's non-domestic figures (§1
  DESNZ table, non-domestic: 58% smart/advanced overall, 61% non-domestic elec, 32% gas) are
  available if the SIM wants a segment split but weren't reconciled against the domestic figures
  in detail this session — flagged for a follow-up if Phase 3 needs SME-specific values.

---

*Filed by discovery agent, 2026-07-08, for Phase 3 of CORE_FIDELITY_PHASES.md. Read-only
research — no simulation/company/saas code touched.*
