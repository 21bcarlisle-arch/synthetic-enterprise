"""Tests for the PULL-LOOP Stop hook (.claude/hooks/pull_next_work.py,
STAGING_PULL_LOOP_RESCOPE.md, 2026-07-15).

Proves the transport's safety invariants WITHOUT enabling it on any live session:
gated-off-by-default, loop-guard, WORKER-SEAT-ONLY (never the sanctified console),
fail-safe on a broken draw, checkpoint cadence, and -- the load-bearing one --
ZERO pane writes (the hook only returns JSON; it never types into a pane, the
whole point of replacing keystroke injection).
"""
import importlib.util
import json
from pathlib import Path

import pytest

HOOK_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "pull_next_work.py"

# The dedicated worker-seat conversation id (must equal worker_seat.WORKER_SESSION_ID
# -- proven by test_worker_session_id_matches_seat_single_source_of_truth below).
WORKER_ID = "22080be5-e19e-4099-a007-d71c3a6e7845"
# A distinct id standing in for the director's sanctified console (or any other session).
CONSOLE_ID = "004ea979-3496-42f2-8a23-c406b531ea9d"


def _wp(session_id=WORKER_ID, **extra):
    """Build a Stop-hook payload for the WORKER seat (real field name `session_id`,
    verified against a dumped live payload 2026-07-17). Pass session_id=... to
    simulate the console/another session."""
    p = {"stop_hook_active": False, "session_id": session_id}
    p.update(extra)
    return p


def _load_hook(tmp_path, monkeypatch, *, enabled, draw_result):
    spec = importlib.util.spec_from_file_location("pull_next_work", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "ENABLE_FLAG", tmp_path / ".build_executor_enabled")
    monkeypatch.setattr(mod, "LOG_FILE", tmp_path / "pull-loop-log.md")
    monkeypatch.setattr(mod, "STATE_FILE", tmp_path / ".pull_loop_state.json")
    # ISOLATION (2026-07-17): decide() now writes _write_health on every worker path. Without
    # patching HEALTH_FILE these tests wrote outcomes (incl. a DRAW_ERROR) into the REAL
    # .pull_loop_health.json, which the live deadman then paged as a SPURIOUS [LOOP BROKEN].
    # Same leak class as the LOG_FILE one -- a test must never write a live observability signal.
    monkeypatch.setattr(mod, "HEALTH_FILE", tmp_path / ".pull_loop_health.json")
    # Pin the worker id so tests don't depend on the live seat's real id.
    monkeypatch.setattr(mod, "WORKER_SESSION_ID", WORKER_ID)
    if enabled:
        (tmp_path / ".build_executor_enabled").write_text("")
    # Inject the draw result without importing the real supervisor.
    import sys, types
    fake = types.ModuleType("background.supervisor")
    fake.find_work = lambda resumed_from_pause=False: draw_result
    monkeypatch.setitem(sys.modules, "background.supervisor", fake)
    return mod


def test_disabled_by_default_allows_stop(tmp_path, monkeypatch):
    mod = _load_hook(tmp_path, monkeypatch, enabled=False, draw_result=("A6 has work", False))
    assert mod.decide(_wp()) is None  # no flag -> inert, even for the worker seat


def test_kill_switch_flag_off_refuses_next_boundary(tmp_path, monkeypatch):
    """R15 KILL-SWITCH PROOF (DIRECTOR_ANSWERS_C7 #6): with the single flag OFF,
    the very next turn boundary MUST refuse to continue. A kill switch never
    proven to kill is a theatre control (kill-list doctrine)."""
    mod = _load_hook(tmp_path, monkeypatch, enabled=False, draw_result=("lots of work", False))
    # flag absent -> refuse (session stops)
    assert mod.decide(_wp()) is None
    # fail-closed: a MALFORMED flag (a directory, not a readable file) -> DISABLED
    (tmp_path / ".build_executor_enabled").mkdir()
    assert mod.decide(_wp()) is None
    # mutation proof the guard is load-bearing: neuter it (force-enable) and the
    # same flag-off state now WRONGLY continues -> the guard is what gates the kill.
    monkeypatch.setattr(mod, "_autonomous_execution_enabled", lambda: True)
    assert mod.decide(_wp()) is not None


def test_self_sustains_across_continuations_not_one_shot(tmp_path, monkeypatch):
    """SELF-SUSTAIN (director P0, 2026-07-17): the old `stop_hook_active -> stop` one-shot made the
    loop do ONE continuation then idle until an unreliable external Stop re-armed it (the
    ~100-min-idle-with-work-queued disease). Now a CONTINUED turn (stop_hook_active=True) with work
    STILL continues -- the chain sustains turn to turn on its own draw."""
    mod = _load_hook(tmp_path, monkeypatch, enabled=True, draw_result=("more queued work", False))
    for shook_active in (False, True, True, True, True):
        out = mod.decide(_wp(stop_hook_active=shook_active))
        assert out is not None and out["decision"] == "block", "chain must NOT die on stop_hook_active"
        assert "more queued work" in out["reason"]


def test_worker_seat_pulled_but_console_and_others_are_exempt(tmp_path, monkeypatch):
    """G-L1 CONSOLE-PULL FIX (2026-07-17): the Stop hook fires on EVERY session in
    the project. It must pull ONLY the dedicated worker seat; the director's
    sanctified console -- and any other/ad-hoc session -- must be left to stop.
    Both directions, the R15 blind spot the old tests never exercised (they passed
    no session id at all)."""
    mod = _load_hook(tmp_path, monkeypatch, enabled=True,
                     draw_result=("self-refill: BUILD SITE1_expert_doors", False))
    # WORKER seat -> BLOCK + draw (pulled)
    out = mod.decide(_wp(session_id=WORKER_ID))
    assert out is not None and out["decision"] == "block"
    assert "SITE1_expert_doors" in out["reason"]
    # CONSOLE (sanctified) -> allow stop, NEVER pulled, even with work waiting
    assert mod.decide(_wp(session_id=CONSOLE_ID)) is None
    # some other ad-hoc session -> allow stop
    assert mod.decide(_wp(session_id="deadbeef-0000-0000-0000-000000000000")) is None
    # absent session_id (defensive) -> allow stop (positive identification required)
    assert mod.decide({"stop_hook_active": False}) is None


def test_fail_safe_unresolved_worker_id_pulls_nobody(tmp_path, monkeypatch):
    """FAIL-SAFE DIRECTION (the exact concern that gated this fix): if the worker id
    can't be resolved (import failed -> WORKER_SESSION_ID is None), NO session may be
    pulled -- not even one carrying the real worker id. Autonomy pauses (safe); the
    console is never wrongly pulled. A wrong/absent id must fail toward NOT acting on
    the console, never toward pulling everyone."""
    mod = _load_hook(tmp_path, monkeypatch, enabled=True, draw_result=("work", False))
    monkeypatch.setattr(mod, "WORKER_SESSION_ID", None)
    assert mod.decide(_wp(session_id=WORKER_ID)) is None  # nobody matches None
    assert mod.decide({"stop_hook_active": False}) is None


def test_enabled_with_work_blocks_and_feeds_the_draw(tmp_path, monkeypatch):
    mod = _load_hook(tmp_path, monkeypatch, enabled=True,
                     draw_result=("self-refill: BUILD SITE1_expert_doors", False))
    out = mod.decide(_wp())
    assert out is not None and out["decision"] == "block"
    assert "SITE1_expert_doors" in out["reason"]
    assert "PULL-LOOP doorbell" in out["reason"]  # R7 doorbell framing carried


def test_enabled_but_no_work_allows_stop(tmp_path, monkeypatch):
    mod = _load_hook(tmp_path, monkeypatch, enabled=True, draw_result=(None, True))
    assert mod.decide(_wp()) is None


def test_fail_safe_allows_stop_when_draw_raises(tmp_path, monkeypatch):
    import sys, types
    mod = _load_hook(tmp_path, monkeypatch, enabled=True, draw_result=("x", False))
    boom = types.ModuleType("background.supervisor")
    def _raise(**k): raise RuntimeError("draw broken")
    boom.find_work = _raise
    monkeypatch.setitem(sys.modules, "background.supervisor", boom)
    # A broken draw must NEVER block the session (fail-safe: allow the stop).
    assert mod.decide(_wp()) is None


def test_instrumented_three_consecutive_boundaries_draw_and_continue(tmp_path, monkeypatch):
    """ACTIVATION PROOF (DIRECTOR_ANSWERS_C7 #2): with work available, THREE
    consecutive turn boundaries each DRAW and CONTINUE, and the pull-loop LOG
    records each -- with ZERO pane writes (the hook spawns no process). This is
    the instrumented proof that gates the flag-flip."""
    import importlib.util, sys, types
    spec = importlib.util.spec_from_file_location("pull_next_work", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    log = tmp_path / "pull-loop-log.md"
    monkeypatch.setattr(mod, "ENABLE_FLAG", tmp_path / ".build_executor_enabled")
    monkeypatch.setattr(mod, "LOG_FILE", log)
    monkeypatch.setattr(mod, "STATE_FILE", tmp_path / ".state.json")
    monkeypatch.setattr(mod, "HEALTH_FILE", tmp_path / ".pull_loop_health.json")  # isolation (no real-file leak)
    monkeypatch.setattr(mod, "WORKER_SESSION_ID", WORKER_ID)
    (tmp_path / ".build_executor_enabled").write_text("")  # enabled (test flag, not the console one)
    draws = iter([("BUILD SITE1_expert_doors", False), ("BUILD F6_bill_integrity", False), ("HARDEN A6_gap", False)])
    fake = types.ModuleType("background.supervisor")
    fake.find_work = lambda resumed_from_pause=False: next(draws)
    monkeypatch.setitem(sys.modules, "background.supervisor", fake)

    reasons = []
    for _ in range(3):  # three consecutive turn boundaries
        out = mod.decide(_wp())
        assert out is not None and out["decision"] == "block", "boundary must draw + continue"
        reasons.append(out["reason"])

    assert "SITE1" in reasons[0] and "F6" in reasons[1] and "A6" in reasons[2]  # distinct real work each
    assert log.read_text().count("BLOCK+continue") == 3  # instrumented: 3 boundaries logged


def test_checkpoint_cadence_injects_compact(tmp_path, monkeypatch):
    mod = _load_hook(tmp_path, monkeypatch, enabled=True, draw_result=("keep building", False))
    last = None
    for _ in range(mod.CHECKPOINT_EVERY):
        last = mod.decide(_wp())
    assert "CHECKPOINT" in last["reason"] and "/compact" in last["reason"]


def test_hook_cannot_write_to_a_pane_structurally():
    # The load-bearing safety invariant: this hook NEVER types into a pane. The
    # structural guarantee is that it spawns NO process at all -- you cannot
    # tmux/xdotool your way into a pane without a subprocess. (The docstring may
    # DESCRIBE replacing keystroke injection; that's documentation, not code.)
    import ast
    src = HOOK_PATH.read_text()
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "subprocess" not in imported, "pull-loop hook must spawn no process"
    for banned in ("Popen", "os.system", "os.popen", "check_output", "send-keys"):
        # in EXECUTABLE code only (exclude the module docstring)
        body = src.split('"""', 2)[-1] if src.count('"""') >= 2 else src
        assert banned not in body, f"pane-write primitive {banned!r} in hook code"


def test_worker_session_id_matches_seat_single_source_of_truth():
    """DRIFT GUARD (R15 independence): the id the hook filters on MUST be the id the
    worker seat actually seeds with -- otherwise the filter could silently diverge
    from the seat (a wrong id fails closed => the console-pull fix stops pulling the
    worker => serial autonomy dies silently, the fail-silent family). The hook
    imports it from worker_seat, so this asserts that single source of truth held and
    that the test's own WORKER_ID constant tracks it too."""
    spec = importlib.util.spec_from_file_location("pull_next_work_realid", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import sys
    sys.path.insert(0, str(HOOK_PATH.resolve().parents[2]))
    from background.worker_seat import WORKER_SESSION_ID as seat_id
    assert mod.WORKER_SESSION_ID == seat_id, "hook filter id drifted from the seat's seed id"
    assert WORKER_ID == seat_id, "this test's WORKER_ID constant drifted from the seat's seed id"


def test_project_dir_resolves_to_repo_root_not_dotclaude():
    """Production-path regression (2026-07-16): PROJECT_DIR must be the REPO ROOT,
    not <repo>/.claude. The hook lives at <repo>/.claude/hooks/, so it is TWO
    levels up (parents[2]); the old `.parent.parent` gave <repo>/.claude, so the
    REAL enable flag at <repo>/docs/observability/.build_executor_enabled was
    never read and kill_switch_enabled() was permanently False -- the daemon and
    Stop hook silently refused to run. Every other test monkeypatches ENABLE_FLAG
    to a tmp path, so ONLY this test exercises the real resolution (the R15
    lesson: a control mocked away from its integration path can't fire in prod)."""
    repo_root = HOOK_PATH.resolve().parents[2]
    spec = importlib.util.spec_from_file_location("pull_next_work_realpath", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert mod.PROJECT_DIR == repo_root, (
        f"PROJECT_DIR resolved to {mod.PROJECT_DIR}, expected repo root {repo_root}"
    )
    # It must be a real repo root, not the .claude subdir.
    assert mod.PROJECT_DIR.name != ".claude"
    assert (mod.PROJECT_DIR / "background").is_dir()
    assert (mod.PROJECT_DIR / ".claude" / "hooks").is_dir()
    # The enable flag must point at the ONE real, director-set location.
    assert mod.ENABLE_FLAG == repo_root / "docs" / "observability" / ".build_executor_enabled"


def test_hook_puts_repo_root_on_syspath_so_import_works_from_alien_cwd():
    """Regression (serial-autonomy maiden-turn watch, 2026-07-17): loading the hook from a cwd
    that is NOT the repo root must make `import background` resolve. The Stop hook runs with an
    arbitrary cwd; without the sys.path fix `from background.supervisor import find_work` raised
    ModuleNotFoundError('background') on EVERY fire and fail-safe'd to allow-stop -- the transport
    silently NEVER delivered work. Every other test mocks background.supervisor, so ONLY this
    exercises the real import path from an alien cwd (subprocess from /tmp to replicate)."""
    import subprocess
    import sys
    import textwrap
    code = textwrap.dedent(f'''
        import importlib.util
        spec = importlib.util.spec_from_file_location("pnw", r"{HOOK_PATH}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)          # runs the module-level sys.path.insert
        import background.supervisor          # must resolve even though cwd=/tmp
        print("IMPORT_OK")
    ''')
    r = subprocess.run([sys.executable, "-c", code], cwd="/tmp", capture_output=True, text=True)
    assert "IMPORT_OK" in r.stdout, f"import failed from alien cwd: {r.stderr[-400:]}"


def test_decide_stdout_is_pure_json_when_find_work_prints(tmp_path, monkeypatch, capsys):
    """Regression (serial-autonomy maiden-turn watch, 2026-07-17): the REAL find_work (via
    supervisor.log()) PRINTS to stdout. The Stop hook's stdout must be PURE JSON or Claude Code
    cannot parse the block+continue -- a leading log line silently drops the drawn turn. decide()
    must capture find_work's stdout so ONLY main()'s json.dumps reaches the pane transport."""
    import sys
    import types
    mod = _load_hook(tmp_path, monkeypatch, enabled=True, draw_result=None)
    noisy = types.ModuleType("background.supervisor")

    def _find_work(resumed_from_pause=False):
        print("- [ts] THREE-LANE self-refill (atoms-drawn-per-cycle): BUILD=1")  # mimic supervisor.log()
        return ("BUILD OPS1_tmux_target_qualification", False)

    noisy.find_work = _find_work
    monkeypatch.setitem(sys.modules, "background.supervisor", noisy)
    out = mod.decide(_wp())
    captured = capsys.readouterr()
    assert captured.out == "", f"find_work stdout leaked into the hook's stdout: {captured.out!r}"
    assert out is not None and out["decision"] == "block"
    assert "OPS1_tmux_target_qualification" in out["reason"]

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
