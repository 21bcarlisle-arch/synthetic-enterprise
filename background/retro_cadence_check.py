#!/usr/bin/env python3
"""Automated staleness check for the retrospective/learn-loop cadence.

Discharges A1_learn_loop_chair's own named L2->L3 gap (docs/design/
maturity_map.yaml, 2026-07-12 DISCOVER pass): the retro cadence trigger
("~50 phases / 2 weeks since the last retro", stated in
.claude/skills/incident-retro/SKILL.md's own prose and the phase-close
checklist's item 6) had ZERO automated staleness check anywhere in
background/ -- relying entirely on an agent noticing during a manual
phase-close. That is exactly the class this project's own MAKE_IT_STICK
retrospective names: "every rule that DECAYED was an exhortation... every
rule that HELD was a MECHANISM." This module is the mechanism.

Two independent thresholds, either alone triggers staleness (matching the
skill's own OR-condition wording):

  - RETRO_STALE_DAYS: calendar days since the last retrospective doc's own
    filename date.
  - RETRO_STALE_PROMOTIONS: a "phase-count proxy". Deliberately NOT raw git
    commit count -- this atom's own 2026-07-13 follow-up pass explicitly
    flagged that raw commit count would badly OVER-count against
    DISCOVER/FRAME documentation churn (a single session produced 68 commits
    in <24h, dominated by atom-level narration, not the substantive
    capability-building units the original "~50 phases" intent was
    calibrated against). Instead this counts real `level_current: N`
    PROMOTION lines added to docs/design/maturity_map.yaml in commits since
    the last retro -- a much closer proxy for "how many atom-level
    capability jumps have landed since the group last learned something
    together", per that follow-up's own recommendation.

Usage:
    python3 -m background.retro_cadence_check          # print, exit 0/1
    python3 -m background.retro_cadence_check --ntfy   # also NTFY if stale

HONEST INTEGRATION NOTE (deliberately not done in this build pass -- see
this atom's own atom_status inbox entry for the reasoning): this module is
intentionally standalone rather than wired into background/health_check.py's
run_health_check() cycle. That one-line integration (import this module,
call check_retro_staleness(), append to problem_lines/ok_lines exactly like
that file's own _check_stale_dependencies()) is the remaining small step to
make this fire automatically inside the existing health-check daemon loop
without a human or agent needing to invoke this module directly. It was out
of this build pass's own granted file_scope (existing files under
background/ were excluded; only a genuinely new file was in scope) -- so
today this is a real, tested, correct MECHANISM, but not yet a *live*
trigger. Do not round this up to "fires automatically" until that
integration lands and is itself verified running.
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RETRO_DIR = PROJECT_DIR / "docs" / "retrospectives"
MATURITY_MAP = PROJECT_DIR / "docs" / "design" / "maturity_map.yaml"
# Transition-only NTFY dedup (2026-07-16, from_rich "repeating retro cadence
# stale FAKE message"): main() previously NTFY'd on EVERY --ntfy run while
# stale, so any caller (a per-turn invocation, a loop) re-sent the identical
# line forever -- an R5 violation and a channel that cries wolf. This stores
# the last warning actually sent; main() fires only on a TRANSITION (the
# warning text changed, or stale->fresh), never on an unchanged repeat.
NTFY_STATE_FILE = PROJECT_DIR / "docs" / "observability" / ".retro_cadence_ntfy_state.json"

# Named thresholds, matching the incident-retro skill's own cited cadence
# ("~50 phases/2 weeks since the last retro, or a harness rule changed" --
# the third OR-condition, a harness rule change, is inherently event-driven
# and not something a periodic staleness check can detect; only the two
# time/volume-based conditions are mechanised here).
RETRO_STALE_DAYS = 14
RETRO_STALE_PROMOTIONS = 50

_FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-")


def last_retro(retro_dir: Path = RETRO_DIR) -> tuple[Path, date] | None:
    """Return (path, date) of the most recent retrospective doc, keyed off
    its own filename date prefix (this project's own naming convention,
    e.g. 2026-07-14-evaporated-director-decision.md). None if the directory
    is missing/empty or no file matches the naming convention."""
    if not retro_dir.is_dir():
        return None
    best: tuple[Path, date] | None = None
    for f in sorted(retro_dir.glob("*.md")):
        m = _FILENAME_DATE_RE.match(f.name)
        if not m:
            continue
        try:
            d = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        if best is None or d > best[1]:
            best = (f, d)
    return best


def promotions_since(since: date, project_dir: Path = PROJECT_DIR) -> int:
    """Count level_current PROMOTION lines added to maturity_map.yaml in
    commits since `since` (inclusive) -- see module docstring for why this
    is preferred over raw commit count. Fails QUIET (returns 0) on any git
    error, matching health_check.py's own _check_stale_dependencies()
    posture: this is an informational proxy that surfaces a candidate, not
    a hard assertion, so a git failure should not itself raise or crash the
    health-check cycle that will eventually call it."""
    map_path = project_dir / "docs" / "design" / "maturity_map.yaml"
    if not map_path.exists():
        return 0
    try:
        rel = map_path.relative_to(project_dir)
    except ValueError:
        rel = map_path
    try:
        out = subprocess.check_output(
            [
                "git", "-C", str(project_dir), "log", "-p",
                "--since", since.isoformat(),
                "--", str(rel),
            ],
            text=True, timeout=30, stderr=subprocess.DEVNULL,
        )
    except Exception:
        return 0
    added = re.findall(r"^\+\s*level_current:\s*\d+", out, flags=re.MULTILINE)
    return len(added)


def check_retro_staleness(
    today: date | None = None,
    retro_dir: Path = RETRO_DIR,
    project_dir: Path = PROJECT_DIR,
) -> str | None:
    """Return an alarm string if the retro cadence is stale by either named
    threshold, else None. `today`/`retro_dir`/`project_dir` are injectable
    so tests never depend on real wall-clock time or this repo's own live
    retrospectives directory."""
    today = today or datetime.now(timezone.utc).date()
    retro = last_retro(retro_dir)
    if retro is None:
        return (
            f"No retrospective doc found in {retro_dir} at all -- "
            "the learn-loop cadence has never fired."
        )
    path, retro_date = retro
    days = (today - retro_date).days
    promos = promotions_since(retro_date, project_dir)
    reasons = []
    if days > RETRO_STALE_DAYS:
        reasons.append(
            f"{days}d since last retro ({path.name}), threshold {RETRO_STALE_DAYS}d"
        )
    if promos > RETRO_STALE_PROMOTIONS:
        reasons.append(
            f"{promos} maturity-map promotions since last retro ({path.name}), "
            f"threshold {RETRO_STALE_PROMOTIONS}"
        )
    if reasons:
        return "Retro cadence STALE: " + "; ".join(reasons)
    return None


def _read_last_ntfy() -> str | None:
    """The last warning string actually NTFY'd, or None. Fail-quiet."""
    try:
        import json
        return json.loads(NTFY_STATE_FILE.read_text()).get("last_warning")
    except Exception:
        return None


def _write_last_ntfy(warning: str | None) -> None:
    """Record the last-NTFY'd warning (None once fresh again, so the next
    genuine staleness fires exactly once). Fail-quiet."""
    try:
        import json
        NTFY_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        NTFY_STATE_FILE.write_text(json.dumps({"last_warning": warning}))
    except Exception:
        pass


def main() -> int:
    send = "--ntfy" in sys.argv
    warning = check_retro_staleness()
    if warning:
        print(f"[retro-cadence] {warning}")
        # TRANSITION-ONLY (R5): NTFY only when the warning first appears or its
        # text changes -- never re-send an unchanged line every run. This is the
        # whole fix for the "repeating retro cadence stale" spam: an unchanged
        # stale state is silent after its one alert.
        if send and warning != _read_last_ntfy():
            try:
                sys.path.insert(0, str(PROJECT_DIR))
                from background.ntfy_utils import send_ntfy
                send_ntfy(
                    f"[RETRO CADENCE] {warning}",
                    headers={"X-Priority": "3", "X-Tags": "warning"},
                )
                _write_last_ntfy(warning)
            except Exception as e:
                print(f"[retro-cadence] NTFY send failed (non-fatal): {e}")
        elif send:
            print("[retro-cadence] unchanged since last alert -- transition-only, not re-sending")
        return 1
    # Fresh again: clear the dedup state so a FUTURE staleness alerts once more.
    if _read_last_ntfy() is not None:
        _write_last_ntfy(None)
    print("[retro-cadence] OK -- within both thresholds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
