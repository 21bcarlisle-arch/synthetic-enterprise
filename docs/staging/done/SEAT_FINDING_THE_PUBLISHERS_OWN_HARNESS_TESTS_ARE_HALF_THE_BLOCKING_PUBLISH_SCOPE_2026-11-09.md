**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `OPS6_scoped_publish_path_suite`

# The publisher's own harness tests are half of the blocking publish scope, so a red in its alarm or census bookkeeping still freezes the site

Found on 9 Nov while grading OPS6 exit (4). The measurement is in
`docs/staging/records/SEAT_RESULT_OPS6_THE_SCOPED_PUBLISH_GATE_GRADED_AGAINST_EVERY_WEDGE_EPISODE_ON_RECORD_2026-11-09.md`.

**What is observed.** `PUBLISH_PATH_SOURCES` in `background/publish_scope.py` declares
`background/process_run_complete.py`, and the scope selects every test that imports a declared source.

> **Correction (same day, measured):** the cause named here is wrong. Dropping the publisher from
> `PUBLISH_PATH_SOURCES` leaves the scope at 348 files. The selector walks imports transitively,
> and the publisher imports four of the other declared producers, so every test that imports it
> reaches them *through* it. Its membership was never the edge.
The publisher is about 9,000 lines and also holds the wedge alarm, the red census and the marker
bookkeeping, so **166 of the 348** blocking files are in `tests/background/`. Of the 25 publish-gate wedge
episodes on record that name a red test, **11 would still block today**. Of those, 7 are the publisher's
bookkeeping: `test_process_run_complete`, `test_staging_archive_policy`, `test_control_mutation`,
`test_publish_gate_red_census`, `test_a_duplicate_marker_is_not_a_publish`, `test_publish_gate_alert` and
`test_head_green_census`. None of them guards a published figure.

**Why it is LATENT, not BLOCKING.** It is not freezing the site today. The last gate pass was on 3 Nov,
and the 7 post-publish reds are a separate matter. But it is the exact shape the 10 Aug ruling exists to
end ("a factory that stops the line for … an unreconciled invoice in accounts"), and it is why OPS6 has earned L1, not its target
of L2.

> **Correction to the recommendation below:** the cut alone would not have worked. A new module
> the publisher imports is reached by every importer of the publisher. What was needed was the cut
> **and** a barrier: the walk does not pass through the orchestrator.

**Recommendation (reversible, the seat's to take).** Do not delete the source: a removal is "the
dangerous direction" and needs evidence, as the module itself says. Instead, **cut the functions that
write the published bytes out of `process_run_complete.py` into their own module and declare that module
in its place.** That is the gate's commit and the copy into `site/data/`. Selection then follows imports
to the publishing code, and stops at the alarm machinery that merely shares a file with it. Do not use a
hand-pinned test list: that is the rename-blind control the module was written to avoid. A test that
proves it: the existing both-directions leg
(`test_a_publish_path_red_blocks_and_a_red_outside_it_only_annotates`) gains a third arm, in which a red
in a module that only imports the publisher's *alarm* half does not block.

**What I cannot yet say.** Whether any of the 166 guards something that only the publisher's prose
path writes onto the page. Answer that before the cut, by listing which of the 166 still import the new
module.

**The level is not recorded.** L1 is earned (exits 1 and 2 met, 3 met in the feed, 4 measured), but the
level gate refused the move under OPS11: at HEAD, `H_harness` is held by
`docs/staging/SEAT_FINDING_OWN_CODE_REVIEW_UNUSED_DUPLICATED_AND_WALL_CROSSING_2026-10-24.md` (BLOCKING,
KNIFE3). Another lane has moved that file to `done/` on disk, but the move is uncommitted and the moved
copy has no `## Done` section, so I did not record-and-accept around it. Record OPS6 at L1 once that
finding's move lands or it is discharged.

**Reverse.** Delete this file.

## Done

Landed 9 Nov (OPS6):

- `select()` in `tools/select_impacted_tests.py` takes a `barrier`. `publish_scope.PUBLISH_PATH_BARRIERS`
  names the publisher. A barrier missing from the tree is inert, which can only widen the scope.
- The publisher's one inline figure, the LATEST.md results block, moved to `background/publish_content.py`,
  which is now declared in place of the publisher. The evidence for the removal is written beside
  the declaration: `generate_site` is a no-op, and every `site/data` figure comes from an imported producer.
- **The open question is answered.** Of the 141 tests the barrier drops, none imports the new module.
  32 name a publisher function, and 31 of those test commit, push, landing or gate mechanics. The 32nd,
  `test_process_run_complete.py`, also tests `update_latest_md` through the wrapper, and that figure's
  guard now blocks from `tests/background/test_publish_content.py`.
- **Scope: 348 → 207 blocking files.** Re-graded with the record's own script. Publish episodes went from
  11 BLOCK / 3 mixed / 11 annotate to **4 BLOCK / 0 mixed / 21 annotate**.
  - My prediction was that all 7 bookkeeping episodes would annotate. 6 did.
  - `tests/controls/test_control_mutation.py` still blocks, because it imports `tools/generate_dashboard_data.py`
    directly. That is correct: it mutates the generator.
  - The other 3 that still block guard content.
- R15: `test_a_red_in_the_publishers_own_bookkeeping_annotates_and_a_figure_red_still_blocks` runs real
  pytest. With the barrier, a bookkeeping red annotates and a figure red blocks. The mutation removes the
  barrier, and the bookkeeping red blocks again. `test_this_guard_blocks_the_publish` reds if
  `publish_content` leaves the declaration (checked by hand).
- OPS6 level not recorded. L1, and now the L2 exit, wait on OPS11's hold on H_harness. The
  BLOCKING `SEAT_FINDING_OWN_CODE_REVIEW_..._2026-10-24` is still owed: B2 is due 21 Nov, and the
  archive is cut in two. Its uncommitted move to `done/` is another lane's. It has no Done section, so it was left alone.

Reverse: revert the commit.
