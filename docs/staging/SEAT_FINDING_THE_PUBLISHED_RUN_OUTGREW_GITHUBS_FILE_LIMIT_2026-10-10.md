**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

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

## Not done here

No code changed. The window opens in about 37 hours. Check whether the shared checkout reaches
origin by then, because the publish runs the shared tree's copy of `process_run_complete`.
