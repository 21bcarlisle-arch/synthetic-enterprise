**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (direction item `a-continuation-is-re-asked-before-it-is-offered`)

# Re-asking a continuation by "an origin commit names its id" was refuted once and does not catch its own cited instance

## Premise, re-measured before building (2026-10-25)

The direction item asks `seat_continuation.live()` to drop a row when an origin commit since it was
written names its id or its NEXT, or a live `surgical_land`'s `-m` names it, and to test this on
`knowledge-pack-verification-census` after `4566ce348`.

1. **The cited instance is not that shape.** `4566ce348`'s message never contains
   `knowledge-pack-verification-census`, and its trailer is `NEXT: none -- the 25 Oct steers'
   Knowledge asks are closed`. An id-naming re-ask would have offered that row exactly as the draw did.
   What spent it was another lane doing the same ask from the advisor steer, under no id. Nothing that
   reads ids can see that.
2. **Retire-on-naming was replayed and refuted on 2026-10-04** (`8dbb82c53`). Over four days it fired
   on about 12 in-flight rows (hand-offs, progress notes, rivals), some 4.6 h early. Every correct
   firing came within minutes of the holder's own retirement.
3. **Two of the three requested legs are already built, in `delivery_lane` and not in `live()`.**
   `finished_on_origin` (bb250f8ea) refuses a row whose finish is published: a
   `NEXT: none -- direction item <id>, finished` trailer or a `--premise-spent` disposition on
   origin. `_live_landings` reads every running `surgical_land`'s argv. `live()` has five callers
   and four of them only want to know what is queued, so it is the wrong place for git and `/proc`.

## Pre-registration (written before the replay below was run)

Replay over every continuation written in the last 7 days. For each one, list the origin/main
commits that name its id as a whole word, inside its live window (`written_at` up to the earlier of
retirement and +6 h), leaving out the ones `finished_on_origin` already catches. A firing is
**prevented-redraw** if the draw ledger's `last_drawn_at` for the id is after that commit.

- **P1:** the leg fires on at least 5 rows.
- **P2:** at most 1 prevented-redraw firing is a real finish that the existing checks miss. The rest
  are the holder's own increments, hand-offs or rivals.
- **P3 (gap, not a prediction):** a live `surgical_land` whose `-m` names an item's id is read by
  the ledger (`_mid_landing`) but not by the draw. `held_grade` matches only held paths, changed
  identifiers and the holder's own names. That leg is narrow: a landing in flight is a collision,
  whether or not it finishes the item. It is built whatever the replay says.

## Replay result (run at origin/main c67f8dec8, the 1,459-row store, 238 rows written in 7 days)

- **P1 held, by a wide margin.** The leg fires on **62 of 238** rows. Most firings are the hand-off
  commit that created the row ("handed on as the continuation X", "queued continuation X"), often
  0.0 to 0.3 h after `written_at`. Retire-on-naming would kill a quarter of all continuations at
  birth.
- **P2 held.** 23 firings are followed by a later draw. Reading each NEXT line: they are hand-offs
  (`e6-the-arrears-overlay-arm-is-graded` 2cd26acfc, `c30-the-per-account-svt-sender-grades-both-sides`
  aed6ba851), progress increments (`anchor-the-446-bare-world-constants-in-impact-order` 6b2b42b7e,
  `closed-account-arrears-recovered-at-the-gone-household-rate` a8ea44a12), and one example of the
  grammar (`grade-the-per-customer-switches-arms-once-flat-rc-exists` named in a5f9cd768). None of
  them is a finish the existing checks miss. The finishes that do name their id without the exact
  `, finished` trailer (`the-brief-says-none-launched-when-it-read-only-endings`, ea1c46dda) were
  never drawn again, so they cost nothing.
- The replay script is not kept: it is a join of the store, the draw ledger and `git log`, and it
  takes 30 lines to redo.

## What was built, and what was not

- **Built:** the P3 leg in `delivery_lane.held_grade`. A live landing whose `-m` names the item's id
  as a whole word holds it from both draw loops. The control is
  `tests/background/test_a_landing_in_flight_that_names_an_item_holds_it_from_the_draw.py`. It uses a
  real `/proc` process carrying the knowledge-pack row's own text, and checks named, longer-id and
  unnamed in one assertion. All three mutations fire.
- **Not built:** the origin-commit leg, refuted twice now (`8dbb82c53` and this replay).
- **The cited instance stays uncaught, and nothing that reads ids can catch it.** `4566ce348` did the
  steer's ask under the steer's own name, not the row's id. What would catch it is an ask key
  shared by the steer and the row. Continuations carry no such key, so it is a GAP and not a
  defect of this leg. The orientation caught it by reading (retired 15:22Z), which is the
  seat's job.
- **The E6 exposure in the item's WHY** (grade rows offered while their work sat in another lane's
  tree) is the held-work leg's job. The orientation's 21:22 note reads that refusal as having fired
  correctly 11 times.
