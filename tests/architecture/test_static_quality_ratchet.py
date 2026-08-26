"""Static-quality ratchet — the ruff baseline (STATIC tier).

WHY THIS EXISTS
---------------
`ruff check .` (the `lint` half of `make check`) currently reports ~2,421
pre-existing errors, so the lint step is a permanent red wall: it blocks the
whole `check` target, which means new lint sins land invisibly behind the
existing noise — nobody re-reads a 2,421-line failure.

This module makes that measurable and UN-REGRESSABLE without fixing a single
pre-existing error, using the same dated, shrink-only ratchet the project
already applies to the epistemic wall (see
tests/architecture/test_epistemic_wall_ratchet.py for the house idiom):

  * RUFF RATCHET — a dated baseline {rule_code: count} frozen from today's tree.
    A NEW rule code (count > 0, not in the baseline) fails. An EXISTING code
    whose count rises above its baseline fails (a regression). A code whose
    count FALLS below its baseline fails as STALE until the baseline is
    shrunk to match — so the baseline can only ratchet down, never silently
    absorb a fix without recording it.

The ratchet fixes nothing. It freezes the debt at today's level and makes every
future delta visible and reviewable — exactly what the lint wall cannot do.

THE MYPY HALF WAS REMOVED (2026-08-08, worker tick) — READ BEFORE RE-ADDING
---------------------------------------------------------------------------
This module used to carry a second, parallel MYPY ratchet: a 551-entry
{module_path: error_count} baseline plus four census tests, a host guard, and
its own mutation proofs. It was removed, not skipped, because it could not run
AT ALL on the only machine that exists — and while it remained it blocked every
publish for hours (7 run_complete markers queued unpublished on 2026-08-08).

Three of its own declared premises are false here (observed, R9):

  * RUFF_PIN was 0.16.1        — installed ruff is 0.15.16, and requirements.txt
                                 itself pins ruff==0.15.16.
  * MYPY_PIN was 2.3.0         — mypy is NOT INSTALLED (no dist metadata) and is
                                 not a declared dependency in requirements.txt,
                                 so `_installed_version("mypy")` raised
                                 PackageNotFoundError and reddened the pin test.
  * RESIDENT_PYTHON was (3,12) — this host has exactly ONE interpreter,
                                 CPython 3.14 (/usr/lib/python3.14; the venv has
                                 pointed at it since 2026-06-11). No 3.11 or
                                 3.12 is present, so the "3.11 counts 542 vs
                                 resident 3.12 counts 551" determinism note
                                 describes an environment nobody here can reach.

The frozen census therefore cannot be reproduced, re-frozen, or even compared
on this host, and no source change can clear it: mypy cannot be installed in an
autonomous run, and CPython 3.12 is absent. Marking it `operational` (the first
attempt) moved the red off the publish gate but left it wedging the pre-commit
gate for its own file and standing permanently red on the operational-layer
signal, where it drove a PRIORITY-ZERO draw every tick — a false alarm that
crowds out real work. R15 says an unavailable check is a FAILED check and must
never be quietly skipped; it does not say a check that can ONLY fail, on
evidence nobody can act on, earns its place. So it is DELETED, with the
provenance recorded here rather than left as an orphan baseline nobody compares.

TO RE-ADD IT, in this order: install mypy and pin it in requirements.txt;
reconcile the interpreter (mypy.ini still says python_version = 3.11 while the
host runs 3.14); RE-FREEZE the baseline from a real run on THIS host — never
re-instate the old 551 numbers, which no run here produced.

DETERMINISM / VERSIONING (READ BEFORE UPGRADING A TOOL)
-------------------------------------------------------
A lint baseline is only meaningful PER TOOL VERSION: ruff adds, renames, and
re-scopes rules between releases, so the same tree yields different counts under
different versions. The version is therefore PINNED here (RUFF_PIN) and
`test_tool_versions_are_pinned` fails loudly with a one-line upgrade instruction
on any drift, and additionally cross-checks the pin against requirements.txt —
two independent sources, so a requirements bump that would silently invalidate
the baseline reds instead. **Upgrading ruff means re-freezing BOTH the pin and
the baseline in the SAME PR** — never bump one without the other.

R15 (CONTROLS_THAT_CANNOT_FAIL) — every assertion below is paired with a
mutation proof: a synthetic violation (in-memory blast-radius tests) and a real
one written to a tmp tree and run through the actual tool, each proving the
control reds EXACTLY the new-violation assertion and nothing else (not the
stale-entry check).

Dependencies: pytest + the pinned ruff CLI + Python stdlib only. No project
imports, so this suite runs even when the app's runtime deps are absent.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from functools import lru_cache
from importlib import metadata
from pathlib import Path

# --------------------------------------------------------------------------
# Pins, scope, and paths.
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = REPO_ROOT / "Makefile"

# The ruff version the baseline below is frozen against. A baseline is only
# valid for the exact version it was frozen under (see the module docstring).
# Cross-checked against requirements.txt by test_tool_versions_are_pinned.
RUFF_PIN = "0.15.16"
REQUIREMENTS = REPO_ROOT / "requirements.txt"

# Date the baseline was frozen. Shrink-only from here.
BASELINE_DATE = "2026-08-06"

# --------------------------------------------------------------------------
# RUFF BASELINE — dated {rule_code: count}, frozen 2026-08-06.
#
# SHRINK-ONLY. To pay down debt: fix the violations, then LOWER the count here
# (or delete the entry when it hits 0). Never RAISE a count or ADD a code to
# silence the suite — a new/rising code is a real new lint sin; fix it instead.
#
# SHRINK LOG — every downward move, with the reason (the ratchet's own remedy).
#   2026-08-26  F841 128 -> 127  (the CLV selection-profile commit)
#     `couple_clv.build_observations` bound `accounts = run.get("by_billing_account")`
#     and never read it — the population it actually walks comes from
#     `known_accounts(run, snapshots)` one line down. Found by running ruff over the
#     files that commit touched rather than by looking for it, which is the only way
#     a per-file ratchet ever gets paid: the debt is invisible until something else
#     brings you to the file. Removed rather than left as a free shrink deferred to
#     nobody, because a pre-existing violation in a file you are already editing is
#     the cheapest one this ratchet will ever offer.
#     TWO counts, TWO different causes, and only one of them was a working-tree
#     transient — the split matters, because freezing the tree's number would have
#     re-frozen a floor HEAD had already left.
#       1375 -> 1374  HEAD ITSELF had already fallen to 1373 and nobody re-pinned it.
#             Measured this tick against a real `git archive HEAD` extraction (NOT
#             the working tree, per this log's standing rule): HEAD I001 = 1373,
#             HEAD total = 2379. The commits that took it there never ran this test,
#             because the pre-commit gate maps tests to CHANGED PATHS and none of
#             them selected `tests/architecture/` — the mechanism named in
#             `WORKER_FINDING_A_RED_AT_HEAD_IS_INVISIBLE_TO_EVERY_COMMIT_THAT_DOES_
#             NOT_SELECT_ITS_FILE_2026-08-15.md`. A shrink-only ratchet cannot see
#             its own good news, so the stale-baseline red waits at HEAD for the
#             next wide-pathspec commit. The content publish is always that commit.
#       1374 -> 1373  ONE real, fixable violation, in the working tree only:
#             `tests/background/test_publish_gate_subject_is_head.py` carried a
#             53-line uncommitted addition whose new
#             `from tests.background.publish_gate_root_shape import ...` left the
#             block un-sorted (I001 at :45). Repaired at source with
#             `ruff check --select I001 --fix` on that one file, per this ratchet's
#             own remedy — not baselined around. Tree and HEAD now agree at
#             I001 1373 / total 2379, so the frozen floor is committed truth again.
#     Recorded rather than left stale, per this log's standing rule.
#   2026-08-14  E402 195 -> 176, F811 96 -> 95, I001 1376 -> 1375, F401 279 -> 278
#     (publish-gate wedge, priority-zero unwedge tick.) `real_ruff_counts()` was
#     exceeding on E402 (195 vs floor 193) and F811 (96 vs 95) and blocking the
#     publish gate outright (`test_ruff_no_rule_exceeds_baseline` runs inside the
#     blocking scope, `tests/architecture/` collects before the OPS2 failure this
#     tick was drawn to fix). Both were real, findable regressions, not baseline
#     drift, and both are repaired at source per this ratchet's own remedy:
#       E402  `saas/reporting/annual_report.py` carried a module-level
#             `_PROJECT = Path(__file__)...` BETWEEN `from pathlib import Path`
#             and the rest of the import block -- the exact recurring shape this
#             log already names four times above (2026-08-09, 2026-08-12 x2,
#             2026-08-13): every import after it reads as "code before imports".
#             071a60ec7 added one more import into that already-broken block
#             (194 -> 195); the underlying block itself had drifted 193 -> 194
#             some time before that and was never re-pinned. Moved the
#             assignment below the import block (its two use sites, both well
#             into the file, are unaffected) and the WHOLE file's E402 count
#             drops to 0, taking the file's 19 lines with it -- 195 -> 176, nine
#             below the recorded floor because the pre-existing 18 were never
#             isolated as their own debt before now.
#       F811  `tests/saas/reporting/test_annual_report.py` imported
#             `_build_clv_snapshots` from `saas.reporting.annual_report` at
#             module top (line 6, part of the shared import block) AND again at
#             line 2905 inside the `WORKER_FINDING_THE_BOOK_VALUE_COUNTS_
#             CUSTOMERS_WHO_HAVE_ALREADY_LEFT` test block, both `# noqa: E402`
#             (deliberate, mid-file) but the second shadowed the first (F811,
#             not noqa'd). Same name, same source module -- the second import
#             was dead weight. Removed; 96 -> 95, back at the frozen floor.
#     I001/F401 shrank as a side effect of the same two edits (fewer lines to
#     sort, fewer names to track) -- not independently hunted, and recorded
#     rather than left stale per this log's own standing rule. Verified against
#     a clean `git write-tree` export, not the working tree (the class this log
#     has caught twice already): `python3 -m ruff check .` inside a fresh
#     extraction of the tree this commit creates.
#   2026-08-13  E731 19 -> 19  (NO MOVE — the SECOND red at HEAD, hidden behind
#     the first) `tests/background/test_gap_ledger_reconciler.py` grew an
#     assigned lambda in 7a9bf56be. It was invisible while I001 was red because
#     the finding that reported the red quoted the I001 line only, and it was
#     invisible on the desk because the def-form repair was sitting UNCOMMITTED
#     in the working tree — the same uncommitted-and-orphaned-work class as the
#     I001 entry below, twice in one census. Committed, not baselined. LESSON:
#     re-run the WHOLE ratchet against a fresh HEAD export after clearing one
#     rule; a per-rule fix proves nothing about the other codes.
#   2026-08-13  I001 1379 -> 1378  (KNIFE3 step 24, the renewal rate-chain cut)
#     `simulation/run_phase2b.py` lost three company-pricing imports and gained
#     two seam imports; the block came back sorted. The floor moves DOWN with
#     it, per the ratchet's own rule that a remediation shrinks the baseline in
#     the same change.
#   2026-08-13  I001 1378 -> 1376  (publish-gate wedge clearance)
#     NOT a fresh remediation — a MISSED re-freeze. Measured by bisect over a
#     clean HEAD export: c96750be8 = 1379, c8284059b = 1376. So c8284059b
#     ("Publishing was dead for 21.7h") cleared THREE and re-froze only one, and
#     the floor has been 2 too high ever since. Confirmed committed, not tree
#     dirt: the dirty working tree and a clean 860ce6f70 checkout both count
#     1376, so this holds the floor at HEAD rather than freezing an uncommitted
#     improvement (the trap the 2026-08-12 entry above records).
#     Same commit, same shape as the `_check_content_publishing` hole in
#     tests/controls/test_daemon_loop_mutation.py: a control landed without its
#     census being re-run. Two reds, one cause.
#   2026-08-13  I001 1379 -> 1379  (NO MOVE — HEAD came back to the floor)
#     Logged here because a red at HEAD that nobody can attribute is how this
#     ratchet dies (WORKER_FINDING_THE_ISORT_RATCHET_IS_RED_AT_HEAD_2026-08-13).
#     HEAD stood at 1381 for two commits. The two blocks were identified by
#     diffing per-file `--select I001` censuses of `git archive` extractions at
#     the last green commit (33592d8d1) and HEAD — never by inference from the
#     working tree, which read 1380 and so understated the debt by one:
#       tests/tools/test_pre_commit_gate_class_checker.py  (landed f4b504e6c)
#       tests/background/test_tree_divergence.py           (its isort fix
#             existed ONLY as an uncommitted working-tree edit — the
#             uncommitted-and-orphaned-work class, committed here)
#     Fixed at source per this ratchet's own remedy; the baseline does NOT move.
#   2026-08-12  I001 1380 -> 1379  (KNIFE3 step 20, the churn-estimation cut)
#     `simulation/run_phase2b.py` lost one un-sorted import block when the three
#     churn crossings were replaced by one sorted `company.interfaces.*` +
#     `simulation.*` pair. A shrink that arrived as a side effect of a cut, not
#     as a lint pass — recorded here anyway, because a stale entry left unlowered
#     is how the floor stops holding.
#     The same step found F401 red at PRISTINE HEAD (281 vs the frozen 279), the
#     class this file's line ~197 already records: `tools/orphan_ratchet.py`
#     (unused `ast`) and `site/customers/test_wall_exhibit.py` (unused
#     `tempfile`), both landed in the preceding six commits by other lanes. Fixed
#     rather than baselined, which is this ratchet's own stated remedy.
#   2026-08-09  I001 1388 -> 1387, F541 28 -> 27  (SECOND publish wedge, ~10h)
#     The same disease as the 7h episode below, the same day, and the reason it
#     read as "stale" rather than "regression" is that the gate was red in BOTH
#     directions at once and each direction HID the other:
#       I001  a real regression landed at HEAD (1388 -> 1389) —
#             `background/blocked_atom_visibility.py` grew an unsorted import
#             block. But the working tree already carried the isort fix for it
#             AND for `tests/harness/test_conversation_gap.py`, both uncommitted,
#             so the tree linted 1387 and the gate only ever reported the stale
#             side. Fixed at source per the ratchet's remedy: both isort fixes
#             are COMMITTED here, so 1387 is the floor at HEAD and not a number
#             that depends on one concurrent writer's unsaved work.
#       F541  `tools/couple_w2_5_c7.py` lost its placeholder-less f-string in
#             D15 (30f111b9e). A legitimate shrink that was never recorded -> 27.
#   2026-08-09  E402 194 -> 193  (KNIFE pass 1, atom `KNIFE1_reporting_cycle`)
#     `saas/reporting/annual_report.py` line 41 was
#     `from simulation.run_phase4c_on_phase2b import main ...`, sitting below a
#     module-level `_PROJECT = Path(...)` and so counted as an E402. Cutting the
#     epistemic-wall crossing deleted the import and the lint with it. Lowered,
#     not left stale: the ratchet holds the new floor.
#   2026-08-09  I001 1392 -> 1388, F401 280 -> 279  (E402 back to 194, unchanged)
#     The ratchet went RED at pristine HEAD between 2026-08-06 and 2026-08-08
#     (E402 201, F401 281, I001 1396) and wedged the publish gate for ~7 hours:
#     process_run_complete rc=1 on ten consecutive run_complete markers. The
#     regression was bisected by diffing `ruff check --output-format=json` on
#     `git archive` extractions of the freeze commit (47fea05c2) and HEAD, then
#     fixed at source per the ratchet's stated remedy — never by raising a count:
#       E402  tests/simulation/test_arrears_engine.py (2, REPO_ROOT moved below
#             the import block), tools/couple_supply_start.py (5, already fixed
#             in the working tree by in-flight work) -> back to the 194 baseline.
#       F401  tools/target_design_delta.py (unused `os`; `RatchetUnavailable`
#             imported but only named in a comment) -> 2 fixed, and one earlier
#             fix in tools/generate_billing_ledger.py had already landed
#             un-recorded, so the floor drops to 279 rather than back to 280.
#       I001  background/process_run_complete.py, tools/generate_maturity_map_data.py,
#             tests/tools/test_map_assertion_provenance.py, tools/couple_supply_start.py
#             -> `ruff --select I001 --fix`, floor drops to 1388.
#   2026-08-09  I001 1387 -> 1386  (publish wedge episode 3; TWO causes, not one)
#     process_run_complete rc=1 on run_complete_20260809T125051Z.md wedged the
#     publish gate again. Both halves were measured against a `git archive HEAD`
#     extraction rather than inferred, because the two causes point opposite ways:
#       EXCEEDS (working tree, 1392): the in-flight `saas.customers.
#             customer_to_settlement_input` -> `company.interfaces.supply_book.
#             settlement_input` seam migration put the new `company.` import below
#             the `saas.` block in five `simulation/run_phase*.py` files, plus the
#             untracked `tests/company/interfaces/test_supply_book_seam.py`
#             -> `ruff --select I001 --fix` on those six, back to 1386.
#       STALE (committed HEAD, 1386): HEAD was already one BELOW the 1387
#             baseline — an earlier fix landed without shrinking the entry, so a
#             *pristine* tree still red-ed `test_ruff_no_stale_baseline_entries`.
#             Fixing only the working tree would have left the gate wedged.
#     Floor drops to 1386, which is now HEAD and working tree alike.
#   2026-08-09  I001 1386 -> 1385  (KNIFE pass 3, the first cuts)
#     Design B1 moved three behavioural-physics modules from `company/core/` to
#     `simulation/`. Renaming the import changed its ALPHABETICAL position, so
#     three unit-test modules that sorted clean at the old path sorted dirty at
#     the new one (working tree 1388). Fixed at source on exactly those three
#     (`ruff --select I001 --fix`), per the ratchet's stated remedy — the count
#     then landed at 1385 rather than back at 1386, because one of the three was
#     ALREADY an offender under its old name and the move happened to fix it.
#     The floor therefore SHRINKS by one: a drop caused sideways is still a drop,
#     and leaving it unrecorded is the exact stale-entry failure the 2026-08-09
#     episode-3 note above describes, which wedged the publish gate for hours.
#   2026-08-10  I001 1385 -> 1384  (KNIFE pass 3, B4 — the DD/refund cuts)
#     Design B4 moved `staggered_payment_day` from `company/billing/direct_debit.py`
#     to `simulation/dd_payment_day.py` and repointed the SIM consumers, two seam
#     doors and five test modules at the new path. The 08-09 B1 entry above led this
#     pass to EXPECT the same sideways breakage (a rename shifts alphabetical
#     position, so clean blocks sort dirty at the new path) — it did not happen, and
#     the per-file census is why that is stated rather than assumed: the ten touched
#     files carried 9 I001 at `git archive HEAD` and carry 8 now, the same blocks in
#     the same files minus one. NO new offender was created. The single drop is
#     `tests/simulation/test_dd_collection_book.py:145`, a two-name
#     `from company.billing.direct_debit import (...)` block that was already dirty
#     and became two sorted single-line imports when the moved name left it. A drop
#     caused sideways is still a drop, so the floor SHRINKS rather than being left
#     stale — the exact stale-entry failure the 08-09 episode-3 entry records.
#   2026-08-10  F541 stays 27, and the tree was made to MEET it (not the reverse)
#     The ratchet was red at PRISTINE HEAD when B4 was drawn — 28 vs the frozen 27 —
#     and it was NOT this pass's doing: bisected by `git log -L` over the census to
#     77c1654e0 (D19, the same day), which added a placeholder-less f-string at
#     `background/gap_metric.py:640`. Measured against a `git archive HEAD`
#     extraction rather than inferred, because a working-tree count cannot tell a
#     regression from a concurrent writer's unsaved fix — the exact confusion the
#     08-09 episode-3 entry above records. Fixed at source (one prefix deleted, no
#     behaviour), so the floor is unmoved and HEAD now meets it. A red-at-HEAD
#     ratchet wedges every lane's commit, so this is repaired here rather than
#     queued: it is a blocker, not a self-interrupt.
#   2026-08-12  I001 1384 -> 1380, E402 repaired to its floor (the 18th publish wedge)
#     The gate was red at COMMITTED HEAD — measured on a `git archive HEAD`
#     extraction, not the working tree, precisely because the 08-09 episode-3 entry
#     above records that a dirty tree cannot tell a regression from a concurrent
#     writer's unsaved fix. At d32ae058b: I001 1388 (baseline 1384) and E402 194
#     (baseline 193). Bisected by extracting every 20th commit: the last tree
#     meeting the floor was cff7a31a4 (2026-08-10 20:47Z); the excess ACCRETED
#     across ~25 commits over two days rather than arriving in one — no single
#     commit to blame, which is why it survived each individual pre-commit run.
#     Set-differenced the violation census green-vs-HEAD (not just the totals) to
#     name the seven files that newly offend, and fixed those only — a repo-wide
#     `--fix` would have rewritten hundreds of files on a tree with concurrent
#     writers. The one new E402 was `import subprocess as _sp` sitting mid-file in
#     tests/background/test_publish_decoupling_exit.py; hoisting it to the import
#     block cleared that file's E402 AND its I001 together. E402 is therefore back
#     AT its floor (193, unmoved — a repair, not a shrink). I001 lands at 1380,
#     four BELOW the frozen 1384, because the seven files fixed were more than the
#     four needed: the floor SHRINKS to 1380 rather than being left stale, per the
#     shrink-only rule this log exists to enforce.
#
# Top-10 offenders on the freeze date (also in the PR body):
#   I001 unsorted-imports .............. 1392  (now 1380)
#   F401 unused-import .................  280  (now  279)
#   E402 module-import-not-at-top ......  194  (now  193)
#   F841 unused-variable ...............  130  (now  128)
#   E741 ambiguous-variable-name .......  108
#   F811 redefined-while-unused ........   95
#   E702 multiple-statements-semicolon .   76
#   E701 multiple-statements-colon .....   45
#   F541 f-string-missing-placeholders .   28  (now   27)
#   E401 multiple-imports-on-one-line ..   21
# `invalid-syntax` (1) is a Python-3.12-only f-string in
# company/trading/emir_reporting_register.py.
#
# 2026-08-26  RED AT HEAD AGAIN, 22 violations across 8 codes; all 22 REPAIRED,
#   F401 SHRUNK 278 -> 277. This is the fourth entry in this log recording the same
#   shape, and the shape is not a coincidence: the pre-commit gate SELECTS TESTS BY
#   THE FILENAME STEM OF THE CHANGED PATHS, so this module runs only on a commit that
#   touches `test_static_quality_ratchet.py` itself. Every other commit is invisible to
#   it. That is the standing finding
#   WORKER_FINDING_THE_RUFF_RATCHET_IS_RED_AT_HEAD_AND_ONLY_SOME_COMMITS_CAN_SEE_IT
#   (2026-08-14), and it is a SCOPE defect in the control, not in the commits: a
#   shrink-only ratchet whose scope excludes almost every commit that can move it will
#   accrete, be found late, and be paid by whoever next touches this file. Recorded
#   here because the repair does not fix it; only changing what selects this test does.
#
#   MEASURED on `git archive HEAD` + an overlay of exactly this commit's 13 paths (the
#   HEAD+pathspec tree the gate actually lints), never the working tree — the 2026-08-09
#   episode-3 entry above is why, and the stale edit this pass discarded is why again:
#   it sat uncommitted for 8 days claiming I001 1367 / F401 276 / F541 26 against a tree
#   measuring 1380 / 277 / 28, numbers that were true of a working tree in 2026-08-18 and
#   of no tree since. A baseline measured on a shared dirty tree expires the moment
#   another lane commits or reverts.
#
#   THE 22, and what each actually was. Eight are real defects; one is a missing
#   annotation and is labelled as such rather than counted as a fix.
#     W291 3 + W293 2  tests/design/test_maturity_map_facets.py — trailing whitespace.
#     F841 5  tools/generate_dashboard_data.py — the five REPORTED_NOT_BLOCKING checks
#       whose results are deliberately unused (they run for their printed diagnosis).
#       Renamed to `_basis_ok` &c: the intent was already correct and documented above
#       them, so the name now SAYS deliberately-unused instead of ruff guessing.
#     E741 2  tools/lane_formation.py — `l` as a comprehension variable; it binds a lane
#       id, so it is now `lane`.
#     F541 1  site/test_the_site_lane_runs_no_untracked_control.py — placeholder-less f.
#     E401 1  tests/background/test_reconcile_watch.py — `import ast, inspect` split.
#     I001 7  seven clean files `--fix`ed one at a time, this ratchet's own stated
#       remedy. NOT a repo-wide `--fix`: 1373 files offend and the tree has concurrent
#       writers, so a sweep would rewrite hundreds of files belonging to other lanes.
#     E402 1  background/health_check.py:34 — the ONE that is an annotation, not a fix.
#       Both imports there must follow `sys.path.insert`; line 23 already carries
#       `# noqa: E402` saying so and line 34 did not. Making the file consistent
#       suppresses nothing line 23 was not already suppressing, but it is a notation
#       change and is not evidence that a defect was removed.
#
#   ONE AUTO-FIX HAD TO BE UNDONE BY HAND, and it is the reason `--fix` is not trusted
#   blind here. On `background/notify.py` ruff's isort split a single
#   `from background.alarm_repetition import (...)  # noqa: E402` into TWO statements and
#   carried the `noqa` onto only one of them — clearing one I001 and MINTING a fresh
#   E402, so the census came back with E402 still one over. Rewritten by hand as one
#   sorted block keeping the noqa. An import-sorter that can move a `noqa` off the line
#   it was written for can convert one violation into another, which no total will show
#   you: it was caught because the per-code census was set-differenced against HEAD's,
#   not because the sum looked wrong.
#
#   F401 277 is NOT this pass's doing — it was already one BELOW the floor at pristine
#   HEAD, i.e. someone deleted an unused import without lowering the baseline. Shrunk
#   here per the shrink-only rule, which is the whole point of the stale-entry check.
#   2026-08-26  I001 1373 -> 1362, F401 277 -> 273, E402 176 -> 174, E401 21 -> 20
#     THE RATCHET CAUGHT THE MAP SPLIT, which is the first time it has caught anything it was
#     not pointed at, and it is worth recording as evidence that it works rather than as a
#     chore. The harness-lane prune inserted `from tools import maturity_map_store as map_store`
#     into 47 modules by hand; the resulting tree came in at I001 1398 (+25), F401 291 (+14) and
#     E402 179 (+3) against this baseline, and the landing was REFUSED. Fixed at source per this
#     ratchet's stated remedy -- `ruff --select I001,F401 --fix` on exactly the landed pathspec,
#     then six `# noqa: E402` annotations where the store import must follow a `sys.path.insert`
#     -- and never by raising a count.
#
#     TWO DEAD PROBES DELETED RATHER THAN ANNOTATED, and the distinction matters because a
#     `noqa` on genuinely dead code is debt wearing a permit. `background/health_check.py` and
#     `tools/discovery_pass_ceiling.py` each opened with `try: import yaml / except ImportError`
#     guarding a parse that the store now performs. The store imports yaml at MODULE scope, so a
#     missing yaml fails those modules' own imports long before either probe is reached: the
#     branches were unreachable, no test asserted them, and they are gone with the parse they
#     guarded.
#
#     THE 08-06 WARNING ABOUT `--fix` FIRED AGAIN, EXACTLY AS WRITTEN. On
#     `background/supervisor.py` ruff's isort split a single
#     `from background.coupled_triad import (...)  # noqa: E402` into two statements and carried
#     the `noqa` onto only one of them, minting a fresh E402 while clearing an I001. Restored by
#     hand. It was caught the way that entry says to catch it: the per-file, per-code census of
#     the RESULTING TREE was set-differenced against a `git archive HEAD` extraction, and that
#     diff contains ONLY removals -- 18 of them, in 13 files, summing exactly to 2378 -> 2360.
#     No total would have shown this; the sum was going down either way.
#
#     The floor therefore drops on four codes at once. Every one of the 18 is a real violation
#     removed from a real file, and 7 of them (gate_authorization F401 x2, health_check I001 x2,
#     naive_organ F401, process_run_complete I001, moap_stage F401) were PRE-EXISTING debt the
#     same `--fix` pass cleared incidentally -- shrink-only, so they are recorded here rather
#     than left as stale entries, which is the failure the 08-09 episode-3 entry above wedged
#     the publish gate on.
#   2026-08-26  I001 1362 -> 1360  (the value cycle's wiring, sideways)
#     Landing `renewal_margin_arm` touched three files in `company/pricing/` and
#     `company/policy/`, and `ruff --select I001 --fix` on exactly those cleared two blocks that
#     were ALREADY dirty before this change went near them -- `decision_policy.py` and
#     `value_based_renewal.py`, one each. Nothing was minted: the per-file per-code census of
#     the resulting tree, set-differenced against a `git archive HEAD` extraction, is two
#     removals and NOT ONE addition. A drop caused sideways is still a drop, so the floor
#     shrinks rather than being left stale -- which is the exact failure the 08-09 episode-3
#     entry above wedged the publish gate on for hours, and the failure this commit's own first
#     gate run reproduced in ninety seconds.
#   2026-08-26  I001 1360 -> 1357, F401 273 -> 272, F541 27 -> 25  (landing eleven written-but-
#               never-committed test files)
#     The ratchet fired UPWARD first, which is the direction that matters: four of the eleven
#     carried an un-sorted import block and I001 went 1360 -> 1361 on the resulting tree. Fixed
#     at source with `ruff --select I001,F401 --fix` over exactly the landed pathspec, per this
#     ratchet's stated remedy, and the same pass cleared three MORE that were already there --
#     plus two F541 that HEAD's copy of `tools/revenue_sanity_check.py` carried and the working
#     tree's did not. Net six down, and the per-file per-code census of the resulting tree
#     set-differenced against `git archive HEAD` is removals only, no additions.
#   2026-08-26  I001 1357 -> 1356  (the worker-test isolation repair, sideways again)
#     `tests/background/test_background_worker.py` carried one already-dirty import block, and
#     `ruff --select I001 --fix` over the single file being landed cleared it. THIS IS THE THIRD
#     SHRINK TODAY and the pattern is worth naming rather than repeating silently: every commit
#     that touches a file carrying pre-existing I001 debt clears it as a side effect of the
#     ratchet's own remedy, and then reds on the stale floor it just created. That is the design
#     working -- a floor nobody shrinks stops measuring -- but it means the cost of this ratchet
#     is one extra gate cycle per commit that lands a dirty file, and the way out is paying the
#     1,356 down rather than tuning the control.
#   2026-08-26  I001 1356 -> 1355, F401 272 -> 269  (bringing six writers inside the live-ledger
#               guard)
#     Sideways again, and by now the pattern is the entry: routing
#     `seat_continuity`, `seat_work_in_hand` and `sim_runner` through
#     `guard_live_ledger_write` meant running the fix pass over them, which cleared three unused
#     imports and one un-sorted block that were all there before the change went near them. Per
#     file, set-differenced against `git archive HEAD`: seat_continuity F401 -2,
#     seat_work_in_hand F401 -1, sim_runner I001 -1. Four removals, no additions.
# --------------------------------------------------------------------------
RUFF_BASELINE: dict[str, int] = {
    "I001": 1355,
    "F401": 269,
    "E402": 174,
    "F841": 127,
    "E741": 108,
    "F811": 95,
    "E702": 76,
    "E701": 45,
    "F541": 25,
    "E401": 20,
    "E731": 19,
    "W293": 19,
    "E722": 5,
    "W291": 3,
    "W292": 2,
    "E713": 1,
    "F601": 1,
    "W605": 1,
    "invalid-syntax": 1,
}
RUFF_BASELINE_TOTAL = 2346  # was 2347; -1 (F841; see the 2026-08-26 shrink-log entry)


# --------------------------------------------------------------------------
# Generic ratchet arithmetic — exercised by the R15 mutation tests. Pure
# functions over {key: count} maps, kept key-agnostic so a second ratchet can
# reuse them unchanged.
# --------------------------------------------------------------------------

def keys_exceeding_baseline(
    baseline: dict[str, int], counts: dict[str, int]
) -> dict[str, tuple[int, int]]:
    """Baseline keys whose CURRENT count is above the frozen count (regression).

    Returns {key: (baseline_count, current_count)}.
    """
    return {
        k: (baseline[k], counts.get(k, 0))
        for k in baseline
        if counts.get(k, 0) > baseline[k]
    }


def new_keys(baseline: dict[str, int], counts: dict[str, int]) -> dict[str, int]:
    """Keys present now (count > 0) but ABSENT from the baseline.

    For ruff these are unknown new rule codes; for mypy they are new files that
    must be type-clean. Returns {key: current_count}.
    """
    return {k: v for k, v in counts.items() if v > 0 and k not in baseline}


def stale_keys(
    baseline: dict[str, int], counts: dict[str, int]
) -> dict[str, tuple[int, int]]:
    """Baseline keys whose CURRENT count is below the frozen count (stale).

    The debt was paid down but the baseline was not shrunk to match. Returns
    {key: (baseline_count, current_count)}; forces the ratchet to only shrink.
    """
    return {
        k: (baseline[k], counts.get(k, 0))
        for k in baseline
        if counts.get(k, 0) < baseline[k]
    }


def _merge(baseline: dict[str, int], delta: dict[str, int]) -> dict[str, int]:
    """baseline + delta, additively (used to simulate a landed violation)."""
    merged = dict(baseline)
    for k, v in delta.items():
        merged[k] = merged.get(k, 0) + v
    return merged


# --------------------------------------------------------------------------
# Makefile scope derivation — the ruff ratchet checks EXACTLY what `make check`
# lints. We read (never modify) the Makefile so the two cannot drift silently.
# --------------------------------------------------------------------------

def makefile_lint_scope() -> list[str]:
    """Positional paths passed to `ruff check` in the Makefile `lint:` target.

    Reads the recipe of the `lint:` target and extracts the arguments to
    `ruff check` that are not flags. Today that is exactly `.` (whole repo).
    """
    lines = MAKEFILE.read_text(encoding="utf-8").splitlines()
    recipe: list[str] = []
    in_lint = False
    for line in lines:
        if re.match(r"^lint:", line):
            in_lint = True
            continue
        if in_lint:
            if line.startswith("\t"):
                recipe.append(line.strip())
            else:
                break  # a blank line or the next target ends the recipe
    for cmd in recipe:
        m = re.match(r"ruff\s+check\s+(.*)$", cmd)
        if m:
            return [a for a in m.group(1).split() if not a.startswith("-")]
    raise AssertionError("could not find a `ruff check` command in Makefile lint target")


# --------------------------------------------------------------------------
# Running the tools programmatically.
# --------------------------------------------------------------------------

def _installed_version(dist: str) -> str:
    return metadata.version(dist)


def ruff_counts_for(paths: list[str], cwd: Path, extra_args: list[str] | None = None) -> dict[str, int]:
    """Run `ruff check <paths> --output-format=json` and count findings by code.

    Parameterised by cwd + paths so the R15 tmp-tree fixture can point it at a
    synthetic tree. Exit code 1 (findings present) is expected and fine; any
    other non-zero code is a real invocation error and raises.
    """
    cmd = [sys.executable, "-m", "ruff", "check", *paths, "--output-format=json"]
    if extra_args:
        cmd += extra_args
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(
            f"ruff invocation failed (exit {proc.returncode}):\n{proc.stderr}"
        )
    counts: dict[str, int] = {}
    for item in json.loads(proc.stdout or "[]"):
        # This pinned ruff emits code='invalid-syntax' for syntax errors; guard
        # a null code for forward-safety by mapping it to the same bucket.
        code = item.get("code") or "invalid-syntax"
        counts[code] = counts.get(code, 0) + 1
    return counts


@lru_cache(maxsize=1)
def real_ruff_counts() -> dict[str, int]:
    return ruff_counts_for(makefile_lint_scope(), REPO_ROOT)


def _fmt_exceed(d: dict[str, tuple[int, int]]) -> str:
    return "\n".join(
        f"    {k}: baseline {b}, now {c}" for k, (b, c) in sorted(d.items())
    )


def _fmt_new(d: dict[str, int]) -> str:
    return "\n".join(f"    {k}: now {c}" for k, c in sorted(d.items()))


# ==========================================================================
# Version pins — the baselines are only valid for these exact versions.
# ==========================================================================

def requirements_ruff_pin() -> str | None:
    """The ruff version pinned in requirements.txt, or None if unpinned/absent.

    An INDEPENDENT source for the pin below (the declared dependency) versus
    what is actually installed — so the cross-check in the test is not a
    tautology reading one source twice.
    """
    if not REQUIREMENTS.is_file():
        return None
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*ruff\s*==\s*([^\s#]+)", line)
        if m:
            return m.group(1)
    return None


def test_tool_versions_are_pinned():
    """The installed ruff must match the version the baseline was frozen under.

    A version drift silently invalidates every count below, so it fails LOUDLY
    with the one-line fix. Checked against BOTH the installed distribution and
    the declared dependency in requirements.txt: the earlier form of this test
    also asserted a mypy pin naming a version that was never installed here,
    which made it unpassable and wedged the publish gate (2026-08-08 — see the
    module docstring). Two independent sources catch that, and catch a
    requirements bump that would silently invalidate the frozen baseline.
    """
    ruff_v = _installed_version("ruff")
    assert ruff_v == RUFF_PIN, (
        f"ruff {ruff_v} installed but the baseline is frozen for {RUFF_PIN}. "
        f"FIX: `pip install ruff=={RUFF_PIN}` to reproduce, OR upgrade the pin "
        f"AND re-freeze RUFF_BASELINE in the SAME PR (a baseline is per-version)."
    )
    declared = requirements_ruff_pin()
    assert declared == RUFF_PIN, (
        f"requirements.txt pins ruff=={declared} but RUFF_BASELINE is frozen "
        f"for {RUFF_PIN}. A dependency bump invalidates the frozen counts: "
        f"re-freeze RUFF_BASELINE in the SAME PR as the bump, or correct the pin."
    )


def test_ruff_scope_is_the_make_check_scope():
    """The ratchet lints exactly what `make check` lints (today: the whole repo)."""
    scope = makefile_lint_scope()
    assert scope == ["."], (
        f"Makefile `lint:` scope changed to {scope!r}; the ruff baseline was "
        f"frozen over `ruff check .`. Re-derive and re-freeze RUFF_BASELINE."
    )


# ==========================================================================
# RUFF RATCHET — regression / new-code / stale, on today's tree.
# ==========================================================================

def test_ruff_no_rule_exceeds_baseline():
    """No known rule code may exceed its frozen count (a regression)."""
    exceed = keys_exceeding_baseline(RUFF_BASELINE, real_ruff_counts())
    assert not exceed, (
        "NEW ruff violations pushed a rule code ABOVE its dated baseline "
        f"(frozen {BASELINE_DATE}). Fix the new violations — do not raise the "
        "baseline:\n" + _fmt_exceed(exceed)
    )


def test_ruff_no_unknown_new_rule_codes():
    """A rule code absent from the baseline must be at 0 (no new sin class)."""
    new = new_keys(RUFF_BASELINE, real_ruff_counts())
    assert not new, (
        "NEW ruff rule code(s) not present in the dated baseline appeared. Fix "
        "the violations; add a code here only as a deliberate, reviewed "
        "grandfathering (it should shrink, not grow):\n" + _fmt_new(new)
    )


def test_ruff_no_stale_baseline_entries():
    """A baseline code whose count fell must be shrunk (shrink-only ratchet)."""
    stale = stale_keys(RUFF_BASELINE, real_ruff_counts())
    assert not stale, (
        "STALE ruff baseline entries — these codes have FEWER violations than "
        "frozen. Good news, but you must LOWER (or delete) their baseline counts "
        "so the ratchet holds the new floor:\n" + _fmt_exceed(stale)
    )


def test_ruff_baseline_matches_frozen_census():
    """On today's tree the ruff counts equal the frozen baseline exactly."""
    counts = real_ruff_counts()
    assert counts == RUFF_BASELINE, (
        "ruff census drifted from the frozen baseline. Diff:\n"
        f"  only-now : { {k: counts[k] for k in counts.keys() - RUFF_BASELINE.keys()} }\n"
        f"  only-base: { {k: RUFF_BASELINE[k] for k in RUFF_BASELINE.keys() - counts.keys()} }\n"
        f"  changed  : { {k: (RUFF_BASELINE[k], counts[k]) for k in RUFF_BASELINE.keys() & counts.keys() if RUFF_BASELINE[k] != counts[k]} }"
    )
    assert sum(counts.values()) == RUFF_BASELINE_TOTAL


# ==========================================================================
# R15 MUTATION PROOFS — in-memory blast radius (a control must be able to FAIL).
#
# Each proof injects ONE synthetic delta and asserts it reds EXACTLY the
# intended check and NOTHING else — not the sibling checks, not the other
# ratchet. Without these, a check that always passes would look identical to
# one that works.
# ==========================================================================

# --- ruff: a brand-new rule code lands ---
def test_mutation_ruff_new_code_reds_only_new_check():
    mutated = _merge(RUFF_BASELINE, {"B008": 1})  # B008 not in select -> never natural
    assert new_keys(RUFF_BASELINE, mutated) == {"B008": 1}
    assert not keys_exceeding_baseline(RUFF_BASELINE, mutated)  # existing codes untouched
    assert not stale_keys(RUFF_BASELINE, mutated)               # adding never staleifies


# --- ruff: an existing code regresses above baseline ---
def test_mutation_ruff_regression_reds_only_exceeds_check():
    # The mutation is stated RELATIVE to the baseline, not against a copied
    # literal: a shrink (see the shrink log) must not be able to silently
    # invalidate the proof, and a pinned number here would do exactly that.
    f401 = RUFF_BASELINE["F401"]
    mutated = _merge(RUFF_BASELINE, {"F401": 1})  # one new unused import
    assert keys_exceeding_baseline(RUFF_BASELINE, mutated) == {"F401": (f401, f401 + 1)}
    assert not new_keys(RUFF_BASELINE, mutated)
    assert not stale_keys(RUFF_BASELINE, mutated)


# --- ruff: a fixed code leaves a stale (un-shrunk) baseline entry ---
def test_mutation_ruff_stale_reds_only_stale_check():
    f401 = RUFF_BASELINE["F401"]
    mutated = dict(RUFF_BASELINE)
    mutated["F401"] = f401 - 1  # one unused import removed but baseline not shrunk
    assert stale_keys(RUFF_BASELINE, mutated) == {"F401": (f401, f401 - 1)}
    assert not keys_exceeding_baseline(RUFF_BASELINE, mutated)
    assert not new_keys(RUFF_BASELINE, mutated)


# ==========================================================================
# R15 MUTATION PROOFS — on-disk (close the fail-open gap where the parser is
# correct but the TOOL never actually produced the finding). A synthetic
# violation is written to a tmp tree and run through the REAL tool; the parsed
# result must red EXACTLY the new-violation assertion and nothing else.
# ==========================================================================

def test_mutation_ruff_ondisk_violation_is_detected_and_reds_only_new_violation(tmp_path):
    """A real unused import in a tmp file -> ruff -> F401 -> reds only the
    regression assertion (F401 is a baselined code), never stale/new."""
    (tmp_path / "rogue.py").write_text("import os\n")  # unused import -> F401
    tmp_counts = ruff_counts_for(["rogue.py"], tmp_path)
    # 1) The real ruff CLI + our JSON parser actually surfaced the violation.
    assert tmp_counts.get("F401", 0) >= 1, (
        f"expected ruff to flag F401 on disk; got {tmp_counts}"
    )
    assert set(tmp_counts) == {"F401"}, f"tmp file should yield only F401, got {tmp_counts}"
    # 2) Landed on the real tree, it reds EXACTLY the exceeds-baseline check.
    mutated = _merge(RUFF_BASELINE, tmp_counts)
    f401 = RUFF_BASELINE["F401"]
    assert keys_exceeding_baseline(RUFF_BASELINE, mutated) == {
        "F401": (f401, f401 + tmp_counts["F401"])
    }
    assert not new_keys(RUFF_BASELINE, mutated)
    assert not stale_keys(RUFF_BASELINE, mutated)


# ==========================================================================
# R15 MUTATION PROOF — the requirements.txt cross-check must be able to FAIL.
#
# Added with the check itself (2026-08-08). The control it replaces was a pin
# assertion that could only ever fail (it named an uninstalled tool), so this
# one is proven to swing BOTH ways: it reds on a real divergence, and it does
# not fail-open on a missing or unpinned requirements file.
# ==========================================================================

def test_mutation_requirements_pin_drift_reds_the_cross_check(tmp_path, monkeypatch):
    """A requirements.txt bump that diverges from RUFF_PIN is DETECTED."""
    module = sys.modules[__name__]
    bumped = tmp_path / "requirements.txt"
    bumped.write_text("pytest==8.0.0\nruff==9.9.9  # bumped\nnumpy==2.0.0\n", encoding="utf-8")
    monkeypatch.setattr(module, "REQUIREMENTS", bumped)
    assert requirements_ruff_pin() == "9.9.9"
    assert requirements_ruff_pin() != RUFF_PIN  # -> the assertion in the pin test reds


def test_requirements_cross_check_does_not_fail_open(tmp_path, monkeypatch):
    """FAIL-OPEN guard (R15): a missing or ruff-less requirements.txt must NOT
    read as agreement. It returns None, which is != RUFF_PIN, so the pin test
    reds rather than silently passing on absent evidence."""
    module = sys.modules[__name__]
    monkeypatch.setattr(module, "REQUIREMENTS", tmp_path / "does_not_exist.txt")
    assert requirements_ruff_pin() is None != RUFF_PIN

    unpinned = tmp_path / "requirements.txt"
    unpinned.write_text("pytest==8.0.0\nruff\n", encoding="utf-8")  # present but unpinned
    monkeypatch.setattr(module, "REQUIREMENTS", unpinned)
    assert requirements_ruff_pin() is None


def test_requirements_cross_check_reads_the_real_file():
    """Independence: on the real tree the two sources genuinely AGREE (so the
    passing cross-check above is evidence, not a fixture artefact)."""
    assert requirements_ruff_pin() == RUFF_PIN == _installed_version("ruff")
