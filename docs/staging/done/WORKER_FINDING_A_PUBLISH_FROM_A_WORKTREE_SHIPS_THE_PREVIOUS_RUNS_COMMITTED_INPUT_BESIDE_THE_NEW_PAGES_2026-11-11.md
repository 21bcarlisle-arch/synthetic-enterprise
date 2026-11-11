**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# A publish from a worktree ships the previous run's committed input beside the new pages (2026-11-11)

*Lane-0 item `the-gate-permitted-6fe7827ab2-book-is-actually-published`. Found on its third attempt.*

## What was seen

e816040ce published the 6fe7827ab2 book from a trunk worktree (`/var/tmp/publish-6fe7827ab2`). The page publishes
757 households and 1,302 legs. The `docs/reports/run_output_latest.json.gz` committed beside it was still
0a6391d186's, with 1,293 legs. The post-publish reader caught the mismatch:
`test_the_published_customer_book_is_reproducible_from_the_run_output_committed_beside_it`. The follow-up commit
lands the right gz.

## Why

`git_commit_push` writes the gz with `write_published(generate_customers_json.RUN_OUTPUT)`, and that file is the
untracked `docs/reports/run_output_latest.json`. Only the shared tree has it, because `sim_runner` copies each run
there. In any other checkout `_customers_input.exists()` is False, so no gz is written and nothing says so. The
surfaces were unaffected. Every producer the publisher calls was given the marker's own JSON, and the committed
billing ledger's `meta.source_json` names the 6fe7827ab2 file with 1,302 customers.

## Why it matters now

A publish has to run from a worktree whenever the shared tree cannot fast-forward. The 17:02 refusal said so, and
it was the only route left today. Each such publish will ship a stale gz without saying anything.

## Proposed fix (not built)

Write the gz from the marker's `json_path` to `PROJECT_DIR / run_output_store.PUBLISHED_REL`. Refuse by name when
neither file is present. Today `write_published` always writes beside its input. Called on the dated run file, it
wrote `run_output_6fe7827ab2_….json.gz` into the shared tree's `docs/reports/`. So the fix needs a target argument.

## Also seen on this item, fixed and landed

- 8d271594d: the weekly window read 601929ce0, a re-emission of the 3 Nov run, as this week's publish. It now
  stays open while origin still shows the run it showed before the week began.
- 40a48b5d8: the stale-copy guard refused the regenerated site/capabilities and site/code pages because they lack
  19aa987bc's own 3 Nov stamps. The publisher now declares those files as drops when the last publish wrote them
  and no commit has touched them since.
- The `.gitignore` patterns `sim/cache/` and `node_modules/` end in a slash, so they do not match the symlinks
  `_overlay_untracked_data` makes in a worktree. A salvage commit (`fork_salvage`, 19:42, ef1070dae8, local only,
  now dropped from HEAD) staged both. Any `git add -A` in an overlaid worktree will do the same.

## Resolution (2026-11-11, built)

Built as proposed. `git_commit_push` takes the marker's `json_path` (passed by `_process`) and gzips it to
`PROJECT_DIR / run_output_store.PUBLISHED_REL`, falling back to the plain `RUN_OUTPUT` only when no marker run is
given. `write_published` has a `target` argument. When `site/data/customers.json` is listed and neither input is on
disk, the publish refuses as `PROVENANCE_REFUSED`, and the evidence names both paths. Control:
`test_a_publish_from_a_checkout_without_the_plain_run_commits_the_markers_own_run`. It reds under both mutations:
source reverted to `RUN_OUTPUT`, and target reverted to beside-the-input. The refusal arm is asserted in
`test_the_publish_commit_carries_the_run_output_the_customer_book_is_made_from`.
