**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The billing ledger outgrew GitHub's file limit; compact JSON lets it through with 13% headroom

*Worker tick, 2026-11-02, diagnosing the publish wedge.*

## What was seen

The 20:02 UTC publish of `run_complete_20261102T173915Z` (book 08f267b666) closed the
`behind_origin` episode (HEAD level with origin/main), then was refused by name before staging:
`docs/state/billing_ledger.json` was **143,753,180 bytes**, over GitHub's 104,857,600 per-file
limit. HEAD's committed copy is 83,451,671 bytes, so the file grew 72% in one book. This is the
same class as `done/SEAT_FINDING_THE_PUBLISHED_RUN_OUTGREW_GITHUBS_FILE_LIMIT_2026-10-10.md`, but in
a second committed file that finding's fix (the run output's gzip) did not cover.

## Measured on the 143.8 MB ledger

| form | bytes | share of limit |
|---|---:|---:|
| indent=2 (as written) | 143,753,180 | 137% |
| compact | 91,168,764 | 87% |
| gzip of compact | 7,122,115 | 7% |

Nearly all of it (91.16 MB of 91.17 MB) is `customers`.

## Done here

Both writes in `tools/generate_billing_ledger.generate` now write compact JSON. No reader parses
the file as text: every reader is `json.load`, and no site JavaScript fetches it. The control is
`test_the_billing_ledger_writer_is_compact` in
`tests/background/test_the_publish_refuses_a_file_github_would_refuse.py`. Restoring indent=2 at
either write turns its own leg red.

## Still open: the durable fix

13% headroom on a file that just grew 72% will not last. The size refusal still fires by name
when it runs out. The recommended fix is the one taken for the run output: commit a gzip, and read
it through one helper such as `tools/run_output_store.load_run_output`. There are about eight
Python readers (`generate_dashboard_data`, `generate_invoice_data`,
`generate_customer_reaction_chain`, `generate_customer_consumption`, `sanity_daemon`,
`post_publish_readers`, and others). The GitHub Pages URL listed in `tools/generate_project_state.py`
would then point at `.json.gz`.
