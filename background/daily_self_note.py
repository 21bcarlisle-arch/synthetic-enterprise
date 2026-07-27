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

from background.harden_commit import is_harden_commit

PROJECT_DIR = Path(__file__).resolve().parent.parent
NOTE_LOG = PROJECT_DIR / "docs" / "observability" / "daily-self-note.md"
LAST_DATE_STAMP = PROJECT_DIR / "docs" / "observability" / ".daily_self_note_last_date"
RATE_LIMITS_SENSOR = PROJECT_DIR / "docs" / "observability" / ".rate_limits.json"  # SM2 (optional)
IN_PROGRESS_DIR = PROJECT_DIR / "docs" / "staging" / "in_progress"  # LAW C independent primary-state read

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


# DIRECTOR-RULING 2026-07-23 (PRODUCT FIRST): site AUTHORED pages/templates are the director's
# window = product, so they count as substantive. The GENERATED subtrees below are regenerated
# every auto-process run (churn) and stay EXCLUDED — verified against real auto-process commits,
# which touch ONLY these paths under site/ (§1 churn exclusion preserved, not weakened).
_SITE_GENERATED_SUBTREES = ("site/data/", "site/state/", "site/shadow/", "site/snapshots/")


def _is_substantive_file(f: str) -> bool:
    if f.startswith("site/"):
        return not f.startswith(_SITE_GENERATED_SUBTREES)
    return f.endswith(".py") or any(f.startswith(p) for p in _SUBSTANTIVE_PREFIXES)


# DIRECTOR-RULING 2026-07-23 (PRODUCT FIRST): split the already-substantive commits into PRODUCT
# (moves the director's axes / commercial spine — the site, wholesale organs, demand surfaces, the
# population generator, fidelity of the simulated world) vs MACHINERY (harness, continuity,
# authority, measurement, governance, meta-fixes). This is a v1, PROVISIONAL prefix classifier —
# the ruling names the definitions "ledger-governed", so this is the seed to be governed, not the
# final word. It splits ONLY the substantive set; the §1 mechanical-republish exclusion is unchanged.
_PRODUCT_PREFIXES = (
    "company/", "saas/", "simulation/", "sim/", "interface/", "site/",
    "docs/market_research/", "docs/vision/", "docs/domain_artefact_library/",
)
_PRODUCT_TEST_AREAS = frozenset({"company", "saas", "simulation", "sim", "interface", "site"})


def _file_class(f: str) -> str | None:
    """PRODUCT / MACHINERY / None(non-substantive). A test file inherits the class of what it
    tests (tests/<area>/...); everything else is classed by prefix. Default is MACHINERY so an
    unrecognised path can never inflate the product count (fail-toward-machinery, matching the
    ruling's intent that machinery is the residual, product the thing that must be proven)."""
    if not _is_substantive_file(f):
        return None
    if f.startswith("tests/"):
        parts = f.split("/")
        area = parts[1] if len(parts) > 1 else ""
        return "product" if area in _PRODUCT_TEST_AREAS else "machinery"
    return "product" if any(f.startswith(p) for p in _PRODUCT_PREFIXES) else "machinery"


def _commit_class(files: list[str]) -> str:
    """A substantive commit is PRODUCT if ANY of its files is product-class, else MACHINERY.
    (Caller guarantees the commit is already substantive — not a mechanical republish.)"""
    return "product" if any(_file_class(f) == "product" for f in files) else "machinery"


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
    product: list[str] = []
    machinery: list[str] = []
    harden: list[str] = []
    republish = 0
    for ln in lines:
        sha, _, subject = ln.partition("\t")
        subj = subject.strip()
        # WORK_DEFINITION §1 (2026-07-27): a HARDEN re-verify NEVER counts as work — excluded from
        # the substantive count AND the product/machinery split before any file classification, so a
        # HARDEN-only window reads 0 product / 0 machinery no matter what code/tests it touched. Keyed
        # on the ACTUAL subject (R15 independence), a sibling class to the §1 republish exclusion.
        if is_harden_commit(subj):
            harden.append(subj)
            continue
        files_out, ferr = _runner("show", "--name-only", "--pretty=format:", sha)
        if ferr is not None:
            return None, f"git show failed on {sha[:9]}: {ferr}"
        files = [f for f in files_out.splitlines() if f.strip()]
        if _is_mechanical_republish(files):
            republish += 1
        else:
            substantive.append(subj)
            (product if _commit_class(files) == "product" else machinery).append(subj)
    return {"substantive_count": len(substantive), "republish_count": republish,
            "substantive_subjects": substantive,
            "product_count": len(product), "product_subjects": product,
            "machinery_count": len(machinery), "machinery_subjects": machinery,
            "harden_count": len(harden), "harden_subjects": harden}, None


def longest_stall(window_hours: int = 24, _runner=_run_git) -> tuple[dict | None, str | None]:
    """Longest gap (minutes) between SUBSTANTIVE commits in the window — the deadman's
    MEANINGFUL-commit clock (reused, not re-implemented as a parallel timer). Returns
    ({gap_minutes, ...}, None) or (None, reason). Fail-closed."""
    out, err = _runner("log", f"--since={window_hours} hours ago", "--pretty=format:%ct\t%H\t%s")
    if err is not None:
        return None, err
    stamps: list[int] = []
    for ln in out.splitlines():
        if not ln.strip():
            continue
        parts = ln.split("\t", 2)
        ct, sha, subject = parts[0], parts[1], (parts[2] if len(parts) > 2 else "")
        # WORK_DEFINITION §1: this IS the deadman meaningful-commit clock (reused) — so a HARDEN
        # re-verify must not close a stall here either, exactly as it no longer refreshes the
        # deadman liveness clock. A HARDEN-only window therefore reads as one long stall.
        if is_harden_commit(subject):
            continue
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
        from background.supervisor import (
            forward_discovery_law_status_line,
            authorized_set_enumeration_line,
        )
        # Ruling 2026-07-23 (R17 class fix §2): the daily note publishes the WHOLE-SET enumeration,
        # not a lane-scoped forward-discovery line only -- a lane-scoped proof can never again ground
        # rest, so the note must show every level's drawable/empty verdict.
        return f"{forward_discovery_law_status_line()} || {authorized_set_enumeration_line()}", None
    except Exception as e:  # noqa: BLE001
        return None, f"R17 status unavailable ({type(e).__name__}: {str(e)[:80]})"


def r17_effect_crosscheck(in_progress_dir: Path | None = None, _status_fn=r17_status) -> str:
    """LAW C item 2 (DIRECTOR_RULING_FAILURE_BIAS_LAWS 2026-07-27): the note must report the
    EFFECT, not merely the STATUS ("lane WIRED"), and it must derive that from PRIMARY state --
    never solely from the tick's own published enumeration.

    So this cross-checks two sources that can disagree: the tick's enumeration (`r17_status()`,
    source A) against an INDEPENDENT read of `in_progress/` (source B, `primary_state_scan`, which
    imports nothing from supervisor.py). If the enumeration claims REST-LEGITIMATE while the
    independent read finds a self-drawable mint UNDRAWN, that is exactly the 42h-stall class -- a
    false "empty" claim -- and the note renders it 🔴, visible from the second source. §2-severed:
    a READ only, never a number that feeds the draw. Fail-closed to a RED, never a flattering ✅."""
    from background.primary_state_scan import drawable_undrawn_mints
    d = in_progress_dir or IN_PROGRESS_DIR
    try:
        undrawn = drawable_undrawn_mints(d)
    except Exception as e:  # noqa: BLE001 — an unavailable independent read is a RED, never a silent green
        return _red(f"LAW-C independent primary-state read unavailable: {e}")
    status_line, _status_err = _status_fn()
    up = (status_line or "").upper()
    claims_rest = bool(status_line) and "REST-LEGITIMATE" in up and "MUST-DRAW" not in up
    if undrawn:
        names = ", ".join(n for n, _ in undrawn[:6]) + ("…" if len(undrawn) > 6 else "")
        if claims_rest:
            return ("🔴 CONTRADICTION (LAW C): the tick's enumeration reports REST-LEGITIMATE, but an "
                    f"INDEPENDENT read of in_progress/ shows **{len(undrawn)} self-drawable mint(s) "
                    f"UNDRAWN** ({names}). Two sources disagree — the enumeration is not to be trusted "
                    "alone; this is drawable work the tick is silently not drawing (the 42h-stall class).")
        return (f"⚠ EFFECT: {len(undrawn)} self-drawable mint(s) currently undrawn in in_progress/ "
                f"({names}); the enumeration DOES flag must-draw, so the two sources AGREE (no false rest).")
    return ("✅ LAW-C cross-check: no self-drawable mint sits undrawn in in_progress/ — the "
            "independent primary-state read AGREES with the tick's enumeration (no false-empty).")


def named_and_not_done_line(
    staging_dir: Path | None = None,
    in_progress_dir: Path | None = None,
    done_dir: Path | None = None,
) -> str:
    """§5 (DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE 2026-07-27, RESTATED): make
    "no below-target work anywhere" CHECKABLE, not merely asserted. Renders the current
    NAMED-BUT-UNMINTED enumeration — deliverables named in a ruling/steer's WORK THIS
    CREATES block that no mint doc (or the ruling's own coverage banner) covers.

    Derived by `primary_state_scan.named_but_unminted`, which reads ONLY primary state
    (the rulings + the staging tree) and imports nothing from the tick's draw — so this
    line is the SECOND source that can contradict a false "idle" claim (LAW C). §2-severed:
    a READ only, never a number that feeds the draw. Fail-closed to a RED, never a
    flattering ✅ (an unreadable primary state is a FAILED check, R15)."""
    from background.primary_state_scan import named_but_unminted
    try:
        residue = named_but_unminted(staging_dir, in_progress_dir, done_dir)
    except Exception as e:  # noqa: BLE001 — an unavailable independent read is a RED, never a silent green
        return _red(f"§5 named-but-unminted enumeration unavailable: {e}")
    if not residue:
        return ("✅ §5 named-but-unminted: EMPTY — every deliverable named in a ruling/steer's "
                "WORK THIS CREATES block is covered by a mint or a landed-coverage marker "
                "(so 'no below-target work' is CHECKED against primary state, not asserted).")
    items = "; ".join(f"{r['ruling'].replace('.md','')}#{r['index']} \"{r['deliverable'][:60]}\""
                      for r in residue[:6]) + ("…" if len(residue) > 6 else "")
    return (f"🔴 §5 named-but-unminted: **{len(residue)} deliverable(s)** named in a ruling but NOT "
            f"minted into an atom — 'no below-target work' is FALSE while these stand: {items}. "
            "Mint one atom per residue item (source → lane → target level → exit criteria).")


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
                     f"{vw['republish_count']} mechanical republish(es) excluded; "
                     f"{vw['harden_count']} HARDEN re-verify(s) excluded (§1 — never counts as work).")
        for s in vw["substantive_subjects"][:8]:
            lines.append(f"    - {s}")
        if vw["substantive_count"] == 0:
            lines.append("    - ⚠ ZERO verified product progress this window (full pipeline liveness ≠ autonomy).")

    # DIRECTOR-RULING 2026-07-23 (PRODUCT FIRST): the headline split + the one plain-words question.
    lines += ["", "**PRODUCT vs MACHINERY** _(DIRECTOR-RULING 2026-07-23 — the headline; "
              "diagnostic-never-target, definitions provisional/ledger-governed)_"]
    if vw_err:
        lines.append(f"- {_red(vw_err)}")
    else:
        lines.append(f"- **PRODUCT: {vw['product_count']}** · MACHINERY: {vw['machinery_count']} "
                     "_(substantive commits; regenerated site/docs churn already excluded upstream)_")
        for s in vw["product_subjects"][:8]:
            lines.append(f"    - 🟢 {s}")
        lines.append("- **What can the director SEE or JUDGE today that he could not yesterday?** "
                     "— agent narrates in product terms (the note computes the split; it cannot judge visibility).")
        if vw["product_count"] == 0 and vw["machinery_count"] > 0:
            lines.append("    - 🔴 PRODUCT=0, MACHINERY-only window. Per the ruling: **the day FAILED "
                         "regardless of how many machinery classes got fixed.**")

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
    # LAW C item 2 (2026-07-27): the note must report EFFECT, not just the WIRED status above, and
    # must cross-check the enumeration against an INDEPENDENT primary-state read so a false "empty"
    # is visible from the second source. (Full dead-hours-with-work time-series is a named LAW-C
    # follow-on; this lands the independence cross-check + the current-snapshot effect.)
    lines.append(f"- {r17_effect_crosscheck()}")
    # §5 (WORK_DEFINITION ruling 2026-07-27, RESTATED): the named-but-unminted enumeration makes
    # "no below-target work" a CHECKABLE claim against primary state — the exact §0 failure (the tick
    # asserted "no below-target work anywhere" while three named items sat unminted) is now caught.
    lines.append(f"- {named_and_not_done_line()}")

    # DIRECTOR_AXES twin pre-score gap (read-only; §2-severed — a diagnostic the
    # note reads, never a number that feeds the draw). Fail-closed on import/read.
    lines += ["", "**Twin pre-score gap** _(belief-vs-truth on the director; Law B — never trains the twin)_"]
    try:
        from background.axis_prescore import retro_gap_line
        lines.append(f"- {retro_gap_line()}")
    except Exception as e:  # noqa: BLE001 — honest RED, never a fabricated gap
        lines.append(f"- {_red(f'twin pre-score gap unavailable: {e}')}")

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
            from background.notify import notify
            # The daily note is a once-per-day DIGEST (G-N2), routed through the ONE contract
            # rather than a direct send_ntfy path. Idempotency is already guaranteed by
            # already_ran_today()/the day-stamp above, so no transition_key is needed here.
            send = lambda m: notify(m, kind="digest", headers={"Title": "Daily self-note"})  # noqa: E731
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
