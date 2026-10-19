**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `D46_the_validator_holds_against_the_varied_population`

# A leaver never read in 42 bills was billed a quarter of its true use, and it refused the 19 Oct publish

**Found by** the delivery seat on 19 Oct 2026, while checking the premise of
`grade-the-dual-fuel-preregs-after-the-publish-run`.

## What happened

The 03:30Z run on 19 Oct (`producing_commit` 8b6fea024) finished. Its publish commit was then
refused by the hook chain at 06:35Z (`process_run`, rc=77, `commit_refused`). The one blocking test
was `tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_margin_for_any_real_customer_year`.
So the first dual-fuel run is still unpublished, and the preregs it was meant to grade can't be
graded yet.

I re-ran the gate on the run's own ledger and sample, copied from the shared tree:

- **All 12 named inversions are gone.** Both void-stub OCC rows, the held-estimate rows, and the
  leaver rows all cleared. The fixes at 650fdcdd7 and e6785dce5 work on a ledger they actually
  billed.
- **One new account fails: `C7`, in 2016–2019.** It was billed 458.85, 528.55, 485.90 and 299.46
  against a gross margin of 1,130.53, 1,292.46, 991.53 and 745.20.

## The cause, at real inputs

| | 2016 |
|---|---|
| World consumption (`per_customer_monthly`) | 13,230 kWh |
| Billed consumption (ledger) | 3,100 kWh, flat, every year |
| Invoices | 42 in a row, all `E`, no catch-up ever, closed on an estimate at 2019-06-30 |
| Ratio billed / true | 0.23 (the next-lowest leg on the book is 0.40) |

C7 is a passive, direct-debit, non-smart founder account. It churned (`churned_billing_accounts`).
Two separate things combine to produce the inversion:

1. **No read was ever forced.** The SLC 21B.4 read instruction at the 11th, 23rd and 35th estimate
   exists (`company/billing/read_duty_register.py`). But
   `DecisionPolicy.instruct_reads_in_billing_run` is off in the standing policy, so the published
   run never raises it.
2. **The closing read is an estimate.** `simulation.meter_reads.simulate_final_read` stopped
   answering actual unconditionally on 2026-10-17, which is a correct fidelity change. In the old
   ledger C7 got an actual read at exit and a catch-up, and that is why it never inverted before.

The gate's docstring said an unresolved estimate on a leaver "is the defect itself". That stopped
being a property of the world on 17 Oct. On this run, 274 of 405 churned legs closed on an
estimate. On 273 of them the error is small enough that billed still exceeds gross, so the gate
still holds for them.

## What I did

- Named the four C7 years in `KNOWN_OPEN_INVERSIONS`, with this cause. That is the file's own
  idiom: a fifth inversion on any other account still turns the gate red. Mutation: with the four
  rows removed, the gate is red on the 19 Oct ledger. With them in, it passes on both the 19 Oct
  ledger and origin's committed one.
- Corrected the `unresolved_account_years` docstring beside the claim the 17 Oct change made
  false.
- **Did not** delete the 12 rows that no longer invert. Origin's committed ledger is still the old
  book and still inverts on them. They go in the first commit after the 19 Oct ledger is
  committed.

## The re-drive (19 Oct, 08:45–09:15Z)

Nothing re-attempted the refused publish after dc4dc0e10 answered its red. The cause is filed as
`SEAT_FINDING_A_REFUSED_PUBLISH_WHOSE_RED_IS_LATER_ANSWERED_IS_NEVER_RE_ATTEMPTED_2026-10-19.md`.
Re-run by hand on the archived marker, the run's outputs were still byte-identical to
8b6fea024's. **The hook chain passed it with no new red.** It committed locally as 2a195224b
(net £555,900). The push was rejected non-fast-forward because origin had moved by two commits,
neither on its paths, and the publisher deferred delivery (rc=80, `committed_delivery_deferred`).
`background.origin_reconcile` then refused the merge on the shared tree (`REFUSED_GATE`, rc=1). Its
`detail` is cut off before the red is named, so the cause there is not established. The same merge
(2a195224b into origin's 9038dd065), built and gated in an origin-based worktree, landed as
f8f3d0fd5 and was promoted. **2a195224b is on origin/main: the 19 Oct dual-fuel book is
published.** The deletions in it (163 `site/data/customers/` files) are the publish's own: the
new run's sample replaced the old one, and origin's side never touched that directory.

Now due, from the list below: delete the 12 `KNOWN_OPEN_INVERSIONS` rows that no longer invert,
since origin's committed ledger is now the 19 Oct one.

**Done 19 Oct (delivery seat).** The sweep was re-run on origin's committed ledger and sample,
both from 2a195224b. Of the 16 named rows, only C7 2016–2019 still invert. Nine of the other
twelve now bill above their gross, and three are no longer account-years in the book. All twelve
are deleted, along with their two reason constants; C7's four stay. Mutation: with C7 2019
removed from the set, the gate is red on exactly `('C7', 2019, 299.46, 745.2)`.

## Owed, and not decided here

- **Which explanation to fix.** In ranked order:
  - (a) The company read duty is off. Turning on `instruct_reads_in_billing_run` is a policy
    change, and K8 says the knowledge page comes first.
  - (b) The world settles the old supplier on true volume but bills it on the estimated
    change-of-supply read. In GB the deemed change-of-supply read fixes the split for both
    suppliers, so settlement and billing should agree on it. This is a W7 fidelity question.
  - (c) 13 MWh a year in a five-plus-person urban flat is itself implausible, and it is the
    reason the 3,100 kWh estimate is so far off. Check it against the population anchors (the
    19 Oct steer's anchor register).
- **Re-grade the preregs once the publish lands.** That is the re-issued drawn item.

## Which cause holds: predictions, written before measuring (delivery seat, 19 Oct)

Ledger and run: `docs/reports/run_output_8b6fea024_20261019T033010Z.json` (the published 19 Oct
book). Population: the 274 churned legs that closed on an estimate.

- **P-a1.** Fewer than half of the 274 reached an 11th consecutive estimate before closing. My
  guess is 25-40%, so 70-110 legs. Most leavers churn inside a year, and a run of estimates is
  broken by the ordinary read on most traditional meters.
- **P-a2.** At the read end, the instruction trues up C7's 11th, 23rd and 35th estimates. The
  gate's per-year comparison then clears for 2016, 2017 and 2018. 2019 stays open, because its
  last run is shorter than 11 bills. The open closing undercharge on the 274 falls by less than
  half, because most of that money sits in runs shorter than 11.
- **P-b1.** The world settles the losing supplier on true consumption up to the switch, not on the
  change-of-supply read the company bills to. So this leg is live on all 274 legs, not only on C7.
- **P-b2.** In GB the change-of-supply read, actual or deemed, closes the old supplier's
  settlement as well as its bill. The rest of the true volume goes to the new supplier. On the
  GB rule, then, C7's margin would be computed on 3,100 kWh a year, and C7 would not invert.
- **P-c1.** 13,230 kWh a year of electricity is above the DESNZ NEED 5+ adult median (4,129) by
  more than 3x, and above Ofgem's high TDCV for profile class 1. So it is a tail draw. Either C7 is
  electrically heated, and then it is plausible, or the draw composes multipliers that have no
  ceiling. I lean towards composition: about 60% on (c) being a world defect.
- **Overall.** I expect (b) to be the cause on the 274, (c) to be the reason only C7 crosses the
  gate, and (a) to shrink C7's gap without being the root.

## Measured, and graded beside each prediction (delivery seat, 19 Oct)

Method: `tools.closing_estimate_run_money` (`closing_accounts`, `read_instruction_reach`) on the
published run, restricted to the legs of `churned_billing_accounts`. That gives **405 legs, 275 of
them closing on an estimate**. The "274" above was one short, and I have not traced why.

**Correction, beside the claim in (c) above.** C7 is not a five-plus-person household.
`simulation/dwelling_records.py` makes it **one person** in a 1-bed EPC C London flat, with
`electric_storage` heating and an EV. Its demand provider is `hh_metered_reads`: the authored
`sim/hh_data/C7.csv`, written once by `tools/generate_hh_data.py` from the PC1 shape run through
`build_demand_shape`.

| Prediction | Measured | Grade |
|---|---|---|
| P-a1: 25–40% of the 275 reach an 11th estimate | **22 of 275 (8%)** carry a closing run of 12 bills or more, so a visit falls inside it. 245 of the 275 runs are under 5 bills. | **Refuted.** Leavers' closing runs are much shorter than I guessed. |
| P-a2: at the read end C7 2016–18 clear and 2019 stays; the open undercharge falls by less than half | C7's visits fall on bills 12, 24 and 36. True totals 2016–18 are £1,743, £1,999 and £1,806 against gross £1,131, £1,292 and £992, so those years clear. 2019 stays at £299 against £745. On all 584 closed legs, the open undercharge goes from £8,597 to £4,245 (−51%), and C7 is most of the change. | **Held on C7. Borderline on the total** (−51% against "less than half"). |
| P-b1: the world settles the losing supplier on true volume, on all 275 | `saas/reporting/annual_report.py:451` sums `margin_gbp`, and `simulation/hedged_settlement.py:353-355` forms revenue AND wholesale on `consumption_shape`, which is true demand. Nothing clips a churned leg to its closing read (also `unbilled_energy_and_revenue_assurance.md` §5: "consumed = settled = billed after catch-up"). | **Held.** All 275 legs. |
| P-b2: on the GB rule C7 would not invert | BSCP504 v53.0 §4.4.1: with no valid actual by SSD+5, "a valid Old Supplier Estimated reading … must be used". "The CoS reading is assumed to be correct by the Old Supplier, until the Old Supplier disputes" it (fn 22). The gaining supplier's first actual read puts the rest on its own customer's bill. The rule is quoted in `unbilled_energy_and_revenue_assurance.md` §4a. Gas: UNC TPD M5.13 (same section). On billed volume, C7's margin scales by about 0.23, to roughly £265 in 2016 against £459 billed. | **Held by arithmetic.** It was not re-run. |
| P-c1: 13,230 kWh is a tail draw, about 60% a world defect | The commons' overnight-dominant (storage-heating) cluster of real London smart-meter homes averages **18.62 kWh/day, about 6,800 kWh/yr** (`hh_load_shape_clustering_2026.md`). C7 is 36.2 kWh/day, about **2x**, for one person in one bedroom. The other authored storage homes are the same size: C8 (4 people, 3-bed semi) 12,642 kWh and C9 (1 person, 2-bed flat) 12,834 kWh. The uplift does not scale with the dwelling. | **Held: a world defect**, not an implausible-but-real household. |

**A fourth cause, not in the ranked list: (d) the estimate itself.** C7 was billed at exactly
3,100 kWh a year. That is the medium TDCV band `company/billing/unread_month_estimate.py` falls back
to when the registration's `eac_kwh` is empty (Jan 2016: 335 kWh = 3,100 × the January share). The
three HH roster accounts carry `eac_kwh: None` (`saas/customers.py`). The world's own
`EFFECTIVE_EAC_KWH` derives about 13,000 kWh from the same HH file for the hedge, but that figure
never reaches the registration the bill reads. A real gaining supplier receives the meter point's
EAC with the registration. A registry figure of about 13,000 would have billed C7 close to true, and
**no read and no closing true-up would have been needed to keep it above its margin**.

There is a related inconsistency in the world. C7 is settled on half-hourly data, yet its meter
returned **42 estimates out of 42** (C8: 21 of 21 actual; C9: 33 of 33 actual). Settling on HH
reads the supplier never receives is (b) again, in its sharpest form.

### Which cause holds, and its share

- **The 274 other estimate-closed legs are not a defect.** Their open runs net −£395 (undercharge
  £2,453, overcharge −£2,849, roughly symmetric), and none of them inverts. A leaver closing on an
  estimate is the 17 Oct fidelity change working as intended.
- **(b) is present on all 275 (100%).** For each one the run credits revenue on energy it never
  billed. Net, £4,605 across the 275, and C7 is £5,000 of the undercharge side. It is a definition
  mismatch between the margin and the bill, and only C7's size makes it show.
- **(d) × (c) is what makes C7 cross.** The estimate is out by 4.3x: 3,100 against 13,230. About
  2x of that is the world's over-sized storage profile (c), and the rest is the empty registry EAC
  (d). Only one of the 275 legs (C7) is affected, and it is 67% of the open undercharge.
- **(a) is a mitigation, not the cause.** It reaches 22 of 275. On C7 it clears three of four years
  at the read end and none at no-access, and the access rate is a GAP.

### Remedy, filed as its own item

`the-hh-roster-accounts-register-their-eac-and-the-leaver-settles-to-its-cos-read`, handed on
through `background.seat_continuation`. It is a world fix with a prediction, in three legs: (d) give
the HH roster accounts the registry EAC a gaining supplier receives; (c) scale the storage-heating
uplift to the dwelling, against the cluster anchor, K8 first; (b) settle a leaver's final span to
the change-of-supply read, W7 and K8 first. **Prediction for (d) alone:** C7's billed/true rises
from 0.23 to at least 0.9, C7 2016–2019 stop inverting, and its four `KNOWN_OPEN_INVERSIONS` rows
can be deleted.

The read-instruction switch-on is **not** filed as the remedy. Its own prereg is already filed
(`records/WORKER_PREREG_THE_READ_INSTRUCTION_ON_A_PUBLISHED_RUN_AT_BOTH_ACCESS_ENDS_2026-10-18.md`),
and on this book it would treat C7's symptom. What it would change is now on the K8 page
(`read_access_and_theft_duties.md` §2.8). The 12 non-inverting rows were already deleted in
b12f10474.
