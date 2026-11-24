**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The book's code is already origin's, and the shared tree's real effect on the post-s.12g book was dropping the MSC hold row

Found by the worker on claim `the-book-can-import-origins-code-when-s12g-ends`, 24 Nov 2026 00:39–00:46Z.

## The premise was half spent

The claim asked for the shared checkout's imported code to be made origin's, so that
`sim_runner.code_admission` would admit the post-s.12g book. The probe it named reads the
**shared** root, and it still prints 9 paths:

    ['company/finance/accounting_close.py', 'company/finance/double_entry.py',
     'company/interfaces/growth_desk.py', 'saas/ledger.py', 'saas/reporting/annual_report.py',
     'sim/forward_curve.py', 'simulation/gain_registration.py', 'simulation/run_phase2b.py',
     'simulation/run_phase4c_on_phase2b.py']

**The daemon has not admitted against that root since `b1c7d76b16` (22 Nov 05:31Z).** It builds
the book in its own worktree, `/var/tmp/se-sim-runner-book`, and calls
`code_admission(book["commit"], root=book["root"])` there (`background/sim_runner.py:1091-1095`).
The running daemon, pid 2960862, started 23 Nov 15:07Z, carries that code. Measured at 00:41Z:

| Reading | Result |
|---|---|
| book worktree HEAD | `95696822cd` = origin/main, clean |
| `imports_off_commit_at_launch(origin, root=book worktree)` | `[]` |
| `code_admission(origin, root=book worktree)` | **admitted** |
| what the daemon actually logs, every 5 min since ≥23:28Z | `DEFERRED -- budget exhausted` on memory: the s.12g book `longjob-value-test-cut012-new-book` (pid 65649, 11,800 MB) and `longjob-land8-msc-replacement-win` (pid 916978, 6,000 MB, 3.8x over its declared time) |

So the 9 dirty imports do not gate the book. The next probe the seat writes for this should
read the book root, not `None`.

## What the stale shared tree DID break: the MSC hold

`book_admission` reads `NEXT_BOOK_REQUIRES = PROJECT_DIR / "background/next_book_requires.yaml"`,
which is the **shared** copy. Origin's `d5a209baca` added the row that holds the post-s.12g book
until the MSC replacement win lands (`commit: null`). The shared tree is 67 behind, so its copy
was HEAD's and did not have that row. At 00:41Z `book_admission("95696822cd")` read
**admitted**. Once s.12g ends (~06:00Z) and its 11.8 GB frees, the book could have built
without MSC. That is exactly the case `d5a209baca` was written to stop.

**Fixed at 00:43Z.** The shared copy was clean (HEAD's blob `645c1ca5`, nothing uncommitted),
so origin's bytes (`090eb69e`) were written over it. `book_admission` now reads:

> admitted: False -- MSC replacement win booked as a levy
> (the-msc-replacement-win-lands-before-the-post-s12g-book) has not landed

This copy is an identical tracked twin to origin, which the reconciler's first class clears.
**REVERSE:** `git show HEAD:background/next_book_requires.yaml > background/next_book_requires.yaml`.

**The fill.** `fill_hold.sh` writes the landed sha into **origin's** row, not the shared one, so
the shared copy would read `null` and hold the book until the file lapses on 25 Nov. A one-shot
transient unit, `b8-msc-hold-row-follow` (`/var/tmp/se-msc-keep/shared-tree-20261124/follow_hold_row.sh`),
waits on pid 916978 through chained `tools.wait_for`, at most 24 h. Then it writes origin's copy
over the shared one, but only if the shared copy is still the null twin and origin's row names a
commit. It logs to `follow_hold_row.log` beside it.

## The 8 dirty code paths, and whose bytes they are

Every copy is preserved byte-for-byte at `/var/tmp/se-msc-keep/shared-tree-20261124/`:
`shared_vs_HEAD_779054e30b.patch` plus `copies/` and `SHA256SUMS`. That covers the 8 code paths
and `tests/simulation/test_run_phase2b.py`. Applying the patch to HEAD reproduces all 9 exactly
(checked with `cmp`). The table below compares each copy's lines-not-in-HEAD against origin with
`msc8.patch` applied, the patch the live MSC lane will land.

| Path | Lines new vs HEAD | Not in origin+msc8 | Whose |
|---|---|---|---|
| `company/finance/accounting_close.py` | 4 | 0 (file **identical** to origin+msc8) | MSC lane |
| `company/finance/double_entry.py` | 6 | 0 (identical) | MSC lane |
| `saas/ledger.py` | 29 | 0 (identical) | MSC lane |
| `company/interfaces/growth_desk.py` | 18 | 0 | MSC lane, on a pre-G15 base |
| `simulation/run_phase4c_on_phase2b.py` | 2 | 0 | MSC lane, before msc8's shared-run read |
| `sim/forward_curve.py` | 53 | 0 | G15, landed on origin; `refresh_to_head` grades it **refreshable** |
| `saas/reporting/annual_report.py` | 5 | 1: `"switching_gsop_payments": _NO_READER,` | the orphaned 6C draft (f80cc5a46's table); origin deliberately kept the 6ZA forward |
| `simulation/run_phase2b.py` | 90 | 2: the 6C draft's `own electricity-only household` comment and bare `if _why_kept is None:`, both since rewritten on origin | MSC lane + 6C draft |
| `simulation/gain_registration.py` | — | — | already origin's bytes; it drops off with any advance |

**The MSC lane is live and these paths were left alone.** Owner: claim
`the-msc-replacement-win-lands-before-the-post-s12g-book`, `longjob-land8-msc-replacement-win`,
`land8.sh` pid 916978, waiting through `wait_for` pid 916982 on the s.12g book pid 65649. It lands
`msc8.patch` from its own worktree `/var/tmp/se-msc-wt` and never reads these shared copies.
`refresh_to_head --base origin/main` refuses 7 of the 8 (holder work, or an ordinary edit), and
that door is right to refuse while MSC is not on origin.

## The other holders of the advance (reconcile-watch 00:39Z: 6 of 41 not provable)

The 6 are `saas/reporting/annual_report.py` and `simulation/run_phase2b.py` (above),
`tests/simulation/test_run_phase2b.py` (salvage `a00ac96e63`, ages out ~24 Nov 09:23Z, per
f80cc5a46), and **the orienting seat's own records**: `docs/direction/DIRECTION.yaml`
(4 conflicts), `docs/direction/decisions.jsonl` and `docs/status/SEAT_STRETCH_LOG.md`, all
written 0.2 h before. Those are the seat's live records and land by its own route. They were not
touched.

## When the advance can happen

After MSC reaches origin, 6 of the 8 code copies become strict subsets of origin. The
exceptions are the 3 draft lines above, and they keep `annual_report.py` and `run_phase2b.py`
conflicting. The reconciler's 48 h abandonment line takes them at ~25 Nov 05:32Z and ~06:18Z.
Nothing about the book waits on that any more.
