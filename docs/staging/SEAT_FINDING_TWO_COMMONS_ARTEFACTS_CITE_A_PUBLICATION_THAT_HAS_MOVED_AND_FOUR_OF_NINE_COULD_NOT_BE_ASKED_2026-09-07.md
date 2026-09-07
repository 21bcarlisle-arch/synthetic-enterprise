**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# Two commons artefacts cite a publication that has moved, and four of nine could not be asked

**Measured:** 2026-09-07, delivery seat. Predictions fixed before the first fetch in
`SEAT_PREREGISTRATION_WHICH_COMMONS_ARTEFACTS_CITE_A_SUPERSEDED_PUBLICATION_2026-09-07.md`.
**Class:** `figures_on_a_superseded_clock`.

## The one-sentence finding

The CM levy's 4.0% error on 2026-09-07 was not an isolated stale read: **`ccl_main_rates` and
`ro_obligation_and_buyout` are both citing publications the publisher has since revised**, and
**four of the nine commons artefacts carried no fetch date in any form**, so no process anywhere
could have enumerated what needed re-reading.

## What was found, per artefact

| artefact | verdict | evidence |
|---|---|---|
| `ccl_main_rates` | **SUPERSEDED** | gov.uk now publishes a *Rate from 1 April 2027* column (electricity and gas £0.00827/kWh). We stop at 2026-04-01. |
| `ro_obligation_and_buyout` | **SUPERSEDED** | OY 2026/27 published: obligation level **0.472** ROC/MWh GB, buy-out **£69.34**/ROC. We stop at OY 2025. |
| `capacity_market_supplier_levy` | current | Ofgem's cap landing page serves Annex 9 **v1.11** today; the artefact cites v1.11. |
| `capacity_market_auction_results` | current | NESO CKAN `package_show`: auction static data modified 2026-04-29, de-rating 2026-05-14 — both older than our 2026-09-07 read. |
| `uk_vat_rates` | current | gov.uk content API `public_updated_at` = **2014-12-12**. |
| `vat_fuel_and_power_de_minimis` | current | `public_updated_at` = **2025-02-05**, an exact match to the `last_updated_on_the_page` the artefact already stored. |
| `ofgem_cap_unit_rate_composition` | cannot_tell | cites `Default_tariff_cap_level_v1.19.xlsx` behind a *landing-page* URL; that page's current model version was not confirmed this pass. |
| `ofgem_default_tariff_cap_windows` | cannot_tell | unit rates come from a third-party cap-history site with no edition marker. |
| `gb_domestic_switching_rate` | cannot_tell | derived in-repo from a DESNZ quarterly series; the artefact cites the derivation, not an edition. |

## Three things the pass found that the drawn item did not predict

**1. The RO artefact's cited URL no longer contains the values it says it read there.** Ofgem's
supplier page publishes "recent obligation periods" as a **rolling window**, and that window now
ends at **2023-24**. Our artefact holds OY 2024 (£64.73) and OY 2025 (£67.06) marked `primary`,
whose legend reads *"read from THIS entry's own `source` URL"*. Those two rows were almost certainly
read correctly when they were read, and the claim is no longer verifiable at the URL that backs it.
A rolling window does not only fail to extend — **it retracts**, and a provenance claim can rot
without anybody touching either the value or the citation.

**2. The 2026/27 buy-out price is on a different indexation basis.** It is the first year indexed to
**CPI** rather than RPI. `ro_obligation_and_buyout.basis` records the RPI rule and nothing records
that it changed. Carrying the 2026 figure forward without that note would put two indexation
regimes in one column under one stated basis — the shape CLAUDE.md calls *the basis travels with
the number*.

**3. `vat_fuel_and_power_de_minimis` was already carrying the right key and nothing used it.** It
stored `last_updated_on_the_page: "2025-02-05"`, which is exactly the field a supersession check
needs, and it matches the live API to the day. The information was present, in the right artefact,
for months. It was not in a shape any machine could read, so it did no work. **That is the finding
in miniature**: the gap was never knowledge, it was askability.

## Where the prediction was wrong

**P3 said CCL would NOT be superseded.** It is. The 2027 column was added by the page's
2025-11-27 update, and the artefact's rates are otherwise correct to the digit for 2023–2026 — so
this is the CM levy's exact shape a second time: **a correct reading of a publication that has since
been extended.** I recorded P3 at "medium" confidence and reasoned that CCL's defect would be the
already-known `recalled` rows. That reasoning was about the wrong failure mode; the `recalled` rows
are real and are a separate, lesser problem.

**P1 was confirmed but by a route I did not anticipate** — I predicted a newer year on the cited
page, and the cited page had instead *shrunk*. Right answer, wrong mechanism.

**P4/P5/P6 held.** P4 was worthless as predicted and is recorded only so no reassurance is drawn
from it.

## What is fixed in this commit, and what is not

**FIXED.** All nine artefacts now carry a normalised, machine-readable `source_check` block, and
`tools/commons_source_supersession.py --check` refuses an artefact that cannot be asked the
question. It refused 9 of 9 before this commit and passes after. The verdicts above are recorded
in the artefacts themselves.

**NOT FIXED, and deliberately left as an open item rather than a quiet edit.** The two superseded
artefacts are not repaired here. The values are established and sourced above — CCL 2027
£0.00827/kWh both fuels; RO 2026/27 level 0.472, buy-out £69.34 — but landing them means extending
year-keyed tables that several controls in both lanes read, on a basis change (RPI→CPI) that needs
recording, and the two lanes' `_BY_YEAR` tables clamp beyond their last key. That is a repair with
its own blast radius and it deserves its own pass rather than being smuggled into the commit that
built the detector. **The detector is what was drawn; the repair is what it found.** Both artefacts
record `found: "superseded"` and name this document, and the ACTIONED leg refuses any attempt to
record a supersession without naming an open finding — so this cannot be forgotten the way the CM
levy's honest prose caveat was.

## What is next

1. Extend `ccl_main_rates` to 2027-04-01 and record the gov.uk `public_updated_at` it was read at.
2. Extend `ro_obligation_and_buyout` to OY 2026/27, **with the CPI basis change recorded in
   `basis`**, and re-cite OY 2024 and OY 2025 to Ofgem's per-year transparency documents rather
   than to the rolling supplier page that no longer carries them.
3. Settle `ofgem_cap_unit_rate_composition`'s `cannot_tell` by fetching the current cap level model
   and comparing to the cited v1.19. This is the `in_filename_only` shape — a landing-page URL that
   keeps resolving while serving a newer edition — and it is the most dangerous of the five, because
   a dead link announces itself and this does not.
