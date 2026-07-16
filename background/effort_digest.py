"""EFFORT DIGEST -- surfaces G5_effort_sizing_discipline's L2 views (remaining
effort, estimate-vs-actual per lane, XL-decompose signal) in the run digest
(LATEST.md), same block-managed pattern as `background/naive_organ.py`'s
`render_digest_section()` (docs/design/EFFORT_SIZING_DESIGN.md sections 2-6).

This module is a thin RENDER layer only -- every real computation lives in
`tools/effort_calibration.py` (the L1 calibration tool + its L2 extensions:
`remaining_effort_report`, `estimate_vs_actual_by_lane`, `xl_decompose_flags`).
Read-only: never mutates `maturity_map.yaml`, never blocks anything.

GUARDRAIL (dial, not a wall -- R12 anti-goal-seek, same law as every other
diagnostic in this project): everything rendered here is a forecast/learning
signal for prioritisation and decomposition. It is never a deadline, never a
completion gate, and a lane's estimate-vs-actual delta is never a stick
against a specific atom or the fork that built it (design section 5).

Degrades gracefully: until FRAME starts setting `size:` on real atoms, the
section still renders (an honest "N below target, 0 sized yet" line) rather
than going silent -- the gap itself is the useful signal, not something to
hide until it looks good.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from tools.effort_calibration import (
    MATURITY_MAP_YAML,
    PROJECT,
    estimate_vs_actual_by_lane,
    load_atom_registry,
    remaining_effort_report,
    xl_decompose_flags,
)


def render_digest_section(
    *, map_path: Optional[Path] = None, repo_root: Optional[Path] = None
) -> str:
    """Render the 'EFFORT SIZING' digest block. Returns '' only if the map
    itself cannot be read (defensive callers -- e.g. process_run_complete.py
    -- should still wrap this in a try/except, matching the naive-organ
    digest section's own failure discipline: the digest must never break
    publishing).

    `repo_root` is exposed (defaulting to this project's own root, the real
    publish-cycle path) purely so tests can point both `map_path` and
    `repo_root` at a synthetic git repo without touching the real one."""
    map_path = map_path or MATURITY_MAP_YAML
    repo_root = repo_root or PROJECT
    try:
        registry = load_atom_registry(map_path)
    except Exception:
        return ""

    remaining = remaining_effort_report(registry, map_path=map_path, repo_root=repo_root)
    est_vs_actual = estimate_vs_actual_by_lane(registry, map_path=map_path, repo_root=repo_root)
    xl_flags = xl_decompose_flags(registry, map_path=map_path)

    lines = [
        "**EFFORT SIZING** (G5_effort_sizing_discipline -- DIAL, never a "
        "target/gate; R12 anti-goal-seek):"
    ]

    if remaining["n_below_target"] == 0:
        lines.append("- No below-target atoms.")
    elif remaining["total_expected_hours"] is None:
        lines.append(
            "- {} atom(s) below target, 0 sized yet -- remaining-effort "
            "inactive until FRAME sets `size:` (activates automatically, no "
            "code change needed).".format(remaining["n_below_target"])
        )
    else:
        lines.append(
            "- Remaining effort: ~{:.1f}h across {} sized atom(s) ({} of {} "
            "below-target atoms still unsized).".format(
                remaining["total_expected_hours"],
                remaining["n_sized"],
                remaining["n_unsized"],
                remaining["n_below_target"],
            )
        )

    lane_lines = [
        "{}: est {:.1f}h vs actual {:.1f}h ({}{:.1f}h, {})".format(
            lane,
            v["estimate_mean_hours"],
            v["actual_mean_hours"],
            "+" if v["delta_hours"] >= 0 else "",
            v["delta_hours"],
            v["direction"],
        )
        for lane, v in sorted(est_vs_actual.items())
        if v.get("status") == "ok"
    ]
    if lane_lines:
        lines.append("- Estimate-vs-actual by lane: " + "; ".join(lane_lines))

    if xl_flags:
        lines.append(
            "- XL decompose signal ({} atom(s)): {} -- decompose before BUILD "
            "or record an exception basis (soft gate, never a block).".format(
                len(xl_flags), ", ".join(f["atom_id"] for f in xl_flags)
            )
        )

    return "\n".join(lines)
