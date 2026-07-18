"""OPS1 sub-step 4 FOUNDATION invariants (pre-absorption WIP).

Two permanent invariants land with the foundation:
  1. the generated systemd units cannot drift from the manifest (deterministic generator);
  2. worker_seat.py stays THIN forever (design law) — scope-creep in that one file is where
     accretion would restart, so its thinness is mutation-guarded.
The reconcile absorption, reaper deletion, boot-announce and live migration are the NEXT pass;
these two invariants are already true and stay true."""
from __future__ import annotations

from pathlib import Path

from background import generate_units


def test_committed_units_equal_regenerated_from_manifest():
    """Anti-drift: every committed unit under background/systemd/ is exactly what the generator
    emits from process_manifest.yaml — the generated layer can't itself drift from the source."""
    regen = generate_units.regenerate()
    committed = {f.name: f.read_text() for f in generate_units.UNITS_DIR.glob("*.service")}
    assert set(committed) == set(regen), f"unit set drift: {set(committed) ^ set(regen)}"
    for name, text in regen.items():
        assert committed[name] == text, f"{name} drifted from the manifest — regenerate it"


def test_every_unit_has_the_G_L3_crash_loop_bound():
    """G-L3: no unit may restart silently forever (the file-api 32,707 lesson)."""
    for name, text in generate_units.regenerate().items():
        assert "StartLimitBurst" in text and "StartLimitIntervalSec" in text, name


def test_file_api_unit_also_has_startlimit():
    t = (Path(generate_units._HERE) / "file-api.service").read_text()
    assert "StartLimitBurst" in t and "StartLimitIntervalSec" in t


# ── worker_seat.py thinness — the design-law invariant ──

_SEAT_SRC = (Path(generate_units._HERE) / "worker_seat.py").read_text()


def test_worker_seat_imports_no_kill_or_notify_machinery():
    """THIN design law: the seat manager must never grow kill/notify machinery. AST-based (not a
    substring grep) so the docstring's *description* of what's forbidden doesn't false-positive —
    it checks real imports and calls. A future edit that adds process-killing or NTFY here fails."""
    import ast
    tree = ast.parse(_SEAT_SRC)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.name.split(".")[0] in {"signal", "requests"} or "ntfy" in n.name:
                    bad.append(f"import {n.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and ("ntfy" in node.module or node.module.split(".")[0] in {"signal", "requests"}):
                bad.append(f"from {node.module}")
        elif isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr in {"kill"}:
                bad.append("a .kill() call")
            if isinstance(f, ast.Name) and f.id in {"send_ntfy", "pkill"}:
                bad.append(f"{f.id}()")
    assert bad == [], f"worker_seat.py grew forbidden machinery: {bad}"


def test_worker_seat_never_uses_continue_flag():
    """Seeding is by dedicated session-id, never `claude -c` (the console-latch bug)."""
    from background import worker_seat
    argv = worker_seat.seat_argv("/fake/claude")
    assert "-c" not in argv and "--continue" not in argv
    assert worker_seat.WORKER_SESSION_ID in argv
    assert ("--session-id" in argv) or ("--resume" in argv)


def test_worker_seat_seed_does_not_auto_advance():
    """G-R4: the seed brings-up-and-reports then STOPS — it must not instruct the seat to
    draw/advance work. The old RESUME_INSTRUCTION's 'ADVANCE THE PROJECT' must be absent."""
    from background import worker_seat
    seed = worker_seat.SEED_PROMPT.lower()
    assert "advance" in seed and "do not" in seed  # it explicitly says do NOT advance
    assert "does not self-advance" in worker_seat.SEED_PROMPT.lower() or "not self-advance" in seed

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
