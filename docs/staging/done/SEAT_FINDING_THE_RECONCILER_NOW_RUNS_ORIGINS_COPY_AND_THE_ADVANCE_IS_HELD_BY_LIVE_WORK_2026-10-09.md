# The reconciler now runs origin's copy; the advance is held by live work, not by the reconciler's age

**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-reconcilers-own-fix-cannot-load-until-the-advance-it-releases`

## Premise, re-measured at draw

- The duplicate claim the draw named was its own write, 22 s old. No other writer had the item.
- The shared tree's `background/origin_reconcile.py` has **zero** mentions of `test_execution_log`.
  Origin's copy declares it in `APPEND_LOGS` (91a798172). Confirmed: reconcile-watch
  (`WorkingDirectory=/home/rich/synthetic-enterprise`) loaded a reconciler that predates the rule.
- Shared tree at 06:47 BST: `e3e5970e1`, 85 behind, 0 ahead, last cycle `NOT_ADVANCED` on 27 paths.

## The 27 blockers, classified by origin's code (read-only, before the pass)

| Class | Paths |
|---|---|
| Untracked twin / earlier revision (lossless) | 14 staging notes |
| Untracked orphan, preservable | 3 staging notes (`ADVISOR_FINDINGS_IMPORT_GRAPH…`, `DIRECTOR_INSTRUCTION_MODULE_GRAPH…`, and one earlier-revision note) |
| Append log (91a798172) | `docs/observability/test_execution_log.jsonl` |
| Generated output | `site/data/delivery.json` |
| Abandoned (>48h) | `background/delivery_lane.py` (98.7h), `tests/background/test_supervisor.py` (98.0h), `tests/simulation/test_the_settled_book_draws_its_headcount_…py` (351.8h) |
| **Seat direction files, live (<1h)** | `docs/direction/DIRECTION.yaml` (0.3h), `docs/direction/decisions.jsonl` (0.1h), `docs/status/SEAT_STRETCH_LOG.md` (0.3h) |
| **Other live work (<48h)** | `docs/institutional/knowledge_map.md` (22.2h), `docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md` (22.2h) |

## The pass with origin's code

`advance_shared_tree` from this origin/main worktree: `advanced: false`, nothing written. 8 of 27 not
proven lossless: the 3 abandoned copies, which clear only when no live copy holds, and **5 live
copies**. The append log is **not** among them. Origin's rule clears it as designed.

**The class still holding the advance is LIVE WORK UNDER 48h**, and three of the five are the
seat's own direction files: `DIRECTION.yaml` carries +263/−217 against HEAD, `SEAT_STRETCH_LOG.md`
+316, and `decisions.jsonl` +9, all written in the last 20 minutes. Whatever writes the direction
record in the shared tree keeps a working copy diverged from HEAD and never lands it. While that
holds, no reconciler of any age can advance this tree. This is the subject of
`SEAT_FINDING_THE_DIRECTION_RECORDS_WORKING_COPY_IS_READ_CARRIED_AND_RECORDED_AS_IF_IT_WERE_ORIGINS_2026-10-07.md`;
it is now measured as the binding cause of the 85-commit stale fleet.

The item's DONE ("a cycle reads ADVANCED with HEAD 0 behind") is **unmet** and cannot be met by the
reconciler. It needs the direction files landed (or their writer moved to land them), and the two
22h documents three-way merged onto origin by their owner.

## The class this exposed, and the bootstrap

A fix to the reconciler loads only after the advance it exists to release. `reconcile_watch` now
routes a **behind** tree to `_reconcile_with_origins_code`. That function checks out `origin/main`
in its own detached worktree (`/var/tmp/se-reconciler-bootstrap`, owner-marked while it runs) and
runs `python3 -m background.origin_reconcile --json` from there. If it cannot stand on origin's
sha, it returns `ERROR … NOTHING WAS RECONCILED` and runs nothing. Ahead-only still runs in process,
because HEAD then contains origin.

- Control: `tests/background/test_reconcile_watch.py::test_a_behind_tree_is_reconciled_by_ORIGINS_copy…`
  is a partition over behind / diverged / ahead-only. It reds on the previous arrangement, where the
  imported copy always ran. A mutation that disables the routing reds it; a mutation that disables
  the sha check reds the fail-closed control.
- Live: run from this worktree against the shared tree, the leg printed
  `NOT_ADVANCED [STILL OPEN]: [origin's reconciler @46951a0ee] …` in 34 s, with the marker removed.

**The bootstrap is itself in `reconcile_watch.py`, which the shared tree loads only after ONE
advance.** It therefore protects every later reconciler fix, but not this one. That is the honest
limit; today it costs nothing, because origin's reconciler refuses for the same live-work reason.

## Actioned, 2026-10-09 (worker tick, ~09:18 BST)

**The DONE is met: the shared tree advanced and reads 0 behind, 0 ahead.** The finding's named cause had
gone stale by the time I drew it, and the actual holders were a different class.

- **The direction files no longer held anything.** By 09:05 `DIRECTION.yaml`, `decisions.jsonl` and
  `SEAT_STRETCH_LOG.md` matched origin byte for byte. Origin's `earlier_revision_twins` puts them
  in a lossless class, so whatever writes them had landed them. The "writer never lands" cause is
  not what held the advance this morning. The 2026-10-07 direction-record finding stays the
  subject for the *pattern*, but it was not binding here.
- **What did hold it: six live (<48h) copies that origin supersedes, plus a staging archive that
  origin reversed.** Each copy was an earlier draft of a later origin revision. Checked by diff
  against origin's history, not assumed:
  `canon_claims.yaml` and `test_canon_drift_check.py` had zero lines that origin lacks;
  `site/index.html` was identical to origin; `maturity_map.yaml` lines were older levels and
  counts; `knowledge_map.md` rows were older wordings; and the save-offer doc said "no Pending
  notice is built", which origin `4805420bd` reversed by building the CSS ITI. The debtor-switch
  note had been moved to `done/` locally, but origin edited its root copy again at 09:09.
  No reconciler class covers "under 48h but strictly superseded", so all of them held the advance
  under the all-or-nothing rule.
- **The remedy:** preserve the bytes, read them back, and restore HEAD under `tree_lock`. All seven
  are on `refs/preserved/superseded-live/20261009T091805` (`b84ae812e`), recoverable with
  `git show <ref>:<path>`. Then origin's `advance_shared_tree` ran and cleared the other 33
  (twins, earlier revisions, append log, generated output, 4 abandoned copies, each on its own
  preserved ref) and fast-forwarded.
- **The class left open:** a copy under 48h that origin strictly supersedes, where every local
  line is either in origin or an earlier wording of origin's line. The reconciler cannot clear
  it today, and it holds the whole fleet until a human or a tick does it by hand.
  `refresh_to_head`'s superset judgement reads Python only, so these doc/YAML copies fell through.
  Not built here: whether "an earlier wording" is mechanically decidable outside the
  zero-novel-lines case is an open question, and the zero-novel-lines case (two of the six) is
  the safe first leg.
