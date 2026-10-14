**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** publish-wedge draw (worker), 2026-10-13 ~23:00 BST

# The billing ledger outgrew Pages' file limit, and that held every page on the old snapshot

**Fate (2026-10-14):** ATOM -- remedy (b) DECIDED by the delivery seat: stop publishing state/billing_ledger.json under site/ and keep it a build input, then withdraw the stale live copy. No page reads it, and sharding (a) would outgrow the limit again as the book grows. Reversible; the build is the harness lane's.

**The wedge moved; it did not end.** The publisher landed `ed3dadd9d` at 21:53 UTC, which is run
2248e3baf: 989 accounts and 39,084 bills. The episode closed. Its deploy, run 38474007478, then
failed inside `wrangler pages deploy` with "Pages only supports files up to 25 MiB in size /
state/billing_ledger.json is 57.7 MiB". Pages refuses the whole upload over one file. So at 22:00
UTC `poesys.net/data/publish_provenance.json` still showed run 998814330 from 2026-10-05: 175
accounts. The ledger grew from 13.9 MB at `0d5304e98` to 60.5 MB because the book grew about 5.6x
(the founder-ruling book). No other file under `site/` is over 20 MiB.

**What I did (reversible, one commit):** I made `deploy-pages.yml` stage `site/` through
`tools/assert_deployed_bytes_are_served.py --stage`. The stage copies everything except files over
`PAGES_MAX_FILE_BYTES` and prints a `::warning::NOT DEPLOYED` line for each file it leaves out. The
post-deploy check now reports such files as NOT DEPLOYED instead of polling for bytes that were
never uploaded. A dry run on the real tree left out exactly one file of 1,238. Both new legs are
mutation-proven. To reverse it, revert the commit.

**What is still wrong, and is owed:** `/state/billing_ledger.json` is a published artefact.
`site/data/publish_steps.json` lists it, and earlier R11 evidence was measured on the live copy.
The edge now serves the 2026-10-05 ledger beside 2026-10-13 pages. Two worlds sit on one site, and
only the deploy log says so. No page fetches the file; the only readers are Python generators that
read it from disk. Two remedies:
(a) shard it per customer or per year so that each shard is under 25 MiB;
(b) stop publishing it under `site/` and keep it as a build input.
I recommend (b): no browser reader exists, and (a) would grow again with the book. Whichever is
chosen, the stale live copy should then be withdrawn or replaced, so that the site stops showing two
snapshots. Either one changes a published artefact, so it is filed here and not decided in a deploy
fix.

## The same publish also red-walled every lane's commit at HEAD

The first landing of this fix was refused, and the refusal was not about this fix. `ed3dadd9d`
was the first publish to commit `run_output_latest.json.gz` and retire the plain file, as designed
on 2026-10-10. `tools/wall_channel_census.artefact_at` read only the plain path. At HEAD it raised
`CensusUnavailable`, and the pre-commit gate turns that into a refusal for any commit that stages a
`.py` file. That would have refused every lane's commit until someone looked.

**Fixed in the same commit.** `artefact_at` reads the plain file if the rev still tracks it, and
the gzip otherwise. The two worktree reads go through `run_output_store.load_run_output`. Provenance
dates the artefact by the last commit that touched either form. A new test covers both legs, and it
reds when the gzip leg is removed.

**Once the census could read the artefact, it was the 2026-10-05 shape again.** The newer artefact
exposed five flat rows and nested fields under 16 keys, all read by code that predates the publish.
The flat reads landed between 2026-10-06 and 2026-10-11. I unioned them into the baseline by hand,
with no `--freeze` and nothing removed; the ruling is in `_meta.last_freeze`. The `sim_*` names under
`svt_decisions` and `world_payment_truth` under `per_customer_behavioral` are read by no module in
`company/` or `saas/` at HEAD.

The P3 atom on the 2026-10-05 finding is still unbuilt: the census does not run on a publish
commit, because the gate skips any commit with no `.py` file staged. That gap is why this widening
was billed to the next code commit again. This occurrence is the second, and it is evidence for
raising that atom.

## Decided and done: remedy (b), 2026-10-14 (worker, claim `the-billing-ledger-leaves-the-published-site`)

- **The ledger now lives at `docs/state/billing_ledger.json`, and nothing is left under `site/`.**
  That path was already a byte-identical, committed copy: the GitHub Pages mirror wrote it every
  publish, and four readers (`generate_company_data`, `raw_account_export`, `statement_export`,
  two tests) already read it. `generate_billing_ledger.OUT_PATH` writes there now, and so do the
  other ~15 generators and controls that read `site/state/`. The mirror row is gone; it would now
  copy the file onto itself. The publish's explicit append is gone too, because `docs/state/` is
  staged as a directory. The step ledger names the new path, and `site/state/billing_ledger.json`
  is deleted. That also drops one of two 58 MB copies from every publish commit.
- **Withdrawal of the stale live copy: measured, nothing owed.** `curl -I
  https://poesys.net/state/billing_ledger.json` returned **404** at 12:07 UTC. A Pages deployment
  is a whole snapshot. Once the staged deploy shipped without the file, the 2026-10-05 copy
  stopped being served. The "two snapshots" this finding saw were gone before this change.
- **Live-URL evidence repointed.** `generate_project_state` no longer lists
  `poesys.net/state/billing_ledger.json`. The github.io URL stays and now says why. The shadow
  generator's link points there as well. Earlier R11 evidence in
  `D_money_boundary_reconciliation` was already measured on `docs/state/`.
- **Dry-run:** `assert_deployed_bytes_are_served.py --stage` on the tree it creates stages
  1,239 of 1,239 tracked `site/` files, with no `NOT DEPLOYED` line.
- **Control:** `test_the_ledger_is_written_outside_the_cloudflare_site`. It went red when
  `OUT_PATH` was set back to `site/state/` and green when restored.
- **Not caused by this, found while doing it:** one test was already red at untouched origin,
  `test_billed_total_never_less_than_gross_margin_for_any_real_customer_year`. It is filed as
  `WORKER_FINDING_NINE_CUSTOMER_YEARS_BILL_LESS_THAN_THEIR_GROSS_MARGIN_AT_ORIGIN_2026-10-14.md`.
