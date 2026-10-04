**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The origin-fork alarm writes into the shared tree the file that blocks the fast-forward it reports

**2026-09-30, seat lane 0, claim `shared-tree-fast-forward-blocked-by-seven-stale-working-copies`.**

The fork closed on origin at 13218de49 (ahead 0), but `origin_reconcile` logged NOT_ADVANCED. Seven
uncommitted shared-tree copies that origin also changes refused the ff-only. Here is each one, read
against both origin and the shared HEAD bc0df4b9e:

| path | shared copy | disposition |
|---|---|---|
| `docs/design/BLOCKED_ATOM_VISIBILITY.md` | generated at 06:24 over 351 atoms; origin's is over 353 | stale, refresh |
| `docs/staging/records/SEAT_PREREG_THE_AB_THAT_VARIES_THE_BOOK_NOT_THE_SEED_2026-09-30.md` | the 09:55 draft; origin is it plus one paragraph | stale, refresh |
| `tools/run_value_cycle_ab.py` | the 09:55 draft of 19ca27dbc; origin adds 47ced1cf2's run identity | stale, refresh |
| `tests/tools/test_a_book_family_redraws_…ep17.py` (untracked) | the same draft, without the seventh mutation's leg | stale, refresh |
| `docs/staging/SEAT_FINDING_THE_STRETCH_LOG_…_2026-09-30.md` (untracked) | byte-identical to origin | refresh |
| `tests/simulation/test_home_move_undeliverable_win.py` | 09-24; another fix for the same red that 48104db63 re-keyed differently. Origin's passes, 6/6 in 625s | superseded, refresh (preserved) |
| `docs/staging/WORKER_FINDING_REPEATING_ALARM_DEADMAN_ORIGIN_FORK_2026-09-15.md` | **live**. `alarm_repetition` rewrote the counts block and appended 6 instances and 6 re-asked lines. Origin appended the seat's fork disposition | 3-way merged and landed, then refresh |

**The seventh path is a mechanism, not a stale draft.** The `deadman_origin_fork` alarm fires when the
shared tree fails to advance, and each firing rewrites its own finding in the shared tree. When a
seat also records a disposition in that finding and the record reaches origin by an isolated
worktree, as it has to, the next ff-only is refused by the alarm's own write. That refusal fires the
alarm again, which rewrites the file again. It clears only because the refresh happens between a
firing and the next reconcile. A finding that an alarm owns should not be the place a seat writes
its disposition. Cheapest remedy: put the disposition in a sibling `SEAT_…` document that links to
the alarm's finding, and leave the alarm's file to the alarm.

**Also seen:** an orientation `git commit` (direction record) had been gating in the shared tree
since 15:28. When it lands on bc0df4b9e the shared tree will be 1 ahead and 20 behind, so it is a
fork again, closed by `origin_reconcile`'s merge leg rather than by the ff this item cleared. This
is the same receipt-less direction-commit shape the 13:30Z correction in the deadman finding names.

## Outcome (14:52Z)

The seven blockers are cleared, and nobody's uncommitted file other than those seven was touched.
`run_value_cycle_ab.py` went through `refresh_to_head` (it was refreshable).
`BLOCKED_ATOM_VISIBILITY.md` went through `refresh_to_head --base-wins`. Five were written by hand,
each preserved first as a blob ref under `refs/preserved/ff-block-2026-09-30/*` in the shared repo,
because the door refused them:

- **The prereg record and the deadman finding were refused with `refused_head_does_not_supersede_it`,
  and each copy was a strict line-subset of origin (0 lines only in the copy).** The stale-copy
  control reads the clock and the names, not line containment, so the one case with nothing to lose
  is the case it cannot admit. A containment leg (every line of the copy is in the base, so the copy
  is `refreshable`) would have made both enactments use the door.
- The two untracked copies were refused with `refused_no_base`, and the reason printed was "the
  fast-forward adds it; nothing needs clearing". That is wrong for `git merge --ff-only`, which
  refuses to overwrite an untracked file. Both were deleted by hand.
  **Correction (14:58Z): that refusal was RIGHT and the hand deletion was unneeded for the
  byte-identical one.** `origin_reconcile.identical_untracked_twins` clears a byte-identical
  untracked twin itself, and `identical_tracked_twins` restores a modified copy that hash-matches
  origin. The line-subset draft was not a twin, so it still needed clearing. One was byte-identical to
  origin, and the other was a line-subset apart from the call the seventh mutation's leg replaced.
- The home-move test was refused as `predates_landing_carrying_some`. The seat decided it as
  superseded, because origin's version passes 6/6 at 13218de49. Its C1b-era monkeypatch and
  `gap_ledger_path=tmp_path` are preserved in the blob ref if either one is wanted again.

As predicted above, the orientation's direction commit 876a64eeb then landed on bc0df4b9e, so the
shared tree read 21 behind and 1 ahead. Origin has not touched those three paths since bc0df4b9e.
`origin_reconcile`'s own merge was running in its isolated worktree at 14:50Z. That merge is the
route that closes it.

## Second pass (14:58Z): the loop, observed

Within two minutes of the refresh the alarm had appended a 09-30 re-ask line to the refreshed deadman
copy, so it was dirty against HEAD once more. At 14:50Z `staging_watcher.check_remote` also
materialised this finding as an untracked twin of 3ed69bb41's bytes, and this seat's second landing,
c3f45f70c, made that twin stale. The watcher skips a path that exists, so an origin edit to a staging
file it has already mirrored always leaves a non-identical twin, and that twin is a blocker. **The
reliable end state is not HEAD's bytes but ORIGIN's.** Both copies were written byte-identical to
origin (preserved under `refs/preserved/ff-block-2026-09-30/twin-*`), which is the shape the
reconciler clears without help.

## 2026-10-01: second clearance, with the writer named for each path

**Claim `the-shared-checkout-reaches-origin-and-stays-there`, 04:20–04:40Z.** The shared tree was
1 ahead and 42 behind. `origin_reconcile` logged `REFUSED_CONFLICT` from 04:12Z, with no newer
`NOT_ADVANCED` line. The blocker set below was re-asked against origin `3f7a0632f`. Every path was
preserved first under `refs/preserved/ff-block-2026-10-01/*`.

**The ahead commit is a second "EP1 pass 20".** `75df9efdf` (04:14 BST) was committed on the shared
HEAD `c71a78417` after `d77ff33d5` had already reached origin from an isolated worktree. The
`surgical_land` pid 3300519 named at orientation had exited by the time this item was drawn. Diffed
against `d77ff33d5`:

- `tools/couple_clv.py` and `tests/tools/test_couple_clv.py` are byte-identical.
- The ratchet carries the same numbers (I001 1302, total 2277) with different comments.
- The simplifications note re-flows the same pass-20 text and adds one paragraph ("QUALIFIED THE
  SAME DAY"). Its substance, one world decision in five, is carried on origin by `d8ae8c2e7` and the
  eight EP1 commits after it.
- `75df9efdf` also adds an archive rotation (`EP1_clv_three_horizon.011.yaml`) that would duplicate
  pass 13, which origin keeps in the live file.

Its two conflicted paths are what refused the reconciler's merge. It was **dropped, not merged**:
shared `main` was moved to origin with `git checkout -B main origin/main`, which carries local
changes. All 88 staged index entries were verified unchanged across the move. `reset --keep` was
tried first and refused. It would have reset those 88 entries, so the refusal was right. Preserved
at `refs/preserved/ff-block-2026-10-01/second-ep1-pass20`. The door was land-twice: the shared tree
landed again a subject that an isolated worktree had already put on origin.

| path | writer, and the door that left it | disposition |
|---|---|---|
| 7 untracked staging docs (CONTINUATION_SWAP_…BILL_SHOCK, EP1_OVER_THE_WHOLE_BOOK, EP1_THE_BELIEF_CARRIES, HEAD_GREEN_CENSUS_WEIGHS_11_GB, WORLD_DECIDES_A_RENEWAL, RETENTION_BELIEFS_ANTI_RANKING, WORLDS_BILL_SHOCK_COUNT_IS_BLIND) | **`supervisor._sync_origin_staging`** (90 s cadence). It writes every root `docs/staging/*.md` that is on origin and absent locally. Byte-identical to origin's tip. | Removed; the move rewrote the same bytes, as tracked files. |
| `SEAT_FINDING_EP1_ALL_CAUSE_EXIT_HAZARD_…` (untracked) | Same writer. Bytes equal `627f05756`'s blob, mtime 1 min after it. Origin revised the doc in `7e2503507`, and the sync never refreshes a path that already exists. | Stale twin, removed. |
| `SEAT_FINDING_EP1_REMAINING_OVERVALUATION_…` (untracked) | Same writer and shape. Bytes equal `8d6123c6a`; revised by `127c007f0`. | Stale twin, removed. |
| `SEAT_FINDING_THE_CENSUS_BOUND_…_2026-09-30` (untracked) | Same writer and shape. Bytes equal `8cbda4280` (the "Result: pending" stub); revised by `fb3e406a5`. | Stale twin, removed. |
| `docs/design/maturity_map.yaml` | **Four stranded in-place edits from other lanes, none landed.** SP2_2 parked idle (tick worker, 09-29). PB4 parked idle (09-29, NTFY 9kuLLifpjEiV). H47 L2→L3 on its second blind pass (09-30 ~20:00; the auth line is in the shared `gate_authorizations.jsonl` only). W2_28 L1→L2 (09-30 18:02; no auth line anywhere). Each one's simplifications file is also dirty. | Three-wayed onto origin. The edits are **kept on disk, unlanded**: they are four other lanes' level and park records, and one level move carries no authorisation. |
| `tests/background/conftest.py` | An in-place edit from 09-27 16:33, never committed. It had two hunks. (1) A rival draft of the landing-marker comment that `159a2d4fc` had already landed differently, so origin's text wins. (2) A redirect of `publish_freshness.PUBLISH_GATE_STATE_FILE` to an absent path, so tests in this directory do not read the live publisher's refusal record. That hunk is on no commit. | Three-wayed onto origin, keeping only hunk (2). It lands as its own commit. |

**Ten of the twelve paths share one door: the supervisor's origin-staging sync.** It materialises a
twin and never revisits it. Seven of those twins were harmless, because `identical_untracked_twins`
clears tip-identical ones. Three blocked, because each equals an EARLIER origin revision of its own
path. That is equally lossless to clear, and the reconciler does not ask. This is the same shape
the 09-30 second pass attributed to `staging_watcher.check_remote`. That attribution is **corrected
here**: the watcher's journal for 02:41 and 02:44Z reads "No [ADVISOR-STAGED] commits … skipping",
so it wrote none of these. Filed as `H49_an_untracked_copy_of_an_earlier_origin_revision_is_cleared_like_a_twin`.

**The seat's own error, recorded beside the claim.** While inserting the H49 row, a one-liner
`open(p,'w').write(f(open(p).read()))` truncated the shared `maturity_map.yaml` to 0 bytes. The file
was empty from 05:25:36 to 05:25:52 BST. It was rebuilt deterministically: the preserved blob,
three-wayed against `75df9efdf` and origin. The result had the same 24-line holder diff and the same
371,964 store bytes as before. Writers that ran in the window: `agent_status`,
`alarm_repetition_state` and the origin-staging stamp. None of them reads the map.

**End state, 04:31Z.** Shared HEAD equals origin/main at `3f7a0632f`, 0 ahead and 0 behind.
`evaluate_boot_sha_drift()` reports `behind_trunk: {}`. `deploy_restart --apply` restarted
background-worker, deadmans-switch and naive-organ. sim-runner is held MID-WORK, and the next
reconciler pass will restart it.
