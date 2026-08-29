# Elexon BSC settlement run timetable — VERIFIED against a primary Elexon document

Research date: 2026-08-29
Scope: closes the verification `settlement_rebilling_best_practice.md` (2026-07-12) asked for and
could not do, and settles the constants in `company/regulatory/settlement_reconciliation.py` and
`simulation/settlement_timetable.py`.

## Access note

`www.elexon.co.uk` is **still bot-walled** — `/bsc/glossary/1st-reconciliation/` returned HTTP 403
this session, the same wall the July note recorded. `bscdocs.elexon.co.uk` resolves but serves only
the document shell (BSCP 01 V30.0, effective 27/11/2025) without body text.

**The route round it: Elexon's own slide deck, hosted on ofgem.gov.uk.** *"Settlement Timetable —
Electricity settlement expert group"*, Jonathan Priestley, Elexon, 16 June 2014 —
`https://www.ofgem.gov.uk/sites/default/files/docs/2014/06/slides_elexon_0.pdf`. Slide 2 is a
labelled diagram of the whole timetable. **This is an Elexon-authored primary document read
directly, not recall.** Everything in the table below is [H].

## The timetable

| Run | | When, after the Settlement Date | NHH energy on actual data | HH |
|---|---|---|---|---|
| **II** | Information run | **1 week** | — | — |
| **SF** | First run | **1 month** | — | 99% |
| **R1** | Interim run | **2 months** | 30% | 99% |
| **R2** | Interim run | **4 months** | 60% | 99% |
| **R3** | Interim run | **7 months** | 80% | 99% |
| **RF** | **Last run** | **14 months** | **97%** | 99% |
| **DF** | *'Extra' runs* — disputes only | **28 months** | — | — |

Slide 2's own labels: II "Information run", SF "First run", R1–R3 "Interim runs", RF "**Last run**",
DF "**'Extra' runs**". Slide 7 confirms DF's nature: *"90 Disputes were closed in 2013. 58 were
upheld, and 56 used the DF run for rectification."* **DF is a dispute rectification run, not a
scheduled stage every settlement day passes through.**

## The correction this forces

`company/regulatory/settlement_reconciliation.py` and its duplicate in
`simulation/settlement_timetable.py` carry **`_RF_MONTHS = 28`, commented `# Final Reconciliation`.**
28 months is **DF**, the dispute run. RF — the last scheduled run, the one that closes the normal
correction window — is **14 months**. The module docstring's opening claim, *"suppliers receive
reconciliation adjustments up to 28 months after each settlement day via the R1/R2/R3/RF run
sequence"*, names the DF lag and attributes it to a sequence that does not include DF.

All four scheduled timings are also wrong, and all four in the same direction (too early):

| | code | Elexon |
|---|---|---|
| R1 | 1 | **2** |
| R2 | 3 | **4** |
| R3 | 5 | **7** |
| RF | 28 | **14** |

**And the shares.** Code apportions the reconciliation volume `0.60 / 0.25 / 0.12 / 0.03`, commented
*"80% of errors found in R1/R2; long tail into RF is small but persistent"*. Elexon's NHH curve is
cumulative 30 / 60 / 80 / 97, i.e. increments of 30 / 30 / 20 / 17, which normalise to
**0.31 / 0.31 / 0.21 / 0.17**. The code front-loads far harder than the real curve and puts **3% at
RF where Elexon's own figure implies about 17%** — so the modelled exposure resolves too early and
too completely, in both timing and amount.

## Vintage, which matters and is bounded

The deck is 2014 and argues *the case for reform*, so the obvious question is whether it still
described 2016–2025. It did, and Elexon says so in its MHHS material: **"the current Settlement
process takes 14 months to complete"**, reducing to **four months** only under Market-wide
Half-Hourly Settlement. MHHS central systems (Milestone 10) went live **24 September 2025**, with
meter migration running ~19 months to a programme deadline of **May 2027** (extended 6.5 months by
Ofgem, 29 November 2024).

**`run_phase2b.REPORT_END` is 2025-06-07 — before MHHS go-live.** So RF = 14 months applies to the
entire modelled window with no time-variation to model. The four-month timetable becomes relevant
only if the window is ever extended past late 2025, and then only progressively as meters migrate.

## What it settles for the publish interval

`SETTLEMENT_CUSTOMER_YEAR_BUDGET`'s time leg has no non-circular basis
(`docs/design/SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md` §7), and the external anchor proposed for
it was *"how often the inputs this site reports actually change"*.

**They cannot change any more.** 2025-06-07 + 14 months = **2026-08-07**. The reported window
reached Final Reconciliation **three weeks ago**. No new Elexon data can revise a figure inside it,
so there is no data-freshness requirement on the publish interval at all — it is purely a choice
about how quickly our own changes become visible, which makes it the director's to name rather than
something to be measured.

Worth noting how narrow that is: the same question asked in July would have had the opposite
answer, and asking it again is only safe while `REPORT_END` stays put.

## Sources

- Elexon, *Settlement Timetable — Electricity settlement expert group*, Jonathan Priestley,
  16 June 2014 (slides 2 and 7). Hosted at
  <https://www.ofgem.gov.uk/sites/default/files/docs/2014/06/slides_elexon_0.pdf> — **[H], read
  directly.**
- Elexon, *Suppliers start moving meters to half-hourly settlement…*, 22 October 2025:
  <https://www.elexon.co.uk/2025/10/22/suppliers-start-moving-meters-to-half-hourly-settlement-hitting-a-major-milestone-for-clean-power-2030/>
  — 14 months current, four months under MHHS, M10 live 24 September 2025. **[M], via search
  summary; the elexon.co.uk page itself is behind the same bot wall.**
- Ofgem, MHHS Change Request CR055 decision (programme deadline May 2027). **[M], same caveat.**

**Still unverified and named as such:** the HH ±0.5% / non-HH ±4% reconciliation variance bands in
`settlement_reconciliation.py`, whose stated source is a general attribution (*"Elexon Settlement
Performance Reports; Ofgem supplier review data"*) rather than a citation. The 2014 deck gives
percentages of energy settled on actual data, which is a different quantity, so it does not settle
them. They are the next thing to verify in this file.
