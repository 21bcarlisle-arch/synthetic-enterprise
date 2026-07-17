"""Reconcile DECLARED OS-level scheduling/services (schedule_manifest.yaml) against ACTUAL.
OPS1 sub-step 3 (G-L2 for scheduling), docs/design/OPERATIONAL_LAYER_DESIGN.md §5.

The blackout's root was an INVISIBLE crontab entry — machine state no repo reader could see,
resurrecting a broken stack. This module makes that class structurally detectable, forever:
it compares the machine's actual `crontab -l` + installed systemd (--user) units against the
committed schedule_manifest.yaml and REPORTS any drift:

    UNDECLARED_CRON    a crontab line not in the manifest (THE invisible-cron class -> alarm)
    MISSING_CRON       a declared cron line not actually present (alarm)
    UNIT_NOT_INSTALLED a declared systemd unit not installed (alarm)
    UNIT_NOT_ENABLED   a declared unit not enabled when it must boot-start (alarm)
    UNIT_DOWN          a declared unit that must be active but isn't (alarm)
    UNDECLARED_UNIT    an SE systemd unit installed but not declared (alarm)
    OK                 declared and matching

REPORT ONLY — it never installs, removes, or edits a schedule/unit (no side effects), exactly
like process_reconciler. Fixing drift is a human/install-script action, never an automatic one.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

_HERE = Path(__file__).resolve().parent
MANIFEST_PATH = _HERE / "schedule_manifest.yaml"
SYSTEMD_USER_DIR = Path.home() / ".config" / "systemd" / "user"

ALARM_STATUSES = {"UNDECLARED_CRON", "MISSING_CRON", "UNIT_NOT_INSTALLED",
                  "UNIT_NOT_ENABLED", "UNIT_DOWN", "UNDECLARED_UNIT"}


class ScheduleManifestError(ValueError):
    pass


def load_manifest(path: Path | None = None) -> dict:
    import yaml
    path = path or MANIFEST_PATH
    data = yaml.safe_load(Path(path).read_text())
    if not isinstance(data, dict) or "cron" not in data or "systemd_units" not in data:
        raise ScheduleManifestError(f"{path}: must declare 'cron' and 'systemd_units' (even if empty)")
    for u in data["systemd_units"]:
        for req in ("name", "unit_file", "reason"):
            if not str(u.get(req, "")).strip():
                raise ScheduleManifestError(f"systemd unit {u.get('name')!r} missing '{req}' (reason-with-state)")
    return data


# ── actual-state readers (each returns something injectable for tests) ──

def _actual_cron_lines() -> list[str]:
    """Non-comment, non-empty user-crontab lines. Empty if no crontab."""
    r = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if getattr(r, "returncode", 1) != 0:
        return []
    return [ln.strip() for ln in (r.stdout or "").splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


def _unit_state(name: str) -> dict:
    """{'installed': bool, 'enabled': bool, 'active': bool} for a --user unit."""
    def _q(prop):
        r = subprocess.run(["systemctl", "--user", "is-" + prop, name],
                           capture_output=True, text=True)
        return (r.stdout or "").strip()
    installed = (SYSTEMD_USER_DIR / name).exists()
    return {"installed": installed,
            "enabled": _q("enabled") == "enabled",
            "active": _q("active") == "active"}


def _installed_se_units() -> list[str]:
    """SE-owned --user unit filenames: those whose unit file references this repo."""
    out = []
    if not SYSTEMD_USER_DIR.is_dir():
        return out
    for f in SYSTEMD_USER_DIR.glob("*.service"):
        try:
            if "synthetic-enterprise" in f.read_text():
                out.append(f.name)
        except OSError:
            pass
    return out


def reconcile(manifest: dict | None = None,
              cron_lines: list[str] | None = None,
              unit_states: dict[str, dict] | None = None,
              installed_units: list[str] | None = None) -> list[dict]:
    """Classify declared vs actual. REPORT ONLY. Params injectable for tests; production
    reads live state."""
    manifest = manifest or load_manifest()
    cron_lines = _actual_cron_lines() if cron_lines is None else cron_lines
    installed_units = _installed_se_units() if installed_units is None else installed_units
    declared_cron = [str(c).strip() for c in manifest.get("cron", [])]
    declared_units = {u["name"]: u for u in manifest.get("systemd_units", [])}

    def _state(name):
        if unit_states is not None:
            return unit_states.get(name, {"installed": False, "enabled": False, "active": False})
        return _unit_state(name)

    results: list[dict] = []

    # cron: any actual line not declared -> UNDECLARED_CRON (the invisible-cron class)
    for line in cron_lines:
        if line not in declared_cron:
            results.append({"kind": "cron", "item": line, "status": "UNDECLARED_CRON", "alarm": True})
    for line in declared_cron:
        if line not in cron_lines:
            results.append({"kind": "cron", "item": line, "status": "MISSING_CRON", "alarm": True})

    # declared systemd units
    for name, u in declared_units.items():
        st = _state(name)
        if not st["installed"]:
            status = "UNIT_NOT_INSTALLED"
        elif u.get("enabled") and not st["enabled"]:
            status = "UNIT_NOT_ENABLED"
        elif u.get("active") and not st["active"]:
            status = "UNIT_DOWN"
        else:
            status = "OK"
        results.append({"kind": "unit", "item": name, "status": status,
                        "alarm": status in ALARM_STATUSES, "reason": u.get("reason", "")})

    # undeclared SE units installed on the box
    for name in installed_units:
        if name not in declared_units:
            results.append({"kind": "unit", "item": name, "status": "UNDECLARED_UNIT", "alarm": True})

    return results


def drift(results: list[dict]) -> list[dict]:
    return [r for r in results if r["alarm"]]


def format_report(results: list[dict]) -> str:
    lines = []
    for r in sorted(results, key=lambda r: (0 if r["alarm"] else 1, r["item"])):
        mark = "✗" if r["alarm"] else "✓"
        lines.append(f"  {mark} [{r['kind']}] {r['item']:<24} {r['status']}")
    return "\n".join(lines)


def _main(argv: list[str]) -> int:
    import sys
    try:
        results = reconcile()
    except ScheduleManifestError as e:
        print(f"SCHEDULE MANIFEST INVALID: {e}", file=sys.stderr)
        return 2
    print(format_report(results))
    alarms = drift(results)
    print(f"\n{len(alarms)} schedule drift alarm(s); {len(results) - len(alarms)} OK.")
    return 1 if alarms else 0


if __name__ == "__main__":
    import sys
    raise SystemExit(_main(sys.argv))
