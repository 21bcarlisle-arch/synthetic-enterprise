# Disposition — the stale fold-noise-floor test copy was already refreshed to HEAD (2026-09-29)

**Item:** `judge-the-stale-fold-noise-floor-test-copy-holding-the-shared-tree-fast-forward` (lane 0).

**Spent on arrival.** The shared tree's `tests/tools/test_fold_noise_floor_family.py` is identical to
HEAD (`git status` clean for the path). Another lane ran `tools.refresh_to_head` at 09:27:47; the
door judged the copy supplied no name HEAD lacks and preserved its bytes at
`refs/preserved/refresh-to-head/fold-witness-selector-residue` (f08a5be81) before writing HEAD over
it. Nothing to land, nothing lost.

**What still holds the fast-forward** (HEAD 0 ahead / 47 behind origin/main; dirty paths that
origin also changes): `background/process_run_complete.py`,
`tests/background/test_process_run_complete.py`, `simulation/arrears_engine.py`,
`simulation/run_phase4c_on_phase2b.py`,
`docs/staging/reference/CLASS_MEASUREMENTS_THAT_MIRROR_2026-08-12.md`. These are outside this item's
scope; each needs the classifier run against an advanced base, not a guess from here.

**Ledger binding (tick worker, later 2026-09-29).** Since this morning, the brief has listed this row and two siblings against commits on no remote ref. Each is now bound to a commit on origin/main with `--premise-spent`:
- this item → `19286b105` (the 14 fast-forward-holding paths are copies that origin supersedes);
- `grade-the-plus-880-once-the-decision-fields-are-on-origin` → `5cbbad968`, which is the grade itself. The row read `landed_unbound` on `9f929478e`, a local refresh-to-head preservation commit. `--landed` refused because the claim had already been released;
- `land-the-stranded-arrears-lines-with-the-decision-fields` → `5f05e0068`. Its stranded copies were superseded: the arrears lines landed in `f997f8bf7` and the decision fields in `5f05e0068`.
