# [WORKER-REPORT] The 19th wedge's red was a sibling test's stale pin, not a regression (2026-08-12)

**Severity:** RECORDED · **Lane:** H_harness
**Drawn as:** PUBLISH-GATE WEDGE self-refill, RUNG 1 (UNWEDGE_PUBLISH_PRIORITY_ZERO 2026-07-23).
Episode: 205 consecutive failures, ~4767 min wedged, no pass at HEAD `1386876c2`.

## Observed, with evidence

The alarm's own `blocking_tests` named one test, and it really was red:

```
FAILED tests/background/test_staging_archive_policy.py::test_process_run_complete_still_sees_a_duplicate_after_the_sweep
E       assert 76 == 0
- [process_run] Already archived at 2026-08 (duplicate run) -- NOTHING was published by this
  process, so this is evidence of nothing about the gate's health (rc=76)
```

This morning's repair (`WORKER_REPORT_A_DUPLICATE_MARKER_NOW_HAS_ITS_OWN_EXIT_CODE_2026-08-12.md`)
deliberately changed the already-archived path in `background/process_run_complete.py` from
`return 0` to `EXIT_NOTHING_PUBLISHED` (76), because zero is the code that means "this process
published" and a duplicate publishes nothing. That repair landed with its own suite and its own
AST class test. What it did not carry was the **older sibling in another file** — an AO10
archive-policy test that pinned the same door's numeric code from a different lane's concern.

The four in-window failures are all the same red. `rc=1` in the doorbell's last-failure line is
the publisher's exit, not the test's.

## Why the citation was a red herring

The doorbell named `WORKER_FINDING_A_REPO_WIDE_CENSUS_IS_NOT_DECOMPOSABLE_BY_PATHSPEC_2026-08-12.md`
as holding the suspects. It does not: that finding is a ruff-census refusal class, LATENT and
queued, and no census refusal occurred in this episode. It has been re-frozen in place with that
provenance rather than re-drawn.

## What landed — `83f80e0ce`

The assertion now reads the **named register**, not a literal, and the test says what its subject
actually is: `locate()` reaching into the exhaust tree after the sweep empties `done/`, so a
marker another process published is recognised rather than read as fresh and republished over
current figures. The numeric code was never the property; it can be renamed again without
re-wedging publishing.

## R15 — the repaired test can still fail

A shared-source mutation was **not** available: a publish gate was mid-run against the very file
(pid 718402), and editing a module under a live pytest is a known corruption. The mutation was
done at fixture level instead, on the test's real subject and with no return code mocked —
`staging_archive_policy.locate` made blind to the exhaust tree, which is exactly the AO10
regression this test exists for:

```
MUTATED rc = 1        (marker not found)
E   AssertionError: assert 1 == 76
```

The opposite direction — a new `return 0` on that path — is already defended by the sibling suite
landed this morning, whose AST test names the offending guard. That is why it was not re-run here.

## What is NOT claimed

The gate has **not** yet been observed green end-to-end from this tick. The evidence is that the
tested trio (`tests/background/test_staging_archive_policy.py`, `background/process_run_complete.py`,
`background/staging_archive_policy.py`) is byte-identical at HEAD to the tree where 29 tests pass,
and the gate's subject is a clean checkout of HEAD. A publisher launched after the push is running
that gate now; if a second, independent red exists behind this one, the `-x` selection would not
have shown it and the next tick draws it.
