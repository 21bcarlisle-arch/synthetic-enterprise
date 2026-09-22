**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `a-generator-must-stamp-provenance-that-describes-what-it-read`

# The stamp now says whether the commit describes what was read, and the honest answer is usually no

*Continues `SEAT_RESULT_A_FEEDS_GIT_STAMP_IS_NOT_A_DESCRIPTION_OF_WHAT_PRODUCED_IT_SO_NO_STANDPOINT_REPRODUCES_IT_2026-09-19.md`,
whose closing paragraph made this the next item. Its premise was re-measured before starting and
holds: `d181b062d` and `be7311e35` are both ancestors of `origin/main`, the repair it named had not
landed by any other route, and the one "duplicate" live claim the draw flagged is this very claim
id held by this invocation.*

---

## What was wrong, in one sentence

`generate_capabilities_door` stamped `git rev-parse HEAD` into `git_commit` and read
`site/data/customers.json` off the working tree. Those describe different states, so the feed
asserted its own provenance falsely — in the one field a reader would trust to settle exactly that.
`generate_evidence_data` had the same shape at `git_hash`.

## What it was replaced with, and why it is a sentence and not a sha

The repair is **not** a better sha. The question a reader of a feed actually wants settled is:

> **If I stood at this commit and read these inputs, would I get the bytes this generator got?**

`tools/provenance_stamp.py` answers that, and the answer travels in the feed under one reserved key,
`published_from`:

```json
"published_from": {
  "commit": "d181b062dc6dbe4c6a315d03a531a4a44325bbe3",
  "tree_was_clean": false,
  "inputs_are_the_committed_bytes": true,
  "inputs": [{"path": "site/data/customers.json", "state": "committed"}, ...],
  "reason": "every input named here matches this commit, but the tree carried other uncommitted
             changes, and this generator reads more than the paths it names — so standing at this
             commit may still not reproduce this feed"
}
```

**It asks the question TWICE on purpose, at two grains, and the coarse one is the load-bearing
half.** A declared input list is a diagnostic: it says *which* input moved, which is what a reader
can act on. It is never a complete account of what a generator read, and enumerating one would go
stale silently — `generate_capabilities_door.wall_position` shells out to a register that walks all
of `company/`, and `generate_evidence_data` counts `def test_` across every test file in the tree.
Neither is a fixed list of paths and neither ever will be. So `tree_was_clean` is the sufficient
condition (nothing in the tree differed ⇒ nothing the generator read differed) and
`inputs_are_the_committed_bytes` is the diagnostic beside it. `describes_its_inputs()` requires
both, in one place, so three callers' `.get()` chains cannot quietly disagree about what a missing
key means. Untracked files count as dirty: a new uncommitted test file is invisible to a
tracked-only diff and moves the `def test_` count all the same.

## The result nobody should skip past: this promotes nothing, and that is the correct outcome

`capabilities_door.json` and `evidence.json` are still not reproducible at their own recorded
commit, and **the repair did not make them reproducible — it made them say so.** Measured in this
tree: `inputs_are_the_committed_bytes: true`, `tree_was_clean: false`. Every named input matched;
another lane's uncommitted work did not.

So `recorded_publication_commit` now returns `NO_STANDPOINT` carrying **the feed's own reason**,
instead of standing at a commit that was never going to reproduce and reporting the difference as a
`DIVERGES_AT_ITS_OWN_COMMIT` red. A refusal that names its cause replaced a red that blamed the
comparator for a producer's honesty. `COVERED_AT_THEIR_OWN_COMMIT` stays empty, and
`test_a_feed_checkable_at_its_own_commit_is_promoted` still asserts over the **candidates**, so the
empty set is still never the evidence.

**This is the shape of the whole 23-feed problem and it is worth stating plainly: in a tree several
lanes write at once, a feed generated from the working tree is structurally uncheckable at the
commit it was generated at.** The honest field is the deliverable. Chasing reproduction here would
mean either publishing only from a clean tree — which would stop the 30-minute cycle — or the
standpoint change filed below.

## The finding this turned up, which is the next piece and is NOT filed as a gap

**The right standpoint is the commit the feed was COMMITTED IN, not the commit it was generated
at.** `background/process_run_complete` commits the whole `site/data` surface in one commit, so
`customers.json` and `capabilities_door.json` land *together*: the commit AFTER generation contains
the feed and the sibling inputs as they actually were. That commit is unknowable at generation time
but trivially knowable at check time — `git log -1 --format=%H -- site/data/<feed>.json`.

I did not build it, for a stated reason rather than for want of time: `check_at_its_own_commit`'s
whole design is that the standpoint is **observed from the feed and never computed by the runner**,
so a feed cannot be graded against a commit chosen by whoever ran the check. Computing the
standpoint from the git log breaks that property, and whether the weaker guarantee is worth it is a
judgement that deserves its own measurement, not a change smuggled into a producer repair. It is a
candidate for promoting several of the remaining 21, and it costs one `git log` call.

## Predictions, kept beside the result

Written before wiring the generators, after the design was fixed:

| # | predicted | outcome |
|---|---|---|
| 1 | both feeds stamp `inputs_are_the_committed_bytes: true` in a normal tree — the named data inputs are rarely the dirty ones | **CONFIRMED** (6/6 and 4/4 `committed`) |
| 2 | `tree_was_clean` is false in this shared tree | **CONFIRMED** — and it is why the coarse question had to exist; prediction 1 alone would have shipped a stamp that said "reproducible" about a run that is not |
| 3 | neither feed is promoted to `COVERED_AT_THEIR_OWN_COMMIT` | **CONFIRMED** |
| 4 | the reserved key can be read after the scalar scan without harm | **REFUTED**, before it shipped. `evidence.json` keeps a short `git_hash` beside the full stamp; the scan counts the short and full forms as **two** commits and refuses. Reading the reserved key first is load-bearing, and `test_a_back_compatible_short_sha_does_not_cost_the_standpoint` pins it. |
| 5 | no existing test reds on the new key | **REFUTED** — `test_page_is_reproducible_from_the_sources` compares the whole payload minus a volatile list. `published_from` is volatile for the same reason `git_hash` is, one step further, and is now named there with the control that does bind it. |

## Mutation evidence — eight mutants, seven caught, one established as an equivalence

Run in a `git archive` extract so the shared tree was never written. Each mutant was caught by the
leg written for it:

| mutant | caught by |
|---|---|
| drop `tree_was_clean` from `describes_its_inputs` | `test_the_coarse_question_catches_what_the_named_list_cannot` |
| any blob at the commit counts as `committed` | `test_a_modified_input_is_named_not_summarised` + the partition leg |
| `stamp()` tolerates an empty input list | `test_a_stamp_over_no_inputs_is_refused` |
| `tree_was_clean` ignores untracked files | `test_an_untracked_file_counts_as_dirty` |
| reserved key trusted without an ancestor check | `test_a_reserved_key_naming_a_commit_this_repo_does_not_have_is_refused` |
| reserved key ignores whether inputs were committed | `test_a_feed_that_says_its_inputs_moved_yields_no_standpoint` |
| reserved key read AFTER the scan | three legs |
| `head_commit` returns `"unknown"` instead of `None` on a malformed sha | **NOTHING — an equivalence**, recorded in the docstring beside the branch: no real git state reaches it (`rev-parse` exits non-zero outside a repo and always returns 40 hex inside one). Kept as a shape guard against a spoofed `git`, deliberately not given a test that would have to shim `git`.

**The sixth mutant was SILENT on the first run**, and the reason is this project's catalogued trap.
Two legs read `ps.head_commit(PROJECT)` and skipped when it was `None` — which is always, in a
`git archive` extract. The run read `10 passed, 2 skipped` and the gutted branch was caught by no
leg. **A skip wears a pass's colour.** Both legs now build a real tmp repository and assert against
that, so they fire everywhere including an extract, and the baseline in the extract is 12 passed, 0
skipped. The lesson is written into the test's own docstring, beside the assertion, rather than
here only.

## One pre-existing red, measured and NOT repaired here

`tests/tools/test_evidence_pages.py::test_page_is_reproducible_from_the_sources` is red at a clean
`HEAD` extract, before any change of mine. Cause, measured:

```
/nodes[4]/atoms[5]/citations[4]/test_functions   100 -> 98
```

The published `evidence.json` counts 100 test functions in a cited file that now holds 98 — the
feed is stale, a lane removed two tests since it was last published. This is exactly the class the
regeneration-check family exists to surface, and the publish cycle clears it within ~30 minutes. I
did not regenerate the feed: republishing would mask a live staleness signal behind my own commit,
and writing a shared generated feed from an isolated worktree is the catalogued way to land another
lane's stale bytes.

## What is done, and what is left of the item

Done and landed: the helper, the reserved key, both generators the item named first, the comparator
side, and the control with its mutation evidence.

Left, and deliberately a second increment: `value_arms.json`'s one reserved key for its publishing
commit — it scatters fifteen content shas today and `recorded_publication_commit` refuses it for
that reason — and `phases.json`'s sha, which records a commit COUNT and no sha at all and is the
cheapest of the four to promote precisely because it has never asserted a provenance it could not
support. Both are now one call to `provenance_stamp.stamp()` rather than a design question.
