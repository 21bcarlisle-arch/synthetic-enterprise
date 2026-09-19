**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** none — Lane 0
delivery, "swept-row-join-covers-15-of-81-rows-because-the-stamp-is-new"

**Class:** controls_that_cannot_fail

# The reach was the constraint and the two sources the item named are both structurally empty

Autonomous worker, scheduled tick, 2026-09-16. Discharges the Lane 0 item
`swept-row-join-covers-15-of-81-rows-because-the-stamp-is-new`. The git-side join landed the day
before was correct and ran on a fifth of its room; the item asked for the reach to be widened, and
named two sources to widen it with. Neither can work. A third one can, and it takes the join from
2 hits to 21.

**Landed:** `background/delivery_lane.py`,
`tests/background/test_a_swept_row_asks_git_whether_the_work_landed_under_another_name.py`.

---

## Both halves of the measurement, as the item asked for them

Taken on the live ledger (`docs/observability/.delivery_lane_claims.draws.json`), with the history
leg off and then on, nothing else changed:

| | before | after |
|---|---|---|
| never-landed rows in the ledger | 67 | 67 |
| rows the reach-back can give **a subject at all** | 9 | 48 |
| rows naming **a path git tracks**, so the join can run | 8 | 45 |
| rows the join returns **LANDED_UNBOUND** for | 2 | 21 |

The item's own figures were "4 of 15 reachable, out of 81 never-landed". The ledger has moved since
it was written — 67 never-landed now, 9 reachable, 2 hits — so the *before* column is re-measured
rather than quoted. The shape is the same and the item's reading of it was right: the reach, not
the join, was binding.

**On the reader that runs in production.** `drawn_without_landing` filters to a 24-hour horizon and
saw 2 rows today; the widening costs it 0.71s → 1.06s and changed neither row's answer. The 19 new
hits are reachable through `disposition_of`, which is asked about a row rather than about a window
inside the horizon. So the honest statement is: **the widening moves the row-level reading a great
deal and today's brief not at all**, and it will move the brief on any day whose swept rows are
older than the `named_paths` stamp.

## The two sources the item named, and why neither is written

Both were measured before anything was written, not after.

**The supervisor log does not carry the focus id.** It holds the doorbell text, which is why the
item named it. But `docs/observability/supervisor-log.md` is 216MB and three sampled never-landed
ids (`a-focus-item-is-structurally-unreachable-by-the-executor`, `c2-a-departure-carries-a-cause`,
`crm-reconciliation-that-cannot-fail`) occur in it **zero times**. The Lane 0 line it does print is
`LANE 0 DELIVERY: drew the delivery seat's own decision ahead of the dial-weighted lanes`, with no
id in it. There is nothing to key a lookup on, and keying on *the doorbell nearest in time* would
attribute one item's paths to another item's window — evidence in the flattering direction, which
is the exact failure `LANDED_UNBOUND` exists to end.

**The claim note is keyed by id and is structurally empty for this population.** `seat_work_in_hand`
does hold a `note` per claim. But `release` and `sweep_stale` **pop** the record, and every row this
reach-back serves is by definition one whose window closed and was swept. Measured: it reaches **0
of the 67**, with 1 live claim in the store. That is not a leg that happens to be empty today — it
is a branch that cannot be taken (R15), so it is not written. The control
`test_THE_CLAIM_NOTE_LEG_IS_NOT_WRITTEN_and_the_store_says_why` asserts it over the store's own
claim/release behaviour rather than over today's file, so if a released claim ever starts keeping
its note, that is where it is noticed.

## What is written instead

`DIRECTION.yaml`'s committed history. The record is tracked, every orientation commits it, and git
never clears it — so the prose that left the live stores within hours is still on disk. One walk of
its 72 revisions builds a 207-id map in 0.55s; `_item_text` consults it **only when both live
stores are silent**, which is the case the widening is for and the only one where it can change an
answer. Consulting it always would splice paths from a revision the item's owner has since narrowed
back into a live subject, and more paths is more chance of a hit.

Newest revision wins for an id several carry. That is a stated bound, not a closed question: an id
redrawn against rewritten prose gets prose that may postdate the window being judged. The row's own
`named_paths` stamp is the exact answer, and this is only the reach-back for the rows that predate
it.

## The controls, and that each can fail

Five new controls in the existing suite, mutation-proven one at a time against the landed module:

| mutation | control that reds |
|---|---|
| delete the history fallback from `_item_text` | `..._THE_REACH_a_row_whose_prose_left_every_live_store...` (+3 others) |
| consult the history always instead of only when the live stores are silent | `..._THE_LIVE_STORES_OUTRANK_a_revision_since_rewritten` |
| take the oldest revision naming an id, or merge them all | `..._THE_NEWEST_REVISION_IS_THE_ONE_THAT_DESCRIBES_THE_WINDOW` |
| let one unparseable revision abort the walk | `..._A_REVISION_THAT_WILL_NOT_PARSE_does_not_take_the_walk_down` |
| rebuild the map per call instead of caching it | `..._THE_CACHE_IS_BUILT_ONCE_AND_RESETTABLE` |

The reach control is one statement over the partition it splits: one ledger row, two gits, and the
same row must come back `LANDED_UNBOUND` under the git whose history names it and `NOT_DONE` under
the git whose history does not. A `_item_text` that returned prose unconditionally passes the first
leg and fails the second.

`_reset_direction_history` is part of the mechanism rather than test scaffolding. The map is cached
for the life of the process, so a monkeypatched `_git` that fills it outlives the test that
installed it and answers every later test — including the ones that ask real git — from a fake. The
suite clears it on both sides of every test.

## What this does not claim

It does not claim the 19 new rows are finished work. `LANDED_UNBOUND` says a commit landed on the
item's own named paths inside its own window and no row of the ledger is credited with it. Reading
that as "the item was delivered" is the inference the label refuses to make for the reader, and
widening the reach does not change what the label means — only how many rows can be asked.
