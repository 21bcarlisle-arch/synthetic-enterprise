"""Did Skynet start itself, or did a human start it?

WHY THIS EXISTS
---------------
On 2026-08-12 a Windows Update restart brought Windows back at 09:33:19 and left WSL — and
therefore every daemon, every recovery mechanism and the whole autonomy layer — down until a
human logged in at 09:55:26. The starter tasks were LOGON-triggered, so an unattended reboot
fired none of them. The gap was not a delay; absent a login it was unbounded.

`SkynetBootStart` (boot trigger, S4U, no stored password) was added to close that. This module
is the control that says whether it actually worked, because "the task exists" is not the claim
— the claim is **WSL came up with nobody logged in**.

THE DISCRIMINATOR, and why it is not a tautology (R15)
------------------------------------------------------
The verdict compares two clocks that come from DIFFERENT authorities:

  * WSL's own boot time, read from `/proc/stat`'s `btime` — the Linux kernel's own record.
  * The first INTERACTIVE Windows logon after the host booted, read from the Windows Security
    event log (4624, logon types 2/10/11) via PowerShell.

Neither is derived from the other, and neither is derived from the scheduled task whose
behaviour is being judged. A task that silently did nothing cannot make this pass, because the
Linux clock would simply not exist until a logon produced one.

FAIL DIRECTION IS `UNPROVEN`, NEVER `PASS`
------------------------------------------
Every way of not knowing — the Security log unreadable (it needs elevation), no logon found,
PowerShell absent, a malformed timestamp — returns UNPROVEN. An unavailable check is a FAILED
check (R15), so this module refuses to convert missing evidence into a green. The three verdicts
are kept apart on purpose:

  PASS      WSL booted BEFORE any interactive logon -> it started itself.
  FAIL      WSL booted AFTER the first interactive logon -> a human started it, as on 2026-08-12.
  UNPROVEN  the question could not be answered from evidence.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path

PASS = "PASS"
FAIL = "FAIL"
UNPROVEN = "UNPROVEN"

POWERSHELL = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
PROC_STAT = Path("/proc/stat")

# Logon types that mean a HUMAN was at (or remoted into) the console. Deliberately excludes
# type 5 (service) and type 3 (network) -- a service logon is not somebody arriving at the
# machine, and counting it would make FAIL unreachable in exactly the case we care about.
INTERACTIVE_LOGON_TYPES = (2, 10, 11)

# ...but the type filter ALONE is not enough, and this was caught by running the thing rather
# than by reasoning about it. Windows logs type-2 logons for its own pseudo-accounts on EVERY
# boot, milliseconds after start:
#
#     09:33:18  type=2  Font\UMFD-0        (Font Driver Host)
#     09:33:18  type=2  Window\DWM-1       (Desktop Window Manager)
#     09:55:26  type=11 MicrosoftAccount\21bcarlisle@gmail.com   <- the actual human
#
# Counting UMFD/DWM would place a "logon" at boot+1s forever, so WSL starting at boot+30s would
# read as "a human got there first" and the control would report FAIL on every single boot. That
# is the exact mirror of a fail-open control -- a fail-ALWAYS control is equally worthless,
# because a verdict that never changes carries no information either way.
NON_HUMAN_LOGON_DOMAINS = ("Window Manager", "Font Driver Host", "NT AUTHORITY", "Window", "Font")

_PS_FIRST_LOGON = r"""
$ErrorActionPreference='Stop'
$boot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
$ev = Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4624; StartTime=$boot} -ErrorAction Stop |
      Where-Object { $_.Message -match 'Logon Type:\s+(2|10|11)\b' } |
      Where-Object {
          $m = [regex]::Match($_.Message, 'New Logon:[\s\S]*?Account Name:\s+(\S+)[\s\S]*?Account Domain:\s+(\S+)')
          $name = $m.Groups[1].Value
          $domain = $m.Groups[2].Value
          # machine accounts end in $; UMFD-n / DWM-n are the window/font hosts.
          -not ($name -like '*$' -or $name -match '^(UMFD|DWM)-\d+$' -or
                $domain -in @('Window','Font','NT') -or
                $domain -like 'Window*' -or $domain -like 'Font*' -or $domain -like 'NT*')
      } |
      Sort-Object TimeCreated |
      Select-Object -First 1
if ($null -eq $ev) { Write-Output 'NONE' } else { Write-Output $ev.TimeCreated.ToUniversalTime().ToString('o') }
"""


def wsl_boot_time_utc(proc_stat: Path = PROC_STAT):
    """When this Linux kernel booted, from its own btime. None if unreadable/absent.

    btime is seconds since the epoch and is written by the kernel at boot, so it survives
    everything a userland process could do to it -- which is the point: the task under test
    cannot forge it.
    """
    try:
        text = proc_stat.read_text()
    except OSError:
        return None
    match = re.search(r"^btime\s+(\d+)\s*$", text, re.MULTILINE)
    if not match:
        return None
    return _dt.datetime.fromtimestamp(int(match.group(1)), tz=_dt.timezone.utc)


def first_interactive_logon_utc(runner=None):
    """First interactive Windows logon since the HOST booted, or None if unanswerable.

    None is 'could not tell', never 'there wasn't one' -- the caller must treat it as UNPROVEN.
    """
    run = runner or _default_runner
    try:
        out = run(_PS_FIRST_LOGON)
    except Exception:
        return None
    if out is None:
        return None
    out = out.strip()
    if not out or out == "NONE":
        return None
    try:
        stamp = _dt.datetime.fromisoformat(out.replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        return None
    return stamp.astimezone(_dt.timezone.utc)


def _default_runner(script: str):
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, timeout=180,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def verdict(wsl_boot, first_logon):
    """PASS / FAIL / UNPROVEN plus the reason, from two independently-sourced clocks."""
    if wsl_boot is None:
        return UNPROVEN, "WSL boot time unreadable (/proc/stat btime absent or malformed)"
    if first_logon is None:
        return UNPROVEN, (
            "no interactive Windows logon could be read since host boot -- the Security log "
            "needs elevation, and an unreadable log is an unanswered question, not a pass"
        )
    delta = (first_logon - wsl_boot).total_seconds()
    if wsl_boot < first_logon:
        return PASS, (
            f"WSL booted {delta:.0f}s BEFORE the first interactive logon -- it started itself"
        )
    return FAIL, (
        f"WSL booted {-delta:.0f}s AFTER the first interactive logon -- a human started it, "
        "which is the 2026-08-12 failure mode"
    )


def evaluate(runner=None, proc_stat: Path = PROC_STAT):
    wsl_boot = wsl_boot_time_utc(proc_stat)
    first_logon = first_interactive_logon_utc(runner)
    status, reason = verdict(wsl_boot, first_logon)
    return {
        "status": status,
        "reason": reason,
        "wsl_boot_utc": wsl_boot.isoformat() if wsl_boot else None,
        "first_interactive_logon_utc": first_logon.isoformat() if first_logon else None,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="emit the result as JSON")
    ap.add_argument(
        "--strict", action="store_true",
        help="exit non-zero unless the verdict is PASS (UNPROVEN also fails)",
    )
    args = ap.parse_args(argv)

    result = evaluate()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['status']}: {result['reason']}")
        print(f"  wsl boot            : {result['wsl_boot_utc']}")
        print(f"  first human logon   : {result['first_interactive_logon_utc']}")

    if args.strict:
        return 0 if result["status"] == PASS else 1
    return 0 if result["status"] != FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
