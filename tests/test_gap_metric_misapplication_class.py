"""D6 CLASS GUARD (R10) -- the prevalence defect belongs to `misapplication_gap`
ITSELF, so it may not be closed at the ageing instance where it was found.

The D6 DISCOVER proved, against the unchanged criterion, that
`background.gap_metric.misapplication_gap` normalises to the majority class --
so its `gap` is a joint statement about the company AND the world's class
balance. `tests/tools/test_d6_ageing_metric_shape.py` characterizes that on the
AGEING call site. This file closes the CLASS:

  1. every result the function returns carries the caveat (the stamp exists),
  2. the caveat survives into the PUBLISHED shape, including when a caller
     replaces `note` -- which both live callers do,
  3. every live call site is enumerated, so a NEW one fails this test rather
     than silently publishing an uncaveated prevalence-normalised figure,
  4. the SECOND call site (W2_9 <-> C11) is measured, not argued, to be in the
     same régime,
  5. every misapplication entry already in the live ledger is caveated.

Verdict + evidence: docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md

These are CHARACTERIZATION tests of a defect that is being carried openly, not
of desired behaviour. When `D7_ageing_gap_metric_reshape` lands, tests 1-3 and 5
should be re-pointed at the replacement measures and test 4 should FAIL -- that
failure is the signal that the reshape actually removed the prevalence
dependence, and it must not be "repaired" by loosening the bound.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from background.gap_metric import (
    MISAPPLICATION_PREVALENCE_CAVEAT,
    misapplication_gap,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

# The live (non-test) modules permitted to call `misapplication_gap`. Adding a
# call site is a deliberate act: register it here AND satisfy yourself that the
# consumer of its number understands the caveat above.
KNOWN_CALL_SITES = {
    "background/gap_metric.py",       # the definition itself
    "tools/couple_w2_11_d5.py",       # ageing dimension (D6's origin)
    "tools/couple_w2_9_c11.py",       # segment debt T&C
    "tools/d6_ageing_metric_oracle.py",  # the D6 oracle, by design
}

# Directories scanned for call sites. `tests/` is excluded on purpose: a test
# calling the metric is characterizing it, not publishing its output.
_SCANNED_DIRS = ("background", "company", "saas", "sim", "simulation", "tools", "site")


def _truth_belief(n_majority: int, n_minority: int, n_wrong: int):
    """A population with a known majority class and an INDEPENDENTLY known
    number of company errors -- the expected values below are read off these
    counts, never off the metric (R15 independence)."""
    truth = ["domestic"] * n_majority + ["business"] * n_minority
    belief = list(truth)
    for i in range(n_wrong):
        belief[i] = "business"
    return truth, belief


def test_1_every_result_carries_the_prevalence_caveat():
    """The stamp exists on every return path -- delete it in gap_metric and this
    fails (R15 mutation-provable)."""
    truth, belief = _truth_belief(100, 10, 5)
    for kwargs in ({}, {"positive_class": "business"}):
        result = misapplication_gap(truth, belief, **kwargs)
        assert result.components["prevalence_caveat"] == MISAPPLICATION_PREVALENCE_CAVEAT
        assert result.components["normalisation"] == "majority-class prevalence"
        # The share the score is really keyed to, stated as a number rather than
        # left implicit inside g0.
        assert result.components["minority_class_share"] == pytest.approx(10 / 110, abs=1e-6)
        assert result.components["minority_class_share"] == pytest.approx(result.g0, abs=1e-6)

    # Vacuity guard: the caveat must be real text, not an empty string that
    # would satisfy every assertion above while telling a reader nothing.
    assert "NOT EVIDENCE" in MISAPPLICATION_PREVALENCE_CAVEAT
    assert len(MISAPPLICATION_PREVALENCE_CAVEAT) > 200


def test_2_the_caveat_reaches_the_published_shape_even_when_note_is_replaced():
    """`note` is overridden by BOTH live callers, so the caveat cannot live
    there. It rides in components, which `to_ledger_entry` copies into the gap
    ledger and from there into site/data/proof.json."""
    truth, belief = _truth_belief(100, 10, 5)
    result = misapplication_gap(truth, belief)
    result.note = "a caller's own headline, with no caveat in it"

    entry = result.to_ledger_entry("W_TEST_ATOM")
    assert MISAPPLICATION_PREVALENCE_CAVEAT not in entry["note"], (
        "precondition: this test is only meaningful if the note really was replaced"
    )
    assert entry["components"]["prevalence_caveat"] == MISAPPLICATION_PREVALENCE_CAVEAT, (
        "the caveat did not survive into the published ledger entry"
    )


def test_3_every_live_call_site_is_registered():
    """R10 -- a NEW call site fails here rather than silently publishing an
    uncaveated prevalence-normalised figure."""
    found = set()
    for d in _SCANNED_DIRS:
        root = REPO_ROOT / d
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if "/test_" in rel or rel.split("/")[-1].startswith("test_"):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, SyntaxError):
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    fn = node.func
                    name = getattr(fn, "id", None) or getattr(fn, "attr", None)
                    if name == "misapplication_gap":
                        found.add(rel)

    # Vacuity guard: an AST walk that finds nothing would "pass" the subset
    # assertion below while proving nothing at all.
    assert found, "scan found no call sites -- the scanner is broken, not the code"
    assert found <= KNOWN_CALL_SITES, (
        "unregistered caller(s) of misapplication_gap: "
        f"{sorted(found - KNOWN_CALL_SITES)} -- read the D6 DISCOVER before "
        "publishing a prevalence-normalised gap from a new site"
    )


def test_4_the_second_call_site_is_measurably_in_the_same_regime():
    """W2_9 <-> C11, measured on the LIVE modules: hold C11's misrecording
    channel fixed and move only the world's business-segment share. The
    company's OWN error rate barely moves; the published normalised gap swings
    an order of magnitude, and at the smallest business share the pair reads
    'no better than blind' on its LOWEST error rate.

    Bounds, not pinned values (a pinned generated number is not a control).
    """
    import tools.couple_w2_9_c11 as w29
    from simulation.segment_debt_obligation import BUSINESS_TERMS

    original_mix = list(w29._TRUE_SEGMENT_MIX)
    error_rates, gaps = {}, {}
    try:
        for biz in (0.02, 0.10, 0.40):
            w29._TRUE_SEGMENT_MIX = [
                ("resi", 1 - biz), ("sme", biz * 0.8), ("iandc", biz * 0.2),
            ]
            truth, applied, _stats = w29.build_scenario(200)
            result = misapplication_gap(truth, applied, positive_class=BUSINESS_TERMS)
            # raw_gap IS the company's own error rate -- the un-normalised
            # quantity, read independently of the normalisation on trial.
            error_rates[biz] = result.raw_gap
            gaps[biz] = result.gap
    finally:
        w29._TRUE_SEGMENT_MIX = original_mix

    company_swing = max(error_rates.values()) / min(error_rates.values())
    metric_swing = max(gaps.values()) / min(gaps.values())

    assert company_swing < 3.0, (
        f"precondition: the company's own error rate must stay roughly fixed "
        f"across the sweep (observed {error_rates})"
    )
    assert metric_swing > 5.0, (
        f"characterization: the normalised gap should swing far more than the "
        f"company does (company x{company_swing:.2f}, metric x{metric_swing:.2f}, "
        f"gaps {gaps}) -- if this now FAILS, the reshape landed; re-point these "
        f"tests, do not loosen the bound"
    )
    assert gaps[0.02] > gaps[0.40], "the swing must be driven by prevalence, not noise"
    assert error_rates[0.02] <= min(error_rates.values()), (
        "the 'no better than blind' reading sits on the LOWEST company error rate"
    )


def test_5_published_misapplication_entries_are_caveated():
    """The live ledger leg: anything already published under this metric must
    carry the caveat where a consumer of the number will see it."""
    ledger_path = REPO_ROOT / "docs/observability/coupled_gap_ledger.json"
    if not ledger_path.is_file():
        pytest.skip("no gap ledger in this checkout")
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))

    entries = {
        k: v for k, v in ledger.items()
        if isinstance(v, dict) and v.get("metric") == "misapplication"
    }
    # Vacuity guard: zero entries means this control measured nothing.
    assert entries, "no misapplication entries in the ledger -- control is vacuous"

    uncaveated = []
    for atom_id, entry in entries.items():
        components = entry.get("components") or {}
        text = f"{components.get('prevalence_caveat', '')}\n{entry.get('note', '')}"
        if "NOT EVIDENCE" not in text:
            uncaveated.append(atom_id)

    assert not uncaveated, (
        f"published prevalence-normalised gap(s) with no caveat: {uncaveated} -- "
        "re-run the pair's runner so the stamped caveat reaches the ledger"
    )
