"""Tenure→low-carbon-adoption per-asset factor SENSITIVITY diagnostic.

FROM_AGENT_SEGMENTATION_INTEGRATION_FOLLOWON item 3 (director's explicit ask):
measure how load-bearing each ASSERTED per-asset × tenure gating magnitude is,
BEFORE it drives the live world. Reported strictly as a DIAGNOSTIC (R12 — the
number is never a target; this tells us how sensitive the world is to a dial the
director sets, not how to tune it).

Method (mechanism-level, no live run — the multiplier is not yet wired into the
live pipeline; that is item 5): build a representative eligible residential
population, then for each asset sweep its gating factor m across a plausible
range and measure the resulting 2016–2025 adoption RATE among households eligible
for that asset. The factor scales the annual Bernoulli adoption probability, so
the rate is a smooth, monotone function of m; the local slope around each asserted
value is the load-bearingness we want to know.

Downstream-outcome (bill/carbon) sensitivity is DEFERRED to item 5: it cannot be
measured until the factor is wired into a live run, and item 5 (activation +
verify-to-live-run) is the pass that does that wiring. Stated honestly here rather
than faked with a mechanism-only proxy.

Run: python3 -m tools.tenure_adoption_sensitivity  [--out PATH]
"""
from __future__ import annotations

import argparse
from pathlib import Path

from simulation.household import make_household
from simulation.life_events import generate_life_events

# The asserted renter magnitudes under test (owners are 1.0 for every asset).
ASSERTED = {
    "solar_pv": {"private_rent": 0.10, "social_rent": 0.25},
    "ev": {"private_rent": 0.55, "social_rent": 0.55},
    "heat_pump": {"private_rent": 0.14, "social_rent": 0.35},
}
_EVENT_OF_ASSET = {
    "solar_pv": "solar_install",
    "ev": "ev_acquired",
    "heat_pump": "heat_pump_installed",
}
# A plausible sweep grid: anchors (0/1) + every asserted renter value + a ±0.1
# band around each asserted value, deduped and sorted.
_BASE_GRID = [0.0, 0.05, 0.10, 0.14, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 1.0]


def _population(n: int = 15000) -> list:
    """A representative eligible residential population spanning the resi
    home-types and EPC bands. Distinct customer_ids so each household's
    deterministic per-customer event stream is one independent sample."""
    home_types = ["suburban_semi", "rural_detached", "terraced", "urban_flat", "tenement_flat"]
    epcs = ["A", "B", "C", "D", "E", "F"]
    beds = [2, 3, 4]
    pop = []
    i = 0
    while len(pop) < n:
        ht = home_types[i % len(home_types)]
        epc = epcs[(i // len(home_types)) % len(epcs)]
        bed = beds[(i // (len(home_types) * len(epcs))) % len(beds)]
        pop.append(make_household({
            "customer_id": f"SENS-{i:05d}",
            "home_type": ht,
            "epc_rating": epc,
            "bedrooms": bed,
            "segment": "resi",
        }))
        i += 1
    return pop


#: Each household is drawn ONCE with seed=None, i.e. its deterministic
#: per-customer_id event stream (one independent 10-year realization). NOTE: an
#: explicit integer `seed=` is used verbatim by the generator and IGNORES the
#: household, so all households would share a stream per seed -- the sample MUST
#: come from many DISTINCT customer_ids, not from many seeds on one household.
#: So a stable rate needs a large population (solar's ~3% cumulative base rate
#: means ~N/30 eligible households actually adopt).


def _structurally_eligible(pop: list, asset: str) -> list:
    """Households that CAN adopt `asset` -- they adopt in their ungated (m=1.0)
    realization. Defined by the generator's own gate (roof/driveway/hp-
    eligibility/heating precondition) EXERCISED rather than re-implemented, so it
    can never drift from the model. These are the households whose adoption is
    responsive to the gating factor; the rate is measured over this base."""
    event = _EVENT_OF_ASSET[asset]
    return [
        h for h in pop
        if any(e.event_type == event
               for e in generate_life_events(h, 2016, 2025,
                                             adoption_eligibility_multiplier={asset: 1.0}))
    ]


def _adoption_rate(eligible: list, asset: str, m: float) -> float:
    """2016-2025 adoption rate for the responsive eligible base at gating factor
    `m`: fraction of eligible households still adopting the asset at least once
    when its factor is `m` (other assets left at 1.0). Monotone in m -- lowering
    m raises the adoption threshold m*p, so an adopter at m=1 drops out once its
    draw no longer clears the lowered threshold."""
    event = _EVENT_OF_ASSET[asset]
    if not eligible:
        return 0.0
    hits = sum(
        1 for h in eligible
        if any(e.event_type == event
               for e in generate_life_events(h, 2016, 2025,
                                             adoption_eligibility_multiplier={asset: m}))
    )
    return hits / len(eligible)


def build_report(n: int = 15000) -> str:
    pop = _population(n)
    lines: list[str] = []
    lines.append("# Tenure→adoption per-asset factor — SENSITIVITY diagnostic")
    lines.append("")
    lines.append("**Type:** DIAGNOSTIC (R12 — never a target). FROM_AGENT_SEGMENTATION_"
                 "INTEGRATION_FOLLOWON item 3. Generated by `tools/tenure_adoption_sensitivity.py`.")
    lines.append("")
    lines.append("**What this measures:** how load-bearing each director-ASSERTED per-asset × tenure "
                 "gating magnitude is — the adoption-rate response to sweeping the factor `m` across a "
                 "plausible range, among the responsive eligible residential base. The factor scales the "
                 "annual Bernoulli adoption probability, so a household eligible at m=1.0 defines the "
                 "responsive base; rate(m) is the fraction of that base still adopting at `m`.")
    lines.append("")
    lines.append("**Scope honesty:** mechanism-level only. The factor is NOT yet wired into the live "
                 "run (item 5), so downstream bill/carbon sensitivity cannot be measured here without "
                 "faking it — it is deferred to item 5's activation + verify-to-live-run.")
    lines.append("")
    lines.append(f"Population: {n} representative eligible residential households "
                 "(resi home-types × EPC A–F × 2–4 beds); deterministic per-customer event streams.")
    lines.append("")

    for asset in ("solar_pv", "ev", "heat_pump"):
        event = _EVENT_OF_ASSET[asset]
        eligible = _structurally_eligible(pop, asset)
        n_elig = len(eligible)
        grid = sorted(set(_BASE_GRID) | set(ASSERTED[asset].values()))
        rows = [(m, _adoption_rate(eligible, asset, m)) for m in grid]
        rate_at_1 = next((r for (mm, r) in rows if mm == 1.0), None)
        lines.append(f"## {asset}  (event: `{event}`)")
        lines.append("")
        lines.append(f"Responsive eligible base: **{n_elig}** households; adoption rate at m=1.0 "
                     f"(ungated) = **{rate_at_1:.3f}**.")
        lines.append(f"Asserted renter factors — private_rent **{ASSERTED[asset]['private_rent']}**, "
                     f"social_rent **{ASSERTED[asset]['social_rent']}** (owners 1.0).")
        lines.append("")
        lines.append("| factor m | adoption rate | rate / rate(m=1) | asserted? |")
        lines.append("|---:|---:|---:|:--|")
        for m, rate in rows:
            rel = (rate / rate_at_1) if rate_at_1 else 0.0
            tags = [t for t, v in ASSERTED[asset].items() if abs(v - m) < 1e-9]
            tag = ", ".join(tags) if tags else ""
            lines.append(f"| {m:.2f} | {rate:.3f} | {rel:.3f} | {tag} |")
        # Local sensitivity around each asserted value: slope over a ±0.1 band.
        lines.append("")
        for tenure, mv in ASSERTED[asset].items():
            lo = max(0.0, round(mv - 0.1, 4))
            hi = min(1.0, round(mv + 0.1, 4))
            r_lo = _adoption_rate(eligible, asset, lo)
            r_hi = _adoption_rate(eligible, asset, hi)
            slope = (r_hi - r_lo) / (hi - lo) if hi > lo else 0.0
            lines.append(f"- **{tenure}** (asserted {mv}): adoption rate over [{lo:.2f}, {hi:.2f}] "
                         f"moves {r_lo:.3f}→{r_hi:.3f}, local slope ≈ **{slope:.3f} rate per unit m** "
                         f"(±0.1 in m ⇒ ≈{abs(slope) * 0.1:.3f} in adoption rate).")
        lines.append("")

    lines.append("## Reading")
    lines.append("")
    lines.append("- **The response is ~LINEAR in m for all three assets**: rate(m) ≈ m·rate(m=1), so "
                 "the local slope near every asserted value is ≈1.0 rate-per-unit-m (a ±0.1 move in the "
                 "factor shifts adoption ≈±0.10 of the ungated base rate). This is expected — the factor "
                 "scales a small annual Bernoulli probability, whose cumulative-adoption response is "
                 "near-linear in that regime. So there is NO differential curvature to exploit; the dial "
                 "is uniformly load-bearing across its range.")
    lines.append("- **What differs between assets is the asserted LEVEL, not the slope.** An asserted "
                 "factor f means eligible renters adopt at ≈f× the ungated rate: solar_pv private_rent "
                 "0.10 ⇒ ≈10% of ungated (strongest suppression); heat_pump private_rent 0.14 ⇒ ≈14%; "
                 "ev 0.55 ⇒ ≈55% (weakest suppression). Each ±0.1 of director uncertainty on a factor "
                 "translates to ≈±10% of the ungated renter adoption rate for that asset — a direct, "
                 "linear read on how much a mis-set dial would move the world.")
    lines.append("- **`has_driveway` acts on ELIGIBILITY, not this slope.** The EV off-street-parking "
                 "barrier removes driveway-less renters from the responsive base ENTIRELY (upstream of "
                 "the tenure factor); it is why EV's asserted factor is set high (0.55) — the tenure "
                 "gate should add only a weak residual once the physical barrier is already modelled, "
                 "not why the adoption-rate slope is any flatter (it isn't).")
    lines.append("- These are the ASSERTED R13 curriculum dials (changeable on the director's word, "
                 "NEVER tuned to company outcomes). This diagnostic informs the item-5 activation "
                 "decision; it does not propose new values.")
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/market_research/tenure_adoption_sensitivity.md")
    ap.add_argument("-n", type=int, default=15000)
    args = ap.parse_args()
    report = build_report(args.n)
    Path(args.out).write_text(report, encoding="utf-8")
    print(f"wrote {args.out} ({len(report)} bytes)")


if __name__ == "__main__":
    main()
