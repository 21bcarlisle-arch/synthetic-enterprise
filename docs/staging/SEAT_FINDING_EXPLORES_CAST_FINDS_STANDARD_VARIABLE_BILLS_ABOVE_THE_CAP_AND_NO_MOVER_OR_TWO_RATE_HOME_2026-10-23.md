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

**Built 24 Oct (beside the claim).** "The ladder has no step after the second notice" was true of
the PUBLISHED record and not of the company. There are two ladders:
- The published per-bill stage list is `arrears_engine.LEDGER_NOTICES`, two notices, read by the
  world's `arrears_stages`.
- The company's live desk (`collections_journey`, run by the triad) has five rungs, up to a Consent
  prepayment offer at day 90. After that rung it went silent until the household left.

The desk now acts past its top rung. Each further missed bill re-offers the SLC 27.6 menu through
the plan door. A live debt is written off by one named rule: the statute bar, six years past due
and six years since any payment.
- K8 page: `docs/market_research/company_debt_management.md`, "After the last rung".
- Partition control: `tests/company/billing/test_the_collections_ladder_has_a_step_after_the_last_rung.py`.

**Still open (handed on):**
- The explore page and the per-bill record show `LEDGER_NOTICES`, not the desk's journey. A reader
  still sees two notices and silence until the per-household record carries the desk's stages.
- The two ladders still disagree on the plan-offer day (21 against 28).

## 4. Slots no household can fill

- **The mover.** The published per-household record has no move-out event and no final-bill
  marker. The 181 `OCC-` accounts are not linked to the household they replaced. Until the 22 Oct
  mover fix emits those links, the slot says so on the page.

  **Re-graded 2026-10-24** (rules: `docs/market_research/home_moves.md` §8.8; measure:
  `billing_accuracy.move_out_final_bills`, over the published run of 2026-10-22, producing commit
  `1044c8fe0d`, no new arm):
  - The household record now carries a `moved_out` event and a `final_bill` event, with the
    closing read's basis and the amount (`tools/generate_customer_reaction_chain.py`). An `OCC-`
    page names its predecessor account from `occupier_successions`. The current run predates that
    field, so all 181 pages say "the run predates occupier_successions" until the next run.
  - **256 move-outs.** 249 closed an account with a final bill. 7 name an account whose final bill
    ended 28 days to 9 months *before* the move. The account had already left us, so the move
    closed nothing of ours, and those 7 are graded against nothing. The world puts a move in the
    supplier's register for a household it no longer supplies. Filed here, not yet chased.
  - **Final bill within 6 weeks (SLC 27.17): 249 of 249 on time, and that proves nothing.** Every
    bill's issue date is its period end (`invoice.py`), so every final bill is dated the day
    before the move (−1 day). The late branch cannot fire in this run. It is proven able to fire
    on a fixture (`test_every_final_bill_branch_can_be_taken`).
  - **Closing read: 164 of 249 estimated (66%)**, 85 actual (electricity 87/136 estimated, gas
    78/113). No rule requires an actual closing read, and the published share is a GAP (G8.9). A
    mover is told to read the meters on the day, so two in three closing on an estimate is a
    fidelity question for the read lane. Not graded as a breach.
  - **Credit refunded within 10 working days of the final bill (GSoP reg 6D): 19 of 21 on time,
    2 late (14 and 20 working days).** Only direct-debit accounts that closed in credit are in
    the refund log. For the other 228 the run records no closing balance. The late tail is the
    world's `credit_refund_events.ON_TIME_PROBABILITY` draw. The log labels this rule "SLC 14",
    which is the wrong locus (corrected in §8.8).
  - **Debt carried: unmeasured, `None` with its reason.** The run publishes no closed account's
    balance at its final bill. Next: publish that balance per closed account, then this branch
    reads it.
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

## Why this stays BLOCKING, 24 Oct 07:25: the fixes are on origin, and the published run is not

The defects in sections 1, 3 and 4 have been built or graded on origin. Section 1 fell from 5,488 to 104
of 24,597 on the fresh run (`d909b69338`). This file still holds lane D, and correctly. The site publishes
run `8b6fea024` of 19 Oct (`site/data/explore_cast.json` `meta.run_git_commit`; `company.json`,
`billing_accuracy.json` and `case_studies.json` are the same). None of the fixes reaches it:
`4bc21e9209` (an incoming occupant is domestic), `4ef70aba92` (the EPG reaches the bill) and
`ce35a25e21` (the void stub's estimate). Its households' bills, and the ledger, debt and revenue figures
drawn from them, still charge 199 of 550 households above the ceiling.
That is `background/finding_severity.py`'s BLOCKING: "a published figure may be wrong".

**What clears it is a published run whose commit carries all three fixes, not more code.** The fresh
run that carries them (`/var/tmp/se-overcap-out/run_output_88cdf35e48.json`) was a grading run. It is
not in `docs/reports/`, so no publish can pick it. Two things stand in the way, measured at 07:23 UTC:

- The shared checkout, which the simulation runner executes, is **106 commits behind origin and
  0 ahead**. Not one of the three fixes is an ancestor of its HEAD. A run it produced now would
  publish the over-cap bills again. Bringing it level is claimed (`the-shared-checkout-reaches-origin`,
  07:20 UTC) and is in the orienting seat's focus, so this file does not do it.
- The publish hold opens Mon 26 Oct 04:00 GMT (`.publish_gate_state.json`).

**To close:** once a run at a commit that has `ce35a25e21` as an ancestor is published, re-grade it with
`tools.grade_svt_invoices_over_ceiling`. The cast's `book_breaches.above_cap` should then fall from 199
households to near the 16 the fresh run showed. Lower this file to LATENT on that reading, not before.
