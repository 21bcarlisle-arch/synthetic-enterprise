"""R15 both-ways proof for SP3, the size + clone ratchet.

Every rule below is proven as a FIRES-THEN-CLEARS pair against a real throwaway git repo: mutate
the tree so the named defect exists -> the gate reports it; revert -> the gate is clean. A control
that only ever passes is worthless (R15), and the three killer patterns are each pinned explicitly:

  TAUTOLOGY   -- `test_the_ceiling_is_not_derived_from_the_thing_it_checks` moves the tree while
                 holding the baseline fixed, proving the gate compares two independent sources
                 rather than echoing one at itself.
  FAIL-OPEN   -- missing/corrupt/unparseable baseline, unparseable source, empty scope scan: each
                 must REFUSE (exit 1) in BOTH rollout states, never pass.
  FAIL-SILENT -- an unreadable decision log must grant NO override (stricter, never laxer).

These run against a temp repo, never the real tree, so the suite can neither be fooled by nor
disturb this repo's permanently-dirty working tree.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import size_ratchet  # noqa: E402
from tools import size_ratchet_gate as gate  # noqa: E402


# --------------------------------------------------------------------------------- fixtures
def _run(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(repo), check=True, capture_output=True)


def _clone_body(name: str, n: int = 14) -> str:
    """A function whose AST shape exceeds the detector's 45-node threshold. Identifiers differ per
    copy so a TEXTUAL matcher would miss it -- the detector is structural, and these must collide."""
    lines = [f"def {name}(alpha, beta):"]
    for i in range(n):
        lines.append(f"    v{i} = alpha + beta * {i}")
    lines.append("    return " + " + ".join(f"v{i}" for i in range(n)))
    return "\n".join(lines) + "\n"


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A throwaway git repo shaped like the real one: two scope roots, a baseline, a HEAD."""
    r = tmp_path / "repo"
    (r / "tools").mkdir(parents=True)
    (r / "background").mkdir(parents=True)
    (r / "docs" / "observability").mkdir(parents=True)

    (r / "tools" / "alpha.py").write_text("def a():\n" + "    x = 1\n" * 40, encoding="utf-8")
    (r / "background" / "beta.py").write_text("def b():\n" + "    y = 2\n" * 30, encoding="utf-8")
    (r / "background" / "gamma.py").write_text(_clone_body("g_one"), encoding="utf-8")

    _run(r, "init", "-q")
    _run(r, "config", "user.email", "t@t.t")
    _run(r, "config", "user.name", "t")
    _run(r, "add", "-A")
    _run(r, "commit", "-qm", "base")
    gate.freeze(r, r / "baseline.json")
    return r


def _gate(repo: Path, state: str | None = None) -> int:
    bp = repo / "baseline.json"
    if state is not None:
        data = json.loads(bp.read_text())
        data["rollout_state"] = state
        bp.write_text(json.dumps(data))
    return gate.run(repo, bp)


def _stage(repo: Path, path: str, text: str) -> None:
    (repo / path).write_text(text, encoding="utf-8")
    _run(repo, "add", path)


def _findings(repo: Path) -> list[size_ratchet.Finding]:
    baseline = size_ratchet.load_baseline(repo / "baseline.json")
    touched = gate.staged_paths(repo)
    index = size_ratchet.census_at(None, project_dir=repo)
    head_lines, head_texts = gate._head_state(repo)
    return size_ratchet.evaluate(
        baseline, index, head_lines, touched, gate._index_texts(repo, touched), head_texts,
        gate.staged_renames(repo),
    )


# ------------------------------------------------------------------ 1/2. file growth, both states
def test_baseline_tree_is_clean(repo: Path) -> None:
    """The gate must not fire on the tree it was frozen against -- a control that reds on clean
    input is a false-positive generator, and this project has stalled on exactly that."""
    _stage(repo, "tools/alpha.py", (repo / "tools" / "alpha.py").read_text())
    assert _gate(repo, "gate") == 0


def test_file_growth_fires_in_warn_and_logs_then_clears(repo: Path) -> None:
    original = (repo / "tools" / "alpha.py").read_text()
    warn_log = repo / "warns.jsonl"
    gate.WARN_LOG_PATH = warn_log  # type: ignore[misc]
    try:
        _stage(repo, "tools/alpha.py", original + "    z = 3\n" * 10)
        assert _gate(repo, "warn") == 0, "warn state must NOT block the commit"
        assert warn_log.exists(), "a real violation must be logged"
        entries = [json.loads(x) for x in warn_log.read_text().splitlines()]
        assert any(e["rule"] == size_ratchet.RULE_FILE_EXCEEDS_BASELINE for e in entries)
        before = len(entries)

        _stage(repo, "tools/alpha.py", original)
        assert _gate(repo, "warn") == 0
        after = len(warn_log.read_text().splitlines())
        assert after == before, "the warn-log must grow ONLY on a real violation, never every run"
    finally:
        gate.WARN_LOG_PATH = size_ratchet.WARN_LOG_PATH  # type: ignore[misc]


def test_append_warn_log_refuses_to_write_when_there_is_nothing_to_report(tmp_path: Path) -> None:
    """Pins `append_warn_log`'s OWN empty-input guard, directly.

    Found by mutation: deleting that guard fired nothing, because `run()` returns early on no
    findings so no caller-level test can ever reach it. It was dead defence that read as covered --
    the same shape as a control whose green count never blinks. Exercised here at the function
    boundary so the guard is genuinely live, and so a future caller that does not pre-check cannot
    turn the warn-log into noise that grows every run.
    """
    log = tmp_path / "w.jsonl"
    gate.append_warn_log([], log)
    assert not log.exists(), "an empty finding list must write nothing at all"

    gate.append_warn_log(
        [size_ratchet.Finding(size_ratchet.RULE_CLONE_CEILING, "<tree>", 283, 284)], log
    )
    assert len(log.read_text().splitlines()) == 1


def test_file_growth_fires_in_gate_state_then_clears(repo: Path) -> None:
    original = (repo / "tools" / "alpha.py").read_text()
    _stage(repo, "tools/alpha.py", original + "    z = 3\n" * 10)
    assert _gate(repo, "gate") == 1, "gate state must BLOCK the commit"
    _stage(repo, "tools/alpha.py", original)
    assert _gate(repo, "gate") == 0


# ----------------------------------------------------------------------- 3. the clone ceiling
def test_clone_ceiling_fires_on_a_new_cross_file_clone_then_clears(repo: Path) -> None:
    baseline = json.loads((repo / "baseline.json").read_text())
    ceiling = baseline["clone_ceiling"]

    _stage(repo, "tools/dup.py", _clone_body("g_two"))
    findings = _findings(repo)
    clone_hits = [f for f in findings if f.rule == size_ratchet.RULE_CLONE_CEILING]
    assert clone_hits, f"a structurally-identical body in a second file must breach ceiling {ceiling}"
    assert clone_hits[0].actual > ceiling

    (repo / "tools" / "dup.py").unlink()
    _run(repo, "rm", "-q", "--cached", "tools/dup.py")
    assert not [f for f in _findings(repo) if f.rule == size_ratchet.RULE_CLONE_CEILING]


def test_the_clone_detector_is_structural_not_textual(repo: Path) -> None:
    """Renaming every identifier must NOT hide the clone -- if it did, the ceiling would be
    dodgeable by find-and-replace, which the ruling names as the fidelity bug itself."""
    body = _clone_body("g_two").replace("alpha", "aaa").replace("beta", "bbb").replace("v", "w")
    _stage(repo, "tools/dup.py", body)
    assert [f for f in _findings(repo) if f.rule == size_ratchet.RULE_CLONE_CEILING]


# ------------------------------------------------------------------------- 4. the new-file cap
def test_new_file_over_cap_fires_then_clears(repo: Path) -> None:
    big = "def big():\n" + "    q = 1\n" * (size_ratchet.NEW_FILE_LINE_CAP + 100)
    _stage(repo, "tools/fresh.py", big)
    hits = [f for f in _findings(repo) if f.rule == size_ratchet.RULE_NEW_FILE_OVER_CAP]
    assert hits and hits[0].ceiling == size_ratchet.NEW_FILE_LINE_CAP

    _stage(repo, "tools/fresh.py", "def small():\n    return 1\n")
    assert not [f for f in _findings(repo) if f.rule == size_ratchet.RULE_NEW_FILE_OVER_CAP]


def test_existing_oversized_files_are_grandfathered_never_retroactively_capped(repo: Path) -> None:
    """43 real files already exceed the cap. The cap governs NEW files only; applying it
    retroactively would red the whole tree on day one and make the ratchet a remediation sprint --
    the exact thing its title says it must never be."""
    huge = "def h():\n" + "    q = 1\n" * (size_ratchet.NEW_FILE_LINE_CAP + 500)
    (repo / "tools" / "legacy.py").write_text(huge, encoding="utf-8")
    _run(repo, "add", "tools/legacy.py")
    _run(repo, "commit", "-qm", "legacy")
    gate.freeze(repo, repo / "baseline.json")

    _stage(repo, "tools/alpha.py", (repo / "tools" / "alpha.py").read_text())
    assert _gate(repo, "gate") == 0, "a grandfathered oversized file must not fire"


def test_new_function_over_cap_fires_then_clears(repo: Path) -> None:
    original = (repo / "background" / "beta.py").read_text()
    body = "def fresh_fn():\n" + "    q = 1\n" * (size_ratchet.NEW_FUNCTION_LINE_CAP + 10)
    _stage(repo, "background/beta.py", original + body)
    hits = [f for f in _findings(repo) if f.rule == size_ratchet.RULE_NEW_FUNCTION_OVER_CAP]
    assert hits and "fresh_fn" in hits[0].path

    _stage(repo, "background/beta.py", original)
    assert not [f for f in _findings(repo) if f.rule == size_ratchet.RULE_NEW_FUNCTION_OVER_CAP]


def _oversized_module(name: str) -> str:
    return f"def {name}():\n" + "    q = 1\n" * (size_ratchet.NEW_FUNCTION_LINE_CAP + 10)


def test_a_pure_rename_does_not_mint_its_functions_as_new(repo: Path) -> None:
    """Rule 2b reads a file's prior state BY PATH, so a `git mv` used to present every function in
    the moved file as brand new -- an oversized-but-grandfathered `main()` fired the moment its
    file was refiled, with zero lines changed. Landed 2026-08-10 from
    `WORKER_FINDING_A_PURE_RENAME_READS_AS_A_NEW_OVERSIZED_FUNCTION_2026-08-10.md`, which the
    `A_composition_lift` cuts hit twice.

    The rename must be recognised through git's own `-M` detection, never through a filename
    heuristic: the ONLY thing that makes a move safe to wave through is that the content is
    unchanged, which is precisely what git measures and a name comparison does not.
    """
    body = _oversized_module("grandfathered_giant")
    (repo / "background" / "legacy_home.py").write_text(body, encoding="utf-8")
    _run(repo, "add", "background/legacy_home.py")
    _run(repo, "commit", "-qm", "the oversized function, already in history")
    gate.freeze(repo, repo / "baseline.json")

    _run(repo, "mv", "background/legacy_home.py", "tools/new_home.py")
    assert gate.staged_renames(repo) == {"tools/new_home.py": "background/legacy_home.py"}
    assert not [
        f for f in _findings(repo) if f.rule == size_ratchet.RULE_NEW_FUNCTION_OVER_CAP
    ], "a pure rename changed no code and must mint no new function"


def test_a_rename_that_also_adds_an_oversized_function_still_fires(repo: Path) -> None:
    """The vacuity guard on the test above. Carrying functions across a rename must not become a
    way to smuggle a NEW oversized one in under cover of the move -- so the same commit that
    renames the file and appends a fresh giant must still red, naming only the appended one.
    """
    body = _oversized_module("grandfathered_giant")
    (repo / "background" / "legacy_home.py").write_text(body, encoding="utf-8")
    _run(repo, "add", "background/legacy_home.py")
    _run(repo, "commit", "-qm", "the oversized function, already in history")
    gate.freeze(repo, repo / "baseline.json")

    _run(repo, "mv", "background/legacy_home.py", "tools/new_home.py")
    _stage(repo, "tools/new_home.py", body + _oversized_module("smuggled_giant"))
    hits = [f for f in _findings(repo) if f.rule == size_ratchet.RULE_NEW_FUNCTION_OVER_CAP]
    assert [h.path for h in hits] == ["tools/new_home.py::smuggled_giant"]


# ------------------------------------------- 5. the touched-file rule (the one that DRAINS debt)
def test_touched_file_that_grew_fires_even_while_under_the_frozen_baseline(repo: Path) -> None:
    """s3.3 is STRICTER than s3.1 and is the whole reason the ratchet drains rather than freezes.

    Shrink a file, commit that, then re-grow it back toward (but still under) its frozen baseline.
    Rule 1 is satisfied throughout -- so if rule 3 were merely rule 1 reused, this would pass. It
    must fire: a commit that TOUCHES a file may not grow it, full stop.
    """
    small = "def a():\n" + "    x = 1\n" * 10
    _stage(repo, "tools/alpha.py", small)
    _run(repo, "commit", "-qm", "shrink")

    regrown = "def a():\n" + "    x = 1\n" * 25  # > HEAD (11 lines), < baseline (41)
    _stage(repo, "tools/alpha.py", regrown)
    findings = _findings(repo)
    assert not [f for f in findings if f.rule == size_ratchet.RULE_FILE_EXCEEDS_BASELINE], (
        "precondition: rule 1 must be satisfied, so this can only be rule 3"
    )
    assert [f for f in findings if f.rule == size_ratchet.RULE_TOUCHED_FILE_GREW]

    _stage(repo, "tools/alpha.py", small)
    assert not [f for f in _findings(repo) if f.rule == size_ratchet.RULE_TOUCHED_FILE_GREW]


def test_an_untouched_oversized_file_is_fine_indefinitely(repo: Path) -> None:
    """The counterpart: the ratchet never demands a remediation sprint on files nobody touched."""
    _stage(repo, "background/beta.py", (repo / "background" / "beta.py").read_text())
    assert not [f for f in _findings(repo) if f.path == "tools/alpha.py"]


def test_a_renamed_file_that_also_grew_still_fires_rule_3(repo: Path) -> None:
    """Rule 3 reads its prior count BY PATH out of `head_lines`, so a file arriving via `git mv`
    was not in it and the rule -- the one whose whole purpose is that the ratchet DRAINS debt --
    was silently switched off for exactly the commits that move code around. The identical
    blindness rule 2b lost on 2026-08-10, in the opposite direction: 2b was too STRICT on a
    rename, 3 was too LAX. Landed from
    `WORKER_FINDING_RULE_3_HAS_THE_SAME_RENAME_BLINDNESS_2026-08-10.md`.

    Rule 1 cannot cover this: the new path has no frozen baseline entry, so if rule 3 were merely
    rule 1 reused the growth would go through unremarked -- which is what KNIFE3 step 10's own
    rename-plus-28-lines did.
    """
    _run(repo, "mv", "tools/alpha.py", "background/moved_alpha.py")
    grown = (repo / "background" / "moved_alpha.py").read_text() + "    x = 1\n"
    _stage(repo, "background/moved_alpha.py", grown)

    assert gate.staged_renames(repo) == {"background/moved_alpha.py": "tools/alpha.py"}, (
        "precondition: git's own -M detection must see the move -- a filename heuristic must "
        "never be what makes this safe"
    )
    hits = [f for f in _findings(repo) if f.rule == size_ratchet.RULE_TOUCHED_FILE_GREW]
    assert [h.path for h in hits] == ["background/moved_alpha.py"]
    assert hits[0].ceiling == 41, "the prior count must be resolved through the OLD path at HEAD"
    assert hits[0].actual == 42


def test_a_pure_rename_is_not_growth(repo: Path) -> None:
    """The vacuity guard on the test above, and the half that makes the fix a fix rather than a
    new false-positive generator: a move with zero content change must stay green. A rename is
    not growth, and resolving the prior count through the rename map is what makes both readings
    -- fires on +1 line, clears on +0 -- come from the same rule.
    """
    _run(repo, "mv", "tools/alpha.py", "background/moved_alpha.py")
    _run(repo, "add", "-A", "tools", "background")

    assert gate.staged_renames(repo) == {"background/moved_alpha.py": "tools/alpha.py"}
    assert not [f for f in _findings(repo) if f.rule == size_ratchet.RULE_TOUCHED_FILE_GREW], (
        "a pure rename changed no code and must not read as growth"
    )


# ------------------------------------------------------------------------------ 6. the override
def test_override_clears_its_own_growth_and_nothing_else(repo: Path, monkeypatch) -> None:
    original = (repo / "tools" / "alpha.py").read_text()
    grown = original + "    z = 3\n" * 10
    _stage(repo, "tools/alpha.py", grown)
    authorised = len(grown.splitlines())

    monkeypatch.setattr(gate, "active_overrides", lambda: {})
    assert _gate(repo, "gate") == 1

    monkeypatch.setattr(gate, "active_overrides", lambda: {"tools/alpha.py": authorised})
    assert _gate(repo, "gate") == 0, "a logged override scoped to this count must clear it"

    # ... and is scoped to THAT count: grow further and the same override must no longer cover it.
    _stage(repo, "tools/alpha.py", grown + "    z = 4\n" * 5)
    assert _gate(repo, "gate") == 1, "an override must not become a standing per-file exemption"


def test_an_unreadable_decision_log_grants_no_override(repo: Path, monkeypatch) -> None:
    """FAIL-SILENT killer: if the override source is unavailable the gate must get STRICTER."""
    def boom() -> list:
        raise OSError("decision log unreadable")

    monkeypatch.setattr("background.decision_log.read_decision_log", boom)
    assert gate.active_overrides() == {}


def test_override_parsing_reads_path_and_count_from_the_logged_entry(monkeypatch) -> None:
    entries = [
        {"what": f"{gate.OVERRIDE_PREFIX} tools/alpha.py @ 120", "why": "w", "how_to_reverse": "r"},
        {"what": f"{gate.OVERRIDE_PREFIX} tools/alpha.py @ 90", "why": "w", "how_to_reverse": "r"},
        {"what": "some unrelated decision", "why": "w", "how_to_reverse": "r"},
    ]
    monkeypatch.setattr("background.decision_log.read_decision_log", lambda: entries)
    assert gate.active_overrides() == {"tools/alpha.py": 120}


# --------------------------------------------------------- 7. warn/gate share ONE detection path
def test_rollout_state_changes_only_the_exit_code_never_the_detection(repo: Path) -> None:
    """Proves warn and gate are a blocking toggle, not two divergently-buggy detectors."""
    _stage(repo, "tools/alpha.py", (repo / "tools" / "alpha.py").read_text() + "    z = 3\n" * 10)
    detected = [f.as_dict() for f in _findings(repo)]
    assert detected

    assert _gate(repo, "warn") == 0
    warn_view = [f.as_dict() for f in _findings(repo)]
    assert _gate(repo, "gate") == 1
    gate_view = [f.as_dict() for f in _findings(repo)]
    assert warn_view == gate_view == detected


# ------------------------------------------------------------------- FAIL-CLOSED (R15 killers)
@pytest.mark.parametrize("state", ["warn", "gate"])
def test_a_missing_baseline_refuses_in_both_states(repo: Path, state: str) -> None:
    """An unavailable check is a FAILED check -- and the warn rail must not swallow it. The warn
    rail absorbs false positives from the RULES; it must never absorb the ratchet being broken."""
    _stage(repo, "tools/alpha.py", (repo / "tools" / "alpha.py").read_text() + "x = 1\n")
    bp = repo / "baseline.json"
    data = json.loads(bp.read_text())
    data["rollout_state"] = state
    bp.write_text(json.dumps(data))
    bp.unlink()
    assert gate.run(repo, bp) == 1


@pytest.mark.parametrize(
    "payload", ["{ not json", json.dumps({"files": {}}), json.dumps({"files": {}, "clone_ceiling": 1,
               "rollout_state": "banana", "scope_roots": []})]
)
def test_a_corrupt_baseline_refuses(repo: Path, payload: str) -> None:
    _stage(repo, "tools/alpha.py", (repo / "tools" / "alpha.py").read_text() + "x = 1\n")
    bp = repo / "baseline.json"
    bp.write_text(payload)
    assert gate.run(repo, bp) == 1


def test_an_unparseable_source_file_refuses_rather_than_shrinking_the_clone_count(repo: Path) -> None:
    """The nastiest fail-open available here: a file that cannot be parsed contributes no
    fingerprints, so a silently-skipping census reports the clone count FALLING at the exact moment
    the tree became unreadable. It must raise instead."""
    _stage(repo, "tools/broken.py", "def oops(:\n  pass\n")
    with pytest.raises(size_ratchet.RatchetUnavailable):
        size_ratchet.census_at(None, project_dir=repo)
    assert gate.run(repo, repo / "baseline.json") == 1


def test_an_empty_scope_scan_refuses(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    (empty / "tools").mkdir(parents=True)
    _run(empty, "init", "-q")
    _run(empty, "config", "user.email", "t@t.t")
    _run(empty, "config", "user.name", "t")
    (empty / "README").write_text("x")
    _run(empty, "add", "-A")
    _run(empty, "commit", "-qm", "x")
    with pytest.raises(size_ratchet.RatchetUnavailable):
        size_ratchet.census_at(None, project_dir=empty)


def test_the_ceiling_is_not_derived_from_the_thing_it_checks(repo: Path) -> None:
    """TAUTOLOGY killer. Hold the baseline FIXED and move only the tree: the verdict must flip.

    A gate that re-derived its ceiling from the same live census it is checking would pass forever
    -- exactly the pattern R15 names, and one this project has already found twice INSIDE tests
    written against R15.
    """
    before = json.loads((repo / "baseline.json").read_text())["clone_ceiling"]
    _stage(repo, "tools/dup.py", _clone_body("g_two"))
    after = json.loads((repo / "baseline.json").read_text())["clone_ceiling"]
    assert before == after, "running the gate must never rewrite its own ceiling"
    assert [f for f in _findings(repo) if f.rule == size_ratchet.RULE_CLONE_CEILING]


# ------------------------------------------------------------ the ratchet's own anti-duplication
def test_sp3_does_not_ship_a_rival_clone_detector() -> None:
    """SP3 must CONSUME `background/shared_primitive_census.py`'s detector, never grow its own.

    Two AST clone detectors in one repo would be the 92nd-register pattern committed by the very
    atom meant to stop it, and would let SP3's ceiling and SP5's register drift into two
    incompatible definitions of the same word. This fails if the fingerprinting comes home.
    """
    src = (ROOT / "tools" / "size_ratchet.py").read_text(encoding="utf-8")
    assert "shared_primitive_census" in src, "the detector must be imported, not reimplemented"
    for smell in ("sha256", "hashlib", "def _function_shape", "fingerprint ="):
        assert smell not in src, f"SP3 looks like it grew its own detector ({smell!r})"


def test_freeze_is_lower_only_and_never_absorbs_growth(repo: Path) -> None:
    """The asymmetry that MAKES it a ratchet: re-freezing may tighten a ceiling, never loosen one.

    If a re-freeze could raise a ceiling, every growth would be one `--freeze` away from becoming
    the new normal and the mechanism would be decorative.
    """
    bp = repo / "baseline.json"
    frozen = json.loads(bp.read_text())["files"]["tools/alpha.py"]

    _stage(repo, "tools/alpha.py", (repo / "tools" / "alpha.py").read_text() + "    z = 3\n" * 10)
    _run(repo, "commit", "-qm", "grow")
    gate.freeze(repo, bp)
    assert json.loads(bp.read_text())["files"]["tools/alpha.py"] == frozen, "growth was absorbed"

    _stage(repo, "tools/alpha.py", "def a():\n    x = 1\n")
    _run(repo, "commit", "-qm", "shrink")
    gate.freeze(repo, bp)
    assert json.loads(bp.read_text())["files"]["tools/alpha.py"] == 2, "a shrink must tighten it"


def test_a_deleted_file_stays_in_the_snapshot_for_audit_but_cannot_violate(repo: Path) -> None:
    _run(repo, "rm", "-q", "tools/alpha.py")
    gate.freeze(repo, repo / "baseline.json")
    data = json.loads((repo / "baseline.json").read_text())
    assert "tools/alpha.py" in data["files"]
    assert gate.run(repo, repo / "baseline.json") == 0


def test_out_of_scope_paths_are_not_governed() -> None:
    assert size_ratchet.in_scope("tools/x.py")
    assert not size_ratchet.in_scope("tests/tools/test_x.py")
    assert not size_ratchet.in_scope("tools/test_x.py")
    assert not size_ratchet.in_scope("site/x.js")
    assert not size_ratchet.in_scope("docs/x.py")
    assert not size_ratchet.in_scope("tools/__pycache__/x.py")


def test_a_commit_touching_nothing_in_scope_costs_nothing(repo: Path) -> None:
    (repo / "notes.md").write_text("hello")
    _run(repo, "add", "notes.md")
    assert gate.run(repo, repo / "baseline.json") == 0
    assert gate.run(repo, repo / "missing-baseline.json") == 0, (
        "an out-of-scope commit must short-circuit before the baseline is even read"
    )
