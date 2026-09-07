**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# PRE-REGISTRATION: which commons artefacts cite a publication that has moved, written before I look

**Written:** 2026-09-07, delivery seat, claim `a-commons-artefact-cannot-tell-when-its-source-was-revised`.

The drawn item asks for a control over supersession. A control needs a defect it can find, and the
honest way to establish whether this class is real — rather than a tidiness exercise — is to go and
ask the publishers. This file fixes what I expect them to say before I ask.

## What is already established as I write, and is therefore NOT a prediction

I have read all nine JSON artefacts under `docs/domain_artefact_library/regulatory/`. Their source
citations are in **six mutually incompatible shapes**, and this is measured, not predicted:

| artefact | where the source lives | a fetch DATE? | a VERSION token? |
|---|---|---|---|
| `capacity_market_supplier_levy` | `source.{workbook,url,fetched,supersedes}` | **yes**, machine-readable | **yes** (`v1.11`, and in the URL) |
| `uk_vat_rates` | `source.{document,url,fetched}` | yes, machine-readable | no |
| `vat_fuel_and_power_de_minimis` | `source.{document,url,fetched,last_updated_on_the_page}` | yes, machine-readable | yes — the page's own "last updated" |
| `capacity_market_auction_results` | `source_urls.*` + `fetched_pass` | **only inside a prose sentence** | no |
| `ro_obligation_and_buyout` | per-row `source` + `fetched_pass` | **only inside a prose sentence** | no |
| `ccl_main_rates` | per-row `source` | **none anywhere** | no |
| `gb_domestic_switching_rate` | `series_source` | **none anywhere** | no |
| `ofgem_cap_unit_rate_composition` | `source_url` | **none anywhere** | no |
| `ofgem_default_tariff_cap_windows` | `window_boundaries_source`, `unit_rate_source` | **none anywhere** | no |

**Four of nine carry no fetch date in any form**, so the supersession question cannot even be put to
them: there is no "since" for "revised since we read it" to be measured from. Two more carry the
date only inside an English sentence a reader must parse. This is the finding the drawn item
predicted, and it is settled before any network call.

Two edges of our own record, also read and therefore not predictions:

* `ro_obligation_and_buyout` ends at **obligation year 2025** in BOTH series (obligation level and
  buy-out price). Its `fetched_pass` is 2026-08-19.
* `ccl_main_rates` carries rates to **2026-04-01** and holds **3 rows marked `recalled`** — electricity
  and gas at 2016-04-01, gas at 2022-04-01 — with `source: null` and `source_label: "not fetched"`.

## The predictions

Answers I do not have. Written before the first fetch of this pass.

**P1 — RO buy-out price is SUPERSEDED.** Ofgem sets the buy-out price by RPI indexation and
announces it in the February before the obligation year opens. OY 2026/27 opened on 1 April 2026,
five months before today. I predict Ofgem's supplier page **publishes a 2026/27 buy-out price we do
not hold**, and that it is above GBP67.06. *Confidence: high.*

**P2 — RO obligation level is SUPERSEDED.** The level for an obligation year is set by notice on or
before 1 October preceding it, so OY 2026/27's level was set by 1 October 2025. I predict a
published 2026/27 obligation level we do not hold, in the range 0.45–0.52 ROC/MWh. *Confidence: high.*

**P3 — CCL is NOT superseded, and its gap is not a supersession gap.** I predict the gov.uk rates
page publishes nothing beyond 2026-04-01 that we lack, and that the defect in this artefact is the
one already recorded — three `recalled` rows never fetched at all. Different disease from the CM
levy's. *Confidence: medium.* The interesting sub-question, which I will also ask: does
legislation.gov.uk settle the 2016 rows, i.e. is the "not located this pass" note itself stale?

**P4 — Annex 9 is CURRENT.** v1.11 was fetched today. I predict no v1.12. *Confidence: high, and this
prediction is nearly worthless* — I record it because a check that only ever runs against sources
fetched the same day would be a control that cannot fail, and saying so now stops me claiming
reassurance from it later.

**P5 — the NESO Capacity Market register is CURRENT** but its URLs are **date-stamped in the
filename** (`cmu_20260902.csv`, `component_20260902.csv`), so a later register publishes at a
DIFFERENT URL and our stored URL will keep serving the old file rather than 404ing. I predict the
dataset landing page lists a resource newer than 2026-09-02 within weeks, and that **nothing in the
artefact would notice**, because a URL that still resolves reads as a source that is still current.
*Confidence: medium on the dated resource, high on "nothing would notice".*

**P6 — the two VAT artefacts are CURRENT** (fetched 2026-08-31, seven days ago). *Confidence: high.*

## What "found a defect" means, and what would refute the whole premise

The premise of the drawn item is that supersession is a live class across the commons, not a
one-off that happened to the CM levy. **It is refuted if P1–P6 all come back "current"** — that
would mean the commons is in fact fresh, the CM levy was an isolated stale read, and the right
deliverable shrinks to the structural block alone with no repairs attached.

It is confirmed if **any** artefact other than the CM levy is citing a publication the publisher has
since revised. P1 and P2 are the two most likely, and they are in the same artefact, so a single
confirmation carries less weight than the count suggests. I will say so if that is how it lands.

## What I am building regardless of the answers

Following `tools/startup_anchor_freshness.py`, which learned this the expensive way: **refuse the
lie, report the age.** A control keyed to age goes red for a reason nobody can act on inside a
commit and gets turned off.

* **REFUSED** (offline, deterministic): an artefact that cannot be ASKED the question — no normalised
  `source_check` block naming publication, URL, fetch date, and what the version token is. Plus the
  coherence legs: a check dated before the fetch, a version claimed where the source publishes none,
  a version in the block that disagrees with the version in its own URL, a `superseded` verdict
  recorded with nothing said about what changed.
* **REPORTED, not refused**: how old each check is and which are due.

The offline half is the load-bearing one. What the CM levy incident actually cost us was not a
wrong number — the artefact's caveat was honest and correct — it was that **no machine anywhere
could put the question**. Four of nine still cannot.
