"""`meter_reads.assumption_toggle` parses the register once per distinct TEXT.

A run asks ~260 times, and re-parsing the YAML on each was 45 s of one census run to 2018-09
(`docs/staging/records/SEAT_PREREG_WHERE_THE_CENSUS_GREW_AFTER_10_18_2026-10-21.md`). The cache must
not outlive an edit: a register rewritten mid-process answers with its new value.
"""
from __future__ import annotations

import simulation.meter_reads as mr


def _register(path, value):
    path.write_text(f"toggles:\n- id: t_probe\n  default: {value}\n  low: null\n"
                    f"  default_reason: a probe\n")


def test_an_edited_register_answers_with_its_new_value(tmp_path, monkeypatch):
    path = tmp_path / "toggles.yaml"
    monkeypatch.setattr(mr, "ASSUMPTION_TOGGLES_PATH", path)
    _register(path, 1.5)
    assert mr.assumption_toggle("t_probe") == 1.5
    _register(path, 2.5)
    assert mr.assumption_toggle("t_probe") == 2.5
    assert mr.assumption_toggle_or_gap("t_probe") == (2.5, None)
    assert mr.assumption_toggle_or_gap("t_probe", "low") == (None, "a probe")


def test_the_same_text_is_parsed_once(tmp_path, monkeypatch):
    path = tmp_path / "toggles.yaml"
    monkeypatch.setattr(mr, "ASSUMPTION_TOGGLES_PATH", path)
    _register(path, 3.25)
    parses = []
    real = mr.yaml.safe_load
    monkeypatch.setattr(mr.yaml, "safe_load", lambda text: parses.append(1) or real(text))
    for _ in range(5):
        assert mr.assumption_toggle("t_probe") == 3.25
        assert mr.assumption_toggle_or_gap("t_probe") == (3.25, None)
    assert len(parses) == 1
