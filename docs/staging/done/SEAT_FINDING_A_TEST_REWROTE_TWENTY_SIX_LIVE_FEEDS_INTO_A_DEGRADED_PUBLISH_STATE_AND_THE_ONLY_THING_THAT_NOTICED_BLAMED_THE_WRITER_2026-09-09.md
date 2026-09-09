**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `every-surface-that-still-says-our-advantage-is-selection-must-answer-the-nine-seed-floor`) · **Class:** controls_that_cannot_fail

**Discharged:** 2026-09-09. Both owed items landed and were re-measured at HEAD d648c7e2a. Item 1 by an entry-point refusal in aac7da7e2 rather than the destination-root parameter it asked for, because 92 modules resolve their output root at import and a parameter they ignore would read as containment while being a fail-open. Item 2 by the test-exhaust tell in 3a197acf4. Item 3 was declared not owed by this document. Re-measurement: the named test file is 26 passed in 2.14s leaving zero dirty published-feed paths, against 27 dirty and 143.62s when this was written. Result and the two carried-forward gaps: SEAT_RESULT_THE_SITE_PIPELINE_CONTAINMENT_PREMISE_IS_SPENT_AND_THE_INSTANCE_STILL_HOLDS_AT_A_HEAD_FOUR_MERGES_LATER_2026-09-09.md


# FINDING — a test rewrote twenty-six live feeds into a degraded publish state, and the only thing that noticed blamed the writer

Found on the way to something else: running `pytest tests/tools/` in a worktree left twenty-six
tracked files dirty, and `promote_worktree_landing` refused the promotion because of them. The
refusal was right to fire and wrong about why, and if the paths had gone into the commit — which a
`site/data/` pathspec routinely does — a **degraded feed set carrying no run stamp** would have
been published as if it were a run.

## What was observed

`git status` after `pytest tests/tools/`, in a tree that was clean of these paths at turn start:

```
 M site/data/{activity_cost,book_growth,capabilities_door,company,director_delta,evidence,
              explore_hh_days,knowledge_review,market,maturity_map,method,phases,premise_demand,
              proof,publish_steps,regulatory,sim_data,simplified,system_status,value_arms,
              world}.json
 M site/state/{PROJECT_STATE.txt,live_decisions_latest.json,scenario_analysis_latest.json,
                track_record_scorecard.json}
 M docs/state/sim_data.json
```

`site/data/publish_steps.json` — the artefact the staleness controls read — before and after:

| | `degraded` | `run_stamp` | `failing_step_count` | `stale_artefacts` |
|---|---|---|---|---|
| HEAD | `false` | `c440337ad` | 0 | none |
| after the test run | **`true`** | **`"unknown"`** | **6** | 4 |

All six failures name the same cause:

```
FileNotFoundError: '/tmp/pytest-of-rich/pytest-1373/test_generate_dashboard_json_r0/run.json'
```

A **pytest temp directory**, written into the repository's own published publish-state ledger.

## The mechanism, and the test names it itself

`tests/tools/test_website_integrity_fix.py::test_generate_dashboard_json_returns_gate_status` calls
`background.process_run_complete.generate_dashboard_json(tmp_path / "run.json")`. That function
unconditionally runs the whole site-regeneration pipeline — roughly forty generator calls. The test
mocks **three** of them. Its own comment says why, and says the rest of it out loud:

> *"most take json_path and fail fast on the nonexistent tmp_path/run.json (caught + logged), but a
> handful take NO json_path at all and **read/write real repo state regardless**, with no staleness
> gate this test can rely on"*

**The three mocks were chosen for COST, not for containment.** The comment is a throughput
write-up: `run_frozen_baseline.generate` (~117s), `generate_provisional_plan_data.main` (~57s),
`generate_test_mix_data.generate` (~47s). The reasoning is explicitly "these are slow and
orthogonal", and it closes with *"every other downstream generator in the pipeline is left real
since each already runs in well under a second"*. Cheapness was the admission criterion. Writing
into `site/data/` was known, written down, and never treated as a reason to mock anything.

So the population of generators that touch the real tree is **whatever is left after the slow ones
were removed** — and it is defined by a property (runtime) that has nothing to do with the property
that matters (does it write published bytes).

## Why nothing catches it, which is the part worth keeping

1. **The test passes.** It asserts one thing — `result is False` — and that is true whatever the
   pipeline wrote on the way.
2. **The site suite passes afterwards.** It reads the feeds; it does not know they were rewritten
   from a nonexistent run.
3. **`publish_steps.json` reporting `degraded: true` is not itself a red.** Degraded is a state the
   ledger is designed to be able to hold. Nothing compares "degraded because a publish cycle had a
   bad day" against "degraded because a unit test was the publisher".
4. **The one thing that noticed names the wrong cause.** `promote_worktree_landing` refused with
   *"the worktree has uncommitted tracked changes outside the directories where machine churn is
   expected, so this landing is not the whole of what was done"*. That sentence tells the writer
   they left work unfinished. The writer did not; a test wrote those bytes. A refusal that names a
   cause the reader can act on is the whole point of writing refusals that name their reason, and
   this one sends the reader to look for their own missing commit.

Item 4 is the one that makes this LATENT rather than RECORDED. The failure mode is not the dirty
tree — it is a writer reading that refusal, concluding "ah, my regenerated feeds", and adding
`site/data/` to the pathspec. **`run_stamp: "unknown"` and six pytest-tmpdir errors then land on
origin as a published run**, and every downstream staleness control keyed to that ledger is now
reading a unit test's exhaust as a publish cycle.

## What was done here, and how to reverse it

The twenty-six paths were **restored to HEAD**, not committed, after their bytes were copied out of
the repository to `/tmp/se_test_pollution_backup_2026-09-09/` (with `PATHS.txt` listing every one).
Establishing they were pollution rather than another lane's work took three checks, and all three
were needed: they were absent from `git status` at turn start; their mtimes fall inside this turn's
pytest window; and HEAD's `publish_steps.json` is clean where disk's is degraded. **The third is
the only one that distinguishes "a real publish ran" from "a test ran"** — the first two are equally
consistent with the publisher having done its job.

## What is next

1. **Contain the pipeline, not the slow parts of it.** `generate_dashboard_json` should take a
   destination root, or the test should point `PROJECT`/the site-output paths at `tmp_path`. Mocking
   by runtime leaves the containment property undefined, and the next generator added under a second
   is born writing the real tree.
2. **The refusal should be able to say "a test wrote these".** `promote_worktree_landing` already
   reads `git status`; a dirty `site/data/publish_steps.json` whose `run_stamp` is `"unknown"` is a
   cheap, specific tell it could name instead of the generic unfinished-work sentence. One leg, not
   a register.
3. **Not owed: a general test-isolation harness.** One test is the instance; the class is "a
   pipeline entry point with no destination parameter". Fixing the parameter fixes it for every
   caller, and a watcher over test side-effects would be a control guarding our own controls.
