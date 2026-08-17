"""The WORLD's default incidence — how much billed revenue actually goes unpaid.

WHY THIS FILE EXISTS (KNIFE pass 3, `B11_default_incidence_is_the_worlds` —
see `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3x).

`simulation/run_phase2b.py` accrued the world's real-time bad debt from
`saas.cost_to_serve.get_bad_debt_rate()` — the SUPPLIER's provisioning
assumption. That is the B3/B2 inversion again: whatever fraction of revenue the
supplier PROVIDED FOR is the fraction the world made go bad, so the provision
could not be wrong. The COUPLED TRIAD scores the gap between what the company
believes and what the world does; a quantity pinned to the company's opinion by
construction contributes a guaranteed zero to that score.

The inversion here was visible in the supplier's own module docstring, which
said `BAD_DEBT_RATE`/`get_bad_debt_rate()` "remain in this module only because
`simulation/run_phase2b.py` still uses them" — a company constant kept alive to
serve the world.

WHAT THIS IS AND IS NOT. This is the world's IN-LOOP accrual: the settlement
loop books margin period by period, before any bill exists, and something has to
say how much of that revenue never arrives. It is deliberately coarse — a
year-and-segment incidence, exactly as coarse as the figure it replaces.

It is NOT the world's real arrears model. Once bills exist,
`simulation/run_phase4c_on_phase2b.py` OVERWRITES every `bad_debt_gbp` written
from here with the emergent outcome of `simulation/arrears_engine.py` (Phase QD,
which found the flat rate overstated true bad debt ~30x). So on the full run this
accrual is transient. It is NOT dead, though, and that is why it moved rather
than being deleted: `run_phase2b` alone is a legitimate entry point, and inside
it this number feeds `net_margin_gbp`, the running treasury balance and
`is_administration_triggered(treasury)` — the world's own decision about whether
the supplier goes bust mid-run. A supplier's provisioning table deciding whether
the supplier survives is the inversion at its sharpest.

THE MODIFIER WAS ALREADY THE WORLD'S. `simulation/payment_timing.py`'s
`stress_bad_debt_multiplier()` — the income-stress uplift applied on top — has
always been world-side. The world owned how much HARDER a stressed household
finds it to pay, and borrowed only the baseline it multiplied. Half the physics
was already home.

WHAT IS DELIBERATELY NOT HERE: a test asserting these values equal
`saas.cost_to_serve`'s. That would restore in the suite precisely the coupling
this cut removes from the code — the refusal recorded for `B3` (the cap
schedule), `B7` (the hedge floor) and `B10` (household identity), for the same
reason each time. The readings MAY drift; drift is a finding for the harness to
report, never something the suite pins shut (R12).

THE VALUES THEMSELVES. Identical to the ones the company's table carried on
2026-08-14, so this cut moves no simulated number; what changed is who depends on
whom. They are a modelling choice calibrated to the shape of the 2021-22 UK
energy crisis payment-default surge, not a sourced external figure: incidence
roughly quadruples for residential across 2021-22, decays over 2023-24, and is
lowest for I&C, who are credit-checked at connection and can be disconnected
fastest. Segments outside the table, and years outside 2016-2024, fall back to
the baseline.
"""
from __future__ import annotations

# Baseline fraction of billed revenue that goes unpaid, by segment, in an
# ordinary year.
WORLD_BAD_DEBT_INCIDENCE: dict[str, float] = {
    "resi": 0.02,
    "SME": 0.01,
    "I&C": 0.005,
}

# The default segment used for a customer whose segment this world has no
# incidence for. Residential is the conservative choice: it is the highest of
# the three, so an unrecognised segment is never quietly treated as the
# best-behaved one.
_UNKNOWN_SEGMENT_INCIDENCE = 0.02

_WORLD_BAD_DEBT_INCIDENCE_BY_YEAR: dict[int, dict[str, float]] = {
    2016: {"resi": 0.02, "SME": 0.01, "I&C": 0.005},
    2017: {"resi": 0.02, "SME": 0.01, "I&C": 0.005},
    2018: {"resi": 0.02, "SME": 0.01, "I&C": 0.005},
    2019: {"resi": 0.02, "SME": 0.01, "I&C": 0.005},
    2020: {"resi": 0.02, "SME": 0.01, "I&C": 0.005},
    2021: {"resi": 0.04, "SME": 0.015, "I&C": 0.005},
    2022: {"resi": 0.08, "SME": 0.03, "I&C": 0.01},
    2023: {"resi": 0.05, "SME": 0.02, "I&C": 0.005},
    2024: {"resi": 0.03, "SME": 0.012, "I&C": 0.005},
}


def world_bad_debt_incidence(year: int, segment: str) -> float:
    """Fraction of this segment's billed revenue that goes unpaid in `year`.

    Years outside the tabulated span fall back to the segment baseline;
    segments outside the baseline fall back to the residential rate.
    """
    year_rates = _WORLD_BAD_DEBT_INCIDENCE_BY_YEAR.get(year, WORLD_BAD_DEBT_INCIDENCE)
    return year_rates.get(
        segment, WORLD_BAD_DEBT_INCIDENCE.get(segment, _UNKNOWN_SEGMENT_INCIDENCE)
    )
