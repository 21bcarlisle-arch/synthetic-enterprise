# The own-book method register asks each account's own fuel

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB8_a_households_payment_channel_changes_over_its_tenure`

**Drawn as:** `the-own-book-method-register-asks-each-accounts-own-fuel` (Lane 0). Closes the "Not done"
item in `SEAT_FINDING_THE_SEAM_NOW_FINDS_A_GAS_ONLY_HOUSEHOLDS_STOP_2026-10-04.md`.

## Premise, re-measured at draw

The cited commit (316cacc0a) is on origin and fixed only the seam's gas branch. The caller half was still
live: `run_phase2b._book_method_of` asked `get_payment_method(cid, "electricity", as_of=)` for every resi
account. The duplicate claim the draw named is this item's own id; no rival `surgical_land` was running.

## Change

`_book_method_of` reads the account's commodity off the live roster (`_ALL_KNOWN_CUSTOMERS` plus
`ACQUIRED_CUSTOMERS`, so funnel wins resolve) and asks the seam on that fuel. An id the roster does not
hold is refused by name rather than defaulted to electricity.

At real inputs: 182 roster accounts, all ids distinct and resolving; of the 178 resi, **66 are gas legs**
that were asked on electricity and are now asked on gas.

Control: `test_every_method_read_in_the_run_asks_on_the_accounts_own_fuel` (AST). No
`get_payment_method` call in the run may pin its fuel as a literal or fall to the seam's default, and the
register's own read must exist. Reverting to `"electricity"` reds it (run 2026-10-04).

## Not measured

The run figure this moves is the own-book default belief, which only exists when
`renewal_default_belief == own_book`. The default policy never reads the register, so no default-run
number moves. How far the own-book belief moves needs an own-book run (about 53 min per seed), and I
have not run one. The prediction, written before any run: a gas leg whose DD was stopped now has its
provisions read on the pay-on-receipt row instead of the DD row after the notice, so the DD row's
learned rate falls slightly and the pay-on-receipt row's rate rises. I expect the size to be small,
because only stopped gas legs move.
