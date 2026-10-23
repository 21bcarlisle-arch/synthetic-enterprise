**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# Explore's cast finds standard-variable bills above the cap, and no mover or two-rate home to show

Raised by the cast rules in `tools/generate_explore_cast.py`, built for the director's 23 Oct
steer (`docs/staging/advisor/done/DIRECTOR_STEER_EXPLORE_IS_A_LIVE_FEATURE_DEMO_THAT_PROVES_THE_FEATURES_WORK_2026-10-23.md`).
His 09:30 point was that each cast rule is also a check that its feature works. On the published
run of 19 Oct (`8b6fea024`, 550 households), three of those checks say a feature does not work.

## 1. Bills on the standard variable tariff above the binding ceiling

**What was measured.** The population is every resi invoice dated before the household's first
renewal on that fuel. Before that renewal, the tariff can only have been standard variable. The
run does not record term length, so this is the one population that is certainly capped. It
undercounts, which is the safe direction. Each invoice's all-in unit rate is (commodity + non-
commodity) × (1 + its own VAT rate) ÷ kWh. Standing charge is excluded and catch-up bills are
skipped. That rate is compared with the household-facing ceiling for the period: min(Ofgem cap,
EPG), from `docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`.

**Result.** 4,764 of 14,012 graded invoices are more than 0.5% above the ceiling, covering 199 of
550 households. 1,791 are above it **on the commodity line alone**. Every capped year is affected:
2019 448, 2020 306, 2021 497, 2022 1,075, 2023 1,557, 2024 685, 2025 196 (invoices). The worst is
January 2023 electricity at 77.6p/kWh against an EPG of 34.0p and an Ofgem level of 67.5p.

**This is not the 1 Oct finding re-found.** `SEAT_FINDING_AN_SVT_SEGMENT_WAS_BILLED_ABOVE_THE_CAP_BY_THE_RENEWAL_CHAIN`
was closed by `592596b44`, and that commit IS an ancestor of the run's `8b6fea024`.

**The mock-up's case, answered.** SYN-2016-306's November 2022 bills come to 51.89p/kWh
electricity and 14.76p/kWh gas, all-in including VAT. Those are **exactly the Ofgem cap levels for
Oct–Dec 2022** (518.9 and 147.6 £/MWh), not the EPG rates the household should have paid (34.0p
and 10.32p). The bill charges the household the cap, and the Treasury's half of the EPG never
reaches it. (That bill falls after the household's 2019 renewal, so it is outside the population
counted above. It shows the EPG leg on its own.)

**I cannot yet say which cause it is.** The explanations the evidence allows, ranked:
(a) non-commodity cost is billed on top of a unit rate that is itself capped, which can only be true
of the 2,973 invoices whose commodity line is under the ceiling; (b) the EPG is not applied to the
household's bill, which fits the 306 case exactly; (c) "before the first renewal" is not the same
as "on standard variable", for example if acquisition was itself onto a fix. That would make the
check wrong, not the bill, and it is the first thing to rule out. (d) A regional cap above the GB
average explains a few percent at most and cannot explain 2×. The one-variable test is to re-grade
the same invoices against the tariff type the run records on the segment, not the timeline.

**Re-graded 23 Oct (correction beside the claim):** (c) is refuted. On the run's recorded
`tariff_type`, 4,579 of the 4,764 are `svt` invoices. The causes are A, an incoming occupant priced
as non-domestic (3,600 invoices, fixed), and B, the EPG not passed to the household (1,817, next):
`SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_NOT_A_GRADING_ARTEFACT_2026-10-23.md`.

## 2. The insulation that never reached the bills (mock-up check 2)

SYN-2016-306's timeline says gas use moved −24% from February 2022. On billed gas, which actual
reads correct through catch-ups (Dec 2022, Apr 2023, Aug 2023, Mar 2024 are all `A` with
`catchup_applied`), the household used 24,506 kWh in 2021 and 22,542 kWh in 2023: **−8%**.
Electricity fell about 18% on the same basis. So the estimate does not ignore actual reads; the
catch-ups land. What did not reach the meter is most of the stated −24%. One untested explanation:
the effect line averages the months before the event against the months after it, and for an event
dated in February that is winter against spring. I have not checked that; it is the next thing to test.

## 3. A debt that was never chased (mock-up check 3)

The £93.68 bill of 30 Apr 2019 drew a first notice (22 May 2019) and a second notice offering a
payment plan (5 Jun 2019). After that there was nothing for five years. £68.50 of it was written
off on 19 Jul 2024, 13 days after the household left on 6 Jul 2024, and placed with an agency on
18 Aug 2024. The gas leg is the same shape: notices in June–July 2018, then write-off of £16.85 on
the same day. The collections ladder has no step after the second notice, and the write-off fires
only on leaving. That is the shape `done/SEAT_FINDING_A_FAILED_BILL_IS_WRITTEN_OFF_IN_FULL_IFF_THE_CUSTOMER_EVER_LEAVES_2026-09-27.md`
recorded, and it still holds on the 19 Oct run. The gas timeline's `"commodity": "electricity"`
on its renewals (at an electricity £/MWh rate) is confirmed on `SYN-2016-306g`.

## 4. Slots no household can fill

- **The mover.** The published per-household record has no move-out event and no final-bill
  marker. The 181 `OCC-` accounts are not linked to the household they replaced. Until the 22 Oct
  mover fix emits those links, the slot says so on the page.
- **Storage heating.** Every one of the run's 38,554 invoices carries one `Anytime` register. There
  is no profile-class-2 home to show. The rule is proven able to fire on a two-register bill
  (`test_the_storage_rule_fires_on_a_two_register_bill`), so the slot is empty because of the run,
  not because the rule is blind.

## Also seen, not yet graded

The EV slot's best household is PROS-2021-0219, and its electric car moved its use by **+8%** (99 →
108 kWh/month). A real EV adds far more than 9 kWh a month. This is filed for the EV lane as a
fidelity question, not a breach: no published rule says how much an EV must add.

## Handed on

- Wire the cast's coverage checks into Monday's end-to-end step (`background/weekly_rhythm.py`), so
  a feature that stops working reds the build before a reader sees it (steer item 4, third bullet).
- Render the customer view from `company/portal/templates/` (steer, view 1). Today the page draws
  it from the same invoices and ledger, and says "simulated household". It does not claim to be
  the supplier's own portal.
- The cold-reader pass the steer asks for (one energy reader, one tech reader).
