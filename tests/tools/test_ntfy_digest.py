"""Phase 265 tests: maybe_ntfy notable-exception logic."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class _MockNtfy:
    def __init__(self):
        self.messages = []
    def __call__(self, msg):
        self.messages.append(msg)


def _patch_ntfy(monkeypatch, mock):
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", mock)


def _run_history_file(tmp_path, entries):
    hp = tmp_path / "run_history.json"
    hp.write_text(json.dumps(entries))
    return hp


def test_ntfy_sent_on_admin_event(monkeypatch):
    from background.process_run_complete import maybe_ntfy
    mock = _MockNtfy()
    _patch_ntfy(monkeypatch, mock)
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", mock)
    data = {"administration_event": {"date": "2021-06-30"}}
    maybe_ntfy(data, 1_000_000)
    assert len(mock.messages) == 1
    assert "ADMINISTRATION" in mock.messages[0]


def test_no_ntfy_on_normal_run(monkeypatch, tmp_path):
    from background import process_run_complete as prc
    mock = _MockNtfy()
    monkeypatch.setattr(prc, "_run_history_max_net", lambda: 6_000_000.0)
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", mock)
    data = {"administration_event": None}
    prc.maybe_ntfy(data, 6_000_000.0)
    assert len(mock.messages) == 0


def test_ntfy_sent_on_new_high(monkeypatch):
    from background import process_run_complete as prc
    mock = _MockNtfy()
    monkeypatch.setattr(prc, "_run_history_max_net", lambda: 5_000_000.0)
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", mock)
    data = {"administration_event": None}
    prc.maybe_ntfy(data, 6_500_000.0)
    assert len(mock.messages) == 1
    assert "NEW HIGH" in mock.messages[0]


def test_ntfy_sent_on_new_low(monkeypatch):
    from background import process_run_complete as prc
    mock = _MockNtfy()
    monkeypatch.setattr(prc, "_run_history_max_net", lambda: 6_000_000.0)
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", mock)
    data = {"administration_event": None}
    prc.maybe_ntfy(data, 1_000_000.0)
    assert len(mock.messages) == 1
    assert "NEW LOW" in mock.messages[0]


def test_ntfy_includes_executive_summary(monkeypatch):
    from background import process_run_complete as prc
    from dataclasses import dataclass, field
    mock = _MockNtfy()
    monkeypatch.setattr(prc, "_run_history_max_net", lambda: 5_000_000.0)
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", mock)

    @dataclass(frozen=True)
    class FakeInsights:
        executive_summary: str = "Test survived crisis."
        recommended_actions: tuple = ("Hedge more.", "Reduce I&C.", "Review costs.")

    data = {"administration_event": None}
    prc.maybe_ntfy(data, 6_500_000.0, FakeInsights())
    assert "survived" in mock.messages[0].lower()


def test_run_history_max_net_returns_zero_on_missing(tmp_path, monkeypatch):
    import background.process_run_complete as prc
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    result = prc._run_history_max_net()
    assert result == 0.0


def test_ntfy_admin_event_message_includes_date(monkeypatch):
    from background.process_run_complete import maybe_ntfy
    mock = _MockNtfy()
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", mock)
    data = {"administration_event": {"date": "2022-09-15"}}
    maybe_ntfy(data, 500_000)
    assert "2022-09-15" in mock.messages[0]


def test_high_and_low_both_send_only_one_ntfy(monkeypatch):
    from background import process_run_complete as prc
    mock = _MockNtfy()
    monkeypatch.setattr(prc, "_run_history_max_net", lambda: 5_000_000.0)
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", mock)
    data = {"administration_event": None}
    prc.maybe_ntfy(data, 6_500_000.0)
    assert len(mock.messages) == 1


def test_no_ntfy_for_same_net_as_history_max(monkeypatch):
    from background import process_run_complete as prc
    mock = _MockNtfy()
    monkeypatch.setattr(prc, "_run_history_max_net", lambda: 6_000_000.0)
    import background.ntfy_utils as nu
    monkeypatch.setattr(nu, "send_ntfy", mock)
    data = {"administration_event": None}
    prc.maybe_ntfy(data, 6_000_000.0)
    assert len(mock.messages) == 0


def test_run_history_max_net_reads_from_history_file(tmp_path, monkeypatch):
    import json as _json
    import background.process_run_complete as prc
    history = [{"net_margin_gbp": 3_000_000.0}, {"net_margin_gbp": 7_000_000.0}, {"net_margin_gbp": 2_000_000.0}]
    hist_dir = tmp_path / "docs" / "observability"
    hist_dir.mkdir(parents=True)
    (hist_dir / "run_history.json").write_text(_json.dumps(history))
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    result = prc._run_history_max_net()
    assert result == 7_000_000.0
