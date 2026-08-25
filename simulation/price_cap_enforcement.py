"""The world's OWN reading of the Ofgem Default Tariff Cap.

KNIFE pass 3, design block `B3_world_needs_its_own_cap_physics`, 2026-08-10.

WHY THIS MODULE EXISTS
----------------------
`simulation/hedged_settlement.py` used to import
`company.pricing.ofgem_price_cap.get_cap_unit_rate_for_date` to decide what
ceiling actually bound a deemed customer's bill. That made the company's READING
of the cap into the world's ENFORCEMENT of it, and collapsed the one thing the
regulation-commons doctrine exists to keep apart:

  > the regulatory TEXT is a shared commons readable by every lane, because law
  > is published in reality — but each lane's IMPLEMENTATION of that law stays
  > independently owned, precisely so that a company misreading the cap stays
  > structurally possible, matching real suppliers who get fined for exactly that.

With the import in place a misread was not merely unlikely, it was
unrepresentable: whatever the company believed the ceiling was, that is what the
world charged, so the belief could never be wrong. That is the same shape as the
B2 churn inversion — a belief that constitutes the fact it is a belief about —
and it silently flatters any cap-compliance figure derived from it.

WHAT IS THE LAW AND WHAT IS A READING (design question (c), settled here)
-------------------------------------------------------------------------
THE LAW, in the commons artefact, identical for both lanes and single-sourced so
it cannot drift:
  * the cap-window boundaries (six-monthly Apr/Oct to Sep-2022, quarterly after)
  * the published typical-household unit rate per window, per fuel
  * the EPG level per window where the EPG was in force, published SEPARATELY
    rather than pre-combined

A READING, owned independently by each lane and allowed to differ:
  * which of the two published instruments actually binds on a given day
  * what happens past the end of the published schedule
  * which customers the ceiling reaches (segment, contract type)
  * whether a sub-annual window is used at all, or a coarser blend

THIS lane's reading — the world's, i.e. what a customer's bill was actually not
allowed to exceed:
  * the binding ceiling is `min(Ofgem cap, EPG)` where an EPG level is published
    for the window, because a customer could not lawfully be charged above
    either instrument
  * before the first published window there was no cap, so there is no ceiling
  * PAST the last published window the last published level STANDS. The cap is a
    standing statutory instrument: "no level has been published for next quarter
    yet" means the current one still binds, never "the ceiling has lapsed".
    Returning None there would un-cap every domestic customer — fail-open, R15.

WHICH SIDE OF VAT (2026-08-25, and it is a reading too)
--------------------------------------------------------
The published levels are INCLUSIVE of VAT at 5% — domestic fuel and power at the
reduced rate, VATA 1994 Sch 7A Group 1 — and the commons artefact says so in its
own `basis` block. Every rate this codebase settles and bills is EX-VAT: VAT is a
separate line added downstream over commodity + non-commodity + standing charge.
So there are two honest numbers here and no basis-less one, which is R14 (`no
financial figure without its clock`) with VAT in the place of the clock.

That rule is written this way because the alternative was tried and failed
silently for as long as the clamp has existed. `hedged_settlement.run_deemed_term`
clamped an ex-VAT rate against `binding_cap_unit_rate_gbp_per_mwh` — a name that
did not say — and the world therefore enforced a ceiling 5% above the law, always
in the supplier's favour. The basis was in the docstring under an R14 heading the
whole time. Being right in a docstring stopped nothing; the repair is that the
number has no basis-less name left to reach for, checked by AST in
`tests/simulation/test_price_cap_vat_basis.py`.

WHAT IT COST, measured over real GB system sell prices 2019-01-01..2025-12-31 at
the live deemed premium of 0.20 (122,720 half-hours, all of them inside a
published cap window):

    ceiling too high by   7.87–16.19 GBP/MWh on electricity, per window
    clamp bound           7.83% of half-hours before → 8.47% after
    billed above the law  786 half-hours, 276 of them 2021 and 451 in 2022
    overcharge            11.08 GBP/MWh on a binding half-hour; 0.94 across all

Small on average and concentrated exactly where the cap is the only thing between
the book and the law — which is the shape a ceiling error takes, and the reason
an average would have been the wrong number to report.

The company's reading (`company/pricing/ofgem_price_cap.py`) reaches the same
answers TODAY, and that is a fact about the tree rather than a property anything
enforces. Nothing pins the two equal, deliberately: a test asserting they agree
would restore in the suite exactly the coupling this cut removes from the code —
the trap B3's design block recorded and B7 refused for the hedge floor. What IS
proven, by mutation, is that the two can DISAGREE:
`tests/architecture/test_price_cap_commons.py`.

DIVERGENCE CONTROL (design question (b), settled here)
-------------------------------------------------------
Two lanes holding cap tables that drift apart silently would be `one name, two
numbers`, a fidelity defect in both. The control is structural rather than
assertive, and it splits on the law/reading line above:
  * THE LAW CANNOT DRIFT — there is one artefact, and a control fails if either
    lane hand-writes a window schedule of its own instead of loading it.
  * THE READINGS MAY DRIFT — that is the point — and the divergence is
    REPORTED, never gated (R12: a diagnostic is not a target).
    `cap_reading_divergence()` in the test module walks the published span and
    names every date where the two readings differ. It asserts nothing about the
    count; it exists so that a divergence is a visible event.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

# The regulation commons. This lane reads the same published artefact the
# company reads, with its own loader — not the company's, and not a shared
# module (a shared module would have to sit in a package the wall walker does
# not walk; a data file has no import statement to hide a dependency in).
_CAP_WINDOWS_ARTEFACT = (
    Path(__file__).resolve().parents[1]
    / "docs" / "domain_artefact_library" / "regulatory"
    / "ofgem_default_tariff_cap_windows.json"
)


def _load_published_windows() -> list[dict]:
    """Read the published cap windows. Raises rather than failing open (R15)."""
    if not _CAP_WINDOWS_ARTEFACT.exists():
        raise FileNotFoundError(
            f"Ofgem cap-window commons artefact missing: {_CAP_WINDOWS_ARTEFACT}. "
            "The world cannot enforce a ceiling it cannot read, and an unenforced "
            "ceiling is not the same as no ceiling."
        )
    raw = json.loads(_CAP_WINDOWS_ARTEFACT.read_text())
    windows = raw.get("windows")
    if not windows:
        raise ValueError(
            f"Ofgem cap-window commons artefact has no windows: {_CAP_WINDOWS_ARTEFACT}"
        )
    parsed: list[dict] = []
    for w in windows:
        entry = {
            "from": date.fromisoformat(w["from"]),
            "to": date.fromisoformat(w["to"]),
            "elec": float(w["elec"]),
            "gas": float(w["gas"]),
        }
        for epg_key in ("elec_epg", "gas_epg"):
            if epg_key in w:
                entry[epg_key] = float(w[epg_key])
        parsed.append(entry)
    return sorted(parsed, key=lambda w: w["from"])


PUBLISHED_CAP_WINDOWS: list[dict] = _load_published_windows()

_FIRST_CAPPED_DAY = PUBLISHED_CAP_WINDOWS[0]["from"]

_FUEL_KEY = {"electricity": "elec", "gas": "gas"}


#: Domestic supply is VAT-rated at 5% (VATA 1994 Sch 7A Group 1, the reduced
#: rate for domestic fuel and power). The published cap levels are inc-VAT at
#: this rate — the commons artefact says so in its own `basis` block — so this
#: is the factor, and the ONLY factor, that separates the two accessors below.
DOMESTIC_VAT_RATE = 0.05


def binding_cap_unit_rate_gbp_per_mwh_inc_vat(fuel: str, on_date: date) -> float | None:
    """The ceiling a domestic bill could not lawfully exceed on `on_date`,
    ON THE PUBLISHED BASIS: GBP/MWh, INCLUDING VAT at 5%, excluding standing
    charge — the basis declared by the commons artefact, carried forward
    unchanged.

    fuel: 'electricity' or 'gas'. Any other fuel has no domestic cap.
    on_date: the settlement date the ceiling is applied to.

    Returns None only where no cap existed (before the first published window)
    or the fuel is not domestically capped. Never None merely because the
    published schedule has run out — see the module docstring.

    THERE IS NO BASIS-LESS ACCESSOR HERE, AND THAT IS THE POINT (2026-08-25).
    Until today this function was named `binding_cap_unit_rate_gbp_per_mwh` and
    its inc-VAT basis lived only in the docstring. `hedged_settlement` clamped an
    EX-VAT rate against it, so the world enforced a ceiling 5% above the law, in
    the supplier's favour, for as long as the clamp has existed. The docstring
    was right and was read by nobody. A caller now cannot obtain the number
    without writing down which side of VAT it wants, which is the only version of
    this rule that survives the next person in a hurry — R14 (`no financial
    figure without its clock`) applied to VAT instead of to the settlement clock.
    """
    key = _FUEL_KEY.get(fuel)
    if key is None:
        return None
    if on_date < _FIRST_CAPPED_DAY:
        return None

    window = next(
        (w for w in PUBLISHED_CAP_WINDOWS if w["from"] <= on_date <= w["to"]),
        None,
    )
    if window is None:
        # Past the published schedule: the standing instrument still binds.
        window = PUBLISHED_CAP_WINDOWS[-1]

    ofgem = window[key]
    epg = window.get(f"{key}_epg")
    return min(ofgem, epg) if epg is not None else ofgem


def binding_cap_unit_rate_gbp_per_mwh_ex_vat(fuel: str, on_date: date) -> float | None:
    """The same ceiling, restated EXCLUDING VAT, for comparison against an
    ex-VAT unit rate.

    This is the one settlement clamps want, because every rate this codebase
    settles and bills is ex-VAT: VAT is a separate line added downstream over
    (commodity + non-commodity + standing charge). A customer charged this rate
    pays exactly the published inc-VAT ceiling once VAT is applied, which is what
    the ceiling means.

    Returns None on exactly the same inputs as the inc-VAT accessor — the
    de-VATing is arithmetic on a number, never a second reading of the law, so
    there is one place where the schedule is interpreted and this is not it.
    """
    inc_vat = binding_cap_unit_rate_gbp_per_mwh_inc_vat(fuel, on_date)
    if inc_vat is None:
        return None
    return inc_vat / (1.0 + DOMESTIC_VAT_RATE)
