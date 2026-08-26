"""W4_2 — the timing/data-flow detection burden is ROUTED, and the routing has a control.

WHY THIS FILE EXISTS.

`tools/epistemic_verifier.py`'s module docstring makes a load-bearing claim in
prose: this tool stays *import-direction* detection, and the data-flow/timing
dimension (the hedge-volatility bug class -- a function receiving an unbounded
historical dataset with no as-of cut) "is carried by two separate mechanisms
instead":

  1. NEAR-TERM  -- `.claude/hooks/block_point_in_time_read.py` (a PreToolUse
     Edit|Write hook), and
  2. PERMANENT  -- the as-of snapshot object,
     `company/interfaces/point_in_time_view.py::PointInTimeView`.

That is the resolution the director decided in
`docs/review_gates/done/EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md`
(Option B/C, 2026-07-10): the verifier itself is NOT modified, and those two
mechanisms carry the burden instead.

Until this file, that claim had **no control**. The hook's *behaviour* is
covered in depth (`tests/tools/test_claude_hooks.py::TestBlockPointInTimeRead`
-- dangerous shapes flagged, as-of-bounded shapes cleared, absolute/worktree
paths normalised). What nothing asserted is that the hook is **WIRED**. A hook
that behaves perfectly and is not registered in `.claude/settings.json` never
runs: it is inert, its own behavioural tests stay green, and the verifier
docstring goes on claiming a detector that fires on nothing. That is the R15
FAIL-SILENT killer pattern applied to a routing decision -- the check is
unavailable, and unavailability reads as a clean pass.

So the control here is deliberately NOT more behavioural coverage of the hook.
It is the three load-bearing facts the routing rests on:

  * the near-term detector exists AND is registered against Edit|Write;
  * the permanent fix exists AND binds its as-of cut on the OBJECT;
  * the verifier itself has NOT quietly grown timing detection.

The third direction matters as much as the first two. The maturity map keeps
re-drawing `W4_2_verifier_timing_extension` at `level_target: 3` with
`file_scope: ["tools/epistemic_verifier.py"]` -- i.e. the map periodically
schedules exactly the build the closed gate declined. A control that only
guarded the carriers would let that build land silently and leave the two
mechanisms in place unexamined, which is how you end up with three registers
of one concept again (see that file's own KNIFE-pass-3 header).

R15 note on this file's own honesty: `_pit_hook_is_wired` is a PURE predicate
over a settings mapping, so `test_wiring_check_fails_on_an_unwired_hook` can
feed it the real settings with the hook removed and prove the checker fires on
its own named defect. A wiring check that could only ever be handed the live,
correct file would be untestable-by-construction -- exactly the tautology R15
names.
"""
from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SETTINGS = REPO_ROOT / ".claude" / "settings.json"
PIT_HOOK = REPO_ROOT / ".claude" / "hooks" / "block_point_in_time_read.py"
PIT_VIEW = REPO_ROOT / "company" / "interfaces" / "point_in_time_view.py"
VERIFIER = REPO_ROOT / "tools" / "epistemic_verifier.py"

# The hook only carries the near-term half of the burden on WRITES of company/
# saas code, so Edit and Write are both required. A registration that covered
# only one of them would be half a detector.
_REQUIRED_MATCHER_TOOLS = ("Edit", "Write")


def _load_settings() -> dict:
    return json.loads(SETTINGS.read_text())


def _pit_hook_is_wired(settings: dict) -> bool:
    """True iff `block_point_in_time_read.py` is registered as a PreToolUse hook
    whose matcher covers BOTH Edit and Write.

    Pure over `settings` on purpose -- see the module docstring's R15 note.
    """
    for entry in (settings.get("hooks") or {}).get("PreToolUse") or []:
        matcher = entry.get("matcher") or ""
        tools = {t.strip() for t in matcher.split("|")}
        if matcher != "*" and not all(t in tools for t in _REQUIRED_MATCHER_TOOLS):
            continue
        for hook in entry.get("hooks") or []:
            if "block_point_in_time_read.py" in (hook.get("command") or ""):
                return True
    return False


def _strip_pit_hook(settings: dict) -> dict:
    """The named defect this control exists to catch: the hook file is still
    present and still passes every one of its own behavioural tests, but nothing
    invokes it."""
    out = copy.deepcopy(settings)
    for entry in (out.get("hooks") or {}).get("PreToolUse") or []:
        entry["hooks"] = [
            h for h in (entry.get("hooks") or [])
            if "block_point_in_time_read.py" not in (h.get("command") or "")
        ]
    return out


class TestNearTermDetectorIsLive:
    def test_hook_file_exists(self):
        assert PIT_HOOK.is_file(), (
            "the near-term timing detector named in tools/epistemic_verifier.py's "
            "scope note is missing -- the routing claim no longer holds"
        )

    def test_hook_is_wired_into_settings(self):
        assert _pit_hook_is_wired(_load_settings()), (
            "block_point_in_time_read.py exists but is not registered as a "
            "PreToolUse Edit|Write hook. An unregistered hook never runs: its own "
            "behavioural tests stay green while it detects nothing (R15 "
            "FAIL-SILENT). Re-wire it in .claude/settings.json, or re-open "
            "EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md -- the burden cannot "
            "simply go unowned."
        )

    def test_wiring_check_fails_on_an_unwired_hook(self):
        """NEGATIVE CONTROL (R15): the checker above must be able to FAIL."""
        assert not _pit_hook_is_wired(_strip_pit_hook(_load_settings()))

    def test_wiring_check_fails_on_a_read_only_matcher(self):
        """A registration under the wrong matcher is inert for authorship too --
        the detector's whole job is to see NEW company/saas code being written."""
        settings = _strip_pit_hook(_load_settings())
        settings["hooks"]["PreToolUse"].append({
            "matcher": "Read|Glob|Grep",
            "hooks": [{"type": "command", "command": "python3 .claude/hooks/block_point_in_time_read.py"}],
        })
        assert not _pit_hook_is_wired(settings)


class TestPermanentFixIsLive:
    def test_snapshot_object_exists_and_binds_its_cut_on_the_object(self):
        assert PIT_VIEW.is_file(), (
            "company/interfaces/point_in_time_view.py -- the PERMANENT half of the "
            "routing -- is missing"
        )
        from company.interfaces.point_in_time_view import PointInTimeView

        params = PointInTimeView.__init__.__code__.co_varnames[
            : PointInTimeView.__init__.__code__.co_argcount
        ]
        assert "decision_time" in params, (
            "PointInTimeView must take its as-of cut at CONSTRUCTION. The whole "
            "point of the permanent fix is that the bound lives on the object, not "
            "in each caller's memory -- a per-read date argument is the "
            "caller-trusted anti-pattern the hedge-volatility bug came from."
        )


class TestVerifierStaysImportDirectionOnly:
    """The other direction of the ruling: the verifier must not quietly grow the
    detection it was decided NOT to carry. The map re-draws W4_2 at
    level_target 3 against this exact file, so the pressure is live, not
    hypothetical."""

    def test_unbounded_history_read_is_not_flagged_but_a_sim_import_is(self, tmp_path):
        """Behavioural, not prose-matching: one file carrying BOTH shapes.

        The SIM import is the POSITIVE control -- it proves the scan actually ran
        over this file, so the timing shape's absence from the findings is a real
        clean, not a scan that never happened (which would pass vacuously).
        """
        from tools import epistemic_verifier

        target = tmp_path / "company" / "trading" / "probe.py"
        target.parent.mkdir(parents=True)
        target.write_text(
            "import simulation.weather_engine\n"
            "\n"
            "def estimate(all_records):\n"
            "    # unbounded historical read, no as-of cut: the hedge-volatility shape\n"
            "    return sum(r['price'] for r in all_records) / len(all_records)\n"
        )

        findings = epistemic_verifier._scan_file(str(target))
        descriptions = [f["description"] for f in findings]

        assert any("simulation.weather_engine" in d for d in descriptions), (
            "positive control failed: the import-direction scan did not run"
        )
        assert not any(
            "timing" in d.lower() or "as-of" in d.lower() or "data-flow" in d.lower()
            for d in descriptions
        ), (
            "tools/epistemic_verifier.py has grown timing/data-flow detection. That "
            "build was declined in docs/review_gates/done/EPISTEMIC_VERIFIER_TIMING_"
            "DETECTION_TIER1.md (Option B/C) and routed to the two mechanisms this "
            "module guards. If it is being re-opened, re-open the gate and retire "
            "this control -- do not leave three registers of one concept."
        )

    def test_scope_note_names_both_carriers(self):
        """The docstring is what a reader trusts; if a carrier is ever renamed,
        this fails alongside the existence checks rather than after them."""
        doc = ast.get_docstring(ast.parse(VERIFIER.read_text())) or ""
        assert "block_point_in_time_read.py" in doc
        assert "snapshot" in doc.lower()


class TestScanReportCount:
    def test_full_scan_file_count_does_not_double_count_saas(self):
        """`main()`'s no-company-files-changed branch built its reported total as
        `company + saas + saas` -- saas twice. The number is only a report line,
        but it is the number a reader uses to judge whether the scan's coverage
        looked right, and an inflated one makes a narrow scan look broad."""
        from tools import epistemic_verifier

        source = VERIFIER.read_text()
        assert source.count('rglob("*.py")) + list(Path("saas").rglob("*.py")) '
                            '+ list(Path("saas")') == 0, (
            "the duplicated saas rglob is back in the reported file count"
        )
        # And the honest total is what the scanner itself would walk.
        expected = len(list((REPO_ROOT / "company").rglob("*.py"))) + len(
            list((REPO_ROOT / "saas").rglob("*.py"))
        )
        assert expected > 0
        assert epistemic_verifier  # module imports cleanly


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
