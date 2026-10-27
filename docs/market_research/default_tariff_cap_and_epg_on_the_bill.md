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

**Payment method (added 27 Oct 2026).** The cap is set per payment method as well as per fuel and
region. `docs/domain_artefact_library/regulatory/pricing_differentiation_permissions.md`: "Ofgem sets
different cap levels for Direct Debit, standard credit and prepayment (S4)". A prepayment household
on a default tariff is bounded by the **prepayment** level, not the direct-debit one. The published
typical-household row in `ofgem_default_tariff_cap_windows.json` is the direct-debit column. All three
columns, unit rate and standing charge, per fuel and window, are in
`docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json` (`by_payment_method`,
`gas_by_payment_method`; ex-VAT, GB median of the model's 15 rows). Read off that file:

| 2019-01 to 2026-12 | electricity | gas |
|---|---|---|
| prepayment unit rate / DD unit rate | 0.965–0.992 in every window | 0.957–0.999, except Oct 2022 – Jun 2023, when it is 1.018–1.028 |
| prepayment standing charge / DD standing charge | 1.095–1.200 | 1.156–1.388 |
| standard credit / DD, both parts | at least 1.053 | at least 1.052 |

**How prepayment came into the default cap, and levelisation.** Confirmed at primary in
`docs/market_research/tariffs_and_the_default_tariff_2026-10-25.md` (V4). The CMA's prepayment
charge restriction expired at the end of 2020, and prepayment was then folded into the default tariff
cap (£1,156 PPM against £1,138 DD from 1 Apr 2021). Levelisation started on 1 Apr 2024: about £49 a
year off prepayment and £10 onto direct debit (Ofgem decision 23 Feb 2024; phase 2 paused Aug 2024).
The published levels for Apr–Jun 2024 were £1,690 DD, £1,796 standard credit and £1,643 PPM
(`docs/market_research/payments_and_direct_debit_2026-10-25.md`).

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

**The floor under a default rate.** The cap bounds a default rate from above only. What it lets a
supplier pass through per unit is published in the same cap level model. It is commodity (DF, CM),
network (NC) and policy (PC), each per region, payment method and window, for single-rate
electricity and for gas. The unit-rate part is benchmark minus nil over the benchmark kWh, which is
Ofgem's own construction. Gas uses 12,000 kWh before 2026, 11,500 for Jan–Jun 2026 and 9,500 from
July 2026, as the model's `1c` table states. Over 2019–2026 the cap's direct-debit unit rate sits
1.11–1.26x above the lowest region's DF+CM+NC+PC for electricity, and 1.08–1.23x for gas. The
narrowest margin is the crisis winter. Read off
`docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json`
(`pass_through_p_per_kwh_ex_vat_min`). The derived gas unit rate reproduces Ofgem's published gas
levels within 0.6% over 21 windows.

- **GAP: the prepayment cap before 2021.** From April 2017 to December 2020 a prepayment household
  was bounded by the CMA's prepayment charge restriction, not by SLC 28AD. The commons does not hold
  its levels. The model's prepayment column for 2019–2020 is the only figure here, and the build
  reads it from 2019. That can only lower a prepayment rate. Nothing is applied for 2017–2018.
- **GAP: where levelisation sits in the model's columns.** The commons says levelisation equalised
  the prepayment and DD standing charge (`pricing_differentiation_permissions.md`, D4). But the
  model's ex-VAT prepayment standing-charge column is still 10–20% above DD for electricity, and
  16–35% for gas, from April 2024. Either
  the columns leave out the levelisation allowance, or the commons' one-line summary is loose. Not
  resolved. The build does not depend on it, because it charges every method the DD standing charge
  and DD is the lower column in every window.
- **GAP: a move onto prepayment for debt.** The company's method register
  (`SimInterface.get_payment_method`) answers with the method the account was set up on, or pay on
  receipt after a stopped DD. It does not see a meter moved to prepayment for debt
  (`simulation/payment_method_dynamics.move_to_prepayment_for_debt`), so after such a move the
  default tariff would stay at the DD level. That route ships at 0 on the default book.
- **GAP: a multi-register floor.** A per-register rate against the blended benchmark floor is not a
  quantity: an off-peak rate is lawfully under it.

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
5. **The EPG on the household's bill (built 24 Oct 2026).** A domestic `svt` term's settled rows
   inside the EPG carry `hmt_epg_receipt_gbp`, kWh × (cap − min(cap, EPG)) ex-VAT, from the same
   accessor as the SVT segment's split (`simulation.svt_product.stamp_hmt_epg_receipt`).
   `saas.bill_generator` carves it out of the household's line, as it carves the levy line, and VAT
   falls on the household's subtotal. `saas.ledger` books it as an `epg_receipt_event`, revenue and
   cash, so the supplier still books the cap (row 1 of the table). Pre-registration:
   `docs/staging/records/SEAT_PREREGISTRATION_THE_EPG_REACHES_THE_HOUSEHOLD_BILL_2026-10-24.md`.
   **Choices this rests on, each a GAP above or here:** the receipt is the full cap − EPG per kWh
   whatever the supplier's own SVT rate (the scheme text is not in the commons); **GAP: the VAT
   treatment of the Treasury payment**, taken here as outside the household's supply; **GAP: the
   scheme's payment timing**, booked at the bill's period start. An estimate on a void row (0 kWh,
   so a 0.0 receipt) takes the row's per-MWh receipt, `hmt_epg_receipt_gbp_per_mwh`, because the
   discount is per unit billed. Without it, 9 such estimates on the `88cdf35e48` run charged the
   household the Treasury's share.

6. **A default tariff is priced at its payment method's column (built 27 Oct 2026).** The world's SVT
   schedule is built before any method register can be asked, so it prices at the published DD level.
   The run loop asks the company's own register for the method on each segment's first day. It then
   re-prices the segment at min(the method's own column, the published DD level), reading the
   column directly (`simulation.price_cap_enforcement.payment_method_cap_factor`,
   `simulation.svt_product.price_segment_for_payment_method`). The EPG still bounds what the
   household pays, so on prepayment the Treasury's receipt is the prepayment cap less the EPG.
   **Why min() and not the method's column alone.** Where the method's column is higher (standard
   credit, and prepayment gas in Oct 2022 – Jun 2023), charging up to it is lawful. But it is the
   supplier's pricing choice, and taking it would raise our own revenue on a reading nobody has made,
   so the DD level stands there. **Why read the column, not scale by a ratio.** A ratio to the
   model's DD row carries the model's disagreement with the published level, up to 1.34%. That left
   the Oct 2020 prepayment rate 1.36% over its own column. **Standing charge:** unchanged. Every
   method pays the DD standing charge, which is below the prepayment and standard-credit columns in
   every window. On the 67a893e749 book, re-priced through the new reader, `INV_UNIT_RATE_SVT_ELEC`
   goes 496 → 0 and `INV_UNIT_RATE_SVT_GAS` goes 462 → 0.

7. **The company's own cap clamp reads the payment method too (built 27 Oct 2026).** Choice 6 priced
   the segment the world hands the company, but the company's renewal rate chain then moves an SVT
   rate. Its portfolio premium and margin surcharge (writers 1 and 2,
   `company.pricing.renewal_rate_chain`) are the supplier's own pricing, and they are lawful while the
   rate stays under the cap. Writer 4 is the clamp that keeps it there. It read the published level,
   which is the DD column, whatever the household's method. On the `871f674a2` book, every one of the
   298 electricity and 249 gas SVT term-windows over their cap is a prepayment segment priced at its
   own column and then raised by writer 1 or 2. 270 electricity and 162 gas were clamped back to the
   DD level, and 28 and 87 were raised to a rate between the two columns. SYN-2016-061, Jan 2023:
   it entered at 631.48 GBP/MWh (the prepayment column), the premium took it to 726.20, and the
   clamp stopped at 642.57 (the published DD level). It was **not** a rate struck once and never
   re-struck: every segment is re-struck at its window, and the grade's "13 windows" are 13
   re-struck segments that were each raised. So the company's ceiling for a domestic default tariff
   is now min(the published level, the method's own column). This is the company's own reading of
   the composition artefact (`company.pricing.ofgem_price_cap.get_payment_method_cap_unit_rate_ex_vat`),
   the same min() as choice 6 and for the same reason. With no method known, the clamp stays at the
   published level. That fails open toward the DD level, and it is said here rather than hidden:
   the run loop hands the chain the method the segment was priced on, so a spliced default segment,
   which resolves no renewal method, still carries one. **Fixed terms are untouched.** The
   acquisition rule's ceiling is the company's choice, not SLC 28AD's.
   **The standing-charge "residue" was not a charge.** The same grade read 735 electricity and 1,502 gas
   SVT standing-charge periods as over the cap, and about half of them as a neighbouring window's
   charge. Every one is a period billed at exactly the cap per day: the bill rounds days × rate to the
   penny, then prints the shortest per-day rate that reproduces that rounded charge
   (`saas.money.display_rate_gbp_per_day`). Over a short period the printed rate can sit up to
   1p ÷ days above the rate charged. The invariants' 0.0001 GBP/day tolerance was tighter than the
   penny rounding its own reason names. The neighbouring-window match was a coincidence of rounded
   figures: no breaching period straddles a cap change. The invariants now also allow a penny over the
   period, and anything larger still breaches.
