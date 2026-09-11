**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# Both superseded commons artefacts are repaired, and one claim in the finding that opened them is wrong

**Measured:** 2026-09-07, delivery seat, second pass of the day.
**Class:** `figures_on_a_superseded_clock`.
**Discharges items 1 and 2** of *What is next* in
`SEAT_FINDING_TWO_COMMONS_ARTEFACTS_CITE_A_PUBLICATION_THAT_HAS_MOVED_AND_FOUR_OF_NINE_COULD_NOT_BE_ASKED_2026-09-07.md`.
Item 3 (`ofgem_cap_unit_rate_composition`, the `in_filename_only` shape) is untouched and that
finding stays open on it.

## No pre-registration, and saying so rather than back-dating one

The two extensions were arithmetic on figures the opening finding had already sourced, so there was
nothing to predict. **One measurement here did have an answer I did not know, and I did not
pre-register it**: whether the finding's claim about the rolling page's retraction actually held
against the artefact as it stands. It does not, and the correction below is the result. A prediction
filed after the answer is not a prediction, so none is filed.

## What landed

**Every value was re-read from its own publisher on 2026-09-07 rather than transcribed from the
finding.** The finding is in-repo evidence, not a source, and a transcription of a transcription is
how the CM levy's 4.0% got two lanes at once.

| artefact | added | provenance | read at |
|---|---|---|---|
| `ccl_main_rates` | 2027-04-01 electricity **£0.00827/kWh**, gas **£0.00827/kWh** | `primary` | gov.uk content API, `public_updated_at` 2025-11-27T14:23:14+00:00, unmoved |
| `ro_obligation_and_buyout` | OY 2026 level **0.472 ROC/MWh** GB | `primary` | gov.uk *Calculating the level of the RO for 2026 to 2027* (published 2025-09-29) |
| `ro_obligation_and_buyout` | OY 2026 buy-out **£69.34/ROC** | `primary` | Ofgem *RO: buy-out price and mutualisation threshold and ceilings 2026 to 2027* (publication date 31 March 2026) |

All five published CCL columns (2023–2027) were re-read for both fuels and agree with the artefact
to the digit. Ofgem's 2026-27 history table (2010–2027) agrees to the penny with every buy-out row
the artefact already held.

**The RPI→CPI change is recorded**, in a new `basis.buy_out_indexation` key rather than a comment:
through OY 2025 Ofgem uprated the buy-out price by the average monthly RPI change over the preceding
calendar year; following DESNZ's decision announced **28 January 2026**, from 1 April 2026 it is the
monthly **CPI** change, and £69.34 was set from CPI of **3.4%** over calendar 2025. Two indexation
regimes now live in one column, which is why the note says so beside them. Nothing in the file
extrapolates — the note exists so nothing downstream does either without knowing which rule it
would be extending.

**`ccl_main_rates.fetched` moves 2025-11-26 → 2026-09-07.** The old value was never a record; it was
the conservative *bound* the first pass could justify (the latest date consistent with the 2027
column being absent). A bound must not outlive the fetch that replaces it.

Both `checked_for_supersession` verdicts move `superseded` → `current`.
`tools/commons_source_supersession --check`: PASS, 9 artefacts askable.

## Where the opening finding is wrong

> *"Our artefact holds OY 2024 (£64.73) and OY 2025 (£67.06) marked `primary`, whose legend reads
> 'read from THIS entry's own `source` URL'. … the claim is no longer verifiable at the URL that
> backs it."*

**Neither row has cited the rolling supplier page since `e9cdef112`** — checked by reading that
commit's copy of the artefact, not the working tree. OY 2024 cited its own per-year Ofgem
transparency document and OY 2025 cited the 2026-27 notice. And the page has not dropped anything we
rely on: it still serves 2009-10 through 2023-24, so **all eight buy-out rows that do cite it
(2016-17 … 2023-24) were verified against it on 2026-09-07 and every one matches.**

The finding's *mechanism* — a rolling window retracts as well as extends, and a provenance claim can
rot with nobody touching the value or the citation — is real and is worth the re-pointing it caused.
Its *instance* was misattributed. Kept here beside the correction rather than edited out of the
finding, because a wrong claim next to its refutation is the only evidence the check was real.

**The defect that WAS there, one row over.** OY 2025's buy-out was marked `primary` while citing the
**next** year's notice — which this file's own legend defines as `secondary` ("read from ANOTHER
obligation year's notice quoting it in a comparison table"). Demoted to `secondary`. The value is
not in doubt (£67.06 identically in Ofgem's 2026-27 notice); the provenance claim was stronger than
its citation supported. Ofgem's own-year 2025-26 notice was searched for at the 2024-25 URL shape
(`/transparency-document/…`, `/publications/…`), the 2026-27 shape (`/data/…`), and through Ofgem's
search and RO scheme pages: **not located**, and that search is recorded in `open_items` so the next
session does not repeat it. An honest `secondary` with a named reason beats a citation that reads
stronger than the evidence.

**This mislabel needed no publisher to detect.** It is a `primary` claim whose `source` is another
year's document, visible from the artefact alone — the same shape as
`vat_fuel_and_power_de_minimis` carrying the right field in a form nothing could read. The
supersession checker cannot see it, because provenance-vs-citation coherence is a different
question from has-the-source-moved. Filed as the next thing to build, not built here.

## The blast radius, which is why this was not smuggled into the detector's commit

Both lanes' year-keyed tables ended at 2025 and **clamp** past their last key. So until this commit a
date in obligation year 2026-27 was served the 2025 rate:

| table | was served for 2026-27 | published | error |
|---|---|---|---|
| `simulation/policy_costs.py::_CCL_ELECTRICITY_RATE_BY_YEAR` | 7.75 £/MWh | 8.01 | **−3.4%** |
| `simulation/policy_costs.py::_GAS_CCL_RATE_BY_YEAR` | 7.75 | 8.01 | **−3.4%** |
| `company/regulatory/ccl_ledger.py::_CCL_ELECTRICITY_P_KWH` | 0.775 p/kWh | 0.801 | **−3.4%** |
| `company/regulatory/ccl_ledger.py::_CCL_GAS_P_KWH` | 0.775 | 0.801 | **−3.4%** |
| `simulation/policy_costs.py::_RO_COST_BY_OY_START` | 33.06 £/MWh | 32.73 | **+1.0%** |

and 2027-28 CCL was **−6.7%**. All five now tabulate the published years. **The clamp itself is
unchanged and still bites past 2027** — this repair moves the edge, it does not remove it, and
`WORKER_FINDING_THE_COST_STACK_CLAMPS_SILENTLY_INSIDE_ITS_OWN_RUN_WINDOW_2026-08-14` still owns it.

The RO lane needed no table edit: `company/regulatory/ro_commons.py` **loads** both series, so OY
2026 arrived in `OBLIGATION_LEVEL_ROC_PER_MWH`, `BUY_OUT_PRICE_GBP_PER_ROC` and
`EFFECTIVE_RO_COST_GBP_PER_MWH` for free. That is what the 2026-08-19 repair bought.

**THE RO SIGN IS THE ONE THING NO EXTRAPOLATION WOULD HAVE FOUND.** The level *falls* 0.493 → 0.472
while the price *rises* £67.06 → £69.34, so the product goes **down** for the first time since
2023-24. A table extending either series by trend — which is exactly the defect
`roc_ledger` shipped for ten years — would have had the sign wrong, and would have had it wrong in
the first year the price basis also changed. Two reasons to be wrong, landing on one plausible
number.

## One control had to be re-keyed, and it failed the right way

`tests/company/test_phase_oi_ccl_levy.py::test_rate_for_unknown_year_closest` asserted the clamp
returns `_CCL_ELECTRICITY_P_KWH[2025]` **by literal year**. It went red the moment the table gained
the published 2026 and 2027 columns — **red because the code became more honest**, which CLAUDE.md
names as exactly backwards, and it would have stayed green if the clamp had silently stopped
working. Re-keyed to the property: the clamp returns `_CCL_ELECTRICITY_P_KWH[max(...)]`, with a leg
asserting 2030 is actually past the table's end so the test still tests a clamp.

That is the only control that moved. Nothing else was adjusted to fit; the other 113 in the
governing families passed unchanged.

## What is next

1. **`ofgem_cap_unit_rate_composition`** — still `cannot_tell`, still the `in_filename_only` shape,
   still the most dangerous of the five because a dead link announces itself and a landing page
   serving a newer edition does not. Untouched here; the opening finding stays open on it.
2. **A provenance-vs-citation coherence leg**, which is the gap this pass walked into: an entry
   claiming `primary` whose `source` is another year's document. Offline, deterministic, needs no
   publisher — and it would have caught OY 2025's buy-out on the day it was written. It belongs
   beside `tools/commons_source_supersession.py`, not inside it: "has the source moved" and "does
   this citation support the provenance it claims" are different questions and conflating them is
   how a control ends up unable to fail at either.
3. **Ofgem's own-year 2025-26 buy-out notice**, to promote that row back to `primary`.
4. The three `recalled` CCL rows (electricity and gas 2016-04-01, gas 2022-04-01) remain open, and
   are older than any of this.
