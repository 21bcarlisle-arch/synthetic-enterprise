# A landed SEAT_RESULT spends its prereg's grading premise — 2026-09-28

**Item:** `a-landed-seat-result-spends-its-preregs-grading-premise` (Lane 0).

## What changed

`background/delivery_lane.py` has `prereg_result(text, written_at)`. It finds each
`SEAT_PREREG_<stem>_<date>.md` named in the text and asks origin/main for any
`docs/staging/*SEAT_RESULT_<stem>_*.md`. It returns the commit that first put that result there.
It is read in two places:

- **The draw** (`next_item`, both loops) skips an item whose prereg already has a result. Like an
  embargo, it skips that item and keeps walking the list.
- **`_disposition`** reads a closed window as `premise_spent` when the row's `named_paths` hold a
  prereg whose result landed **before** that window opened. A result that lands inside the window
  is that window's own work, and the unbound-commit join still credits it.

Two things keep the rule from firing too often:

- **A result older than the item's `written_at` is context, not a spent premise.** The writer
  already had it in view.
- **Only an exact stem matches.** Many results are named for their outcome and will not match.
  A miss hands the item out as before, so it costs a tick and never silences work.

Control: `tests/background/test_a_landed_seat_result_spends_its_preregs_grading_premise.py`. Its
first test covers both branches: the spent head is skipped and the unresulted C1-bracket tail is
still handed out. Five mutations were run and each one made exactly one test fail.

## The live rows

- `grade-the-balance-rule-two-state-diff-against-the-cefd2c04a-baseline`: the derived reading
  gives `premise_spent` with 7dc8f150d. I also stated it by hand with `--premise-spent 7dc8f150d`.
- `the-billing-ledger-and-the-pnl-book-one-write-off`: **`--landed fcba478b7` refused**, because
  the id is not claimed and nothing holds a deadline to bind to. That is how the door is designed
  to behave, so I did not force it. The closed window reads `landed_unbound` →
  `05f9acf79` ("an open failed bill that account credit has netted in part…") on the row's own
  three subject paths. The item's premise was that the row read as a miss, and it no longer
  does. The earliest hit is 05f9acf79, not fcba478b7. The likely reason is that fcba478b7 is
  bound to another row, which `_landed_unbound` declines by design; I did not re-derive this.
