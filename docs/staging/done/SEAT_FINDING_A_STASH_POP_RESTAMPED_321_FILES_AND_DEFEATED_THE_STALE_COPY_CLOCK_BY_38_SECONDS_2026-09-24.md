**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — a `git stash` pop restamped 321 tracked files and defeated the stale-copy clock by 38 seconds, so no door admits six gap paths

*Filed by the delivery seat from an isolated worktree, 2026-09-24. Claim id
`the-shared-checkout-cannot-fast-forward-and-five-of-its-six-gap-paths-are-pure-stale-copies`.*

## The state, measured not inherited

`background.deploy_restart.checkout_drift()` on `/home/rich/synthetic-enterprise`:

```
{"behind": 20, "ahead": 3, "contains_origin": false, "gap_paths": 36, "unresolved": null}
MISSING 20 commit(s) from origin/main (36 path(s) the daemons cannot load whatever their stamp
says; restarting them would clear the verdict and deliver none of it)
```

**`ahead` is 3, so "fast-forward" in the claim's own title is wrong.** The shared tree carries
three commits origin lacks (`526aa4f70`, `51aab95a8`, `224ed807c`), so the advance is a MERGE, not
an FF. That does not change the remedy — a merge is refused by the same dirty paths an FF is — but
it changes what "done" can mean: clearing the dirty paths lets the reconciler *merge*, and nothing
here can make the tree fast-forward.

## The duplicate-work check resolved: same id, not a rival id

The draw flagged `the-shared-checkout-cannot-fast-forward-...` as a live claim that "may be this
work under another name". It is not another name — it is **this very id**, sitting in
`.seat_work_in_hand.json` with `"paths": []` from a prior invocation. The two claim stores are
separate and `delivery_lane --release` does not clear `.seat_work_in_hand.json`, so a residue under
the same id is the expected shape, not a collision. **No disposition is owed; the work is unspent.**
Both stores are released at the end of this turn.

## The path list the item carried was stale, in both directions

The item named six contested paths and graded five of them against the shared tree's *behind* HEAD.
Re-measured against `origin/main` just now, the intersection of *in the gap* and *dirty* is **nine**
paths, not six:

| path | working copy vs origin/main |
|---|---|
| `site/test_the_book_is_bounded_by_compute_reaches_the_reader.py` | byte-identical |
| `tests/background/test_harden_rung_pass_ceiling.py` | byte-identical |
| `tests/tools/test_discovery_pass_ceiling.py` | byte-identical |
| `background/supervisor.py` | 18 working-only lines |
| `tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py` | 4 |
| `tests/background/test_publish_gate_subject_is_head.py` | 9 |
| `tests/background/test_publish_gate_wedge_draw.py` | 48 |
| `docs/observability/agent_status.json` | 11 (daemon-written state) |
| `site/data/tick_heartbeat.json` | 24 (daemon-written state) |

`background/delivery_lane.py`, which the item named, is **no longer in the gap at all** — the trunk
moved past the reading the item was written from. That is the item's own caveat coming true.

## PRE-REGISTRATION — written before `refresh_to_head --base origin/main` was run

Recorded here so the survey can refute it rather than confirm a story told afterwards.

1. The three byte-identical paths will be admitted outright: the base supersedes a copy equal to it.
2. The four code/test paths will be admitted, because reading their diffs against `origin/main`
   line by line shows the trunk strictly richer — every working-only line is an OLDER revision of
   prose the trunk replaced, or a superseded mechanism. Specifically
   `test_publish_gate_wedge_draw.py`'s working copy is 1341 lines against the trunk's 1463, is
   missing the whole AST `_kinds_written_by` rewrite, and its module-level `from background import
   process_run_complete as prc` exists only to serve the one-hop `getattr` resolver the trunk
   *deliberately deleted* ("no import, because importing a daemon to read a label is a side effect
   for a string"). Its only genuinely trunk-absent content is a 16-line banner whose substance the
   trunk carries in the test's own docstring.
3. The two daemon-written JSON artefacts will NOT be cleanly admissible, and even if they are the
   refresh will not hold: their writers are live and will re-dirty them within seconds.

**If (3) is right, clearing the seven code paths is necessary but not sufficient, and the residue
is a different class of problem — a live writer inside the gap, not a stale checkout.** That
distinction is the finding; it is not what the item predicted.

## Result — the pre-registration was REFUTED on point 2, and the refutation is the finding

`refresh_to_head --base origin/main` (survey), then enacted where admitted:

| path | verdict | what happened |
|---|---|---|
| `site/test_the_book_is_bounded_by_compute_reaches_the_reader.py` | `already_at_head` | nothing to do |
| `tests/background/test_harden_rung_pass_ceiling.py` | `already_at_head` | nothing to do |
| `tests/tools/test_discovery_pass_ceiling.py` | `already_at_head` | nothing to do |
| `background/supervisor.py` | `predates_landing` | **REFRESHED**, 18 lines preserved at `refs/preserved/refresh-to-head/seat-gap-supervisor` (`03cb5d7df`) |
| `tests/background/test_a_swept_row_names_...windows_commit.py` | `refused_head_does_not_supersede_it` | refused |
| `tests/background/test_publish_gate_subject_is_head.py` | `refused_head_does_not_supersede_it` | refused |
| `tests/background/test_publish_gate_wedge_draw.py` | `refused_supplies_names_head_lacks` (`prc`) | refused |
| `docs/observability/agent_status.json` | `refused_rival_values_no_key_the_base_lacks` | refused |
| `site/data/tick_heartbeat.json` | `refused_supplies_names_head_lacks` (8 keys) | refused |

Prediction 2 said the four code/test paths would be admitted because the trunk is strictly richer.
**Three of the four were refused.** Prediction 3 was right about the two JSON artefacts but for a
narrower reason than I gave. So the remedy the item prescribed clears **one** path, not five, and
the checkout is still `contains_origin: false`.

### Why the three were refused, and it is not what the refusal says

`refresh_to_head` tells the reader: *"the stale-copy control has NO complaint about this copy
against origin/main: it does not predate the last landing there ... Refreshing it would discard an
ordinary edit."*

**It is not an ordinary edit. It is a restored `git stash`.**

All three working copies are byte-identical to commit **`23e9917bc`**, whose subject is
`WIP on main: 51aab95a8 ...` — a stash object. The timeline, in UTC:

```
14:01:09Z  git stash          -> 23e9917bc snapshots the then-dirty tree
14:01:15Z  reflog: reset: moving to HEAD      (the stash's own reset)
14:01:53Z  b3aa159dd LANDS ON ORIGIN/MAIN     (another lane; carries the newer content)
14:02:31Z  stash restored     -> 321 tracked files rewritten, ALL stamped 14:02:31Z
```

`tools/stale_copy_refusal.taken_before` asks `committed_at(commit) > mtime`. The content was
snapshotted **44 seconds before** the landing; the mtime says **38 seconds after** it, because a
stash restore restamps every file it writes. So:

- `judge`'s rule-1 `any`-vouch does not fire (each copy happens to share ≥1 distinctive line);
- `judge`'s older-clock leg at line 1188 — the leg written for exactly this, whose docstring says
  *"a file that predates a commit cannot have been derived from it"* — **does not fire, by 38
  seconds**;
- `clock_judge` returns at line 1288 before asking anything, because `.py` is in `READABLE` — by
  design, and correctly, since rule 1 owns that suffix;
- so no door admits the copy, and the refusal asserts authorship it has not measured.

**This is the FAIL-OPEN direction on a control whose whole job is to catch a pre-landing draft.**
The clock is being read as evidence of authorship when it is evidence of a bulk restore: **321
tracked files share that one mtime to the second.** Six of the nine contested gap paths are in that
cohort. An mtime shared by hundreds of files is a write event, not an author.

### The repair, and why it is not a widening

The honest clock for these bytes already exists in the object store: **the stash commit's own
committer date**, `14:01:09Z`, which genuinely predates the landing. So `taken_before` should ask,
when the on-disk bytes are byte-identical to a `WIP on ...` object's blob for that path, that
object's committer date rather than the file's mtime.

That admits **exactly one population — copies that literally came out of a stash** — and for those
it is strictly more truthful than what it does now. It is not a threshold, not a dial, and it does
not reach a single copy some lane actually typed. It can be mutated: flip the stash date back to
the mtime and the three paths above go green again.

`23e9917bc` is preserved as `refs/preserved/shared-tree-stash-pop-2026-09-24` so the discard, when
it is licensed, is recoverable.

### And the upstream cause: `git stash` was used on the shared tree

`git stash` is on this repository's never-do list, and this is the bill. The stash is why the gap
paths are dirty at all, the pop is why the clock control cannot grade them, and the 44-second
straddle of another lane's landing is why the two facts point opposite ways. **Nothing else in the
tree can see this**: the reflog entry is a bare `reset: moving to HEAD`, and the `WIP on main:`
object is unreferenced once popped — it survives here only because this turn wrote a ref to it.

## Where this leaves the checkout

`contains_origin` is still `false`: `{"behind": 20, "ahead": 3, "gap_paths": 36}`. One of nine
contested paths cleared. The remaining eight split into two classes that need different doors:

1. **Six stash-restored copies** — blocked on the `taken_before` repair above. Do NOT force them:
   `--base-wins` is not licensed for them and `isolate_hunks` would land `prc` back over a trunk
   that deliberately deleted it.
2. **Two live daemon-written artefacts** (`agent_status.json`, `tick_heartbeat.json`) — a live
   writer inside the gap, which no refresh can settle because they re-dirty within seconds.

**The supervisor is still deliberately NOT restarted.** `checkout_drift()` is the reading that
matters and it says restarting "would clear the verdict and deliver none of it".

