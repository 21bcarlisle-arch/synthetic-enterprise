**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `twenty-three-published-feeds-cannot-be-checked-against-their-generator`

# A feed's git stamp is not a description of what produced it, so no standpoint reproduces it

*Pre-registration, written before each of the two measurements:
`SEAT_PREREG_WHETHER_THE_FOUR_GIT_IDENTITY_FEEDS_DIVERGE_ONLY_AT_THE_KEY_THE_ITEM_NAMES_2026-09-19.md`.
Two of its nine predictions are refuted and both refutations changed the design.*

---

## The drawn item's premise, and what is left of it

The item: four feeds — `capabilities_door.json`, `evidence.json`, `phases.json`, `value_arms.json` —
*"whose only outside-the-commit input is the live git log"*, sharing *"a single shared shape"*, each
divergent at one named key, promotable by separating the recorded provenance from the measured
content. That was inherited from the 2026-09-19 sweep and never re-asked. Re-asked, it is wrong in
three ways, and each one costs a different piece of the remedy.

**1. It is not one shape. It is four.** Measured at HEAD:

| feed | diverges at | the input that is not in the commit |
|---|---|---|
| `phases.json` | `total_commits`, **and `commits_by_day[94][1]`** | the live git log, at two paths not one |
| `value_arms.json` | `publishing_tree_commit` ×2, **and `reading` ×2** | the identity, *threaded into published prose* |
| `capabilities_door.json` | `git_commit`, **and `/scale/figures[0]/as_of`** | **another committed feed**, `customers.json` |
| `evidence.json` | `git_hash`, **and `test_functions`, `suite/test_count`, `suite/timestamp`** | **a gitignored suite-collection artefact** |

Two of the four have a second outside-the-commit input that is **not the git log at all**. The
item's literal remedy — exclude the four named keys from the comparison — promotes **zero of four**,
not the four it was drawn for.

**2. The feeds do not agree on how to record where they came from.** Over all 61 published feeds,
asking which record a commit of this repository reachable from HEAD: 39 record none, 17 record
exactly one, and 5 record between 2 and 40. `value_arms.json` records **fifteen** — which tree each
floor leg ran on, which commit a bias was measured against, which commit a pre-registration was
written at. Those are its *subject*. `phases.json` records **none**: a commit count, no sha. So
"read the commit it was published at out of the feed" is answerable for two of the four and
meaningless for the other two, and any rule that picked one sha out of fifteen would be choosing
arbitrarily among content while looking like provenance.

**3. And the stamp the two do record is not true of their contents.** This is the finding.

## The finding

`generate_capabilities_door` stamps `git rev-parse HEAD` into `git_commit`, and reads
`site/data/customers.json` **off the working tree**. In this shared tree several lanes hold dirty
copies at any moment, so those two describe different states of the world. Standing in a clone
checked out at `be7311e35` — the commit the published feed itself names — and regenerating:

```
DIVERGES_AT_ITS_OWN_COMMIT  capabilities_door.json  at be7311e35aa403a699b8b813175cd21c58968b2a
    /scale/figures[0]/as_of | 2026-09-19T06:53:33Z -> 2026-09-19T04:39:13Z
```

`git_commit` comes right — standing at the recorded commit *does* repair the git identity, which is
the half of the item's premise that survives. `as_of` does not, and cannot: the published feed read
a `customers.json` **newer than `be7311e35` ever committed**. `be7311e35`'s own committed
`capabilities_door.json` records a third commit again (`3d5fc9a60`) and a third `as_of`
(`02:20:23Z`), which is the same defect one publication earlier.

**There is no commit to stand at that describes these inputs, because the inputs were never a
commit.** A stamp of `HEAD` beside content read from the working tree is a provenance field that
names a state the generator did not read. It is not a comparator problem and no comparator can
repair it.

That is a sharper defect than the SLC-27B one this control family was built for. SLC-27B was a
published byte disagreeing with its source. This is a published feed **asserting its own
provenance falsely** — and asserting it in the one field a reader would trust to settle exactly
that question.

## The predictions, kept beside the result

| # | predicted | outcome |
|---|---|---|
| 1 | all four `DIVERGES`, none nondeterministic | **CONFIRMED** |
| 2 | at least one diverges on more than its named key | **CONFIRMED** — three of four do |
| 3 | `phases.json` also at `commits_by_day` | **CONFIRMED** |
| 4 | `value_arms.json` at `short`, `produced_by_the_tree_it_publishes_from`, `reading`, `objective` | **PARTLY** — `reading` yes (prose carrying the short sha), the booleans and the `objective` block no: the blob comparison read the same answer at both commits |
| 5 | `capabilities_door.json` and `evidence.json` diverge at their named key **alone** | **REFUTED** — the reason I gave (a single subprocess call with no downstream reader) was true of the *stamp* and told me nothing about the rest of the generator. I checked the producer of the named key and inferred the feed. |
| 6 | the literal remedy promotes at most 2 of 4 | **CONFIRMED**, and worse: 0 of 4 |
| 7 | `capabilities_door.json` reproduces exactly at `be7311e35` | **REFUTED** — and this is the finding. I predicted `as_of` was a function of that commit because it is read from a committed feed. It is read from the working COPY of a committed feed, which is not the same thing, and in this tree routinely is not. |
| 8 | `evidence.json` still diverges at `/suite/*` there | **CONFIRMED** |
| 9 | the mechanism promotes `capabilities_door.json` and not `evidence.json` | **REFUTED** — it promotes neither |

Predictions 5 and 7 are the pair worth keeping: both were wrong the same way. I reasoned from the
*producer of the key the item named* to a conclusion about the *whole feed*, twice, and both times
the rest of the generator had an input I had not looked at. The item's premise had the same shape,
which is presumably where I caught it from.

## What was built, and what it is worth given it promotes nothing

`tools/published_feed_regeneration_check.check_at_its_own_commit` — stand at the commit the feed
itself records, regenerate, compare against the published bytes. The standpoint is **observed** from
the feed by `recorded_publication_commit`, never passed in, and it refuses in both directions rather
than guessing: no commit recorded is *"it has not said"*, more than one is *"which is standpoint and
which is subject cannot be told apart from the bytes"*. The whole candidate sweep costs 15s.

Its verdicts are deliberately spelled differently — `AGREES_AT_ITS_OWN_COMMIT`, not `AGREES` —
because it answers a strictly weaker question: *were these the bytes the generator produced back
there*, which catches a hand-edit made after publication and is **silent about staleness**. A merely
stale feed agrees here. Sharing the word with `check()` would let a caller that switched on the
verdict read the weaker claim as the stronger one.

It promotes nothing today, and `COVERED_AT_THEIR_OWN_COMMIT` is empty on purpose with the measured
reason recorded beside it. The empty set is never the evidence:
`test_a_feed_checkable_at_its_own_commit_is_promoted` asserts over the **candidates** and reds the
day one starts reproducing — which is the day somebody fixes a generator to stamp what it read. So
the instrument marks the completion of the work it cannot do itself, and the finding above is what
that work now is.

## What this makes the next piece, ahead of the remaining 21

The item asked for the four cheapest of 23. The measurement says the four are not the cheapest and
are not one shape. The thing all four share is upstream of all of them:

**A generator that stamps `git rev-parse HEAD` beside content it read from the working tree is
publishing a false provenance field.** Fixing that is one helper and a control — a feed records the
commit *and* whether the bytes it read at that commit were the committed ones — and it is what makes
`capabilities_door.json` checkable, `value_arms.json`'s fifteen-sha ambiguity resolvable by a single
reserved key, and the same question askable of the other 19 without re-deriving it each time. It is
not filed as a gap here; it is filed as the next item, because a defect that publishes a false claim
about provenance outranks extending coverage over feeds whose provenance we would then trust.

`phases.json` is separately worth noting as the one feed of the four that is **honest and
uncheckable**: it records a commit count, not a sha, so it never asserts a provenance it cannot
support — and there is correspondingly nothing to stand at. A reserved stamp would make it the
cheapest of the four to promote, not the hardest.
