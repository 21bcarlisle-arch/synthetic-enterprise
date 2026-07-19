"""The fidelity-evidence INSPECTION CHAIN -- atom **G3** (Epoch-2
`G_data_learning` lane, HARNESS-side; sibling to G1's
`background/fidelity_grid_scorer.py` and G2's
`background/fidelity_evidence_ledger.py`).

Design source (read this pass, no network):
    docs/design/EPOCH2_G_FIDELITY_EVIDENCE_MACHINERY_DISCOVER.md  S4 (the
        four-layer inspection chain, navigable both directions) and S5 (the
        R15 mutation requirements this module's own controls must satisfy).

WHAT THIS MODULE IS. The DATA MODEL + LINK GRAPH for S4's four-layer
inspection chain -- **no live sim consumer, no SITE rendering** (that is a
separate atom; S4's own words: "this section designs the data model, the
SITE rendering is the separate SITE-lane atom"). Three pieces:

    1. Four validated record types -- EVIDENCE / WORLD / BELIEF_ACTION /
       CONSTRAINT (S4's table, verbatim field names).
    2. A directed, cycle-safe link graph over those records
       (`InspectionChain.link` / `.causes_of` / `.consequences_of`) that is
       *navigable* in both directions even though each edge is stored once,
       directed cause -> consequence (see "EDGE DIRECTION" note below).
    3. The in-schema wall-discipline validator, `assert_no_belief_leak` --
       the load-bearing control: a BELIEF/ACTION record that carries a
       non-null `truth_ref` is a WALL LEAK (S4: "a layer-(c) belief that
       could see truth_ref is a wall leak, caught red") and this function
       RAISES on it. Plus `validate_links`, the dangling-link fail-closed
       guard (S4's bidirectional graph is only trustworthy if every edge
       resolves to a real node).

FIELD-SHAPE REUSE (do NOT invent a divergent schema). The EVIDENCE layer's
`relationship` mapping reuses G2's shape verbatim (`kind`, `strength`,
`provenance`, `series_ref`, `independent_anchor`, `simplification_id`) --
an EVIDENCE node in this chain is the same conceptual object as a G2 ledger
record; this module does not re-derive or re-validate G2's own structural
rules (that is `fidelity_evidence_ledger._validate_record`'s job), it only
requires the mapping be present so the chain can hang WORLD/BELIEF/CONSTRAINT
links off a stable `rel_id`.

EDGE DIRECTION (an R10 simplification, registered here, not hidden). S4's
table lists each layer's links with a per-row "<-"/"->" arrow (e.g. the
EVIDENCE row: "-> produces WORLD outputs (fwd); <- cited by a BELIEF gap
(back)"; the BELIEF row: "<- WORLD it observed; <- EVIDENCE it
mis/estimated; -> CONSTRAINT that bent the action"). Read literally the two
rows describe the SAME connection from each endpoint's own point of view
("fwd"/"back" are the two traversal DIRECTIONS over one edge, not two
edges). This module therefore stores exactly ONE directed edge per relation
-- cause -> consequence -- and exposes traversal in BOTH directions
(`causes_of` walks edges backward, `consequences_of` walks them forward)
rather than materialising a duplicate reverse edge. The five canonical
edges (matching S4's table row-by-row):

    EVIDENCE   -> WORLD           kind="produces"          (Evidence row fwd / World row <-)
    WORLD      -> BELIEF_ACTION   kind="observed_by"       (World row fwd / Belief row <-)
    EVIDENCE   -> BELIEF_ACTION   kind="cites_evidence"    (Belief row <- "EVIDENCE it mis/estimated";
                                                              a direct link for a belief that estimated
                                                              a relationship without an intervening
                                                              WORLD series)
    BELIEF_ACTION -> CONSTRAINT   kind="bent_by"           (Belief row fwd / Constraint row <-)
    CONSTRAINT -> EVIDENCE        kind="prevents_exploitation_of"  (Constraint row fwd: "the
                                                              EVIDENCE/relationship whose exploitation
                                                              it prevented")

Note the CONSTRAINT -> EVIDENCE edge closes a cycle (EVIDENCE -> WORLD ->
BELIEF_ACTION -> CONSTRAINT -> EVIDENCE). This is intentional and matches
S4's own text ("cut this relationship, what loses fidelity?" is a
consequences_of(EVIDENCE) query that legitimately terminates back at a
CONSTRAINT that in turn references other EVIDENCE) -- `causes_of` /
`consequences_of` are cycle-safe (visited-set BFS), never infinite-loop.

A note on the doc's own worked example ("a large BELIEF gap -> follow ...
back to the EVIDENCE relationships that produced it AND the CONSTRAINT that
bent the response"): in the human narrative both EVIDENCE and CONSTRAINT
read as "causes" of an odd BELIEF outcome, but in this directed data model
EVIDENCE is upstream of BELIEF_ACTION (`causes_of` territory) while
CONSTRAINT is downstream of it (`consequences_of` territory, since the
CONSTRAINT record explains why THIS action deviated -- it is authored citing
the action, not the other way round). This module exposes the pure
directional primitives the DISCOVER doc asks for (`link`/`causes_of`/
`consequences_of`); composing both into a single "explain this node" view
for a director's drill-down is the SITE atom's job (S4's own scope line),
not re-implemented here.

THE WALL (CLAUDE.md Architectural Laws). Pure HARNESS code, same standing as
`fidelity_grid_scorer.py` / `fidelity_evidence_ledger.py`: it sits OUTSIDE
the epistemic wall by design, and never imports `sim.*` / `simulation.*` /
`company.*` / `saas.*`. It operates purely on already-computed record dicts
handed to it by callers on either side of the wall -- including the one
record type (BELIEF_ACTION) that is ALLOWED to carry a company-observable
view alongside a harness-only `truth_ref`, which is exactly why this module
must police that field rather than merely store it.

R12 anti-goal-seek: nothing here adjusts a record, a link, or a validator's
verdict to flatter a "done" reading.

R15: `assert_no_belief_leak` and `validate_links` are each proven, in
`tests/test_fidelity_inspection_chain.py`, to fire on their own named
defect (a BELIEF_ACTION carrying `truth_ref`; a link referencing a missing
node id) and clear when the defect is removed -- mutation-tested, not just
happy-path-tested. `causes_of`/`consequences_of` correctness is proven on a
small hand-built chain, including a mutation that REVERSES a link's
direction and asserts the traversal result changes accordingly (proof the
traversal actually respects edge direction, not a tautology that would
return the same answer either way).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, FrozenSet, List, Mapping, Optional, Set, Tuple

# ===========================================================================
# Layer identifiers + node-id namespacing
# ===========================================================================

LAYER_EVIDENCE = "EVIDENCE"
LAYER_WORLD = "WORLD"
LAYER_BELIEF_ACTION = "BELIEF_ACTION"
LAYER_CONSTRAINT = "CONSTRAINT"

LAYERS: Tuple[str, ...] = (
    LAYER_EVIDENCE, LAYER_WORLD, LAYER_BELIEF_ACTION, LAYER_CONSTRAINT,
)


def _node_id(layer: str, local_id: str) -> str:
    """The stable, namespaced node id every record type derives its own
    `node_id` from -- prevents a WORLD ref and an EVIDENCE rel_id that
    happen to share a string from colliding into the same graph node."""
    return f"{layer}::{local_id}"


# ===========================================================================
# The four record types (S4's table, verbatim field names)
# ===========================================================================

@dataclass(frozen=True)
class EvidenceRecord:
    """Layer (a) EVIDENCE -- the data + fit behind a relationship. Field
    names match G2's ledger record (`fidelity_evidence_ledger.py`) so a G2
    record's `rel_id` / `relationship` mapping serialises straight in
    without a translation layer."""

    rel_id: str
    relationship: Mapping[str, Any]  # kind/strength/provenance/series_ref/independent_anchor/... (G2 shape)
    node_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.rel_id:
            raise ValueError("EvidenceRecord.rel_id must be non-empty")
        object.__setattr__(self, "node_id", _node_id(LAYER_EVIDENCE, self.rel_id))


@dataclass(frozen=True)
class WorldRecord:
    """Layer (b) WORLD -- the simulated output as an explorable multi-
    variable time series. `regime_label` is HIDDEN FROM THE COMPANY (S4:
    "a real supplier gets no labelled regime") -- this record type is a
    harness/director artefact; company-facing code must never read
    `regime_label` off of it (enforced at the seam that constructs a
    company-visible view, not here -- this module only stores the field
    honestly rather than pretending it doesn't exist)."""

    world_series_ref: str
    variables: Tuple[str, ...]
    regime_label: Optional[str]  # harness/director-only; company never reads this
    driven_by: Tuple[str, ...] = ()  # rel_ids of the EVIDENCE that produced this series
    node_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.world_series_ref:
            raise ValueError("WorldRecord.world_series_ref must be non-empty")
        object.__setattr__(self, "node_id", _node_id(LAYER_WORLD, self.world_series_ref))


@dataclass(frozen=True)
class BeliefActionRecord:
    """Layer (c) BELIEF/ACTION -- what the company observed, believed
    (point-in-time, NEVER hindsight), and did, plus the measured
    belief-vs-truth gap.

    `truth_ref` is the HARNESS-ONLY field (S4: "the SIM answer key ... a
    harness-only field the company never reads"). It exists on this record
    type ONLY so the harness's own copy of the chain can hold it for gap
    computation; any record that is meant to represent what the COMPANY
    itself can see must leave it `None`. `assert_no_belief_leak` below is
    the mechanised version of that rule -- a non-null `truth_ref` on this
    record type is flagged as a wall leak, not merely discouraged.
    """

    belief_id: str
    cell: str
    belief: Mapping[str, Any]     # observable-only view the company actually held
    action: Mapping[str, Any]
    gap: Optional[float]
    as_of: str                    # PIT stamp -- never a hindsight timestamp
    observed_world_ref: Optional[str] = None   # WORLD.world_series_ref it observed
    cites_evidence: Tuple[str, ...] = ()        # rel_ids it mis/estimated
    truth_ref: Optional[str] = None             # HARNESS-ONLY -- see docstring; must be None
    node_id: str = field(init=False)            # to yield a clean (non-leaking) record.

    def __post_init__(self) -> None:
        if not self.belief_id:
            raise ValueError("BeliefActionRecord.belief_id must be non-empty")
        if not self.as_of:
            raise ValueError("BeliefActionRecord.as_of (PIT stamp) is required")
        object.__setattr__(self, "node_id", _node_id(LAYER_BELIEF_ACTION, self.belief_id))


@dataclass(frozen=True)
class ConstraintRecord:
    """Layer (d) CONSTRAINT -- why the action was not the naive optimum:
    which constraint bound, the shadow price, the trade-off made."""

    constraint_id: str
    binding_constraint: str
    naive_optimum: Any
    trade_off: str
    shadow_price: Optional[float] = None
    transversal_pressure: Optional[str] = None
    bends_action: Optional[str] = None          # belief_id of the ACTION it bent
    prevents_evidence: Tuple[str, ...] = ()      # rel_ids whose exploitation it prevented
    node_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.constraint_id:
            raise ValueError("ConstraintRecord.constraint_id must be non-empty")
        if not self.binding_constraint:
            raise ValueError("ConstraintRecord.binding_constraint must be non-empty")
        object.__setattr__(self, "node_id", _node_id(LAYER_CONSTRAINT, self.constraint_id))


ChainNode = Any  # one of the four record dataclasses above


# ===========================================================================
# Exceptions -- fail-closed, per R15
# ===========================================================================

class DanglingLink(ValueError):
    """Raised by `validate_links` when an edge references a node id that is
    not present in the chain's own node set -- a bidirectional graph is only
    trustworthy if every edge resolves; a dangling link is FAIL-CLOSED, not
    silently dropped from traversal."""


class BeliefLeakError(ValueError):
    """Raised by `assert_no_belief_leak` when a BELIEF_ACTION record
    carries a non-null `truth_ref` -- the epistemic wall expressed in the
    data model (S4). This is the load-bearing control this atom exists to
    provide."""


# ===========================================================================
# The link graph
# ===========================================================================

@dataclass(frozen=True)
class Link:
    """One directed edge, cause -> consequence (see module docstring's
    EDGE DIRECTION note for why this is stored once, not duplicated in both
    directions -- traversal, not storage, is bidirectional)."""

    cause_id: str
    consequence_id: str
    kind: str


class InspectionChain:
    """The four-layer inspection chain: a node registry (keyed by
    namespaced `node_id`) plus a directed edge list, with cycle-safe
    both-directions traversal. Pure graph ops over the record set -- no I/O,
    no sim/company import, no live consumer wiring (that is later atom
    work; see module docstring)."""

    def __init__(self) -> None:
        self._nodes: Dict[str, ChainNode] = {}
        self._links: List[Link] = []

    # -- node registration --------------------------------------------------

    def add_node(self, node: ChainNode) -> str:
        """Register any of the four record types by its own `node_id`.
        Re-adding the same `node_id` overwrites (last-write-wins, matching
        the ledger's own read-merge-write convention) rather than silently
        keeping a stale copy."""
        node_id = node.node_id
        self._nodes[node_id] = node
        return node_id

    def add_evidence(self, rec: EvidenceRecord) -> str:
        return self.add_node(rec)

    def add_world(self, rec: WorldRecord) -> str:
        """Registers the WORLD node AND the canonical EVIDENCE -> WORLD
        `produces` edges implied by `rec.driven_by` (auto-derived from the
        record's own reference field, so a caller cannot register a WORLD
        series without its provenance edge silently missing)."""
        node_id = self.add_node(rec)
        for rel_id in rec.driven_by:
            self.link(_node_id(LAYER_EVIDENCE, rel_id), node_id, kind="produces")
        return node_id

    def add_belief_action(self, rec: BeliefActionRecord) -> str:
        """Registers the BELIEF_ACTION node AND its canonical incoming
        edges: WORLD -> BELIEF_ACTION (`observed_by`, from
        `observed_world_ref`) and EVIDENCE -> BELIEF_ACTION
        (`cites_evidence`, from `cites_evidence`)."""
        node_id = self.add_node(rec)
        if rec.observed_world_ref:
            self.link(_node_id(LAYER_WORLD, rec.observed_world_ref), node_id, kind="observed_by")
        for rel_id in rec.cites_evidence:
            self.link(_node_id(LAYER_EVIDENCE, rel_id), node_id, kind="cites_evidence")
        return node_id

    def add_constraint(self, rec: ConstraintRecord) -> str:
        """Registers the CONSTRAINT node AND its canonical edges:
        BELIEF_ACTION -> CONSTRAINT (`bent_by`, from `bends_action`) and
        CONSTRAINT -> EVIDENCE (`prevents_exploitation_of`, from
        `prevents_evidence`)."""
        node_id = self.add_node(rec)
        if rec.bends_action:
            self.link(_node_id(LAYER_BELIEF_ACTION, rec.bends_action), node_id, kind="bent_by")
        for rel_id in rec.prevents_evidence:
            self.link(node_id, _node_id(LAYER_EVIDENCE, rel_id), kind="prevents_exploitation_of")
        return node_id

    # -- the required pure graph ops -----------------------------------------

    def link(self, cause_id: str, consequence_id: str, kind: str) -> Link:
        """Add one directed edge, cause -> consequence. Pure graph op --
        does not require either id to already be registered (so a
        hand-built test chain, or the R15 dangling-link mutation, can
        construct an edge before/without its node; `validate_links` is the
        separate fail-closed check that catches that case)."""
        edge = Link(cause_id=cause_id, consequence_id=consequence_id, kind=kind)
        self._links.append(edge)
        return edge

    def _traverse(self, start_id: str, *, forward: bool) -> FrozenSet[str]:
        """Cycle-safe BFS transitive closure. `forward=True` walks edges
        cause -> consequence (i.e. `consequences_of`); `forward=False` walks
        them consequence -> cause (i.e. `causes_of`). Never infinite-loops
        on a cycle (e.g. the canonical EVIDENCE->WORLD->BELIEF_ACTION->
        CONSTRAINT->EVIDENCE cycle) because of the `seen` set."""
        seen: Set[str] = set()
        frontier: List[str] = [start_id]
        while frontier:
            current = frontier.pop()
            for edge in self._links:
                src, dst = (edge.cause_id, edge.consequence_id) if forward else (edge.consequence_id, edge.cause_id)
                if src == current and dst != start_id and dst not in seen:
                    seen.add(dst)
                    frontier.append(dst)
        return frozenset(seen)

    def causes_of(self, node_id: str) -> FrozenSet[str]:
        """Every node upstream of `node_id` (transitive closure, walking
        edges backward: consequence -> cause). Excludes `node_id` itself."""
        return self._traverse(node_id, forward=False)

    def consequences_of(self, node_id: str) -> FrozenSet[str]:
        """Every node downstream of `node_id` (transitive closure, walking
        edges forward: cause -> consequence). Excludes `node_id` itself."""
        return self._traverse(node_id, forward=True)

    # -- accessors ------------------------------------------------------------

    @property
    def nodes(self) -> Mapping[str, ChainNode]:
        return dict(self._nodes)

    @property
    def links(self) -> Tuple[Link, ...]:
        return tuple(self._links)

    def nodes_of_layer(self, layer: str) -> Tuple[ChainNode, ...]:
        prefix = f"{layer}::"
        return tuple(n for nid, n in self._nodes.items() if nid.startswith(prefix))


# ===========================================================================
# Validators -- fail-closed (R15)
# ===========================================================================

def validate_links(chain: InspectionChain) -> None:
    """Every edge's `cause_id` and `consequence_id` must resolve to a
    registered node. FAIL-CLOSED (R15 fail-silent doctrine): a dangling
    link is raised loud, never silently skipped by the traversal (a
    traversal that quietly ignores an edge to a missing node would let a
    malformed chain LOOK complete)."""
    known = set(chain.nodes.keys())
    dangling: List[str] = []
    for edge in chain.links:
        if edge.cause_id not in known:
            dangling.append(f"{edge.kind}: cause_id {edge.cause_id!r} has no registered node")
        if edge.consequence_id not in known:
            dangling.append(f"{edge.kind}: consequence_id {edge.consequence_id!r} has no registered node")
    if dangling:
        raise DanglingLink(
            "inspection chain has dangling link(s): " + "; ".join(dangling)
        )


def assert_no_belief_leak(chain: InspectionChain) -> None:
    """THE load-bearing wall-discipline control (S4). A BELIEF_ACTION
    record carrying a non-null `truth_ref` is a flagged epistemic-wall leak
    -- the company-facing layer must never be able to see the harness's own
    answer key. Raises `BeliefLeakError` (fail loud, not a returned bool a
    caller could ignore) naming every offending `belief_id`.

    Mutation-tested (R15, `tests/test_fidelity_inspection_chain.py`): give a
    BELIEF_ACTION record a `truth_ref` -> this MUST raise; remove it -> the
    same chain MUST validate clean.
    """
    leaking = [
        rec.belief_id
        for rec in chain.nodes_of_layer(LAYER_BELIEF_ACTION)
        if getattr(rec, "truth_ref", None) is not None
    ]
    if leaking:
        raise BeliefLeakError(
            "epistemic wall leak: BELIEF_ACTION record(s) carry a non-null "
            f"truth_ref (harness-only field, S4): {sorted(leaking)}"
        )


def validate_chain(chain: InspectionChain) -> None:
    """Convenience: run both fail-closed validators. Order matters only in
    that both must run -- neither short-circuits information the other
    would have reported; each raises independently so a caller invoking
    them separately gets the same verdicts as calling this."""
    validate_links(chain)
    assert_no_belief_leak(chain)
