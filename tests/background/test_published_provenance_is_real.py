"""R15 on the provenance-integrity guard, both ways, driven rather than asserted.

THE DEFECT (2026-08-11, observed on the LIVE surface, not hypothesised):

    [08:58Z] Provenance banner: Verification paused since 2026-08-11T08:58:57Z
             . showing run run_verified.json (last verified 2026-08-11T08:58:57Z)
    [08:58Z] Provenance banner published to origin.

`run_verified.json` is a test fixture literal. A fabricated run id was, for a period, the public
claim about how current poesys.net was. Nothing flagged it.

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


def _real_sha() -> str:
    return subprocess.run(["git", "rev-parse", "--short=9", "HEAD"], cwd=str(prc.PROJECT_DIR),
                          capture_output=True, text=True).stdout.strip()


def _stamp(run_id, sha):
    return {"run_id": run_id, "git_commit": sha,
            "generated_at": "2026-08-11T08:51:21Z", "verified_at": "2026-08-11T08:51:21Z"}


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
    """Every provenance commit -- red-cycle banner and green-cycle content alike -- passes
    through `_commit_and_push_paths`, so the refusal is proven at that chokepoint, and proven
    to be LOUD: the defect published in silence, and a silent refusal only moves the silence.

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
    that fires on everything is as useless as one that fires on nothing."""
    live = prov.read(prov.PROVENANCE_FILE)
    assert prov.publishable_violations(live, repo_root=prc.PROJECT_DIR) == []


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
