**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `contain-the-site-pipeline-so-a-test-cannot-publish-a-degraded-feed-set`) · **Class:** controls_that_cannot_fail

# RESULT — the containment premise is spent, and the instance still holds at a HEAD four merges later

The item drawn this tick asked for two things. Both were already on `origin/main` when the tick
opened. This turn did not rebuild them; it **re-measured them at the current HEAD**, because the
evidence the item rests on is an empirical observation and code-reading is not the same check.

## The premise, re-measured

| Half of the drawn work | Where it landed | In `origin/main`? |
|---|---|---|
| Contain the pipeline against a test process | `aac7da7e2` — `guard_site_publish_pipeline`, `background/process_run_complete.py:3791`, called as the first statement of `generate_dashboard_json` | yes |
| Let the promotion refusal name the test-exhaust tell | `3a197acf4` — `_dirty_cause`, `tools/promote_worktree_landing.py:136` | yes |

`HEAD` and `origin/main` are both `d648c7e2a`. The prereg that drove the work,
`docs/staging/records/SEAT_PREREG_CONTAINING_THE_SITE_PIPELINE_2026-09-09.md`, already carries its
results beside its predictions (P1–P4 all confirmed).

Both control suites, run this turn: `tests/background/test_the_site_publish_pipeline_is_contained.py`
and `tests/tools/test_the_promotion_route_refuses.py` — **22 passed**.

## The independent re-measurement, and why it was worth the minutes

The prereg measured P3 at `b9ff0425b`. HEAD has since moved through several merges, and a control
that was green at the commit that landed it is not evidence about the commit you are standing on.
So the named instance was re-run in a **clean `git archive HEAD` extract** with a baseline commit,
never in the shared tree:

```
pytest tests/tools/test_website_integrity_fix.py   →  26 passed in 2.14s
git status --porcelain -- site/data site/state docs/state   →  0 lines
git status --porcelain (whole tree)                →  1 line
```

The one line is `M docs/observability/test_execution_log.jsonl` — machine churn, and already on the
`SHARED_BY_DESIGN` exclusion list that `_refuse_if_dirty` ignores by design. So it is not a leak.

Against the finding's original measurement, at the same test file:

| | dirty published-feed paths | `publish_steps.json` | wall clock |
|---|---|---|---|
| finding, at `c440337ad` | **27** (26 tracked + 1 new untracked) | degraded `true`, run_stamp `"unknown"`, 6 failing | 143.62s |
| this turn, at `d648c7e2a` | **0** | untouched | 2.14s |

The 140 seconds that went away were the pipeline republishing the live site from a test process.
That the runtime collapsed by the same fact that the dirt disappeared is the useful cross-check:
the guard is not merely making an assertion pass, it is stopping ~40 generators from running.

## The class leg is partial, and is reported as partial

The instance is one test file. The item's own evidence was `pytest tests/tools/` **entire**, so that
is the honest class measurement, and it was launched detached in the same clean extract. At the time
of writing it is **19% through with 0 dirty paths across the whole extract tree**. That is
consistent with containment and it is *not* a completed measurement — the run needs roughly another
fifty minutes and this is a bounded tick. **Nobody should read "0 dirty" here as the class result.**
If the remaining 81% turns up a second writer into the published feed dirs, that is a new finding
and not a regression of this one: the guard is keyed to one entry point by construction, and a
different door was never inside its claim.

## What is genuinely still open, carried forward from the prereg

Neither of these is owed by the drawn item; both are recorded so they are not rediscovered as new.

1. **The destination root is not built.** 92 modules under `tools/` and `background/` resolve their
   own output root at import time. The guard makes the pipeline *unreachable* from a test; it does
   not make it *redirectable*, so no test can exercise the pipeline end to end. Nothing needs to
   today. If one ever does, that is a migration, not a parameter — and a `dest_root` parameter
   accepted by 92 roots that ignore it would be a fake more permissive than its subject.
2. **The promotion refusal is blind to a feed a test CREATES.** It runs
   `git status --untracked-files=no` deliberately, so a test that only invents new feeds and
   modifies none trips nothing. Flipping to `--untracked-files=all` would refuse on ordinary machine
   churn and make the route unusable, which is the defect it exists to avoid. Closed for the site
   pipeline by the entry-point guard; the general hole stands.

Item 3 of the finding's own "what is next" — a general test-isolation harness — was declared **not
owed** there, and this turn agrees: it would be a control guarding our own controls.

## Disposition

`SEAT_FINDING_A_TEST_REWROTE_TWENTY_SIX_LIVE_FEEDS_INTO_A_DEGRADED_PUBLISH_STATE_AND_THE_ONLY_THING_THAT_NOTICED_BLAMED_THE_WRITER_2026-09-09.md`
is removed from the staging root in the same commit as this record. Both of its owed items are
landed and re-measured; its third was not owed. It stayed drawable after its work landed, which is
why this tick drew it again — the disposition, not the fix, is what was missing.
