# EP14 — The published cost stack: the constants checked against the publications, at last

**Atom:** `EP14_adapter_published_cost_stack` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-17 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom is
epoch-3 BUILD-gated (`block_reason`: director-reserved curriculum sequencing, R13);
`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level:** HELD at 0 — the adapter is the deliverable, not the document (EP10 precedent, as passes 2 and 3).
**Map and note store deliberately NOT edited** — `tests/design/test_simplifications_store.py` couples
`simplifications_count` to the store file's note count, so a note append obliges a same-commit map edit,
and `docs/design/maturity_map.yaml` carries other lanes' hunks. This document is the record.

**This is the FOURTH pass on EP14, and it is the first with network access.** Three prior passes each
deferred the same item, and each named the same reason:

> pass 1 (note store): *"the gas tables' **values** were not re-checked against source"*
> pass 3 (§7): *"The gas tables' *values* still not re-checked against source — open since the first pass."*
> pass 3 (§7): *"**No external source fetched: this tick had no network.** Nothing here claims any
> tabulated rate is numerically wrong."*

This tick had network. **The deferral was never a judgement — it was an unavailable input**, and the
moment the input became available the item took twenty minutes. Worth naming as a pattern: an item
deferred three times for a *stated environmental reason* is not the same as an item deferred three times
on merit, and the register did not distinguish them. Everything below is `observed-with-evidence` unless
labelled otherwise (R9). **MEASURED AT:** HEAD `cb82f3af5`, live `docs/reports/run_output_latest.json`,
`simulation/policy_costs.py` functions called directly, nothing monkeypatched.

---

## 1. THE FINDING — the gas CCL table is exact against the statute on ten years out of ten; the electricity CCL table, transcribed from the SAME statutory rows, is out by £49,208

`simulation/policy_costs.py` carries two CCL tables. They are two columns of one table in one Act, set
by one section, on one date each year. The gas column was transcribed correctly. The electricity column
was not.

**Gas CCL — `_GAS_CCL_RATE_BY_YEAR`, checked by calling the shipped reader:**

| OY | model £/MWh | published £/kWh | published £/MWh | match |
|---|---:|---:|---:|:--:|
| 2016 | 1.95 | 0.00195 | 1.95 | ✅ |
| 2017 | 1.98 | 0.00198 | 1.98 | ✅ |
| 2018 | 2.03 | 0.00203 | 2.03 | ✅ |
| 2019 | 3.39 | 0.00339 | 3.39 | ✅ |
| 2020 | 4.06 | 0.00406 | 4.06 | ✅ |
| 2021 | 4.65 | 0.00465 | 4.65 | ✅ |
| 2022 | 5.68 | 0.00568 | 5.68 | ✅ |
| 2023 | 6.72 | 0.00672 | 6.72 | ✅ |
| 2024 | 7.75 | 0.00775 | 7.75 | ✅ |
| 2025 *(clamped)* | 7.75 | 0.00775 | 7.75 | ✅ |

**Ten out of ten, to the penny — including the clamped year.** The first pass's open item is closed
GREEN, and that is the honest headline for the gas side.

**Electricity CCL — `_CCL_ELECTRICITY_RATE_BY_YEAR`, same method:**

| OY | model £/MWh | published £/MWh | delta | provenance of the published figure |
|---|---:|---:|---:|---|
| 2016 | 5.44 | 5.59 | −0.15 | recalled, not fetched |
| 2017 | 5.54 | 5.68 | −0.14 | recalled, not fetched |
| 2018 | 5.83 | **5.83** | **0.00** | recalled, not fetched |
| 2019 | 6.11 | **8.47** | **−2.36** | **PRIMARY** — FA2016 s.147 |
| 2020 | 7.17 | 8.11 | −0.94 | **PRIMARY** — FA2020 s.92 |
| 2021 | 7.17 | 7.75 | −0.58 | recalled, not fetched |
| 2022 | 7.17 | 7.75 | −0.58 | **PRIMARY** — FA2021 Pt.3 |
| 2023 | 7.26 | 7.75 | −0.49 | **PRIMARY** — FA2021 Pt.3 + gov.uk CCL rates |
| 2024 | 7.35 | 7.75 | −0.40 | **PRIMARY** — gov.uk CCL rates |
| 2025 *(clamped)* | 7.35 | 7.75 | −0.40 | **PRIMARY** — gov.uk CCL rates |

**2018 matching exactly is the control, and it is what makes this an error rather than a modelling
choice.** It proves the intended subject (the *main* rate, not a CCA-discounted or effective rate — the
module comment says so too: *"Business electricity pays the main CCL rate"*) and the intended unit
convention (p/kWh × 10 = £/MWh). One year lands dead on it. The rest do not.

**The shape is inverted, not merely mis-levelled.** The model's table rises smoothly, 5.44 → 7.35, and
its own comment names the wrong year for the step:

    2020: 7.17,    # April 2020: step-change — electricity CCL raised as gas CCL frozen

The actual history is a **step UP in April 2019** (5.83 → 8.47, the Budget-2016 rebalancing) followed by
a **DECLINE** (8.11, then 7.75 flat to date). April 2020 was a *cut*. So the comment asserting the
step-change is not just attached to the wrong year — it has the wrong sign. The model has invented a
gentle monotonic climb where the statute has a spike and a taper.

**Exposure, on business electricity volume from the run's own `bills`** (resi excluded — domestic
electricity is CCL-exempt and the shipped reader returns 0.0 for it), each bill's kWh apportioned evenly
across its period days and bucketed by Apr–Mar obligation year:

| | |
|---|---:|
| model electricity CCL line | £459,799.16 |
| **understatement, PRIMARY-fetched years only** | **£43,074.89 (9.4%)** |
| understatement including recalled years | £49,208.14 (10.7%) |

**£43,074.89 is the defensible floor** — it uses only years whose published rate I fetched from the
legislation or the publisher myself. The larger figure is stated for completeness and rests partly on
recall; do not quote it without re-fetching 2016, 2017 and 2021. **2019 alone is £18,274.68**, 42% of the
floor, because that is the year the model missed the step.

Filed as `docs/staging/done/WORKER_FINDING_THE_ELECTRICITY_LEVY_TABLE_DIVERGES_FROM_THE_STATUTE_ITS_GAS_TWIN_MATCHES_2026-08-17.md`
(**BLOCKING** — queued, not fixed, per SELF_INTERRUPT discipline; grading argument in the finding).

**REPAIRED 2026-08-17** by the RUNG-1c BUILD draw that took this blocking finding off the lane. The
nine divergent years now carry the statutory figures; verified on the shipped functions, nothing
monkeypatched: `get_ccl_per_mwh("2019-06-01", "I&C")` → `8.47` (was `6.11`) and
`("2020-06-01", "I&C")` → `8.11` (was `7.17`), against FA2016 s.147 `£0.00847/kWh` and FA2020 s.92
`£0.00811/kWh` — the same sections that set the gas rates directly beneath them, which were already
exact. The step now lands in **April 2019 and upward**, where the statute puts it, instead of April
2020 and the wrong sign.

The instance fix alone would breach R10, so the CLASS is what was actually built. Because the defect
was a MIS-TRANSCRIPTION and not a missing citation, the control cannot be another census: the pinned
rates live in the regulation commons at `docs/domain_artefact_library/regulatory/ccl_main_rates.json`
in **the statute's own unit (GBP/kWh)**, never the model's GBP/MWh, and
`tests/simulation/test_policy_cost_values_vs_source.py` performs the conversion. That is what keeps
the checked value independent of the value it checks — had the commons carried GBP/MWh, the control
would have been the R15 tautology shape that let B5 score this table green in the first place.
Provenance is load-bearing: only `primary` (fetched this pass) and `bracketed` (both neighbours
primary AND equal) entries are asserted as equalities; the three `recalled` years are EXCLUDED from
the assertions and counted against a ratchet, so an unverified year is visible rather than silently
trusted.

R15 — mutation-proven, all six fire, unmutated baseline 13 passed:

1. the named defect replayed (2019 restored to `6.11`) → equality leg red
2. a drifting **pin** (the commons moved instead of the table) → same leg red, so neither side is privileged
3. a table year with no pin → coverage leg red
4. a new year-keyed table classified nowhere → scope leg red
5. an emptied register → loader raises, rather than the equality leg passing vacuously
6. a missing register → loader raises; an unavailable check is a FAILED check

Mutation 2 is the one that matters for tautology: the control is not "trust the commons", it is
"the pair must agree", so a constant cannot be greened by quietly moving its own source.

**NOT claimed:** that the other eleven tables' values are right. This pass source-checked three of
thirteen; the remaining eleven are declared in the control's `_UNVERIFIED_TABLES` with a per-table
reason and ratcheted downward-only, which makes the gap visible and shrinking rather than closed.
The two largest lines by money (electricity network £869k, RO £1.72M) are still unverified. The
published `total_gap_gbp` still carries the old figure — it moves on the next sim run, and that rise
is the repair landing, not a regression (the CCL line was UNDERstated, so the stack grows).

## 2. This is what B5 was actually testing, and B5 passed it

Pass 3 scored the scope brief's **B5** — *"every constant traces to a published artefact — an
untraceable constant is invented physics"* — as **12 of 13**, one table citing no source. That verdict
stands as written. But the verdict answers a weaker question than the brief's own words imply:

* **B5 as run** asked: does a comment above the table NAME a publication?
* **B5 as meant** asks: does the constant TRACE to that publication — i.e. is it the published number?

`_CCL_ELECTRICITY_RATE_BY_YEAR` cites *"HMRC Climate Change Levy rates tables"* and would score a PASS
on the first reading. It is £43k away from those tables. **A citation is not an agreement**, and a
census of citations cannot fail on a mis-transcribed constant — the R15 tautology shape, applied to a
documentary control: the checker reads the same comment the author wrote, so the only defect it can find
is a *missing* comment, never a *false* one. This is the second time on this atom that a green battery
verdict has turned out to measure something narrower than its sentence (pass 3 §2 found the same about
B2, which *"passes because the stack is shape-invariant everywhere, including the two places where
shape-invariance is the wrong answer"*).

**Recommendation, acted on by recording it here rather than asking:** when EP14 opens, B5's exit
criterion reads *"every constant equals the figure in the publication it cites, checked by fetching it"*,
not *"every constant cites a publication"*. That is the criterion an ingest adapter can actually be
built against — and it is nearly free once the adapter exists, which is the point of the adapter.

## 3. B5's one untraceable table is 95.66% of the network line — the count inverts under money

Pass 3 §4 named `_DUOS_IC_BY_YEAR` as the one table of thirteen citing no source, and stated its own
gap honestly: *"Not quantified here: what share of the £869,332.79 electricity network line is I&C DUoS.
Decomposing it needs a re-run attributing by segment, which this pass did not do."*

**It does not need a re-run.** The run's `bills` already carry `segment` and `commodity` per bill, so the
attribution is available from the published artefact by calling the shipped reader per day:

| segment | elec MWh | network £ | share |
|---|---:|---:|---:|
| **I&C (DUoS-only, the untraceable table)** | **65,947.5** | **835,226.01** | **95.66%** |
| SME | 301.8 | 14,793.56 | 1.69% |
| resi | 431.7 | 23,058.29 | 2.64% |
| total | 66,681.0 | 873,077.86 | |

(£873,077.86 against pass 3's £869,332.79 — 0.43% apart, two different runs and an even-day
apportionment. **No before/after claim is made across those two refs**; the mixed-join shape manufactures
the defect it counts.)

So **"12 of 13 tables cite a source" is a COUNT, and it inverts under money weighting**: the single
table that cites nothing carries 95.66% of the electricity network line and £835,226 — **17.3% of the
entire £4.84M non-commodity stack**. A 1-in-13 miss reads as a rounding gap; the same miss weighted by
what it prices is the largest single untraced quantity in the stack. Recorded because the count was the
number in the summary table, and the count is the misleading one.

## 4. The clamp finding's own stated evidence gap is now closed — and the answer is table-specific

Pass 2 filed `WORKER_FINDING_THE_COST_STACK_CLAMPS_SILENTLY_INSIDE_ITS_OWN_RUN_WINDOW_2026-08-14.md` as
**LATENT**, and its own grading paragraph named exactly what it lacked:

> "it does not claim the 2024 rates are the wrong stand-in for 2025, and **it fetched no external source
> that could say**."

Fetched. For the two gas tables whose 2025-26 rates are published:

| table | clamped value (2024) | published 2025-26 | verdict |
|---|---:|---:|---|
| gas CCL | 7.75 £/MWh | **7.75 £/MWh** | clamp is **exactly right** |
| GGL | 0.105 p/meter/day | **0.821 p/meter/day** | clamp is **7.82× low** |

**The clamp is not uniformly wrong or uniformly harmless — it is table-specific**, and the two tables
land on opposite answers. That is the substantive addition: the finding's exposure cannot be reasoned
about in aggregate ("8.09% of the stack is priced on clamped tables") because for gas CCL the clamped
number is the published number, while for GGL it is out by a factor of eight.

Money in *this* run is small and is stated plainly rather than dressed up: the gas book is **five
meters** and the clamped window is **130 meter-days**, so the GGL understatement is **£0.93**. The
defect is in the mechanism, not in this run's P&L — it scales linearly with meter count, so the same
mechanism on a real book of 500k meters is ~£930k/yr. **I am not re-grading another pass's document from
this one**; the numbers are recorded here and the grading stays with its own lane. What can be said is
that its stated reason for LATENT ("no source could say") no longer holds, and whoever draws it next has
the source.

Also confirmed on the primary publisher, and it matters for EP14's premise more than for the arithmetic:
the model's GGL table is **right** where it has rows — `0.122` (2023-24) and `0.105` (2024-25) both match,
and the table's `× 365 / 100` construction reproduces the publication's own annual figures ("45p per
meter", "38p per meter") to the penny.

## 5. EP14's premise, confirmed against reality rather than argued

This atom exists to build **file-ingest adapters tolerant of publication drift**. Its `origin_note`:

> "a published spreadsheet whose columns move between periods is the normal case, not the edge case"

That claim has been carried through three passes as a design assumption. It is now an observation. The
live GOV.UK *Climate Change Levy rates* page — the publication `_GAS_CCL_RATE_BY_YEAR` and
`_CCL_ELECTRICITY_RATE_BY_YEAR` both cite — **today serves only 2023, 2024 and 2025**. Its own change
note records the deletion:

> "The rates from 1 April 2022 have been removed" *(November 2025 update)*

**Seven of the nine rows the model depends on are gone from the page it cites.** Not moved to another
column — removed from the current document, recoverable only from the statutes that set them
(legislation.gov.uk), which is how they were recovered above. So the drift is not hypothetical and it is
not a column shuffle; it is **row deletion on the canonical page, inside the model's own lifetime**.

Two consequences for the build, both concrete:

1. **An adapter pointed at the current page cannot reconstruct the model's own history.** Any EP14
   ingest design that treats "the rates page" as the source of truth for 2016-2022 is already broken.
   The durable source for historical main rates is the Finance Acts, and the adapter needs a
   *time-indexed* source strategy — publisher page for current, statute for historical — not one URL.
2. **This is precisely the failure the `origin_note` demands fail-LOUD behaviour for.** A parser that
   requested 2019 from that page today would get *nothing*, and the reader beneath it would clamp
   silently to the nearest year (§4) and return a number indistinguishable from a published one. The
   fail-loud requirement is a property of the **reader**, not only the parser — which is what pass 2
   concluded from the other direction, now with a live instance behind it.

## 6. What this pass did NOT do

* **No adapter, parser, schema-drift or cap-annex work.** Nothing in `file_scope` touched. No BUILD.
* **The electricity CCL divergence is NOT repaired** — filed and queued (§1), per SELF_INTERRUPT
  discipline. A LANE 3 draw carries no BUILD, and the repair is a class question (which other tables were
  transcribed from a column they share with a correct one?), not a nine-value edit.
* **2016, 2017 and 2021 electricity CCL rates were not fetched** — recalled only, and excluded from the
  £43,074.89 floor. Someone should close those three before the full £49,208.14 is quoted anywhere.
* **The network and RO tables were not source-checked.** RO, CM, FiT, CfD, mutualisation, both standing
  charges, gas network and both network tables are all still unverified against source — **this pass
  checked 3 of 13 tables** (gas CCL, electricity CCL, GGL). The B5-as-agreement census is *started*, not
  done, and the two largest lines by money (electricity network £869k, RO £1.72M) are untouched.
* **B1 still not run** (blocked on this atom's own unbuilt half — pass 3 §6 established this and nothing
  here changes it). **B6 still not run** (`D2_three_clocks` owns it).
* No level moved, no map edit, no note-store edit, nothing under `company/`, `saas/`, `sim/`,
  `simulation/` or `site/` changed.

---

## Sources fetched this pass

* [Climate Change Levy rates — GOV.UK](https://www.gov.uk/guidance/climate-change-levy-rates) — current
  page; 2023/2024/2025 main rates, and the "rates from 1 April 2022 have been removed" change note.
* [Finance Act 2016 s.147 — legislation.gov.uk](https://www.legislation.gov.uk/ukpga/2016/24/section/147/data.html)
  — CCL main rates from 1 April 2019: electricity £0.00847/kWh, gas £0.00339/kWh.
* [Finance Act 2020 s.92 — legislation.gov.uk](https://www.legislation.gov.uk/ukpga/2020/14/section/92/data.html)
  — from 1 April 2020: electricity £0.00811/kWh, gas £0.00406/kWh.
* [Finance Act 2021 Pt.3, environmental taxes — legislation.gov.uk](https://www.legislation.gov.uk/ukpga/2021/26/part/3/crossheading/environmental-taxes/enacted)
  — from 1 April 2022 and 1 April 2023.
* [GGL rates 2024-2025 — GOV.UK](https://www.gov.uk/government/publications/green-gas-levy-ggl-rates-and-exemptions/green-gas-levy-ggl-rates-underlying-variables-mutualisation-threshold-and-de-minimis-for-the-2024-2025-financial-year)
  — 0.105p per meter per day, 38p per meter per year.
* [GGL rates 2025-2026 — GOV.UK](https://www.gov.uk/government/publications/green-gas-levy-ggl-rates-and-exemptions/green-gas-levy-ggl-rates-underlying-variables-mutualisation-threshold-and-de-minimis-for-the-2025-2026-financial-year)
  — 0.821p per meter per day, £3.00 per meter per year.
