"""SM1 — the daily self-note automation (SELF_MEASUREMENT_UNIFIED_DESIGN.md §1/§1b,
DIRECTOR_STEER_SELF_MEASUREMENT_AND_AXES_2026-07-22.md §1).

Computes ONE honest morning note from REUSED organs (no parallel measurement layer —
the steer's §13 anti-gaming principle) and publishes it unprompted each morning:
  - Verified autonomous work in the window (git + gate_authorizations.jsonl), with
    mechanical-republish commits EXCLUDED (the single most important honesty decision,
    §1: the auto-process treadmill republishing an unchanged net must NOT read as autonomy).
  - Longest stall + honest cause (the deadman's MEANINGFUL-commit clock).
  - The R17 always-drawable-law status (the director's specific standing ask: the note
    reports THIS rule's status every morning unprompted).
  - Resource inputs (SM2 rate_limits sensor — optional, fail-closed when absent).

TWO WALLS this module honours:
  * §2 HARD LAW — SEVERANCE. This module has NO path into the draw and the draw never
    reads it. It only READS observability/git and WRITES the note (a log + NTFY). It is
    never imported by supervisor.py / find_work; no number it computes feeds priority,
    reward, selection, or scheduling. Enforced structurally + by test_daily_self_note.py.
  * R15 FAIL-CLOSED — an unavailable source is a RED in the note, never a silent zero (a
    silent zero would flatter). Every reader returns ("value", None) or (None, "reason").

Definitions are LEDGER-GOVERNED (§1b): changing what a number MEANS is a director-ratified
edit, not a quiet code change here.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
NOTE_LOG = PROJECT_DIR / "docs" / "observability" / "daily-self-note.md"
LAST_DATE_STAMP = PROJECT_DIR / "docs" / "observability" / ".daily_self_note_last_date"
RATE_LIMITS_SENSOR = PROJECT_DIR / "docs" / "observability" / ".rate_limits.json"  # SM2 (optional)

# SUBSTANTIVE-WORK ALLOWLIST (§1 honesty decision, robust form). A denylist of churn dirs is
# fragile — the auto-process treadmill also sweeps docs/observability + docs/staging/done, which a
# denylist keeps missing. Instead: a commit is SUBSTANTIVE iff it touches at least one real-work
# path (code, tests, design/map, or DISCOVER findings); everything else — reports, status, state,
# site/data, shadow, observability logs, staging archival — is mechanical republish/churn. A
# gate-backed level move always co-touches docs/design/maturity_map.yaml, so it counts here.
_SUBSTANTIVE_PREFIXES = (
    "company/", "saas/", "simulation/", "sim/", "tools/", "interface/",
    "tests/", "hooks/", "docs/design/", "docs/market_research/", "docs/vision/",
)


def _is_substantive_file(f: str) -> bool:
    return f.endswith(".py") or any(f.startswith(p) for p in _SUBSTANTIVE_PREFIXES)


def _run_git(*args: str) -> tuple[str | None, str | None]:
    """(stdout, None) on success; (None, reason) on any failure — fail-closed."""
    try:
        r = subprocess.run(["git", *args], cwd=str(PROJECT_DIR),
                           capture_output=True, text=True, timeout=30)
    except Exception as e:  # noqa: BLE001
        return None, f"git unavailable ({type(e).__name__})"
    if r.returncode != 0:
        return None, f"git rc={r.returncode}: {r.stderr.strip()[:120]}"
    return r.stdout, None


def _is_mechanical_republish(files: list[str]) -> bool:
    """True iff NO changed path is substantive (all churn/archival). Empty diff (a merge with no
    files) counts as republish — nothing landed."""
    return not any(_is_substantive_file(f) for f in files)


def verified_work(window_hours: int = 24, _runner=_run_git) -> tuple[dict | None, str | None]:
    """Count SUBSTANTIVE commits in the window (mechanical republishes excluded). Reuses git —
    NOT a parallel verifier. Returns ({substantive, republish, subjects}, None) or (None, reason).
    Fail-closed: any git failure is a RED, never a flattering zero."""
    since = f"{window_hours} hours ago"
    out, err = _runner("log", f"--since={since}", "--pretty=format:%H\t%s")
    if err is not None:
        return None, err
    lines = [ln for ln in out.splitlines() if ln.strip()]
    substantive: list[str] = []
    republish = 0
    for ln in lines:
        sha, _, subject = ln.partition("\t")
        files_out, ferr = _runner("show", "--name-only", "--pretty=format:", sha)
        if ferr is not None:
            return None, f"git show failed on {sha[:9]}: {ferr}"
        files = [f for f in files_out.splitlines() if f.strip()]
        if _is_mechanical_republish(files):
            republish += 1
        else:
            substantive.append(subject.strip())
    return {"substantive_count": len(substantive), "republish_count": republish,
            "substantive_subjects": substantive}, None


def longest_stall(window_hours: int = 24, _runner=_run_git) -> tuple[dict | None, str | None]:
    """Longest gap (minutes) between SUBSTANTIVE commits in the window — the deadman's
    MEANINGFUL-commit clock (reused, not re-implemented as a parallel timer). Returns
    ({gap_minutes, ...}, None) or (None, reason). Fail-closed."""
    out, err = _runner("log", f"--since={window_hours} hours ago", "--pretty=format:%ct\t%H")
    if err is not None:
        return None, err
    stamps: list[int] = []
    for ln in out.splitlines():
        if not ln.strip():
            continue
        ct, _, sha = ln.partition("\t")
        files_out, ferr = _runner("show", "--name-only", "--pretty=format:", sha)
        if ferr is not None:
            return None, f"git show failed: {ferr}"
        files = [f for f in files_out.splitlines() if f.strip()]
        if not _is_mechanical_republish(files):
            try:
                stamps.append(int(ct))
            except ValueError:
                return None, f"unparseable commit time on {sha[:9]}"
    if len(stamps) < 2:
        return {"gap_minutes": None, "substantive_commits": len(stamps),
                "note": "fewer than 2 substantive commits in window — no inter-commit gap to measure"}, None
    stamps.sort()
    gap = max(b - a for a, b in zip(stamps, stamps[1:]))
    return {"gap_minutes": round(gap / 60, 1), "substantive_commits": len(stamps)}, None


def r17_status() -> tuple[str | None, str | None]:
    """The R17 always-drawable-law status line (the director's standing morning ask). Imported
    LAZILY and read-only — this is a READ of draw state, never a write into it (§2 severance:
    the note reads the world; it never feeds the draw). Fail-closed on import/read error."""
    try:
        from background.supervisor import forward_discovery_law_status_line
        return forward_discovery_law_status_line(), None
    except Exception as e:  # noqa: BLE001
        return None, f"R17 status unavailable ({type(e).__name__}: {str(e)[:80]})"


def resource_inputs() -> tuple[str | None, str | None]:
    """SM2 rate_limits token-headroom sensor (optional). Absent → an honest 'not built' line,
    NOT a hard red (design §4: SM1 fail-closed WITHOUT it). A present-but-stale sensor IS a red."""
    if not RATE_LIMITS_SENSOR.exists():
        return "SM2 rate_limits sensor not built — resource-headroom input unavailable (optional).", None
    try:
        data = json.loads(RATE_LIMITS_SENSOR.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return None, f"rate_limits sensor present but unreadable ({type(e).__name__})"
    return f"resource headroom: {data.get('headroom_pct', '?')}% (as of {data.get('as_of', '?')})", None


def _red(reason: str) -> str:
    return f"🔴 RED — source unavailable: {reason} (fail-closed, not a zero — R15)"


def render_note(now_iso: str, window_hours: int = 24, _runner=_run_git) -> str:
    """Assemble the morning note. Every claim is observed-with-evidence or flagged RED (R9/R15)."""
    vw, vw_err = verified_work(window_hours, _runner)
    st, st_err = longest_stall(window_hours, _runner)
    r17, r17_err = r17_status()
    res, res_err = resource_inputs()

    lines = [
        f"## Daily self-note — {now_iso} (window: prior {window_hours}h)",
        "",
        "_Machine-computed from reused organs (git + ledgers), never a parallel verifier. "
        "The agent narrates; it does not compute (§2 severance: no number here feeds the draw)._",
        "",
        "**Verified autonomous work** _(substantive commits; mechanical republishes EXCLUDED — §1)_",
    ]
    if vw_err:
        lines.append(f"- {_red(vw_err)}")
    else:
        lines.append(f"- {vw['substantive_count']} substantive commit(s); "
                     f"{vw['republish_count']} mechanical republish(es) excluded.")
        for s in vw["substantive_subjects"][:8]:
            lines.append(f"    - {s}")
        if vw["substantive_count"] == 0:
            lines.append("    - ⚠ ZERO verified product progress this window (full pipeline liveness ≠ autonomy).")

    lines += ["", "**Longest stall + honest cause** _(deadman meaningful-commit clock)_"]
    if st_err:
        lines.append(f"- {_red(st_err)}")
    elif st.get("gap_minutes") is None:
        lines.append(f"- {st['note']}.")
    else:
        lines.append(f"- Longest inter-substantive-commit gap: **{st['gap_minutes']} min** "
                     f"({st['substantive_commits']} substantive commits). "
                     "Cause requires narration (authority-gated vs drained vs genuine idle) — agent adds it.")

    lines += ["", "**R17 — THE TICK NEVER RESTS (status, standing morning report)**"]
    lines.append(f"- {r17 if r17 else _red(r17_err)}")

    lines += ["", "**Resource inputs**"]
    lines.append(f"- {res if res else _red(res_err)}")

    lines += ["", "---", ""]
    return "\n".join(lines)


def _today(now: datetime) -> str:
    return now.strftime("%Y-%m-%d")


def already_ran_today(now: datetime) -> bool:
    try:
        return LAST_DATE_STAMP.read_text(encoding="utf-8").strip() == _today(now)
    except OSError:
        return False


def publish(note: str, now: datetime, *, send=None) -> None:
    """Append the note to the durable log, stamp the day (idempotent per day), and send ONE NTFY
    digest line. `send` injectable for tests (defaults to the real NTFY, lazily imported)."""
    NOTE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with NOTE_LOG.open("a", encoding="utf-8") as f:
        f.write(note + "\n")
    LAST_DATE_STAMP.write_text(_today(now), encoding="utf-8")
    if send is None:
        try:
            from background.ntfy_utils import send_ntfy
            send = lambda m: send_ntfy(m, headers={"Title": "Daily self-note"})  # noqa: E731
        except Exception:  # noqa: BLE001
            return
    # ONE terse digest line (R5 transition discipline: the note itself is the payload in the log).
    first = next((ln for ln in note.splitlines() if ln.startswith("## ")), "Daily self-note")
    r17, _ = r17_status()
    try:
        send(f"{first}\n{r17 or 'R17 status: RED'}\nFull note: docs/observability/daily-self-note.md")
    except Exception:  # noqa: BLE001
        pass


def run(force: bool = False, now: datetime | None = None, *, send=None,
        _runner=_run_git) -> str:
    """Entry point (systemd oneshot). Idempotent per day unless force=True. Returns a status word."""
    now = now or datetime.now(timezone.utc)
    if already_ran_today(now) and not force:
        return "already_ran_today"
    note = render_note(now.isoformat(timespec="minutes"), _runner=_runner)
    publish(note, now, send=send)
    return "published"


def main() -> None:
    print(run())


if __name__ == "__main__":
    main()
