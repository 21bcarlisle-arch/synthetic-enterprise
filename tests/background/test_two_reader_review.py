"""The two-reader lane: it selects only module-adding commits, records both verdicts, files only
what both readers raised, and fails closed when a reader breaks format."""
import json

import pytest

from background import two_reader_review as tr

SHA = "a" * 40


def _reading(verdict, *findings):
    body = {"verdict": verdict, "findings": [
        {"id": i, "severity": sev, "file": "tools/x.py", "line": 10 * i, "claim": claim}
        for i, sev, claim in findings]}
    return f"prose before\n```json\n{json.dumps(body)}\n```\n"


def test_selection_admits_a_new_module_and_refuses_a_test_or_a_doc():
    """Defect caught: a selector that admits every commit (the ruling's feared spend) or none."""
    log = "\n".join([
        "@" + "1" * 40 + " 2026-10-27T10:00:00+00:00", "tools/new_thing.py",
        "@" + "2" * 40 + " 2026-10-27T11:00:00+00:00", "tests/tools/test_new_thing.py",
        "@" + "3" * 40 + " 2026-10-27T12:00:00+00:00", "docs/staging/X.md", "background/conftest.py",
        "@" + "4" * 40 + " 2026-10-27T13:00:00+00:00", "simulation/a.py", "simulation/test_a.py",
    ])
    got = tr.qualifying_commits(git=lambda *a: log)
    assert [c["sha"][0] for c in got] == ["1", "4"]
    assert got[1]["modules"] == ["simulation/a.py"]


def test_a_reading_on_origin_counts_when_the_shared_tree_lags(monkeypatch, tmp_path):
    """Defect caught: a lagging working tree makes the lane buy a reading origin already holds."""
    (tmp_path / "ledger.json").write_text("[]")
    monkeypatch.setattr(tr.tl, "LEDGER_PATH", tmp_path / "ledger.json")
    origin = json.dumps([{"subject": f"reading-review-live-2026-10-28:{SHA[:10]}:arm{a}"} for a in "AB"])
    entries = tr._ledger_entries(git=lambda *a: origin)
    assert tr._is_read(SHA, tr.read_shas(entries))
    assert not tr._is_read(SHA, tr.read_shas(entries[:1]))       # one arm is not a reading


def test_queue_partition_reaches_read_waiting_and_given_up():
    commits = [{"sha": c * 40, "committed": "", "modules": ["m.py"]} for c in "abc"]
    attempts = {"c" * 40: [{"outcome": "unreadable"}] * tr.MAX_ATTEMPTS}
    q = tr.queue(commits, {"a" * 10}, attempts)
    assert q["read"] and q["waiting"] and q["given_up"]
    assert [c["sha"][0] for c in q["waiting"]] == ["b"]


def test_a_reader_that_breaks_format_is_refused_not_read_as_a_pass():
    """Defect caught: an unparseable reader counted as PASS with no findings."""
    assert tr.parse_reading("I looked and it seems fine.") is None
    assert tr.parse_reading('```json\n{"verdict": "LGTM"}\n```') is None
    assert tr.parse_reading('```json\n{"verdict": "NEEDS_WORK", "findings": [{"id": 1}]}\n```') is None
    ok = tr.parse_reading(_reading("NEEDS_WORK", (1, "major", "wrong")))
    assert ok["findings"][0]["severity"] == "MAJOR"
    assert tr.parse_reading(_reading("PASS")) == {"verdict": "PASS", "findings": []}


def test_the_matcher_cannot_invent_an_id_or_pair_one_twice():
    a = [{"id": 1}, {"id": 2}]
    b = [{"id": 7}]
    assert tr.valid_pairs({"pairs": [[1, 7], [2, 7], [3, 7], [1, 9]]}, a, b) == [(1, 7)]
    assert tr.valid_pairs("nonsense", a, b) == []


@pytest.fixture
def lane(monkeypatch, tmp_path):
    def fake_extract(sha, dest):
        (dest / "tree").mkdir(parents=True)
        (dest / "packet").mkdir()
    monkeypatch.setattr(tr, "_extract", fake_extract)
    monkeypatch.setattr(tr, "SCRATCH_ROOT", tmp_path / "scratch")
    recorded = []
    staging = tmp_path / "staging"
    staging.mkdir()

    def run(outputs, matcher='```json\n{"pairs": [[1, 2]]}\n```'):
        calls = iter(outputs + [matcher])

        def claude(prompt, cwd, tools, timeout):
            out = next(calls)
            return (0, out) if isinstance(out, str) else out
        commit = {"sha": SHA, "committed": "2026-10-28T10:00:00+00:00", "modules": ["tools/x.py"]}
        rec = tr.read_commit(commit, claude=claude, staging=staging,
                             readings=tmp_path / "readings.jsonl",
                             record=lambda *a, **k: recorded.append((a, k)))
        return rec, recorded, sorted(staging.iterdir())
    return run


def test_both_verdicts_are_recorded_and_only_a_shared_finding_is_filed(lane):
    """Partition control: a shared pair files, and no shared pair files nothing. A lane that filed
    every finding, or none, fails one of the two."""
    rec, recorded, filed = lane([_reading("NEEDS_WORK", (1, "BLOCKING", "opening read cannot fail")),
                                 _reading("NEEDS_WORK", (1, "MINOR", "style"),
                                          (2, "BLOCKING", "INV_OPENING_READ is CLEAN by construction"))])
    assert rec["outcome"] == "read" and rec["pairs"] == [(1, 2)]
    subjects = [a[3] for a, _k in recorded]
    assert [s.split(":", 1)[1] for s in subjects] == [f"{SHA[:10]}:armA", f"{SHA[:10]}:armB"]
    assert tr._is_read(SHA, tr.read_shas([{"subject": s} for s in subjects]))   # the lane sees its own
    assert all(a[1] == "needs_work" and a[2] == "phase-close-evaluator" for a, _k in recorded)
    assert len(filed) == 1
    text = filed[0].read_text()
    assert text.startswith("**Severity:** MAJOR")          # an unchecked vote is capped below BLOCKING
    assert "B#1 (MINOR): style" in text                     # what the vote discarded stays visible


def test_no_shared_finding_records_both_verdicts_and_files_nothing(lane):
    rec, recorded, filed = lane([_reading("NEEDS_WORK", (1, "MAJOR", "x")),
                                 _reading("PASS", (2, "MINOR", "y"))],
                                matcher='```json\n{"pairs": []}\n```')
    assert rec["outcome"] == "read" and rec["pairs"] == []
    assert [a[1] for a, _k in recorded] == ["needs_work", "pass"]
    assert filed == []


def test_a_broken_reader_records_no_verdict_and_logs_the_attempt(lane, tmp_path):
    """Defect caught: half a reading recorded as one arm's verdict, which read_shas would then
    never see completed, or a failure that leaves no trace and retries forever."""
    rec, recorded, filed = lane([_reading("PASS"), (124, "timed out after 1500s")])
    assert rec["outcome"] == "unreadable" and rec["arm"] == "B"
    assert recorded == [] and filed == []
    assert len(tr._attempts(tmp_path / "readings.jsonl")[SHA]) == 1


def test_the_tick_spawns_nothing_when_the_dial_holds_it(monkeypatch):
    monkeypatch.setattr(tr, "qualifying_commits", lambda: pytest.fail("held tick must not select"))
    assert tr.tick(gate=lambda route: (False, "off", "tick mode off")).startswith("held")


def test_the_route_is_registered_with_the_dial():
    """Defect caught: a token-spending route the director's `off` cannot reach."""
    from background import tick_mode
    assert tr.ROUTE in tick_mode.ROUTES


def test_a_matcher_that_answers_in_prose_is_a_failed_match_not_no_pairs(lane, tmp_path):
    """Defect caught (both blind readers, on the lane's own first commit c89a199faf): rc 0 with no
    json read as `pairs: []`, so both verdicts were recorded and the commit left the queue with
    nothing filed, for good."""
    rec, recorded, filed = lane([_reading("NEEDS_WORK", (1, "MAJOR", "x")),
                                 _reading("NEEDS_WORK", (2, "MAJOR", "x"))],
                                matcher="These two look like the same defect to me.")
    assert rec["outcome"] == "matcher_failed"
    assert recorded == [] and filed == []
    assert len(tr._attempts(tmp_path / "readings.jsonl")[SHA]) == 1


def test_an_exception_mid_reading_is_logged_as_an_attempt(monkeypatch, tmp_path):
    """Defect caught (both blind readers, c89a199faf): an exception skipped the log, so MAX_ATTEMPTS
    never counted it and the timer retried the same commit for ever."""
    def broken_extract(sha, dest):
        raise RuntimeError("git archive failed")
    monkeypatch.setattr(tr, "_extract", broken_extract)
    monkeypatch.setattr(tr, "SCRATCH_ROOT", tmp_path / "scratch")
    commit = {"sha": SHA, "committed": "", "modules": ["tools/x.py"]}
    rec = tr.read_commit(commit, claude=lambda *a: pytest.fail("no reader without a tree"),
                         record=lambda *a, **k: pytest.fail("no verdict"),
                         staging=tmp_path, readings=tmp_path / "readings.jsonl")
    assert rec["outcome"] == "error" and "git archive failed" in rec["error"]
    assert len(tr._attempts(tmp_path / "readings.jsonl")[SHA]) == 1
    assert list((tmp_path / "scratch").iterdir()) == []      # the extract is removed either way
