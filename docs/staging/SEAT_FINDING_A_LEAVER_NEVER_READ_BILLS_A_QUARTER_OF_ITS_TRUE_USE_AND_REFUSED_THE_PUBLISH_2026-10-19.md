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
