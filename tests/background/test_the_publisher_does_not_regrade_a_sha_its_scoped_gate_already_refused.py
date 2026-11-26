"""The publisher does not re-grade a HEAD its own scoped gate already graded red.

THE DEFECT (finding 2026-10-13; seen again 2026-11-26, b1399c108 graded red at 18:24Z and 19:12Z).
The scoped gate's subject is a clean checkout of HEAD, so a re-grade at an unchanged sha reads the
same bytes and returns the same red -- while holding the run lock `origin_reconcile` stands down
for. The re-grade cannot change the verdict and costs the one advance that can.

ONE CONTROL OVER THE PARTITION, so a publisher that defers everything fails it as surely as one
that defers nothing:
  * scoped red recorded at HEAD           -> DEFERRED, no suite, cause recorded as UNJUDGED
  * scoped red recorded at an older sha   -> graded (HEAD moved: that is what re-grades)
  * hook-chain red at HEAD                -> graded (its subject was HEAD plus the publish's writes)
  * scoped red at HEAD but past max age   -> graded (bounds a red from the live box, not the tree)
"""
import contextlib
import json
import time

import background.process_run_complete as prc
import background.publish_cause as pc
from tests.background.publish_gate_root_shape import materialise_repo_shaped_root

HEAD = "de3138e6d037235d853d77689c75a4e8cac69959"
OLDER = "b1399c1083aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def _record(path, graded, census=prc.CENSUS_COMPLETE, age_s=60):
    path.write_text(json.dumps({
        "ts": time.time() - age_s, "git_hash": "76f894811d", "graded_sha": graded,
        "census": census, "total_red": 1, "fork_behind": 0, "fork_ahead": 0,
        "node_ids": ["tests/x.py::test_red"]}))


def _drive(monkeypatch, tmp_path, name, **rec):
    blocking = tmp_path / (name + ".json")
    _record(blocking, **rec)
    monkeypatch.setattr(prc, "GATE_BLOCKING_TESTS_FILE", blocking)
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    monkeypatch.setattr(prc, "PUBLISH_CAUSE_FILE", tmp_path / (name + "_cause.json"))
    monkeypatch.setattr(prc, "_head_sha", lambda: HEAD)
    ran = []

    def _suite(head_dir, full_env, git_hash):
        ran.append(git_hash)
        return False, False

    @contextlib.contextmanager
    def _checkout():
        yield materialise_repo_shaped_root(tmp_path / ("head_" + name))

    monkeypatch.setattr(prc, "_run_gate_in", _suite)
    monkeypatch.setattr(prc, "_repair_derived_artefacts_in", lambda head_dir: None)
    monkeypatch.setattr(prc, "_head_checkout", _checkout)
    verdict = prc.run_fast_tests("76f894811d")
    cause_file = tmp_path / (name + "_cause.json")
    cause = json.loads(cause_file.read_text()) if cause_file.exists() else None
    return verdict, bool(ran), cause


def test_only_a_scoped_red_at_the_unmoved_head_defers(monkeypatch, tmp_path):
    cases = {
        "same_sha": dict(graded=HEAD),
        "short_same_sha": dict(graded=HEAD[:10]),
        "head_moved": dict(graded=OLDER),
        "hook_chain": dict(graded=HEAD, census=prc.CENSUS_HOOK_CHAIN),
        "stale": dict(graded=HEAD, age_s=prc.GATE_BLOCKING_TESTS_MAX_AGE_SECONDS + 60),
    }
    out = {name: _drive(monkeypatch, tmp_path, name, **rec) for name, rec in cases.items()}
    graded = {name for name, (_, ran, _) in out.items() if ran}

    # The partition: both branches are reachable, and each case lands on its own side.
    assert graded == {"head_moved", "hook_chain", "stale"}, graded

    for name in ("same_sha", "short_same_sha"):
        verdict, _, cause = out[name]
        assert verdict == (False, False), "a deferral must never read as a pass"
        assert cause is not None, "the deferral recorded no cause"
        assert pc.SCOPED_GATE_UNJUDGED in json.dumps(cause), cause
        assert HEAD[:10] in json.dumps(cause), "the refusal does not name the sha it held at"
