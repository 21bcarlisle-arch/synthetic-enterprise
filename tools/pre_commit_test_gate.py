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


WALL_REGISTER_PATH = "docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md"


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
