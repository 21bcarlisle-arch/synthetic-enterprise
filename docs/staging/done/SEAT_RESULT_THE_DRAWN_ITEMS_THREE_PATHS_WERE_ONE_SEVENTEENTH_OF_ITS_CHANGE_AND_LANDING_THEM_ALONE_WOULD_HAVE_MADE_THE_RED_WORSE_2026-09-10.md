**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `land-the-ledger-guard-ratchet-repair-from-isolated-bytes-and-discharge-its-finding`) · **Class:** uncommitted_and_orphaned_work

**Discharged:** the landing itself. `tests/background/test_live_ledger_guard.py::test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed` and `tests/background/test_the_site_publish_pipeline_is_contained.py` are green in a clean extract of the commit, over the 22-path set — not the 3-path set the item named.

# RESULT — the drawn item's three paths were one seventeenth of its change, and landing exactly them would have made the red worse

Pre-registered before measuring: `docs/staging/records/SEAT_PREREG_WHAT_THE_LEDGER_GUARD_CENSUS_READS_WHEN_ONLY_THE_ITEMS_THREE_PATHS_LAND_2026-09-10.md`.

## What the item said

The Lane 0 item named three paths — `background/live_ledger_guard.py`,
`background/process_run_complete.py`, `tests/background/test_live_ledger_guard.py` — said the repair
behind them was "finished in the working tree", said explicitly **do not rebuild it and do not
re-measure it**, and gave the clean-HEAD figures as already established: *86 → 56, delta 30 across
**17 modules**, subset-proven.*

Three paths contain one module. A delta of 30 across seventeen modules cannot fit in them. **The
item's own two sentences refute each other, and the arithmetic is the whole tell** — it took one
`comm` between "modules calling the guard in the working tree" and "modules calling it at HEAD" to
see that sixteen more files were carrying the change.

## What the numbers say

Every figure below is from a clean HEAD extract with the named bytes and nothing else, using the
test's own `_gap_ledger_modules` / `_functions_that_write` / `_calls_the_guard` predicates — never
the shared tree, which reads one higher because it holds four other lanes' uncommitted modules.

| Predicted | Measured | Tree |
|---|---|---|
| 86 | **86** | HEAD, unmodified |
| 78 (band 78–80), **RED** | **78, RED** — `assert 78 <= 56` | HEAD + the item's three paths |
| 56, GREEN | **56, GREEN** | HEAD + the real 22-path set |
| strict subset | **strict subset**, 0 new | — |
| — | **30 writers, 17 modules** | — |

All five predictions held, including the band. The load-bearing one is the second row.

## Why this is the interesting half

A drawn item that names too FEW paths does not fail loudly. Obeying it literally would have
produced a commit that:

* lowers the ratchet's bound from 74 to 56 — the hard, correct, argued-for half of the work; and
* lands one module's worth of the guarding that earns it, leaving 78 unguarded writers.

That commit leaves `test_the_narrowing_to_measurement_ledgers_is_measured_not_assumed` **red at
HEAD in a new and worse way than the red it was drawn to clear** — and it would have looked like
progress in every record: three named paths landed, a finding discharged, a bound moved down. The
class is *a landing keyed to a stated path list rather than to the property the list is supposed to
carry.* It is the same shape as R15's "key a control to the property, not to today's answer", one
level up: **key the pathspec to the change, not to the list.**

Two of the twenty-two are not even census members and are load-bearing anyway:
`tests/background/test_the_site_publish_pipeline_is_contained.py` and
`tests/tools/test_website_integrity_fix.py` both import `SitePublishUnderTest` /
`guard_site_publish_pipeline` from `process_run_complete` at HEAD. `guard_site_publish_pipeline`
moves home to `live_ledger_guard.py` in this commit, so landing the three named paths without those
two leaves **two `ImportError`s at HEAD** on top of the red.

## How the path list was recovered, which is the reusable part

Not by reading the item and not by reading the diff. By asking the tree:

```
comm -23  <(grep -l guard_live_ledger_write background/*.py | sort) \
          <(git grep -l guard_live_ledger_write HEAD -- background/ | sed 's|HEAD:||' | sort)
```

Sixteen modules, plus `process_run_complete.py` which was already a caller and adds eight more
sites: seventeen, exactly the number the item's own docstring quoted. **The number that proves the
path list wrong was printed in the path list's own justification.**

One of those sixteen was a false positive and worth naming, because the same grep will produce it
again: `background/head_red_register.py` matches `grep -l` on a **docstring** saying `save_observed`
is deliberately unguarded — `conftest.py`'s `production_surface_guard` already patches
`Path.write_text` for every test and lists `docs/observability` as protected, so a second guard
there would be a second implementation of a live rule. A name-grep is blind to the mechanism in both
directions; the AST predicate (`_calls_the_guard`) is what settled it. That docstring is landed here
so the next reader does not re-add the call.

## What is NOT claimed

* **Item 3 of the original finding — why nothing selected this test for two weeks — is untouched.**
  Clearing this instance does nothing about the class, and the same silence would cover any ratchet
  under `tests/background/`.
* The 35 writers that append through `open(..., "a")` remain invisible to this census
  (`SEAT_FINDING_THE_LIVE_RECORD_CENSUS_ONLY_SEES_WRITE_TEXT_AND_THIRTY_FIVE_WRITERS_APPEND_THROUGH_OPEN_2026-09-09.md`).
* No `dest_root` parameter was threaded through the 92 import-time site roots. That is still the
  correct fix for the publish-pipeline half and is still a named gap, not a placeholder.

## What is next

Whether any ratchet in `tests/background/` is currently red at HEAD and selecting nothing. This one
was, for fourteen days, and the only reason it was found is that an unrelated lane tried to edit the
file it lived in. That is not a detection mechanism.
