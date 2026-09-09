**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `contain-the-site-pipeline-so-a-test-cannot-publish-a-degraded-feed-set`) · **Class:** controls_that_cannot_fail

# PRE-REGISTRATION — containing the site pipeline against a test-process publisher

Written BEFORE the measurements below were run. Predictions recorded so the result can refute them.

## The subject

`background.process_run_complete.generate_dashboard_json` runs ~40 generators, most of which
resolve their own output root at import time (`Path(__file__).resolve().parents[1]`). Measured
before writing this: **92 modules** under `tools/` and `background/` reference `site/data`.

## Predictions

**P1 — the premise still reproduces.** Running
`tests/tools/test_website_integrity_fix.py::test_generate_dashboard_json_returns_gate_status`
alone, in a tree clean of those paths, leaves **≥20 tracked files dirty** under `site/data/`,
`site/state/`, `docs/state/`, and flips `site/data/publish_steps.json` to `degraded: true` with
`run_stamp: "unknown"`. *(The finding measured 26 at commit `c440337ad`; HEAD has moved, so the
count is a prediction, not a restatement.)*

**P2 — a destination-root PARAMETER cannot be honoured in one turn, and I predict it would be a
fake.** If `dest_root` were added and passed a `tmp_path`, I predict the dirty-file count would
**not** drop to zero, because the generators resolve absolute roots at import and never consult a
caller's parameter. A parameter that is accepted and not honoured is a fail-open dressed as
containment (R15: *a fake more permissive than its subject*). **If this prediction is wrong — if
the generators do route through a redirectable seam — the parameter is the better fix and I will
take it.** This is the prediction I most want refuted, because refutation is cheaper.

**P3 — the refusal contains it.** With a fail-closed refusal at the pipeline entry, keyed to
`live_ledger_guard.in_test_process()`, the same run leaves **zero** tracked files dirty.

**P4 — the refusal is reachable, and provably so.** Before asserting what the guard refuses, a
poison round must show the unguarded path CAN be taken. I predict the pipeline entry is reached by
at least one test today (the one above), so the guard is not born unreachable.

## What would make me wrong about the whole approach

If a substantial number of tests call this entry point deliberately and depend on it writing the
live tree, then a refusal wedges the suite and the containment has to be staged instead. Census
before landing.

## The second leg (no prediction needed — it is a message change)

`promote_worktree_landing` refuses with *"the worktree has uncommitted tracked changes ... this
landing is not the whole of what was done"*, which sends the writer to look for their own missing
commit. A dirty `site/data/publish_steps.json` whose `run_stamp` is `"unknown"` is a test's
exhaust. The refusal should name that, because a refusal that names its reason is how the reader
finds out the refusal was about something else.

---

# RESULTS — written after the runs, beside the predictions that earned them

## P1 — CONFIRMED, and understated

`pytest tests/tools/test_website_integrity_fix.py::test_generate_dashboard_json_returns_gate_status`
alone, at `b9ff0425b`, against a tree measured clean (`git status --porcelain -- site/ docs/state/`
→ 0 lines). **1 passed in 143.62s**, and:

| | `degraded` | `run_stamp` | `failing_step_count` |
|---|---|---|---|
| before | `false` | `c440337ad` | 0 |
| after | **`true`** | **`"unknown"`** | **6** |

**27 paths, not 26** — 26 tracked, plus one the original finding did not report:
`?? site/state/live_decisions_20260908.json`, a **newly created untracked feed**. See the recorded
gap below; this matters more than the count.

## P2 — CONFIRMED, and it is why there is no `dest_root` parameter

Measured: **92 modules** under `tools/` and `background/` reference `site/data`, and each resolves
its own root as `Path(__file__).resolve().parents[1]` **at import time**. There is no seam a caller
can pass a destination through. A `dest_root` parameter would have been accepted and ignored — a
fake more permissive than its subject, reading as containment at every call site. I wanted this
prediction refuted because refutation was the cheaper fix; it was not refuted, so the parameter is
**not** written and the destination-root work is recorded as a named gap instead of a placeholder.

## P3 — CONFIRMED

With `guard_site_publish_pipeline` at the entry point: **0 dirty paths**, and the same test file
runs in **2.83s instead of 143.62s**. The 140s was the pipeline republishing the live site.

## P4 — CONFIRMED by the poison round, which ran BEFORE the guard existed

The unguarded path was reachable and *was being taken* — that is what the 27 dirty files are. The
guard's tests are therefore not born green. The poison round is recorded in the test file's own
section header so the next reader does not have to take this on trust.

## An assumption that was checked and held

I predicted a refusal might wedge the suite if many tests depend on this entry point. Censused:
**four** tests reach it and **three already monkeypatch it away** — one saying why in its own
comment, *"generate_dashboard_json writes to the REAL site/data/dashboard.json ... mock it to avoid
corrupting the live dashboard"*. The class was known and solved three times as an instance. The
refusal costs the suite nothing.

## RECORDED GAP 1 — the destination root is not built

Threading a real destination root through those 92 import-time roots is the correct fix and is
**not done**. The guard makes the pipeline unreachable from a test; it does not make it
*redirectable*, so no test can exercise the pipeline end-to-end. Nothing needs to today. If one
ever does, this is the work, and it is a migration, not a parameter.

## RECORDED GAP 2 — the refusal is blind to a feed a test CREATES

`promote_worktree_landing` runs `git status --untracked-files=no` **by design** (untracked files
are the machine's data overlay). So the 27th path — a *new* feed a test invented — is invisible to
it, and would have stayed invisible even with this turn's tell. A test that only creates feeds and
modifies none would trip nothing at all. Not fixed here: flipping to `--untracked-files=all` would
refuse on ordinary machine churn and make the route unusable, which is the defect it was built to
avoid. The entry-point guard closes this for the site pipeline; the general hole stands.
