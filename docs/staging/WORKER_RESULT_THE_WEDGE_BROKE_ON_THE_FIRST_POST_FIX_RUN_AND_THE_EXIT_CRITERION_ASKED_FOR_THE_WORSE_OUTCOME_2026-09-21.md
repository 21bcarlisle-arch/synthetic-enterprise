**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the wedge broke on the first post-fix run, and the exit criterion asked for the worse of the two outcomes

**Filed:** 2026-09-21, 19:20 local. Drawn as Lane 0 delivery,
`nothing-has-reached-a-reader-for-45-hours-and-the-fix-is-unpushed`.

---

## The headline

**A figure is in front of a reader.** `60c8c1d4b Auto-process run complete: report + LATEST.md +
site/ (git=87b25d6da, net=£158,278)` is committed, pushed, and `HEAD == origin/main`. The publish
gate state written at 18:15:57Z records `total_red: 0`, `blocking_tests: []`, `episode_failures:
19 → 0`, `wedge_since: None`, and `last_clean_publish: 2026-09-21T18:15:57Z` — the first since
2026-09-19T19:57:19Z. **A 46.3-hour publishing outage, 44.0 hours of it formally wedged, is over.**

Both queued markers (`run_complete_20260921T131342Z`, `run_complete_20260921T152931Z`) drained to
`docs/staging/done/`. The queue is empty.

## What the item asked, and what was already true when it was drawn

The item had three ordered steps. **Two of the three were already spent before this turn began**,
and establishing that was the first thing done rather than the last.

**(2) PUSH — already spent.** The item said `git log origin/main..HEAD` held exactly two commits.
At this turn's first measurement, after `git fetch`, it held **none**: `12f4073ed` and `8062b2265`
had both already reached origin by another route. Nothing was pushed by this turn.

**(1) READ THE GATE STATE AND CHECK ITS MTIME — the warning was right, and then it expired.** The
item predicted the state file would be the stale 16:59:48Z one. It was not: mtime was **17:34:13Z**,
written *after* `12f4073ed` landed at 17:13:17Z. But the item's underlying caution survived its own
literal: **mtime post-fix, measurement pre-fix.** That record's own `red_at_head_reason` said the
red was measured at `git=afae0e321` — which `git rev-parse 12f4073ed^` confirms is **the parent of
the fix**. So the 19th failure was graded on the pre-fix tree, exactly as the item warned, and was
not evidence about the fix. *A state file newer than HEAD is still stale evidence if the tree it
graded is older than HEAD. The mtime is the cheap half of the check; `red_at_head` is the real one,
and the file already carried it.*

**The blocking test is genuinely green at HEAD.** Confirmed in a clean `git archive HEAD` extract,
never in this worktree (the gate grades a throwaway HEAD checkout):
`tests/background/test_episode_prior_partition.py` → **60 passed**.

## How the verdict was actually obtained

Not by reading a file, and not by re-running the gate by hand. **A `process_run_complete` was
already in flight** — PID 1183179, started **17:42:28Z, twenty-nine minutes *after* the fix
landed**, with its pytest gate (PID 1209548) started 17:50:09Z. That run *was* the first post-fix
grading the item asked to wait for. It was waited out on `tools/wait_for.py --pid` (not a
hand-rolled poll, not `pkill`), finished after 555s, and its state file is the one graded above.

So step (3) — "if the first post-fix gate state still names a red, name the second cause" — **does
not apply. There was no second cause.** The episode-prior repair was the whole of it.

## The finding: the exit criterion asked for the worse of the two outcomes

The item's FINISHED test was:

> `episode_clean_publishes` is non-zero in a gate state written AFTER `12f4073ed`

**That is unsatisfiable in the success case it was written to detect.** In
`background/process_run_complete.py::record_publish_gate_success`:

```python
episode_closed = (pending == 0)
episode_clean  = 0 if episode_closed else ((int(prev_clean) if isinstance(prev_clean, int) else 0) + 1)
```

and `background/episode_monotonic.py::guard_episode` returns `new` untouched when
`episode_closed=True`, so the proposed `0` stands against the high-water guard.

`episode_clean_publishes` is **episode-scoped, and correctly so** — its own docstring says it exists
to tell *"the gate cannot pass"* apart from *"the gate passes and the queue outruns it"*. It is
non-zero **only while the episode stays OPEN**, i.e. the gate passed but markers are still queued —
the *partial* recovery. A **full drain closes the episode and resets it to 0 alongside
`episode_failures`**, which is the *better* outcome. The observed state is `episode_failures: 0,
episode_clean_publishes: 0, wedge_since: None` — the complete recovery, reading 0 on the one field
the criterion asked about.

**Taken literally, the criterion would have graded this success as a continuing wedge**, and the
honest next move would have been to go hunting for a "second cause" that does not exist.

The field that *does* carry the positive evidence is **`last_clean_publish`** — and the code comment
beside it records that this exact confusion was already fixed once, on this exact field, on
2026-09-16: it used to be cleared on episode close, so *"the publish that drained the queue and
closed a 146-hour episode wrote `last_clean_publish: null`"*, making a recovered publisher and one
that had never run byte-identical. The **writer** was repaired. **The reader was not** — and the
seat wrote an exit test against the un-repaired reading six days later.

This is `CLAUDE.md`'s *"key a control to the property, not to today's answer"*, landing on the
seat's own exit test: an episode counter was used as an outage-recovery criterion. **The property is
"a clean publish happened since the fix" — `last_clean_publish > commit_time(12f4073ed)` — not "a
counter scoped to an episode that success deletes".**

### Recommended, not asked

Any future publish-recovery criterion should read `last_clean_publish`, with `wedge_since: None` and
`episode_failures: 0` as corroboration. `episode_clean_publishes` answers a different question
(is the publisher losing a race with its own queue?) and answers it well; it is simply not the
outage question. Not filed as a code change: there is no code defect here, only a reader's defect,
and the one reader was this item.

## Evidence

| | value |
|---|---|
| publish commit | `60c8c1d4b` (55 files, `site/data/*`, `site/state/*`, `docs/status/LATEST.md`) |
| `HEAD == origin/main` | `60c8c1d4bf755fac2a1d86e225e201d652e2df51` (after `git fetch`) |
| figure published | net margin **£158,278.48**, `generated_at` 2026-09-21T17:47:56Z, `git_commit` 87b25d6da |
| `last_clean_publish` | 2026-09-21T18:15:57Z (prior: 2026-09-19T19:57:19Z) |
| outage ended | **46.3 h** since last clean publish; **44.0 h** since `wedge_since` |
| `episode_failures` | 19 → **0** · `total_red` 0 · `blocking_tests` `[]` · `wedge_since` `None` |
| blocking test at HEAD | `test_episode_prior_partition.py` **60 passed**, clean `git archive HEAD` extract |
| grading run | PID 1183179, started **17:42:28Z** (fix landed 17:13:17Z), waited via `tools/wait_for.py --pid`, finished +555s |
| queue | both markers drained to `docs/staging/done/` |

## Corrections to the drawn item, kept beside it

1. *"`git log origin/main..HEAD` holds exactly two commits"* — **false at draw time.** Already
   pushed; the push half was spent before the item was drawn.
2. *"its `blocking_tests`, its `episode_failures: 18` and its `red_at_head` describe a tree that no
   longer exists"* — **right in substance, wrong in instance.** The 16:59:48Z file it named had
   already been superseded; the 17:34:13Z file that replaced it had the same defect for a different
   reason (post-fix mtime, pre-fix graded tree, `episode_failures: 19`).
3. *"FINISHED means `episode_clean_publishes` is non-zero"* — **inverted**, per the finding above.
