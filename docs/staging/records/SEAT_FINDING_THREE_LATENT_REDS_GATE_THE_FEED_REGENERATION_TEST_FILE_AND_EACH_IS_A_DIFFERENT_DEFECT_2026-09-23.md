**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `control_cannot_fail` (primary) · `publish_gate_and_wedge` (secondary)

> **CLOSED 2026-09-23 in `6b4bfdd15`.** All three green, each keyed to its property. Result and the
> measurement that decided it:
> `SEAT_RESULT_A_DISPLACED_CLOCK_SEPARATES_THE_FEEDS_THAT_ARE_A_FUNCTION_OF_THEIR_COMMIT_2026-09-23.md`,
> pre-registered in `WORKER_PREREG_WHAT_A_DISPLACED_CLOCK_MEASURES_ABOUT_THE_COVERED_FEED_SET_2026-09-23.md`.
>
> **AND §1 BELOW IS HALF WRONG, corrected here rather than quietly revised.** The probe's resolution
> is real and is not the binding constraint. The determinism tree is only built when the FIRST tree
> disagrees, so a feed whose committed bytes are fresh AGREES and is never asked the determinism
> question at any resolution — which is what actually promoted `knowledge_review.json`. Widening
> the probe alone would have repaired the half that was not load-bearing. Both are repaired; the
> clock now moves 400 days AND the probe runs on the agreeing path.
>
> A fourth defect turned up while fixing the third and is in the result: one of these very legs read
> `site/data/<feed>` off the WORKING TREE, four tests away from the leg that exists to refuse exactly
> that. The producer defect under §2 is untouched and wants its own item.

# Three latent reds gate the feed-regeneration test file, and each is a different defect

**Claim:** `the-regeneration-check-clones-at-head-so-it-cannot-see-the-producer-edit-that-wedges-the-publisher`
**Found while** landing the second relation kind (`59ccdb550`). Not part of that claim, measured
because it refused the commit, and filed rather than routed around.

## The three, each red at HEAD without any edit of mine

Verified by re-running them against a stashed-clean tree **before** writing a line of the work they
blocked — so none of these is my diff's.

| Test | Why it reds |
|---|---|
| `test_every_covered_feed_is_what_its_generator_produces` | `knowledge_review.json` diverges on `age_days` 24→26, 11→13 |
| `test_a_candidate_standpoint_is_observed_from_the_feed_not_asserted` | both candidates yield `NO_STANDPOINT` |
| `test_a_feed_checkable_at_its_own_commit_is_promoted` | same `NO_STANDPOINT`, same two feeds |

**They are three different defects wearing one refusal, and none is a hand-edit** — which is the
only thing that file's assertions are worded to mean.

### 1. A determinism probe whose resolution is shorter than the period it hunts

`knowledge_review.json` diverges ONLY on `age_days` and the prose that renders it ("Checked 24 days
ago…" → "Checked 26 days ago…"). That feed is not a function of its commit: it reads the wall
clock. The module's membership rule is explicitly *"the feeds that ARE a function of their
commit"*, so it should never have been in `COVERED_FEEDS` — and the reason it got in is the
interesting part.

`NONDETERMINISTIC` is measured by running the generator **twice and comparing**. Two runs seconds
apart produce the SAME `age_days`, because the quantity changes once a day. **The probe's
resolution is shorter than the period of the nondeterminism it exists to detect**, so a
clock-dependent feed reads as deterministic and gets promoted into the covered set, where it is
green on the day it lands and reds two days later. Re-running the generator only buys another day
— a control that must be re-greened daily is not a control.

This is the same shape as a limitation measured and documented during `59ccdb550`: two writes one
statement apart return byte-identical `st_mtime_ns`, so an mtime comparison cannot order them.
**Both are instruments blind to intervals shorter than their own tick, and in both cases the
blindness reads as a clean answer rather than as "cannot tell".**

### 2. A control pinned to the current state, reddening because the code got MORE honest

Both candidates now return `NO_STANDPOINT` with the feed naming its own reason — e.g.
*"records `a8e63a711` but says the bytes it read were not that commit's — read off the working
tree: `site/data/customers.json`, … — standing at this commit will not reproduce this feed"*.

That is the module **working as designed**. Its docstring says so outright: *"a feed published from
a dirty one is uncheckable and now names which input moved."* The provenance stamp was added in
`d181b062d` precisely so a feed could say this. The tests assert every candidate is **graded**, so
the honest refusal fails them.

The tests are not simply wrong — their comment names a real defect they are guarding
(*"checking only that a row came back would make this green by the control's own filters emptying
its evidence"*). Both concerns are legitimate and the current wording cannot hold both. **Keyed to
the property, the distinction is: an ungraded candidate is acceptable iff the feed ITSELF names why
(a `NO_STANDPOINT` carrying a reason out of its own provenance stamp), and never acceptable when it
is unexplained** (`WROTE_NOTHING`, a dead generator, an emptied filter). That preserves the defect
the legs exist to catch and stops them reddening when the tree becomes more honest.

Underneath it is a live producer defect worth its own look: the publisher is publishing those feeds
from a **dirty working tree**, which is why no standpoint exists.

## The reason this stayed invisible until someone touched the file

These sit in the catalogued *"reds on origin/main that no commit's gate selection reaches"* class
(`SEAT_FINDING_ORIGIN_MAIN_CARRIES_SEVEN_REDS…_2026-09-22.md`). Measured here, and it is the
actionable part:

**Editing `tools/published_feed_regeneration_check.py` does NOT select that test file. Editing the
test file selects it.** My first landing attempt edited the test file and was refused by all three;
the identical tool-module change with the new legs in a **separate** file landed clean
(`59ccdb550`). So the reds gate *whoever next edits that file* and are invisible to everyone else —
including to the module's own author making any change to the module itself.

That is why the new relation's legs live in
`tests/tools/test_a_derived_artefact_is_regenerated_when_its_producer_changes.py`. **That separation
is a consequence of this defect and not a design preference**, and it should be revisited once the
three are cleared — though the two files do control genuinely different relations over different
trees, so keeping them apart may survive on its own merits.

## What done means

All three green with the legs keyed to properties rather than to today's tree:
`knowledge_review.json` out of `COVERED_FEEDS` with its wall-clock dependency recorded as the
measured reason (and `test_the_feed_the_defect_happened_on_is_covered`'s `len(COVERED) >= 8` floor
re-derived rather than decremented to fit); the two standpoint legs accepting a self-explained
`NO_STANDPOINT` while still reddening an unexplained one. **Not attempted here** — three defects in
another claim's subject, none of them reachable from the item I hold.
