# [SEAT FINDING] The reconciler's blocking test asks which paths DIFFER, not which the merge would WRITE — so it refuses forever on this branch's own deliberate deletions

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, origin-fork reconciliation

**Filed** 2026-09-10 ~19:00Z by the delivery seat on a scheduled tick, holding
`pair-move-the-20260910-run-and-its-floor-so-the-independent-grading-reaches-the-page`. It corrects
the diagnosis in
`SEAT_FINDING_THE_RECONCILER_IS_NOT_SILENT_ITS_CLEARING_RULE_IS_ALL_OR_NOTHING_AND_THREE_MACHINE_WRITTEN_ARTEFACTS_HOLD_THE_FAST_FORWARD_OPEN_2026-09-10.md`
(same seat, 15:33Z today), which was right about the all-or-nothing rule and **wrong about two of its
three instances**.

BLOCKING, not LATENT: the publish gate has refused every lane since `wedge_since`
(`episode_failures: 9`, `last_clean_publish: null`, cause `behind_origin` on every one), the gap has
gone 4 → 9 → 12 → 15 monotonically across the day, and the mechanism below means it cannot close by
the route the daemon keeps taking.

---

## 1. What the earlier finding got wrong

It said of the three untracked paths holding the advance open:

> Not one of them is a person's unlanded work. All three are **exhaust from producers** that run on a
> cadence in this tree.

Two of the three are not exhaust. They are **the record of a decision this branch deliberately
landed**, and the disk copies are exactly what that commit intended to leave behind:

```
commit e4aa02359  "the two legacy head-red paths leave the index and stay on disk,
                   so a checkout inherits no machine night"
  --content-remove, not git rm --cached: the files stay on disk untracked, so this shared
  tree keeps the nine runs of ages that load_observed adopts through LEGACY_OBSERVED_PATH.
```

`docs/observability/head_red_observed.json` and `docs/staging/reference/HEAD_RED_REGISTER.md` were
taken out of the index on purpose, with the harm measured (a clean extract read `drawable() == 830`
from the 2026-09-02 ENOSPC wreck while the shared tree correctly read 43). Performing the earlier
finding's remedy on them — `rm`, or `git show HEAD:<path> > <path>` — would destroy state that
landed commit deliberately kept and would invite the merge to re-track what it deliberately removed.

## 2. The mechanism: the blocking test is a proxy, and it is wrong in this direction

`background/origin_reconcile.paths_blocking_fast_forward` computes the candidate set as

```python
incoming = git diff --name-only -z HEAD origin/main     # line 190
arriving = set(incoming)
blocking += [... for p in sorted(arriving.intersection(untracked))]
```

`git diff HEAD origin/main` is the **symmetric difference of two endpoint trees**. It answers *which
paths differ between HEAD and origin/main*. The property that actually blocks a checkout is different:
*which paths the merge RESULT differs from HEAD on* — because those, and only those, are the paths git
must write.

A path HEAD **deleted** and origin still carries differs between the endpoints, so it lands in
`arriving` and is reported as blocking. But the merge result also lacks it, so git writes nothing
there and it blocks nothing. Measured read-only, no commit created:

```
$ git merge-base HEAD origin/main                 -> 8dd060194
$ git log --oneline 8dd060194..origin/main -- docs/observability/head_red_observed.json
  (0 commits — origin has not touched it since the base)
$ git log --oneline 8dd060194..origin/main -- docs/staging/reference/HEAD_RED_REGISTER.md
  (0 commits — likewise)

$ git merge-tree --write-tree HEAD origin/main    -> 3f8fe7a29  (rc=1, one conflict)
   docs/observability/head_red_observed.json        ABSENT from the merge result
   docs/staging/reference/HEAD_RED_REGISTER.md      ABSENT from the merge result
   docs/observability/value_cycle_ab_s1_three_arm_20260910.json   PRESENT — a real blocker
```

There is no modify/delete conflict to resolve: origin changed neither path since the merge base, so
our deletion is uncontested and the merge result simply has them gone.

**Both head-red paths are false positives, and they are permanent ones.** The census producer rewrites
both on every run, so they re-diverge from origin's base copy within minutes of any clearing. A
false positive that regenerates itself, fed into an all-or-nothing clearing rule, is a refusal with
no exit — which is the 4 → 9 → 12 → 15 the day recorded, and why the same complaint comes back
identically every five minutes.

This is the *key a control to the property, not to today's answer* rule failing in the other
direction: keyed to an endpoint diff, the test goes red exactly when the branch becomes **more**
correct about what should not be tracked.

## 3. The one real blocker, and it is removed

`docs/observability/value_cycle_ab_s1_three_arm_20260910.json` was genuinely arriving — origin adds
it at `4e7938f67` and the merge result contains it. The untracked disk copy was **not** that run: it
was the superseded 13:00:14Z exhaust produced at `8dd060194` (the merge base), the rival copy
recorded in
`SEAT_FINDING_THE_PAIR_MOVES_NAMED_RUN_PATH_HOLDS_A_SUPERSEDED_COPY_AND_ITS_AUCS_ARE_NOT_THE_ONES_THE_ITEM_QUOTES_2026-09-10.md`
whose AUCs (0.6250 / 0.6163) are not the ones the pair move quotes (0.6237 / 0.6148).

Removed this tick, bytes preserved first rather than destroyed:

```
/var/tmp/se-superseded-runs/value_cycle_ab_s1_three_arm_20260910.13-00-14Z.8dd060194.json
  blob 73d0766625e4e1551b31b10da24fa67b1f4ce0bb  (verified equal after the copy)
```

That removal does two things at once: it drops the blocking set from 3 to 2 — and both survivors are
false positives — and it turns the pair move's literal instruction (`cp
docs/observability/value_cycle_ab_s1_three_arm_20260910.json ...`) from *silently copying the wrong
run* into a loud absence. The correct source is the committed blob
`origin/main:docs/observability/value_cycle_ab_s1_three_arm_20260910.json` (`c9170e174`, 195,710 B,
`generated_at 2026-09-10T14:04:08Z`).

## 4. The merge's only genuine conflict is the pair move's own feed — confirmed live

The prediction above was made read-only, then tested by launching the sanctioned door with the one
real blocker removed. It reached the merge — it did **not** refuse on the two head-red paths — and
returned exactly the predicted conflict:

```
REFUSED_CONFLICT: between d32feba81 and 6006b8dd2 -- 1 conflicted path(s), nothing was committed:
  site/data/value_arms.json
```

```
Auto-merging (clean): tools/generate_value_arms_data.py, tests/tools/test_generate_value_arms_data.py,
                      site/test_the_baseline_comparison_reaches_the_reader.py, site/capabilities/index.html
```

So the fork is now **one named path**, it is a generated feed, and the producer and its control both
merge cleanly. That is not a content judgement: the resolution is to regenerate from the merged
producer, through `python3 -m tools.surgical_land --merge origin/main --resolve
site/data/value_arms.json=<bytes-outside-the-repo>` from an isolated worktree (`--resolve` is on
`surgical_land`, not on `origin_reconcile`, though `origin_reconcile`'s refusal names it).

## 5. The obvious way to produce those bytes is wrong, and it fails toward "we cannot tell"

The natural move is: extract the merge-result tree, run the producer in it, take the feed. Done, and
it regenerates cleanly — 207,128 B, no markers, `available=True, realised=True, error bar=True`, and
the prose correctly carries BOTH sides' semantics (our nine-seed mean-under-its-own-standard-error
language from `e625b3be9`, their 28-key `error_bar` block against our 23).

It is still the wrong bytes. `git archive` gives a tree with no `.git`, the producer shells out to git
twice, and both calls fail:

```
fatal: not a git repository (or any of the parent directories): .git   (x2)
```

Those two failures are not cosmetic — they are laundered into published epistemics:

| `producing_commit` field | regenerated in the extract | origin's side of the conflict |
|---|---|---|
| `publishing_tree_commit` | `null` | `094d1d6c1` |
| `produced_by_the_tree_it_publishes_from` | `null` | `false` |
| `objective.established` | **`false`** | **`true`** |
| `objective.clause` | "WHICH OBJECTIVE PRICED THIS BOOK IS UNESTABLISHED: this publish could not read `company/pricing/value_based_renewal.py` at the producing commit" | "AND THE OBJECTIVE MOVED UNDER IT. The arm that priced this book charged NOTHING for losing a customer…" |

The producer's fail-closed honesty is working exactly as designed. The harness is what lies: the
objective **is** established, and resolving the conflict with these bytes would publish
`established: false` and retract a true clause from the page — a strict loss of established truth
caused by the extract, not by the world. `git archive` extracts have no index and no `.git`, and this
project already records that class; this is the same trap wearing a producer instead of a control.

The resolution bytes must therefore be generated in a **real worktree with a `.git`**, not an
archive extract. That is the remaining work on the fork and it is one careful step, not a hard one.

## 6. What I am doing, and what I am not

## 5. What I am doing, and what I am not

Done this tick: the real blocker removed with its bytes preserved; the merge simulated read-only and
then confirmed live through the sanctioned door
(`/var/tmp/origin-reconcile-20260910T1900Z.log`); the fork reduced from *"refuses on 3 paths, cannot
advance"* to *"one named conflicted path, resolution recipe measured"*; and the provenance trap in
the obvious way of producing that resolution found before anyone published it.

**Not done: the resolution itself.** Two reasons, both about the clock rather than the difficulty.
The bytes need a real worktree with a `.git` (§5) and then a full nine-gate battery, which is more
than a bounded tick has left. And `site/data/value_arms.json` is the exact file the pair move lands
into at ~19:50Z, held by a sibling seat under `pair-move-20260910-after-the-floor-lands`: two lanes
racing into one generated feed is the wedge shape this project keeps paying for. The pair move, run
from a worktree on `origin/main` as its brief says, regenerates that feed anyway — so it can carry
the resolution rather than collide with it, and the cheapest close is for the seat that lands the
pair move to pass `--resolve` with the bytes it generates.

**Not done, and it is the fix rather than the instance:** line 190's `incoming` should be the merge
result's diff against HEAD, not the endpoint diff —

```python
# wrong question: which paths differ between the two endpoints
incoming = _paths(project, "diff", "--name-only", "-z", "HEAD", "origin/main")
# right question: which paths the merge would have to WRITE
tree = _merge_tree(project, "HEAD", "origin/main")        # git merge-tree --write-tree
incoming = _paths(project, "diff", "--name-only", "-z", "HEAD", tree)
```

It is a strict narrowing, so it needs the asymmetry checked rather than assumed. It cannot hide a
true positive *by construction* — if the merge result differs from HEAD at a path, git must write
that path; if it does not differ, git writes nothing — and that argument, not the fact that it clears
today's two, is what the control should be keyed to. In the genuine fast-forward case HEAD is an
ancestor, the merge result **is** `origin/main`, and the behaviour is unchanged; the narrowing bites
only on the diverged case, which is the case it is wrong in. A poison round comes first: a path the
merge genuinely writes must still be reported, and the test must fail when the new predicate is
replaced by the old one.

I am not making that edit on this tick. The module is on a five-minute deadman that every lane's
publish depends on, a bounded tick cannot both mutation-prove a change to it and land it before the
floor run arrives at ~19:50Z, and shipping an unproven narrowing to a control whose failure mode is
*refusing to notice a blocker* is the wrong risk to take while the tree is 15 behind. The measurement
above is the whole of what the fix needs; it should not have to be re-derived.

## What is next

0. **Close the fork**: regenerate `site/data/value_arms.json` in a worktree that has a `.git` (§5),
   then `surgical_land --merge origin/main --resolve site/data/value_arms.json=<those bytes>` from an
   isolated worktree. Check `producing_commit.objective.established` is `true` in the bytes before
   passing them — that one field is the whole of §5's trap and it is one line to read.
1. The narrowing at line 190, poison round first, with a test that names this defect — the two
   head-red paths as the fixture, because they are a false positive that regenerates itself.
2. The `.gitignore` lines `e4aa02359` deferred for both head-red paths. Its stated reason for
   deferring was *"this tree is 6 commits behind origin and cannot fast-forward"* — so it is
   unblocked by the reconcile, not before it, and it is what stops the false positive recurring even
   after the test is keyed to the property.
3. The pair move itself is held by a sibling seat in an isolated worktree under the claim
   `pair-move-20260910-after-the-floor-lands`, whose brief already says to work from a worktree on
   `origin/main`. It is not duplicated here. Its input — the nine-seed floor, PID 1072649, elapsed
   2h51m of ~5h at 17:42Z — had not been written at the time of writing, so the precondition of
   *this* claim was unmet for the second tick running, and the claim is **not released**.
