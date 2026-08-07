"""STOP-CONTROL AUDIT — the falsifier for `docs/design/STOP_CONTROL_GAP.md`.

Atom `H_stop_control_gap_characterisation` (SPEC_005 §7.13, material safety). The DISCOVER
half produced the inventory doc; that doc is PROSE, and prose about what can be stopped decays
silently — a control it lists gets retired, a cited test gets renamed, a daemon it claims to
halt goes `retired` in the process manifest, and the document keeps reading as reassurance.

This module is the doc's machine-readable half and its falsifier. The atom's own mint note set
the bar (R15, OUTCOME-test form): *"a characterisation that lists only the stops that WORK has
demonstrated nothing — the artefact must name the known gaps and be checkable against the live
process set, so a later reader can falsify it by finding a stop it claims exists that does
not."* That is exactly what `audit()` does.

INDEPENDENCE (R15 TAUTOLOGY killer). The registry below is the CLAIM. It is never checked
against itself — every check resolves against a source the registry does not control:
  - module/symbol claims  -> the real file's real source text
  - flag claims           -> the literal flag name appearing in the reader's source
  - cited-test claims     -> `def <name>(` in the real test file
  - reach-of-a-stop claims-> `background/process_manifest.yaml`'s declared state
  - the headline verdict  -> the verdict sentence written in the doc
A control that claims to halt a process the manifest declares `retired` halts NOTHING; that is
a DEAD_TARGET defect, not a footnote.

FAIL-CLOSED (R15 FAIL-SILENT / FAIL-OPEN killers). A missing doc, a missing manifest, or a
malformed either RAISES — an unavailable check is a FAILED check, never a silent pass. An empty
registry, or a registry with no live stop control in it, is VACUOUS and reported as a violation
(a population control that passes because the population is empty is worse than none). A control
claimed as live with no cited test is an UNTESTED_CLAIM, not a pass.

WHAT THIS IS NOT: it adds, wires, and modifies no stop control. It is an auditor of the
existing inventory. The residual gap it measures — a director-window-reachable, authenticated,
mid-flight stop — remains open; see §3/§4 of the doc.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

PROJECT_DIR = Path(__file__).resolve().parent.parent
GAP_DOC_PATH = PROJECT_DIR / "docs" / "design" / "STOP_CONTROL_GAP.md"
PROCESS_MANIFEST_PATH = PROJECT_DIR / "background" / "process_manifest.yaml"

# A control classified `stop_control` is claimed to be a LIVE affordance that halts something.
# `not_a_stop_control` is the honest-record classification: the row stays in the inventory
# (retired paths, detectors, rate limiters) but claims no stopping power, so the manifest-state
# and cited-test requirements do not apply to it.
CLASSIFICATIONS = frozenset({"stop_control", "not_a_stop_control"})

# How a human reaches the control. `window` is the bar SPEC_005 §7.13 actually sets
# (≤1 screen from the director landing); `console` is a terminal-only filesystem flag;
# `automatic` fires on an internal condition and is not human-reachable at all.
REACHES = frozenset({"window", "console", "automatic"})

# Manifest states in which a process can still be stopped by something. A `retired` process
# must never run, so a control claiming to halt it halts nothing.
_STOPPABLE_STATES = frozenset({"enabled", "dark", "held"})


@dataclass(frozen=True)
class StopControl:
    """One row of the inventory, as a checkable claim."""

    id: int
    name: str
    classification: str
    reach: str
    # Does it terminate work ALREADY IN FLIGHT, or only prevent the next cycle starting?
    mid_flight: bool
    module: str
    symbols: tuple[str, ...] = ()
    # Durable flag file it reads (final path component is what appears in source).
    flag: str | None = None
    flag_readers: tuple[str, ...] = ()
    # Manifest `session` names this control can actually halt.
    halts_processes: tuple[str, ...] = ()
    cited_tests: tuple[str, ...] = ()
    note: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# THE REGISTRY — one entry per row of §1 of the doc. Ids must match the doc's table.
# ─────────────────────────────────────────────────────────────────────────────
REGISTRY: tuple[StopControl, ...] = (
    StopControl(
        id=1,
        name="`.build_executor_enabled` — the one durable kill switch for autonomous execution",
        classification="stop_control",
        reach="console",
        mid_flight=False,
        module="background/executor_governor.py",
        symbols=("kill_switch_enabled",),
        flag="docs/observability/.build_executor_enabled",
        flag_readers=(".claude/hooks/pull_next_work.py", "background/worker_tick.py"),
        halts_processes=("executor-daemon", "claude"),
        cited_tests=(
            "tests/background/test_executor_governor.py::test_run_loop_continues_until_kill_switch_flips",
            "tests/background/test_executor_governor.py::test_governor_never_writes_the_enable_flag",
            "tests/background/test_worker_tick.py::test_kill_switch_disabled_no_spawn",
            "tests/background/test_worker_tick.py::test_autonomy_enabled_fail_closed",
        ),
        note="Fail-closed on absence. Effective at the loop/cycle boundary only — stops the NEXT "
             "turn being dispatched, never the one already running.",
    ),
    StopControl(
        id=2,
        name="`.sim_runner_hold` — director hold on starting new simulation runs",
        classification="stop_control",
        reach="console",
        mid_flight=False,
        module="background/sim_runner.py",
        symbols=("HOLD_FLAG", "_check_hold", "FORCE_REPUBLISH_FLAG"),
        flag="docs/review_gates/.sim_runner_hold",
        flag_readers=("background/sim_runner.py",),
        halts_processes=("sim-runner",),
        cited_tests=(
            "tests/background/test_sim_runner.py::test_check_hold_flag_present_skips_and_marks_held",
            "tests/background/test_sim_runner.py::test_check_hold_flag_still_present_stays_held_no_relog",
            "tests/background/test_sim_runner.py::test_check_hold_cleared_transition_touches_force_republish_flag",
        ),
        note="The one control whose RELEASE side-effect is tested end-to-end (no orphan "
             "transition, R11/OPS1). Still boundary-only: no kill of an in-flight run.",
    ),
    StopControl(
        id=3,
        name="R3 two-strike halt (`MAX_CONSECUTIVE_FAILURES`)",
        classification="not_a_stop_control",
        reach="automatic",
        mid_flight=False,
        module="background/executor_governor.py",
        symbols=("MAX_CONSECUTIVE_FAILURES", "repeated_failure"),
        note="A self-diagnosed halt, not a human-triggered stop. Inventory completeness only — "
             "it cannot satisfy §7.13's 'reach a stop control'.",
    ),
    StopControl(
        id=4,
        name="`TurnBudget` sliding-window cap",
        classification="not_a_stop_control",
        reach="automatic",
        mid_flight=False,
        module="background/executor_governor.py",
        symbols=("TurnBudget",),
        note="A rate limiter that self-clears as the window slides. Not director-triggered.",
    ),
    StopControl(
        id=5,
        name="`code_stale` self-staleness re-exec",
        classification="not_a_stop_control",
        reach="automatic",
        mid_flight=False,
        module="background/executor_daemon.py",
        symbols=("source_fingerprint", "code_stale"),
        note="Self-healing re-exec of the daemon's own process, not a stop control.",
    ),
    StopControl(
        id=6,
        name="Page-comment intake lock (`.comment_intake_locked`) — RETIRED, halts nothing",
        classification="not_a_stop_control",
        reach="console",
        mid_flight=False,
        module="background/director_comments.py",
        symbols=("main",),
        halts_processes=("director-comments",),
        note="FALSIFIED BY THIS AUDIT, 2026-08-03. The 2026-07-28 inventory listed this as an "
             "existing director-only halt flag. It is not one: the channel was RETIRED "
             "permanently on 2026-07-24 (DIRECTOR_RULING_RETIRE_PAGE_COMMENT_CHANNEL), the "
             "module's intake path is DELETED, `main()` is a permanent safe no-op, no source "
             "here references `.comment_intake_locked` at all, and the process manifest declares "
             "`director-comments` state=retired. A lock over a process that must never run stops "
             "nothing. Kept as an inventory row, reclassified to its true status.",
    ),
    StopControl(
        id=7,
        name="Per-turn timeout / surplus-child kill (`reap_turn`)",
        classification="not_a_stop_control",
        reach="automatic",
        mid_flight=True,
        module="background/build_executor.py",
        symbols=("reap_turn", "_reap_surplus_child"),
        note="The ONE place the codebase already terminates a live child (`proc.kill()`), so a "
             "director-triggered mid-flight stop is a small delta rather than new invention. "
             "But it fires on an internal deadline / landed-evidence condition and is not "
             "reachable by a human — it does not close the residual.",
    ),
    StopControl(
        id=8,
        name="Dead-man's switch",
        classification="not_a_stop_control",
        reach="automatic",
        mid_flight=False,
        module="background/deadmans_switch.py",
        symbols=("BLOCKED_THRESHOLD_SECONDS", "SILENT_STALL_THRESHOLD_SECONDS"),
        note="A detector/alarm. It halts nothing — listed to rule it out explicitly, because it "
             "is informally described as a safety net.",
    ),
)


class StopControlAuditError(RuntimeError):
    """The audit could not run. An unavailable check is a FAILED check (R15)."""


@dataclass
class AuditResult:
    violations: list[str] = field(default_factory=list)
    live_controls: list[int] = field(default_factory=list)
    derived_verdict: str = ""
    residual: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


def _read(path: Path) -> str:
    if not path.exists():
        raise StopControlAuditError(f"required file missing: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def load_process_states(path: Path | None = None) -> dict[str, str]:
    """session -> declared state, from the ONE authoritative process manifest.
    Raises on missing/malformed — never returns an empty map as a silent pass."""
    p = path or PROCESS_MANIFEST_PATH
    data = yaml.safe_load(_read(p))
    if not isinstance(data, dict) or not isinstance(data.get("processes"), list):
        raise StopControlAuditError(f"process manifest malformed (no 'processes' list): {p}")
    states = {
        proc["session"]: proc.get("state")
        for proc in data["processes"]
        if isinstance(proc, dict) and proc.get("session")
    }
    if not states:
        raise StopControlAuditError(f"process manifest declares no processes: {p}")
    return states


def doc_row_ids(doc_text: str) -> set[int]:
    """The control ids the inventory table actually claims. Independent of the registry."""
    return {int(m) for m in re.findall(r"^\|\s*(\d+)\s*\|", doc_text, re.MULTILINE)}


def doc_verdict(doc_text: str) -> str:
    """The headline coverage verdict as WRITTEN in the doc (PARTIAL / MET / NONE)."""
    m = re.search(r"Coverage verdict:?\*{0,2}\s*\*{0,2}(PARTIAL|MET|NONE)", doc_text)
    if not m:
        raise StopControlAuditError(
            "STOP_CONTROL_GAP.md states no 'Coverage verdict: <PARTIAL|MET|NONE>' — the "
            "doc's headline conclusion cannot be checked against reality"
        )
    return m.group(1)


def _derive_verdict(controls: tuple[StopControl, ...]) -> tuple[str, list[str]]:
    """The verdict the REGISTRY implies, and the residual gaps behind it.

    §7.13 is MET only when a live stop control is both window-reachable and able to halt
    work already in flight. Anything less is PARTIAL; no live control at all is NONE.
    """
    live = [c for c in controls if c.classification == "stop_control"]
    if not live:
        return "NONE", ["no live stop control of any kind"]
    residual = []
    if not any(c.reach == "window" for c in live):
        residual.append("no director-window-reachable stop affordance (all are console-only)")
    if not any(c.mid_flight for c in live):
        residual.append("no stop halts work already in flight (all act at a cycle boundary)")
    return ("MET" if not residual else "PARTIAL"), residual


def _check_vocabulary(c: StopControl, tag: str) -> list[str]:
    out = []
    if c.classification not in CLASSIFICATIONS:
        out.append(f"{tag}: unknown classification {c.classification!r}")
    if c.reach not in REACHES:
        out.append(f"{tag}: unknown reach {c.reach!r}")
    return out


def _check_module_symbols(c: StopControl, tag: str, root: Path) -> list[str]:
    """Oracle: the implementing file's real source text."""
    module_path = root / c.module
    if not module_path.exists():
        return [f"{tag}: MODULE_MISSING — {c.module} does not exist"]
    source = module_path.read_text(encoding="utf-8", errors="replace")
    return [
        f"{tag}: SYMBOL_MISSING — {c.module} no longer contains {sym!r}"
        for sym in c.symbols
        if sym not in source
    ]


def _check_flag_readers(c: StopControl, tag: str, root: Path) -> list[str]:
    """Oracle: the literal flag name in the source of each module said to read it. A flag file
    is only a control because something reads it."""
    if not c.flag:
        return []
    flag_name = Path(c.flag).name
    out = []
    if not c.flag_readers:
        out.append(f"{tag}: UNREAD_FLAG — claims flag {c.flag} but names no reader")
    for reader in c.flag_readers:
        reader_path = root / reader
        if not reader_path.exists():
            out.append(f"{tag}: READER_MISSING — {reader} does not exist")
        elif flag_name not in reader_path.read_text(encoding="utf-8", errors="replace"):
            out.append(f"{tag}: FLAG_UNREFERENCED — {reader} does not reference {flag_name}")
    return out


def _check_halt_targets(c: StopControl, tag: str, states: dict[str, str], live: bool) -> list[str]:
    """Oracle: the process manifest's declared state. This is the check that found row 6."""
    out = []
    for session in c.halts_processes:
        state = states.get(session)
        if state is None:
            out.append(f"{tag}: UNKNOWN_PROCESS — {session!r} is not in the process manifest")
        elif live and state not in _STOPPABLE_STATES:
            out.append(
                f"{tag}: DEAD_TARGET — claims to halt {session!r}, which the manifest declares "
                f"state={state!r}; a control over a process that must never run halts nothing"
            )
    return out


def _check_cited_tests(c: StopControl, tag: str, root: Path, live: bool) -> list[str]:
    """Oracle: `def <name>(` in the real test file. The inventory's 'Release tested?' column is
    otherwise a claim about nothing."""
    out = []
    if live and not c.cited_tests:
        out.append(f"{tag}: UNTESTED_CLAIM — claimed as a live stop control with no cited test")
    for cite in c.cited_tests:
        if "::" not in cite:
            out.append(f"{tag}: malformed test citation {cite!r}")
            continue
        rel, test_name = cite.split("::", 1)
        test_path = root / rel
        if not test_path.exists():
            out.append(f"{tag}: TEST_FILE_MISSING — {rel}")
        elif f"def {test_name}(" not in test_path.read_text(encoding="utf-8", errors="replace"):
            out.append(f"{tag}: TEST_MISSING — {rel} no longer defines {test_name}")
    return out


def _check_doc_alignment(controls: tuple[StopControl, ...], doc_text: str) -> list[str]:
    """Oracle: the `| N |` rows of the document itself — the doc must not grow a row nobody
    checks, nor lose one the registry still claims."""
    out = []
    row_ids = doc_row_ids(doc_text)
    registry_ids = {c.id for c in controls}
    if unchecked := row_ids - registry_ids:
        out.append(
            f"DOC_ROW_UNCHECKED — STOP_CONTROL_GAP.md §1 lists control(s) {sorted(unchecked)} "
            f"that this audit does not check"
        )
    if phantom := registry_ids - row_ids:
        out.append(
            f"REGISTRY_ROW_UNDOCUMENTED — registry control(s) {sorted(phantom)} appear in no "
            f"row of STOP_CONTROL_GAP.md §1"
        )
    return out


def audit(
    controls: tuple[StopControl, ...] | None = None,
    doc_path: Path | None = None,
    manifest_path: Path | None = None,
    project_dir: Path | None = None,
) -> AuditResult:
    """Check every registry claim against real state. Empty violations == the audit passes."""
    controls = REGISTRY if controls is None else controls
    root = project_dir or PROJECT_DIR
    doc_text = _read(doc_path or GAP_DOC_PATH)
    states = load_process_states(manifest_path)
    result = AuditResult()

    # VACUITY GUARD — a population check that passes on an empty population proves nothing.
    if not controls:
        result.violations.append("VACUOUS: the stop-control registry is empty")
        return result

    seen_ids: set[int] = set()
    for c in controls:
        tag = f"control #{c.id}"
        if c.id in seen_ids:
            result.violations.append(f"{tag}: DUPLICATE id in the registry")
        seen_ids.add(c.id)
        live = c.classification == "stop_control"

        result.violations += _check_vocabulary(c, tag)
        result.violations += _check_module_symbols(c, tag, root)
        result.violations += _check_flag_readers(c, tag, root)
        result.violations += _check_halt_targets(c, tag, states, live)
        result.violations += _check_cited_tests(c, tag, root, live)

        if live:
            result.live_controls.append(c.id)

    if not result.live_controls:
        result.violations.append(
            "VACUOUS: no control is classified `stop_control` — the inventory claims no live "
            "stopping power at all"
        )

    # -- the doc's own table must not drift from what gets checked ---------------
    result.violations += _check_doc_alignment(controls, doc_text)

    # -- the doc's headline verdict must match what the registry now implies -----
    result.derived_verdict, result.residual = _derive_verdict(controls)
    written = doc_verdict(doc_text)
    if written != result.derived_verdict:
        result.violations.append(
            f"VERDICT_STALE — STOP_CONTROL_GAP.md states coverage verdict {written}, but the "
            f"audited controls imply {result.derived_verdict}"
            + (f" (residual: {'; '.join(result.residual)})" if result.residual else "")
        )

    return result


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        result = audit()
    except StopControlAuditError as exc:
        print(f"STOP-CONTROL AUDIT UNAVAILABLE (= FAILED): {exc}", file=sys.stderr)
        return 2
    print(f"stop-control audit: {len(REGISTRY)} inventory rows, "
          f"{len(result.live_controls)} live control(s) {result.live_controls}")
    print(f"derived coverage verdict: {result.derived_verdict}")
    for gap in result.residual:
        print(f"  RESIDUAL: {gap}")
    if result.ok:
        print("PASS — every claim in STOP_CONTROL_GAP.md resolves against real state")
        return 0
    print(f"FAIL — {len(result.violations)} violation(s):", file=sys.stderr)
    for v in result.violations:
        print(f"  - {v}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    try:  # seat guard, FIRST act -- refuse to start on foreign soil (background/_seat.py)
        from background._seat import refuse_if_foreign
    except ModuleNotFoundError:  # launched as `python3 background/stop_control_audit.py`
        from _seat import refuse_if_foreign
    refuse_if_foreign("stop_control_audit")
    raise SystemExit(main())
