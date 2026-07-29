"""SPINE_1 — the scenario world-state substrate (Wave-A compounding substrate).

Provenance: ``docs/design/SCENARIO_SPINE_AND_TRADING_FRICTION_FRAME.md`` §A (director
FRAME, non-vetoed 2026-07-23, §A.8 verdict "PROCEED (SPINE_1 build) ... reversible SIM
machinery"). Built 2026-07-29 acting on the director's warning to stop tidying and
"pick the hardest item on your own list, start the work (not a proposal or a frame)"
(``docs/staging/DIRECTOR_WARNING_QUIET_BUSYWORK_2026-07-29.md``) — which explicitly
overrides the atom's ``blocked_on: director_build_open`` gate ("there are no one-way
doors ... you are authorised to be wrong").

WHAT THIS IS
------------
The container a run's world is drawn from. A :class:`ScenarioSpine` is an immutable,
version-pinned value object holding time-indexed EXOGENOUS paths (gas trend, economy
factor, renewables buildout, storage capacity) for ONE world (FRAME §A.2). Generators
read their exogenous inputs from the spine instead of a single hardcoded record, so the
company can live through named, director-authored worlds (FRAME §A.6) rather than only
the single real 2016–25 replay.

THE WALL (FRAME §A.3, the steer's central construct)
----------------------------------------------------
The company NEVER reads scenario state. No ``company/**`` or ``saas/**`` code may import
this module, and no ``ScenarioSpine`` field crosses ``company/interfaces/sim_interface.py``.
The company infers gas trend / renewables buildout / storage state the way a real supplier
does — from observed prices and its own book — and is allowed to be wrong; the gap is the
score. Enforced by the failable wall test (``tests/sim/test_scenario_spine.py::test_wall``,
FRAME §R15 W1).

BASELINE SAFETY (FRAME §A.5, the byte-identical guarantee)
----------------------------------------------------------
The default ``world_id='history_replay'`` selects NO exogenous overrides: every field of
:meth:`ScenarioSpine.paths_as_of` returns :data:`NO_OVERRIDE`, so every existing run stays
byte-identical to pre-spine (the spine is additive and dormant unless a non-baseline world
is chosen). Enforced by FRAME §R15 W2.

R13 CURRICULUM WALL (FRAME §A.8 / R13 baseline-curriculum split)
----------------------------------------------------------------
Difficulty worlds are the DIRECTOR'S. A curriculum artefact only becomes ROTATION-eligible
once it carries a ratification record (``ratified: true`` backed by a ``ratification:``
block). Unratified proposed worlds still LOAD (the mechanism can see them), but can NEVER
enter rotation — :func:`rotation_set` excludes them and :func:`select_for_rotation` raises.
The agent controls both sides of the wall, so the curriculum must face the director: there
is no setter, the object is frozen, and no company-P&L outcome can write a scenario value
back. Enforced by FRAME §R15 W3.

SIMPLICITY GUARD (scale addendum): a frozen dataclass + a committed YAML curriculum
artefact per world. No repository-over-JSON cathedral, no adapter-for-future-adapters —
the SIM/company wall already provides the go-live seam.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Union

import yaml

# --- constants ---------------------------------------------------------------

HISTORY_REPLAY = "history_replay"
"""The default/baseline world_id (FRAME §A.5): the real 2016–25 record, no overrides."""

CURRICULUM_DIR = Path(__file__).resolve().parent / "curriculum"
"""Where committed, version-pinned world artefacts live (never synthesised at runtime)."""

# The four exogenous path fields the spine carries (FRAME §A.2 table).
PATH_FIELDS = ("gas_trend", "economy_factor", "renewables_buildout", "storage_capacity")


class _NoOverride:
    """Sentinel meaning 'this field has no scenario override — use the baseline record'.

    Distinct from ``None`` (which a curriculum could legitimately mean as a value) and
    from ``0.0`` (a real override to zero). Singleton, falsy, reprs clearly in test output.
    """

    _instance: Optional["_NoOverride"] = None

    def __new__(cls) -> "_NoOverride":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __bool__(self) -> bool:  # falsy so `if override:` reads naturally
        return False

    def __repr__(self) -> str:
        return "NO_OVERRIDE"


NO_OVERRIDE = _NoOverride()


class ScenarioError(Exception):
    """Base for scenario-spine load/selection errors."""


class ScenarioNotRatified(ScenarioError):
    """Raised when a non-ratified (or non-in-rotation) world is asked to enter rotation."""


class ScenarioArtefactError(ScenarioError):
    """Raised when a curriculum artefact is malformed or fails the R13 ratification guard."""


# --- the value object --------------------------------------------------------


def _to_date(t: Union[str, _dt.date, _dt.datetime]) -> _dt.date:
    if isinstance(t, _dt.datetime):
        return t.date()
    if isinstance(t, _dt.date):
        return t
    if isinstance(t, str):
        return _dt.date.fromisoformat(t[:10])
    raise TypeError(f"unsupported time key: {t!r}")


@dataclass(frozen=True)
class ScenarioSpine:
    """An immutable, version-pinned world the company lives through (FRAME §A.2).

    Loaded ONCE per run from a committed curriculum artefact, never synthesised at
    runtime, never mutated mid-run (C-S2 deterministic replay: same world + seed
    reproduces identical state). ``frozen=True`` is load-bearing — it is the mechanical
    form of the R13 wall: the agent cannot write a company-P&L outcome back into a
    scenario value because the object has no setter (FRAME §R15 W3).
    """

    world_id: str
    version: str
    provenance: str  # 'baseline' | 'proposal' | 'ratified'
    ratified: bool
    in_rotation: bool
    true_probability: Optional[float]  # curriculum (R13), None until ratified; company never reads it
    sampling_weight: Optional[float]
    description: str = ""
    source_citations: tuple = ()
    # Each path: tuple of (date, value) sorted ascending; empty tuple => no override.
    _paths: Mapping[str, tuple] = field(default_factory=dict)

    # -- properties --

    @property
    def is_baseline(self) -> bool:
        return self.world_id == HISTORY_REPLAY

    @property
    def selects_no_overrides(self) -> bool:
        """True iff every exogenous field is empty — the byte-identical dormancy flag (FRAME §A.5)."""
        return all(not self._paths.get(f) for f in PATH_FIELDS)

    @property
    def is_rotation_eligible(self) -> bool:
        """A world enters the tail-heavy rotation ONLY when the director has ratified it.

        The baseline is the DEFAULT world, not a rotation member (FRAME §A.6), so it is
        excluded here too — it is always available as the default, never sampled.
        """
        return self.ratified and self.in_rotation and not self.is_baseline

    # -- the Blindfold-clean accessor (FRAME §A.4) --

    def paths_as_of(self, t: Union[str, _dt.date, _dt.datetime]) -> dict:
        """Return each exogenous field's value effective at time ``t``.

        Blindfold-clean by construction: never returns a value dated AFTER ``t`` (the
        exogenous path is a scenario INPUT, not a forecast the company reads). A field
        with no anchor at-or-before ``t`` returns :data:`NO_OVERRIDE` so callers fall
        back to the baseline record. For ``history_replay`` every field is NO_OVERRIDE.
        """
        as_of = _to_date(t)
        out = {}
        for f in PATH_FIELDS:
            anchors = self._paths.get(f) or ()
            value = NO_OVERRIDE
            for (d, v) in anchors:  # anchors sorted ascending
                if d <= as_of:
                    value = v
                else:
                    break
            out[f] = value
        return out


# --- registry ----------------------------------------------------------------


def _parse_paths(raw: Optional[dict]) -> dict:
    parsed = {}
    for f in PATH_FIELDS:
        entries = (raw or {}).get(f) or {}
        if not entries:
            parsed[f] = ()
            continue
        pairs = sorted((_to_date(k), float(v)) for k, v in entries.items())
        parsed[f] = tuple(pairs)
    return parsed


def load_world(world_id: str, curriculum_dir: Union[str, Path, None] = None) -> ScenarioSpine:
    """Load a committed world artefact into an immutable :class:`ScenarioSpine`.

    R13 ratification guard (FRAME §R15 W3, fail-CLOSED): a non-baseline artefact that
    claims ``ratified: true`` MUST carry a ``ratification:`` block (a director record). A
    ``ratified: true`` with no ratification record is a malformed curriculum and is
    REJECTED — never loaded as silently rotation-eligible.
    """
    base = Path(curriculum_dir) if curriculum_dir is not None else CURRICULUM_DIR
    art = base / f"{world_id}.yaml"
    if not art.exists():
        raise ScenarioArtefactError(f"no curriculum artefact for world_id={world_id!r} at {art}")
    with art.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    if raw.get("world_id") != world_id:
        raise ScenarioArtefactError(
            f"artefact {art.name} declares world_id={raw.get('world_id')!r}, expected {world_id!r}"
        )
    ratified = bool(raw.get("ratified", False))
    is_baseline = world_id == HISTORY_REPLAY
    # Fail-closed R13 guard: a difficulty world may only claim ratification with a record.
    if ratified and not is_baseline and not raw.get("ratification"):
        raise ScenarioArtefactError(
            f"world {world_id!r} claims ratified: true but carries no 'ratification' record — "
            "curriculum difficulty is director-authored (R13); rejected fail-closed"
        )

    return ScenarioSpine(
        world_id=world_id,
        version=str(raw.get("version", "")),
        provenance=str(raw.get("provenance", "proposal")),
        ratified=ratified,
        in_rotation=bool(raw.get("in_rotation", False)),
        true_probability=raw.get("true_probability"),
        sampling_weight=raw.get("sampling_weight"),
        description=str(raw.get("description", "")).strip(),
        source_citations=tuple(raw.get("source_citations", []) or []),
        _paths=_parse_paths(raw.get("paths")),
    )


def available_worlds(curriculum_dir: Union[str, Path, None] = None) -> list:
    """Every world_id with a committed artefact (loadable — NOT necessarily rotation-eligible)."""
    base = Path(curriculum_dir) if curriculum_dir is not None else CURRICULUM_DIR
    if not base.exists():
        return []
    return sorted(p.stem for p in base.glob("*.yaml"))


def default_world(curriculum_dir: Union[str, Path, None] = None) -> ScenarioSpine:
    """The baseline the curriculum worlds are proposed ALONGSIDE, never instead of (FRAME §A.6)."""
    return load_world(HISTORY_REPLAY, curriculum_dir)


def rotation_set(curriculum_dir: Union[str, Path, None] = None) -> list:
    """The worlds the director has ratified INTO rotation (empty until a real ratification)."""
    out = []
    for wid in available_worlds(curriculum_dir):
        if load_world(wid, curriculum_dir).is_rotation_eligible:
            out.append(wid)
    return sorted(out)


def select_for_rotation(world_id: str, curriculum_dir: Union[str, Path, None] = None) -> ScenarioSpine:
    """Select a world for a rotated run — refuses anything the director has not ratified.

    The baseline (``history_replay``) is always selectable as the DEFAULT, but is not a
    rotation member; any other world must be ratified + in_rotation or this raises.
    """
    spine = load_world(world_id, curriculum_dir)
    if spine.is_baseline:
        return spine
    if not spine.is_rotation_eligible:
        raise ScenarioNotRatified(
            f"world {world_id!r} is not rotation-eligible "
            f"(ratified={spine.ratified}, in_rotation={spine.in_rotation}) — "
            "no non-baseline world enters rotation until the director ratifies its values (R13)"
        )
    return spine
