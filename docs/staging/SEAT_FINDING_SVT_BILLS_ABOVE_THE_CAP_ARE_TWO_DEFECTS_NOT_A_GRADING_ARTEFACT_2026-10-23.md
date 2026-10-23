**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** `price-cap` -- `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`

# Standard-variable bills above the cap are two billing defects, not a grading artefact

Follows section 1 of `SEAT_FINDING_EXPLORES_CAST_FINDS_STANDARD_VARIABLE_BILLS_ABOVE_THE_CAP_AND_NO_MOVER_OR_TWO_RATE_HOME_2026-10-23.md`
(4,764 of 14,012 graded invoices above min(cap, EPG), 199 of 550 households, run `8b6fea024`). Its
causes were ranked (a)-(d) and run in this order: (c), then (b), then (a). The pre-registration is the last section, filed before the re-grade ran.

**Billing is defined here** as what the household is charged per kWh on its invoice: (commodity +
non-commodity) × (1 + the invoice's own VAT) ÷ kWh, with standing charge excluded and catch-ups
skipped. The ceiling is min(Ofgem cap, EPG) for the invoice's period, GB average. That is not the
same as what the supplier receives; see the knowledge page's three-row table.

**Atom.** Bound to D48, the map's billing-accuracy atom (lane D, epoch 4), not minted. D48's title is
billed kWh against used kWh; this is the price leg of the same question, whether the household
was billed what it owed. The cap's own atom, `W3_1b_intra_year_price_cap_granularity`, owns the
clamp the A fix passes through.

## (c) refuted: it is not the check

Re-graded against the tariff type the run records per term (`account_state_log.tariff_type`),
not "before the first renewal": **4,579 of the 4,764 are on `svt` terms; 185 are on fixed terms.**
The prediction was that at least 70% would fall away. It was wrong: 3.9% fell away. Over every
invoice with a recorded type, **5,492 of 18,374 `svt` invoices are above the ceiling, across 244 of
550 households.** By year: 2019 431, 2020 306, 2021 497, 2022 1,397, 2023 2,078, 2024 590,
2025 193. 360 of 5,160 fixed-term invoices are also above it, which is lawful for a fix.

## The 5,492, split by cause

| cause | invoices | where |
|---|---|---|
| **A. An incoming occupant priced as non-domestic.** The term's own struck rate is above its window's cap ex-VAT. | 3,600 | every one an `OCC-` account at term ≥ 1 |
| **B. The EPG not passed to the household.** The bill is at or under the Ofgem level, and above the EPG. | 1,817 | Oct 2022 – Jun 2023 |
| rate at the cap ex-VAT, bill above it | 66 | not yet explained |
| at the ceiling within rounding | 9 | the 0.5% edge |

**A, measured on terms rather than bills:** 1,388 of 1,866 `OCC-` `svt` terms at index ≥ 1 sit
above their own window's cap, median ×1.15, max ×1.38. **None of the 6,187 SYN/PROS `svt` terms
does, and none of the 128 OCC first terms does.** Cause: `simulation/run_phase2b._RESI_CUSTOMER_IDS`
is a frozenset built at import from `CUSTOMERS`. A change-of-tenancy account is admitted mid-run
(`_admit_incoming_occupant`), so it was never in it, and the renewal chain was told
`is_domestic=False`. Writer 4, the cap clamp, then skips it, and writers 1-3 (the premium, the
surcharge, the uplift) move its default-tariff rate above the cap. A first term is struck at the cap
and no writer moves it, which is why term 0 is clean. **Fixed in this landing as an error fix:**
an admitted leg whose premise was resi is domestic (`_is_domestic_leg`).

**B:** `company/pricing/renewal_rate_chain.EPG_MADE_WHOLE_TARIFF_TYPES` holds an SVT strike at the
Ofgem level, because that is what the supplier receives. That part is right. The world splits every
SVT segment into `household_charged_unit_rate_gbp_per_mwh` + `hmt_epg_receipt_gbp_per_mwh`
(`simulation/svt_product.py`). But settlement bills `unit_rate_gbp_per_mwh`, the revenue rate, so
the household's invoice carries the Treasury's half. SYN-2016-306's November 2022 bill at exactly
51.89p is this shape. **Not fixed in this landing:** see "Next" below.

**(a), the levy line stacked on a capped rate,** was already fixed by `1d3c289307` (10 Oct), an
ancestor of `8b6fea024`. 4,981 of the 5,492 reproduce their term's struck rate × VAT within 1%,
so nothing is stacked on those. 436 in A and B (314 and 122), plus the 66 below, do not. I cannot
yet say why; that is item 3. **(d), regional cap,** does not apply: this
world bills at GB-average levels.

## What landed

- The A fix, `simulation/run_phase2b.py`.
- `DEFAULT_TARIFF_INVOICE_WITHIN_HOUSEHOLD_CEILING` and `default_tariff_invoice_excess_p_per_kwh`,
  `company/compliance/domain_invariants.py`. The control
  `tests/company/compliance/test_default_tariff_invoice_within_household_ceiling.py::test_the_partition`
  asserts both verdicts are reachable: a planted over-cap SVT bill fails, an SVT bill at the
  Ofgem level during the EPG fails, an SVT bill within the ceiling passes, and a fixed bill priced
  above the cap passes. Three mutations each red it (in the file's docstring).
- The Explore cast's `above_cap` rule now calls that invariant. One implementation of one legal
  rule. Recomputed on the published data: still 199 of 550 households, so the cast's own figure is
  unchanged.
- K8: `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`.

## Prediction for the next fresh run, filed before it exists

On the recorded tariff type, `svt` invoices above the ceiling fall from 5,492 to **between 2,000
and 3,000**. The 2,980 cause-A invoices outside EPG windows clear. The 620 inside them stay above
the ceiling, now on cause B. **Outside the EPG windows, at most 200 remain** (from 3,055). The fix
changes OCC renewal prices, so OCC churn and the invoice count may move. The denominator is
reported with the count. If more than 200 survive outside the EPG windows, A was not the whole
story.

## Next, ranked

1. **B, the EPG on the household's bill.** Bill the household `household_charged`, and book
   `hmt_epg_receipt` as a Treasury receivable, not a household charge. It moves the bill-derived
   ledger, debt, DD and bad-debt figures in the crisis quarters, so it needs its own
   pre-registration. The company's `company/regulatory/epg_reconciliation_register.py` is the
   existing home for the receivable. Expected: about 2,430 invoices clear.
2. The re-grade of the fresh run, against the prediction above, using `account_state_log`.
3. The 502 bills that do not reproduce their term's struck rate (436 in A and B, 66 struck at the cap).
4. The cast's section 3, collections after the second notice, is its own item.

**Advisor channel, seen on the way:** the shared tree's root copy of
`docs/staging/advisor/DIRECTOR_STEER_THE_OTHER_PAGES_MATCH_THE_FRONT_DOOR_2026-10-23.md` is an older,
unsigned copy of a steer that is already in `advisor/done/` on origin, closed with its `## Done`
section. Moving the root copy into `done/` would overwrite that closure, so the right action is to
delete the stale root copy, not move it. It is untracked on the shared tree, which this isolated
worktree does not touch.

## Pre-registration, written before the re-grade and not edited since: the 4,764 "above the cap" bills, re-graded on the tariff the run records

Written 23 Oct 2026, before the re-grade was run. Subject: section 1 of
`SEAT_FINDING_EXPLORES_CAST_FINDS_STANDARD_VARIABLE_BILLS_ABOVE_THE_CAP_AND_NO_MOVER_OR_TWO_RATE_HOME_2026-10-23.md`.

**What the run records.** `run_output_8b6fea024_20261019T033010Z.json` → `account_state_log`: one row
per account per term, `tariff_type` ∈ {fixed, svt}, with `term_start`/`term_end` (10,831 svt rows,
1,089 fixed). The cast graded by "before the first renewal" instead. Account C1's term 0 is
`fixed`, so acquisition can be onto a fix, which is cause (c).

**Already known before measuring.** Cause (a), the levy line stacked on an all-in rate, was fixed in
`1d3c289307` (10 Oct), an ancestor of the run. The world's deemed/SVT path clamps at
min(cap, EPG) ex-VAT (`simulation/hedged_settlement.run_deemed_term`).

**Prediction.** At least 70% of the 4,764 fall away because they are fixed-term invoices; the
svt-tagged invoices above min(cap, EPG) by more than 0.5% are under 20% of 4,764 (< 953). If the
remnant is larger, (c) is not the main cause and (b) is next.

## Result (added after the run; the prediction above is unedited)

**Refuted.** 4,579 of the 4,764 are on `svt` terms; only 185 (3.9%) fall away. The svt-tagged
remnant is 4,579 of the population (96%), not under 953. (c) is not the cause; the causes are above.
**A belief above was also wrong:** `svt` terms are not settled by `run_deemed_term`. They are settled
by `run_hedged_term` at the renewal chain's rate, so the world's deemed clamp never reached them.

## Item 3, the 502 bills that do not reproduce their term's struck rate: prediction, filed before the read

Written 23 Oct 2026, before any of the 502 was looked at one by one. The read compares each over-ceiling
`svt` invoice's (commodity + non-commodity) × (1 + its own VAT) ÷ kWh with its `account_state_log`
term's `unit_rate_gbp_per_mwh` × (1 + VAT), as the earlier split did.

**The 66 struck at the cap ex-VAT and billed above it.** Predicted cause: the term's rate was struck
at the cap of the window it started in, and the invoice falls in a LATER window whose cap is lower.
The default rate was not moved down when the cap fell. Predicted: at least 50 of the 66 have an
invoice window different from the term-start window, with a lower ceiling.

**The 436 in A and B (314 and 122).** Predicted cause: the invoice does not carry one rate. Either a
term boundary falls inside the invoice period, so the bill blends two terms, or the world re-prices the
SVT segment inside a term (`simulation/svt_product.py` segments by cap window) and the state log
records only the term's first rate. Predicted: at least 60% of the 436 have a term boundary or a cap
window change inside, or before, the invoice period within the same term. If fewer, the bill carries
something the term's rate does not, such as a levy or adder line, and that is a billing defect.

## Item 3, result (added after the read; the prediction above is unedited)

**Both predictions refuted.** Re-read on the published books of `8b6fea024` (`site/data/customers/`,
the cast's own source) with the class invariant: the same 5,492 of 26,496 `svt` invoices over the ceiling, in 244
households. (26,496 counts every invoice inside a recorded `svt` term. The 18,374 above was a
narrower base. The numerator agrees.) **501** do not reproduce their term's rate within 1%: 310 in A,
132 in B, and 59 struck at the cap. That is not 436 and 66, because the 1% edge falls differently on rounded invoices.

- **The cap did not fall under any of the 59.** Each sits in its term's own window, which has the
  same cap as its start. The 50-of-66 prediction got none.
- **No term boundary lies inside 492 of the 501**, and the state log's SVT terms are already cap
  quarters (`svt_product.py`). The 60% prediction got 9 (2%).

**The cause is a ToU pair on the default tariff.** All 501 are electricity; gas reproduces every time.
Within one term, the bill's unit rate moves month to month around the struck rate (OCC-104d24fa71c2,
struck 174.0: Aug 171.8, Sep 176.6), and the term's total lands back on it. That is a peak/off-peak
pair priced "revenue-neutral at 30/70", read at each month's own peak share. `run_phase2b` asks
`request_tou_offer` on every electricity term, and `tou_desk.offers_tou` is
`saas.smart_meter_rollout.is_tou_eligible`, which reads the meter only (`smart_meter` or HH). So
**every term of a smart-metered home is settled as ToU, the default tariff included**, and the renewal
chain grades it against the multi-register cap through the same predicate. The run does not export
the flag, so the partition is by its footprint. A smart meter sends actual reads:

| resi electricity accounts | terms | median of each account's median |bill rate / struck − 1| | accounts > 1% |
|---|---|---|---|
| actual reads ≥ estimates | svt | 1.44% | 91% of 47 |
| actual reads ≥ estimates | fixed | 1.67% | 95% of 59 |
| mostly estimated | svt | 0.01% | 2% of 346 |
| mostly estimated | fixed | 0.02% | 3% of 277 |

**476 of the 501 are on the 127 actual-read accounts** (304 A, 116 B, 56 at the cap). The other 25 are
estimates on 7 accounts, at 0.97–1.01 of the struck rate. That fits an estimate scaled from ToU-priced
records (`_estimated_settlement_records` keeps the month's rate), but it is not verified. **GAP:** the run does not
export `smart_meter`.

**What it means for the cap.** For A and B, the ToU pair moves how far over the bill sits, not
whether: the term's rate is already over. For the 59 at the cap, the pair alone puts a month's bill
over. SLC 28AD.4 grades a Multi-Register Tariff at its Assumed Consumption Split, not bill by bill
(`docs/domain_artefact_library/regulatory/slc_28ad_multi_register_cap_test.md`). Struck at the cap,
the pair is at the cap at its split, so **these 59 are not a cap breach. They are the invariant grading
a multi-register bill per invoice, which the cap does not do.** No billing fix lands for item 3, and the
partition control is unchanged.

**What it does expose, ranked as items 5 and 6 below, not fixed here:**

5. **Who is on ToU, and why.** A household rolled onto the default tariff with a smart meter is
   billed two rates it never chose. Whether a supplier can do that is a K8 question for the
   knowledge layer. The candidates are the SLC 47 consent rules on half-hourly data and the
   definition of a Multi-Register Tariff as a contractual arrangement. It also decides which cap the
   renewal chain grades against. Before that is settled, the household-ceiling invariant cannot
   tell a ToU invoice from a single-rate one.
6. **The invoice shows one register for a two-rate charge.** Every one of the 501 carries a
   single `Anytime` register at the blended rate. A ToU bill that does not show its rates cannot be
   checked by the household. Where an invoice carries its registers, the invariant can grade a ToU
   bill at its split and stop misgrading it.

## Earlier flat-against-per-customer readings, and the books they ran on

Cause A entered with `8359d5acd4` (6 Oct): an incoming occupant was supplied on the default tariff,
under the frozen domestic set. Cause B entered with `592596b44f` (2 Oct): the SVT strike was held at
the Ofgem level through the EPG. Both stand until `4bc21e920` (23 Oct; A fixed) and the EPG landing (B).
**So every run produced from 6 Oct to 23 Oct ran on a book with both, and every run from 2 Oct
carries B.** That covers each flat-against-per-customer reading in that window:

- the B11 per-customer-against-flat draws (prereg 16 Oct);
- the renewal-churn belief's section 14 seeds 1-5 and the four-seed grade (19-23 Oct);
- the shortfall-shared seeds (20-22 Oct);
- the per-customer switches together against flat (prereg 21 Oct).

Each arm pair shares its world, so both arms carried the over-cap bills. **The difference between
arms is affected only where an arm changes who is an incoming occupant on the default tariff, or who
is on SVT through the EPG quarters.** Departure and default-roll arms do exactly that. Their GBP
differences are not trusted until the fresh run is graded. Their signs are not called wrong either.

## Status, 23 Oct, late evening

- Item 3: explained above (ToU pair on the default tariff), with 25 labelled GAP.
- Item 1, the EPG: held by the seat executor (pid 1378640, `epg-reaches-the-household-bill`,
  restarted 21:52 after its first attempt ran out of time at 20:22). Nothing of it is on origin, so
  **the fresh run is not launched.** The draw's premise, "pid 1127827 is landing it", was spent: that
  pid exited with nothing landed.
- Item 2, the fresh run and its re-grade: waits on item 1. The grade is
  `python3 -m tools.grade_svt_invoices_over_ceiling <run_output>`. It applies the class invariant to every
  bill inside a recorded default-tariff term, reads the run output alone, and prints its denominator.
  **Its baseline on `8b6fea024`:** 5,488 of 18,398 gradeable default-tariff bills, 244 households,
  3,051 outside the EPG windows. That is within 0.1% of the 5,492 / 18,374 / 3,055 above, which were
  counted on rounded invoices. The prediction above is compared against this tool's figures.
