**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# The ledger draws a payer's outcome on bills the engine never asks them for

*Worker, 2026-10-15, left over from `the-live-books-ledger-and-pnl-write-offs-disagree-for-48-accounts`
(see `done/WORKER_FINDING_THE_LIVE_BOOK_S_LEDGER_AND_P_AND_L_DISAGREE_ON_WRITE_OFFS_FOR_48_ACCOUNTS_2026-10-15.md`).*

**Measured.** On `run_output_2248e3baf`, 695 of 39,075 bills carry `occupier_share + void_owner_share
>= 1`. These are B7 change-of-tenancy and void windows, booked as occupier debt or owner charge.
`arrears_engine._resolve_bills` skips them: no named payer is asked for them. A further 186 are partly
the occupier's. The ledger now takes every other bill's outcome from the engine. For these 695 it
still draws one, so the named payer can show a failed DD, notices and a `BALANCE_OPEN` case for money
the supplier never asked them for. None can be written off, so the write-off control cannot see them.

**Next:** count how many of the 695 render a failed or disputed case. Then decide what the
household-facing ledger should show for a bill that belongs to the occupier: the occupier's own
account, or nothing on the payer's. The decision follows from B7's design, not from this count.
