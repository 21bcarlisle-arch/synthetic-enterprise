**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A ledger-only commit selected seven simulation runs through scratch-path leaves, and the 3,600 s gate timed out (2026-11-19)

**What happened.** The D48 rows for `docs/observability/coupled_gap_ledger.json` (W2_30, W1_14) were
refused twice by `surgical_land`. Both times the reason was `pre-commit timed out after 3600 seconds`.
The second attempt was killed at 57% of its test run. The bytes being landed were 718 added lines of
JSON and nothing else.

**Cause, measured.** `data_surface_tests` selected 41 test files for that one path. Thirteen of them
name the ledger only as a leaf on pytest's scratch directory, for example
`tmp_path_factory.mktemp("gap") / "coupled_gap_ledger.json"`. Seven of those thirteen are
whole-simulation runs (`run_phase2b.main`), all added between 2026-10-06 and 2026-10-23. EP1's ledger
row gated in 178 s on 2026-10-01, before they existed. A test that writes to its own scratch copy
cannot change verdict when the committed file changes. On this machine (load 2.7 on 16 cores), the
departed-household run alone went more than 8 minutes without finishing.

**Fix.** `_names_it_outside_comments` now drops a string constant that is only the right-hand leaf of
a `/` whose left side roots in `tmp_path`, `tmpdir` or `tmp_path_factory` (`_scratch_path_leaves`). A
leaf on any other root still counts, and so does a bare literal or a leaf assigned through a
variable. Both errors lean toward running. With the fix the ledger selects 28 files, and every
simulation run is gone. The control is
`test_a_test_that_names_a_data_file_only_as_a_scratch_path_leaf_is_not_its_guard`. Its drop legs are
asserted first. With the drop mutated out (`and True`) it goes red, which was checked.

This is the same shape as the 2026-11-17 markdown cut in the same function: a citation that cannot
read the file put an 18-minute run under every edit to it.
