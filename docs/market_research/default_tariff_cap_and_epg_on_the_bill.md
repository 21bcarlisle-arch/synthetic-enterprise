**Knowledge:** price-cap

# How the cap and the Energy Price Guarantee bind a default-tariff bill

K8 page for the billing fix in
`docs/staging/SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_NOT_A_GRADING_ARTEFACT_2026-10-23.md`.
Written 23 Oct 2026. It says what the rules require of the unit rate a household on a default tariff
is charged, what the commons holds, what is not established (GAP), and which choices the build makes.

## What the rules require

**The cap (SLC 28AD).** Quoted in `docs/domain_artefact_library/regulatory/slc_28ad_multi_register_cap_test.md`:
28AD.2 says that for each tariff, the "aggregate Charges for Supply Activities applicable to any
Relevant 28AD Customer at any consumption level (x kWh) ... do not exceed the Relevant Maximum
Charge". The customers it covers are those on a default tariff: the evergreen standard variable
tariff, a deemed contract, and a default fixed term. A fixed term the household chose is outside it.
The charge is all-in. Ofgem builds the cap from wholesale, network, policy, operating cost and
margin allowances (the price-cap knowledge page), so its unit rate already contains every
non-commodity cost. A supplier may not add network or levy charges on top of it.

**Two parts, both capped.** The maximum charge has a nil-consumption part (the standing charge) and
a per-kWh part. The commons row is the per-kWh part only:
`docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`, `basis.standing_charge`:
"EXCLUDED - this is a unit-rate ceiling only".

**VAT.** The published levels include VAT. Domestic fuel is reduced-rated at 5% (VATA 1994 Sch 7A
Group 1). Electricity is zero-rated from 2026-10-01 to 2027-03-31, so that row is inclusive of 0%
(the artefact's `basis.vat`). A bill is graded inc-VAT against an inc-VAT ceiling, at the invoice's
own VAT rate. Dividing every row by 1.05 is wrong for the 2026-10 electricity row.

**The Energy Price Guarantee, 1 Oct 2022 – 30 Jun 2023.** The commons publishes the EPG unit rates
separately from the cap (`elec_epg` 340.0, `gas_epg` 103.2 £/MWh inc-VAT, three windows). Its
`epg_note`: the EPG "held a typical dual-fuel bill at GBP 2,500, well below the Ofgem cap". The
household paid the EPG rate, and HM Treasury paid the supplier the gap up to the supplier's tariff
(`company/regulatory/epg_reconciliation_register.py`: "Suppliers applied the EPG rates to all
bills"; "HM Treasury paid suppliers the difference"). So on a default tariff:

| quantity | ceiling | who pays |
|---|---|---|
| what the supplier receives per kWh | the Ofgem cap level | household + Treasury |
| what the household is charged per kWh | min(Ofgem cap, EPG) | household |
| the Treasury receipt per kWh | cap − min(cap, EPG) | Treasury |

The first row is `SOLD_UNIT_RATE_WITHIN_CAP_EX_VAT`. The second is the new
`DEFAULT_TARIFF_INVOICE_WITHIN_HOUSEHOLD_CEILING`. Both are in `company/compliance/domain_invariants.py`.
A bill that charges the household the cap during the EPG passes the first and fails the second: it
bills the household the Treasury's half.

**Regional level.** The cap is set per region (14 GB regions), not as one national number.

## GAPs

- **GAP: regional cap levels.** The commons holds GB-average typical-household unit rates only.
  This world bills every household at the GB average, so a GB-average ceiling does not false-fire
  here. A world with regional pricing needs Ofgem's per-region cap tables first.
- **GAP: the EPG scheme's own text.** The Energy Prices Act 2022 and the EPG scheme rules are not in
  the commons. The table above rests on the commons' `epg_note` and the company register's summary,
  not on the scheme text.
- **GAP: the EPG standing charges.** The company register carries 46p and 28p a day, cited to BEIS,
  but the commons has no EPG standing-charge row. The invariant grades the unit rate only.
- **GAP: the EPG on fixed terms.** The EPG reached every domestic tariff, fixed terms included.
  `simulation/price_cap_enforcement.hmt_epg_receipt_gbp_per_mwh` names this gap world-side: the
  world applies it to default-tariff rates only.

## Choices the build makes, and why

1. **The invariant grades the household's invoice against min(cap, EPG)**, all-in inc its own VAT,
   with standing charge excluded. That is the commons row's own basis, so no conversion is needed.
2. **Tolerance 0.5%.** It absorbs the published rows' rounding to 0.1 £/MWh and the invoice's
   rounding to the penny, and nothing else.
3. **A catch-up invoice is not graded** (it returns None, never a pass). Its charge spans earlier
   periods under earlier ceilings.
4. **An incoming occupant on a domestic premise is domestic.** The world's renewal loop held a set of
   domestic account ids frozen at import, so a change-of-tenancy account admitted mid-run was priced
   as non-domestic and its default tariff was never clamped. Fixed as an error, not behind a switch.
5. **Not yet built: the EPG on the household's bill.** The world already splits every SVT segment
   into `household_charged_unit_rate_gbp_per_mwh` + `hmt_epg_receipt_gbp_per_mwh`
   (`simulation/svt_product.py`), but settlement bills the household the revenue rate. The fix bills
   the household's charge and books the receipt as a Treasury receivable. It moves the
   bill-derived ledger, debt and direct-debit figures, so it is the next increment with its own
   pre-registration (see the finding).
