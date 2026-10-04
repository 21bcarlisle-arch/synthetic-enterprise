**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

# The tracked feed was rewritten by the dashboard generator, not by a site control

Item: `a-site-control-stops-rewriting-a-tracked-feed` (DIRECTION.yaml `wrong`, "a control in a clean
origin extract rewrites a tracked file (site/data/dd_opening_arms.json)").

## 1. The writer is not in `site/`

In a clean origin extract at `265c60801`, every `site/test_*.py` that names the feed (307 passed)
and then the whole `site/` suite (1,093 passed) left `site/data/dd_opening_arms.json` untouched.

The bisect log (`/var/tmp/headred-bisect.log`) shows the last file it ran before the checkout failed:
`tests/tools/test_website_integrity_fix.py`. Under a write recorder, `generate_dashboard_data.generate()`
wrote exactly two files: `OUTPUT_PATH`, and `DD_ARMS_FEED` at its own absolute path. Three tests
redirect only `OUTPUT_PATH` and then call `generate()`:
`test_website_integrity_fix.py` (two tests), `test_generate_dashboard_mgmt.py` and
`test_query_interface.py`. So all three rewrote the tracked feed in whatever tree they ran in.

**Why `git status` never showed it at origin.** The feed is a pure function of the committed
artefact `docs/reports/dd_opening_arms.json`, so at origin the rewritten bytes equal HEAD's. It
only goes dirty when the checked-out commit's artefact and feed disagree. That happened in the
bisect, which walks old commits. A `git status --porcelain` census would have passed on that
coincidence, so the control records writes instead.

## 2. What landed

- `generate()` writes the feed as a sibling of `OUTPUT_PATH`
  (`OUTPUT_PATH.parent / DD_ARMS_FEED.name`). A caller that redirects the dashboard therefore
  redirects the feed too. Production is unchanged: both constants sit in `site/data/`.
- `tests/tools/test_the_dashboard_generator_writes_no_tracked_file_when_its_output_is_redirected.py`
  runs `generate()` under a recorder that patches `open`, `io.open` and `os.replace`. It asserts
  that no recorded write is a tracked path. Its positive leg asserts that both expected writes are
  seen, at the redirected location.
- **Mutation seen red.** Restoring `_write_dd_opening_arms_feed(DD_ARMS_FEED)` turns both tests red.
  The census names `['site/data/dd_opening_arms.json']`. Reverted, both are green.

## 3. Two writers this item did not fix

1. **Every pytest session appends to a tracked file.** `tests/conftest.py::pytest_sessionfinish`
   calls `tools.test_execution_metric.record_execution`, which appends to
   `docs/observability/test_execution_log.jsonl`. Every extract that runs any test, the gate's
   included, is dirty afterwards. The bisect survived it only because its `red_at` checks out
   with `-f`. **Recommendation:** record only when the tree is not a linked worktree or extract,
   for example when `git rev-parse --git-dir` equals `--git-common-dir`. The metric it feeds is the
   director's cumulative-tests figure, and the runs that count are the shared tree's. Not done
   here because it changes what that figure counts.
2. **The book resolution writes two untracked run records.** `simulation.live_population`
   (`_resolve_campaign` and `_record_subset_verdict`) writes `docs/observability/book_growth_campaign.json`
   and `book_subset_verdict.json` when `generate()` resolves the book. I saw this under a
   standalone probe. It did NOT reproduce inside the pytest run in §5, so the test session seems
   to suppress it, though I have not confirmed why. They are untracked, belong to the world
   lane, and the census does not grade them.

## 4. Why the census is not "run the site suite and read `git status`"

The item asked for exactly that. It would have stayed green over this defect, as §1 shows, and it
costs a whole suite per run. The property-keyed census does the job in 6 s.

## 5. The extract after the fix

In a clean origin extract carrying this change, I ran the whole `site/` suite together with the four
`generate()`-calling test files and the new control: 1,157 passed, 54 skipped. The feed's mtime did not
change (1791125375 before and after). The only tracked path `git status` listed afterwards was
`docs/observability/test_execution_log.jsonl`, which is §3.1.
