# FINDING — the board's headline net figure is published, and announced in 43 commit messages, from a run record the repo has not carried since 2026-07-29

**Severity:** LATENT · **Lane:** H_harness · **Disposition:** QUEUED (not fixed on sight)

**Atom:** `D35_the_render_site_sweep_stops_at_this_processs_edge` (LANE 3 idle draw, DISCOVER/FRAME, 2026-08-18)
**Class:** the same "publish commits the door and not the record" class as
`WORKER_FINDING_THE_PUBLISH_PATH_COMMITS_THE_DOOR_AND_NOT_THE_RECORD_IT_RENDERED_2026-08-17.md`,
one layer worse — there the record existed and went uncommitted for a run; here the record has been
frozen for 20 days while the doors kept republishing from the working-tree copy

Full derivation and every number: `docs/design/simplifications/D35_the_render_site_sweep_stops_at_this_processs_edge.yaml`
(2026-08-18 entry, Findings 2, 3 and 4). Staged separately because it is a live publish-path defect on
the company's headline financials, not a precision question, and so is not this atom's to fix.

## The observation

`docs/reports/run_output_latest.json` feeds `tools/generate_company_data.py` (→ `site/data/company.json`)
and the dashboard. All `observed-with-evidence`, 2026-08-18, HEAD 660a19719:

    last commit of docs/reports/run_output_latest.json   59ab1ac01, 2026-07-29
    committed total_net_gbp  (HEAD, and at every 2026-08 publish commit)   1,521,069.65
    on-disk   total_net_gbp                                                1,530,002.96
    committed final_treasury_gbp 3,898,728.86   on-disk 3,906,125.44

    $ git log --since=2026-08-06 --format=%s | grep -c 'net=£'
    43
    announced values: £1,526,252 (x24), £1,547,113 (x7), £1,530,003 (x7),
                      £1,526,676 (x4), £1,533,687 (x1)   — the committed figure is NONE of them

    $ grep -o 1530002.96 site/data/company.json | wc -l      # 1   (single-line JSON,
    $ grep -o 1530002.96 site/data/dashboard.json | wc -l    # 21   so count occurrences)

Commit `c23faeba0` announces `net=£1,530,003` in its own subject line while the tree that commit
creates says 1,521,069.65. The published doors carry the disk figure; the repo carries neither.

## Why it is not the 2026-08-17 finding again

That finding's subject is one ledger and one door, and its proposed repair is a publish pathspec.
Two differences, both measured:

1. **The freeze is 20 days, not one run.** 43 publish commits have passed without the record.
2. **The probe that finding recommends cannot run here.** `run_output_latest.json` carries no
   identity field at all — no `generated_at`, no `run_git_commit` — so the two-lookup
   (measured_at, run_git_commit) join has nothing to join on. Per R15 that leg must score FAILED,
   never `committed`: an unavailable check is a failed check. Only a value join is available.

## What is NOT claimed

`inferred`, R9: nothing here says the published figures are WRONG. They are the current run's own
output. The claim is narrower and it is the R11/R14 one — the figures on the live doors, and the
figures in 43 commit subjects, are not reconstructible from the committed repo, and the repo's own
answer to "what was the net?" has been 1,521,069.65 since 2026-07-29.

A neighbouring instance found in the same pass and recorded in the atom record (Finding 3):
`site/data/market.json` publishes a `published_at` stamp that is in 0 committed blobs of
`docs/market_data/price_feed.json` (47 of 47 publish commits), but there the price VALUES are
byte-identical to the committed feed — only the refresh stamp churns. The two cases need different
repairs, which is the reason the atom record now splits the predicate's outcomes into LOST_VALUE and
STAMP_CHURN rather than routing both to "commit the record".

## Suggested disposition (not taken)

Rank: backlog behind the 2026-08-17 finding, whose repair (co-commit the record on the publish
pathspec) is the same mechanism and should be sized to cover this record too. Do not repair by
committing the market feed's stamp — see above.
