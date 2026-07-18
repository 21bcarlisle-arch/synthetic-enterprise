"""W1_3 Gap 3 — the INDEPENDENT validator anchor (anti-marking-own-homework).

The weather engine (``sim/weather_engine.py``) is CALIBRATED on the 4-location
Open-Meteo daily series (``sim/weather_data/*.csv``). It must therefore NOT be
VALIDATED on that same series — a generator scored against its own fitting data
is marking its own homework and can hide a real defect. The atom's registered
anchoring rule (see ``docs/design/NATIONAL_WEATHER_SIGNAL_FRAME.md`` §3 Gap 3,
``WEATHER_PHYSICS_HIERARCHY_DESIGN.md`` §5) requires the GENERATOR anchor and the
VALIDATOR anchor to be **different sources**.

This module is that seam. It defines:

  * ``IndependentAnchor`` — a typed, injectable published-statistic anchor, with
    an explicit ``is_placeholder`` flag and ``source`` citation. The value is
    OPTIONAL: a placeholder anchor carries NO magnitude at all (``value=None``)
    rather than a fabricated number.
  * ``validate_against_independent_anchor`` — compares a synthetic statistic to
    the anchor and returns a typed result. Crucially it is **fail-closed** (R15
    FAIL-SILENT guard): when the anchor is a placeholder / has no real magnitude,
    the result is ``INDETERMINATE`` — it can NEVER certify a PASS off a
    placeholder. An unavailable check is a FAILED check, never a silent green.

HONESTY / R10 named simplification (this build fork has NO network):
  The real independent magnitude — a published GB Dunkelflaute / cold-and-still
  spell frequency (candidate sources named below) — could not be fetched. The
  anchor mechanism is fully real; only the *magnitude* is a labelled placeholder
  (``value=None``), so the real figure drops in through ``IndependentAnchor``
  without touching any logic. Registered in ``SIMPLIFICATIONS``.

Epistemic wall: SIM-side world validation. Nothing here is company-readable; the
company never validates against SIM ground truth, and this file imports no
``company.*`` / ``saas.*``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


SIMPLIFICATIONS: list[dict[str, str]] = [
    {
        "id": "W1_3_INDEPENDENT_ANCHOR_MAGNITUDE_PLACEHOLDER",
        "what": "The independent-validator anchor magnitude (a published GB "
                "cold-and-still / Dunkelflaute spell frequency) is a PLACEHOLDER "
                "(value=None). No real number is asserted — fetching a published "
                "source needs network this build fork does not have.",
        "why_ok": "The anchor MECHANISM (a typed, injectable, fail-closed anchor "
                  "distinct from the generator's Open-Meteo fit) is fully real. "
                  "validate_against_independent_anchor returns INDETERMINATE — "
                  "never PASS — off a placeholder, so no false green can arise. "
                  "The real magnitude drops in via IndependentAnchor with no "
                  "logic change. Fabricating a precise real figure here would "
                  "violate Historical Ground Truth; a placeholder does not.",
        "rule": "R10",
        "unblocks_when": "a discovery-agent pull of a published GB Dunkelflaute / "
                         "cold-and-still spell-frequency statistic (candidates: "
                         "NESO Winter Outlook / ESO system-stress commentary; Met "
                         "Office seasonal & extreme-event bulletins on named "
                         "blocking-high episodes; published DESNZ/BEIS degree-day "
                         "extreme records) — a SOURCE DISTINCT from the 4-location "
                         "Open-Meteo series the generator is fitted on.",
    },
]


@dataclass(frozen=True)
class IndependentAnchor:
    """A published, independent validation statistic — a DIFFERENT source from
    the generator's fitting data.

    ``value`` is Optional on purpose: a placeholder anchor carries no magnitude
    (``None``) rather than a fabricated number. Inject the real ``value`` +
    ``tolerance`` (and set ``is_placeholder=False``) once a real figure is pulled.
    """

    name: str
    metric: str  # what the statistic measures
    source: str  # published-source citation (or placeholder note)
    is_placeholder: bool
    value: Optional[float] = None
    tolerance: Optional[float] = None
    unit: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        # Guard against a self-contradictory anchor: a non-placeholder anchor MUST
        # carry a real magnitude + tolerance, or it cannot validate anything.
        if not self.is_placeholder and (self.value is None or self.tolerance is None):
            raise ValueError(
                "a non-placeholder IndependentAnchor must have both value and "
                "tolerance set; got value=%r tolerance=%r" % (self.value, self.tolerance)
            )


@dataclass(frozen=True)
class ValidationResult:
    status: str  # "PASS" | "FAIL" | "INDETERMINATE_PLACEHOLDER"
    anchor_name: str
    synthetic_value: float
    anchor_value: Optional[float]
    tolerance: Optional[float]
    message: str

    @property
    def is_pass(self) -> bool:
        return self.status == "PASS"


# ---------------------------------------------------------------------------
# The placeholder anchor (labelled; carries NO magnitude — value=None).
# ---------------------------------------------------------------------------
PLACEHOLDER_DUNKELFLAUTE_ANCHOR = IndependentAnchor(
    name="gb_cold_still_spells_per_winter",
    metric="count of cold-and-still spells (>=3 consecutive days, both "
           "temperature and wind in their seasonal low tail) per winter",
    source="PLACEHOLDER — no real figure pulled (no network in this build fork). "
           "Intended source: a published GB Dunkelflaute / cold-and-still spell "
           "frequency DISTINCT from the 4-location Open-Meteo generator fit "
           "(NESO Winter Outlook / Met Office extreme-event bulletins / DESNZ "
           "degree-day extremes). See SIMPLIFICATIONS.",
    is_placeholder=True,
    value=None,
    tolerance=None,
    unit="spells/winter",
    notes="R10 named simplification. Injectable — real magnitude drops in here.",
)


def validate_against_independent_anchor(
    synthetic_value: float,
    anchor: IndependentAnchor = PLACEHOLDER_DUNKELFLAUTE_ANCHOR,
) -> ValidationResult:
    """Validate a synthetic statistic against an INDEPENDENT published anchor.

    Fail-closed (R15 FAIL-SILENT guard): a placeholder anchor (or any anchor with
    no real magnitude) yields ``INDETERMINATE_PLACEHOLDER`` — it CANNOT return
    PASS. This is deliberate: an unavailable independent check is a FAILED check,
    not a silent green, and it prevents the atom's L3 anchoring gate from being
    satisfied by a fabricated/absent number.
    """
    if anchor.is_placeholder or anchor.value is None or anchor.tolerance is None:
        return ValidationResult(
            status="INDETERMINATE_PLACEHOLDER",
            anchor_name=anchor.name,
            synthetic_value=float(synthetic_value),
            anchor_value=anchor.value,
            tolerance=anchor.tolerance,
            message=(
                "INDETERMINATE: the independent anchor is a labelled placeholder "
                "(no real magnitude). Cannot certify PASS off a placeholder — an "
                "unavailable independent check is a FAILED check (R15). Inject a "
                "real IndependentAnchor to run the comparison."
            ),
        )

    within = abs(float(synthetic_value) - anchor.value) <= anchor.tolerance
    return ValidationResult(
        status="PASS" if within else "FAIL",
        anchor_name=anchor.name,
        synthetic_value=float(synthetic_value),
        anchor_value=anchor.value,
        tolerance=anchor.tolerance,
        message=(
            "synthetic=%.3f vs independent anchor=%.3f±%.3f %s -> %s"
            % (
                synthetic_value,
                anchor.value,
                anchor.tolerance,
                anchor.unit,
                "PASS" if within else "FAIL",
            )
        ),
    )
