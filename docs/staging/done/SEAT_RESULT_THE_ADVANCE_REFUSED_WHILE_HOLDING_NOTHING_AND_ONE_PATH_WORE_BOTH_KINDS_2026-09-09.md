**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The advance refused while holding nothing, and the 32-hour wedge was an arithmetic error

*Seat result, 2026-09-09. Lane 0: `publish-once-cleanly-and-take-the-refusal-at-the-instant-it-fires`.*

**Outcome: the shared tree is level with origin again — `dba27b77d`, 0 ahead / 0 behind.** It had
been 2 commits behind, with `last_clean_publish: null` and `wedge_since` 32 hours old.

---

## The drawn premise was spent, and spent differently than the item said

The item asserted that HEAD, the cached `origin/main` and the real remote *"all read `60bcdec35`
right now"*, and concluded the recorded `behind_origin` cause was therefore stale. Measured at draw
time:

| | item's claim | measured 2026-09-09 |
|---|---|---|
| HEAD | `60bcdec35` | `f0551719a` |
| real remote (`git ls-remote`) | `60bcdec35` | `dba27b77d` |
| relation | level | **HEAD 2 commits BEHIND** |

So `behind_origin` was **not** spent. It was live, and correct, and had been correct for 32 hours.
The item's own diagnosis — *"the count measures races lost rather than publishes prevented"* — is
what routed three previous stretches into the wrong place. This is the fourth reading of that cause
and the first one taken while it was true.

**The lesson is the one the item was reaching for and stated backwards:** a cause read from
`.publish_gate_state.json` and a cause re-measured at the instant it fires can differ in *either*
direction. The prior three stretches found it expired; this one found it live. Re-measuring is what
settles it — not a prior about which way the staleness runs.

## What actually held it

Exactly one path:

```
docs/staging/SEAT_PREREGISTRATION_WHAT_THE_FIXED_HORIZON_CUTS_OWN_NULL_INTERVAL_WILL_SAY_2026-09-09.md
```

**staged-deleted in the index, still present on disk.** That is both blocking kinds at once, and
both censuses in `paths_blocking_fast_forward` are right to report it:

* `git diff --name-only HEAD` reports it — the worktree copy differs from HEAD's copy.
* `git ls-files --others` reports it — the index has no entry for it.

Its bytes on disk hashed `75738ea13`. Origin's blob at that path hashed `75738ea13`. **Identical.**
The fast-forward was being refused on a file it was about to write back unchanged.

## The defect: two sides of one comparison were different domains

`background/origin_reconcile.py`, `advance_shared_tree`:

```python
resolvable = sorted(set(twins) | set(tracked))   # deduplicated set of PATHS
if len(resolvable) != len(blocking):             # list of (path, kind) ENTRIES
```

Both twin sweeps hash-proved the path, so `resolvable` deduplicated to **1**. `blocking` carried
**2** entries for that same path, one per kind. `1 != 2` → refuse.

**The refusal said so in its own words, every five minutes for 32 hours:**

> `0 of 2 blocking path(s) are NOT byte-identical to what origin brings, so clearing the 1 that are
> would delete files and still not advance. Nothing was removed. Held by: `

Zero held. One resolvable. Two blocking. And a refusal. The sentence is internally contradictory,
and the empty tail after `Held by: ` read as formatting.

R15 class: **a comparison whose two sides are different domains.** Not fail-open and not a
tautology — it fails *closed*, which is why it survived. A fail-closed counting error looks exactly
like a working protection, and the only tell it emitted was an empty list nobody had reason to read.

## The repair

The comparison is now over path sets on both sides, and is expressed as *which paths are held*
rather than as two lengths:

```python
blocked_paths = {b["path"] for b in blocking}
held = sorted(blocked_paths - set(resolvable))
if held:
    ...
```

This makes the domain error unrepresentable rather than merely fixed: `held` is the thing computed,
the thing tested, and the thing reported.

The clearing act is unchanged and correct for the both-kinds shape. The path is in `tracked_set`, so
it takes `restore_tracked_twin` (`git checkout HEAD -- <path>`), which clears the staged deletion
*and* the worktree difference. `unlink` would have left the index entry behind and kept the
fast-forward refused on a file no longer even on disk.

**Safety argument, unchanged from the sibling sweeps:** the path is only resolvable because its
working-tree bytes were hash-proven equal to origin's blob at the same path. Returning it to HEAD
cannot lose content origin already holds, and the fast-forward this unblocks writes those same bytes
back. Verified after the run: the file is on disk, tracked, clean, blob `75738ea13` — unchanged.

## Control: `tests/background/.../test_a_refusal_that_holds_nothing_wedged_the_tree_two_commits_behind.py`

The existing suite `test_the_twin_sweep_was_defeated_by_git_add.py` was **completely blind**: 9/9
pass against the exact defect that wedged the tree. Every case there gives each kind its own
distinct path, so it never constructs the duplicate.

Three controls, mutation battery run:

| mutation | result |
|---|---|
| restore `len(resolvable) != len(blocking)` (the original defect) | **2 red** (repair + property); old suite 9/9 green — the blindness, measured |
| `if not resolvable` (relax the safety property) | **1 red** (safety) |
| dedupe the *report* but keep entry-count arithmetic | **1 red** (safety) |

`test_a_refusal_always_names_at_least_one_path_it_is_holding` is keyed to the **property**, not to
this instance: a refusal on the twin comparison that can name no held path is an arithmetic error
whatever produced it. It runs over three shapes and catches the *next* domain mismatch here too.

## The repair reached origin

`5469f7b92`, pushed via the reconciler's own leg (`PUSHED: pushed 1 gated landing(s) that were
sitting local-only` — `surgical_land` never pushes). HEAD == remote == `5469f7b92`, 0 ahead / 0
behind. Receipt verified: `tree f62f3ea11, 3 path(s), gate-rc 0`.

## What is NOT done, and the honest reason

`last_clean_publish` is still `null`, and **it could not have been set by this turn.**

I first wrote here that the next thing in front of this lane was the level-promotion gate, because
that is what the last recorded failure names (`non_test_gate_refusal`). **That was wrong, and it is
the same mistake this item has now cost four stretches.** Two measurements, both taken after the
fork closed:

* `python3 tools/level_promotion_gate.py` at the new HEAD → **rc=0, no output. Green.**
* The recorded failure is keyed to `git_hash: 7e699a126`. By `publish_cause`'s own contract a record
  keyed to a different commit is `UNATTRIBUTED` for any current cycle. **It is evidence about a
  cycle that no longer exists**, and I read it as a live cause for the second time in one turn.

The actual reason is structural and has nothing to do with a gate: **there is no pending
`run_complete_*.md` marker.** The publisher is marker-driven — `process_run_complete.main()` takes
one marker path, and markers are produced by a sim run. With no marker there is nothing to publish,
so `last_clean_publish` stays `null` however healthy the tree is. `docs/observability/` holds none.

So the done-condition as written (`last_clean_publish` non-null) is **not reachable from a repair
turn at all** — it needs a sim run first. What this turn could do, it did: the 32-hour fork that
would have refused that publish is closed, and the tree is level with origin.

## For whoever picks this up

1. **Do not read `.publish_gate_state.json`'s `failures[-1].cause` as live.** Check its `git_hash`
   against HEAD first. Three of the four wrong diagnoses on this item, including one of mine in this
   turn, came from that field. The re-test-before-counting fix the item proposes is right, and its
   motivation is now measured: not that causes expire, but that a cause is only worth counting — or
   paging on — **if it is still true when read**.
2. The next real question is whether a sim run's marker now publishes cleanly. The fork is closed
   and the level gate is green, so the preconditions hold for the first time in 32 hours.
3. `episode_failures: 32` still counts refusals nobody re-tested. That count is not evidence of 32
   prevented publishes.
