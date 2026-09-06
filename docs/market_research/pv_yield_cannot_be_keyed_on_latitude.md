**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_28_pv_yield_by_cell_not_by_latitude

**Knowledge:** none -- the weather-cells knowledge page is deliverable 1 of the weather ruling and is
not yet written. The published anchor this table stands on (MCS 2025 fleet average) is cited beside
the constant in `company/regulatory/seg_export_estimator.py`.

# PV yield cannot be keyed on latitude, and the company had one number for the whole country

**Landed 2026-09-06**, delivery seat, `W1_28`. Second of the two repairs `W1_27`'s decision named.

`company/regulatory/seg_export_estimator.py` applied **850 kWh/kWp to every household in the book** —
Penzance and Thurso at the same rate. `W1_25` measured what that carries: a **3.4% RMS error** in
annual generation across the household-weighted population, which is the same order as the SEG rate
spread the figure is used to value. Five bands take it to **0.95%**.

---

## The finding: the bands are not latitude bands

The obvious implementation is a latitude lookup — a supplier knows the address, sunshine runs
north–south, done. It does not work, and the numbers say why. Clustering the 121,668 occupied cells
on annual sunshine, household-weighted, and then reading each band's latitude range:

| band | latitude range of its cells | mean latitude | yield |
|---|---|---:|---:|
| sunniest | **49.89 – 54.12 °N** | 51.02 | 947 kWh/kWp |
| | 49.98 – 56.32 | 51.56 | 909 |
| middle | 50.08 – 57.24 | 52.25 | 888 |
| | 50.42 – 57.85 | 53.45 | 866 |
| dullest | **50.55 – 60.80 °N** | 54.63 | 835 |

**The sunniest and dullest bands overlap across four degrees of latitude.** Britain's sunshine is
coastal and eastern as much as it is southern: the Norfolk and Lincolnshire coasts sit in the
sunniest band at 52–53 °N while inland Devon at 50.6 °N sits in the dullest. A latitude lookup would
look entirely reasonable, would be right on the mean, and would be wrong for most of the country.

**So the lookup is keyed on the quantity that actually governs** — the cell's annual sunshine
duration, which the Met Office publishes on a 1 km grid and a supplier can read for any postcode.
That is the same "climate classes, not contiguous regions" property the cells have everywhere else.

## The table, and which half of it is published

| band | annual sunshine | yield | share of GB households |
|---|---|---:|---:|
| 0 | under 1400.6 h | 834.8 kWh/kWp | 16.2% |
| 1 | 1400.6 – 1512.6 | 865.8 | 24.7% |
| 2 | 1512.6 – 1603.2 | 887.9 | 29.8% |
| 3 | 1603.2 – 1727.2 | 908.7 | 23.9% |
| 4 | over 1727.2 | 946.6 | 5.4% |

**The shape is derived and the level is published, and they are different kinds of thing.** Shape:
household-weighted clustering of HadUK-Grid annual sunshine, converted to irradiation by
Ångström–Prescott (`H/H₀ = a + b·n/N`, Prescott's a = 0.25, b = 0.50) — the method the UK's own
gridded solar resource is built from. Level: scaled so the household-weighted mean is the **MCS 2025
fleet average of 882 kWh/kWp**.

That anchor also replaces the old 850, which cited *"BEIS Solar PV Deployment Statistics, SAP 10.2
Table H1"* for a figure neither source states. The identity is checkable and is a control: weight the
five band yields by their household shares and the answer must be 882.

> **The published 750–1,050 kWh/kWp range is NOT a check on this table, and the obvious comparison
> does not hold.** That range is quoted for optimally tilted south-facing installations at the
> geographic extremes; the MCS fleet average is over all orientations and tilts. Two different
> populations. The derived 835–947 spread being narrower says nothing about either, and reading it
> as corroboration or as refutation would both be wrong.

## What changed in the code

- `yield_kwh_per_kwp(annual_sunshine_hours)` has **no default**. Passing `None` is how a caller
  chooses the national figure, and it is a visible act — the defect being closed was a national
  figure nobody had to ask for.
- `annual_yield_kwh` keeps a `None` default so every existing caller works unchanged. That is the
  one concession to compatibility, and it is why the function beneath it refuses to hide the same
  choice.
- A non-positive sunshine duration is refused rather than banded: zero hours is a broken lookup, not
  the dullest place in Britain.

Six controls, six mutation kills: defaulting the location back in, an off-by-one on a band boundary,
the anchor drifting off its source, the bands flattened to immateriality, a zero duration banded,
and the estimator ignoring the location it was given.

**Nothing pinned the old constant.** All 21 existing tests passed with 850 replaced by 882 — a 3.8%
move in a figure that multiplies every SEG payment in the book, and the suite was indifferent. The
level identity above is the control that was missing.

## Limits

- **The band boundaries are cut points between cluster edges**, so a cell exactly at a boundary is
  assigned by an arbitrary tie-break. At 0.95% RMS the effect is immaterial, but the boundaries are
  not physical.
- **Orientation and tilt are not in this table at all.** They are the largest single determinant of a
  real installation's yield and the fleet average absorbs them. A supplier that knew a customer's
  roof aspect could do better, and `Household.roof_aspect` exists — unused here.
- **No shading, no degradation, no inverter curve.** Same absorption argument: the anchor is a fleet
  average of installations that have all of those.
- **Five bands is `W1_27`'s decision, not an optimum.** Three bands give 1.52% and one gives 3.42%;
  nothing establishes where the marginal band stops paying against the SEG rates it multiplies.
