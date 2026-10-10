**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The published run has outgrown GitHub's file limit, so the next publish fails at push

*Worker tick, 2026-10-10, found while grading the single-levy re-run
(`SEAT_FINDING_EVERY_SETTLED_BILL_CHARGED_THE_LEVIES_TWICE_2026-10-10.md`).*

## What was seen

`background/process_run_complete.py::git_commit_push` commits `docs/reports/run_output_latest.json`
beside `site/data/customers.json` (the "ITS INPUT TRAVELS WITH IT" block, added after 0247f3061).
`sim_runner` copies each run onto that name byte for byte, and `tools/run_annual_report` writes it
with `json.dumps(data, indent=2)`.

GitHub refuses any file over 100 MiB (104,857,600 bytes) at push. The runs have grown past that:

| run | size | reached origin? |
|---|---:|---|
| 998814330 (2026-10-05, 175 accounts) | 26.6 MB | yes, last publish |
| 7a4f75b25 (2026-10-09 13:01) | 55.1 MB | no, window held |
| 611cae007 / 224e4af02 / 5343a8e96 / cf8706023 (10-09 to 10-10) | ~120.7 MB each | no, window held |
| 7379375f6 (the single-levy run, 2026-10-10 14:50) | **123.5 MB** | no, graded only |

No run over 100 MB has been pushed yet, because the weekly window has held every run since 10-05.
**The first publish after the window opens (Mon 2026-10-12 04:00 BST) will try to push a ~120 MB
blob and be refused.** Nothing in the publish path checks the size before it commits.

## Measured on the 123.5 MB run

| form | size |
|---|---:|
| as written (indent=2) | 123.5 MB |
| compact JSON (`separators=(",",":")`) | 91.5 MB (8% under the limit) |
| gzip of the indent=2 file | 11.5 MB |

Largest keys, compact: `bills` 37.7 MB, `years` 11.6, `meter_read_log` 10.5, `dd_collection_book`
5.6, `svt_decisions` 4.9, `account_state_log` 4.5.

## Proposal (the seat's call, not taken here)

Compact JSON is the smallest change that lets Monday through. Every reader uses `json.load`, so none
of them would notice. But it leaves only 8% headroom on a book that has just grown 4.6x, so it
buys time and does not fix anything. The durable choices are:

- commit a gzip and teach the readers to open it (one helper; the reproducibility control reads
  through the generator); or
- stop committing the full run and commit a reduced published input that carries only what the
  site generators read.

Either way, add a size check before the publish commits, so that the next growth fails on the
seat's surface rather than as a refused push.

## Not done here (as first written)

No code changed. The window opens in about 37 hours. Check whether the shared checkout reaches
origin by then, because the publish runs the shared tree's copy of `process_run_complete`.

## Done, 2026-10-10 (delivery seat, `the-published-run-fits-under-githubs-file-limit-before-monday`)

*Severity moved BLOCKING -> LATENT: Monday's publish is no longer refused at push, and the next
growth past the limit is refused by name before anything is staged. What stays open is the
durable choice below.*

- **The stopgap: compact JSON at the one writer.** `tools/run_annual_report.dump_run_output`
  (`separators=(",",":")`) now writes both `--save-json` (the file `sim_runner` byte-copies onto
  `run_output_latest.json`) and `save_run_output_json`. Measured on the shared tree's 123,654,505
  byte run: **91,599,892 bytes, 87.4% of 104,857,600**, and `json.loads` of it equals the indent=2
  load. `sim_runner` keeps its byte copy on purpose (one writer, one format).
- **The refusal.** `process_run_complete._files_over_push_limit` runs after the pathspec is built
  and before the landing; it walks directories in the pathspec too. A file over 100 MiB returns
  `COMMIT_REFUSED` (no fingerprint, the next cycle retries) with the `NON_TEST_REFUSAL_CAUSE`
  override, logs, and pages NTFY `real_alarm` naming the file, its bytes and the limit.
- **Proven able to fire.** `tests/background/test_the_publish_refuses_a_file_github_would_refuse.py`:
  a 101 MiB sparse fixture is refused by name; a file inside a staged directory is seen; the
  partition control lands a file at exactly the limit and refuses one byte over; both writers are
  compact; HEAD's committed run, through the real writer, reads back equal and is admitted. Each
  leg was mutated and went red.

**Check before Monday 04:00:** the publish runs the SHARED tree's code and the shared tree's file.
The 123.6 MB file on disk now was written by the old code, so it is compact only once the shared
checkout carries this commit AND a run has been written since. If no run lands before the window,
the publish is now *refused by name* rather than rejected at push -- the site still waits a week.

**Met on disk, 2026-10-10 18:34Z (route b).** sim-runner had deferred every cycle since 11:07 to a
resident long job (`save-eight`, declared 50 min, running ~2h), so the shared tree's
`docs/reports/run_output_latest.json` was re-written from the graded single-levy run
(`/var/tmp/single_levy/run_output_abb925ec7.json`, `producing_commit` 7379375f6, which has 1d3c28930
as an ancestor) through `tools.run_annual_report.dump_run_output`: 91,506,306 bytes, read back equal
to the source, and `_files_over_push_limit` returns empty for it. The publish checks size, not that
the run's commit is HEAD; `test_the_published_run_output_names_its_world_and_adds_up` and
`test_every_promote_target_producer_declares_its_run_identity` pass against it. The double-levied
run it replaced is still on disk as `docs/reports/run_output_cf8706023_20261010T013208Z.json`, so
copying that back undoes the change. If sim-runner gets a cycle before the window, its own compact HEAD run
overwrites this one, which is also fine. Whatever overwrites it, the size refusal still guards Monday's publish.

## Proposal: the durable choice (seat's recommendation)

Compact JSON leaves 12.6% headroom on a book that grew 4.6x in a week; the next book growth
crosses it. **Recommend gzip with one reader helper**: 11.5 MB on the same run (~9x headroom),
content-identical, so the reproducibility control
(`test_a_published_surface_is_reproducible_from_its_committed_input`) still reads the full input,
and the change is one helper (`load_run_output(path)` opening `.json.gz` or `.json`) plus the
census of `json.load` readers of this path. The alternative -- a reduced published input carrying
only what the site generators read -- is smaller still, but it makes a second schema that drifts
from the run and needs its own reproducibility argument; take it only if the gzip proves too
large. Either way the size refusal above stays.

## The durable choice, taken (delivery seat, 2026-10-10, `the-published-run-is-gzipped-with-one-reader-helper`)

**Premise re-measured at draw:** the shared tree's checkout carries f235d64c8, but its
`run_output_latest.json` is still the 123,654,505-byte indent=2 file written at 03:46 by the old
code. With no run since, Monday's publish would be refused by name, as predicted above.

**Design.** `tools/run_output_store.py`: the publish commits `run_output_latest.json.gz`
(deterministic, mtime 0; 10,720,259 bytes on the 123.6 MB run, 10.2% of the limit; 4.5 s to write,
0.8 s to read back). `load_run_output(path)` prefers the plain file and falls back to `<path>.gz`.
The plain file is retired from HEAD **by the shared tree's own publish** (`surgical_land` content
None + `drops`; the file stays on disk and is then ignored by `run_output_*.json`), never by a
deletion landed from a worktree: that would reach the shared tree through `merge --ff-only`, which
refuses to delete the dirty copy that sits there between every run and its publish.

**Pre-registration (before the gz-only arm is run).** Arm A: the 45 test files that name the file,
with the plain copy present. Arm B: the same tree with only the `.gz` present (what every worktree
and gate extract sees after the first gz publish). Prediction: 8-20 tests change outcome A->B,
most of them pass->skip (readers guarded by `exists()`), a few pass->fail; production readers in
`company/` and `saas/` are not reached from any test with the real file and stay plain-path readers
(they run in the shared tree, where the plain file stays).

**Result: the prediction was wrong, low by about 4x.** Before any reader was converted, arm B
moved 54 tests pass->skip and 32 pass->fail, plus 4 errors (A: 1,327 passed / 5 skipped; B: 1,238
passed / 59 skipped / 36 failed / 4 errors). The skip-guarded readers were the bulk, as predicted;
the failures were unguarded `open(...)` readers (`test_phase_cn_*`, `test_phase_cp_*`), the
pricing tool's own tracked-run tier, and the ledger/P&L fixture. After converting them, both arms
read **3 failed / 1,333 passed / 5 skipped**, identical, and all 3 are red at clean HEAD for
reasons unrelated to this change (two are the hollow-2022 rows in
`WORKER_FINDING_2022_IS_A_HOLLOW_YEAR_..._2026-10-10.md`, the third is
`test_a_log_the_run_makes_..._survives_the_reduction`).

**Readers converted** (through `load_run_output` / `resolve_run_output`, or `as_plain_file` where the
consumer is in `company/` and may not import `tools/`): the generators `generate_customers_json`,
`generate_supplier_json`, `generate_billing_ledger`, `population_anchor`, `generate_dashboard_data`,
`couple_value_based_pricing` (its tracked tier accepts the gz twin), and 15 test files. The
reproducibility control reads `HEAD:run_output_latest.json.gz` when the tree carries it, the plain
file before the first gz publish.

**Not converted, deliberately, and what that costs:**

- `company/` and `saas/` production readers (`company/portal/app.py`, `saas/reporting/annual_report`
  CLI default, `background/sanity_daemon`, `dd_h_solvency_gap`, `run_live_decisions` and the other
  shared-tree tools). They run in the shared tree, where the plain file stays on disk. In any other
  checkout they see no run, as they would have for any untracked run before.
- `tests/company/compliance/test_crisis_bad_debt_validator.py` and
  `tests/saas/reporting/test_a_churned_account_has_a_departure_record.py`. Both carry a row that
  is red at HEAD now (hollow 2022), and the commit gate refuses any landing that selects a red
  file, so editing them here would block this landing. **After the first gz publish**, in any
  checkout but the shared tree: the crisis file's run-reading tests SKIP, which hides its XPASS red
  without fixing it, and the churned-account file gains a second red, "is missing". Whoever lands
  the 2022 fix has to touch that file anyway; the conversion is two lines (`resolve_run_output(RUN_OUTPUT_PATH)
  is not None` for the existence assert, `load_run_output(RUN_OUTPUT_PATH)` for the read).

**Withdrawn after landing, same evening: the conversion of
`tests/tools/test_a_published_rate_says_which_rate_it_is.py`.** The shared tree holds an
uncommitted in-place edit of that file dated 2026-09-24 (newer than its last commit, 7a995e2b1, so
another lane's work, not a stale revert). `origin_reconcile.paths_blocking_fast_forward` named it
as blocking the shared tree's `--ff-only` the moment 8f02e2f39 reached origin. The file is restored
to its pre-landing bytes so the shared tree can advance; until that lane lands or drops its edit,
the file's run-reading legs skip in gz-only checkouts. The conversion is the same two lines as
the others.

## Follow-through, 2026-10-10 19:10 BST (delivery seat, `the-first-gz-publish-retired-the-plain-run`)

- **The fast-forward.** origin/main is 34aa44858. The shared tree fast-forwarded to 126cac71e at
  18:53, and at draw time nothing blocked the next step: `paths_blocking_fast_forward()` returned
  `[]`. The shared copy of `test_a_published_rate_says_which_rate_it_is.py` now equals 126cac71e's
  converted bytes. The 2026-09-24 in-place edit that the withdrawal was protecting is no longer on
  disk, so 34aa44858 now reverts a conversion that nothing contests. Re-landing it is refused by
  `surgical_land`'s stale-copy gate as `predates_landing`, because it puts back names 34aa44858
  removed. That refusal is right by its own rule. The re-landing needs a fresh edit
  (`resolve_run_output` / `load_run_output`) rather than 126cac71e's bytes. Not done here.
- **The first gz publish has NOT happened yet.** The weekly window opens Mon 2026-10-12 04:00 BST.
  The retirement path in `_land_publish_commit` (content None + drops) is still unrun on the real
  publish. **Check on Monday:** HEAD should carry `docs/reports/run_output_latest.json.gz` and no
  plain `run_output_latest.json`, and the plain file should still be on disk in the shared tree.
- **`tools/generate_billing_ledger` converted**, now that its HEAD red is cleared. The red was not
  about the ledger. The three tests (`test_dd_high_some_failures`, `test_churned_arrears_written_off`,
  `test_resi_dd_path_unchanged`) pinned the old unsourced 35% HIGH DD tier, which
  `SEAT_FINDING_THE_DD_FAILURE_CORRECTION_MOVED_MEASURED_FACTS_2026-10-09.md` replaced with
  10.15%. They are re-keyed to the property. The rate leg now asserts that the HIGH tier is
  whatever `_DD_FAILURE_PROB["HIGH"]` says, within 4 sd over 4,000 draws; a HIGH->LOW collapse
  mutant reads 34 against an expected 406 and goes red. The two cascade fixtures set HIGH to
  certainty, because their subject is the path a failure takes, not how often one happens. A new
  gz-only leg reds when the reader is reverted to a plain `json.loads`.
- **Still deferred: the crisis validator and the churned-account file.** Both are still red at HEAD
  (crisis XPASS(strict); `test_every_year_the_published_run_reports_appears_in_its_lifecycle_record`),
  for the hollow-2022 reason. The conversion waits for the 2022 fix, as already written above.
