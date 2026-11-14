**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `unminted`

# The seat's journal dropped the red site test's name, and the direction record has since reached origin (2026-11-14)

**Premise re-measured at draw (item `the-direction-record-reaches-origin`).** Part (c) was already
done before this turn. Origin carries direction records landed at 06:50 (a23001d35) and 09:51
(f0cf90fe9, `oriented_at: 2026-11-14T09:24:43Z`). On the shared tree, `rev-list --count
HEAD..origin/main` reads **0**. Nothing was landed by hand, and DIRECTION.yaml was not touched.

**(b) The defect, fixed here.** The 03:54 journal line reads `GATE RED ... | ❌ SITE TESTS FAILED
-- COMMIT REFUSED. | [site-lane] ...` and names no test. `delivery_seat.refusal_verdict` cut the
text at the first `❌`. The site lane prints its banner *after* pytest's run, so every
`FAILED site/...::test_x` node above the banner was dropped. The fix keeps the pytest
`FAILED`/`ERROR` node lines that come before the `❌` (up to 10) and puts them ahead of the banner.
The test `test_a_site_lane_refusal_names_its_red_test_in_the_journal` covers it. Mutation check:
reverting the fix turns it red.

**(a) The red test at 03:54, measured.** I ran `pytest site/` at cc27c048e (origin/main at 03:52)
with no direction record on it. It was red on origin alone: 1 failed, 1896 passed, 159 skipped.
The failure was
`site/knowledge/test_the_reading_log_door.py::test_the_committed_feed_is_what_the_log_builds_today`,
because `site/data/reading_log.json` was stale (`unplaced` 0 on disk, 2 when built). The record
carried no direction field that any reader got wrong. The cause was db80910fa (advisor, 13 Nov
20:00). It edited `docs/institutional/reading_log.md` through `surgical_land`, but the site lane
mapped that file to no test, so the commit passed and the next full site run inherited the red.
fcdbd4cb0 (04:37) regenerated the feed in passing. That test passes 8/8 on origin today.

Fixed as a class, in one leg: `tools/site_lane_gate.SOURCE_DOOR_TESTS` maps the reading log to
its door test. The control `test_an_edit_to_the_reading_log_runs_the_door_that_rebuilds_its_feed`
asserts the mapping fires and that the mapped test file still exists. Mutation check: disabling
the mapping turns it red.

**Not established.** Why the seat's record, whose four paths select no site test, ran the WHOLE
site suite at 03:54. The gate's selection line is not in the journal. `plan()` returns
`(None, None)` for DIRECTION.yaml, decisions.jsonl, the stretch log and STARTUP_ANCHORS.md alike.
One candidate is the merge fallback in `pre_commit_test_gate.selection_paths`: it selects every
staged path when the merge parent cannot be diffed. Another is a base-advance merge whose combined
diff carried `site/data`. With (b) in place, the next refusal will name its test. Its selection
line is still not kept.

**Correction, same day (item `why-a-record-ran-the-whole-site-suite`).** The paragraph above is
wrong about the record's paths. A direction landing carries **five** paths, not four. The fifth is
`site/data/delivery.json`, which `direction.WRITE_SCOPE` names and `tools/generate_delivery_page`
regenerates before every `commit_direction`. Every seat landing since 13 Nov touches it (9dabdf2d9,
7e8a48b07, 389f8f5f1, a23001d35, f0cf90fe9). `plan()` over the scope returns `("full", None)`. A
`site/data/**` change is a broad trigger by design. So the whole suite ran because of the record's
own feed. It was neither the merge fallback nor a base advance. The paragraph listed
STARTUP_ANCHORS.md, which is not in the scope. It left out the one site-facing file, which is.

The record does author something site-facing. A changed `delivery.json` can break the harness
door, so running the site suite on it is the gate working. Narrowing `delivery.json` to its
consumers would weaken a fail-closed control to spare the seat about 150 s. **Not done.** The
reading-log mapping already fixes the class that actually let the red in. Two changes keep the
reason on the record: the site lane's `running` line now names the paths that tripped the broad
trigger, and `refusal_verdict` keeps that line in the journal next to the red node. Controls:
`test_a_whole_suite_run_names_the_path_that_tripped_it` and
`test_a_site_lane_refusal_keeps_the_line_that_says_why_the_suite_ran`. Each turns red when its
fix is reverted.
