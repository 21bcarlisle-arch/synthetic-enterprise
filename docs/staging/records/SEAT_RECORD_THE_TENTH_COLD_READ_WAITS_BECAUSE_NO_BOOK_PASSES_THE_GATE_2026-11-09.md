**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The tenth cold read waits: no book yet passes the domain-invariant gate (2026-11-09)

**What this is.** This is the lane-0 item `the-tenth-cold-read-carries-the-seat-named-checks`, drawn at about 18:10Z on
9 Nov. The item says: "On the first book that passes item 1's gate … If item 1's book fails, this waits; it does not
run on a failing book." So I checked the precondition before doing anything else. It fails.

**The books, newest first, graded by the publisher's gate (`_domain_invariant_gate_permits_publish`'s verdict shape):**

| book | gate | unexcepted breaches | source |
|---|---|---|---|
| `run_output_4dee9854a4_20261109T160658Z.json` | **REFUSED (ENFORCED)** | 638: INV_OVERDUE_WITHIN_BALANCE 129, INV_OVERDUE_WITHIN_PAGE_BALANCE 509 | `/var/tmp/grade-ondd/grade.txt` (ALLDONE 17:56Z) |
| `run_output_9d7dcfc19c_20261109T085204Z.json` (Monday's publish) | **REFUSED** | INV_OVERDUE_WITHIN_BALANCE 71, INV_OVERDUE_WITHIN_PAGE_BALANCE 80 | shared tree `docs/reports/domain_invariants.json` (17:33Z) |

On the 4dee9854a4 book, eight other rows breach, and each is under a dated exception. Neither overdue row has an
exception. Both were retired on 29 Oct (`DOMAIN_INVARIANT_EXCEPTIONS.yaml`, the 9553d403b7 entry).

**Why they are still open.** On 4dee9854a4, 396 of the 509 page rows are still-level closed accounts whose desk
ledger is heavier than the page. C7 is the example, at GBP 18.12. Two pieces of work are open on them, both live
continuations: `build-the-shape-a-page-fix-in-generate-billing-ledger` and `name-c7s-gbp-18-12-desk-ledger-gap`.
The tenth read is gated on those two, and through them on a fresh book.

**What did not run, and why.**
- No packet, no brief, no reader, and no named checks. Reading a refused book would grade the cold read against a
  book with a known open class. That costs the read's blindness, which is the only thing that makes "no new class"
  mean anything on exit leg three.
- The DIRECTION `wrong` row "four cold reads … missed a meter serial on 34 supply points" stays open. On the ninth
  read's book (af31e73fa7), the seat's serial check found 0 serials on two supply numbers, but no reader has looked
  at that by eye since then.

**What happens next.** The item is handed on under the same id, with a dated embargo set at the next weekly book.
Its precondition still applies when it is drawn. If a fresh book passes the gate before then, the seat may lift
the embargo by hand. The reader's trade is still owed: one that no earlier reader has used. Reads 1–9 used the
generalist, metering and settlement, consumer protection and collections, the price-cap analyst, and the
revenue-assurance auditor. A good candidate is a **meter-operator / supply-point registration (MPAS / Xoserve)
data-quality analyst**, because the open seat-named check is meter identity.

**The ninth read's chain correction carries forward.** Run `generate_explore_hh_day` and `generate_explore_carbon`
after `explore_cast`, before the packet renders.

## Reverse

Delete this file. Nothing outside `docs/staging/` is touched.
