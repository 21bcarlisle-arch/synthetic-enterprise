"""The electricity SVT table is a SECOND HOME for a series the commons already publishes.

WHAT THIS CONTROLS, and why it is a control rather than a repair. `simulation/svt_rates.py`
carries `_SVT_ELEC_PENCE_PER_KWH` as a hand-written table. Its own gas leg does not: it delegates
to `simulation/price_cap_enforcement.binding_cap_unit_rate_gbp_per_mwh_inc_vat`, and the block
above `get_svt_gas_rate_gbp_per_mwh` says exactly why -- "restating it would make a second home
for a number that already has one, and the two would drift".

They drifted. This file measures the drift and holds it from growing. The repair -- the
electricity leg reading the commons the way the gas leg does -- moves the world, so it is its own
increment; this is the mechanism that stops a twelfth divergence appearing while that is done.

FOUND BY `tools/published_row_scalar_census.py`, which ranked four of this table's values as
specificity-1 collisions with the published record. The census compares VALUES, so it found the
copies; it does not compare BASES, and the basis question is what turned four coincidences into
eleven real divergences. Both halves are recorded in
`docs/staging/SEAT_RESULT_THE_ELECTRICITY_SVT_TABLE_IS_A_SECOND_HOME_2026-09-08.md`, including a
prediction this measurement REFUTED.

THE CONTROL IS KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. It asserts that the divergent rows
are a SUBSET of the named ones. Repairing a row -- making the table agree with the publication --
shrinks the set and stays green; a new divergence, or an existing one moving to a different value,
goes red. A control pinned to the exact set would go red when the code became more honest, which
is backwards and has happened in this repository before.
"""
from __future__ import annotations

from datetime import date

import pytest

from simulation.price_cap_enforcement import (
    PUBLISHED_CAP_WINDOWS,
    binding_cap_unit_rate_gbp_per_mwh_inc_vat,
)
from simulation.svt_rates import _SVT_ELEC_PENCE_PER_KWH

#: p/kWh. The table is written to 2dp and the commons to 0.1 GBP/MWh, which is the same
#: precision, so anything above float noise is a real disagreement and not a rounding artefact.
_TOLERANCE_P_PER_KWH = 0.01

#: The span the commons actually publishes. Outside it the accessor carries the last window
#: forward -- that is the commons' own rule for a standing instrument, and comparing the table's
#: declared extrapolation against a carried-forward value would be grading two guesses.
_FIRST_PUBLISHED = PUBLISHED_CAP_WINDOWS[0]["from"]
_LAST_PUBLISHED = PUBLISHED_CAP_WINDOWS[-1]["to"]


#: Every row where the table disagrees with the published binding rate TODAY, with the reason
#: established for each. Grouped by cause, because the four causes need four different repairs.
KNOWN_DIVERGENCES: dict[tuple[int, int], str] = {
    # (1) BLIND TO THE ENERGY PRICE GUARANTEE. The table carries the Ofgem CAP for these
    # windows; the instrument that actually bound a household's unit rate was the EPG, at
    # 34.0p/kWh from Oct-2022 to Jun-2023. The commons publishes both and returns the binding
    # one, and its `epg_note` names this exact failure in advance: "a lane which fails to notice
    # the EPG is a lane that MISREAD the law rather than a lane that was handed a different law".
    # This is the largest error in the table and the largest in the file: +33.00p/kWh at
    # 2023-01 is a reference rate 97% above what an SVT household was charged.
    (2022, 10): "carries the cap (51.89) where the EPG bound at 34.00",
    (2023, 1): "carries the cap (67.47 -> 67.0) where the EPG bound at 34.00",
    (2023, 4): "carries NEITHER: 30.10 is the Jul-2023 cap, in the Apr-2023 slot, where the "
               "EPG bound at 34.00. EPG-blind and window-shifted at once.",
    # (2) A WINDOW LATE. The value is a real published cap, in the wrong window -- the previous
    # one carried forward over a cap change the table missed.
    (2024, 1): "carries the Oct-2023 cap (27.35) over the Jan-2024 change to 28.62",
    # (3) EXTRAPOLATED OVER A PUBLISHED SERIES. The table's own comment says "Extrapolated 2026+
    # -- moderate decline as renewables penetration rises". The commons PUBLISHES 2026, from
    # Ofgem's cap level model v1.31. An invented number standing where an established one exists
    # is the precise shape this atom was drawn to close, and it is four rows wide here.
    (2026, 1): "extrapolated (26.00) where the commons publishes 27.69",
    (2026, 4): "extrapolated (25.50) where the commons publishes 24.67",
    (2026, 7): "extrapolated (25.00) where the commons publishes 26.11",
    (2026, 10): "extrapolated (25.50) where the commons publishes 26.32",
    # (4) TRANSCRIPTION NOISE, <= 0.05p. Too small to move a result and too small to be a
    # different reading; they are simply copies that were typed rather than derived, which is
    # the whole argument for deriving them.
    (2020, 1): "17.81 for a window the commons publishes at 17.85 (the NEXT window's value)",
    (2023, 7): "30.10 against 30.11",
    (2023, 10): "27.40 against 27.35",
}


def divergent_rows(table: dict[tuple[int, int], float]) -> dict[tuple[int, int], tuple[float, float]]:
    """`{key: (table_p_per_kwh, published_p_per_kwh)}` for every row inside the published record
    where the two disagree by more than the tolerance.

    Taking the table as an argument is what makes this file able to fail: the poison round below
    feeds it a table it KNOWS is clean, and a comparison that cannot see a planted disagreement
    would not have seen the eleven real ones either.
    """
    out: dict[tuple[int, int], tuple[float, float]] = {}
    for (year, month), table_p in table.items():
        when = date(year, month, 1)
        if not (_FIRST_PUBLISHED <= when <= _LAST_PUBLISHED):
            continue
        published = binding_cap_unit_rate_gbp_per_mwh_inc_vat("electricity", when)
        if published is None:
            continue
        published_p = published / 10.0
        if abs(table_p - published_p) > _TOLERANCE_P_PER_KWH:
            out[(year, month)] = (table_p, published_p)
    return out


def test_the_comparison_reaches_the_table_at_all():
    """Reachability, first, because every assertion below passes over an empty comparison.

    A `_FIRST_PUBLISHED`/`_LAST_PUBLISHED` window that excluded everything, or an accessor
    returning None throughout, would make this file green and silent.
    """
    compared = [
        k for k in _SVT_ELEC_PENCE_PER_KWH
        if _FIRST_PUBLISHED <= date(k[0], k[1], 1) <= _LAST_PUBLISHED
    ]
    assert len(compared) >= 30, f"only {len(compared)} rows fall inside the published record"
    # and the comparison is not all-exception: most rows genuinely agree, which is what makes
    # the disagreeing ones evidence of a copy rather than of two different quantities.
    agreeing = len(compared) - len(divergent_rows(_SVT_ELEC_PENCE_PER_KWH))
    assert agreeing >= 20, f"only {agreeing} rows agree; the two series may not be comparable"


def test_no_divergence_beyond_the_ones_named():
    """THE CONTROL. A new disagreement, or a named one moving, is a red; repairing one is green."""
    divergent = divergent_rows(_SVT_ELEC_PENCE_PER_KWH)
    unexplained = {k: v for k, v in divergent.items() if k not in KNOWN_DIVERGENCES}
    assert not unexplained, (
        "the electricity SVT table disagrees with the published cap at rows nobody has "
        f"dispositioned: {unexplained}. Each is either a transcription error or a reading that "
        "needs stating; neither is allowed to be silent. The repair that removes this whole "
        "class is the electricity leg reading the commons, as the gas leg already does."
    )


def test_a_planted_disagreement_is_caught():
    """POISON ROUND. `test_no_divergence_beyond_the_ones_named` passes if `divergent_rows` sees
    nothing at all -- a broken accessor, a units slip, a window filter that excludes the world.
    Plant a disagreement in a row that currently AGREES and require it to be found.
    """
    clean = {
        k: v for k, v in _SVT_ELEC_PENCE_PER_KWH.items() if k not in KNOWN_DIVERGENCES
    }
    assert not divergent_rows(clean), "the non-exception rows should agree by construction"
    victim = max(k for k in clean if _FIRST_PUBLISHED <= date(k[0], k[1], 1) <= _LAST_PUBLISHED)
    poisoned = dict(clean)
    poisoned[victim] = clean[victim] + 1.0
    found = divergent_rows(poisoned)
    assert victim in found, f"a 1p/kWh error planted at {victim} was not detected"


def test_the_named_divergences_are_all_still_real():
    """An exception that no longer diverges is stale bookkeeping, not a defect -- but it must not
    sit here unnoticed, because a list of exceptions nobody prunes is how a control quietly stops
    controlling anything. This names them rather than failing: the repair is the point.
    """
    divergent = divergent_rows(_SVT_ELEC_PENCE_PER_KWH)
    stale = sorted(k for k in KNOWN_DIVERGENCES if k not in divergent)
    if stale:
        pytest.skip(
            f"{len(stale)} named divergence(s) now agree with the publication and can be "
            f"deleted from KNOWN_DIVERGENCES: {stale}"
        )


def test_the_epg_rows_are_the_expensive_ones_and_are_not_understated():
    """The size of the error is part of the finding, so it is asserted rather than described.

    2023-01 is the worst: a reference rate 97% above what an SVT household actually paid, in the
    quarter the Ofgem cap peaked at GBP 4,279 and the EPG held the bill at GBP 2,500.
    """
    divergent = divergent_rows(_SVT_ELEC_PENCE_PER_KWH)
    table_p, published_p = divergent[(2023, 1)]
    assert table_p - published_p > 30.0
    assert table_p / published_p > 1.9
