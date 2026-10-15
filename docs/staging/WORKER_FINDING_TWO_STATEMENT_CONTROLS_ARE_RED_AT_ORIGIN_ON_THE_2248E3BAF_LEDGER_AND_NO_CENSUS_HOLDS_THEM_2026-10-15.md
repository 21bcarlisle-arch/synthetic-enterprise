**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `D46_the_validator_holds_against_the_varied_population` · **Claim:** none (found while landing `a-held-estimate-is-known-at-assembly-knowledge-and-prereg-first`)

# Two statement controls are red at origin on the 2248e3baf ledger, and no census holds them

**Fate (2026-10-15):** ATOM -- folds into `D46_the_validator_holds_against_the_varied_population` (re-pointed 2026-10-15; an ATOM fate names its atom).

Run on 2026-10-15 in a fresh origin worktree with `monthly_bill_assembly.py` restored to HEAD, so
neither red is the held-estimate change:

- `tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py::test_the_event_walk_closes_where_the_ledger_says_it_closes`
  disagrees with the ledger's closing balance on PROS-2016-0207g (−10.10 vs −3.17), PROS-2022-0327
  (−430.02 vs −389.17), PROS-2022-0327g, PROS-2024-0110, SYN-2016-202, SYN-2016-221, and more.
- `...::test_the_vat_charged_on_every_catchup_bill_matches_the_NET_base_across_the_real_book`:
  "0 bills charge VAT on the corrected base and 2 on neither".

Both read the committed `docs/state/billing_ledger.json`, last written by `ed3dadd9d` (run
2248e3baf). Neither `HEAD_RED_REGISTER.md` nor `head_red_observed.json` names them. This is the same
class as the nine-inversions and stayers findings of 2026-10-14: a test whose data is a published
artefact goes red when a publish lands, and the census never runs it.

**I cannot yet say** whether this is one cause or two. The two VAT "neither" bills could be the held
estimates' catch-ups (11 of them on this book), which this run's statement walk does not see. That is
a guess. Next step: print the two bills' ids and compare them with the 11 catch-up bills in
`SEAT_PREREG_A_HELD_ESTIMATE_IS_KNOWN_AT_ASSEMBLY_2026-10-15.md`.
