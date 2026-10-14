# A supplier does not review the direct debit at an account's final bill: K8 note

**Purpose:** K8 knowledge-before-build note for claim `dd4b-does-a-supplier-review-the-dd-at-a-final-bill`,
acting on `docs/staging/SEAT_FINDING_THE_IN_LOOP_DD_REVIEW_IS_TOLD_TRUE_CONSUMPTION_NOT_THE_SUPPLIERS_
ESTIMATED_BILLS_2026-10-13.md`'s refuted leg. After `5cdaca020`, 45 reviews were in the post-loop census
but not in the loop. Every one was dated at a partial last bill. This note was written before the code
change it authorises.

**Knowledge:** none -- no knowledge-site topic covers the DD review yet. The sibling note
`a_suppliers_annual_dd_review_is_sized_from_its_own_issued_bills_not_true_consumption_2026-10-13.md`
records the same gap.

**Date:** 2026-10-13.

## First, say what the 45 are

The 45 are two different things that happen to share a shape: a bill that ends before the month does.

| | Count (f200) | What it is | Does the account continue? |
|---|---|---|---|
| **A. Leaver's final bill** | 37 | The account closed (switch away or move out). The supplier bills to the last day it supplied. | No |
| **B. Run-end stub** | 8 | The simulation stops at `2025-06-07`, so the last bill is cut short there. | Yes, in the world being modelled. The stub is an artefact of the horizon. |

Each needs its own answer. If the question is asked once about "partial bills", one of the two will get
the wrong answer.

## A. A closing account: no review

**Published (secondary sources quoting Ofgem's rules; Ofgem's own page refused the fetch with a 403):**
- A supplier must send a final bill within **six weeks** of a switch. Which?, *Energy switching
  problems: are you entitled to compensation?* (which.co.uk, 2020): "Ofgem also requires energy
  suppliers to issue a final bill within six weeks."
- Any credit must be refunded within **10 working days** of the final bill (same source; in force from
  2019 under the Guaranteed Standards of Performance, with automatic compensation for a breach).
- A last direct debit may be taken after the final bill only to clear a balance that the account's
  credit does not cover. This is supplier practice as described on supplier forums (search
  2026-10-13). It is a one-off collection of a residual, not a new monthly amount.
- Centrica's receivables disclosure puts **"final bill"** customers in a class separate from Direct
  Debit and pay-on-receipt customers: "Final bill customers are those who are no longer customers"
  (`bad_debt_provisioning.md`). The industry's own books treat a closed account as having left the
  DD population.

**Strong logic (stated belief, near-certain):** an annual DD review sets the monthly amount for the
**coming** year (SLC 27.15, "best and most current information"; see
`what_a_supplier_holds_to_size_a_direct_debit.md` §5). A closing account has no coming year. What
happens to a closing account is settlement: a final bill, a credit refund or one last collection. No
supplier writes to a departing household to say its DD is going up next year.

**What remains unknown (GAP):** what a supplier does when the anniversary falls a few days before a
switch it already knows about. It could suppress the review, or send it and then withdraw it. No
published source covers this. In this model the review is dated at the first bill of the new window.
For these 37 accounts that bill is the final bill, so the question never comes up.

**Decision:** the post-loop chain is wrong for population A. `run_annual_reviews` must not emit a
review dated at the final bill of an account that has left supply. Closure is something a supplier can
know, because it receives the loss notification at the switch or the move-out. The world already
passes it to the bill assembly as `churned_ids`. The loop is right not to tell these households.

## B. The run-end stub: the review is real

For a continuing account, the year in window *w* is complete. A supplier would review at the
anniversary whether or not the simulation is about to stop. Its review uses window *w*'s bills only
(`run_annual_reviews` sums `windows[wi]`), so the short stub does not change the amount. Only the
**date** is an artefact.

**Decision:** the post-loop chain is right for population B. The loop is wrong: `InLoopDDReview.post`
looks up its event at `_month_end(month)` and misses a review dated at the run's last settled day. The
fix is not to match on month alone. That would also find population A's final bills, because the loop
cannot know closure ahead of time. Instead, the loop is told the run's last settled day and looks there
in the month the run ends. A continuing account's bill period ends either at month-end or at the run
end, so those are the only two dates it needs.

## The prediction this note makes (f200, from the saved runs)

The census drops from 846 to 809 events, losing 37 rather than 45. Material rises drop by the leaver
share of the 8. `matched` = 809, `only_post_loop` = 0, `only_in_loop` = 0. One rival could break the
last figure: a leaver whose final bill falls exactly on a month-end. That bill is month-end dated, so
the loop tells it, while the post-loop chain now drops it. If the result shows `only_in_loop` > 0, that
rival is the cause.

**Result (2026-10-13, written beside the prediction).** I applied both rules to the saved
`f200-low-ownbills` and `f200-high-ownbills` runs; the two give identical figures. The census figure was
**wrong**. The post-loop chain drops **46** events, not 37, and ends at 800, not 809. The rival fired:
**9** leavers have a final bill that falls exactly on a month-end and is the first bill of a new year.
Those are 9 of the 95 closed accounts whose last bill falls on a month-end. Before the loop's closure
guard was added, `only_in_loop` came out at 9, as the rival predicted. With the guard: matched **800**,
`only_in_loop` 0, `only_post_loop` 0, material rises **292** in both chains (was 293 / 301), and a
maximum rise gap on matched reviews of 0.0. One caveat: I took closure as "last bill before the run
end", not from the run's own `churned_ids`. The report does not carry those ids under the bills'
namespace. The world's DD4b response was not re-run, so its change is not measured. That change
covers 8 run-end households now told a review and 9 month-end leavers no longer told one.
