**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — a fourth door carries the same narrow read, and widening it would manufacture six false
spent premises

**Filed:** 2026-09-22, after `0b1898452`/`14dc33969` landed the `path_note` widening.
Pre-registration:
`docs/staging/records/SEAT_PREREG_DOES_WIDENING_THE_PREMISE_NOTE_GAIN_MORE_REACH_THAN_IT_SUPPRESSES_2026-09-22.md`.

## The trap

The drawn item said `path_note` was *"the only one of the three path doors still reading a narrower
field set than the canonical one"*. True — **of the path doors**. Grepping the narrow literal at
`origin/main` after landing still finds it at `background/delivery_lane.py:3372`, inside
**`premise_note`**: a fourth door, same hand-rolled `what + why`, subject is cited **commit SHAs**
rather than paths.

It now sits one screen above a function that was just widened for looking exactly like it. **The
next session to grep that literal will read it as an unrepaired instance of a defect this project
has already fixed, and the fix is wrong.**

## Why it is wrong, measured rather than argued

`premise_note` fires only when **every** commit an item cites has reached `origin/main` — the
property being *"nothing this item points at is still outstanding"*.

`what`/`why` is where an item states what it **depends on**. `done_means`/`note` is where it states
**criteria, anchors and completion markers**. All 11 live continuation entries citing a SHA only in
the later fields cite one of those three kinds, and **not one** cites a dependency:

| entry | the later-field citation |
|---|---|
| `the-selection-leg-is-negative-...` | "Parts TWO and THREE are **DISCHARGED in commit 96ec173c0**" |
| `restore-the-six-live-reverts-...` | "the census fail-open **closed in 37138c44f**" |
| `the-branch-half-of-the-multi-home-sweep` | "12 unjudged here-relative strings **at 9e9f4d994**" |
| `read-the-next12-twelve-alone-...` | "producing_commit **must read a178b56d6**, and if it reads **7da627b90** that Finding is struck" |

A completion marker **has arrived by definition.** Folding it into `all arrived` makes the condition
trivially true and publishes *"The work may have landed by another route… RE-MEASURE THE PREMISE…
release the claim rather than doing the work twice"* over an item whose work has not started. That
is precisely the false positive `premise_note`'s own docstring was designed against.

## My own prediction was confirmed as a count and refuted as a conclusion

Pre-registered P1: *"gain exceeds loss — more entries acquire a premise note than lose one."*
Measured: **6 gain, 1 loss, 4 unchanged.** The count is confirmed. **The conclusion it was standing
in for is wrong**, and the reason is this project's own recurring lesson — *before dividing two
numbers, say what each one counts*. I was counting **verdict flips**, not **correct verdicts**. All
six "gains" are false positives, and the one "loss" is the door correctly declining to treat a
grading criterion as a dependency.

P2 (*the loss is not zero*) confirmed. P3 confirmed in substance and improved on: I predicted the
right shape was to widen the search and keep the verdict narrow. The measurement says something
simpler — **there is nothing worth widening the search for**, because no later-field citation in
the live population is a dependency at all. The narrow read is not a gap; it is the correct scope.

## A control that stubs its own subject, caught by the leg written against it

The first draft of the guard stubbed `dl._git` to answer only `merge-base --is-ancestor`. But
`_cited_commits` confirms each token with `cat-file -e` **first**, so the stub yielded zero cited
commits and `premise_note` returned `""` — the assertion passed **for the reason it was testing
for**. The second leg (`!= ""`, the door is not simply dead) reds on that stub and caught it. Both
legs are kept, and the stub comment records why.

## What landed

* `background/delivery_lane.py` — `premise_note`'s docstring now names the widening it must refuse,
  with the measurement and the wrong-ruler correction.
* `tests/background/test_two_ids_for_one_piece_of_work_are_named_at_the_draw.py` —
  `test_PREMISE_NOTE_STAYS_ON_WHAT_AND_WHY_AND_MUST_NOT_BE_WIDENED_WITH_THE_PATH_DOORS`.
  Mutation-proven: widening `premise_note` to `_ITEM_PROSE_KEYS` reds it, and the failure output is
  the spurious note itself.

## Residue

None in this family. The three path doors read the canonical tuple and are guarded; the fourth door
reads the narrow pair, and is now guarded against being "fixed".
