**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — found in passing

# Two home-move controls are red at HEAD, refused by the live-ledger guard, and the pre-commit selection never asks them

**Found 2026-09-19 by the delivery seat, in passing, while running the whole of `tests/simulation`
as a cross-check on an unrelated landing (claim
`the-svt-household-has-no-route-back-to-a-fixed-term`).** Not my subject and not my defect; filed
because an unfiled red at HEAD is worse than another document in the queue.

## The reds

```
FAILED tests/simulation/test_home_move_undeliverable_win.py::
       test_a_won_home_mover_with_no_successor_still_goes_to_market
FAILED tests/simulation/test_home_move_undeliverable_win.py::
       test_a_won_home_mover_WITH_a_successor_activates_it_and_does_not_go_to_market
```

Both raise `background.live_ledger_guard.LiveLedgerWriteUnderTest`:

> *"`gap_metric.write_gap_entry` refused: this is a test process and
> `docs/observability/coupled_gap_ledger.json` is a LIVE observability record … Pass an explicit
> `ledger_path=tmp_path / "ledger.json"` instead. There is no env-var override by design."*

So the guard is doing exactly its job and the guard is not the defect: these two tests drive a path
that writes the coupled gap ledger without handing it a temp path, and the guard that exists
because a test population once overwrote that ledger and republished the public Proof door's
payment gap 2.68× too low is correctly refusing them.

## Attribution, by swapping ONE thing

Found while my own change was in the tree, so it was not assumed to be somebody else's. The
bytes of `f10e6c643` (HEAD at the time) for `simulation/renewals.py`, `simulation/run_phase2b.py`
and `simulation/renewal_engagement.py` were written over the working copies and the file re-run
alone: **the same two tests fail, identically, 4 passed.** The working copies were then restored.

**WHAT THAT DOES AND DOES NOT ESTABLISH.** It establishes the reds are not caused by the three
simulation modules any lane was editing that evening, and that they predate the landing which found
them. It does NOT re-verify them at today's `aeb8a4970`, which is four commits further on — two of
them in `simulation/renewals.py` and `run_phase2b.py`. The refusal is raised by a ledger write-path
guard with no relation to those modules, so the reds are expected to stand; that is a prediction,
and whoever picks this up should re-run the file first rather than take it from here.

## Why nothing noticed

Pre-commit selection is by subject module stem, so a commit that does not touch a `home_move`
module never asks these two. The gate run that sat beside this finding executed 995 tests and did
not include them. They are only reachable by running the directory, which is what happened here by
accident rather than by design.

## The remedy, named but not taken

Thread an explicit `ledger_path` into the `gap_metric.write_gap_entry` call these two tests reach,
from a `tmp_path` fixture — which is the remedy the guard's own refusal prints. Not done here
because it is another lane's module and this turn's claim is elsewhere; a repair that lands inside
somebody else's subject without their context is how one-line fixes become two-day merges.

## What is NOT claimed

That these are the only reds in `tests/simulation`. The run that found them was `-x`, so it stopped
at the first; everything after `test_home_move_undeliverable_win.py` in collection order was not
executed. **832 passed before it stopped**, and the un-run tail is not evidence of anything either
way.
