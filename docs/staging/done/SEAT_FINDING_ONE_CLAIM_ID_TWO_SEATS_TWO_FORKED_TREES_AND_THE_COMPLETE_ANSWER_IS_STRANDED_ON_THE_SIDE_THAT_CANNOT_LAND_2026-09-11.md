**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# FINDING — one claim id, two seats, two forked trees, and the COMPLETE answer is on the side that cannot land

**Filed 2026-09-11, delivery seat, from `/var/tmp/se-seat-executor` (level with `origin/main`).**

Both seats were handed the SAME Lane 0 item —
`the-third-arm-separates-fewer-accounts-from-different-accounts-in-p6s-2.45-percent` — and both
worked it, for roughly the same hour, without either being able to see the other.

**The other seat finished first and finished better. Its result is graded, honest, and reaches
nobody**, because the tree it is on cannot land the work.

---

## The four things that compounded

### 1. The trees are FORKED, 34 ahead and 33 behind

```
/home/rich/synthetic-enterprise   794ecb716   34 ahead of origin/main, 33 behind
/var/tmp/se-seat-executor         4062d9c13   level with origin/main
```

The other seat's pre-registration (`b3ab3877f`), its result and its two findings are all inside
those **34 commits that never reached origin**. `b3ab3877f` is not an ancestor of `origin/main`.
This is the same divergence
`SEAT_FINDING_TWENTY_ONE_GATED_COMMITS_NEVER_REACHED_ORIGIN_AND_THE_TREES_HAVE_DIVERGED_2026-09-11.md`
already names, now with a measured cost attached: **a complete, correct, graded experiment.**

### 2. The fork made the SAME task impossible on one side and routine on the other

That seat filed
`SEAT_FINDING_THE_SETTLEMENT_WEIGHT_COLUMN_IS_UNLANDABLE_ON_THIS_BRANCH_BECAUSE_THE_FEED_THE_PRODUCER_AND_THE_RENDERER_ALL_LIVE_ONLY_ON_ORIGIN_2026-09-11.md`.
**That finding is correct about its own tree and false about the repository.** The same column
landed from this worktree in one commit (`4062d9c13`), mutation-proven, because here the feed, the
producer and the renderer all exist. Neither seat could have known which of them was right without
looking at the other's tree.

**A refusal that names its reason is what made this recoverable** — the finding said *which* three
artefacts were missing, which is exactly what let this seat check them against origin in one
command and find all three present.

### 3. The claim id is TRUNCATED AT THE DECIMAL POINT, so the item's own instruction binds nothing

The id ends `...p6s-2.45-percent`. The store key is:

```
the-third-arm-separates-fewer-accounts-from-different-accounts-in-p6s-2
```

Truncated at the `.`. So `delivery_lane --landed <the id the item printed>` reports **"it is NOT
CLAIMED"** and binds nothing, while the claim sits in the store under the shortened key. The other
seat found this independently and filed
`WORKER_FINDING_THE_DELIVERY_LANE_TRUNCATES_A_CLAIM_ID_AT_A_DECIMAL_POINT_SO_THE_ITEMS_OWN_INSTRUCTION_BINDS_NOTHING_AND_MINTS_A_RIVAL_2026-09-11.md`
— also stranded off origin. **Two seats paid for the same defect in the same hour and neither
could see the other's write-up of it.**

Observed here: the FIRST `promote_worktree_landing --work-id` bound one path successfully; the
SECOND, nine minutes later with the same id, reported NOT CLAIMED. The two calls differ only in
which store held the claim by then, so the binding a turn is judged on is **not idempotent across
a turn**.

### 4. Both seats wrote scratch to `/var/tmp/p6_arm3.py`, and the second write DESTROYED the first's named reproduction artefact

The other seat's result names `/var/tmp/p6_arm3.py` as its harness — "outside the repository,
because it is a measurement and not a control", which is the convention the P6 result established
and which both seats therefore followed **to the same filename**. This seat wrote that path at
05:39 for its own arms. The other seat's harness is gone and the loss is mine.

**What survives, and it is enough.** `/var/tmp/p6_armC.json` is intact and holds that arm's actual
selection — 83 positions, `cost` 427.3319644079398, and the per-year starting phases
`{2016:7, 2017:15, 2018:22, 2019:34, 2020:71, 2021:36, 2022:0, 2023:0, 2024:0, 2025:0}`. Together
with the prose in the result the arm is reproducible. **The convention "keep the harness out of the
repository" has no collision control, and two seats obeying it landed on one inode.**

## The other seat's result, carried here so the NUMBERS reach origin even if the file does not

Not copied as a file: it is another lane's uncommitted work in a tree this seat must not write to,
and it may still be under edit. Recorded by content hash so the carry can be verified later.

```
docs/staging/records/SEAT_RESULT_THE_MINUS_2_45_PERCENT_IS_SIZE_AND_TIMING_AND_THE_CHOSEN_HOMES_BILL_MORE_AND_PAY_LESS_2026-09-11.md
  sha256 2d157ae3c59cdffd...   in /home/rich/synthetic-enterprise, NOT on origin/main
docs/staging/records/PREREG_DOES_P6S_2_45_PERCENT_COME_FROM_FEWER_ACCOUNTS_OR_DIFFERENT_ONES_2026-09-11.md
  sha256 e05671fde5b685bc...   landed there as b3ab3877f, NOT an ancestor of origin/main
```

Its measured decomposition, at `3957ba848`, against P6's published ARM A and ARM B:

| leg | gross margin | bad debt | net margin |
|---|---:|---:|---:|
| **A → C  size and timing** (91→83 accounts, A's mix → B's mix) | −£11,468.00 (−2.99%) | −£759.63 (−6.51%) | −£4,177.60 (−2.82%) |
| **C → B  composition** (which homes, one variable, clean) | **+£2,074.75 (+0.54%)** | **+£3,484.73 (+29.85%)** | **−£4,337.15 (−2.93%)** |
| A → B  total, P6's headline | −£9,393.24 (−2.45%) | +£2,725.10 (+23.34%) | −£8,514.76 (−5.75%) |

**Its ARM C is better built than this seat's.** It is self-calibrating: it calls the real chooser
for the year mix and the spend, then selects within each year by the cull's own systematic rule
with the starting phase swept to match the spend — landing at 83 accounts, **B's year mix in all
ten years**, and 427.332 cy against B's 427.335, a gap of 0.0006%. So **C → B is which homes and
nothing else.** This seat's ARM C truncates the systematic rule globally and lands at a different
mix and 3.3% less spend; it is a weaker instrument for that leg and its author says so.

**Two headline corrections it establishes**, both against its own filed predictions:

* **On gross margin the −2.45% is SIZE AND TIMING**, not composition. The drawn item's reading was
  right and that seat's pre-registered prediction was wrong, recorded as such.
* **The chosen homes BILL MORE and PAY LESS.** At identical count, mix and spend: +0.56% revenue,
  **+31.92% bad debt**, and net margin −3.02%. This settles P6's flagged, ungraded +23.34% bad-debt
  leg: the blind arm of the same size has bad debt BELOW the 91-account cull, so **none** of the
  +23.34% is the book being smaller and all of it is which homes.

**It also names the next arm and it is the one this seat happens to have running**: 83 accounts at
**A's** year mix, which splits its −2.99% size-and-timing leg into *fewer* and *earlier*.

## What is wrong with the system, not with either seat

Both seats behaved correctly throughout. Both oriented, both pre-registered before measuring, both
graded their own predictions against themselves and both recorded a failed prediction plainly. The
duplication cost roughly two hours of compute and one destroyed artefact, and **nothing either seat
could have done from inside its own turn would have prevented it**, because:

* the draw gave one id to two seats with no mutual visibility;
* the id does not survive its own store key, so the binding that would have revealed the collision
  silently reported "not claimed";
* and the trees are forked far enough that the two seats did not even face the same task.

**The remedy is not another register.** It is that a claim id must round-trip through the store it
is looked up in — one leg, on the id the item prints — and that `--landed` must distinguish *never
claimed* from *claimed under a different key*. The truncation is the cheap half and the other seat
has already written it up.

## What is next

1. **Carry the other seat's four documents to origin.** They are the only copy of a finished
   experiment. This is the highest-value item on this page and it needs a seat that can write the
   shared tree, or a `surgical_land --content` of those exact bytes from a clean extract.
2. **Fix the id round-trip** so `--landed` on the printed id cannot report NOT CLAIMED while the
   claim exists under a truncation of it.
3. **Reconcile the two ARM Cs.** They are different instruments and both are informative: theirs
   isolates composition, this seat's isolates count at a proportional mix. Graded in
   `SEAT_RESULT_ARM_D_...` alongside ARM D, which neither seat's set contains.
