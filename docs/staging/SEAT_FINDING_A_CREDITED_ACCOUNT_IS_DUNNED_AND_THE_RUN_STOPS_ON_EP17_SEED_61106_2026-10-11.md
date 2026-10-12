# A credited account is dunned, and the run stops on EP17 seed 61106

**Fate (2026-10-12, clear-the-decks):** ATOM -- domain question: open-item view (gross overdue) vs ledger (net) disagree on credited accounts; seed worked around, not fixed (P2)

**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** unassigned · **Atom:** `unminted`

Filed by the scale lane, 2026-10-11, from the founders-only seed family at origin `bf238e2bf`.

## What happened

The founders-only book on authorised seed 61106 (400 founders, no win settled) stopped inside the
settlement loop:

    company.compliance.domain_invariants.DunningOfAClearedDebtError:
    ACC-OCC-a8040dab0992 reminder_2 on 2019-02-11 with the ledger at GBP -0.0 (cured 2019-02-25)

The invariant did its job. The defect is in what it caught: `collections_journey._step` reads
"overdue" off the collections view (`arrears_engine.collections_view`: `max_days_overdue > 0`
and `undisputed_overdue_gbp > 0`), and the invariant reads the ledger's rolling balance. Under
open-item accounting the view sums overdue ITEMS gross, while the balance nets credits. So an
account holding an overdue bill and a credit of at least the same size is "overdue" to the
journey and owes nothing on the ledger. The journey stepped to reminder_2, and the cure came 14
days later, at the journey's next mover date.

## Why it is the seat's and not the scale lane's

Which reading is right is a domain question: under SLC 27.16 a credit exists only net of the
contract's arrears, which says the ledger is right and the view should net. I have not changed
it. The account is a change-of-tenancy occupant (`ACC-OCC-*`), the class that also raised two
KeyErrors fixed on 2026-10-10 (`8c3b5c27c`, `a5514d75d`). It has not fired on the default book
or on seeds 61101-61105, 61107. 61106 has been left out of the family, and it is replaced by
61109, so the family does not depend on a seed that runs past it. A replacement chosen because it
runs is a selection, and the read-out says so.

## To reproduce

    python3 -m tools.seed_family member --shape founders_only --seed 61106 --out /tmp/x

About 45 minutes. Log: `/var/tmp/longjob-seed-family-fo4-61106.log`.
