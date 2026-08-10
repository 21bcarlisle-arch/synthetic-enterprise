"""THE PROOF must keep showing an atom's Expert-Hour findings after they are rehomed.

`expert_hour.findings` is the append-per-Hour narrative list inside the map's `expert_hour`
mapping -- the second unbounded flow, one level below the top-level lists H41 drained. It crossed
the 12,288 B per-atom map budget on H27_payment_belief_gap at its seventh Hour and wedged
publishing for 25 hours, so it now moves to the sibling record store ONE ATOM AT A TIME, as the
cap names each one.

That makes the migration PARTIAL by design and permanently so: some atoms keep findings inline,
some hold them in the store. THE PROOF's verification stack is the surface whose entire claim is
that the NEEDS_WORK history is visible, so a reader that saw only the inline shape would delete a
rehomed atom's defect history from the one page that exists to show it -- silently, and looking
like an improvement (fewer findings, same green suite).

R15: the store branch has its own named test below, and the file name carries the `test_
generate_proof_data_*` stem the pre-commit gate's `tests_for()` maps from generate_proof_data.py
-- naming this file for its ASPECT alone would make it invisible to the gate that must run it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools import generate_proof_data as gp  # noqa: E402
from tools import simplifications_store as store  # noqa: E402

PROJECT = Path(__file__).resolve().parent.parent.parent
STORE_DIR = PROJECT / "docs" / "design" / "simplifications"


def test_findings_are_read_from_the_store_when_the_map_holds_none():
    """THE REHOMED SHAPE. Kill the store branch in `_expert_hour_findings` and this is the
    test that dies."""
    findings = gp._expert_hour_findings(
        {"id": "H27_payment_belief_gap"}, {"status": "passed", "last": "2026-08-10"}
    )
    assert findings, "a rehomed atom's findings vanished from THE PROOF's reader"
    assert len(findings) == 11
    assert any("DETECTION headline is an as_of ARTEFACT" in str(f) for f in findings)


def test_the_live_atom_really_is_rehomed_not_still_inline():
    """NON-VACUITY. The test above proves nothing if H27 still carries its findings inline --
    it would be reading the fallback of an atom that never needed one. This pins the premise:
    the map holds the structured members only, and the store holds the list."""
    atoms = {a["id"]: a for a in gp._load_atoms() if isinstance(a, dict) and a.get("id")}
    eh = atoms["H27_payment_belief_gap"]["expert_hour"]
    assert set(eh) == {"last", "status"}, f"expert_hour still carries {sorted(eh)}"
    assert "expert_hour_findings" in atoms["H27_payment_belief_gap"]["records_rehomed"]
    stored = store.records_for_atom("H27_payment_belief_gap", STORE_DIR)
    assert len(stored["expert_hour_findings"]) == 11


def test_inline_findings_win_over_the_store():
    """Same rule as `simplifications_store.hydrate`: the inline value is what the spine is
    actually showing, so a silently-preferred store copy would make the two-sources-of-truth
    contract unfalsifiable."""
    got = gp._expert_hour_findings(
        {"id": "H27_payment_belief_gap"},
        {"status": "passed", "findings": ["the inline one"]},
    )
    assert got == ["the inline one"]


def test_an_atom_with_findings_nowhere_returns_empty_not_none():
    """FAIL-SAFE shape: `_verification_stack` tests this value for truthiness and takes its
    len(); a None would raise mid-publish rather than read as 'no findings'."""
    assert gp._expert_hour_findings({"id": "NOSUCHATOM_ever"}, {}) == []
    assert gp._expert_hour_findings({}, {}) == []


def test_the_rehome_did_not_move_the_published_finding_count():
    """The measurement that makes this a REHOME and not a deletion. THE PROOF publishes
    `findings_caught_total`; if moving 11 findings out of the map changed it, the store copy is
    not being read (or is being double-counted)."""
    vs = gp._verification_stack(gp._load_atoms())
    assert vs["findings_caught_total"] == 57, vs["findings_caught_total"]
