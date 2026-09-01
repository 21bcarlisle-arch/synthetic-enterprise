"""R15 on the provenance-integrity guard, both ways, driven rather than asserted.

THE DEFECT, stated at the accuracy the evidence supports (R9), because the first telling of it
was wider than the facts:

  * ESTABLISHED -- commit `d4d1a04e6` (2026-08-10 17:15) published, and pushed to origin,
    `showing_run.run_id = "run_output_abc1234_20260621T104002Z.json"`. `abc1234` is the standard
    fixture sha in this repo's publisher tests, and `git cat-file` confirms it names no commit.
    A fabricated run id WAS, for a period, the public claim about how current poesys.net was.
    Mechanism: `tests/conftest.py` already records it -- the decoupling made `_process()` stamp
    this file, so ordinary publisher tests driving `_process()` wrote the REAL surface.

  * NOT ESTABLISHED -- the 08:58Z log line `showing run run_verified.json`. Every commit that
    ever touched the provenance was searched; NONE carries that value. It reached the LOG (the
    banner line is rendered from in-memory state before the commit, and the file was rewritten
    in between) and there is no evidence it reached origin. Reporting it as published was an
    overstatement, corrected here rather than left standing.

Note which of the two the shape check alone would have missed: `run_output_abc1234_...json` is
REAL-SHAPED and matches the run-id regex. Only the commit-EXISTENCE check refuses it. That is the
whole argument for asking git rather than only asking a regex.

The guard asserts on the VALUE, not on the writer, because the writer is NOT ESTABLISHED. So the
question this file must answer is not "did we stop the known caller" but "can a value that could
not have come from a run reach a published surface" -- and the answer has to be no for values
nobody has thought of yet, which is why the shape check carries the weight and the named
vocabulary is only belt-and-braces.

  * FIRES   -- the exact literal that reached origin; a fixture sha; a real-SHAPED sha that
               names no commit; a malformed stamp; and the recorder refuses at the write.
  * SILENT  -- the genuine live state, and a legitimately-empty state on a fresh machine.
  * FAIL-CLOSED -- an unavailable git reads as "not a real commit", never as a pass.
  * MUTATION -- with the guard removed the fixture publishes, which is what makes the pass above
               mean something.
"""
from __future__ import annotations

import subprocess

import pytest

from background import process_run_complete as prc
from background import publish_provenance as prov
from background import tree_lock as _tree_lock


@pytest.fixture(autouse=True)
def _origin_is_level(monkeypatch):
    """Hold the divergence read at "level with origin" for this file.

    `git_commit_push` reads origin before it stages (2026-09-01: the publish loop's own retry was
    widening the fork it was blocked by -- see `_divergence_refusal`). Every green-cycle test below
    replaces `prc.subprocess.run` with a stub answering rc=0 and EMPTY stdout, and one builds a
    real scratch repo that has no `origin` remote at all. Both read as UNREADABLE -- correctly, an
    empty `rev-list --count` is not a zero -- so without this line these tests measure
    `behind_origin` instead of the provenance guard they are about.

    STATED, NOT NEUTERED, and this file is the one that would notice. The mutation test below
    neutralises `_provenance_is_publishable` and requires the publish to REACH `git commit`; if
    this fixture were hiding a refusal, that test could not pass. The divergence guard itself is
    proven against a real git repository in
    `test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py`, which does NOT use
    this fixture -- so pinning the read here cannot make that control green.
    """
    monkeypatch.setattr(prc, "_commits_origin_is_ahead_by", lambda: 0)


@pytest.fixture(autouse=True)
def _never_take_the_real_working_tree_lock(tmp_path, monkeypatch):
    """THE FOURTH INSTANCE OF THE SAME TRAP, and the first one that could stall another process.

    `tree_lock.LOCK_FILE` is computed at module import from the real `PROJECT_DIR`, so patching
    `prc.PROJECT_DIR` inside a test does not move it -- exactly the trap this file already patches
    around three times (`LATEST_MD`, `LAST_PUSH_FILE`, `PUBLISH_CAUSE_FILE`, each with its own
    comment). The tests below drive `_process()` end to end, which takes the WORKING-TREE LOCK.

    That lock is not a record; it is coordination state shared with every live git writer on this
    machine, and a test holding it serialises real publishes behind a fixture. It surfaced on
    2026-08-31 when `docs/observability` became a protected surface -- the guard refused the write
    and the failure said, correctly, that a test was reaching into production.
    """
    monkeypatch.setattr(_tree_lock, "LOCK_FILE", tmp_path / ".tree.lock")


#: The two fields `record_verified` writes on every stamp since 2026-08-31. Declared once, so the
#: shape of a stamp stays one fact rather than a habit repeated at each call site.
#:
#: `population` is what makes the page checkable against the run it names, and `run_retained` says
#: whether that run can be opened at all. The measurement that forced both: the live page published
#: `verification_state: "verified"` naming a run in NO COMMIT, while the surfaces beside it had
#: drifted a month ahead of the tree's inputs.
_STAMP_EXTRAS = {"population": {"accounts": 251, "bills": 10948, "total_revenue_gbp": 801199.0},
                 "run_retained": False}


def _real_sha() -> str:
    return subprocess.run(["git", "rev-parse", "--short=9", "HEAD"], cwd=str(prc.PROJECT_DIR),
                          capture_output=True, text=True).stdout.strip()


def _stamp(run_id, sha):
    return {"run_id": run_id, "git_commit": sha,
            "generated_at": "2026-08-11T08:51:21Z", "verified_at": "2026-08-11T08:51:21Z",
            **_STAMP_EXTRAS}


def _state(run_id, sha):
    s = _stamp(run_id, sha)
    return {"verification_state": "verified", "showing_run": s, "last_verified": s,
            "paused_since": None}


# ----------------------------------------------------------------- FIRES

def test_it_fires_on_the_literal_that_actually_reached_origin():
    """The regression test for the observed incident, by its own value."""
    v = prov.publishable_violations(_state("run_verified.json", "v" * 40),
                                    repo_root=prc.PROJECT_DIR)
    assert v, "the fixture that was published to origin is considered publishable"
    assert any("run_verified.json" in x for x in v)


def test_it_fires_on_a_real_shaped_sha_that_names_no_commit():
    """The subtle half. A value can pass every shape check and still be a lie -- this is the
    one that catches a fabricated-but-plausible provenance, and it is why existence is checked
    rather than only the regex."""
    ghost = "deadbeef1"
    v = prov.publishable_violations(_state("run_output_{}_20260811T080000Z.json".format(ghost),
                                           ghost), repo_root=prc.PROJECT_DIR)
    assert any("names no commit" in x for x in v), v


@pytest.mark.parametrize("run_id", [
    "run_verified.json", "abc1234", "", None, 12345,
    "run_output_.json", "run_output_zzzz_20260811T080000Z.json",
    "run_output_3cc852aff_notadate.json", "../../etc/passwd",
])
def test_it_fires_on_every_run_id_a_run_could_not_have_produced(run_id):
    v = prov.publishable_violations({"showing_run": {"run_id": run_id, "git_commit": _real_sha()}},
                                    repo_root=prc.PROJECT_DIR)
    assert v, "publishable: {!r}".format(run_id)


def test_the_recorder_refuses_at_the_write(tmp_path):
    """Loud at the moment it happens, not merely blocked later at the commit."""
    with pytest.raises(prov.ProvenanceRefused):
        prov.record_verified(run_id="run_verified.json", git_commit="v" * 40,
                             path=tmp_path / "p.json")


def test_the_commit_chokepoint_refuses_and_says_why(tmp_path, monkeypatch):
    """The RED-cycle chokepoint: `_commit_and_push_paths`, which serves the banner and the
    liveness heartbeat. The refusal is proven here, and proven to be LOUD: the defect published
    in silence, and a silent refusal only moves the silence.

    This docstring used to claim the green cycle passed through here too. It did not -- see the
    green-cycle section at the end of this file, which is the wiring that makes the claim true.

    The log assertion is on `prc.log` itself rather than on captured stdout. Capturing stdout
    here would pass whether or not anything was written (an empty string satisfies a truthy
    `or`), which is the tautology this project keeps finding inside its own R15 tests."""
    root = tmp_path / "repo"
    prov_path = root / "site" / "data" / "publish_provenance.json"
    prov_path.parent.mkdir(parents=True, exist_ok=True)
    prov_path.write_text('{"showing_run": {"run_id": "run_verified.json",'
                         ' "git_commit": "vvvvvvv"}}')
    monkeypatch.setattr(prc, "PROJECT_DIR", root)

    def _explode(*a, **k):
        raise AssertionError("git was reached despite a false provenance")

    monkeypatch.setattr(prc.subprocess, "run", _explode)

    said = []
    monkeypatch.setattr(prc, "log", lambda m: said.append(str(m)))

    assert prc._commit_and_push_paths([str(prov_path)], "msg", label="Test banner") is False
    joined = "\n".join(said)
    assert said, "the refusal was SILENT -- nothing was logged"
    assert "REFUS" in joined.upper(), joined
    assert "run_verified.json" in joined, \
        "the refusal does not name the offending value, so it cannot name the cycle"


def test_the_chokepoint_ignores_commits_that_do_not_touch_the_provenance(tmp_path, monkeypatch):
    """It guards ONE file. A commit of anything else must pass through untouched -- otherwise
    this becomes a general commit gate nobody asked for, and its false positives are outages."""
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    assert prc._provenance_is_publishable([str(tmp_path / "docs" / "LATEST.md")]) is True


# ----------------------------------------------------------------- SILENT

def test_it_is_silent_on_the_genuine_live_state():
    """The control must not red the real thing. This is the anti-'always-red' half: a detector
    that fires on everything is as useless as one that fires on nothing.

    THE POPULATION STAMP IS EXEMPTED WHILE THE LIVE RECORD PREDATES IT (2026-08-31), and only
    that. On the day `population`/`run_retained` were added, the live record was one written
    before they existed — it named `run_output_5ccc0e0c8_20260831T130500Z.json`, a file in no
    commit, and said nothing whatever about it. Refusing it here would red this leg for a state
    the machine has not had a chance to rewrite yet, which is the false positive this test exists
    to prevent. Every OTHER violation is still asserted absent, so a fixture sha or a fabricated
    commit in the live record still fires, and the window closes on the next publish because
    `record_verified` cannot write a stamp without them.
    """
    live = prov.read(prov.PROVENANCE_FILE)
    violations = [v for v in prov.publishable_violations(live, repo_root=prc.PROJECT_DIR)
                  if "population is" not in v and "run_retained is unstated" not in v]
    assert violations == []


def test_a_fresh_machine_with_nothing_verified_is_publishable():
    """`showing_run is None` is what a machine that has never published looks like. Refusing it
    would wedge the first publish on every new checkout -- a control whose false positive is an
    outage."""
    assert prov.publishable_violations(
        {"verification_state": "paused", "showing_run": None, "last_verified": None},
        repo_root=prc.PROJECT_DIR) == []


def test_a_genuine_stamp_still_records():
    sha = _real_sha()
    assert prov.publishable_violations(
        _state("run_output_{}_20260809T171913Z.json".format(sha), sha),
        repo_root=prc.PROJECT_DIR) == []


# ----------------------------------------------------------------- FAIL-CLOSED

def test_an_unavailable_git_reads_as_not_real(monkeypatch):
    """R15's third pattern: an unavailable check is a FAILED check. If the repo cannot be asked,
    the answer is REFUSE -- the site stays honestly paused rather than publishing a claim
    nothing stands behind."""
    def _boom(*a, **k):
        raise OSError("git is gone")

    monkeypatch.setattr(prov.subprocess, "run", _boom)
    sha = "3cc852aff"
    v = prov.publishable_violations(
        _state("run_output_{}_20260809T171913Z.json".format(sha), sha),
        repo_root=prc.PROJECT_DIR)
    assert any("names no commit" in x for x in v), v


# ----------------------------------------------------------------- MUTATION

def test_mutation_without_the_shape_check_the_fixture_publishes(monkeypatch):
    """What makes every pass above evidence. Neuter the shape check and the literal that
    reached origin is considered publishable again -- so these tests can fail, and did."""
    monkeypatch.setattr(prov, "RUN_ID_RE", __import__("re").compile(r".*"))
    monkeypatch.setattr(prov, "COMMIT_RE", __import__("re").compile(r".*"))
    monkeypatch.setattr(prov, "_commit_exists", lambda *a, **k: True)
    monkeypatch.setattr(prov, "FIXTURE_VOCABULARY", frozenset())
    assert prov.publishable_violations(_state("run_verified.json", "v" * 40),
                                       repo_root=prc.PROJECT_DIR) == [], \
        "the mutation did not reach the checked value -- this test is not proving what it claims"


# ------------------------------------------------- THE GENERALISATION: the figures' own stamp

def test_the_live_dashboard_meta_is_publishable():
    """Anti-false-positive on the real thing: the shipped dashboard must pass."""
    import json
    meta = json.loads((prc.PROJECT_DIR / "site" / "data" / "dashboard.json").read_text())["meta"]
    assert prov.dashboard_meta_violations(meta, repo_root=prc.PROJECT_DIR) == []


@pytest.mark.parametrize("meta,why", [
    ({"source_file": "run_verified.json"}, "fixture run id"),
    ({"source_file": "run_output_abc1234_20260621T104002Z.json",
      "git_commit": "abc1234"}, "the value that actually reached origin in d4d1a04e6"),
    ({"git_commit": "deadbeef1"}, "real-shaped sha naming no commit"),
    ({"git_commit": 12345}, "not even a string"),
])
def test_it_fires_on_a_dashboard_stamped_with_a_run_that_does_not_exist(meta, why):
    """A dashboard stamped with a run that does not exist is a page of numbers attributed to
    nothing. The second case is not hypothetical -- it is the blob committed in d4d1a04e6."""
    assert prov.dashboard_meta_violations(meta, repo_root=prc.PROJECT_DIR), why


def test_the_chokepoint_guards_the_dashboard_too(tmp_path, monkeypatch):
    """The generalisation reaches the commit path, not just the validator."""
    import json as _json
    root = tmp_path / "repo"
    dash = root / "site" / "data" / "dashboard.json"
    dash.parent.mkdir(parents=True, exist_ok=True)
    dash.write_text(_json.dumps({"meta": {"source_file": "run_verified.json",
                                          "git_commit": "abc1234"}}))
    monkeypatch.setattr(prc, "PROJECT_DIR", root)
    monkeypatch.setattr(prc.subprocess, "run",
                        lambda *a, **k: (_ for _ in ()).throw(
                            AssertionError("git reached despite a false dashboard stamp")))
    said = []
    monkeypatch.setattr(prc, "log", lambda m: said.append(str(m)))
    assert prc._commit_and_push_paths([str(dash)], "msg", label="Content") is False
    assert any("source_file" in s for s in said), said


# ------------------------------------- THE GREEN CYCLE, which did not pass through the choke
#
# `test_the_commit_chokepoint_refuses_and_says_why` says, in its own docstring, "every
# provenance commit -- red-cycle banner and green-cycle content alike -- passes through
# `_commit_and_push_paths`". That was WRONG, and the tests below are what makes it true.
#
# `_commit_and_push_paths` serves two callers: the liveness heartbeat and the RED-cycle banner.
# The GREEN cycle -- `git_commit_push`, the function that commits site/data/dashboard.json and
# site/data/publish_provenance.json in one commit on every healthy run -- never called the
# checker at all. It is also the path the ESTABLISHED incident took: `d4d1a04e6` published
# `run_output_abc1234_20260621T104002Z.json` to origin from a content publish, not from a
# banner. So the guard was mounted on the cycle that did not do it.
#
# The class, stated for the next reader: a control's subject is the call sites it is wired
# into, never the sentence in its docstring. "Impossible from here" was true of the function
# it sat in and false of the publisher.


def _fake_git(calls):
    """Records every git argv and never touches a repo."""
    class _R:
        returncode = 0
        stdout = ""
        stderr = ""

    def _run(cmd, **kwargs):
        calls.append(list(cmd))
        return _R()
    return _run


def _green_cycle_tree(tmp_path, run_id, sha):
    """A tree shaped like the real one at the moment of a green publish: both published files
    present, so `git_commit_push` puts both in its commit list."""
    import json as _json
    root = tmp_path / "repo"
    (root / "site" / "data").mkdir(parents=True, exist_ok=True)
    stamp = {"run_id": run_id, "git_commit": sha,
             "generated_at": "2026-08-12T09:00:00Z", "verified_at": "2026-08-12T09:00:00Z",
             **_STAMP_EXTRAS}
    (root / "site" / "data" / "publish_provenance.json").write_text(_json.dumps(
        {"verification_state": "verified", "showing_run": stamp, "last_verified": stamp}))
    (root / "site" / "data" / "dashboard.json").write_text(_json.dumps(
        {"meta": {"source_file": run_id, "git_commit": sha}}))
    (root / "site" / "index.html").write_text("<html></html>")
    return root


def test_the_green_cycle_publish_refuses_a_false_provenance(tmp_path, monkeypatch):
    """FIRES on the path the fixture actually took. Nothing is committed and nothing is pushed:
    the report, LATEST.md and every site file stay unpublished this cycle, which is the
    fail-closed direction this whole surface is built on."""
    root = _green_cycle_tree(tmp_path, "run_verified.json", "v" * 40)
    monkeypatch.setattr(prc, "PROJECT_DIR", root)
    monkeypatch.setattr(prc, "LATEST_MD", root / "docs" / "status" / "LATEST.md")
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", root / ".last_push_time.json")
    # THE LIVE RECORD IS NOT A TEST FIXTURE (2026-08-30). `PUBLISH_CAUSE_FILE` is computed
    # at module import from the real PROJECT_DIR, so patching PROJECT_DIR afterwards does
    # not move it -- the same trap `LAST_PUSH_FILE` above is patched to avoid. Without this
    # line these tests drive the publisher into `publish_cause.record_cause` against the
    # repository's own `.last_publish_cause.json`, and `live_ledger_guard` refuses (it had
    # already let a fixture's git_hash "abc1234" reach that record before the guard landed).
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", root / ".last_publish_cause.json")
    calls = []
    monkeypatch.setattr(prc.subprocess, "run", _fake_git(calls))
    said = []
    monkeypatch.setattr(prc, "log", lambda m: said.append(str(m)))

    assert prc.git_commit_push("3abd6e1df", 1000.0) is False
    assert not calls, "git was reached despite a false provenance: {}".format(calls)
    assert any("REFUS" in s.upper() for s in said), said
    assert any("run_verified.json" in s for s in said), \
        "the refusal does not name the offending value, so it cannot name the cycle"


def test_the_green_cycle_publish_commits_a_genuine_stamp(tmp_path, monkeypatch):
    """SILENT on the real thing, driven end to end: a real run id and a sha that names a real
    commit in a real repo must publish exactly as before. Without this, the test above is
    satisfied by a guard that refuses everything -- an outage wearing a control's hat."""
    root = tmp_path / "repo"
    root.mkdir(parents=True, exist_ok=True)
    for cmd in (["git", "init", "-q"],
                ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                 "--allow-empty", "-m", "seed"]):
        subprocess.run(cmd, cwd=str(root), capture_output=True, timeout=60)
    sha = subprocess.run(["git", "rev-parse", "--short=9", "HEAD"], cwd=str(root),
                         capture_output=True, text=True, timeout=60).stdout.strip()
    assert len(sha) == 9, "the fixture repo was not created; this test would prove nothing"

    _green_cycle_tree(tmp_path, "run_output_{}_20260812T090000Z.json".format(sha), sha)
    monkeypatch.setattr(prc, "PROJECT_DIR", root)
    monkeypatch.setattr(prc, "LATEST_MD", root / "docs" / "status" / "LATEST.md")
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", root / ".last_push_time.json")
    # THE LIVE RECORD IS NOT A TEST FIXTURE (2026-08-30). `PUBLISH_CAUSE_FILE` is computed
    # at module import from the real PROJECT_DIR, so patching PROJECT_DIR afterwards does
    # not move it -- the same trap `LAST_PUSH_FILE` above is patched to avoid. Without this
    # line these tests drive the publisher into `publish_cause.record_cause` against the
    # repository's own `.last_publish_cause.json`, and `live_ledger_guard` refuses (it had
    # already let a fixture's git_hash "abc1234" reach that record before the guard landed).
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", root / ".last_publish_cause.json")
    calls = []
    monkeypatch.setattr(prc.subprocess, "run", _fake_git(calls))

    prc.git_commit_push(sha, 1000.0)
    assert any(c[:2] == ["git", "commit"] for c in calls), \
        "a genuine stamp did not publish -- the guard is refusing the healthy cycle"


def test_the_green_cycle_refusal_is_the_guards_doing(tmp_path, monkeypatch):
    """MUTATION. Neutralise the checker and the same false provenance publishes -- which is what
    makes the refusal above evidence about THIS call rather than about some other early return
    in a 300-line function."""
    root = _green_cycle_tree(tmp_path, "run_verified.json", "v" * 40)
    monkeypatch.setattr(prc, "PROJECT_DIR", root)
    monkeypatch.setattr(prc, "LATEST_MD", root / "docs" / "status" / "LATEST.md")
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", root / ".last_push_time.json")
    # THE LIVE RECORD IS NOT A TEST FIXTURE (2026-08-30). `PUBLISH_CAUSE_FILE` is computed
    # at module import from the real PROJECT_DIR, so patching PROJECT_DIR afterwards does
    # not move it -- the same trap `LAST_PUSH_FILE` above is patched to avoid. Without this
    # line these tests drive the publisher into `publish_cause.record_cause` against the
    # repository's own `.last_publish_cause.json`, and `live_ledger_guard` refuses (it had
    # already let a fixture's git_hash "abc1234" reach that record before the guard landed).
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", root / ".last_publish_cause.json")
    monkeypatch.setattr(prc, "_provenance_is_publishable", lambda *a, **k: True)
    calls = []
    monkeypatch.setattr(prc.subprocess, "run", _fake_git(calls))

    prc.git_commit_push("3abd6e1df", 1000.0)
    assert any(c[:2] == ["git", "commit"] for c in calls), \
        "the mutation did not reach the publish -- this pair is not proving what it claims"


# ---------------------------------------------------------------------------
# ONE GENERATION PER CYCLE (2026-09-01)
# ---------------------------------------------------------------------------
# The guard above asks whether a stamp's VALUES could have come from a run. This asks something
# the value check structurally cannot: whether the code that WROTE the stamp and the code that
# JUDGED it came from the same version of this repository.
#
# MEASURED, not hypothesised. On 2026-09-01 a publisher process started at 02:40 UTC from
# main at d95c659e3, whose `record_verified` call site passed no `population`. At 02:49 the
# merge d9b9dd2f3 brought 31def55aa onto main, rewriting BOTH `publish_provenance` (population
# now REQUIRED) and the publisher's call site (population now SUPPLIED). At 03:05 that
# still-running 02:40 process executed a function-scope `from background import
# publish_provenance` and got the 02:49 module. Old call site, new checker:
#
#   "Provenance stamp skipped (non-fatal): REFUSING TO PUBLISH A FALSE PROVENANCE --
#    showing_run.population is missing"
#
# followed by `Commit/push failed (provenance_refused)` and a wedged publish gate. Nothing in
# the tree was wrong and the scoped suite was green, so it read as a self-clearing wedge and
# repeated. A ~25-minute publish cycle in a tree several lanes land into makes this ordinary,
# not exotic.
#
# `sys.modules` caches on first import, so WHERE the first import happens decides which
# generation the whole process gets. At module scope it is pinned to the process's own
# generation; inside the publish path it is whatever the tree holds 25 minutes later.
#
#   * FIRES   -- a function-scope import of the provenance module (the shape that was live).
#   * SILENT  -- the current source.
#   * VACUITY -- a source that imports it NOWHERE fails too, so deleting the binding cannot
#                buy a pass.


def _function_scope_imports_of(source: str, module: str) -> list:
    """Line numbers where `module` is imported INSIDE a function/class body, not at module scope.

    Driven rather than asserted: the same function is run below against a source known to carry
    the defect, so a pass here is evidence the check can see it."""
    import ast

    tree = ast.parse(source)
    module_scope = {id(n) for n in ast.walk(tree) if isinstance(n, ast.Module)}
    del module_scope
    nested = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.ImportFrom) and inner.module == "background":
                if any(a.name == module for a in inner.names):
                    nested.append(inner.lineno)
            elif isinstance(inner, ast.ImportFrom) and inner.module == "background." + module:
                nested.append(inner.lineno)
            elif isinstance(inner, ast.Import):
                if any(a.name in (module, "background." + module) for a in inner.names):
                    nested.append(inner.lineno)
    return sorted(set(nested))


def _module_scope_imports(source: str, module: str) -> bool:
    import ast

    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "background":
            if any(a.name == module for a in node.names):
                return True
        if isinstance(node, ast.ImportFrom) and node.module == "background." + module:
            return True
        if isinstance(node, ast.Import):
            if any(a.name in (module, "background." + module) for a in node.names):
                return True
    return False


def _publisher_source() -> str:
    from pathlib import Path

    return Path(prc.__file__).read_text()


def test_the_checker_sees_a_function_scope_import():
    """FIRES. The exact shape that was live at 03:05 on 2026-09-01, so the silence below is
    evidence about the source rather than about a checker that finds nothing anywhere."""
    defective = (
        "from background import publish_cause\n"
        "def _process():\n"
        "    from background import publish_provenance as _prov\n"
        "    return _prov\n"
    )
    assert _function_scope_imports_of(defective, "publish_provenance") == [3]
    assert not _module_scope_imports(defective, "publish_provenance"), \
        "the defective fixture must not also carry the module-scope binding, or it proves nothing"


def test_the_publisher_binds_one_generation_of_its_provenance_module():
    """SILENT on the current source, and NOT VACUOUSLY: the module-scope binding must exist.

    Keyed to the property (the process uses one generation of the module it is judged by), not
    to today's line numbers -- a new lazy import anywhere in the file turns this red, and
    deleting the binding altogether does too."""
    source = _publisher_source()
    nested = _function_scope_imports_of(source, "publish_provenance")
    assert not nested, (
        "background/process_run_complete.py imports publish_provenance inside a function body "
        "at line(s) {} -- a publish cycle runs ~25 minutes in a tree other lanes land into, so "
        "this binds whatever generation the tree holds at the moment the publish path is "
        "reached, which on 2026-09-01 paired an old call site with a new checker and wedged "
        "the publish gate. Import it at module scope.".format(nested))
    assert _module_scope_imports(source, "publish_provenance"), (
        "no module-scope binding of publish_provenance -- the check above is then vacuous, and "
        "the publisher has no pinned generation of the module that judges its own stamps")
