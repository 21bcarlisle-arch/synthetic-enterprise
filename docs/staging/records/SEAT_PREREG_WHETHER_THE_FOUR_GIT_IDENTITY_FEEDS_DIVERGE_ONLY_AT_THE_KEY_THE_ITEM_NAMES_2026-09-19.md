**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `twenty-three-published-feeds-cannot-be-checked-against-their-generator`

# Pre-registration: do the four git-identity feeds diverge ONLY at the key the drawn item names?

*Written before reading the output of
`python3 -m tools.published_feed_regeneration_check generate_capabilities_door generate_evidence_data
generate_phases_json generate_value_arms_data --json`. The run was launched first and its output sat
unread on disk while this was written; nothing below was informed by it. The honest statement of that
ordering is here rather than in a footnote, because "pre-registered" is a claim about what I could
see, not about which command ran first.*

## The claim being tested

The drawn item states the four feeds' **only** outside-the-commit input is the live git log, and
names one key each: `capabilities_door.json` `git_commit`, `evidence.json` `git_hash`,
`phases.json` `total_commits`, `value_arms.json` `publishing_tree_commit`. That is a factual claim
about the tree, inherited from the 2026-09-19 measurement, and it is un-re-asked. If it is true, the
remedy is a four-key exclusion. If the identity is *threaded* — read once and then used to compute
other published fields — a four-key exclusion leaves all four still DIVERGES and the remedy has to
separate provenance at the point it is produced, not at the point it is compared.

## Predictions

| # | prediction | why I think so |
|---|---|---|
| 1 | All four return `DIVERGES`, none `NONDETERMINISTIC` or `WROTE_NOTHING` | the 2026-09-19 sweep put all four in the "live git log" row, which is deterministic at a commit |
| 2 | **At least one diverges on MORE than its named key.** | see 3 and 4 |
| 3 | `phases.json` also diverges at `commits_by_day` | `generate_phases_json` reads `git log --format=%ad` for a cumulative per-day series; that is the same input at a second path, and the item names only the scalar |
| 4 | `value_arms.json` diverges at several paths derived FROM the commit — `short`, `produced_by_the_tree_it_publishes_from`, `reading`, and the `objective` block | `_producing_commit` reads `PUBLISHING_TREE_COMMIT` once and computes prose and booleans from it, including `git show <commit>:<path>` against the publishing tree. The identity is an input to a comparison, not just a recorded field. |
| 5 | `capabilities_door.json` and `evidence.json` diverge at their named key **alone** | both are a single `subprocess` call assigned straight into the payload with no downstream reader |
| 6 | The item's literal remedy (exclude the four named keys from the comparison) would promote **at most 2 of 4** | follows from 3 and 4 |

## What would refute the design I intend to build

I intend to make the provenance **observable** rather than listed: a value is publication provenance
when it IS the identity of the tree under test, so no per-feed key table exists to go stale. That
design is refuted if prediction 4 holds and the derived fields are *prose* — a sentence containing a
short sha is not equal to the sha, so it cannot be recognised by identity, and no comparator-side
rule can separate it from content. If that is what I find, the separation has to happen in the
generator, and the honest report is that the four are not one shape but two.

## Addendum, written after reading the first result and before running the second

The first result refuted prediction 5 in a way that changes the design, so a second prediction is
registered here rather than folded into the writeup afterwards.

`capabilities_door.json` diverges at `/scale/figures[0]/as_of`, which `generate_capabilities_door`
reads out of `site/data/customers.json` — a **committed** feed. `evidence.json` diverges at a
`test_functions` count read live off the tree. Neither is the git log, and both are nonetheless
functions of *a* commit — just not of HEAD. That points at a different mechanism from the one I
pre-registered: not "exclude the provenance from the comparison" but **"stand at the commit the feed
records and regenerate there"**. The feed already names where to stand.

| # | prediction | why |
|---|---|---|
| 7 | Regenerated in a clone checked out at `be7311e35` — the commit `capabilities_door.json` records — the feed reproduces **exactly**: `git_commit` and `as_of` both come right | both divergences are functions of that commit, one trivially and one through `customers.json`'s committed bytes |
| 8 | `evidence.json` at the same commit loses `git_hash` and `test_functions` but **still diverges at `/suite/test_count` and `/suite/timestamp`** | the clone has no gitignored artefact, so the suite record falls back to a committed one from 2026-07-17; standing at an older commit does not conjure the cache |
| 9 | So this mechanism promotes `capabilities_door.json` and **not** `evidence.json`, and the reason `evidence.json` stays out is a *different class* from the one the item names | follows from 7 and 8 |

If 7 fails the mechanism is dead and I report that; if 8 fails — evidence.json also reproduces — then
the suite record is committed after all and I have mis-read the cache.

## What "done" means for this turn

A feed is done when it is in `COVERED_FEEDS` and
`test_a_feed_that_became_checkable_must_be_promoted` is green with it there — that leg reds while a
reproducing feed sits outside the set, so the work marks its own completion and I do not get to
grade it. Any of the four I cannot promote is reported with the specific reason, not dropped.
