"""Tests for the PULL-LOOP Stop hook (.claude/hooks/pull_next_work.py,
STAGING_PULL_LOOP_RESCOPE.md, 2026-07-15).

Proves the transport's safety invariants WITHOUT enabling it on any live session:
gated-off-by-default, loop-guard, fail-safe on a broken draw, checkpoint cadence,
and -- the load-bearing one -- ZERO pane writes (the hook only returns JSON; it
never types into a pane, the whole point of replacing keystroke injection).
"""
import importlib.util
import json
from pathlib import Path

import pytest

HOOK_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "pull_next_work.py"


def _load_hook(tmp_path, monkeypatch, *, enabled, draw_result):
    spec = importlib.util.spec_from_file_location("pull_next_work", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "ENABLE_FLAG", tmp_path / ".build_executor_enabled")
    monkeypatch.setattr(mod, "LOG_FILE", tmp_path / "pull-loop-log.md")
    monkeypatch.setattr(mod, "STATE_FILE", tmp_path / ".pull_loop_state.json")
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
    assert mod.decide({"stop_hook_active": False}) is None  # no flag -> inert


def test_kill_switch_flag_off_refuses_next_boundary(tmp_path, monkeypatch):
    """R15 KILL-SWITCH PROOF (DIRECTOR_ANSWERS_C7 #6): with the single flag OFF,
    the very next turn boundary MUST refuse to continue. A kill switch never
    proven to kill is a theatre control (kill-list doctrine)."""
    mod = _load_hook(tmp_path, monkeypatch, enabled=False, draw_result=("lots of work", False))
    # flag absent -> refuse (session stops)
    assert mod.decide({"stop_hook_active": False}) is None
    # fail-closed: a MALFORMED flag (a directory, not a readable file) -> DISABLED
    (tmp_path / ".build_executor_enabled").mkdir()
    assert mod.decide({"stop_hook_active": False}) is None
    # mutation proof the guard is load-bearing: neuter it (force-enable) and the
    # same flag-off state now WRONGLY continues -> the guard is what gates the kill.
    monkeypatch.setattr(mod, "_autonomous_execution_enabled", lambda: True)
    assert mod.decide({"stop_hook_active": False}) is not None


def test_loop_guard_allows_stop_when_already_blocking(tmp_path, monkeypatch):
    mod = _load_hook(tmp_path, monkeypatch, enabled=True, draw_result=("A6 has work", False))
    assert mod.decide({"stop_hook_active": True}) is None  # never an infinite loop


def test_enabled_with_work_blocks_and_feeds_the_draw(tmp_path, monkeypatch):
    mod = _load_hook(tmp_path, monkeypatch, enabled=True,
                     draw_result=("self-refill: BUILD SITE1_expert_doors", False))
    out = mod.decide({"stop_hook_active": False})
    assert out is not None and out["decision"] == "block"
    assert "SITE1_expert_doors" in out["reason"]
    assert "PULL-LOOP doorbell" in out["reason"]  # R7 doorbell framing carried


def test_enabled_but_no_work_allows_stop(tmp_path, monkeypatch):
    mod = _load_hook(tmp_path, monkeypatch, enabled=True, draw_result=(None, True))
    assert mod.decide({"stop_hook_active": False}) is None


def test_fail_safe_allows_stop_when_draw_raises(tmp_path, monkeypatch):
    import sys, types
    mod = _load_hook(tmp_path, monkeypatch, enabled=True, draw_result=("x", False))
    boom = types.ModuleType("background.supervisor")
    def _raise(**k): raise RuntimeError("draw broken")
    boom.find_work = _raise
    monkeypatch.setitem(sys.modules, "background.supervisor", boom)
    # A broken draw must NEVER block the session (fail-safe: allow the stop).
    assert mod.decide({"stop_hook_active": False}) is None


def test_checkpoint_cadence_injects_compact(tmp_path, monkeypatch):
    mod = _load_hook(tmp_path, monkeypatch, enabled=True, draw_result=("keep building", False))
    last = None
    for _ in range(mod.CHECKPOINT_EVERY):
        last = mod.decide({"stop_hook_active": False})
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
