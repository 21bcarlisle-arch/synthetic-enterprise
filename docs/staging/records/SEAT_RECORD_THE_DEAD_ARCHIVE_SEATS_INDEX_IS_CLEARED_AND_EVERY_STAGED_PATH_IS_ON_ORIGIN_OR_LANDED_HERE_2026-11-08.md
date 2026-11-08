**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The dead archive seat's index is cleared, and every staged path is on origin or lands here (2026-11-08)

Lane 0 claim `unstick-the-shared-checkout-before-the-monday-publish`. At 20:17Z the shared tree at
`/home/rich/synthetic-enterprise` was at 86e3373b79: 0 ahead of origin/main and 35 behind
(d5b17899ef). It held 637 staged paths left by the archive seat. That seat was not running: no
process named archive or unhooked was alive, and its last write was 08:47Z.

## The reversal

`git write-tree` on the index before anything changed: **`b940021baecc47ac71f25eb15ab82460ef23ea0d`**.
The tree object is in the object store. `git read-tree b940021bae` puts the index back exactly as it
was. I ran it again just before the unstage and got the same sha, so nothing was staged in between.

## Classification

Staged blobs were compared with `origin/main` at d5b17899ef.

| Group | Count | Verdict |
|---|---:|---|
| `archive/unhooked_supplier/**` (94 renames) + `archive/README.md`, `archive/conftest.py` | 96 | Identical to origin at the same path |
| `archive/MANIFEST.txt` | 1 | Index and disk equal 745a5fd27d's copy; origin has since revised it. On origin's history, nothing lost |
| `docs/staging/**` adds whose blob origin holds at another path (mostly `done/`) | 108 | On origin |
| `docs/staging/**` adds whose basename origin holds, bytes different | 16 | Each staged blob is in a commit (2 in origin's own history of the `done/` copy, 14 in earlier commits). Older drafts of filed documents; nothing lost |
| `docs/staging/records/PREREG_OWN_FORECAST_PLUS_BALANCE_…_2026-10-13.md`, `SEAT_RESULT_OWN_FORECAST_PLUS_BALANCE_…_2026-10-13.md` | 2 | **In no commit anywhere.** A filed prediction and its result from 13 Oct that never landed. They land in this commit |
| `docs/staging/reference/CLASS_FIGURES_ON_A_SUPERSEDED_CLOCK_2026-08-28.md` (M) | 1 | The index held the version before origin added the `Epoch`/`Atom` header fields (c7f87af406). The disk already equals origin. **Nothing to land** |
| Staged deletions of four `docs/staging/SEAT_FINDING_*` (30 Oct, 4 Nov) | 4 | Origin still holds all four at those paths. The unstage leaves origin's decision in force |
| `site/data/customers/*.json` | 409 | **Publish output that origin pruned.** All 409 were on origin and were later removed by `Auto-process run complete` commits: 267 last touched 26 Oct, 69 on 19 Oct, 64 on 13 Oct, 5 on 5 Oct, 4 on 25 Sep. They are not anyone's work |
| **Total** | **637** | |

I ran `git restore --staged` on exactly these 637 paths (731 with renames counted on both sides).
That left 0 staged. The working tree was not touched.

## What the index was not holding

The fast-forward is also held by the working tree, and unstaging does not change that. After the
unstage, `paths_blocking_fast_forward` named 125 paths. On disk, 113 equal origin's tip, so the
reconciler can clear them as twins. The other 12 differ from both HEAD and origin:

- **Nine are copies of a committed revision.** `archive/MANIFEST.txt`,
  `docs/design/ORPHAN_DISPOSITION_REGISTER.md`, `docs/design/orphan_baseline.json`,
  `tests/architecture/test_year_keyed_rate_table_census.py` and
  `tests/company/compliance/test_every_company_deadline_counts_on_the_one_calendar.py` are at
  745a5fd27d. `docs/market_research/payments_and_direct_debit_2026-10-25.md`,
  `simulation/run_phase4c_on_phase2b.py` and `tools/generate_billing_ledger.py` are at 75f66f6521.
  Both of those commits are on origin. `tests/background/test_publish_freshness.py` is at
  23e9917bc6, which is **not** on origin.
- **Three match no commit:** `docs/direction/DIRECTION.yaml`, `docs/status/SEAT_STRETCH_LOG.md` and
  `site/harness/index.html`. The first two were written at 18:29Z today by the seat on the shared
  tree, so they are live work. The stretch log and the harness page were carried by the reconciler.
  What happened to the direction record is under Result.

The reconciler's own classes deal with these: earlier-revision twins, superseded, carried and
abandoned. Its result is below.

## Result

`python3 -m background.origin_reconcile` ran at 20:22Z with the index clear. It proved 123 of the
125 blockers lossless or carryable. Two held it:

- **`tests/background/test_publish_freshness.py`** had not been written for 1,086 hours, and its
  merge conflicted once. Its disk blob, 3d92349a2b, is the copy on
  `refs/preserved/annual-report-stash-23e9917bc-20260925` (24 Sep). I checked the ref and found the
  same blob there before writing anything. The shared tree now holds HEAD's bytes, and the
  fast-forward installs origin's copy.
- **`docs/direction/DIRECTION.yaml`** is the seat's 18:23Z orientation, written on the stuck tree.
  It is the record the `DELIVERY_SEAT_THE_DIRECTION_RECORD_DID_NOT_REACH_ORIGIN` alarm is about, and
  it carries this item. Merging it with origin's copy gave four conflicts. Field by field, it already
  holds everything d087da7204 (the director's 8 Nov ruling) wrote, with one exception: the `evidence`
  field on `the-publish-window-is-anchored-to-monday`. That field is put back. This commit lands that
  copy, the seat's record plus origin's one field, and the shared tree's disk holds the same bytes.
  The seat's own disk blob before the edit is d8e3fcdfc2, which is in the object store.

The two 13 Oct records about the third DD review rule land in this commit.

**The reversal:** `git read-tree b940021bae` restores the index. Then
`git show 3d92349a2b > tests/background/test_publish_freshness.py` and
`git cat-file blob d8e3fcdfc2 > docs/direction/DIRECTION.yaml` put back the two disk copies.
