**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `A45_the_canon_is_a_standing_subject`

# The VAT de minimis is two published numbers and the code had one of them, applied to both fuels

**Found:** 2026-08-31, working the domain-constant origin debt down. The constants gate has stood at
**197 no-origin, 2 collisions, unmoved** since it was built the night before, so this is the first
of that debt actually paid rather than counted.

## The rule, established from the published record before anything was changed

**VAT Notice 701/19 (HMRC), fetched 2026-08-31.** A supply of fuel and power to *business* premises
at or below its fuel's de minimis rate is charged at the reduced rate; above it, the standard rate.

| fuel | limit | the notice's words | section |
|---|---|---|---|
| electricity | **33 kWh/day** (1,000 kWh/month) | *"supplies of not more than an average rate of 33 kilowatt hours per day, 1,000 kilowatt hours per month"* | §5.2 |
| gas | **145 kWh/day** (5 therms/day, 4,397 kWh/month) | *"supplies of not more than an average rate of 5 therms or 145 kilowatt hours per day, 150 therms or 4,397 kilowatt hours per month"* | §4.2 |

**Gas's limit is 4.39x electricity's.** Domestic supply is reduced-rated regardless of quantity —
a de minimis test applied to a domestic account is not redundant, it is a different rule.

Filed in the commons: `docs/domain_artefact_library/regulatory/vat_fuel_and_power_de_minimis.json`.

## The defect

```python
SME_VAT_THRESHOLD_KWH_PER_DAY = 33.0          # no comment, no source

def _sme_vat_rate(daily_kwh: float) -> float:
    return 0.20 if daily_kwh > SME_VAT_THRESHOLD_KWH_PER_DAY else 0.05
```

`_sme_vat_rate` takes **no fuel argument**, and its caller `_invoice_to_section(inv, fuel, ...)`
runs **once per fuel leg**. So every SME gas leg was tested against electricity's threshold, and
**the whole 33–145 kWh/day band was charged the standard rate where the law says reduced.**

That is the direction that matters. Under-charging VAT leaves the supplier owing HMRC the
difference; **over-charging it takes money from a customer that was never owed.** A mid-sized SME
gas account at 100 kWh/day was being billed 20% on a supply the law reduced-rates.

## Severity, measured rather than inferred

**LATENT.** `company/billing/dual_fuel_bill` has exactly one non-test importer,
`company/portal/app.py`, and the portal **is not served** — the only uvicorn unit in the repository
is `background.file_api`. No bill a reader can see carries the wrong figure. The instrument is
wrong; the exposure is nil.

Filed this way round deliberately. The first VAT finding of 2026-08-30 was filed BLOCKING on the
inference *"a published figure may be wrong"* and corrected to LATENT ten minutes later by
measuring. Measuring first this time.

## Repaired

* **The limits live in the commons and the module reads them at import.** Same doctrine and same
  shape as `company/crm/market_conditions._load_published_rate_pct` — the commons is the published
  record, readable by every lane, and what stays owned per lane is the *reading*.
* **`_sme_vat_rate(daily_kwh, fuel)` — `fuel` is required, with no default.** A default is what
  would re-create this the moment a third call site appears.
* **An unknown fuel raises**, naming the fuels the artefact does carry, rather than falling back to
  another fuel's threshold. Refusing to bill is safe; billing at a rate no published limit supports
  is a legal error whichever way it lands.
* **The loader fails closed** on a missing, empty or malformed artefact. A VAT threshold that
  quietly defaults to a hard-coded number is the original defect: the fallback is what let one
  fuel's limit stand in for both for as long as nobody looked.
* `SME_VAT_THRESHOLD_KWH_PER_DAY` survives under its old name for its existing importers, but is now
  **derived** from the table rather than restated, so it cannot become a second answer.
* Control: `tests/company/billing/test_the_vat_de_minimis_is_per_fuel.py`, seven legs, **seven
  mutations proven to fire** — one threshold for both fuels, a defaulted `fuel`, a fallback instead
  of a raise, the boundary flipped to `>=`, the limits hard-coded instead of read, the loader
  defaulting, and the artefact losing its declared gaps. **Keyed to the published rule, not to 33
  and 145**: neither figure is written in the test, so if HMRC moves one, the artefact changes and
  every leg still passes.

## What this does NOT fix, declared rather than left to be found

1. **Whether the limits moved across 2016–2025 is NOT established.** The notice page records that
   the de minimis *guidance* section was updated 2022-05-16; that is a change to the guidance and is
   not evidence the figures changed. Everything in this repository modelling a year before 2025 uses
   today's limits for that year, and nobody has checked. Declared on the artefact.
2. **The rates themselves (0.05 / 0.20) are still unsourced.** Notice 701/19 names "the reduced
   rate" and "the standard rate" and states neither percentage — it points at
   `gov.uk/vat-rates`. Copying them into this artefact would attach its citation to figures it does
   not carry, which is how an unsourced number acquires a source it never had. They need their own
   artefact against their own page.
3. **`VAT_RATE` is still one name with two values** — `company/billing/invoice.py` = 0.05 and
   `saas/non_commodity.py` = a per-segment table. Untouched here; that is the *rate* question above,
   not the de minimis one, and both are held in
   `test_a_domain_constant_carries_its_origin.KNOWN_NAME_COLLISIONS` as an exact set so fixing
   either reds the gate until its entry is removed.
4. **The averaging window is a named simplification.** "An average rate per day" is computed over
   the billing period here; the notice does not say the period, and whether it should be a month or
   a rolling window is unchecked.

## The other collision, resolved as a FINDING rather than a value

`MAX_CHURN_PROBABILITY` = 1.0 in `company/crm/churn_model` and 0.95 in `saas/churn_model` is **not
a disagreement about a number.** Read: the 1.0 is the **asymptote** of a saturation curve, set
deliberately on 2026-08-25 with a stated reason (*"a decision that maximises `P(stay) x margin` is
unbounded for any asymptote below 1.0 and bounded for 1.0 exactly"*), and it already carries a
belief origin. The 0.95 is a **hard cap** inside a `min()`. Two different quantities wearing one
name.

The rename that would say so touches **83 references across 25 files**, including live company code
and a published grading tool. Not started here: a diff that wide across the company's churn model,
on a shared tree with two other sessions writing it and a churn capture running, is the trade that
goes wrong. Registered as its own item.

---

## And paying the first unit of debt exposed a hole in the gate that counts it

**The debt moved 197 → 196, and NOT because a constant gained an origin.** It moved because
`SME_VAT_THRESHOLD_KWH_PER_DAY = 33.0` stopped being a numeric literal: it is now
`SME_VAT_DE_MINIMIS_KWH_PER_DAY = _load_de_minimis()`, read at import from a cited commons
artefact. `scan()` only sees constants whose value is a literal, so **it stopped seeing this one
at all.**

**The count could not tell the best possible repair from a deletion, and fell either way.** That is
the same family as *debt paid by renaming out of scope*
(`feedback_a_ratchet_with_no_floor_cannot_fail`, 2026-08-30) in a new disguise: **debt paid by
promoting a literal to a read.** Left alone, this gate would have rewarded leaving a number in
place with a comment over replacing it with the authority — the exact opposite of the rule it
enforces.

**Measured, and it is bigger than my one unit: 29 constants were ALREADY promoted and invisible.**
`_CAP_ANCHOR_YEARS`, `UNIT_RATE_ELEC_RESI_BY_YEAR`, `MARKET_SWITCHING_RATE_PCT_BY_YEAR`,
`STATUTORY_RATE_HISTORY_START` and 25 others — many of them `Call`s reading the commons, which is
the best shape a domain constant can have. **So the 197 baseline was never the whole population.
It excluded the constants that had already been done properly**, and a count built that way can
never show progress made the right way.

### Repaired

* `tools/domain_constant_origins.promoted()` — every domain-named module constant whose value is
  **not** a literal, with the AST form it took. Reported on every run and behind `--promoted`.
  Deliberately a COUNT a reader can subtract rather than a static "does this call reach the
  commons" classifier, which would be a guess.
* `test_the_whole_domain_named_population_is_still_in_scope` — a floor under **literals +
  promoted**, so neither half can quietly leave. Renaming out of the regex, deleting, and promoting
  all reduce the debt; only this separates *the scan lost its subject* from *the work was done*.
  Second leg: `promoted()` must be non-empty, because zero means it has broken shut and every
  future proper repair would read as a deletion.
* Mutation-proven: `promoted()` returning nothing reds; narrowing `DOMAIN_NAME` now reds **four**
  tests where it red three; the null rung (`scan()` walks no files) reds four.

**The debt ceiling stays at 197 and the floor at 150.** Neither moved: 196 is inside both, and
lowering the ceiling to 196 would claim a unit of progress the paragraph above says the count
cannot see. When the debt is next worked down by a repair the count CAN see, the ceiling moves and
that edit is the record.
