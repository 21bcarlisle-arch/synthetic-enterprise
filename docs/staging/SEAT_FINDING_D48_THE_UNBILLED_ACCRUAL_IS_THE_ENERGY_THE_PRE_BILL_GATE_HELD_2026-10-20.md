**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** unbilled-energy-and-revenue-assurance

# D48's unbilled accrual: what it is in this run, and what it measured (2026-10-20)

*Delivery seat, 2026-10-20. Discharges the accrual clause of
`SEAT_FINDING_D48_THE_EXPERT_HOUR_FAILS_ON_THE_CLAIM_NOT_THE_MEASURE_2026-10-14.md` (MAJOR #2).*

## What the accrual is, before it is measured

Unbilled energy at a period end is energy the company believes was used and has not charged
anyone for. Per account, at a month end T: the company's own figure for each period up to T (the
actual read where it has one; otherwise the estimate it made for that period from its last actual
reads shaped by the published profile, or before any read from the registry EAC/AQ with the TDCV
fallback -- `unread_month_estimate.py`, already stamped on every bill as
`estimated_consumption_kwh`), less what it ISSUED bills for. Priced at the account's own unit rate.

In this run every account is billed every calendar month to the month end, so the only way a
period's energy is used and not charged is that the pre-bill gate HELD the bill
(`pre_bill_validation.validate_bills`): the ledger does not recognise it, the customer never sees
it. A held estimate stays unbilled until an actual read ends its run (the catch-up reconciles it as
"billed nothing", `monthly_bill_assembly._resolve_catchup`); that is the same "a read ends the run"
rule E3's `estimated_billing_outstanding` uses, and it is reused, not restated. A held bill on an
actual read is not in any estimated run, so no catch-up ever recovers it.

Centrica's "unread revenue" = billed-on-estimate (E3's figure) + unbilled (this). Both are now
computed; they count different bills and are never added into one number on our page.

## Pre-registration (written before any run figure was read)

1. The accrual at each year end is non-zero but small: under 1% of that year's issued kWh per fuel.
2. Most held bills are on an estimate rather than an actual read.
3. Some held ACTUAL-read bills exist on the published run, and their energy is never billed later.

## Measured

On the published run's bills (`docs/reports/run_output_latest.json`, run_output_44a21e3e8_20261020T085542Z,
38,005 bills, run end 2025-06-07), through the run's own door
(`company.interfaces.bill_assembly.billing_accuracy` -> `K1_unbilled_accrual`). 46 bills were held:
40 estimated, 6 on an actual read. Every one is electricity; gas has a measured zero at every
month end.

| Month end | Accounts | Held estimates open | Held actuals | Unbilled kWh | £ net of VAT | of which >12 months old | of which on closed accounts | Issued elec kWh that year |
|---|---|---|---|---|---|---|---|---|
| 2016-12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 444,578 |
| 2017-12 | 2 | 2 | 0 | 7,146 | 888 | 0 | 0 | 779,609 |
| 2018-12 | 3 | 6 | 1 | 18,293 | 2,539 | 0 | 12,825 | 675,392 |
| 2019-12 | 3 | 14 | 1 | 38,651 | 6,232 | 14,797 | 12,825 | 634,160 |
| 2020-12 | 3 | 7 | 1 | 19,937 | 2,873 | 14,797 | 12,825 | 617,955 |
| 2021-12 | 2 | 5 | 2 | 17,024 | 2,414 | 14,797 | 12,825 | 614,587 |
| 2022-12 | 2 | 5 | 3 | 19,186 | 3,774 | 17,024 | 12,825 | 610,865 |
| 2023-12 | 3 | 6 | 3 | 21,337 | 4,295 | 17,024 | 12,825 | 641,009 |
| 2024-12 | 2 | 5 | 3 | 19,186 | 3,774 | 19,186 | 12,825 | 686,255 |
| 2025-06 (run end) | 3 | 5 | 6 | 27,632 | 6,192 | 19,186 | 12,825 | 317,229 (half year) |

The last column is a year's FLOW beside a STOCK at one date, so their ratio is not a share of
anything; it is there for scale only.

**Pre-registration graded.**
1. REFUTED. The stock is 1-6% of the year's issued electricity kWh, not under 1%. It is
   concentrated: seven accounts across the decade, two or three at any year end.
2. CONFIRMED. 40 of 46 held bills are estimates.
3. CONFIRMED. Six held actual-read bills on two accounts, never billed later. One
   (OCC-8c6b8bb21743, 2025-01) carried a 1,266 kWh / £310 catch-up that went out with nobody.

**What it is made of.** Every held bill on this run was held by the same check: `vat_by_segment`,
a "resi" account whose metered load (2,000-4,300 kWh a month) implies a non-domestic customer. The
gate holds the bill and nothing ever resolves the hold, so the energy stays unbilled. One leaver,
PROS-2017-0117, left in April 2018 with five held estimates (12,825 kWh) and no read: the whole
"closed account" column. PROS-2017-0336 had 32 held estimates over 2017-2021, each recovered by a
later read's catch-up (subject to the 12-month bar).

**Against the one published witness.** Centrica's year-end gross unbilled is about 20 days of
revenue (§K1). Ours is near zero by construction for every ordinary account, because calendar
billing to the month end leaves no between-bill-runs part. What we have is only the
billing-failure part of K1. That gap is stated in the note's K1 row, not filled with a number.

## What this discharges, and what it leaves

- **Discharged:** MAJOR #2 of the 2026-10-14 expert hour. The accrual is computed, from the
  company's own bills only, and reached from the run through the issuance door
  (`bill_assembly.billing_accuracy` names the held bills, because issuance is decided there).
  Controls: `test_the_unbilled_accrual_takes_every_branch_and_counts_only_energy_never_issued` and
  `test_the_run_door_carries_the_accrual_and_it_counts_a_bill_the_gate_held`. Four mutations went
  red: accrual dropped from the summary, door passing no held set, the "a read ends the run" rule
  removed, and a held actual's catch-up dropped.
- **Reused, not restated:** E3's predicate is now `saas.ledger.open_estimated_bills`, the one
  statement read by both `estimated_billing_outstanding` and the accrual. The estimate per period is
  the one `unread_month_estimate.py` already stamped on the bill.
- **Still open, filed here:**
  1. `account_billing_accuracy` counts held bills in `billed_kwh` and K2's `estimated_kwh`. A held
     bill was never billed. 46 of 38,005 bills, so the published shares barely move, but "billed"
     includes bills nobody received. Fix: the same held set, passed in.
  2. A `vat_by_segment` hold is never resolved, so the same household's energy goes unbilled month
     after month. A real exception queue is worked: the account is re-segmented and billed, or
     confirmed domestic. `release_confirmed_domestic` exists for the consumption-scale hold only.
     That is a billing-operations gap, not something to fix in the measure.
  3. The accrual is not yet on the billing page (`published_view`). The summary carries it.
  4. Billed against settled (K6) stays a GAP: settled volume does not cross the seam.

## Follow-on (open items 1 and 3): held bills leave "billed", the accrual reaches the page

*Delivery seat, 2026-10-20, later the same day.*

**Definition first.** "Billed" means issued: a bill the customer received. The per-account rows
(K2's billed and estimated kWh, the true-ups, K3's barred energy) and the K1 billed-on-estimate
grades are therefore read over the issued set, the one `saas.ledger.estimated_billing_outstanding`
already uses. The held bills are the accrual's alone, so the two halves of unread revenue count
disjoint bills by construction, not by a note on the page.

**Pre-registration (written before the before/after was printed).**
1. Gas: every K2 figure is unchanged (no gas bill was held).
2. Electricity: K2's estimated share of billed kWh moves by less than 0.5 percentage points, and
   down (40 of the 46 held are estimates, so estimated kWh loses proportionally more than billed).
3. Electricity's K1 year-end outstanding falls at the year ends where held estimates were open
   (2017-2025), by roughly the accrual's held-estimate £ at that month end.

**Measured** at real inputs, the 44a21e3e8 run's 38,005 bills (46 held), the same bills before
(held set empty) and after:

| Fuel | Billed kWh | Estimated kWh | K2 estimated share | Snapshot no-read | K3 barred share |
|---|---|---|---|---|---|
| electricity | 6,145,724 -> 6,021,639 | 4,153,261 -> 4,042,716 | 67.58% -> 67.14% | 6/175 -> 6/175 | 0.259% -> 0.260% |
| gas | 14,710,733 (unchanged) | 9,966,238 (unchanged) | 67.75% (unchanged) | 7/132 | 0.877% (unchanged) |

Electricity K1 outstanding on estimate, before -> after: 2017-12 £45,157 -> £44,225; 2019-12
£70,172 -> £64,031; 2022-12 £131,919 -> £130,203; 2024-12 £109,102 -> £107,386 (2016-12
unchanged, nothing held yet). The fall is gross of VAT; the accrual at the same dates is net of
VAT and includes the held reads, so the two match roughly, not exactly, as they should.

**Graded.** 1 CONFIRMED (gas identical). 2 CONFIRMED (-0.44 pp, down). 3 CONFIRMED (falls at
every year end from 2017, by about the held estimates' value).

**Published.** `site/data/billing_accuracy.json` regenerated from the run it already published
(8b6fea024; the 44a21e3e8 run stays held for the weekly window): electricity K2 67.60% -> 67.06%,
and the accrual table, 2025-06: 5 held estimates and 2 held reads, 19,055 kWh, £3,441 net of VAT.
`published_view` now rebuilds the summary from the run's bills and the held set the issuance door
names (`bill_assembly.held_bills`), so an older run output publishes both changes without a re-run.

Items 1 and 3 discharged. Item 2 (a `vat_by_segment` hold is never worked) and item 4 (K6) stay
open.

## Follow-on (open item 2): why six held actual-read bills are never released

*Delivery seat, 2026-10-20, later again.*

**Which part never fires.** Not the release's reach: `validate_bills` calls
`release_confirmed_domestic` on every hold, and on the 44a21e3e8 run it already releases 21 held
actual-read bills (`validate_bill` alone holds 67; 46 survive the queue). Not the hold reason: all
six are `consumption_scale_only` (the implied-VAT and resi-plausibility ceilings, nothing else).
**It is the listing.** All six bills carry no `premise_council_tax_listed`, and so do all 6,342
bills on the run's 178 `OCC-` accounts. `simulated_council_tax_listing` answers by ACCOUNT id
(`customer_id in live_premises()`), but a council tax listing is a fact about the supply ADDRESS.
An incoming occupier is supplied at the dwelling its predecessor vacated
(`incoming_occupant_of`), so the address is on the list whenever the predecessor's was; the
lookup never asks.

The six, by dwelling (link reconstructed from each OCC account's acquisition date against
`home_move_outs`, unique for both):
- `OCC-8c6b8bb21743` (2025-01, the GBP 310 catch-up, and 2025-02): SYN-2016-565's dwelling, which
  is listed. The address-keyed lookup releases both.
- `OCC-d8e674fa38de` (4 bills, 2018-2025): founder C8's home. The world holds no premise record
  for a hand-authored founder, so the answer stays None and the four stay held. That is the
  feed's own honest None, not this defect; filed below.

**Pre-registration (written before the before/after is printed).**
1. Held bills 46 -> 44; held actual-read bills 6 -> 4; held estimates unchanged at 40.
2. K1_unbilled_accrual is unchanged at every year end through 2024-12 (both released bills are
   2025) and falls at the 2025-06 run end by the two bills' 4,964 kWh, from 27,632 to 22,668.
3. Every OCC account whose dwelling is a drawn premise reads `listed True` after the fix; the
   founders' dwellings and their occupiers stay absent.

**Fix.** `simulated_council_tax_listing` (simulation/run_phase4c_on_phase2b.py) now asks about the
dwelling: `_supply_address_of` follows `incoming_occupant_of` back through the occupant book to the
first account at the premise, and the answer is that dwelling's listing. World-side only; the
company reads the same `premise_council_tax_listed` key as before. Control:
`test_the_council_tax_listing_is_asked_about_the_dwelling_an_occupier_moved_into`. It goes red
when the lookup is keyed by account id again, and red when only one move is followed.

**Measured** at real inputs: the 44a21e3e8 run's 38,005 bills, before and after. "After" has the
key stamped the way the fixed feed stamps it, with each OCC account's dwelling taken from the
reconstructed link, read through the run's own door (`bill_assembly.held_bills` /
`billing_accuracy`). This is not a re-run. The run output was stamped by the old feed, so the
published page moves at the next run, not now.

| | before | after |
|---|---|---|
| Held bills | 46 | 44 |
| of which on an actual read / estimated | 6 / 40 | 4 / 40 |
| OCC accounts read as listed | 0 of 178 | 157 of 178 |
| K1 accrual, electricity, 2016-12 .. 2024-12 | (table above) | identical at every month end |
| K1 accrual, electricity, 2025-06: accounts / held actuals | 3 / 6 | 2 / 4 |
| K1 accrual, electricity, 2025-06: kWh | 27,632 | 21,402 |
| K1 accrual, electricity, 2025-06: GBP net of VAT | 6,192 | 4,386 |
| Gas | 0 | 0 (unchanged) |

**Graded.**
1. CONFIRMED. 46 -> 44 held, actuals 6 -> 4, estimates 40.
2. Half right. "Unchanged through 2024-12" is CONFIRMED: 2025-06 is the only month end that
   moved. The kWh is REFUTED: the accrual fell 6,230 kWh, not 4,964, to 21,402, not 22,668. The
   1,266 kWh I did not predict is exactly the 2025-01 bill's `read_true_up_kwh` (1,266.10): energy
   from the 2024-10..12 estimates, under-billed and carried by the held actual. Releasing that bill
   releases its true-up as well. The earlier section counted "a held actual's catch-up" in the
   accrual, and I left it out of the prediction.
3. PLAUSIBLE, not confirmed. 157 of 178 read listed. Of the 21 that do not, 7 are occupiers of
   founder homes (C1, C1g, C4, C4g, C8) and 2 chain through those. The other 12 are accounts my
   reconstruction could not link uniquely (more than one move-out on the date). That is a limit of
   this instrument, not of the feed, which follows the real link. The next run settles it.

**What stays held, and why.** The four `OCC-d8e674fa38de` bills (and the founders' own
consumption-scale holds) are at hand-authored founder homes. The world draws no premise for these,
so the listing honestly answers None. A real supplier would look the address up. The founders
have no address to look up, so this is a gap in the roster's data and not in billing operations.
Open, filed here: either give the eight founder homes a drawn premise record, or let the queue
re-segment a hold the listing cannot answer. The re-segment route is the other half of a worked
exception queue, and nothing here does it yet. The 40 held estimates stay held by design until an
actual read replaces them.

Item 2 discharged for the defect the item named, and the founder-home remainder filed above.
Item 4 (K6) stays open.

## Follow-on (closed account): the leaver's held estimates go out on its final bill

*Worker, 2026-10-21. Claim `d48-a-held-estimate-on-a-closed-account-is-never-worked`.
Pre-registration: `docs/staging/records/WORKER_PREREG_A_HELD_ESTIMATE_ON_A_CLOSED_ACCOUNT_GOES_OUT_ON_THE_FINAL_BILL_2026-10-21.md`.
K8: `docs/market_research/unbilled_energy_and_revenue_assurance.md`, K6, "A held bill on an
account that closes".*

**What the hold was.** PROS-2017-0117 is on the council tax list (`premise_council_tax_listed`
True on every bill). The listing was never what held it. Its four interim estimates (2017-12 to
2018-03) and its estimated final bill (2018-04-11) were each over the domestic ceiling. A ceiling
hold on an estimate waits for an actual read, and after the exit no read reaches the losing
supplier. Its closing read is the CoS read, actual or Old Supplier Estimated, and it is settled on
that read. The read moves only through a dispute. SLC 27.17 wants the final bill within 6 weeks,
running to that read.

**Fix.** `build_monthly_bills` stamps `final_bill` on a churned account's last bill. The queue now
releases a hold in the account's closing run, meaning the estimated bills after its last actual
read through the final bill, when four things hold: every reason is consumption scale, the account
is resi, the address is listed, and SLC 21BA does not bar the bill at the final bill's date
(`pre_bill_validation.release_at_closing_read`). The released copy carries `issued_with_final_bill`.
The accrual counts such a bill as unbilled until the final bill's month
(`issued_with_final_bill`), so the 2017-12 to 2018-03 month ends still show it.

**Controls.** `test_every_leg_of_the_closing_run_release_is_reachable` covers the whole partition
in one call: released, open account, unlisted, final on an actual read, and barred by 21BA.
`test_the_accrual_holds_a_closing_run_until_the_final_bills_month` and
`test_the_billing_run_stamps_only_a_churned_accounts_last_bill_as_final` cover the other two legs.
Six mutations were run. Five went red: the release dropped, the 21BA bar dropped, the listing check
dropped, the accrual's late issue dropped, and the stamp dropped. The sixth, dropping the
"final bill is an estimate" test from `_closing_runs`, stayed green. That is an EQUIVALENCE, not a
missing test. A final bill on an actual read is the last read, so its run is already empty. The
clause was redundant and has been deleted.

**Measured** on the 44a21e3e8 run's 38,005 bills, with `final_bill` stamped the way the changed
assembly stamps it (each churned account's last bill), through `bill_assembly.held_bills` /
`billing_accuracy`. This is not a re-run.

| Month end | before: accounts / held est. / held act. / kWh / GBP / closed-account kWh | after |
|---|---|---|
| 2017-12 | 2 / 2 / 0 / 7,146 / 888 / 0 | unchanged |
| 2018-12 | 3 / 6 / 1 / 18,293 / 2,539 / 12,825 | 2 / 1 / 1 / 5,468 / 904 / 0 |
| 2019-12 | 3 / 14 / 1 / 38,651 / 6,232 / 12,825 | 2 / 9 / 1 / 25,827 / 4,597 / 0 |
| 2021-12 | 2 / 5 / 2 / 17,024 / 2,414 / 12,825 | 1 / 0 / 2 / 4,199 / 779 / 0 |
| 2024-12 | 2 / 5 / 3 / 19,186 / 3,774 / 12,825 | 1 / 0 / 3 / 6,361 / 2,139 / 0 |
| 2025-06 | 3 / 5 / 6 / 27,632 / 6,192 / 12,825 | 2 / 0 / 6 / 14,807 / 4,557 / 0 |

At 2018-03 the accrual still holds the four interims (18,212 kWh). At 2018-04 they are gone.
Held bills fell 46 -> 41, and gas stays zero.

**Where the energy went: unbilled -> billed on estimate.** This is the one other figure that moves,
and it is the correct move. A final bill on an estimated closing read is billed on an estimate that
no read will true up. The other leavers whose final bill was on an estimate sit in the same place.
Electricity K2 rose from 67.14% to 67.21% (billed kWh +12,825, estimated kWh +12,825). K1's
billed-on-estimate outstanding gained the account's 12,825 kWh / about GBP 1,716 gross of VAT at
every year end from 2018-12. Unread revenue (billed-on-estimate plus unbilled) is unchanged; the
energy changed halves. No other account's figures moved.

**Graded.**
1. CONFIRMED. Exactly the five PROS-2017-0117 bills were released. No other bill changed state.
2. CONFIRMED. 2016-12 and 2017-12 are unchanged. Every later year end falls by 12,825 kWh and
   GBP 1,635. `closed_account_kwh` is 0 at every month end.
3. CONFIRMED. Nothing was barred: the run spans under five months.

This measurement does not include the founder-home fix (claim
`d48-a-ceiling-hold-the-listing-cannot-answer-is-never-worked`). That fix lists the founders'
authored homes, which releases the four `OCC-d8e674fa38de` bills at C8's semi. It is **built and
not landed**: its turn ended at 02:15 BST with no commit, and the work survives only as salvage
commit `9dc0cf4b0` (`SALVAGE(auto)`, the seat's `/var/tmp/se-seat-executor` fork). Re-apply it,
don't rebuild it. *(Later, 2026-10-21: re-applied and landed. See "Follow-on (founder homes)" below.)* With both fixes in place, the 2025-06 accrual is the two `OCC-8c6b8bb21743` bills
that item 2 released in code (6,230 kWh). The run was stamped by the old feed, so they still read
held here, and the next run settles them. The published page moves at the next run, as items 2 and
3 did.

**Left open, named.**
- An interim that 21BA bars at the final bill stays held. Its energy shows in the accrual's
  over-12-months column, but it is not booked to the write-off register. **GAP**, recorded in the
  K8 section.
- The K1 billed-on-estimate grade and the per-account rows read a released interim as issued at its
  own period end, not at the final bill's. On this run that misdates one bill at one year end
  (2017-12, 3,120 kWh). It is a dating error in a grade. *(Fixed 2026-10-21: see "Follow-on (K1 dating)" at the end.)*
- A dispute of the closing read is not modelled, by the same choice as the leaver's settlement leg.

## Follow-on (founder homes): the four held bills at C8's semi are released

*Delivery seat, 2026-10-21 (built); worker, 2026-10-21 (landed). Claim `d48-a-ceiling-hold-the-listing-cannot-answer-is-never-worked`.
Pre-registration: `docs/staging/records/SEAT_PREREG_THE_FOUNDER_HOMES_ARE_ON_THE_COUNCIL_TAX_LIST_2026-10-21.md`.*

**Which route.** The world side. The premise above, that "the world holds no premise record" for a
founder, was half true. The founders draw no premise, but the world authored each resi founder as a
dwelling (`home_type`: urban_flat, suburban_semi, tenement_flat, rural_detached). C8 is a 3-bed
Manchester semi. Every GB dwelling is on a council tax list (VAT Notice 701/19; the Scottish Assessors
keep the list for the Glasgow founders). So the honest world answer is True, and the None was the
feed not asking. `simulated_council_tax_listing` now also lists an address in `_authored_dwellings`.
That set is the roster records whose `home_type` is a dwelling type in
`dwelling_records.PROPERTY_TYPE_BY_HOME_TYPE`: C1-C4, C7-C9 and the gas legs. C5, C6 and the I&C
points stay None. Control:
`test_a_founder_authored_as_a_home_is_on_the_list_and_a_business_founder_is_not`. It goes red when
the founder clause is dropped, and red when every authored founder is listed. Both mutations were
run. K8 section: `docs/market_research/unbilled_energy_and_revenue_assurance.md` §4c, with a
paragraph published on the unbilled-energy page.

**Why not the other route.** A run refuses a resi electricity account with no dwelling
(`build_properties` raises `DwellingNotDrawn`). So once authored homes answer, no domestic hold in
this world reaches the queue without a listing answer. A contact/certificate or re-segmentation step
would be a mechanism nothing reaches. It is recorded as a design choice and a GAP in §4c: an address
genuinely off the list, such as a new build before banding, is not modelled.

**Measured** with item 2's method: the 44a21e3e8 run's 38,005 bills, stamped the way the fixed feed
stamps them, through `bill_assembly.held_bills` / `billing_accuracy`. This is not a re-run.

| Month end | before: accounts / held actuals / kWh / GBP | after |
|---|---|---|
| 2017-12 | 2 / 0 / 7,146 / 888 | unchanged |
| 2018-12 | 3 / 1 / 18,293 / 2,539 | 2 / 0 / 16,321 / 2,156 |
| 2019-12 | 3 / 1 / 38,651 / 6,232 | 2 / 0 / 36,680 / 5,849 |
| 2020-12 | 3 / 1 / 19,937 / 2,873 | 2 / 0 / 17,965 / 2,490 |
| 2021-12 | 2 / 2 / 17,024 / 2,414 | 1 / 0 / 12,825 / 1,635 |
| 2022-12 | 2 / 3 / 19,186 / 3,774 | 1 / 0 / 12,825 / 1,635 |
| 2023-12 | 3 / 3 / 21,337 / 4,295 | 2 / 0 / 14,975 / 2,156 |
| 2024-12 | 2 / 3 / 19,186 / 3,774 | 1 / 0 / 12,825 / 1,635 |
| 2025-06 | 2 / 4 / 21,402 / 4,386 | 1 / 0 / 12,825 / 1,635 |

Held bills 44 -> 40, all 40 estimates. Gas stays zero. From 2021-12 to the run end, K1 is now exactly
the closed account's 12,825 kWh of held 2018 estimates. The closed-account fix (7a266cb76, the
section above) releases those. It landed after this measurement was taken, so this table's "before"
does not include it. With item 2, the closed-account fix and this one all in place, the 2025-06
held-actual accrual is the two `OCC-8c6b8bb21743` bills item 2 released in code. They still read held
here only because the run was stamped by the old feed.

*Re-applied 2026-10-21 by a worker tick from salvage commit `9dc0cf4b0`. The turn that built it was
killed at 02:15 BST before it committed. The code, the control, the K8 section and these numbers are
that turn's. Only this paragraph and the sentence above it are new.*

**Graded.**
1. CONFIRMED. 44 -> 40 held, actuals 4 -> 0, estimates 40.
2. CONFIRMED. Held actuals are 0 at every month end. The first move is 2018-12. At 2025-06 the
   accrual fell 8,577 kWh, which is the four bills' kWh (1,972 + 2,227 + 2,162 + 2,216). None of
   the four carried a `read_true_up_kwh`.
3. REFUTED AS MEASURED, and the refutation is the instrument's. Outside a run, 288 resi `PROS-`
   accounts in the 44a21e3e8 bills read None. HEAD's campaign draws a different winner set from the
   code that produced that run: 371 PROS ids are in the run's bills and 358 in HEAD's draw, of which
   228 are shared. 8927e9345 (founders as 400 households) landed after the run. Inside a run the
   winners are the run's own, and `build_properties` refuses any resi electricity account without a
   dwelling. So "no resi hold without an answer" holds by construction for electricity. It is not
   measured here. The next run settles it.

The published page moves at the next run, as item 2's did.

## Follow-on (K1 dating): a closing-run interim counts as billed on estimate from the final bill's month

*Worker, 2026-10-21. Pre-registration:
`docs/staging/records/WORKER_PREREG_THE_K1_GRADE_DATES_A_CLOSING_RUN_INTERIM_AT_THE_FINAL_BILL_2026-10-21.md`.*

**Fix.** `estimated_billing_outstanding_grade` now dates each bill by the month it was issued. For
a bill in `issued_with_final_bill` that is the final bill's month; for every other bill it is the
bill's own period end. `billing_accuracy_summary` computes the late-issue map once and passes it to
both the grade and the accrual, so the two halves of unread revenue count disjoint bills at every
month end. Control:
`test_the_k1_grade_counts_a_closing_run_from_the_final_bills_month_and_never_beside_the_accrual`.
It goes red when the grade dates by period end again (mutation run).

**Measured** with the pre-registration's instrument: the 44a21e3e8 run's 38,005 bills, with
`final_bill` stamped on each churned account's last bill. 5 bills were released at closure and 41
are held. Before (no late map) and after were computed in one process.

| Year end | before -> after |
|---|---|
| electricity 2017-12 | open bills 988 -> 987; open kWh 292,782 -> 289,662 (-3,120.35); outstanding GBP 44,642 -> 44,225 (-417.16); open runs 212 -> 211; never-read runs 72 -> 71, kWh -3,120.35 |
| every other electricity year end, every gas year end | identical |

**Graded.** 1 CONFIRMED: only 2017-12 moves, by PROS-2017-0117's 2017-12 interim (3,120.35 kWh,
GBP 417.16). 2 CONFIRMED: no `graded_*` figure moves. 3 CONFIRMED: gas is identical. 4 holds by
construction: the accrual reads the same map it read before.

Left open from the closed-account list: the 21BA-barred interim's write-off (GAP), and the dispute
of the closing read (not modelled).

## Follow-on (first run carrying the releases): graded, and the estimate half of the ceiling gets its release

*Worker, 2026-10-21. Pre-registration and grade:
`docs/staging/records/WORKER_PREREG_D48_THE_FIRST_RUN_CARRYING_THE_HELD_BILL_RELEASES_2026-10-21.md`.*

The unpublished shared-tree run at 9ca972774 carries items 2, closed account and founder homes. All
four predictions held. There are no held actuals at any month end, no resi electricity bill with an
unanswered listing, and no held bill in any of the 2,734 closing-run bills. K1 differs from HEAD at
one year end only, as ab3baa0b0 predicts.

The 40 held estimates that remain are five accounts. 32 of them are PROS-2017-0336, a listed
dwelling, which went 14 months with no bill and then got one GBP 5,067 catch-up. 31 of the 40 were
at or under a rate the same meter had already measured. **Built:**
`pre_bill_validation.release_on_measured_rate`, asked by the issuance door and by the assembly's
catch-up. Rules first: `unbilled_energy_and_revenue_assurance.md` §4d (SLC 21B.5). Re-validated
over these bills: 9 held. The money moves at the next run, as the pre-registration predicts.

## The money grade for `release_on_measured_rate`, on the first run that carries it (worker, 2026-10-21, evening)

The shared tree's plain run is at **8e99f83cd** (generated 15:57Z), which has 4d6d5ab91 as an ancestor. It is
unpublished. The instrument is the one the pre-registration names: `bill_assembly.held_bills` over the run's
53,314 bills.

| prediction (records/WORKER_PREREG_D48_..._2026-10-21.md, as corrected 08:10Z) | run | verdict |
|---|---|---|
| held estimates fall to single digits | **9**, on 4 accounts, all estimates, 0 actuals | HELD |
| no gap over two months on PROS-2017-0336 | 2017-12 and 2018-01 held, then released at its first actual read | HELD |
| none over three on the book | longest is 3 (SYN-2016-582, 2016-12 to 2017-02) | HELD |
| PROS-2017-0336's largest catch-up below GBP 1,000 | **cannot be graded from this run** | NOT GRADED |

This is the same 9-bill set that HEAD's re-validation named at 08:10Z, so the run agrees with the gate's own
reading. The 2019-04 to 2020-05 silence on PROS-2017-0336 is gone: each of those months now carries its own
estimated bill (GBP 426-654).

**Why the fourth does not grade.** The published `bills` rows drop the `catchup_*` fields that
`monthly_bill_assembly` stamps, so the catch-up adjustment cannot be read. The only figure available is the bill
total. The account's 2018-02 actual bill is GBP 1,809, against GBP 495-555 for its neighbouring months. That
excess (~GBP 1,250) is about the two held months (GBP 516 + 546) plus a true-up. If that inference is right, the
bound is narrowly **not met**. But it is an inference from totals, and it is not recorded as a grade. Grading it
needs the catch-up fields carried on the published bill, or the run re-assembled. The two held months are what
§4d intends the screen to hold (no earlier read), so a two-month catch-up of ~GBP 1.1k is the rule working, not a
defect. The GBP 1,000 bound was set before the 08:10Z correction left these two months held. It should be read
as "no more than the held months", not as a number.
