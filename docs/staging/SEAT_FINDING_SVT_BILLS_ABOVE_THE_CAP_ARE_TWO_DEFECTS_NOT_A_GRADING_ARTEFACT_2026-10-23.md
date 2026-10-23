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
