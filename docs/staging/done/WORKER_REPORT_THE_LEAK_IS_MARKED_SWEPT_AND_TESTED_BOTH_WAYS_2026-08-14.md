# [WORKER-REPORT] The landing tool's leak is closed: marked, swept, tested both R15 directions (2026-08-14)

**Severity:** RECORDED · **Lane:** H_harness

**Header added 2026-08-15, and the "PENDING, not done" sentence below was STILL TRUE when it
was added.** This report reached the staging root with no machine-readable severity, so
`background/finding_severity.py` read it UNCLASSIFIED and `background/gate_authorization.py` held
level-recording in EVERY lane (an unclassified document's severity could be BLOCKING and its lane
is unknown, so it cannot show any lane clear). RECORDED is the right severity: the CODE fix
landed and was receipt-verified at `5bf1efd52`, which is what this report is about.

**A correction to this note's own first draft, kept because the class is worth more than the
tidiness.** The first draft asserted the archival had landed, on the strength of an `ls` of
`docs/staging/done/`. It had not. `git ls-tree HEAD` showed the path in NEITHER room: the archive
move existed only as a staged-but-uncommitted `A ` entry in the shared index, exactly as the
paragraph below said. The gate refused the commit and named it — `_landed_manifest_check`, which
resolves a document's `LANDED` claim against the tree the commit would create rather than against
the filesystem. **`ls` reads the working tree; a claim about what is archived is a claim about the
tree.** This is the same class as
`WORKER_FINDING_A_PATHSPEC_COMMIT_LANDED_THE_CONSUMER_AND_LEFT_THE_SUPPLIER_STAGED_2026-08-14`,
caught here by a control rather than by a reader.

**Now discharged rather than re-promised:** the archival is landed in the same commit as this
note, so the sentence below is superseded by an act, not by an assertion. The finding is in one
room only — it was never committed to the staging root, so no deletion was owed and the
two-rooms rule is not in play.

**Closes:** `WORKER_FINDING_THE_ONLY_LEGAL_LANDING_MOVE_LEAKS_150MB_A_KILL_2026-08-14.md` (BLOCKING,
H_harness) — drawn ahead of the general disposition queue per OPS12 clause 3, as the doorbell
instructed. The CODE fix is landed and pushed (below). **This report's own archival commit —
moving the closed finding to `docs/staging/done/` — is PENDING, not done**: the first attempt hit
`WORKER_FINDING_298_SIMPLIFICATION_FILES_SIT_UNCOMMITTED_AND_THREE_ALREADY_DESYNC_THE_MAP_2026-08-14.md`,
a separate, larger, unrelated defect this tick found and filed rather than fixed blind. Both this
report and the `done/`-moved finding file sit correctly in the working tree, uncommitted, ready to
land once that blocker clears.

## What was owed, and what landed

The finding's four asks, `tools/surgical_land.py`, commit `5bf1efd52` (pushed, receipt-verified —
`python3 -m tools.surgical_land --verify 5bf1efd52` → `receipt consistent ... gate-rc 0`):

1. **`atexit` + `SIGTERM`/`SIGINT` handler** — `_install_signal_handlers()` cleans up the current
   checkout on a routine kill; `atexit.register(_cleanup_active_checkouts)` covers normal
   exceptional exit. Acknowledged as insufficient alone (no handler catches `SIGKILL`), which is
   why (2) is not optional — matches the finding's own framing.
2. **Startup sweep of stale `surgical-land-*` extracts** — `sweep_stale_extracts()` runs before
   every landing attempt (`_land_once`, before `materialise`). Every checkout is stamped with its
   owning PID (`OWNER_MARKER = ".owner-pid"`) the instant it exists — written before anything else
   can fail or take long — so the sweep (this process's own next attempt, or a concurrent lane's)
   can tell a live extract from an abandoned one. A directory with no marker (every extract made
   before this fix — the 24-directory backlog the finding measured) or a marker naming a dead PID
   is removed; a directory with no live holder is by definition abandoned, since the tool creates
   exactly one checkout per run and removes it in `finally:`.
3. **R15 both ways** — `tests/tools/test_surgical_land.py` gained 8 tests:
   `test_sweep_removes_a_markerless_legacy_extract` and `test_sweep_removes_a_dead_extract` pin
   the sweep firing on its own named defect (a real dead PID, obtained by spawning a subprocess
   and waiting for it to exit — not a guessed-unused number); `test_a_live_extract_survives_the_
   sweep` pins the fail-dangerous direction — a marker naming the CURRENT process's own live PID
   sits in the same directory, matches the same glob, and is left standing while its dead sibling
   is removed. `test_sweep_ignores_the_index_tempfile_and_unrelated_directories` and
   `test_a_landing_writes_the_owner_marker_before_anything_else_can_fail` cover the two ways this
   could quietly become a tautology (matching a file instead of a dir; a real landing leaking its
   own marked checkout despite the new code path). 33 tests total in the file, all green.
4. **The refusal names what it found** — `materialise()` now takes the sweep's own `(count, mb)`
   and folds it into the disk-refusal message: *"Swept N stale surgical-land extract(s) first,
   reclaiming MMB — still short."* `test_a_disk_refusal_names_what_the_sweep_found` forces the
   refusal path (`MIN_FREE_MB` monkeypatched to an unreachable value) and asserts the message
   pattern, so a regression that silently drops the stat back to `(0, 0)` reds.

## What was NOT changed, on purpose

The finding's own caveat held: *"it is a change to the landing tool itself, and a landing tool
cannot safely be edited by the tick that is mid-landing through it."* This tick edited the tool
first, landed the edit through the **unmodified** tool (git log shows `5bf1efd52`'s own gate ran
against the resulting tree containing the new code — the tool gated itself), and only the
now-landed version carries the fix forward. No attempt was made to retrofit the sweep into the
in-flight commit that created it.

## Verified on real disk state, not just the test suite

    $ python3 -c "from tools import surgical_land as sl; print(sl.sweep_stale_extracts())"
    (0, 0)
    $ df -h /tmp
    7.8G total, 3.1G used, 4.8G free, 40%

Zero stale extracts on the real box right now — the finding's own text already noted the leaked
space had been reclaimed by hand ("Status: measured, and the leaked space reclaimed"), so this
run's sweep had nothing left to do. The mechanism is proven by the planted-defect tests above, not
by this incidental zero.

## Landing itself hit the exact race class this repo already knows about

The `surgical_land` commit landed clean (`git log` shows `5bf1efd52` on `origin/main`), but the
final real-index refresh step failed once with `ex.lock': File exists` — a concurrent `git commit`
(another lane, `site/data/publish_provenance.json`) held `.git/index.lock` at that instant. Per the
tool's own refusal text, waited for the lock to clear (~8s) and ran `git reset -- tools/surgical_
land.py tests/tools/test_surgical_land.py`, confirmed `git diff HEAD` for those two paths is empty
afterwards. HEAD was never at risk — `_commit_and_swap` uses `commit-tree`/`update-ref`, not the
real index — only the working-tree bookkeeping needed the manual follow-up. No new finding filed
for this; it is the shared-tree collision this repo's `tree_lock` discipline already names.
