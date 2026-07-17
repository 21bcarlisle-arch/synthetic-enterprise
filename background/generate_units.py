"""Generate systemd (--user) unit files from process_manifest.yaml.
OPS1 sub-step 4 — the manifest is the SINGLE source; units are DERIVED, committed, and readable.

Every entry with owner=="systemd" gets one deterministic .service under background/systemd/.
A test asserts the committed units == regenerate() output, so the generated layer can't itself
drift from the manifest (director requirement). The worker seat (owner==worker-seat-manager) and
retired entries get NO unit; file-api is a separately-owned service (schedule_manifest.yaml).

G-L3 is baked into every unit: StartLimitBurst/IntervalSec so a crash-loop enters `failed` instead
of restarting silently forever (the file-api 32,707 lesson). EnvironmentFile uses `-` so a missing
secret degrades rather than crash-loops.
"""
from __future__ import annotations

from pathlib import Path

_HERE = Path(__file__).resolve().parent
UNITS_DIR = _HERE / "systemd"
PY = "/usr/bin/python3"
ENV_FILE = "/home/rich/.config/synthetic-enterprise/.env.ntfy"

# G-L3 crash-loop bound: >BURST failures in INTERVAL seconds -> unit goes to `failed`.
START_LIMIT_BURST = 5
START_LIMIT_INTERVAL = 120


def _exec_start(command: str) -> str:
    """Manifest command (starts with `python3 `) -> absolute ExecStart."""
    assert command.startswith("python3 "), command
    return PY + command[len("python3"):]


def generate_unit(entry: dict) -> str:
    name = entry["session"]
    desc = entry.get("purpose", name).replace("\n", " ").strip()
    return (
        f"# GENERATED from background/process_manifest.yaml by generate_units.py — DO NOT EDIT.\n"
        f"# Edit the manifest and regenerate. state={entry['state']} owner={entry['owner']}\n"
        f"[Unit]\n"
        f"Description=Synthetic Enterprise: {desc}\n"
        f"After=network.target\n"
        f"# G-L3: a crash-loop enters `failed` instead of restarting silently forever.\n"
        f"StartLimitIntervalSec={START_LIMIT_INTERVAL}\n"
        f"StartLimitBurst={START_LIMIT_BURST}\n"
        f"\n"
        f"[Service]\n"
        f"Type=simple\n"
        f"WorkingDirectory=/home/rich/synthetic-enterprise\n"
        f"EnvironmentFile=-{ENV_FILE}\n"
        f"ExecStart={_exec_start(entry['command'])}\n"
        f"Restart=on-failure\n"
        f"RestartSec=5\n"
        f"\n"
        f"[Install]\n"
        f"WantedBy=default.target\n"
    )


def regenerate(manifest_path: Path | None = None) -> dict[str, str]:
    """{unit_filename: unit_text} for every owner==systemd entry. Deterministic (sorted)."""
    from background import process_reconciler as R
    entries = R.load_manifest(manifest_path)
    out = {}
    for e in sorted((e for e in entries if e.get("owner") == "systemd"), key=lambda e: e["session"]):
        out[f"{e['session']}.service"] = generate_unit(e)
    return out


def write_units() -> list[str]:
    UNITS_DIR.mkdir(exist_ok=True)
    written = []
    for fname, text in regenerate().items():
        (UNITS_DIR / fname).write_text(text)
        written.append(fname)
    # remove any stale committed unit no longer in the manifest
    for f in UNITS_DIR.glob("*.service"):
        if f.name not in regenerate():
            f.unlink()
    return sorted(written)


if __name__ == "__main__":
    print("wrote:", write_units())
