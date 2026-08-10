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


def binding_cap_unit_rate_gbp_per_mwh(fuel: str, on_date: date) -> float | None:
    """The ceiling a domestic bill could not lawfully exceed on `on_date`.

    fuel: 'electricity' or 'gas'. Any other fuel has no domestic cap.
    on_date: the settlement date the ceiling is applied to.

    Returns None only where no cap existed (before the first published window)
    or the fuel is not domestically capped. Never None merely because the
    published schedule has run out — see the module docstring.

    Basis (R14): GBP/MWh, including VAT at 5%, excluding standing charge — the
    basis declared by the commons artefact, carried forward unchanged.
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
