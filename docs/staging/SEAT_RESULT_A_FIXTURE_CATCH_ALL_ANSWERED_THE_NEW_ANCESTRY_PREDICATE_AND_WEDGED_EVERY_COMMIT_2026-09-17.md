**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** n/a (blocking red, cleared)

# RESULT: a fixture's catch-all answered the new ancestry predicate, graded the success path as a refusal control, and wedged every commit in the repository

Delivery seat, 2026-09-17. Found while landing the weather-world machinery
(`SEAT_RESULT_THE_STRANDED_WEATHER_MACHINERY_WAS_ONE_LAND_SHORT_...`); not part of that item, and
taken because it refused every commit in the tree and not only mine.

## 1. THE RED, AND THAT IT WAS NOT MINE

`tools.surgical_land` refused my landing with
`tests/background/test_the_liveness_surfaces_refusals_left_only_an_orphaned_log_line.py::test_every_refusing_exit_records_and_they_do_not_all_say_the_same_thing`
— nothing to do with weather. **Proven pre-existing at `origin/main` in a clean extract holding
none of my work**: `git archive origin/main | tar -x` into an empty directory, confirmed the three
weather modules absent, ran the one test — `1 failed in 0.07s`. So it was not my change, not test
pollution in a shared tree, and not a stale base: it was red on the trunk, and every lane's commit
was refused by it.

## 2. THE MECHANISM: A FAKE MORE PERMISSIVE THAN ITS SUBJECT

On 2026-09-16 `_push_reached_origin` was correctly re-keyed from *"are the heads equal"* to the
property *"did the publish commit reach origin"*. Its docstring argues this well and cites
CLAUDE.md's own rule; `05add41ab` was a real publish recorded as `push_did_not_reach_origin` with
`last_clean_publish: null` six days into a wedge already over, because a commit created while
behind origin can never make origin's head equal ours.

The new second leg is `_commit_is_ancestor`, and it issues a subprocess call the fixture had never
seen: `git merge-base --is-ancestor`. The fixture's `fake_run` ended with

    return types.SimpleNamespace(returncode=0, stdout="", stderr="")

for every unrecognised command, and `_commit_is_ancestor` reads `returncode == 0` as **yes, an
ancestor**. So the `push_never_landed` leg — local `new11111`, origin standing still at `old99999`
— returned `True`:

* the anti-phantom guard the 3.5-hour origin-freeze of 2026-07-24 bought was **answered by the
  fixture rather than by the code**;
* the leg asserting `is False` was grading the success path, which is exactly what its own message
  says it must never do;
* and the production code was never wrong. **The defect is entirely in the test double.**

This is the catalogued shape *a fake more permissive than its subject turns a fail-open into a
green suite*, with a specific and repeatable trigger: **a predicate gains a new subprocess call,
and a fixture whose catch-all returns success absorbs it silently and affirmatively.** The
permissive catch-all is not a shortcut that saved a line — it is a standing offer to answer any
future question with "yes".

## 3. THE REPAIR

* **Ancestry is modelled explicitly and defaults to `False`** — the fail-closed direction, and the
  same direction `_commit_is_ancestor` itself takes for a question git cannot answer.
* **The fixture asserts the argv order it is answering.** `_commit_is_ancestor(commit, tip)` asks
  whether *our* commit is reachable from *origin's* tip; a fixture with these reversed answers a
  different question and still looks plausible.
* **The catch-all now REFUSES an unrecognised `git` call** with a message naming the command and
  why, instead of blessing it. `git add` is modelled explicitly as the success it is. The next
  predicate that reaches for a new subprocess is caught by this fixture rather than absorbed by it
  — which is the whole of the generalisable fix.
* **A new control for the property the widening bought**, which had none:
  `test_a_behind_origin_publish_that_DID_reach_origin_is_a_success_not_a_refusal`. Every existing
  leg in the file asks whether a refusal refuses, so a predicate returning `False` for everything
  would have passed all of them.

### Mutation-proven in both directions, which is the point

| mutation | effect | control that fired |
|---|---|---|
| drop the ancestry leg (revert the 09-16 widening to equality) | a real behind-origin publish reads as a refusal | **the new success-path control** |
| `_commit_is_ancestor` returns `True` always (the fail-open the old fixture simulated) | `push_never_landed` reads as a publish | **the four-exits refusal control** |

Baseline green after each; 15 passed, up from 14-with-one-red. The two mutations are mirror images
and each is caught by a different leg, so the ancestry leg is load-bearing in both directions
rather than a constant — the thing a single-sided pair cannot establish.

## 4. AN OBSERVATION I AM NOT REPAIRING, RECORDED SO IT IS NOT RE-DISCOVERED

`docs/design/orphan_baseline.json` carried `module_count: 1154` while `origin/main`'s own tree holds
1147 modules. The ratchet's provenance note names this case itself: a `freeze()` output from another
tree — an older checkout or an isolated worktree with uncommitted modules — pasted in, in which case
the orphan list beside it is that tree's reachability and not the trunk's. My freeze rewrote it to
this tree's honest 1150 (1147 plus the three weather modules) and added nothing else, so the
discrepancy is now closed for the trunk; but **whether the rows frozen at 1154 were ever this
tree's reachability is unestablished**, and a lane that trusts that list is trusting a measurement
of a tree nobody can now identify. Not blocking, not mine, and cheap to check by re-freezing on a
clean trunk extract and diffing the row set.
