**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The fifty-eight-failure publish episode has no red test, and the wedge is a merge-to-push race

*Worker, 2026-09-17, scheduled tick. The drawn item directed: "DIAGNOSE the failing test with
evidence (R9) ... FIX the red test". **There is no red test.** What follows is the measurement that
refutes the premise, kept beside it rather than replacing it.*

## 1. The drawn premise is REFUTED, and the record already said so

The item's frame — a red test wedging the gate — is contradicted by the gate's own state file at
the moment the item was drawn. `.publish_gate_state.json` carried `blocking_tests: []`,
`total_red: 0`, and `red_census: fail_fast_only`. Every one of the last three recorded failures is
either `kind: commit_did_not_land` or `cause: unattributed`. None names a test.

The in-flight run the item told me to wait for (PID 2019790, `run_complete_20260917T072251Z.md`,
~30 min) settled it first-hand. Failure #58:

```
kind  = commit_did_not_land
rc    = 77
cause = push_never_landed
reason= the publish COMMIT did not land ... -- the publisher's own scoped suite was GREEN
```

**The suite was GREEN.** The episode is 58 consecutive *publishing* failures, not 58 red tests.
Every hour spent looking for a red test is an hour spent on a test that does not exist.

**One further claim in the item is wrong.** It states "no report-only census is on record".
`tools/enumerate_publish_gate_reds.py` exists and is exactly that instrument — the director's own
`DIRECTOR_PRIORITY_ENUMERATE_THE_STACK_2026-08-10`, gate-identical scope with `-x` asserted
removed. Its artefact `docs/observability/publish_gate_red_census.json` is real but dated
2026-09-03 (1 red, `test_derived_artefact_register.py::test_every_registered_artefact_is_currently_fresh`).
So the census is **stale, not missing** — a materially different repair. I did not re-run it: the
item correctly forbade a second full suite beside the live one on this cgroup.

## 2. What the wedge actually is

A race between the reconciler's gate and a sibling lane's push cadence.

| Measured | Value |
|---|---|
| `origin_reconcile` merge→gate→push, end to end | **556 s** (~9.3 min) |
| Sibling lane (`W1_14`) push interval at the time | **~10 min** (`cef62f22e` +88s, `c57a03f6d` +10m, `d4a57f17f` +24m) |

The reconciler merges, gates clean, then pushes. Origin moves during the ~9 min gate. The push is
rejected non-fast-forward, and the gate run is spent. That is the whole mechanism, and the margin
between 9.3 min and ~10 min is why it sometimes wins and mostly does not.

First pass this turn: `REFUSED_RACE` — "the merge gated clean and origin moved before the push
landed". Second pass: **won**.

## 3. Outcome — the publish commit is on origin

```
git merge-base --is-ancestor 84c8bdee7 origin/main  ->  YES
```

Publish commit `84c8bdee7` (263 `site/data/` files, `docs/reports/ANNUAL_REPORT.md`,
`docs/status/LATEST.md`, net £158,380, generated `2026-09-17T07:53:12Z`) **reached origin**, and
the `run_complete_*` queue is empty. The fork with origin was fully disjoint when I closed it —
zero common paths between the publish commit and the four origin commits (publish surfaces vs.
`sim/weather_ingestor.py`, `docs/institutional/knowledge_map.md`, `tools/build_weather_world.py`).

**Stated honestly: this is not a gate-graded clean publish.** `episode_failures` is still 58,
`last_clean_publish` is still `null`, and `episode_clean_publishes` is still 0 — because the commit
reached origin through my manual reconcile, not through a publish cycle the gate itself graded.
The blocker is cleared; the episode counter is not, and only the next cadence can clear it.

## 4. A second, separate defect found on the way

`background/origin_reconcile.py:1287` — the `NOT_ADVANCED` verdict.

The branch fires on `still_behind` **alone**, and then hard-codes a cause it has not measured:

> "This is NOT a closed fork -- origin moved and this tree did not, which is precisely the state
> that loops if it is retried on a cadence."

At the moment it printed that sentence, both halves were false:

- **`ahead == 0`.** The push had succeeded and `84c8bdee7` was on origin. The fork *was* closed.
  The tree was merely *behind*. "Behind" and "not a closed fork" are two different quantities and
  this branch reads one for the other.
- **Retrying does fix it.** The advance failed on `Unable to create '.git/index.lock': File
  exists` — a sibling lane's `git commit` (PID 2123356, started 09:26:24, blocked in `do_wait` on
  its pre-commit hook chain, committing `docs/direction/DIRECTION.yaml`). A transient lock held by
  an in-flight sibling commit clears by itself. The sentence asserts the precise opposite of the
  truth, in the one case the operator most needs to distinguish.

To its credit the verdict *does* print git's own words underneath, so the evidence to refute it is
in the same string as the wrong claim. But the graded status and the leading sentence are what a
cadence and a draw read.

**The shape is familiar:** a verdict keyed to *today's answer* (still behind ⇒ must be the
origin-moved loop) rather than to *the property* (is the fork actually open? did the advance fail
for a cause that self-clears?). `_blocking_clause` already distinguishes dirty-tree collisions from
everything else; lock contention is a third case with no branch of its own.

**Remedy (not implemented this turn, and deliberately so):** split `NOT_ADVANCED` on the evidence
already in hand at that line — `ahead` (is the fork open at all) and whether `adv["reason"]`
matches a lock-contention shape. A self-clearing lock deserves its own status that a cadence reads
as "retry, nothing owed", which is what `REFUSED_RACE` already does one branch up. I am leaving it
un-coded because the reconciler is on the publish path, a sibling lane holds the index right now,
and landing a change to the module that just unwedged publishing — during the same tick, on a tree
5 commits behind — is how the next episode starts.

## 5. The static-quality ratchet red is working-tree pollution, and it is NOT at HEAD

Running the cheap gates before landing, `tests/architecture/test_static_quality_ratchet.py` was red:

```
changed: {'I001': (1308, 1307)}
```

One violation FEWER than the frozen baseline — the "ratchet red as good news" shape, which is
normally the tell that a file stopped parsing and took its violations with it. I checked that
first, and the check was *positive*: `ruff check --statistics` reports `1 invalid-syntax`, at
`company/trading/emir_reporting_register.py:108` — a PEP 701 nested-same-quote f-string that this
tree's Python 3.14 executes happily but that ruff, pinned `target-version = "py311"`, cannot parse.

**That turned out not to be the cause, and I record it because it nearly was.** The frozen baseline
*already contains* `invalid-syntax: 1`. It was frozen while that file was unparseable, so the
absence was baked in, not new. I fixed the f-string, confirmed the UTI output byte-identical
(`GBABCDEF20260917TRD-00001`), and the I001 count **did not move** — the file has sorted imports
and was hiding nothing. So I reverted it to HEAD's bytes rather than carry an unrelated
`company/` change and a baseline re-freeze into a publish-wedge tick.

The actual cause, established in a **full clean `git archive` extract of HEAD** (2,940 Python
files, `ruff.toml` present):

```
1308  I001   [*] unsorted-imports
   1         [ ] invalid-syntax     <- exactly the frozen baseline
```

**The ratchet is GREEN at HEAD.** The red lives entirely in the shared working tree: 21 of the 63
modified `.py` files carry an *uncommitted* import-sort fix by other lanes (`background/supervisor.py`,
`background/process_run_complete.py`, `tools/level_promotion_gate.py`, …). Their work is an
improvement; it simply has not landed yet, and the baseline is correctly keyed to HEAD.

**So the baseline must NOT be re-frozen to 1307.** Doing so would bake twenty-one other lanes'
uncommitted edits into a committed claim — sweeping their work into my commit, and going red on
them the moment any one of them reverts. This is the wedge `tools/surgical_land` exists for: it
gates HEAD-plus-my-hunks, which is the tree my commit would actually create, and that tree is
green.

*Method note for whoever repeats this: my first attempt compared a SPARSE extract (only the 63
modified files) and reported 21 spurious differences. A sparse tree changes ruff's isort
first-party inference, so the comparison was meaningless even with `ruff.toml` copied in. Only the
full-tree extract is a valid subject.*

## 6. What I did not do

- Did not run the gate argv or the census beside the live run (item's own instruction; OOM risk).
- Did not touch `.git/index.lock`. It is held by a live sibling `git commit`, verified by PID,
  start time and wait state — not stale.
- Did not fast-forward the local tree. It is 5 behind for exactly as long as that sibling commit
  holds the index, and that is correct behaviour, not a wedge.
- Did not re-freeze the ruff baseline, and did not land the `emir_reporting_register.py` f-string
  fix. Both are defensible on their own merits and neither belongs in this tick — see §5.

**Director notified** on NTFY (`publishing_down`, id `NchRoDuZhj2J`) with the one-line cause.
