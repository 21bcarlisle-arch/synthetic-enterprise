# The withdrawn sanity-daemon manifest draft is cleared from the shared tree — 2026-09-29

**Item:** `clear-the-withdrawn-sanity-daemon-manifest-draft-from-the-shared-tree` (lane 0).

**Premise re-measured before acting.** The shared copy of `background/process_manifest.yaml` differed
from HEAD by exactly one hunk: 16 added lines, zero deleted — the sanity-daemon `log_silence` draft
(mtime 2026-09-28 16:20 BST). Not grown, so not live holder work. Its subject landed as 27aba4242 and
was withdrawn by 0afe22631; both are ancestors of origin/main, and origin's manifest carries none of
the draft's text. All 16 lines are present verbatim in
`records/SEAT_RESULT_THE_SHARED_TREE_IS_PINNED_BY_A_MERGE_BUDGET_ONE_RECEIPT_OUTGREW_AND_BEHIND_IT_BY_ONE_WITHDRAWN_MANIFEST_DRAFT_2026-09-29.md`
on origin.

**Done.** `refresh_to_head` refuses the copy by rule (`refused_supplies_names_head_lacks`) — it
cannot tell withdrawn prose from holder work, which is the judgement this item existed to make.
So the refresh was done by hand under `shared_tree_lock`: the one-hunk shape was asserted inside
the lock, the copy written to blob `c1a9b18cd` under
`refs/preserved/refresh-to-head/withdrawn-sanity-daemon-log-silence-draft`, then HEAD's bytes
written. The shared copy now equals HEAD.

**To reverse:** `git cat-file -p c1a9b18cd > background/process_manifest.yaml`.

**Not this item's, named rather than touched.** `tests/tools/test_fold_noise_floor_family.py` in the
shared tree differs from both HEAD and origin/main, and its mtime (2026-09-28 05:57) predates
origin's last commit to that path (b9c9092e6, 2026-09-29 06:30). It may still hold the fast-forward;
the reconciler's next pass will say so. The other contested paths
(`process_run_complete.py`, `arrears_engine.py`, `run_phase4c_on_phase2b.py`,
`test_process_run_complete.py`) already equal origin/main, so the advance takes them as they are.

**Re-drawn and landed (later invocation, 2026-09-29).** The item was drawn again. The shared copy
still equals HEAD, and the preserved ref and blob `c1a9b18cd` are still there. So the work was done,
but this record had never been committed. The re-draw landed the record and did nothing else. The
shared tree is still 45 behind origin. That is no longer this manifest's doing:
`tests/tools/test_fold_noise_floor_family.py` still differs from both HEAD and origin/main, and
it is the next thing the reconciler's pass will name.
