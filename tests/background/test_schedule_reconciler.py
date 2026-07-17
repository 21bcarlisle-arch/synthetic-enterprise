"""Tests for OPS1 sub-step 3 (G-L2 for scheduling): the schedule/service manifest + reconciler.

The load-bearing one is test_injected_rogue_crontab_entry_is_caught — the invisible-cron class
that caused the blackout is now structurally detectable, forever. All actual-state is injected so
tests never touch the real crontab/systemd."""
from __future__ import annotations

import pytest

from background import schedule_reconciler as S

# A minimal manifest: no declared cron; one declared systemd unit that must be enabled+active.
MANIFEST = {
    "cron": [],
    "systemd_units": [
        {"name": "file-api.service", "unit_file": "background/file-api.service",
         "enabled": True, "active": True, "reason": "director-access infra"},
    ],
}
_OK_UNIT = {"file-api.service": {"installed": True, "enabled": True, "active": True}}


def _status(results, item):
    return next(r for r in results if r["item"] == item)


def test_injected_rogue_crontab_entry_is_caught():
    """THE cron lesson made permanent: any crontab line not declared in the manifest is
    flagged UNDECLARED_CRON — the invisible-cron that resurrected the broken stack could
    never hide from the repo again."""
    rogue = "*/30 * * * * /home/rich/synthetic-enterprise/background/start_worker.sh"
    res = S.reconcile(MANIFEST, cron_lines=[rogue], unit_states=_OK_UNIT, installed_units=["file-api.service"])
    hit = _status(res, rogue)
    assert hit["status"] == "UNDECLARED_CRON" and hit["alarm"] is True


def test_empty_declared_cron_with_no_actual_cron_is_clean():
    res = S.reconcile(MANIFEST, cron_lines=[], unit_states=_OK_UNIT, installed_units=["file-api.service"])
    assert S.drift(res) == []


def test_missing_declared_cron_is_flagged():
    m = {"cron": ["0 3 * * * /repo/nightly.sh"], "systemd_units": []}
    res = S.reconcile(m, cron_lines=[], unit_states={}, installed_units=[])
    assert _status(res, "0 3 * * * /repo/nightly.sh")["status"] == "MISSING_CRON"


def test_declared_unit_ok_when_installed_enabled_active():
    res = S.reconcile(MANIFEST, cron_lines=[], unit_states=_OK_UNIT, installed_units=["file-api.service"])
    assert _status(res, "file-api.service")["status"] == "OK"
    assert _status(res, "file-api.service")["alarm"] is False


def test_unit_not_installed_alarms():
    res = S.reconcile(MANIFEST, cron_lines=[],
                      unit_states={"file-api.service": {"installed": False, "enabled": False, "active": False}},
                      installed_units=[])
    assert _status(res, "file-api.service")["status"] == "UNIT_NOT_INSTALLED"
    assert _status(res, "file-api.service")["alarm"] is True


def test_unit_not_enabled_alarms():
    res = S.reconcile(MANIFEST, cron_lines=[],
                      unit_states={"file-api.service": {"installed": True, "enabled": False, "active": True}},
                      installed_units=["file-api.service"])
    assert _status(res, "file-api.service")["status"] == "UNIT_NOT_ENABLED"


def test_unit_down_alarms():
    res = S.reconcile(MANIFEST, cron_lines=[],
                      unit_states={"file-api.service": {"installed": True, "enabled": True, "active": False}},
                      installed_units=["file-api.service"])
    assert _status(res, "file-api.service")["status"] == "UNIT_DOWN"
    assert _status(res, "file-api.service")["alarm"] is True


def test_undeclared_se_systemd_unit_is_flagged():
    """An SE systemd unit installed on the box but NOT declared is drift too — the same
    invisible-machine-state class as an undeclared cron, via systemd."""
    res = S.reconcile(MANIFEST, cron_lines=[], unit_states=_OK_UNIT,
                      installed_units=["file-api.service", "rogue-se.service"])
    assert _status(res, "rogue-se.service")["status"] == "UNDECLARED_UNIT"
    assert _status(res, "rogue-se.service")["alarm"] is True


def test_report_only_no_install_or_action_key():
    for r in S.reconcile(MANIFEST, cron_lines=[], unit_states=_OK_UNIT, installed_units=["file-api.service"]):
        assert "install" not in r and "action" not in r and "kill" not in r


def test_loader_rejects_unit_without_reason(tmp_path):
    bad = tmp_path / "s.yaml"
    bad.write_text("cron: []\nsystemd_units:\n  - {name: x.service, unit_file: background/x.service}\n")
    with pytest.raises(S.ScheduleManifestError, match="reason"):
        S.load_manifest(bad)


def test_committed_manifest_declares_file_api_and_no_cron():
    m = S.load_manifest()  # background/schedule_manifest.yaml
    assert m["cron"] == []
    names = [u["name"] for u in m["systemd_units"]]
    assert "file-api.service" in names
    for u in m["systemd_units"]:
        assert u.get("reason")  # reason-with-state enforced
