**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `contain-the-site-pipeline-so-a-test-cannot-publish-a-degraded-feed-set`) · **Class:** controls_that_cannot_fail

# FINDING — the unguarded-ledger-writer ratchet has been red at HEAD for two weeks, and its own message says not to do the easy thing

Found on the way to the site-pipeline containment work: `tests/background/test_live_ledger_guard.py
::test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed` is **red at HEAD**.

```
AssertionError: the un-guarded observability-writer population GREW to 86 ... assert 86 <= 74
```

## It is not the current lane's

Proved rather than assumed, because a red that refuses a landing is very often pre-existing. The
census was run over `background/` extracted clean at HEAD (`git archive HEAD background`) and over
the working tree, with the same predicate functions:

```
HEAD      86
WORKTREE  86
```

**Identical.** This turn's changes (an import and a guard call in `process_run_complete.py`, a new
function in `live_ledger_guard.py`) are neutral to this census — neither adds an unguarded
observability writer.

## How long

The bound was last set to `74` in `18e8d215e` (**2026-08-26**). It is now 86. **Twelve unguarded
observability writers have landed in the fourteen days since and nothing went red anywhere a lane
could see it.** The repository has been committing normally throughout — five commits on
2026-09-09 alone — so whatever test selection the publish gate runs is not selecting this file.
That is the part worth keeping: *the ratchet did not wedge anything, which is why nobody noticed it
had stopped ratcheting.*

It is present in `docs/observability/head_red_observed.json` and **absent from
`head_red_baseline.json`** — so it is an observed red that was never accepted into the baseline
either. It is unregistered in both directions.

## Why this is BLOCKING and not RECORDED

The guard this ratchet watches is the one that stops a test process overwriting a published
measurement. Its incident of record is a 276-invoice fixture book replacing a 1600-invoice
population and republishing the public Proof door's payment gap **2.68x too low**. A ratchet over
that population which has been silently 12 writers behind for two weeks is not a bookkeeping
discrepancy — it is the control that was supposed to notice the class growing, not noticing.

## The trap, which is why this is a finding and not a fix

The test's own failure message says:

> *"widen `live_ledger_guard` rather than this bound, which is now a move that actually lowers this
> number"*

**Raising `74` to `86` is the wrong move and the message names it in advance.** It banks the drift
and re-arms the ratchet at a number nobody chose on purpose, and the next reader inherits a bound
with no argument behind it. The right move is to work the 86 down by guarding the writers — the
list is in the failure output, fully enumerated, and `process_run_complete.py` alone contributes 14
of them.

Deliberately **not** done in this turn: it is a separate subject from the site-pipeline
containment, it is a dozen-plus writers of work, and doing it here would have hidden it inside a
commit about something else.

## What is next

1. **Do not raise the bound.** If a lane needs this green to land, that is a fact to state, not a
   reason to bank 12 writers of drift.
2. Guard the writers the failure output already enumerates, `process_run_complete.py`'s 14 first,
   and let the bound fall out of the work rather than be set to meet it.
3. **Separately, and cheaper: find out why nothing selected this test for two weeks.** A ratchet
   that goes red at HEAD and blocks nothing is the more general defect here, and it is not specific
   to this file — the same silence would cover any other ratchet in `tests/background/`.
