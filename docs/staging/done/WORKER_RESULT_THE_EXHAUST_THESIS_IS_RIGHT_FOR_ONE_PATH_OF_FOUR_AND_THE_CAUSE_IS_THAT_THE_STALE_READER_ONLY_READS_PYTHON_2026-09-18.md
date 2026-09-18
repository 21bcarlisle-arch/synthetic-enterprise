**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** publish-wedge-advance-classes

# The exhaust thesis is right for one path of four, and the cause is that the stale reader only reads Python

*Worker, 2026-09-18. Drawn item: `the-publishers-own-exhaust-is-what-blocks-the-publishers-reconcile` (LANE 0 DELIVERY).*

**Claim:** `the-publishers-own-exhaust-is-what-blocks-the-publishers-reconcile`
**Class:** publish_gate_and_wedge
**Premise re-measured at HEAD before starting; three of four cited commits were already spent.**

---

## The drawn premise was partly spent before I started, and its measurement had moved

The item cited four commits and a four-path intersection. Re-measured at draw time against
`origin/main` after a `git fetch`:

| The item said | Measured 2026-09-18 |
|---|---|
| `HEAD..origin/main` = 11, `origin/main..HEAD` = 3 | **13 behind, 1 ahead** |
| three local commits to clear: `f66ad19fe`, `4ff9bb8f6`, `fdca62381` | **all three already ancestors of `origin/main`** — landed by another route |
| intersection is exactly four paths | **eleven paths block the fast-forward** |
| the three exhaust paths are `agent_status.json`, `tick_heartbeat.json`, `value_arms.json` | **only `value_arms.json` still blocks**; the other two are dirty in the worktree but byte-identical between HEAD and origin, so they are not in the fork at all |

The one local commit remaining is `96ec173c0`, a 235-line staging document in one file. It is in no
commit on origin.

So **three of the item's four cited commits were spent**, and two of its three named exhaust paths
were not blockers. The item's instruction was to say so rather than do the work twice. This is that,
and then the repair, because the thesis underneath survives the instances.

---

## What actually holds the tree, measured rather than argued

`origin_reconcile.paths_blocking_fast_forward()` on the live shared tree returns **eleven** paths:
seven untracked, four tracked. Asking each of the module's own verdict classes about them:

| Path | Class | Verdict |
|---|---|---|
| 6 × `docs/staging/*.md` (untracked) | untracked twin | **clearable** — byte-identical to origin |
| 1 × `docs/staging/SEAT_RESULT_THE_PUBLISHED_EIGHTEEN_POOLS…md` | untracked orphan | **clearable** — preserved on a ref first |
| `docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` | — | **refused**: *"no reader for .md files"* |
| `site/data/value_arms.json` | — | **refused**: *"no reader for .json files"* |
| `tests/background/test_process_run_complete.py` | — | refused: a REPLACEMENT, two implementations of one property |
| `tests/tools/test_fold_noise_floor_family.py` | — | refused: holder work, supplies 4 names origin lacks |

**The item's thesis — the publisher's own exhaust blocks the publisher's own reconcile — is correct
for exactly one of the four tracked blockers.** The other three are authored: one stale class
register and two lanes' genuine test work. Calling all four "exhaust" would have sent someone at two
test files that are nobody's to touch on a cadence.

### The two test files are mostly STALE, which the item did not know

The item said the fourth path "needs a real answer, not the same treatment". It needs a *third*
answer. Counting test functions:

- `test_fold_noise_floor_family.py` — worktree **17**, origin **25**. One name is novel.
- `test_process_run_complete.py` — worktree **98**, origin **100**. Three names are novel.

Both working copies are *behind* origin and carry a small novel delta on top: stale and holder at
once. `HEAD` vs `origin/main` is `+103 −0` and `+144 −0` respectively — origin is **purely additive**
over our base. Landing either working copy wholesale would delete work origin already has.
`stale_copy_verdicts` already names the exact remedy for one of them
(`isolate_hunks --survey`, land hunk 2 over HEAD). Neither is this turn's judgement and neither was
touched.

---

## The cause, and it is not "exhaust"

A generated feed defeats all four existing classes **at once**, and the reason has nothing to do
with its content:

1. Both twin sweeps need hash equality with origin. A generated feed is **never** hash-equal — its
   producer rewrote it after the last landing and rewrites it again next tick. `value_arms.json` was
   rewritten at 01:24 this morning.
2. `stale_copy_verdicts` cannot reach it because **`refresh_to_head` reads Python**. Asked about a
   `.json` feed it returns *"this control has no reader for .json files, so it CANNOT establish that
   the copy has nothing to lose"* — fail-closed, correctly, on a question never answerable in that
   language.
3. The untracked-orphan class does not apply to a tracked path.

So the path was **permanently** unresolvable — and under the module's all-or-nothing rule, one
permanently unresolvable path is fatal to *every other class beside it*. The six hash-proven twins
were cleared by nothing for as long as the feed sat there.

The loop that makes it self-sustaining is the item's, and it is real: `reconcile` merges and pushes
from an **isolated worktree**, so origin advanced on the cadence all week while the shared tree could
not follow. Origin's copy of these files carries `00e13306b merge origin/main: automatic
reconciliation in an isolated worktree` dated today; ours carries the same message dated yesterday.
Each cadence closed a fork and re-opened it. **The exhaust is inside the loop it blocks** — the item
had that exactly right, and had the mechanism wrong.

### And the module already knew, in prose, in the same refusal

`_split_generated` asks the same two oracles a few hundred lines above, and `_landing_clause` prints
the answer to a human:

> the GENERATED path(s) are a PRODUCER'S OUTPUT, not work — do NOT land them

The refusal that then held the tree said it could not establish whether that same path was some
lane's work. **Both sentences are in the same refusal, about the same path, and only one of them was
ever acted on.**

---

## The repair

A fifth class, `origin_reconcile.generated_output_verdicts`, keyed to the property rather than to
today's paths. Its safety argument is the twin's on different ground: for a twin the claim is *these
bytes are already on origin*; here it is *these bytes are not authored at all* — re-derivable by
running the producer, and rewritten by the next tick whatever the advance does. The act is the twin's
own `restore_tracked_twin`, so the fast-forward writes origin's bytes over it a moment later. Acts
stay at three; grounds go to five.

Two deliberate asymmetries against `_split_generated`, which fails **soft**:

- **Both oracles must answer.** There the output is remedy prose and failing soft costs a reader a
  hand-check. Here it decides whether a file is written over, so an unasked oracle reads as neither
  "generated" (a write bought on an unread state) nor silently "authored". `None` refuses the batch.
- **A path the oracles do not know is authored work and stays refused.** Measured on the live tree,
  the class approves `value_arms.json` and refuses all three authored paths.

Control: `tests/background/test_a_producers_own_output_could_be_proven_lossless_by_no_class_and_it_held_the_advance.py`,
seven legs each naming its own defect, including one reachability control over the whole partition
(a class that approved *nothing* would pass every refusal leg) and one over the *question* rather
than the answer (a caller that widened the class to every blocking path is invisible to a fixture
that only records answers).

### Mutation-proven, every leg, in a clone

Run in `~/.cache/gen_class_mut` (a `git clone` of the shared tree, so `_blob_in_head` has a real
HEAD to read and no mutation touched a lane's in-flight gate). Baseline 7 passed; each mutation
reds exactly the leg that named it and nothing else:

| Mutation | Reds |
|---|---|
| drop `set(generated)` from the `resolvable` union | `…_cleared_and_the_advance_then_succeeds`, `…_restored_and_never_unlinked` |
| verdict body always returns `(False, …)` | `…_verdict_partition_is_reachable_both_ways` |
| treat a `None` verdict map as empty | `…_unavailable_oracle_refuses_and_touches_nothing` |
| drop the `_blob_in_head` leg | `…_generated_path_head_does_not_hold_is_refused` |
| offer every candidate, not candidates-minus-stale | `…_asked_only_of_what_the_stale_class_left` |
| clear by `unlink` instead of `restore` | `…_restored_and_never_unlinked` |
| drop the all-or-nothing guard | `…_authored_path_beside_a_generated_one_still_refuses_everything` |

No leg was left ungraded, and no mutation was recorded as an equivalence.

Full advance-class suite re-run together — the new file plus all seven siblings that exercise
`advance_shared_tree` — **71 passed**, so the four existing classes are undisturbed.

---

## What this does NOT do, stated plainly

**It does not unwedge the tree, and the DONE clause is not met.** The all-or-nothing rule is a safety
property and it is correct: clearing the feed while three authored paths still stand would touch
files and still not advance — the one shape in which clearing actually costs someone something. After
this repair the advance still refuses, and now refuses on **three** paths instead of four, naming
each with its own reason.

Closing the remaining three needs:

1. the stale `.md` class register — the same defect as `.json`, a file type the stale reader cannot
   read. Its worktree blob **is** reachable in history (`b10e16207`), so a blob-on-a-ref proof would
   take it. Not built here; filed as the obvious next increment.
2. two lanes' stale-and-holder test files — `isolate_hunks`, origin's bytes plus the novel hunks
   only. A judgement, not a cadence, and one of them is *currently open* under a running publisher.

**`last_clean_publish` is still `null` and I am not claiming otherwise.** The item said an eighth
cause with no repair is a failure; this is a repair with its reach stated, which is the honest
version of the same sentence.

## Not touched, as instructed

- The six tests in `blocking_tests` are recorded against `82f7bb0d9` with `red_at_head:
  not_established`. Nobody was sent at them.
- `MEASURED_COMMIT_HOOK_CHAIN_SECONDS_2026_09_04` was not re-dated.
- `process_run_complete.py` was mid-gate (pid 756622, ~21 min in) throughout this turn; the shared
  tree was not written under its running gate beyond this lane's own pathspec.
