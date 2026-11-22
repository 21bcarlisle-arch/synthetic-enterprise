# A credited account is dunned, and the run stops on EP17 seed 61106

**Fate (2026-10-15):** ATOM -- folds into `EP4_collections_journey` (re-pointed 2026-10-15; an ATOM fate names its atom).
**Fate (2026-10-12, clear-the-decks):** ATOM -- domain question: open-item view (gross overdue) vs ledger (net) disagree on credited accounts; seed worked around, not fixed (P2)

**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** unassigned · **Atom:** `EP4_collections_journey`

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

## Resolution (2026-11-22, delivery seat): the cause was a re-judged step, not an un-netted view

Second occurrence: `ACC-SYN-2016-239 reminder_2 on 2020-12-15 with the ledger at GBP -22.53 (cured
2020-12-16)`, book 61118 at the s.12g pin, 2h21m in (`/var/tmp/longjob-value-test-cut012-new-book.log`).

**The diagnosis above was wrong for this shape.** A residential account is balance-based, and every
view `collections_snapshot` can take for one (`age_balance`, `level_shortfall`, `age_left_level`)
already nets the ledger balance: none returns an item when the balance is a penny or less. The
evidence is in the error itself. `CollectionsJourneyDesk._step` runs the refusal straight after
every step, so the reminder_2 on 12-15 was refused-or-passed on 12-15, and it passed: the ledger then
owed. The message names a cure (12-16), so it was raised at the cure step, a day later. Between the
two refusals a credit value-dated on or before 12-15 was posted after the walk had passed 12-15,
and the cure handed the WHOLE journey to the refusal again, which re-read 12-15 on the revised
ledger. Seed 61106's message has the same shape (reminder_2 on 02-11, raised at the cure on 02-25).

**Fix (company/billing/collections_journey.py, `_refuse_issued`).** Each step is judged once, on
the ledger the desk held when it issued it: the refusal reads the stages issued at this step (and
any cure). A step issued on a ledger that already reads cleared still raises. What the re-read
would have refused is not dropped: it is recorded in `steps_cleared_after_issue` when the journey
cures. A supplier's ledger takes back-valued cash routinely (a bank's value date precedes the day
the file arrives), so a reminder sent before the credit was known is lawful on what was held.

**Controls** (`tests/company/billing/test_a_step_is_judged_on_the_ledger_it_was_issued_on.py`):
the late-credit control reproduces the production error verbatim with the guard removed (mutation
run 22 Nov: 1 failed, 2 passed); an account still in arrears still climbs to reminder_2 and the plan
offer; a step issued on an already-cleared ledger still raises.

**Not established (named gap).** Which posting crossed late on ACC-SYN-2016-239 was not traced: the
triad's `_walk_bound` promises the ledger complete to each walk's `through`, and this shows that
promise broken somewhere (a held lump settlement, a second leg, or a desk-posted instalment are the
candidates). It no longer stops a run; how often it happens is now countable in
`steps_cleared_after_issue`, which no run summary publishes yet.
