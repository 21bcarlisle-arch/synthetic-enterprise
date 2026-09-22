**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# The publish wedge is a fixture that pinned two of the three windows its guard reads, and the chain's dearest control walked the tree twice

**Filed** 2026-09-18 · worker · lane 0 delivery
**Item** `cut-the-hook-chain-because-the-only-remaining-move-when-the-floor-meets-the-ceiling-is-a-cheaper-chain`

> **The 13-cycle publish wedge is not a fault in the publish guard: it is a fixture that pinned two
> of the three windows the guard reads, so a third window added inside it returned `None` on every
> leg and two publish-expecting controls went red at origin/main. Repaired, mutation-proven, and
> the function that caused it — which had NO control of any kind — now has five. Separately, the
> dearest single file in the always-run control set walked the whole committed tree twice per run;
> it now walks once, measured one-variable in one extract at 42.36s → 22.47s.**

---

## The premise held, and the commit the item cites is the analysis, not the remedy

The draw's premise check reported `34b817d83` already an ancestor of `origin/main`. It is — that is
the commit that FITTED the +6.3%/day growth rate. Nothing in it makes the chain cheaper, and no
commit since does either. The premise is intact and I carried on.

## Measurement: the second date the item said did not exist

`tools/time_the_commit_hook_chain.py --control-set`, shared tree, 2026-09-18T01:12Z, HEAD
`49e08b13b`. Against the only previous run (2026-09-17, transcribed from the sibling result):

| | 2026-09-17 | 2026-09-18 |
|---|---|---|
| always-run control set, ONE pytest run | 185.4s | **155.2s** |
| `site_lane_gate` | 142.9s | **149.8s** |
| `startup_anchor_freshness` | 33.6s | **1.8s** |
| `test_a_control_reads_python_as_code.py` | 45.6s | 40.1s |
| `test_publish_scope.py` | 39.4s | 33.5s |

**The 09-17 cut is confirmed live, not merely committed:** `startup_anchor_freshness` 33.6s → 1.8s.
**`site_lane_gate` is now the single largest step and it GREW.** Both runs are contended — another
lane's full suite was running throughout this one — so a 5-10% difference between them attributes
nothing; the 18x and the growth of the largest step are outside that.

Both dates are now in `docs/observability/commit_hook_step_timings.jsonl`, machine-readable, one
line per run, carrying the commit. **That file is why this turn had to re-take the measurement
before it could start.** The first run wrote its numbers behind an optional `--json` nobody passed,
so the readings survived only as a table inside a prose document; the tool now appends by default
and `--no-series` is the opt-out. The 09-17 row is marked `"partial": true` and `"commit": null`,
because the document states its eight dearest steps and does not name the tree it measured — an
absent step in that row is NOT a zero.

## The 13-cycle publish wedge: four of the six blocking tests were already green

`.publish_gate_state.json` named six blocking tests. Re-graded in a clean `git archive` extract of
`origin/main` (the recorded reds were measured on diverged trees and say nothing about the shared
branch): the four in `test_a_multi_chain_landing_is_not_recorded_as_one_chain.py` PASS. Two are
genuinely red at origin/main, and they are both in
`test_the_publish_refusal_asks_whether_the_fork_touches_its_own_paths.py`.

**The cause.** `_divergence_refusal` reads three windows onto the world: how far origin is ahead,
what paths origin is bringing, and — added 2026-09-17 — whether a previous publish commit is
already stranded on our side of the fork. The first two are pinned by the fixture. The third,
`_unabsorbed_publish_commits`, shells out to `git rev-list --count FETCH_HEAD..HEAD`. **A test tree
has never fetched, so there is no `FETCH_HEAD`, so rev-list exits non-zero, so the function returns
its fail-closed `None`, so the refusal fires on every leg** — including the two that exist to prove
the guard can publish at all.

The R15 reachability control did its job: `test_both_sides_of_the_new_branch_are_reachable` is
written over the whole partition precisely so a guard that refuses everything cannot pass. It went
red immediately and correctly. What failed is that the red then stood for a day and wedged every
publish behind it.

**`_unabsorbed_publish_commits` had no control of any kind.** It is the function that shipped the
wedge, and nothing in the tree could fire on it.

### What landed

`_arrange` now pins the third window, and the ceiling has five controls of its own — three against
a REAL temporary repository rather than a stubbed `subprocess`, because the whole defect is about
what git does when the ref it names is absent, and a stub cannot be wrong about that.

Every one is mutation-proven in the extract, each firing on its own named defect:

| mutation | control that fires |
|---|---|
| `returncode != 0` → `return 0` | `test_a_missing_FETCH_HEAD_is_NOT_established_and_never_zero` |
| `stranded is None` branch removed | reachability partition + `..._refuses_rather_than_guessing` |
| `-- <paths>` dropped from the rev-list | `test_the_ceiling_counts_the_commits_that_actually_write_the_surface` |
| `if stranded:` branch removed | reachability partition + `..._refuses_and_says_how_many` |

**The second layer of the wedge, which this does NOT clear and which is nobody's defect.** The
shared tree is 4 ahead / 14 behind, and two of those four local commits (`77f4a1e53` the liveness
heartbeat, `0ccf6c97a` the paused banner) ARE publish-surface commits. So once the reds are gone,
`_unabsorbed_publish_commits` will correctly count 2 and correctly refuse: two unpushable copies of
the same surface is the 2026-09-01 shape and the ceiling exists to say so. **The remaining remedy is
`origin_reconcile`, not another repair here.** Said plainly so the next turn does not read a
continuing refusal as this repair having failed.

## The cut: the dearest always-run control walked the tree twice

`tests/architecture/test_a_control_reads_python_as_code.py` is 40.1s of a 155.2s control set. It
censused the whole committed `tests/` + `tools/` + `background/` tree TWICE per run — once for its
vacuity guard through `_real_tree()`, once through `census.check(REPO)` — over the same tree at the
same commit, so the two could not disagree.

`check()` now takes an optional `scans`, and the floor test hands it the walk `_real_tree()` already
took. **One variable, one extract, one box: 42.36s → 22.47s** (and 68.3s under the mutation below,
which is three walks — the clearest evidence the parameter is doing the work).

The parameter's own risk is that it is accepted and ignored, which would leave the floor green,
byte-identical and exactly as slow — a cut that reads as landed and delivers nothing.
`test_a_handed_in_census_is_what_the_floor_is_graded_against` grades both directions of the
comparison over a synthetic row set sharing no member with the real tree, so a hidden walk reddens
all three legs. **MUTATION: `census(root)` unconditionally — fires.**

## What I measured and did NOT cut, with the reason

1. **`site_lane_gate`, 149.8s — now the largest step, and it grew.** `pytest site/` is 82.3s in a
   clean extract with 67 skipped, because the extract has no `node_modules` and the browser legs
   skip. The 51s of module-scoped fixtures the 09-17 result named are in that skipped population,
   so **this cannot be attributed from an extract at all** — it needs a `git init` extract with
   `node_modules` symlinked, which is the shape this repo has paid for before. Bigger than the
   remainder of this turn, and the largest lever left.
2. **`test_publish_scope.py`, 33.5s.** Six tests at 4.7-6.2s each; five call
   `publish_scope.resolve_scope()`, and **only three of the five are unpatched** — two monkeypatch
   the selector and must not share a cached value. A shared fixture over the three saves ~9s. Not
   taken this turn because the honest version has to distinguish the patched calls, and a fixture
   that cached across them would disarm two mutation controls to save nine seconds.
3. **`pytest-xdist` is still not installed.** 16 cores idle through a 155s serial run. A real-world
   action; it belongs to the director, and it remains the single largest available lever.

## Arithmetic on the deadline, stated so it can be refuted

The control set fell 185.4 → 155.2 and this turn takes ~20s more off its dearest file. Against
+6.3%/day that is worth roughly two days of headroom before the 660s staleness assert, not a
reprieve. **The wall is unchanged and the prediction stands:** without the site lane, the chain
meets its ceiling inside a fortnight.
