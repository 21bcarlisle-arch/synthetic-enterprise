"""Accuracy control for the G11 activity-cost classifier (the REMAINS-(2) gate).

The classifier in tools/activity_cost.py maps real git commits into a 7-class
PRODUCTIVE/WASTE taxonomy. Until now there was NO ground truth -- the productive-%
headline rested on unvalidated keyword judgment. This file is that ground truth:
a HAND-LABELLED, stratified fixture of real commits (drawn across every taxonomy
class via `git log`), labelled INDEPENDENTLY of the classifier's rules by reading
each commit's subject + changed files against the taxonomy DEFINITIONS. It is a
REPEATABLE control (runs every suite against live git history), not a one-off audit.

WHY TWO THRESHOLDS (and why they differ):
  * COARSE agreement -- PRODUCTIVE vs WASTE vs unattributed. This is the axis the
    HEADLINE productive-% actually depends on. Held to the HIGH bar (>= 0.90): if
    the classifier can't reliably tell product-work from self-work, the headline
    is worthless.
  * FINE agreement -- the full 7-class label. Held LOWER (>= 0.80) on purpose:
    the sub-class boundaries are inherently fuzzy and DO NOT move the headline --
    product-vs-discovery is productive-vs-productive; which-waste-bucket is
    waste-vs-waste. A wrong sub-label costs a taxonomy row, not the diagnostic.

The residual disagreements (documented in DISAGREEMENT_NOTES) are the DECLARED R10
coarseness of a keyword+file-domain classifier: (a) product features whose NAME
contains a discovery-ish word ("...Register", "Coverage Sprint") route to
PRODUCTIVE/discovery (still productive); (b) product feature-builds that touch
mostly tooling/observability files get plurality-flipped to WASTE/self-repair
(a CONSERVATIVE under-count of productive, the safe direction for a
diagnostic-not-target metric). Neither is self-flattering.

R15 (a control must be able to FAIL): the mutation tests below prove this control
FIRES -- a degenerate classifier, and a corrupted fixture label, both drop
agreement below threshold. A control that cannot fail is worse than none.

GUARDRAIL: this is a DIAGNOSTIC of classifier quality, never a target -- the fix
for a low score is to improve the classifier's correctness (per-commit justified),
NEVER to relabel the fixture toward the classifier's output (that would be the
tautology R15 forbids: checking a value against a source derived from itself).
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from tools.activity_cost import (
    PRODUCTIVE_CLASSES,
    WASTE_CLASSES,
    UNATTRIBUTED,
    Commit,
    classify_commit,
    git_log_commits,
)

# ---------------------------------------------------------------------------
# Hand-labelled ground truth. {12-char sha: taxonomy_class}. Labelled by a
# cold-eyes review reading each commit's subject + changed files against the
# taxonomy definitions -- NOT by running the classifier (that would be circular).
# Stratified across classes (over-sampling the rare WASTE buckets on purpose, to
# stress the classes most prone to keyword false-positives).
# ---------------------------------------------------------------------------
PRODUCT = "PRODUCTIVE/product"
DISCOVERY = "PRODUCTIVE/discovery"
SELF_REPAIR = "WASTE/self-repair"
REWORK = "WASTE/rework"

HAND_LABELS: dict[str, str] = {
    # -- auto-process run-complete = the product OPERATING and publishing output --
    "4d3fb5d43e2c": PRODUCT, "0b4890a9969e": PRODUCT, "aede93e9b0db": PRODUCT,
    "326bb55f228c": PRODUCT, "1fa24a1bdf95": PRODUCT, "31530d0b14a0": PRODUCT,
    "dac54ae14b4b": PRODUCT, "7902c9aa7d25": PRODUCT, "0d0e25038977": PRODUCT,
    "9d809e308452": PRODUCT,
    # -- product feature/twin builds (company/sim/saas/site) --
    "83a00998e671": PRODUCT, "467768046daa": PRODUCT, "1320d1956e3c": PRODUCT,
    "808bcecd1299": PRODUCT, "884d4e3ce718": PRODUCT, "daefe53b3e79": PRODUCT,
    "2d8e356f341b": PRODUCT, "1eb80f63feb5": PRODUCT, "a6a5fa1101e2": PRODUCT,
    "04e4df294c6e": PRODUCT, "fe85d2a21d23": PRODUCT, "9642c994a10b": PRODUCT,
    # -- discovery/framing/research + staged directives (framing investment) --
    "faf2751a95b1": DISCOVERY, "81738b59cc4d": DISCOVERY, "29200a4333ec": DISCOVERY,
    "970463f4dcd0": DISCOVERY, "bae02bdf32b1": DISCOVERY,
    "3f5dfb07af31": DISCOVERY, "5f4f0767514a": DISCOVERY, "7d1a819906a8": DISCOVERY,
    "ad63fda66abd": DISCOVERY, "f28ba8b60bef": DISCOVERY, "3b8b2667772b": DISCOVERY,
    "f5ac422a4e19": DISCOVERY, "600f06873268": DISCOVERY, "b5c7200f410f": DISCOVERY,
    "9a3d476b8be3": DISCOVERY, "04dc5851f872": DISCOVERY, "cf8081381a5c": DISCOVERY,
    "347b770a720a": DISCOVERY, "59d9fd0477ef": DISCOVERY,
    # -- self-repair: fixing/maintaining the machine's own plumbing + observability --
    "3364fdc69fb8": SELF_REPAIR, "89f54aaeadf9": SELF_REPAIR, "e3a195566256": SELF_REPAIR,
    "3dbcd7a1c187": SELF_REPAIR, "013eeee9e395": SELF_REPAIR, "ab3281f4be9d": SELF_REPAIR,
    "edcb914f169b": SELF_REPAIR, "82b116dd9e27": SELF_REPAIR, "bc1aca9a148b": SELF_REPAIR,
    "6ad184ed4fad": SELF_REPAIR, "5a4f8c7db957": SELF_REPAIR, "06f72a31e247": SELF_REPAIR,
    "dab0edccc7a0": SELF_REPAIR, "c02de3a93b2b": SELF_REPAIR, "7f05ba129117": SELF_REPAIR,
    # -- rework: genuine reverts / re-draws --
    "2c5a654373e7": REWORK, "caab8d8c11a2": REWORK,
    # -- unattributed: thin status/priority-doc updates with no clear activity signal --
    "fc79952eeabb": UNATTRIBUTED, "27e6aba6e964": UNATTRIBUTED, "14aaa1505c86": UNATTRIBUTED,
    "9f2346f35977": UNATTRIBUTED, "66d3b67714b7": UNATTRIBUTED, "f0127a42bbff": UNATTRIBUTED,
}

# Thresholds. Justified in the module docstring. The measured margins (Jul 2026):
# coarse ~0.94, fine ~0.86 -- both clear with room, so a real accuracy regression
# (not just noise) is what trips the gate.
COARSE_THRESHOLD = 0.90
FINE_THRESHOLD = 0.80

# The known, ACCEPTED residual disagreements (declared R10 coarseness). Documented
# so a reviewer can see the control's misses are understood, not hidden. NOT used
# to inflate the score -- the score is computed over the raw fixture.
DISAGREEMENT_NOTES = {
    "1eb80f63feb5": "Phase-build with a doc-heavy file list, no product keyword -> unattributed (excluded, conservative).",
    "a6a5fa1101e2": "Run-insight feature lives in background/ -> self-repair by file domain (conservative under-count).",
    "884d4e3ce718": "Company twin whose commit also touches tools/observability -> plurality flips to self-repair (conservative).",
    "82b116dd9e27": "CLAUDE.md archival housekeeping -> discovery by docs/claude domain (mild over-count, offsets).",
    "04e4df294c6e": "'registered backlog item' KPI build -> discovery keyword (productive<->productive, headline unaffected).",
    "daefe53b3e79": "Feature named '...Register' -> discovery keyword (productive<->productive).",
    "2d8e356f341b": "Feature named '...Register' -> discovery keyword (productive<->productive).",
    "fe85d2a21d23": "'Coverage Sprint' test build with a NEXT_PHASE draft file -> discovery domain (productive<->productive).",
    "7f05ba129117": "'two-strike redesign' of a control -> rework keyword (waste<->waste).",
}


def _coarse(cls: str) -> str:
    if cls in PRODUCTIVE_CLASSES:
        return "PRODUCTIVE"
    if cls in WASTE_CLASSES:
        return "WASTE"
    return "unattributed"


def _resolve_commits() -> dict[str, Commit]:
    """Index live git history by 12-char sha prefix. The whole-history walk is the
    same read the report uses, so the fixture is checked against exactly what the
    metric sees. Fail-CLOSED (R15): every fixture sha MUST resolve -- a missing
    commit is a failed check, never a silently-shrunk sample."""
    by_prefix: dict[str, Commit] = {}
    for c in git_log_commits():
        by_prefix[c.sha[:12]] = c
    missing = [sha for sha in HAND_LABELS if sha not in by_prefix]
    assert not missing, (
        "accuracy control cannot run -- these hand-labelled commits are not in "
        f"the current git history (fail-closed, not skipped): {missing}"
    )
    return {sha: by_prefix[sha] for sha in HAND_LABELS}


def _measure(classifier) -> tuple[float, float, list[tuple]]:
    """Return (fine_agreement, coarse_agreement, disagreements) of `classifier`
    against the hand-labelled fixture over live git history."""
    commits = _resolve_commits()
    n = len(HAND_LABELS)
    fine = coarse = 0
    disagreements = []
    for sha, label in HAND_LABELS.items():
        pred, rule = classifier(commits[sha])
        if pred == label:
            fine += 1
        else:
            disagreements.append((sha, label, pred, rule, commits[sha].subject[:70]))
        if _coarse(pred) == _coarse(label):
            coarse += 1
    return fine / n, coarse / n, disagreements


# ---------------------------------------------------------------------------
# The control
# ---------------------------------------------------------------------------
def test_sample_size_is_stratified_and_meaningful():
    # A real, not token, sample; spanning at least the four bulk classes.
    assert len(HAND_LABELS) >= 40
    present = {_ for _ in HAND_LABELS.values()}
    for cls in (PRODUCT, DISCOVERY, SELF_REPAIR, UNATTRIBUTED):
        assert cls in present, f"fixture missing class {cls}"


def test_classifier_meets_coarse_accuracy_threshold():
    """PRODUCTIVE vs WASTE vs unattributed -- the axis the headline depends on."""
    fine, coarse, dis = _measure(classify_commit)
    assert coarse >= COARSE_THRESHOLD, (
        f"coarse agreement {coarse:.3f} < {COARSE_THRESHOLD} -- the productive/waste "
        f"split has regressed. Disagreements:\n" + "\n".join(map(str, dis))
    )


def test_classifier_meets_fine_accuracy_threshold():
    """Full 7-class label (a looser bar -- sub-class fuzz does not move the headline)."""
    fine, coarse, dis = _measure(classify_commit)
    assert fine >= FINE_THRESHOLD, (
        f"fine agreement {fine:.3f} < {FINE_THRESHOLD}. Disagreements:\n"
        + "\n".join(map(str, dis))
    )


def test_all_disagreements_are_documented():
    """Every miss must be an ACKNOWLEDGED residual (declared coarseness), so a NEW
    kind of misclassification surfaces as an undocumented disagreement here."""
    _, _, dis = _measure(classify_commit)
    undocumented = [d for d in dis if d[0] not in DISAGREEMENT_NOTES]
    assert not undocumented, (
        "new, undocumented classifier disagreements (investigate before promoting):\n"
        + "\n".join(map(str, undocumented))
    )


# ---------------------------------------------------------------------------
# R15 mutation proofs -- the control MUST be able to fail.
# ---------------------------------------------------------------------------
def test_mutation_degenerate_classifier_fails_coarse():
    """A classifier that calls EVERYTHING product must fail the coarse gate --
    proving the gate discriminates (it is not fail-open / tautological)."""
    always_product = lambda c: (PRODUCT, "mutant")
    fine, coarse, _ = _measure(always_product)
    assert coarse < COARSE_THRESHOLD
    assert fine < FINE_THRESHOLD


def test_mutation_all_waste_classifier_fails():
    """The opposite degenerate (everything self-repair) must also fail -- the gate
    is not merely rewarding a product-heavy sample."""
    always_waste = lambda c: (SELF_REPAIR, "mutant")
    fine, coarse, _ = _measure(always_waste)
    assert coarse < COARSE_THRESHOLD


def test_mutation_corrupted_label_would_trip_the_gate():
    """Flipping the fixture's correct labels to a wrong constant drops agreement
    below threshold -- proving the fixture (not just the classifier) is load-bearing
    and a mislabel cannot silently pass."""
    corrupted = {sha: REWORK for sha in HAND_LABELS}  # almost all wrong
    commits = _resolve_commits()
    n = len(corrupted)
    coarse = sum(
        _coarse(classify_commit(commits[sha])[0]) == _coarse(lbl)
        for sha, lbl in corrupted.items()
    ) / n
    assert coarse < COARSE_THRESHOLD


def test_current_margins_are_reported(capsys):
    """Not a gate -- prints the live margins so the control's headroom is visible
    in test output (a DIAGNOSTIC, per the module guardrail)."""
    fine, coarse, dis = _measure(classify_commit)
    print(f"\nG11 classifier accuracy on {len(HAND_LABELS)} hand-labelled commits: "
          f"coarse={coarse:.3f} (>= {COARSE_THRESHOLD}), fine={fine:.3f} (>= {FINE_THRESHOLD}), "
          f"{len(dis)} declared-residual disagreements")
    assert fine <= 1.0 and coarse <= 1.0
