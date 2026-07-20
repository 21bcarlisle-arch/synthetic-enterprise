"""LIVE bridge: the payment coupled-triad's per-run belief-vs-truth gap, emitted
into the G1/G2/G3 fidelity-evidence machinery.

WHY THIS MODULE EXISTS. Every G atom (`G1_fidelity_grid_scorer`,
`G2_fidelity_evidence_ledger`, `G3_fidelity_inspection_chain`) carries
`blocked_on: coupled_triad_l3_needs_live_company_consumer`: the machinery is
built + R15-tested but was fed only synthetic/offline fixtures, so it could not
reach L3. The director's directive ("Wire a live company consumer for G1-3")
names exactly this. This module is that wire: it takes the SAME live
belief-vs-truth signal the L3 payment triad already produces per run
(`background/live_payment_triad.py`: W2_11 payment TRUTH -> W4_4 seam -> D5
`PaymentObservationConsumer` belief) and shapes it into all three G surfaces --
the inspection chain (G3), the grid score (G1, via the A-atom's grid), and the
emit-DoD ledger record (G2). It is also the L1->L2 feed named in the A and D
atoms ("feed real per-cell coupled gaps from a live run").

WHY A BRIDGE, NOT A SECOND CONSUMER (SIMPLICITY GUARD / R4 -- nearest working
analogue, minimal diff). The live company consumer already exists and is proven
at L3. This module does NOT re-run it and does NOT hold either side of the wall.
It receives the ALREADY-MEASURED PRIMITIVES the run loop computes at
`run_phase2b` measure time -- the true failure count, the company's BELIEVED
(seam-observed) failure count, and the detection gap between them -- and shapes
them into evidence. Because it takes primitives, it imports NEITHER `sim.*` /
`simulation.*` NOR `company.*` / `saas.*`: the epistemic wall is not merely
respected here but structurally unreachable (a stronger stance than
`live_payment_triad.py`, which legitimately must hold both sides to compute the
gap in the first place). Proven by `test_no_sim_or_company_import` (AST scan),
the same guard the D5 module carries.

THE CELL (honest attribution, S2/S3 of the A frame). A live run spans 2016-2025
-- calm years AND the 2021-22 gas crisis -- so the measured payment-detection
gap is REGIME-MIXED, not isolated to one regime. Its natural home in the 5x3
grid is `A1_G2` = affordability-stressed household x crisis/sustained-spike
regime (G2's own named physics is "bill-shock -> arrears, affordability
collapse"). Attributing a regime-mixed measurement to the single G2 cell is an
approximation, registered as an R10 simplification on the emitted record
(`_REGIME_MIXED_SIMP_ID`), NEVER asserted silently. The other 14 cells stay
UNMEASURED -> G1's fail-open floor scores them >= the worst measured cell and
the grid can never report `clean` while any cell is untested. One corner lit,
the rest honestly dark -- exactly the map-of-ignorance the A frame exists to
keep visible.

R12 (anti-goal-seek): the gap is a DIAGNOSTIC. This module never adjusts a gap,
a threshold, or the gate verdict to flatter a "done" reading -- it emits what
was measured and fails LOUD (raises) if the record it just wrote does not pass
the record's own emit-DoD gate (a record that cannot pass its own gate is a
defect, not a silent skip -- R15 fail-closed).

C-S2 (determinism): this module makes no clock or random draw. `as_of` and
`run_git_commit` are gathered by the caller at write time and passed straight
through, identical to `live_payment_triad.measure_and_write`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from background.scope_of_need_scoring_frame import ScopeOfNeedScore, score_scope_of_need
from background.fidelity_inspection_chain import (
    BeliefActionRecord,
    EvidenceRecord,
    InspectionChain,
    WorldRecord,
    assert_no_belief_leak,
    validate_chain,
)
from background.fidelity_evidence_ledger import (
    GateResult,
    append_record,
    fidelity_evidence_gate,
)

# The single cell the live payment consumer illuminates (see module docstring).
LIVE_CELL_ID = "A1_G2"

# Which physics atom this evidence belongs to. The payment TRUTH world atom;
# the gate that reads this ("W2_11 is not emit-DoD-done until it emits live
# evidence") is called with this id. Overridable for tests / a future consumer.
DEFAULT_ATOM_ID = "W2_11_payment_truth"

# Stable rel_id / node refs for the payment detection relationship.
_REL_ID = "live_payment_detection_gap"
_WORLD_REF = "w2_11_payment_truth_series"
_BELIEF_ID = "d5_payment_observation_belief"

# R10 simplification: a regime-MIXED live run attributed to the single G2 cell.
_REGIME_MIXED_SIMP_ID = "live_payment_gap_regime_mixed_attributed_to_G2"


@dataclass(frozen=True)
class LiveFidelityEmission:
    """The result of one live emission -- everything a caller/test needs to
    inspect WITHOUT re-reading the ledger or re-scoring the grid. `gate.passed`
    is always True on a returned value (a failing gate RAISES, never returns),
    so a caller can treat a returned emission as proven-DoD."""

    grid_score: ScopeOfNeedScore
    gate: GateResult
    chain: InspectionChain
    cell_id: str
    detection_gap: float
    true_failures: int
    believed_failures: int


class LiveFidelityGateFailure(RuntimeError):
    """Raised when the record just emitted does not pass its own emit-DoD gate
    -- a record that cannot pass the gate it was written for is a DEFECT, made
    LOUD (R15 fail-closed), never a silent skip."""


def build_inspection_chain(
    *,
    detection_gap: float,
    true_failures: int,
    believed_failures: int,
    as_of: str,
    cell_id: str = LIVE_CELL_ID,
    regime_label: Optional[str] = "mixed_2016_2025",
) -> InspectionChain:
    """Build + validate the four-layer G3 chain for one live payment emission.

    EVIDENCE (the payment-detection relationship) -> WORLD (the SIM payment
    truth series) -> BELIEF_ACTION (what the company OBSERVED through the seam,
    the believed failure count, and the measured gap). `truth_ref` is left
    None on the belief record (the company never holds the answer key);
    `assert_no_belief_leak` proves it, and `validate_chain` proves no edge
    dangles. `regime_label` lives ONLY on the WORLD record (harness/director
    artefact, never read company-side)."""
    chain = InspectionChain()
    evidence = EvidenceRecord(
        rel_id=_REL_ID,
        relationship={
            "kind": "payment_failure_detection",
            "provenance": "estimated_from_data",
            "simplification_id": _REGIME_MIXED_SIMP_ID,
            "detection_gap": float(detection_gap),
            "true_failures": int(true_failures),
            "believed_failures": int(believed_failures),
        },
    )
    chain.add_evidence(evidence)
    chain.add_world(WorldRecord(
        world_series_ref=_WORLD_REF,
        variables=("payment_result", "dd_failure_reason"),
        regime_label=regime_label,
        driven_by=(_REL_ID,),
    ))
    chain.add_belief_action(BeliefActionRecord(
        belief_id=_BELIEF_ID,
        cell=cell_id,
        belief={"observed_failures": int(believed_failures)},
        action={"kind": "arrears_risk_flagging", "flagged_failures": int(believed_failures)},
        gap=float(detection_gap),
        as_of=as_of,
        observed_world_ref=_WORLD_REF,
        cites_evidence=(_REL_ID,),
        truth_ref=None,  # company-clean -- the wall in the data model (G3 S4)
    ))
    validate_chain(chain)
    assert_no_belief_leak(chain)
    return chain


def build_ledger_record(
    *,
    detection_gap: float,
    true_failures: int,
    believed_failures: int,
    atom_id: str = DEFAULT_ATOM_ID,
    cell_id: str = LIVE_CELL_ID,
) -> dict:
    """Shape the G2 emit-DoD ledger record. Provenance is
    `estimated_from_data` (the gap is a genuinely measured live quantity), and
    it STILL carries `simplification_id` documenting the regime-mixed cell
    attribution -- honest beyond the gate's minimum (the gate only REQUIRES a
    simplification_id when provenance == 'asserted'). No `per_cell_lift` is
    emitted: a lift needs a naive-baseline prediction error, which the live run
    does not compute, and fabricating one would be a made-up number (R12)."""
    return {
        "rel_id": _REL_ID,
        "atom_id": atom_id,
        "relationship": {
            "kind": "payment_failure_detection",
            "provenance": "estimated_from_data",
            "simplification_id": _REGIME_MIXED_SIMP_ID,
            "detection_gap": float(detection_gap),
            "true_failures": int(true_failures),
            "believed_failures": int(believed_failures),
            "cell_id": cell_id,
        },
    }


def emit_live_fidelity_evidence(
    *,
    detection_gap: float,
    true_failures: int,
    believed_failures: int,
    as_of: str,
    atom_id: str = DEFAULT_ATOM_ID,
    cell_id: str = LIVE_CELL_ID,
    ledger_path: Optional[Path] = None,
) -> LiveFidelityEmission:
    """Emit ONE live payment belief-vs-truth measurement into all three G
    surfaces and return the composed result.

      G3: build + validate the inspection chain (wall proven no-leak).
      G1: score the 5x3 grid with the single measured `cell_id`, the rest
          untested (fail-open floor) -- never clean while a cell is untested.
      G2: append the emit-DoD ledger record, then RE-READ the gate for
          `atom_id`. A non-passing gate RAISES `LiveFidelityGateFailure`
          (fail-closed): a record that cannot pass its own gate is a defect.

    Pure evidence-shaping over primitives -- no sim/company import, no clock,
    no random draw. R12: emits what was measured, never tunes toward 'done'."""
    chain = build_inspection_chain(
        detection_gap=detection_gap,
        true_failures=true_failures,
        believed_failures=believed_failures,
        as_of=as_of,
        cell_id=cell_id,
    )
    grid_score = score_scope_of_need({cell_id: float(detection_gap)})

    record = build_ledger_record(
        detection_gap=detection_gap,
        true_failures=true_failures,
        believed_failures=believed_failures,
        atom_id=atom_id,
        cell_id=cell_id,
    )
    append_record(record, ledger_path=ledger_path)

    gate = fidelity_evidence_gate(atom_id, ledger_path=ledger_path)
    if not gate.passed:
        raise LiveFidelityGateFailure(
            f"live fidelity emission for {atom_id!r} did not pass its own "
            f"emit-DoD gate: {gate.reasons}"
        )

    return LiveFidelityEmission(
        grid_score=grid_score,
        gate=gate,
        chain=chain,
        cell_id=cell_id,
        detection_gap=float(detection_gap),
        true_failures=int(true_failures),
        believed_failures=int(believed_failures),
    )
