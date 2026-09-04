**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# A background test regenerates three live data feeds into the tree, and truncates one by 87%

*Delivery seat, 2026-09-04, found while landing
`decide-the-proposal-side-of-a-low-water-episode-field-2026-09-04`. Not that claim's subject —
it is what refused that claim's promotion.*

---

## What happens

Running `tests/background/test_process_run_complete.py` writes three **tracked, committed** files
in the working tree:

```
 M docs/market_data/grid_intensity_feed.json     2314 lines -> 293   (2027 deleted)
 M site/data/explore_carbon.json
 M site/data/weather.json
```

Reproduction, from a clean tree, ~40 seconds:

```bash
git status --short docs/market_data/grid_intensity_feed.json   # clean
python3 -B -m pytest -q -p no:randomly tests/background/test_process_run_complete.py
git status --short docs/market_data/grid_intensity_feed.json   # ' M'
```

Bisected against five sibling publish-path suites (`test_publish_scope`, `test_publish_gate_scope`,
`test_publish_freshness`, `test_published_provenance_is_real`, `test_publish_decoupling_exit`) —
none of them touches the files. Only `test_process_run_complete.py` does. The route is
`background/process_run_complete.py`, which names all three feeds and drives
`tools/generate_grid_intensity_feed.py` and `tools/generate_explore_carbon.py`; the test reaches a
real publish path whose generators are not redirected, so they regenerate from whatever local data
the test environment has and write the result over the committed artefact.

## Why this is BLOCKING and not housekeeping

**It refuses landings.** `promote_worktree_landing` correctly reads a tracked change outside the
machine-churn directories as "this landing is not the whole of what was done" and refuses. That is
exactly what happened to this turn: a full `tests/background/` run at 16:34:56 BST dirtied the
three files, and the promotion of an already-gated commit was refused until they were restored by
hand. Any turn that runs the background suite before landing hits this.

**The truncation is the dangerous half.** `grid_intensity_feed.json` does not merely get rewritten
— it loses 2027 of 2314 lines, because the regeneration runs against whatever the test environment
could reach rather than against the record the committed file holds. A shorter feed is not an
obviously-broken feed; it is a plausible one.

**And there is a route for it to land.** The publish daemon commits generated site output it finds
in the tree. `site/data/explore_carbon.json` and `site/data/weather.json` are exactly that shape.
A truncated feed written by a test, sitting in the tree when the daemon sweeps, is committed as
data — with no source change beside it to make anyone look.

**It is also a test manufacturing the evidence a control reports on** — the same class the episode
guard's own suite has a fixture docstring about, caught in the act on 2026-08-10:

> the moment the recorder gained a second state path, running this suite wrote
> `docs/observability/.wedge_suspect_hit_rate.json` into the live tree — a test manufacturing the
> very evidence a control reports on.

That fix isolated the paths the recorder was *known* to use. This is the same defect one publish
stage further out, and the same remedy applies: isolate the paths the path under test is known to
write, not the ones a test happened to need.

## What I did and did not do

Restored all three from `HEAD` (via `git show HEAD:<path> > <path>`, not `git checkout`) so the
landing could promote. **I did not fix the test** — the claim in hand was the episode guard's
proposal side, and silently widening a landing to cover an unrelated suite is how a commit stops
being reviewable. It is written down here instead, at the severity it earns.

## The narrowing that is still owed

Which test *within* `test_process_run_complete.py`, and which generator call escapes redirection.
The bisect above stopped at file granularity because the claim in hand was elsewhere; the next step
is a `-k` bisect over that file with the three mtimes watched, which is the same shape as the loop
that found it and costs about a minute.
