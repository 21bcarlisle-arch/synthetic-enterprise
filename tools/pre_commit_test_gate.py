"""Pre-commit TEST GATE (director P0, 2026-07-17): a commit with red tests is STRUCTURALLY
IMPOSSIBLE, not merely discouraged.

Why a mechanism, not a resolution: on 2026-07-17 two commits landed with red tests because the
process was "run tests, then commit" -- a remembered discipline, and remembered disciplines are
exactly what failed (twice). The same principle as everything else in the operational rebuild:
structural impossibility over remembered care (reaper deleted -> exit-143 impossible; this gate ->
red-commit impossible). It matters MOST right now because parallel-safety controls (the gate-wall,
the reconcilers) are being built with an autonomously-committing loop: if red commits are possible,
a subtly-broken safety control could land looking green in the log.

What runs (fast, so the loop's cadence is not taxed):
  - the SAFETY-CONTROL set ALWAYS, whenever any CODE/config file is staged -- these protect the
    controls even when an unrelated dependency (e.g. background/notify.py, which every alarm routes
    through) changes.
  - the test file for each changed source file (background/X.py -> tests/**/test_X.py; a changed
    test file -> itself).
A pure docs/site/data commit (no code/config staged) runs nothing -- it cannot break a control.
Any failure -> exit 1 -> the commit is ABORTED. The only bypass is git's own --no-verify, which
this repo's own one_way_door.py flags as a dangerous pattern; none of our committers use it.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Always run when code/config changes -- the controls the director is protecting tonight.
CONTROL_TESTS = [
    "tests/background/test_gate_authorization.py",
    "tests/background/test_fork_reconciler.py",
    "tests/background/test_transport_failure_loud.py",
    "tests/background/test_deadmans_switch.py",
    "tests/background/test_status_honesty.py",
    "tests/hooks/test_pull_next_work.py",
    # R10 class closure for W2_sme_segment_case_normalisation (2026-08-08). Its
    # own `test_the_real_simulation_tree_is_clean` scans EVERY file under
    # simulation/ for a non-canonical segment literal, so it has to run on any
    # code change -- not only when the guard itself is edited. Per-file test
    # selection would fire the guard when `tools/segment_case_guard.py` changes
    # and stay silent when someone adds `segment == "sme"` to a brand-new sim
    # module, which is the case the guard exists to catch. ~0.2s.
    "tests/tools/test_segment_case_guard.py",
    # R10 class closure for H30_sim_runner_discards_child_stderr (2026-08-08).
    # Same reasoning, different class: `test_the_live_background_tree_is_clean`
    # scans EVERY file under background/ for a daemon that reports a child's
    # failure while discarding its stderr. Per-file selection would fire when
    # `tools/child_stderr_guard.py` is edited and stay silent when a brand-new
    # daemon lands with an uncaptured launch -- which is the only case that
    # matters. It also fails rc=2 if a declared daemon moves outside the
    # scanned root, so this is where a coverage hole surfaces. ~0.3s.
    "tests/tools/test_child_stderr_guard.py",
    # R10 class closure for WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF
    # (2026-08-14, BLOCKING). Same reasoning as the two guards above, third class:
    # `test_the_real_tree_carries_exactly_one_series` AST-walks EVERY file under company/ and
    # saas/ for a second annual grid-intensity series. Per-file selection would fire it when
    # `tools/grid_intensity_guard.py` is edited -- the case that needs it least -- and stay
    # silent when a brand-new reporting module declares its own intensity table, which is the
    # only case it exists for. That silence is not hypothetical: the published series lived as a
    # LOCAL inside `annual_report._section_carbon_emissions` and disagreed with the two other
    # live series by up to 55.6% for an unknown length of time, with nothing able to see it.
    # ~0.6s.
    "tests/tools/test_grid_intensity_guard.py",
    # R10 class closure for WORKER_FINDING_A_NULL_CLV_ENTERS_THE_PUBLISHED_MEDIAN_AS_THE_NUMBER_
    # ZERO (2026-08-18, BLOCKING). Fourth class, same reasoning as the three guards above:
    # `test_the_real_tree_is_clean` AST-walks EVERY file under company/, saas/, sim/, simulation/,
    # tools/, background/ and interface/ for a deliberately-null field given a numeric fallback at
    # its read site. Per-file selection would fire it when `tools/structural_blank_guard.py` is
    # edited -- the case that needs it least -- and stay silent when a brand-new reporting module
    # writes `v.get("clv_gbp") or 0.0`, which is the only case it exists for. Measured, not
    # asserted: BOTH shipped instances were in modules (`saas/reporting/annual_report.py` --
    # live and wrong; `tools/generate_shadow_html.py` -- latent, empty triggering population)
    # whose own stem-selected tests do not run this guard.
    #
    # What the silence cost: 5 of 13 accounts entered a published MEDIAN as manufactured zeros,
    # that median is a quadrant BOUNDARY, and two accounts reached a board recommendation for
    # "immediate retention offers" purely because of it. The repair moved the published line from
    # 5 CRITICAL accounts to 1. The shape never raises, so nothing else in the tree could see it.
    # ~3.8s, the second most expensive entry here and stated rather than glossed: it is an AST
    # walk of seven packages.
    "tests/tools/test_structural_blank_guard.py",
    # AO8 (2026-08-08). A mechanised battery line rots when work ELSEWHERE
    # renames or deletes the check it names. Per-file selection would fire this
    # when the register is edited (needs it least) and stay silent then (the
    # case it exists for). Also catches a stale status block. ~0.3s.
    "tests/domain/test_battery_register_integrity.py",
    # THE EPISTEMIC WALL (KNIFE pass 3 step 12, 2026-08-10). Same R10 shape as the
    # three above, on the one control CLAUDE.md classes as a WALL rather than a dial:
    # `test_no_new_sim_reads_company` walks EVERY file under company/, saas/, sim/ and
    # simulation/, so it has to run on any code change. Per-file selection fired it when
    # the ratchet itself was edited -- the case that needs it least -- and stayed silent
    # when a brand-new sim module landed importing `saas.*`, which is the only case it
    # exists for. Until now the wall was enforced only by the post-commit publish gate,
    # so a crossing could LAND and be found hours later; `WORKER_FINDING_THE_EPISTEMIC_
    # WALL_IS_BREACHED_AT_HEAD_2026-08-09` is what that costs. ~4.8s, by far the most
    # expensive entry in this list and stated rather than glossed: it is an AST walk of
    # four packages, and it is paid on every code commit deliberately.
    "tests/architecture/test_epistemic_wall_ratchet.py",
]

# A staged path under any of these = a code/config change that could break a control or its own
# tests -> run the gate. Anything else (docs/status, docs/reports, site/data, observability) is
# pure data and cannot break a control -> skip (keep the loop's commit cadence fast).
# NOT `site/**/*.html`, though it once counted as "pure data" here: a PAGE can break a control
# (the reachability one), so it gets its own surface trigger -- see SITE_SURFACE_PREFIX below.
CODE_PREFIXES = (
    "background/", ".claude/", "tests/", "tools/",
    "saas/", "company/", "sim/", "simulation/", "interface/",
)

# THE LEVEL SURFACE (director P0, 2026-07-21): these two files ARE data, but a change to either is
# a level/ledger claim whose downstream effects MUST be validated at COMMIT time, not left to the
# full publish suite. Twice on 2026-07-21 a maturity-map change reached the publish gate red: the
# morning's unbacked self-promotion, and a LEGITIMATE ledger-backed W1_5 L1->L3 ratification that
# flipped a level-dependent count in a proof test. Neither is under CODE_PREFIXES, so the test-gate
# skipped both as "pure data". A change here now runs the LEVEL-SENSITIVE tests -- the reconciler
# (the self-promotion guard), the level gate itself, the coupled-triad gate, and the proof panel
# whose counts derive from live map levels. Director's ask made mechanism: a level-quality claim's
# effect is caught at commit time.
LEVEL_SURFACE_FILES = (
    "docs/design/maturity_map.yaml",
    "docs/observability/gate_authorizations.jsonl",
)
# The map/store contract, named once and shared by both surfaces that can break it (the map
# below, and the store files themselves via STORE_SURFACE_PREFIX).
STORE_CONTRACT_TESTS = [
    "tests/design/test_atom_notes_store.py",
    "tests/design/test_atom_records_store.py",
    # THE SIZE HALF OF THE SAME CONTRACT (2026-08-14). The two entries above were added
    # 2026-08-10 for exactly this class and the third file was left out, so the map's own
    # SIZE RATCHET and its `simplifications_count` check stayed unreachable from a map edit.
    # Measured that day with `select_targets` called directly: a `docs/design/maturity_map.yaml`
    # edit selected 7 targets and this file was not among them, and neither was it reachable
    # from `docs/design/simplifications/<atom>.yaml` -- so BOTH controls could only be selected
    # by editing their own implementation or themselves. EVERY EDIT THAT CAN BREAK THEM WAS AN
    # EDIT THAT COULD NOT SELECT THEM. Consequence observed, not predicted: HEAD sat 495 B over
    # the ratchet with two atoms declaring counts their store files contradicted, and a commit
    # EDITING THE MAP landed through `surgical_land` at gate-rc 0 on top of it.
    #
    # This is R15's FAIL-SILENT shape at the SELECTION layer rather than inside the assertion --
    # the control bodies were fine and fired correctly the moment anything ran them. A data file
    # has no implementation stem for a name-stem selector to match, which is why this class is
    # PERMANENT for data-file subjects rather than transient as it is for a moved module.
    # Mutation-proven from the DATA side (tests/tools/test_pre_commit_test_gate_selection.py):
    # one byte over the ratchet, added to the map, must RED at the commit.
    "tests/design/test_simplifications_store.py",
]
LEVEL_SENSITIVE_TESTS = [
    # tests/background/test_fronts_reconciler.py removed 2026-08-03 with the module itself (the
    # fronts/BUILD-open scope-permission machinery -- see the deletion note in supervisor.py).
    "tests/background/test_gate_authorization.py",
    "tests/tools/test_level_promotion_gate.py",
    "tests/tools/test_generate_proof_coupled_gaps.py",
    "tests/test_coupled_triad_gate.py",
    # R10 class fix (2026-07-23, DIRECTOR_RULING_UNWEDGE_AND_AXIS3 item 1): the level-surface gate
    # ran the level/ledger/reconciler tests on a maturity_map.yaml edit but NOT the map-HYGIENE
    # facets (value_stream hygiene C3, coupling topology C5). So the F1c registration (an atom given
    # value_stream=close_to_learn but never added to the reviewed allowlist) passed at commit time
    # and only the full publish gate caught it -> wedge. Registration-time facet violations are now
    # caught at commit, making the whole class (not just this instance) structurally uncommittable.
    "tests/design/test_maturity_map_facets.py",
    # Same R10 shape, one surface further out (2026-08-10, the fourteenth publish wedge). A MINT
    # copies `records_rehomed`/`notes_rehomed` into the new map entry from a template while the
    # store file docs/design/simplifications/<id>.yaml is never written -- the declaration says
    # "the store holds this" of a file that does not exist. The two store-contract tests below
    # fire on exactly that, but neither was reachable from a maturity_map.yaml change, so three
    # successive mints (A9, AO12, D23, H42) each landed red on committed HEAD and were found
    # hours later by the publish gate. It recurs at MINT RATE, which is why the fix is the DRAIN
    # (unmintable at commit time) and not the two map lines the instance needed.
    *STORE_CONTRACT_TESTS,
]

# THE PER-ATOM STORE SURFACE (2026-08-10, the other direction of the same contract). The store
# files are data by every prefix rule here, but the map DECLARES their contents, so removing or
# renaming one silently falsifies a declaration that lives in a file this commit never touched.
# Both directions of `check_declarations_match` therefore need both sides of the surface.
STORE_SURFACE_PREFIX = "docs/design/simplifications/"

# THE PUBLISHED SURFACE (2026-08-12, DIRECTOR_OBSERVATION_PUBLISHED_SURFACE_NAV_AND_STAMPS
# item 1). Fifth sibling of LEVEL_SURFACE / MINT_MARKER / CANON_SURFACE / STORE_SURFACE, and
# the clearest case of the shape yet: `site/` is deliberately NOT in CODE_PREFIXES ("site/data
# ... is pure data and cannot break a control"), which was true when the only thing under it
# was rendered data. It is not true of the pages. A new `site/**/*.html` with no route in is a
# page published to nobody, and the commit that adds it touches no `.py` at all -- so the gate
# skipped it as a pure docs commit, `tests_for()` mapped an `.html` to zero tests, and the
# defect was found by the DIRECTOR reading the live site, which is the failure mode his
# observation asks to end ("rather than be found by the director looking at the site").
#
# WHOLE-TREE, hence a surface trigger rather than per-file selection -- the same reasoning
# CONTROL_TESTS records for test_segment_case_guard: the control scans every page for one with
# no route in, so it must run when a page is ADDED, not only when the checker itself is edited.
# Per-file selection would fire on tools/site_reachability.py and stay silent on the exact
# commit that strands a section. ~0.15s (no subprocess, no network; it reads 35 files).
SITE_SURFACE_PREFIX = "site/"
SITE_SURFACE_TESTS = [
    "tests/tools/test_site_reachability.py",
]

# THE DATA SURFACE (2026-08-12), discharging
# WORKER_FINDING_THE_PRE_COMMIT_GATE_MAPS_NO_TESTS_TO_A_DATA_FILE_2026-08-09.md.
#
# The five surfaces above are HAND-KEPT LISTS, and every one of them was written after its own
# incident: a level claim, a mint marker, the canon, the per-atom store, a stranded page. That is
# the accretion pattern OPERATIONAL_COHERENCE_DESIGN_PASS names, and it only ever covers the data
# files something has already gone wrong about. The general defect underneath them is one line in
# `tests_for()`: a changed non-`.py` file selected NO tests at all, because coverage was derived
# from a FILENAME SUFFIX rather than from "what does this file actually affect".
#
# The instance that filed it: `background/process_manifest.yaml` calls itself "the SINGLE
# authoritative manifest of what SHOULD be running" and `tests/background/test_process_reconciler.py`
# asserts exact sets computed from it -- yet a manifest edit selected that test zero times, passed
# this gate, and wedged the publish gate on the very next cycle (2026-08-09, 12:22 UTC).
#
# WHAT IS DERIVED, NOT LISTED: the repo is asked which of its own `.py` files NAME the staged path
# (by repo-relative path, or by basename for the `_HERE / "x.yaml"` construction that is how such a
# path is usually written). A test that names it is selected directly; a module that names it
# selects that module's tests through the same convention map every other `.py` change uses. So a
# data file NOBODY has yet had an incident about is covered on the same footing as the five above.
#
# NOT `select_impacted_tests` outright, though the finding proposes it and its policy is the right
# one: its answer for an unmappable path is the FULL SUITE, and its import-graph answer for one
# module here is 53 test files / 2.6s to build. Both are correct for a fork's inner loop and
# unaffordable on every commit -- a gate too expensive to run gets bypassed, which is the fail-open
# it was meant to close. This takes that tool's DOCTRINE (cannot prove impact -> do not stay silent)
# at the cost the commit path can actually pay: ~0.1s of `git grep`, and zero when the staged data
# file is one no module reads.
DATA_SURFACE_SUFFIXES = (
    ".yaml", ".yml", ".json", ".jsonl", ".toml", ".ini", ".cfg", ".csv", ".txt", ".md", ".sh",
)

# THE PUBLISHER'S OWN OUTPUTS -- the one narrowing, stated with the number that forced it rather
# than glossed as "for speed". These roots hold artefacts the repo REGENERATES: their content is
# an effect of running the publisher, not a declaration the publisher reads. They are also read
# very widely, so the derivation above answers them with 14-30 test files: measured, a staged
# `site/data/dashboard.json` selects 29 files / 583 tests / **111 seconds**, on the single most
# frequent commit in the loop (every auto-process publish). This gate's whole premise is that it
# is cheap enough to never be worth bypassing -- a two-minute pre-commit gate is a gate someone
# reaches for `--no-verify` against, which CLAUDE.md classes as a WALL, so the expensive-and-
# correct version would buy a fail-open worse than the one it closes.
#
# ACCEPTED AS A RECORDED LIMITATION (clause 2), not as a repair, and it is bounded rather than
# open: each excluded root is the SUBJECT of a different named gate that does run on it --
# `site/**` has `tools/site_lane_gate.py` plus the SITE_SURFACE trigger above, and the published
# report/status artefacts are the publish gate's own subject at HEAD. What is genuinely NOT
# covered is a commit that lands a bad published artefact and is caught minutes later by the
# publish gate instead of instantly at commit time. `test_the_published_output_exclusion_is_
# bounded_by_another_gate` pins that claim so it reds if one of those gates stops covering it.
PUBLISHED_OUTPUT_ROOTS = ("site/", "docs/reports/", "docs/status/")

# THE SECOND NARROWING, and it is the same one (2026-08-13, the eighteen-hour publish freeze).
#
# WHAT HAPPENED. The derivation above landed at 21:40 on 2026-08-12. The last content publish
# reached origin at 21:28. Every auto-process publish from 22:29 onward died on `git commit`
# exceeding its 300s hook deadline, twenty-one consecutive times across eighteen hours, and the
# site served 08-12 figures while a `chore(liveness)` heartbeat kept landing on origin every
# thirty minutes. Nothing was red. The commit simply never finished.
#
# WHY THIS FILE. `background/process_run_complete.py::git_commit_push` stages
# `docs/design/maturity_map.yaml` on EVERY publish (the pre-gate atom_status inbox fold, `git
# add -A`). Measured on the real staged index: the map's derived answer alone is **50 test
# files**, taking the commit's selection to 58 files and **over twenty minutes** -- and it pulls
# in `tests/simulation/test_run_phase4c_on_phase2b.py`, a full simulation run that the publish
# gate's own argv explicitly `--ignore`s as too slow to gate on. The same commit narrowed to the
# map's CURATED list runs **13 files in 40 seconds**.
#
# So this is not a new policy. It is PUBLISHED_OUTPUT_ROOTS' own reasoning -- "a gate too
# expensive to run gets bypassed, which is the fail-open it was meant to close" -- applied to the
# second path that is staged on the single most frequent commit in the loop. The failure it
# actually bought was worse than a bypass, because nobody bypassed anything: the gate was never
# reached for a verdict, and an unfinished gate is indistinguishable in the log from a quiet one.
#
# BOUNDED THE SAME WAY, and this bound is stronger than the published-output one. Each path here
# is the SUBJECT of a hand-kept surface list above that fires on exactly this file and is not
# narrowed at all -- `docs/design/maturity_map.yaml` keeps every one of LEVEL_SENSITIVE_TESTS
# (the reconciler, the level gate, the coupled triad, the proof panel, the map facets, both store
# contracts), each of which was added after its own incident. What is dropped is the derived
# tail: the tests of the ~37 modules that merely READ the map. `test_a_curated_surface_path_
# keeps_its_curated_tests` and `test_every_curated_surface_narrowing_has_a_surface_list` pin both
# halves, so narrowing a path whose curated list was later deleted reds instead of going silent.
CURATED_SURFACE_PATHS = LEVEL_SURFACE_FILES


def staged_files() -> list[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=str(ROOT), capture_output=True, text=True,
    ).stdout
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def tests_for(path: str) -> list[str]:
    """Map a changed file to its test file(s): a changed test file -> itself; a changed *.py ->
    tests/**/test_<stem>.py AND tests/**/test_<stem>_*.py if present.

    THE SUFFIX HALF IS LOAD-BEARING, not tidiness (2026-08-09, the second publish wedge). This
    globbed the EXACT stem only, so a module whose tests live in a QUALIFIED file was mapped to
    zero tests and committed untested. `simulation/live_population.py` is covered solely by
    `tests/simulation/test_live_population_seam.py`; `tests_for()` returned `[]` for it, the
    pre-commit gate passed, and the wall-hygiene test in that very file then wedged the publish
    gate for ~112 minutes. Naming a test file after the ASPECT it covers is normal in this repo
    (`_seam`, `_event_log`, `_guards`), so the exact-stem glob was silently blind to a whole
    naming convention the repo actively uses.

    Same shape as the non-`.py` blind spot filed alongside it (a control whose SCOPE was derived
    from a convenient filename proxy rather than "what does this file actually affect"); this
    closes the `.py` half. The non-`.py` half is closed by `data_surface_tests()` below (2026-08-12)
    -- keep the two separate: this one answers "which tests are NAMED FOR this module", that one
    answers "which modules READ this file", and fusing them would make each unfalsifiable.
    """
    p = Path(path)
    if p.suffix != ".py":
        return []
    if p.name.startswith("test_") and (ROOT / p).exists():
        return [str(p)]
    matches = set(ROOT.glob(f"tests/**/test_{p.stem}.py"))
    matches |= set(ROOT.glob(f"tests/**/test_{p.stem}_*.py"))
    return sorted(str(c.relative_to(ROOT)) for c in matches)


# THE MINT-MARKER SURFACE (2026-07-28, atom `unstated_reason_block_impossible` §3): a
# PLANNER_MINTED_*.md parked in in_progress/ is pure DATA (not under CODE_PREFIXES), so a mint doc
# committed with a reason-less/unresolvable block marker would slip the gate exactly as a bad map
# level once did. Staging one now runs the mint-block-hygiene test (which scans the LIVE in_progress
# set), so a `blocked` mint carrying no resolvable `<!-- BLOCK_RELEASE: <releaser> -- <reason> -->`
# CANNOT be committed -- the sibling of the LEVEL_SURFACE mechanism, "cannot be written" not "flagged
# after" (§3). Narrow trigger (only a staged mint doc), so unrelated docs/data commits stay fast.
MINT_MARKER_PREFIX = "docs/staging/in_progress/PLANNER_MINTED_"
MINT_HYGIENE_TESTS = [
    "tests/background/test_staging_disposition.py",
]

# THE CANON SURFACE (2026-08-10, atom OPS5). CLAUDE.md and the design doc beside it are data by
# every prefix rule here, but they are the files that tell a seat what it may DO -- and one of the
# rules they now carry (hook-bypass is a WALL, and the one legal move that replaced the sanctioned
# interim bypass) is a rule about how commits themselves are made. Editing that text without
# re-running its guard is how the retirement would quietly un-happen: a wall deleted from CLAUDE.md,
# or the four-condition carve-out restated as live, would sail through as a "pure docs commit" and
# only surface in the publish suite, if at all. Third sibling of LEVEL_SURFACE / MINT_MARKER, same
# reason each time: when a data file's CONTENT is a control, its change is a code change.
CANON_SURFACE_FILES = (
    "CLAUDE.md",
    "docs/design/SURGICAL_LANDING.md",
)
CANON_SURFACE_TESTS = [
    "tests/tools/test_interim_bypass_retirement.py",
    # THE SIZE CEILING (2026-08-12 decay audit §6). OPS5 added the TRIGGER (CLAUDE.md, above) and
    # never wired it to the control that measures the file, so 52693115b sat 504 chars over the
    # limit for four days, red at HEAD, found only by the publish suite. Rationale and the mutation
    # proving this selection BITES: tests/tools/test_pre_commit_gate_canon_surface.py. ~0.4s.
    "tests/tools/test_claude_md_integrity.py",
]


def _py_files_naming(needle: str) -> set[str]:
    """Tracked `.py` files whose SOURCE contains `needle` as a literal. `git grep` over the index,
    not a walk of the working tree: the gate's subject is what is being committed, and a fork
    worktree's stale copies must never enter the answer."""
    r = subprocess.run(
        ["git", "grep", "-l", "--fixed-strings", "-I", needle, "--", "*.py"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    # rc 1 = no match (not an error); rc >1 = git itself failed -> no claim, empty set.
    if r.returncode > 1:
        return set()
    return {ln.strip() for ln in r.stdout.splitlines() if ln.strip()}


def _basename_identifies_one_file(name: str) -> bool:
    """Is this basename a NAME for one file, or a word the repo reuses? `process_manifest.yaml`
    names exactly one tracked file, so a module writing `_HERE / "process_manifest.yaml"` is
    talking about that file. `README.md` names dozens, so the same match means nothing -- and
    unconditional basename matching duly pulled 13 unrelated test files into a design-doc commit
    (caught by test_a_non_store_design_doc_is_still_pure_data). Ambiguity is resolved by dropping
    the ambiguous route, never the precise one: the repo-relative path is still asked."""
    r = subprocess.run(
        ["git", "ls-files", "--", f"*/{name}", name],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    if r.returncode != 0:
        return False
    return len([ln for ln in r.stdout.splitlines() if ln.strip()]) == 1


def data_surface_tests(path: str) -> list[str]:
    """Tests to run for a staged NON-`.py` file: the tests that name it, plus the convention tests
    of the modules that name it. See THE DATA SURFACE above for why this is derived rather than a
    sixth hand-kept list.

    FAILS TOWARD RUNNING, never toward silence, in the two places it can be wrong:
      * the basename fallback OVER-matches (two files sharing a name both answer) -- that costs a
        few seconds of tests, where under-matching costs a wedge;
      * a `git grep` that errors returns nothing, which is the one fail-open here and is bounded:
        the staged file is still subject to CODE_PREFIXES and the five surfaces above.

    `site/` references are excluded: that lane has its own gate (`tools/site_lane_gate.py`) and
    must never couple to the `tests/` selection.
    """
    p = Path(path)
    if p.suffix == ".py" or p.suffix.lower() not in DATA_SURFACE_SUFFIXES:
        return []
    if path.startswith(PUBLISHED_OUTPUT_ROOTS):
        return []  # regenerated output, gated elsewhere -- see PUBLISHED_OUTPUT_ROOTS
    if path in CURATED_SURFACE_PATHS:
        return []  # already covered by its own surface list -- see CURATED_SURFACE_PATHS
    # BOTH routes, unioned -- not basename-as-fallback. They answer DIFFERENT questions and the
    # first one is not the stronger: a doc-string or a test may cite the full repo path while the
    # module that actually LOADS the file writes `_HERE / "process_manifest.yaml"` and so is only
    # ever found by basename. Making basename a fallback selected the citers and dropped the
    # reader -- the finding's own instance, missed by its own fix (caught by the fires-test).
    referencing = _py_files_naming(path)
    if _basename_identifies_one_file(p.name):
        referencing |= _py_files_naming(p.name)
    targets: set[str] = set()
    for ref in referencing:
        if ref.startswith("site/"):
            continue
        if ref.startswith("tests/"):
            # a fixture/conftest that names the path is not itself a runnable guard
            if Path(ref).name.startswith("test_"):
                targets.add(ref)
        elif ref.startswith(CODE_PREFIXES):
            targets.update(tests_for(ref))
    return sorted(t for t in targets if (ROOT / t).exists())


def select_targets(files: list[str]) -> list[str]:
    """The set of test files to run for this commit, or [] to skip (no code/config/level-surface/
    mint-marker/canon-surface staged)."""
    code_changed = any(f.startswith(CODE_PREFIXES) for f in files)
    level_surface_changed = any(f in LEVEL_SURFACE_FILES for f in files)
    mint_marker_changed = any(
        f.startswith(MINT_MARKER_PREFIX) and f.endswith(".md") for f in files
    )
    canon_surface_changed = any(f in CANON_SURFACE_FILES for f in files)
    store_surface_changed = any(
        f.startswith(STORE_SURFACE_PREFIX) and f.endswith(".yaml") for f in files
    )
    site_surface_changed = any(
        f.startswith(SITE_SURFACE_PREFIX) and f.endswith(".html") for f in files
    )
    # THE DATA SURFACE: derived, so it is computed BEFORE the skip decision -- a data file that
    # some module reads is not a "pure docs/data commit", and deciding that from the prefix list
    # alone is the exact fail-open this closes.
    data_targets: set[str] = set()
    for f in files:
        data_targets.update(data_surface_tests(f))
    if not (code_changed or level_surface_changed or mint_marker_changed
            or canon_surface_changed or store_surface_changed or site_surface_changed
            or data_targets):
        return []  # pure docs/data commit touching no control, level surface, mint marker,
        # canon, per-atom store, page, or file any module reads
    targets: set[str] = set(data_targets)
    if code_changed:
        targets.update(t for t in CONTROL_TESTS if (ROOT / t).exists())
    if level_surface_changed:
        targets.update(t for t in LEVEL_SENSITIVE_TESTS if (ROOT / t).exists())
    if mint_marker_changed:
        targets.update(t for t in MINT_HYGIENE_TESTS if (ROOT / t).exists())
    if canon_surface_changed:
        targets.update(t for t in CANON_SURFACE_TESTS if (ROOT / t).exists())
    if store_surface_changed:
        targets.update(t for t in STORE_CONTRACT_TESTS if (ROOT / t).exists())
    if site_surface_changed:
        targets.update(t for t in SITE_SURFACE_TESTS if (ROOT / t).exists())
    for f in files:
        targets.update(tests_for(f))
    return sorted(targets)


def _gitless_env(env: dict) -> dict:
    """Strip every GIT_* key from an environment mapping.

    CRITICAL: during a `git commit` the hook inherits GIT_INDEX_FILE / GIT_DIR / GIT_WORK_TREE /
    GIT_PREFIX pointing at the IN-PROGRESS commit. Any git-touching test (e.g. build_executor,
    retro_cadence_check, worker_seat) then runs `git` subprocesses that operate on the REAL
    worktree index -- observed corrupting it (phantom deletions) and once producing a commit that
    deleted the whole tree; a leaked GIT_DIR is also the likely setter of the core.bare=true
    corruption. Scrubbing GIT_* makes gate-run tests use their own tmp repos, never the commit's
    index. (H24_precommit_gate_git_env_isolation)
    """
    return {k: v for k, v in env.items() if not k.startswith("GIT_")}


STAGING_ROOM_PREFIX = "docs/staging/"


def _class_consolidation_check() -> tuple[bool, str]:
    """Run the finding-class checker against the REAL tree. FAIL-CLOSED.

    `background.finding_classes.check()` enforces six rules over the five class
    documents (at most one class per finding, no unconsolidated instance, no
    resurrection, printed count == list length, no document in two rooms, printed
    severity == derived severity). Until now NOTHING ran it -- every class document
    says membership "is DERIVED, never hand-kept" and re-derives "if a live finding
    belongs to this class and is not listed here", which read as a standing
    guarantee and was in fact an invitation to type a command
    (`WORKER_FINDING_THE_CLASS_CHECKER_HAS_NO_AUTOMATED_CALLER_2026-08-12`).

    FAIL-CLOSED is the whole point, and it is R15's THIRD killer pattern
    (FAIL-SILENT: a check skipped because its module did not import is a check that
    passed). An import error, an unexpected exception, anything at all -> the commit
    is REFUSED with the reason. There is no path through this function that reports
    success without `check()` having actually returned a clean result.
    """
    # ROOT ON sys.path FIRST, and this is not boilerplate. The gate's own legal
    # committer (`tools/surgical_land.py`) runs it against a SCRATCH CHECKOUT of the
    # tree the commit would create -- a different cwd, with `background` nowhere on
    # the default path. Without this line the import below raises
    # ModuleNotFoundError, the fail-closed branch fires for an ENVIRONMENTAL reason,
    # and EVERY staging commit is refused with a message blaming the class checker.
    # Caught by surgical_land refusing this very commit; `test_checker_imports_from_a_foreign_cwd`
    # is the falsifier.
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from background.finding_classes import check
    except Exception as e:  # noqa: BLE001 -- an unavailable check is a FAILED check
        return False, (
            f"class checker UNAVAILABLE: {type(e).__name__}: {e}\n"
            "An unavailable check is a FAILED check (R15 FAIL-SILENT). If the module is "
            "genuinely being removed, remove this gate step in the same commit."
        )
    try:
        result = check()
    except Exception as e:  # noqa: BLE001
        return False, f"class checker RAISED: {type(e).__name__}: {e}"
    if result.ok:
        return True, "class consolidation holds"
    return False, "\n".join(f"  - {f}" for f in result.failures)


def _staging_severity_check(staged: list[str]) -> tuple[bool, str]:
    """Every staging document THIS COMMIT writes carries a parseable severity header.

    WHY (2026-08-15). `background/finding_severity.py` already implements the
    zero-unclassified control -- its `main()` returns 1 on any unclassified document, and
    its own module comment calls it "the zero-unclassified control". NOTHING RAN IT. It
    was reachable only by typing the command or by tripping over its consequence, which
    is the same defect the class checker had
    (`WORKER_FINDING_THE_CLASS_CHECKER_HAS_NO_AUTOMATED_CALLER_2026-08-12`, closed by
    `_class_consolidation_check` above) -- and this one bites harder, because
    `background/gate_authorization.py` refuses a level raise in EVERY lane while any
    document is unclassified ("an unclassified document refuses EVERY lane, deliberately"
    -- its own words, and the loophole it closes is that mangling a header would otherwise
    be the cheapest way to clear a hold).

    MEASURED: two documents with no severity header
    (`DIRECTOR_DECISION_PENDING_RATE_REBASELINE_AND_SPLIT_APPROVAL_2026-08-14`,
    `WORKER_REPORT_THE_LEAK_IS_MARKED_SWEPT_AND_TESTED_BOTH_WAYS_2026-08-14`) held
    level-recording in all 13 lanes. Both authored by this machine; neither author was
    told. Per R10 the instance fix (two header lines) does not close the class -- this
    step is what makes the whole class fail automatically.

    SCOPE IS THIS COMMIT'S OWN DOCUMENTS, not the whole room, and that is deliberate. The
    sibling `_landed_manifest_check` states the reason: a whole-rooms scope bills this
    committer for other authors' rot, and a fail-closed control with no reachable
    discharge is how this project has wedged its own publishing before. A header is the
    AUTHOR's obligation at the moment of writing, and this fires exactly there. (The
    backlog is separately at zero as of this commit, so the narrow scope forgoes nothing
    today.)

    THE SUBJECT IS THE TREE THIS COMMIT WOULD CREATE, never the working tree. Reading the
    working file would let a `git commit -- <pathspec>` land an unheadered blob while a
    fixed-but-unstaged copy sat on disk saying otherwise -- the exact defect filed as
    `WORKER_FINDING_THE_SITE_LANE_GATES_THE_WORKING_TREE_NOT_THE_COMMIT_2026-08-13`.

    DELETIONS ARE SKIPPED, and that is the archive path, not an escape hatch: moving a
    document to `docs/staging/done/` deletes it from the room, `git cat-file` finds no
    blob, and there is nothing left to classify. Doorbells (`run_complete_*`,
    `run_pending_*`, `from_rich_*`) are excluded by the same exact-prefix list the parser
    uses, imported rather than re-typed, so the two populations cannot drift apart.

    FAIL-CLOSED at every step (R15 killer pattern 3): unimportable parser, unusable index,
    unreadable blob -> REFUSED with the reason. An unavailable check is a FAILED check.
    """
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from background.finding_severity import DOORBELL_PREFIXES, parse_severity_text
    except Exception as e:  # noqa: BLE001 -- an unavailable check is a FAILED check
        return False, (
            f"severity parser UNAVAILABLE: {type(e).__name__}: {e}\n"
            "An unavailable check is a FAILED check (R15 FAIL-SILENT). If the module is "
            "genuinely being removed, remove this gate step in the same commit."
        )

    # The staging ROOM is flat: `classifiable_documents` globs `*.md` and never recurses,
    # so `done/` and `in_progress/` are outside the classified population by construction.
    # Mirror that here with a segment count rather than a second glob.
    candidates = [
        p for p in staged
        if p.startswith(STAGING_ROOM_PREFIX)
        and p.endswith(".md")
        and "/" not in p[len(STAGING_ROOM_PREFIX):]
        and not p[len(STAGING_ROOM_PREFIX):].startswith(DOORBELL_PREFIXES)
    ]
    if not candidates:
        return True, ""

    try:
        tree = _index_tree()
    except Exception as e:  # noqa: BLE001
        return False, f"could not determine the tree this commit would create: {e}"

    failures: list[str] = []
    checked = 0
    for path in candidates:
        try:
            blob = subprocess.run(
                ["git", "cat-file", "blob", f"{tree}:{path}"],
                cwd=ROOT, capture_output=True, text=True, timeout=30,
            )
        except Exception as e:  # noqa: BLE001
            return False, f"could not read {path} out of tree {tree[:9]}: {e}"
        if blob.returncode != 0:
            continue  # not in the tree this commit creates -- a deletion (the `done/` move)
        result = parse_severity_text(blob.stdout, Path(path))
        checked += 1
        if result.severity == "UNCLASSIFIED":
            failures.append(f"{path}: {result.reason}")

    if failures:
        return False, "\n".join(f"  - {f}" for f in failures)
    return True, f"{checked} staging document(s) carry a parseable severity header"


WALL_REGISTER_PATH = "docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md"
WALL_CENSUS_BASELINE = "docs/design/wall_channel_census_baseline.json"


def _index_tree(root: Path = ROOT) -> str:
    """The sha of the tree THIS COMMIT WOULD CREATE. Raises on anything else.

    `git write-tree`, against A COPY of the index in effect, and both halves of
    that sentence were paid for.

    WHICH INDEX. The environment is READ, not scrubbed — the one place in this
    file where scrubbing `GIT_*` would be a defect. `git commit -- <pathspec>`
    builds a TEMPORARY index and hands the hook its path in `GIT_INDEX_FILE`;
    ignore that and write-tree serialises the REAL index instead — the whole
    shared tree's staged state rather than the pathspec the committer chose —
    and the gate would judge a tree nobody is about to create. (The pytest run
    below still scrubs, for the opposite and equally deliberate reason: a test
    subprocess must not inherit a commit in progress.)

    WHY A COPY. `git write-tree` takes `index.lock` to write back the cache-tree
    extension, and during a plain `git commit` GIT HOLDS THAT LOCK while the
    hook runs: called on the live index it dies `rc=128 index.lock: File exists`
    and, being fail-closed, would REFUSE EVERY COMMIT of that shape. Found the
    way the last one was — by the gate refusing its own commit — and it is the
    same environmental-refusal defect `surgical_land` caught when the class
    checker was wired (a check that reds for a reason that is not its subject is
    worse than no check). Copying costs one file write and cannot lock anything.
    """
    idx = os.environ.get("GIT_INDEX_FILE")
    if not idx:
        where = subprocess.run(["git", "rev-parse", "--git-path", "index"], cwd=str(root),
                               capture_output=True, text=True, check=False)
        if where.returncode != 0:
            raise RuntimeError(f"git rev-parse --git-path index rc={where.returncode}: "
                               f"{where.stderr.strip()[-200:]}")
        idx = where.stdout.strip()
    src = Path(idx) if os.path.isabs(idx) else (root / idx)
    if not src.is_file():
        raise RuntimeError(f"no index to read at {src}")
    with tempfile.TemporaryDirectory(prefix="gate-index-") as tmp:
        copy = Path(tmp) / "index"
        shutil.copyfile(src, copy)
        out = subprocess.run(["git", "write-tree"], cwd=str(root), capture_output=True, text=True,
                             check=False, env={**os.environ, "GIT_INDEX_FILE": str(copy)})
    if out.returncode != 0:
        raise RuntimeError(f"git write-tree rc={out.returncode}: {out.stderr.strip()[-300:]}")
    tree = out.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", tree):
        raise RuntimeError(f"git write-tree returned something that is not a tree sha: {tree!r}")
    return tree


def _wall_crossing_landed_check(staged: list[str]) -> tuple[bool, str]:
    """Reconcile the wall-crossing register against THE TREE THIS COMMIT CREATES.

    THE CLASS THIS CLOSES. `tools/wall_crossing_dispositions.py --at-head` was
    built on 2026-08-10, after the THIRD instance in two days of a register
    entry claiming a cut that no commit contained, and it is proven against real
    history. It then had no automated caller, and the class recurred one KNIFE
    step later — five files of step 21 sat untracked while the atom's own record
    said LANDED (WORKER_FINDING_THE_CLOSE_TIME_CHECK_THAT_CATCHES_THIS_HAS_NO_CALLER,
    2026-08-13). A control invoked only by someone typing it is R15's FAIL-SILENT
    pattern: permanently unavailable, therefore permanently passing. **A control
    built to catch "the record outran the code" cannot be invoked by the record.
    It has to be invoked by the thing that makes the code real — the commit.**

    ORDERING, the first of the two questions that finding left open. `--at-head`
    is asymmetric by design (working-tree register vs HEAD's code), which at
    pre-commit time measures the tree the commit REPLACES — it would red on
    precisely the commit that repairs a divergence. So this caller uses the
    `--at-tree` mode against `git write-tree`: the tree the commit WOULD create,
    both sides from that one tree. Same subject `tools/surgical_land.py` gates
    on, and the finding named that as the remedy.

    SCOPE, the second. Any staged `.py` at all, plus the register itself. Not
    "wall-side directories": `tools/` and `background/` are BRIDGE packages the
    walker routes INDIRECT crossings through, so a `tools/` edit can create a
    crossing, and a scope that excluded them would be blind to exactly the edges
    that are hardest to find. A pure docs/data commit skips it (and skips the
    import), so the fail-closed branch below can never refuse a commit that had
    no code in it.

    The finding also asked whether a register edit and its code cut may land in
    SEPARATE commits within one tick. They may — in the order code-then-record.
    What reds is record-first, and that is not an honest split: it is a claim
    published into the repo that the repo does not support. Note this adds no
    new rule, because the working-tree gate has always demanded that coherence
    of the desk; this demands it of the tree other people receive.

    FAIL-CLOSED at every step (R15, third pattern): unimportable module, an
    unusable index, a raising checker -> the commit is REFUSED with the reason.
    """
    if not (any(p.endswith(".py") for p in staged) or WALL_REGISTER_PATH in staged):
        return True, ""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from tools.wall_crossing_dispositions import run_at_tree
    except Exception as e:  # noqa: BLE001 -- an unavailable check is a FAILED check
        return False, (
            f"wall-crossing checker UNAVAILABLE: {type(e).__name__}: {e}\n"
            "An unavailable check is a FAILED check (R15 FAIL-SILENT). If the tool is "
            "genuinely being removed, remove this gate step in the same commit."
        )
    try:
        tree = _index_tree()
    except Exception as e:  # noqa: BLE001
        return False, f"could not determine the tree this commit would create: {e}"
    try:
        findings, report = run_at_tree(tree)
    except Exception as e:  # noqa: BLE001
        return False, f"wall-crossing checker RAISED against tree {tree[:9]}: {type(e).__name__}: {e}"
    if not findings:
        return True, (
            f"wall crossings reconcile at the tree this commit creates "
            f"({report['measured_crossings']} live, {report['rows']} ruled)"
        )
    return False, "\n".join(f"  - {f}" for f in findings)


def _wall_channel_census_check(staged: list[str]) -> tuple[bool, str]:
    """Has any of the wall's FOUR WALKER-INVISIBLE channels grown in the tree this commit creates?

    THE CLASS THIS CLOSES. The step above reconciles the disposition register, whose subject is
    the import edge -- channels A and B of the 2026-08-15 conformance census. That census found
    SIX mechanisms carrying data across the wall and that the repo could see two of them: the
    envelope (C), the same-step typed port (D), the structural Protocol (E) and the published
    artefact (F) were invisible to every automated control in the tree, and the widest of them was
    91 keys wide with 11 reader modules. A crossing added on any of those four could not be
    noticed by anything. `tools/wall_channel_census.py` enumerates them; this is the caller that
    makes it real, for the reason the step above states in full -- a control invoked only by
    someone typing it is permanently unavailable, therefore permanently passing.

    SAME TREE, SAME REASON. `census_at` is given `git write-tree`, so the readers and the
    published artefact channel F joins them against both come from the tree the commit WOULD
    create. HEAD would red the commit that repairs a divergence and pass the one that introduces
    it, which is the ordering trap this file already learned once.

    SHRINK-ONLY, NOT ZERO. A member disappearing passes and is reported; only growth refuses. The
    frozen list is `docs/design/wall_channel_census_baseline.json`, and re-freezing is how a new
    member gets ruled -- which is a decision someone has to write down rather than one this gate
    can make.

    FAIL-CLOSED at every step (R15 FAIL-SILENT): unimportable module, unusable index, raising
    checker, unreadable baseline -> the commit is REFUSED with the reason.
    """
    if not any(p.endswith(".py") for p in staged) and WALL_CENSUS_BASELINE not in staged:
        return True, ""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from tools.wall_channel_census import (
            census_at,
            check,
            load_baseline,
            wire_conformance_at,
        )
    except Exception as e:  # noqa: BLE001 -- an unavailable check is a FAILED check
        return False, (
            f"wall-channel census UNAVAILABLE: {type(e).__name__}: {e}\n"
            "An unavailable check is a FAILED check (R15 FAIL-SILENT). If the tool is "
            "genuinely being removed, remove this gate step in the same commit."
        )
    try:
        tree = _index_tree()
    except Exception as e:  # noqa: BLE001
        return False, f"could not determine the tree this commit would create: {e}"
    try:
        verdict = check(census_at(tree, ROOT), load_baseline())
    except Exception as e:  # noqa: BLE001
        return False, f"wall-channel census RAISED against tree {tree[:9]}: {type(e).__name__}: {e}"
    try:
        wire = wire_conformance_at(rev=tree, repo_root=ROOT)
    except Exception as e:  # noqa: BLE001
        return False, f"channel-D wire check RAISED against tree {tree[:9]}: {type(e).__name__}: {e}"
    # CHANNEL D'S WIRE CHECK BLOCKS -- 2026-08-19 pass 13, restored in the same commit that made
    # it satisfiable, which is the only commit in which restoring it is honest.
    #
    # `WireVerdict.ok` is `not self.silent`: zero tolerance, no frozen debt list, unlike the
    # census half beside it which has one. That is deliberate -- channel D's whole conformance is
    # three call sites, so a debt list here would be a list of the entire subject. The reason the
    # previous pass downgraded it to reporting was NOT that the rule was wrong: it was that the
    # three sites it names lived only in an uncommitted tree, so every commit in the repo was
    # refused, the publisher's included. That is a landing-order defect, not a control defect, and
    # the fix is to land the sites -- which this commit's own tree does. Measured before restoring
    # rather than hoped: `wire_conformance_at` against the tree this commit creates reports all 3
    # sites carrying, while against HEAD it names exactly those 3 as silent.
    if not verdict.ok:
        return False, verdict.report()
    if not wire.ok:
        return False, wire.report()
    return True, (
        "the wall's four walker-invisible channels have not grown; "
        f"channel D's {len(wire.carrying)} wire site(s) carry the version"
    )


def _symbol_landing_check(staged: list[str]) -> tuple[bool, str]:
    """Does every first-party reference this commit CHANGES resolve in the tree it creates?

    THE CLASS THIS CLOSES. `19d8f94da` committed two readers of
    `tools.simplifications_store.atom_name` and not the function itself. At HEAD the
    symbol did not exist; in the working tree it did; the publish gate found it hours
    later as a wedge with no attribution (229 consecutive failures, ~6,923 min). A
    pathspec commit names the paths the author EDITED, not the paths their change CALLS.

    WHY THE EXISTING CONTROLS WERE ALL BLIND, and it is one sentence: every one of them
    was looking at a different tree. The pytest run below selects from the index and
    executes in the WORKING TREE, where the supplier was present. The capability index's
    untracked-row check asks "is this FILE tracked?" -- and it was; only the new function
    inside it was missing, which is a granularity that check cannot reach.

    SCOPE, and it is deliberately the narrow one. The consumer population is the `.py`
    files this commit CHANGES (`--since-tree HEAD`), not the whole tree. Measured over
    the last 80 commits, the whole-tree scope carries a pre-existing finding that has
    nothing to do with the committer, and billing them for it is how a gate gets
    disabled. The changed-file scope's measured cost on that same history: ONE commit
    red of 80, and it is `19d8f94da` itself.

    FAIL-CLOSED at every step (R15): an unimportable checker, an unusable index, a
    raising resolver -> REFUSED with the reason. An unavailable check is a FAILED check.
    """
    if not any(p.endswith(".py") for p in staged):
        return True, ""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from tools.symbol_landing_check import run_at_tree
    except Exception as e:  # noqa: BLE001 -- an unavailable check is a FAILED check
        return False, (
            f"symbol-landing checker UNAVAILABLE: {type(e).__name__}: {e}\n"
            "An unavailable check is a FAILED check (R15 FAIL-SILENT). If the tool is "
            "genuinely being removed, remove this gate step in the same commit."
        )
    try:
        tree = _index_tree()
    except Exception as e:  # noqa: BLE001
        return False, f"could not determine the tree this commit would create: {e}"
    try:
        findings, report = run_at_tree(tree, since_tree="HEAD^{tree}")
    except Exception as e:  # noqa: BLE001
        return False, (f"symbol-landing checker RAISED against tree {tree[:9]}: "
                       f"{type(e).__name__}: {e}")
    if not findings:
        return True, (f"every first-party reference resolves in the tree this commit "
                      f"creates ({report.get('references_resolved', 0)} checked)")
    return False, "\n".join(f"  - {f}" for f in findings)


def _landed_manifest_check(staged: list[str]) -> tuple[bool, str]:
    """Does every path a staged DOCUMENT claims LANDED exist in the tree this commit creates?

    THE CLASS THIS CLOSES, third instance in three days. A finding opened
    `status: INSTANCE FIXED (the supplier half landed)` and closed with a "what landed this
    tick" manifest; none of it was in any tree, and the publish gate logged the identical
    red for another 30 cycles while readers who believed the manifest diagnosed elsewhere
    (229 -> 244 consecutive failures). The first two instances were both closed with PROSE.

    WHY IT IS NOT THE SIBLING CHECKS. `_symbol_landing_check` resolves changed REFERENCES
    and cannot see this: nothing was committed, so there was no changed reference to
    resolve. `_wall_crossing_landed_check` reads a structured REGISTER; this reads a
    document's own prose claim, which is where findings actually make their promises.

    SCOPE. Staging documents this commit CHANGES, which is the moment the claim becomes
    load-bearing for the next reader -- including the archive-to-`done/` move. Not the
    whole rooms: paths move, and archived documents cite paths since renamed (66 dead
    evidence paths across 80 atoms, 2026-08-13), so a whole-rooms scope would bill this
    committer for other authors' rot. Like the class checker, it runs BEFORE the pure-docs
    early return, because a staging-only commit selects no test targets and IS the commit
    that files the claim.

    FAIL-CLOSED at every step (R15): unimportable checker, unusable index, raising
    resolver -> REFUSED with the reason. An unavailable check is a FAILED check.
    """
    if not any(p.startswith(STAGING_ROOM_PREFIX) for p in staged):
        return True, ""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from tools.landed_manifest_check import run_at_tree
    except Exception as e:  # noqa: BLE001 -- an unavailable check is a FAILED check
        return False, (
            f"landed-manifest checker UNAVAILABLE: {type(e).__name__}: {e}\n"
            "An unavailable check is a FAILED check (R15 FAIL-SILENT). If the tool is "
            "genuinely being removed, remove this gate step in the same commit."
        )
    try:
        tree = _index_tree()
    except Exception as e:  # noqa: BLE001
        return False, f"could not determine the tree this commit would create: {e}"
    try:
        findings, report = run_at_tree(tree, since_tree="HEAD^{tree}")
    except Exception as e:  # noqa: BLE001
        return False, (f"landed-manifest checker RAISED against tree {tree[:9]}: "
                       f"{type(e).__name__}: {e}")
    if findings:
        return False, "\n".join(f"  - {f}" for f in findings)
    # The unchecked count is PRINTED on the green path on purpose: it is the control's own
    # error bar (claims seen, no path parsed), and a control that hides it invites the
    # confidence its subject is made of.
    unchecked = len(report["unchecked_documents"])
    msg = (f"every landing claim resolves in the tree this commit creates "
           f"({report['paths_checked']} path(s) in {report['documents_claiming_a_landing']} "
           f"document(s)")
    msg += f"; {unchecked} claim(s) unchecked, no path parsed)" if unchecked else ")"
    return True, msg


def _record_landing_claim_check(staged: list[str]) -> tuple[bool, str]:
    """Does an atom's own STORE RECORD claim a symbol landed where the tree has it not?

    THE CLASS THIS CLOSES, and it is R3 territory: FIVE consecutive `EP6_wall_protocol_typing`
    passes wrote a record asserting three `include_schema_version` call sites had landed, and
    at `d1d1e1fc5` `git grep -c include_schema_version HEAD -- simulation/` was still empty.
    Recommendation 1 of
    `WORKER_FINDING_THREE_CONSECUTIVE_PASSES_RECORDED_A_LANDING_THAT_IS_IN_NO_COMMIT_2026-08-19`,
    the one left unbuilt when the landing tool itself was redesigned.

    WHY IT IS NEITHER SIBLING. `_symbol_landing_check` resolves references a commit CHANGES,
    and those passes committed no code at all. `_landed_manifest_check` reads a staging
    document's prose for PATHS, and every path EP6 named existed at HEAD throughout -- what
    was missing was a symbol inside one, and the claim lived in the store record, not the
    staging room.

    WHY THE CLAIM IS SCOPED. `include_schema_version` was present at HEAD the whole time, in
    three port modules and their tests. "Does the tree carry this symbol?" is GREEN on the
    real defect; only "does it carry it HERE?" can be red.

    FAIL-CLOSED at every step (R15): unimportable checker, unusable index, raising resolver
    -> REFUSED with the reason. An unavailable check is a FAILED check.
    """
    if not any(p.startswith("docs/design/simplifications/") for p in staged):
        return True, ""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from tools.record_landing_claim_check import run_at_tree
    except Exception as e:  # noqa: BLE001 -- an unavailable check is a FAILED check
        return False, (
            f"record-landing-claim checker UNAVAILABLE: {type(e).__name__}: {e}\n"
            "An unavailable check is a FAILED check (R15 FAIL-SILENT). If the tool is "
            "genuinely being removed, remove this gate step in the same commit."
        )
    try:
        tree = _index_tree()
    except Exception as e:  # noqa: BLE001
        return False, f"could not determine the tree this commit would create: {e}"
    try:
        findings, report = run_at_tree(tree, since_tree="HEAD^{tree}")
    except Exception as e:  # noqa: BLE001
        return False, (f"record-landing-claim checker RAISED against tree {tree[:9]}: "
                       f"{type(e).__name__}: {e}")
    if findings:
        return False, "\n".join(f"  - {f}" for f in findings)
    if not report["records_changed"]:
        return True, ""
    return True, (
        f"every landing claim in {report['records_changed']} changed record(s) resolves in "
        f"the tree this commit creates ({report['claims_checked']} claim(s) checked, "
        f"{report['records_claiming_a_landing']} record(s) asserting a landing)"
    )


def main() -> int:
    staged = staged_files()

    # THE CLASS-DOCUMENT SURFACE. Fourth sibling of LEVEL_SURFACE / MINT_MARKER /
    # CANON_SURFACE, same reason each time: when a data file's CONTENT is a control,
    # its change is a code change.
    #
    # THIS RUNS BEFORE THE PURE-DOCS EARLY RETURN ON PURPOSE. A commit that only
    # touches `docs/staging/**` selects no test targets, so it takes the `return 0`
    # below -- and a staging-only commit is EXACTLY the commit that files a
    # sixteenth instance against an unrendered class, or walks an archived finding
    # back into the root. Putting the check after that return would have wired the
    # caller to everything except the writes that cause the rot.
    if any(p.startswith(STAGING_ROOM_PREFIX) for p in staged):
        ok, detail = _class_consolidation_check()
        if not ok:
            sys.stderr.write(
                "\n[test-gate] ❌ FINDING-CLASS CONSOLIDATION BROKEN -- COMMIT REFUSED.\n"
                f"{detail}\n"
                "[test-gate] Re-render with `python3 -m background.finding_classes --render`, "
                "or fix the membership, then commit. Verify with `--check`.\n"
            )
            return 1
        print("[test-gate] ✓ finding-class consolidation holds")

        # THE DOCUMENT'S OWN LANDING CLAIM. Same room, same reason, and it must sit inside
        # this staging branch: the claim it judges is written by a staging commit.
        ok, detail = _landed_manifest_check(staged)
        if not ok:
            sys.stderr.write(
                "\n[test-gate] ❌ A DOCUMENT CLAIMS A PATH LANDED THAT THIS COMMIT'S TREE "
                "DOES NOT CARRY -- COMMIT REFUSED.\n"
                f"{detail}\n"
                "[test-gate] A false LANDED is worse than no finding: it redirects the next "
                "reader away from the live cause. Land the path in this commit, or drop the "
                "claim.\n"
                "[test-gate] Reproduce: `python3 -m tools.landed_manifest_check --at-tree "
                "$(git write-tree) --since-tree 'HEAD^{tree}'`\n"
            )
            return 1
        if detail:
            print(f"[test-gate] ✓ {detail}")

        # THE DOCUMENT'S OWN SEVERITY HEADER. Third member of this staging branch, and it
        # belongs here for the branch's own stated reason: a staging-only commit selects no
        # test targets, and a staging-only commit is EXACTLY the commit that files an
        # unheadered document -- which holds level-recording in all 13 lanes, not one.
        ok, detail = _staging_severity_check(staged)
        if not ok:
            sys.stderr.write(
                "\n[test-gate] ❌ A STAGING DOCUMENT THIS COMMIT WRITES HAS NO PARSEABLE "
                "SEVERITY HEADER -- COMMIT REFUSED.\n"
                f"{detail}\n"
                "[test-gate] An unclassified document refuses a level raise in EVERY lane "
                "(background/gate_authorization.py): its severity could be BLOCKING and its "
                "lane is unknown, so it cannot show any lane clear.\n"
                "[test-gate] Fix is one line in the header block (first 40 lines, before the "
                "first `## `):\n"
                "[test-gate]   **Severity:** BLOCKING|LATENT|RECORDED · **Lane:** <lane>\n"
                "[test-gate] Reproduce: `python3 -m background.finding_severity`\n"
            )
            return 1
        if detail:
            print(f"[test-gate] ✓ {detail}")

    # THE ATOM'S OWN STORE RECORD, checked against the tree this commit creates. Runs before
    # the pure-docs early return for the branch's standing reason: a commit that touches only
    # `docs/design/simplifications/**` selects no test targets, and that commit is precisely
    # the one that records a landing which never happened. Five EP6 passes took exactly it.
    ok, detail = _record_landing_claim_check(staged)
    if not ok:
        sys.stderr.write(
            "\n[test-gate] ❌ A STORE RECORD CLAIMS A LANDING THIS COMMIT'S TREE DOES NOT "
            "CARRY -- COMMIT REFUSED.\n"
            f"{detail}\n"
            "[test-gate] Five consecutive EP6 passes wrote this claim and no tree ever held "
            "the code. Land it in this commit, or state what you actually did.\n"
            "[test-gate] The checkable form is one line:  LANDED: `symbol` in `path/prefix`\n"
            "[test-gate] Reproduce: `python3 -m tools.record_landing_claim_check`\n"
        )
        return 1
    if detail:
        print(f"[test-gate] ✓ {detail}")

    # THE WALL-CROSSING REGISTER, checked against the tree this commit creates.
    # Like the class checker above, this runs BEFORE the pure-docs early return:
    # a commit that lands ONLY the register (the record without the code) selects
    # no test targets, and that commit is the whole class this closes.
    ok, detail = _wall_crossing_landed_check(staged)
    if not ok:
        sys.stderr.write(
            "\n[test-gate] ❌ WALL-CROSSING REGISTER DISAGREES WITH THIS COMMIT'S TREE "
            "-- COMMIT REFUSED.\n"
            f"{detail}\n"
            "[test-gate] The register is a claim about what LANDED. Land the code in this "
            "commit, or correct the row.\n"
            "[test-gate] Reproduce: `python3 -m tools.wall_crossing_dispositions "
            "--at-tree $(git write-tree)`\n"
        )
        return 1
    if detail:
        print(f"[test-gate] ✓ {detail}")

    # THE FOUR CHANNELS THE REGISTER ABOVE CANNOT SEE. Same tree, same placement, and for
    # the same reason: a commit that widens the envelope, a port, a structural Protocol or
    # the published artefact may select no test targets at all.
    ok, detail = _wall_channel_census_check(staged)
    if not ok:
        sys.stderr.write(
            "\n[test-gate] ❌ A WALKER-INVISIBLE WALL CHANNEL HAS GROWN IN THIS COMMIT'S TREE "
            "-- COMMIT REFUSED.\n"
            f"{detail}\n"
            "[test-gate] The list is shrink-only. If the new crossing is intended, RULE it and "
            "re-freeze in this commit: `python3 -m tools.wall_channel_census --worktree "
            "--freeze` -- a freeze without a reason is an amnesty.\n"
            "[test-gate] Reproduce: `python3 -m tools.wall_channel_census --rev "
            "$(git write-tree)`\n"
        )
        return 1
    if detail:
        print(f"[test-gate] ✓ {detail}")

    # THE SUPPLIER HALF OF THIS COMMIT. Also before the pure-docs early return -- not
    # because a docs commit can trip it (it cannot; it needs a staged `.py`), but
    # because the commit that omits a supplier is frequently one whose OWN test
    # selection is empty, and the check must not live downstream of that `return 0`.
    ok, detail = _symbol_landing_check(staged)
    if not ok:
        sys.stderr.write(
            "\n[test-gate] ❌ A REFERENCE THIS COMMIT CHANGES DOES NOT RESOLVE IN THE TREE "
            "IT CREATES -- COMMIT REFUSED.\n"
            f"{detail}\n"
            "[test-gate] The consumer is in this commit and the supplier is not. Your "
            "pathspec named the paths you EDITED, not the paths your change CALLS -- add "
            "the file that defines the symbol.\n"
            "[test-gate] Reproduce: `python3 -m tools.symbol_landing_check --at-tree "
            "$(git write-tree) --since-tree 'HEAD^{tree}'`\n"
        )
        return 1
    if detail:
        print(f"[test-gate] ✓ {detail}")

    targets = select_targets(staged)
    if not targets:
        return 0  # pure docs/data commit -- nothing that can break a control
    print(f"[test-gate] {len(targets)} test file(s): {', '.join(targets)}")
    gitless_env = _gitless_env(os.environ)
    r = subprocess.run(
        [sys.executable, "-m", "pytest", *targets, "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=str(ROOT),
        env=gitless_env,
    )
    if r.returncode != 0:
        sys.stderr.write(
            "\n[test-gate] ❌ TESTS FAILED -- COMMIT REFUSED.\n"
            "[test-gate] A red commit is structurally impossible (director P0, 2026-07-17). "
            "Fix the tests, then commit.\n"
        )
        return 1
    print("[test-gate] ✓ all targeted tests green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
