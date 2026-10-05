"""The C29 retention-guard arm refuses an arm it does not know, by name, before any run starts.

An arm name mistyped into a launch line would otherwise run the default policy for an hour and
write an artefact labelled as whichever arm was meant.
"""
from __future__ import annotations

from tools import _c29_retention_engagement_arm as arm


def test_an_unknown_arm_is_refused_by_name_and_writes_nothing(tmp_path, monkeypatch, capsys):
    out = tmp_path / "arm.json"
    monkeypatch.setattr("sys.argv", ["arm", "onn", str(out)])
    assert arm.main() == 2
    assert "unknown arm 'onn'" in capsys.readouterr().out
    assert not out.exists()
