**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The 0a6391d186 publish passed its gate and was refused because the dashboard was emptied while the gate ran (2026-11-03)

Drawn as `the-0a6391d186-publish-lands`: confirm the 21:22Z run's publish lands and supersedes
`run_complete_20261102T173915Z`. **It has not landed.** The site still serves the 26 Oct dashboard.
On origin, `site/data/dashboard.json` was last committed by 60e4d4dc52 (git=4ae8da9b0f).

## What happened, from `docs/observability/sim-runner-log.md`

- 23:32Z (2 Nov): the first attempt was refused by the scoped gate on
  `test_every_gate_the_chain_runs_is_either_named_or_declared_unnameable`. 87a83c4300 fixed that
  (it passes at HEAD, 28/28), and the provenance banner commit a3c9baf86a says so.
- 01:00Z (3 Nov): another attempt started. It regenerated `site/data/dashboard.json` at 01:03Z. The
  domain invariants found 0 unexcepted breaches (6 excepted). The scoped gate was **green**, and
  provenance was stamped "Verified 01:47:46Z, showing run_output_0a6391d186_20261102T212232Z".
- 02:01Z: **the publish commit was refused by the hook chain** (rc=77) on
  `test_the_published_series_and_the_ledger_it_came_from_are_committed_together.py::test_every_run_the_committed_dashboard_publishes_is_in_the_committed_ledger`:
  "site/data/dashboard.json publishes an EMPTY run_history".

## The cause is the file, not the series

The shared tree's `site/data/dashboard.json` is **2 bytes, `{}`**, with mtime **01:27:45Z**, which is
24 minutes after the publisher wrote it. The ledger it is built from is fine:
`docs/observability/run_history.json` has 100 entries, the last of which is 0a6391d186.
`extract_run_history` is not failing closed; something overwrote the whole dashboard.

It was the **only** file in the shared tree written between 01:26:30 and 01:28:00. The only
writer on record in that window is session cd7fc3c0 (the publish-gate-wedge worker). It launched
`tools.surgical_land` for e5f745334 (`background/seat_continuity.py`,
`tests/background/test_seat_continuity.py` and one done/ finding) at 01:24:04Z, and that landed at
~01:33Z. **Prime suspect: a gate or test in that commit's hook chain writes the real
`site/data/dashboard.json`, or `{}` read back and rewritten, instead of its redirected copy.**

Not yet established. The suspect is ranked on timing alone, and no writer has been reproduced. The
same test was a post-publish red on 4ae8da9b0 (26 Oct,
`docs/observability/.post_publish_reader_reds.json`), which suggests the clobber is a repeat and not
a one-off.

## Disposition

- The wedge worker (session synthetic-enterprise-f7 / cd7fc3c0) was already running this exact
  bisection at 02:02Z, with mtime stamps around each suite. I sent it the timing above and stood
  down, so that two sessions do not hunt one writer and two publishers do not re-arm one marker.
- **Re-arm route, once the writer is fixed:** give the publisher the `done/` path,
  `python3 background/process_run_complete.py docs/staging/done/run_complete_20261102T212232Z.md`,
  run from the shared tree's root. A copy put back in `staging/` is swept as a two-rooms duplicate
  (measured 2 Nov, see the 08f267b666 finding). That publisher regenerates the dashboard, so the
  `{}` in the shared tree needs no hand repair. Re-arming before the writer is found risks a fourth
  refusal.
- `run_complete_20261102T173915Z` is not superseded yet, because nothing newer has published.

## Done means

A commit on origin whose `site/data/dashboard.json` names run 0a6391d186 (or a later run) with a
non-empty `run_history`, and a named, fixed writer of `{}`.
