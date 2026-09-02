**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `the-annual-report-publishes-one-shock-field-a-hundredfold-apart-and-ignores-the-split-that-supersedes-it`

# FINDING — the bill-shock population split has one implementation and it is in the wrong layer

**Filed: 2026-09-02, delivery seat.** LATENT, not BLOCKING: no published figure is wrong as a
result of either half below. Both are structural residue of the MAJOR units/definition fix that
landed alongside this document, left because the repair each needs is outside that change's
pathspec.
**Found while:** wiring `saas/reporting/annual_report.py` to the population split that already
existed, closing the hundredfold units defect
(`PREREG_ANNUAL_REPORT_BILL_SHOCK_UNITS_AND_BAND_2026-09-02.md`).

---

## What is wrong

`_annual_shock_by_population` and `_shock_stats` — the functions that compute what a bill shock is
per population, with n and a bootstrap interval — live in `tools/generate_dashboard_data.py`. So
does `SHOCK_DEFINITION_POPULATION`, the constant that decides *which population's figure is a bill
shock at all*.

`saas/reporting/annual_report.py` now imports all three, lazily, to avoid minting a second
implementation. That was the right call at the fork — two implementations of one published quantity
is this project's most expensive recurring shape, and the VAT rule (one legal requirement, five
implementations, a defect fixed in one in July and still live in another in August) is what it costs
— but the direction of the dependency is backwards. A publishing tool now owns a domain definition
that the business layer has to reach up into.

The population constants it is derived from (`BILL_SHOCK_POPULATION_BY_PAYMENT_CHANNEL`,
`UNKNOWN_BILL_SHOCK_POPULATION`) are already in `saas/bill_generator.py`. The definition is split
across two layers with the derived half above the raw half.

## Why it did not get fixed in the same change

The drawn pathspec was `saas/reporting/annual_report.py`, `tests/saas/`,
`docs/reports/ANNUAL_REPORT.md`, explicitly excluding `tools/generate_dashboard_data.py`. Moving the
function needs the dashboard generator in the pathspec to re-point its own call site. Importing the
existing one was strictly better than writing a rival that can drift, so that is what landed.

## The repair

Move `_annual_shock_by_population`, `_shock_stats`, `_bootstrap_mean_interval`,
`SHOCK_DEFINITION_POPULATION` and `UNMEASURABLE_SHOCK_POPULATION` into `saas/` beside the population
constants they derive from — `saas/bill_shock_populations.py` or into `saas/bill_generator.py`. Have
BOTH `tools/generate_dashboard_data.py` and `saas/reporting/annual_report.py` import from there.
The lazy imports in `annual_report.py` become ordinary top-level ones and the comment explaining why
they are lazy goes with them.

`test_the_defined_population_matches_the_dashboards_own_constant`
(`tests/saas/reporting/test_a_rendered_shock_figure_is_in_the_units_of_its_own_percent_sign.py`)
holds the coupling until then: if a second copy of the constant ever appears and they disagree, it
goes red.

---

# SECOND FINDING, same document, filed here because it has the same cause

**Severity:** LATENT · **Lane:** `C_customer_ops` (the header above carries `D_billing_metering` for the first finding; only one lane parses per document, and this half belongs to customer ops)

`company/crm/service_quality_monitor.py` carries two defects that the annual report has now routed
around rather than fixed, because `company/` was outside the pathspec:

1. **`bill_shock_rag` fails OPEN on a missing measurement.**
   `if self.avg_bill_shock_pct is None or self.avg_bill_shock_pct < _BILL_SHOCK_AMBER: return
   GREEN` — an unmeasured shock reports the best branch. That is the exact shape of the `or 0.0`
   defaults the report fix just closed, one layer down. `overall_rag` then ORs it in, so an
   unmeasured leg silently improves the overall verdict.
2. **`_BILL_SHOCK_AMBER = 0.20` / `_BILL_SHOCK_RED = 0.30` carry the comment `# pct` and are
   compared against a FRACTION**, and the module docstring attributes them to Ofgem: *"Ofgem
   benchmarks: complaints < 2.5% of bills; clarity > 0.80; bill shock < 0.30%."*
   `docs/market_research/BILL_SHOCK_EVENT_TYPES_ANCHORS.md` §3 records the search for exactly this
   and its answer: **"Confirmed: no"** — no Ofgem definition of bill shock as a term, threshold or
   comparison basis. The `< 2.5%` complaints figure and the `> 0.80` clarity figure in the same
   sentence are **also unchecked** and should be run through the commons on the same pass; the
   report's clarity/complaint bands are still published on that attribution's strength.

The annual report no longer reads `bill_shock_rag`, `overall_rag`, `worst_bill_shock_year`,
`red_years` or `amber_years`, and passes `avg_bill_shock_pct=None` — so nothing published today
depends on any of this. **It is a loaded gun for the next caller**, and `worst_bill_shock_year`
will now raise on a `None` if anything calls it, which is a fail-closed accident rather than a
design.

## The repair

Make `avg_bill_shock_pct: Optional[float]`, have `bill_shock_rag` return a fourth
`NOT_MEASURED` state (or raise) rather than GREEN on `None`, make `overall_rag` propagate it, make
`worst_bill_shock_year` skip unmeasured years, and either source the three bands from
`docs/domain_artefact_library/` or restate them in the docstring as this project's own working
thresholds with the "Confirmed: no" citation beside them — the way
`annual_report._SHOCK_BAND_ATTRIBUTION` now does.
