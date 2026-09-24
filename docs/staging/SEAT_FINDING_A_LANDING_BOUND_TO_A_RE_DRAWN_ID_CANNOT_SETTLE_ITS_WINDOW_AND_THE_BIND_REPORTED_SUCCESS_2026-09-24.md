**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — a landing bound to an id that has since been RE-DRAWN cannot settle the row, and `--landed` reported plain success

Drawn as `bind-the-refuted-knee-draw-to-the-commit-that-actually-landed-it`. The item was a Lane 0
steer promoted from rank 5 after going undrawn twice, and its whole content was one command:

> Run `python3 -m background.delivery_lane --landed the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term --commit 3b01193a8`.
> … Finished when the row stops appearing in the brief's `lane_0_drawn_never_landed` block.

The command ran, succeeded, and the row did not stop appearing. That is the finding.

## The premise, re-measured at draw

**Not spent, and the instruction was right.** `3b01193a8` ("the refuted bill-stress term is bounded
to the only published measurement of distress-driven switching", 2026-09-23 17:54:15 +0100) is an
ancestor of `origin/main` and touches `company/crm/churn_model.py`, one of the claim's own named
paths. The draw ledger row held `last_landing_at: null`. The bind was owed and has now been made:
five paths bound, exit 0.

The path check's `already landed` annotation on `company/crm/churn_model.py` is expected and is not
a reason to skip: this item edits no source file of its own, and that path was evidence, not a
subject.

## What the instruction could not have known, and what it cost

The item's duplicate-work check named
`the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term` as a live claim sharing
this subject. It is more than that. Read off the two stores at 11:37:31:

| instant | what |
|---|---|
| 2026-09-23 10:54:17 | the knee item FIRST drawn (`first_drawn_at`) |
| 2026-09-23 17:54:15 | `3b01193a8` lands the work — 4h20m after that window shut |
| **2026-09-24 11:36:32** | **the knee item RE-DRAWN — a sibling tick holds it right now** |
| 2026-09-24 11:36:43 | this binding item drawn, eleven seconds later |

The binding exists to stop the draw handing a worker tick work that is already done. It arrived
**eleven seconds too late** — the tick it was meant to save had already been dispatched, on the
same cycle. That is the cost of the two undrawn attempts at rank 5, paid in full.

## The mechanism, and why the bind could not clear the row

Two deliberate decisions, each correct alone.

1. `_remember_landing` writes `last_landing_at` as **the commit's own timestamp**, not `now`, "so a
   reader comparing it against a turn's start instant is comparing two facts about git".
2. `drawn_without_landing`'s third clause and `_disposition` both compare against **THIS draw**, so
   that a stale credit cannot silence a new window — a fail-open this lane already paid for once
   (`test_a_stated_disposition_explains_its_own_window_and_not_the_next_one.py`).

Together: `last_landing_at = 1790182455` (2026-09-23 17:54) `<` `last_drawn_at = 1790246192`
(2026-09-24 11:36), so the row stays a miss no matter how correctly the bind ran. Measured, two
hours out, immediately after the bind:

```
the-refuted-bill-stress-knee-... -> not_done
  evidence: asked git for any commit touching ... between 2026-09-24 11:36 and 14:16: none on
  those paths -- BUT THE WORK MAY BE SITTING THERE ...
```

**The remedy the lane prescribes is a no-op on exactly the population it is prescribed for.** An id
is re-offered *because* its landing was never bound; every unbound re-draw pushes the newest window
further past the commit; so the longer a row has been going round, the more certainly `--landed`
cannot clear it — and the caller was told `bound 5 path(s)`, exit 0, and nothing else.

## Disposition taken

`--premise-spent` is the only per-window disposition, so it is the only thing that could answer the
2026-09-24 window. Stated, with its reason, and re-measured:

```
the-refuted-bill-stress-knee-... -> premise_spent
  evidence: 3b01193a8: ... this window opened 2026-09-24 11:36, 17h42m AFTER that landing, so
  there was nothing left to deliver on.
```

The row still *appears* in `lane_0_drawn_never_landed` — the block is every closed window, and the
disposition is the column that says which kind. **The item's done-means ("the row stops appearing")
is unreachable by any command available to this seat**, because only a landing stamped inside the
current window can remove a row, and the work is already done. `premise_spent` is what "finished"
actually looks like here, and it is recorded as such rather than the residual `not_done`.

The sibling's live claim on the knee item is **left alone**: it is held by a concurrent writer that
may be mid-turn, and retiring it under them is not this seat's call. The disposition is a reading,
takes no claim and restarts no deadline.

## The one leg shipped

`background/delivery_lane.landing_predates_this_window`, printed by `--landed`'s success branch:

```
bound 5 path(s) to <id>: ...
BUT IT DOES NOT SETTLE THE CURRENT WINDOW: 2026-09-23 17:54 (the commit) predates 2026-09-24
11:36 (this id's latest draw), so `drawn_without_landing` still counts this row a miss and the
seat will be offered it again. If the work is done, state the disposition: python3 -m
background.delivery_lane --premise-spent <id> <commit> '<why there was nothing left to deliver on>'
```

Exit stays 0 — the binding *did* happen and must not be retried; what was owed is a sentence, not a
failure. It goes quiet once a landing inside the window arrives, and once a disposition has been
stated for this window, so it is keyed to the property rather than to today's ledger.

`tests/background/test_a_bind_that_cannot_settle_its_own_window_says_so.py` — six controls,
seven mutations each proven to fire, including the production-caller chain (`--landed` itself must
reach the sentence; every other leg stays green while no caller asks). One correction is kept
beside its claim there: the first draft's unreadable-ledger leg was an **equivalence**, because
`seat_work_in_hand._load` already answers `{}` for unreadable, so the bytes never reached the
`except` the test named — the third cause of a green mutation.

## What is NOT fixed, and is the next item

The draw still had no way to notice that an id's own work was on `origin/main` before it handed the
id out. `--premise-spent` is written by hand, after the fact, by whoever happens to look. The
reading that would have stopped the 11:36:32 dispatch — *does a commit on this row's named paths
already sit on `origin/main`, newer than the last thing bound to it?* — is the same git join
`_landed_unbound` already runs on the way OUT. Nothing asks it on the way IN.
