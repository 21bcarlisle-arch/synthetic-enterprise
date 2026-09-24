**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The shared checkout's advance is judged by the shared checkout's own code, so every rule written to unwedge it ships inside the payload the wedge is blocking

Claim id: `enact-the-fast-forward-now-that-rule-1b-opens-the-comment-revert-door`.
Measured 2026-09-24 18:10–18:25 BST from an isolated worktree at `193fa7caa`, against the shared
tree `/home/rich/synthetic-enterprise`. Pre-registration written before any census:
`records/PREREG_THE_SHARED_CHECKOUTS_FF_IS_BLOCKED_BY_DIVERGENCE_NOT_BY_THE_COMMENT_REVERT_2026-09-24.md`.

## The one-line result

The drawn item's thesis — *"the door is open and nobody has walked through it"* — is **false**. The
door is shut, and rule 1b is not the lock. Rule 1b is **inert in the only tree that needs it**.

```
shared HEAD                          ffa14f065          origin/main   193fa7caa
checkout_drift()                     behind 28, ahead 5, contains_origin False, gap_paths 48
git show HEAD:tools/stale_copy_refusal.py | grep -c reverted_comment_block   ->  0
```

The item said to check that grep and said what follows if it is zero. It is zero.

## The differential, which is the whole finding

One path, one working copy, one project directory. The **only** variable is which
`tools/stale_copy_refusal.py` is on `sys.path` — the shared checkout's (no rule 1b) or origin's
(rule 1b present). Both arms call `origin_reconcile.stale_copy_verdicts(shared_tree, paths=[…])`.

`tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py`:

| arm | judge module | verdict |
|---|---|---|
| **A — placebo** | shared checkout's copy, `reverted_comment_block` absent | `(False, "the stale-copy control has NO complaint about this copy against origin/main: it does not predate the last landing there and it deletes no name. Refreshing it would discard an ordinary edit, which is `git checkout <path>` with a nicer name -- and that is forbidden here for this exact reason.")` |
| **B — treatment** | origin's copy, rule 1b present | `(True, "rival copy: supplies no name origin/main lacks, and the stale-copy control refuses it [reverts_a_landed_comment_block]. origin/main strictly supersedes it.")` |

The other seven graded paths returned **byte-identical verdicts in both arms**. So the arm is not
measuring "newer code says more things"; it moves exactly one path, and that path is the one rule 1b
was written for. **Rule 1b is load-bearing, it works, and it cannot run where the wedge is.**

This is the recursion one turn more general than the one
`SEAT_FINDING_THE_CHECKOUT_CANNOT_ADVANCE_BECAUSE_A_PRODUCERS_OUTPUT_IN_AN_AUTHORED_TREE_IS_INVISIBLE_TO_THE_GENERATED_ORACLE_2026-09-24.md`
banked. That one found *a producer's output blocks the checkout carrying the producer's repair*.
This one is not about any particular producer: **`advance_shared_tree` decides whether the shared
checkout may advance by running the shared checkout's copy of the judge.** So for every future rule
R added to `stale_copy_refusal` in order to unwedge a behind checkout, R is by construction
unavailable to that checkout until it advances — which is the thing R exists to enable. The class
is self-defeating by deployment path, not by any bug in R.

## Why the fast-forward still cannot be enacted, and rule 1b is only one of three reasons

`paths_blocking_fast_forward()` returns **13**, not the item's ~10. Graded (arm B, the generous arm):

| class | n | paths |
|---|---|---|
| identical to origin/main — twin, auto-clears | 3 | `site/test_the_book_is_bounded_by_compute_reaches_the_reader.py`, `tests/background/test_harden_rung_pass_ceiling.py`, `tests/tools/test_discovery_pass_ceiling.py` |
| refreshable `[reverts_a_landed_comment_block]` — **needs rule 1b** | 1 | `tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py` |
| untracked orphan — class four, auto-clears | 5 | the five `SEAT_FINDING_*_2026-09-24.md` |
| **holder work** — needs a landing, no door here clears it | 2 | `tests/background/test_publish_gate_wedge_draw.py` (hunk 1), `tools/refresh_to_head.py` (hunks 1,3,4,7) |
| **REPLACEMENT** — *"a judgement neither door may make"* | 2 | `tests/tools/test_refresh_to_head.py`, `docs/staging/reference/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` |

Three independent blockers, and clearing rule 1b's inertness clears **one row of thirteen**:

1. **`ahead == 5`.** Divergence is asked first and no path class is reached at all. At 18:07 an
   `origin_reconcile` merge (`surgical_land --merge origin/main`, pid 2362783) was already in the
   gate closing this leg. Not my work and not blocked on me.
2. **Rule 1b inert** — the differential above.
3. **Four paths in classes no unattended door may clear** — 2 holder work, 2 REPLACEMENT.

## The four contested paths are one lane's in-flight rework of the refresh door itself

`tools/refresh_to_head.py` + `tests/tools/test_refresh_to_head.py` + the CLASS reference document
are a single coherent change adding `--staged-too` / `STAGED_DISAGREES` /`_index_bytes` /
`_clear_index_entry`. Every one of those working copies carries mtime **09-24 15:02** — a single
restamping event, the one
`SEAT_FINDING_A_STASH_POP_RESTAMPED_321_FILES_AND_DEFEATED_THE_STALE_COPY_CLOCK_BY_38_SECONDS_2026-09-24.md`
already banked. Origin's last commit to `tools/refresh_to_head.py` is **777c4adb8 at 17:10 — rule
1b's own commit**, which restructured that file's import block.

**So the prescribed `--content` door here would land 15:02 bytes over a 17:10 landing, and the
17:10 landing is rule 1b.** `Verdict.by_clock` exists for exactly this and its docstring says the
right thing — *"a copy taken before a landing cannot be holder work OVER that landing"* — but it
did **not** fire: `judge_copy(root, 'tools/refresh_to_head.py', base='origin/main')` returns
`state='refused_supplies_names_head_lacks'`, `gains=('STAGED_DISAGREES', '_clear_index_entry',
'_index_bytes')`, `by_clock` unset. The symbol reader answers first and the clock is only consulted
where no symbol reader can. That ordering is defensible on its own terms — symbols are stronger
evidence about *content* than mtime is — and it is a **concurrent fork, not a stale revert**, so
the holder-work verdict is not simply wrong. But the two arguments disagree here and the module
prints only one of them, with no note that the other exists. A reader walking the printed door
cannot see that the base moved after their copy was taken.

**I did not walk that door.** Splitting a coherent three-file rework in half by landing four hunks
of the tool without its test rework, over the commit that restructured the very imports those hunks
sit in, is not a thing to do unattended — and the module's own REPLACEMENT verdict says so in
words: *"which survives is a judgement neither door may make. Decide it, then land the winner
deliberately."*

## Pre-registration, scored

1. **Divergence is the binding refusal, no path class reached.** ✅ CONFIRMED. `ahead == 5`.
2. **Ahead closes without me; behind GROWS.** ✅ **CONFIRMED** — settled while this finding's own
   commit was in the gate, and scored in the addendum below rather than back-filled here.
3. **The comment-revert path grades `refreshable`, and rule 1b is why.** ✅ CONFIRMED, **and the
   placebo arm is what confirms it.** Without arm A this would have been the flattering reading —
   "the verdict is there, so the rule works" — with no evidence the rule was what produced it.
4. **Fewer than half the 48 gap paths resolve to a blocker class; residue dominated by
   `docs/observability/` dotfiles.** ❌ **REFUTED, and the prediction was malformed.** 13 of 48 is
   indeed fewer than half, but that is not a measurement of what I said: `gap_paths` counts paths
   differing across the 28-commit gap, while `paths_blocking_fast_forward` counts working-tree
   collisions. They are two different populations and their ratio is not a quantity. I wrote a
   prediction about the world and the instrument answered a different question — the shape
   `records/` already carries as *a pre-registered count predicts the INSTRUMENT, not the world*.
   Recording it rather than quietly rewriting it, because it is the fourth thing I predicted and
   the one I said I was most likely to talk myself into.

## The remedy, in the order the evidence supports

1. **The class fix: `advance_shared_tree` should judge with the BASE's rules, not the checkout's.**
   The question it asks is *"does origin/main supersede this copy?"* — that is origin's question,
   so origin's `stale_copy_refusal` is the right judge. Today the behind checkout grades itself
   with its own stale rulebook. This is the durable repair and it retires the whole class, not just
   rule 1b. It is its own careful piece of work (importing a module from a non-checked-out ref is
   not a one-liner) and it is handed on rather than half-built here.
2. **Until 1 lands, an inert-judge rule is invisible.** The cheapest one-leg control that would have
   caught this: `checkout_drift()` already knows the gap paths — assert that
   `tools/stale_copy_refusal.py` is not among them, or print it if it is. One field, and it turns
   this recursion from something only the seat can notice into a printed fact.
3. **The refresh-door rework (4 paths) wants a deliberate decision**, and it is the seat's: it is a
   concurrent fork carrying real new work whose base moved underneath it. Not a door either
   automatic classifier may walk.
4. `Verdict.by_clock` losing silently to the symbol reader when both are readable and they disagree
   is a separate, smaller defect. The verdict should say the base moved after the copy was taken
   even when it still prints the holder-work door.

## What this turn did NOT do, deliberately

Advance the shared tree, or clear any of another lane's working copies in it. The reconciler holds
the ahead leg and was mid-gate; four of the thirteen blockers are judgements the machinery
explicitly refuses to make unattended; and this invocation's isolation from the shared index is the
only reason it was allowed to run at all.

---

## 2026-09-24, +50 min — prediction 2 settled, and the new field earned its keep in public

The whole series, every reading from `deploy_restart.checkout_drift()` on the shared tree, taken
across this turn while `c72c41e4c` sat in its own gate:

| time | behind | ahead | contains_origin | gap_paths | stale_judges |
|---|---|---|---|---|---|
| 18:07 | 28 | 5 | False | 48 | *(field did not exist)* |
| 18:38 | 28 | 6 | False | 49 | `stale_copy_refusal`, `refresh_to_head` |
| 18:46 | 29 | **1** | False | 40 | `stale_copy_refusal`, `refresh_to_head` |
| 19:05 | **31** | 1 | False | 45 | `stale_copy_refusal`, `refresh_to_head` |

**Prediction 2 CONFIRMED, and by the exact mechanism predicted.** `ahead` fell 5 → 1 without any
act of mine — `origin_reconcile`'s merge closed it. `behind` did not fall with it: it ROSE, 28 → 31.
`contains_origin` was False at the start and False at the end, and the reason changed underneath it
from *diverged* to *merely behind*. This is the shape already in this seat's memory — *the ahead leg
closes and the behind leg grows, so `contains_origin` stays false for the opposite reason* — and it
is now measured end-to-end in one window rather than inferred across two.

It also disposes of the drawn item's framing. Closing the ahead leg was never the blocker a seat
needed to act on; the reconciler does it unattended and did it here within the hour. What no
cadence closes is `behind`, and what nothing at all noticed until this commit is that
`stale_judges` never moved off two names through the entire series.

**The field is not reporting a transient.** Both judges were stale at every reading, across four
merges, two of them landed by the reconciler and one by this lane. A wedge that persists through
three tree advances is not a race — and prior to `c72c41e4c` no surface anywhere printed it.

One thing this addendum deliberately does not claim: that `behind` rising is a defect. Origin is
being landed onto by several lanes continuously, so a growing `behind` on a checkout that never
advances is arithmetic, not pathology. The pathology is `contains_origin: False` holding for 30+
commits while every automatic remedy reports success — which is the finding above, not this table.
