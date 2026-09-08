**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
W2_19_who_lives_where_money_and_composition

**Knowledge:** none -- this is the evidence and design brief that precedes a knowledge page; the page
it feeds is `how-many-synthetic-households`, which is written and blocked on the site lane. Declared
`none` rather than naming a topic no committed tree carries.

# Gas demand: what drives it, what we have, and the term the model is missing

**Researched and measured 2026-09-08**, delivery seat, on the director's brief: published evidence
first, then discovery against what we have, then a recommendation. **Nothing is built.**

---

## 1. The published evidence

### Setpoint — anchored, and the code's number is not

| quantity | published | source |
|---|---|---|
| thermostat set-point, median | **20°C** | EFUS 2017, n=1,008 centrally heated with a thermostat |
| interquartile range | **19–21°C** | same (EFUS 2011: 18–21°C) |
| reported range | 10–35°C | same |
| mean living-room temperature, heating season | **19.3°C** | EFUS 2017 measured, Oct–Apr |
| mean hallway / bedroom | 18.8°C / 18.9°C | same |

**The set-point and the achieved temperature are different quantities and both matter.** Households
*set* 20°C and their living rooms *sit* at 19.3°C on average across the heating season.

### Internal temperature runs OPPOSITE to fabric quality — the finding that matters most

| cut | mean living-room temperature |
|---|---|
| pre-1919 dwellings | **17.7°C** |
| post-1990 dwellings | **19.1°C** |
| EPC F/G | **17.2°C** |
| EPC A–C / D | 18.6–19.3°C |
| no insulation measures | 17.5°C |
| two or more insulation measures | 18.8–19.0°C |
| houses / flats | 18.5°C / 19.5°C |
| household with a pensioner | higher; HRP 75+ living room 19.8°C |

**Worse-insulated homes are colder, not merely more expensive.** The spread is about **2°C** and it
runs against the fabric effect, partially cancelling it.

**This is decision-relevant for the mission, not a curiosity.** Our model gives every household the
same set-point, so it heats a leaky pre-1919 home to the same temperature as a new-build. Reality
says that home sits 1.4–2.1°C colder. **So the model overstates demand — and therefore overstates
the insulation saving — in exactly the homes a supplier would target for insulation.** A ranking of
interventions built on it is biased toward the measures we would most want to recommend.

### Gas by EPC — a direct validation anchor we are not yet using

| EPC | median annual gas |
|---|---|
| A–C | **9,600 kWh** |
| D | **13,000 kWh** |
| E | **14,500 kWh** |

(EFUS 2017, gas meter-point data.) This is the observed relationship the model should reproduce and
currently is not checked against.

### Schedule and duration — anchored, and richer than the code assumes

| quantity | published |
|---|---|
| households heating **twice** a day | **8.9 million** |
| households heating **once** a day | **3.5 million** |
| twice-a-day pattern | 89% have a wake-up period **under 4h (median 2h)**, then home-time **4–10h (median 5h)** |
| once-a-day pattern | 39% wake-up for 11–16h; 19% evening for ≥17h; 17% home-time 4–10h |
| median weekday heating hours — someone in all day | **8h30** |
| — variable daytime occupancy | **7h00** |
| — out all day | **6h00** |
| weekend, all occupancy groups | 8h00, no significant difference |
| heat twice a day — out all day / variable / in all day | **77% / 60% / 48%** |

**Presence drives schedule, measured.** This is the join between the people layer and the gas
physics, and it is published at exactly the grain we need.

### Controls and end-use split

Programmers 95%, boiler thermostats 89%, TRVs 89%, room thermostats 88% (EFUS 2017). Domestic gas
end use is roughly **75% space heating** (DESNZ 2024), with hot water 12–25% and cooking 5–10%
depending on source and boiler type — for combi boilers specifically, one 2018–2024 daily-data study
puts space heating at 88% and hot water 12%.

**The director's separation test is sound and the spread in that last row is why it is worth doing:**
published shares disagree by a factor of two, and summer gas measures the base directly.

---

## 2. Discovery: what we actually have

**The mechanism he suspected is real, and it is worse than he described.**

### The model has one free parameter per household

Correlation of each demand-vector axis with annual gas, over 12,000 generated households:

| axis | r with annual gas |
|---|---:|
| seasonal swing | **+0.9879** |
| weather sensitivity | **+0.9879** |
| turn-down ceiling | **+0.9879** |
| insulation ceiling | **+0.9735** |
| annual electricity | +0.1396 |
| peak-window share | −0.0108 |

**Three axes agree to four decimal places — the same signature he spotted in the half-hourly shape.**
They are all `heat-loss coefficient × (a function of the weather cell)`, so they are deterministic
monotone transforms of one another. **Seven axes, three of them independent.**

The reason is structural: space-heat demand in our closed form is
`HLC × degree-days × hours − gains`, and the only household-specific term is `HLC`. Fabric gives the
coefficient, weather gives the outside, and **nothing gives the inside** — exactly as he said.

### The world already has the missing term; the measurement discards it

- `fabric_physics.heating_schedule_for` draws a **per-premise set-point** (mean 20.5°C, sd 1.2,
  clipped 17–24), a **setback offset** (2.5–6.0°C), a **two-period schedule** (06:30–08:30 and
  16:00–22:00, jittered ±90 min), a deadband, and a `continuous` flag for weather-compensated
  systems.
- `fabric_physics.simulate_premise` runs a **half-hourly 2R2C thermal model** with chained mass
  state and returns `indoor_air_c`, `fuel_kwh` and `duty_cycle_fraction` per day.
- **`demand_vector_coverage` uses neither.** It calls a closed-form degree-day proxy with
  `SETPOINT_C = 20.0` fixed for every household in the country.

So the sample cannot tell apart two houses at different set-points **because the measurement holds
the set-point constant**, not because the world lacks it.

### The set-point constants are unanchored and biased upward

`_SETPOINT_MEAN_C = 20.5` carries a bare ``domain-knowledge`` comment reading *"BEIS/EST measured
living-room setpoint distribution"* — no document, no table, no date. Against EFUS: the median is
**20.0**, not 20.5, and an IQR of 19–21 implies sd ≈ **1.48**, not 1.2. Both errors push demand up.

### The daily-average model cannot represent intermittent heating

He is right that this is physics, not price. Mean internal temperature over a day depends on **when**
the heating ran, because the mass node charges and discharges; a daily-average degree-day model has
no representation of that. Two homes at 21°C — one constant, one for eight hours — have different
daily totals **and our closed form gives them the same one**.

### And the half-hourly electricity shape, re-checked as he asked

Confirmed and already landed: `family` and `single` occupancy multipliers are **(1.1, 0.85, 1.4)**
and **(1.0, 0.75, 1.25)**, whose ratios are 1.10 / 1.133 / 1.12 — a spread of 0.033. Nearly
proportional, and a share is scale-invariant, so the curves are the same shape at different levels
(max normalised difference **0.0005**). Only `elderly` reshapes (ratio spread 0.72). There is no
after-school band; `children_count` is documented as not moving the shape.

---

## 3. What we cannot capture, against his candidate list

| candidate | status |
|---|---|
| **set-point** | present in the world, **discarded by the measurement**, constants unanchored |
| **schedule, timed vs constant** | present (two-period + `continuous`), **not varied by presence**, not in the vector |
| **flow temperature / radiator ΔT** | **absent entirely.** No flow-temperature term exists |
| **TRV behaviour** | absent; whole-dwelling single-zone model, no per-room control |
| **combi vs cylinder** | `HeatingSystem` distinguishes them; **no hot-water store, no standing loss** |
| **does the boiler condense in practice** | absent — efficiency is not flow-temperature dependent |
| **cooking source** | absent from the gas model |

**Flow temperature is the largest single omission relative to the mission.** He is right that it
matters twice: a condensing boiler run at 80°C flow rather than ~55°C loses roughly 6–10% of its
efficiency, and it is the cheapest intervention a supplier can recommend — no capital, no
disruption. **We cannot currently model the one recommendation with the best cost-to-benefit ratio
in the whole intervention set.**

---

## 4. Recommendation — the shape, not the build

### The core change: stop proxying, use the model we already have

Replace the degree-day closed form in the demand vector with `simulate_premise`, and give every
household a **drawn set-point and a presence-driven schedule**.

**Why this is smaller than it sounds:** the half-hourly thermal model, the schedule object, the
set-point draw and the chained mass state all exist and are tested. The work is wiring and
calibration, not physics.

### Half-hourly for gas, as he ruled

Agreed, and the discovery supports the reason he gave. `simulate_premise` is already sub-daily, so
this is not a resolution *increase* — it is using the resolution we already compute and currently
throw away by summing to a daily total.

### What it costs — measured, not estimated

**0.50 seconds per premise-year** (31 days in 42 ms, single-threaded).

| what | households | cost |
|---|---:|---|
| a drawn sample of ~3,000 | 3,000 | **25 minutes** |
| the 40,000-point reference | 40,000 | 5.6 hours |
| the 120,000-point reference | 120,000 | 16.7 hours |

**The sample is cheap and the reference is not.** The reference is built once and cached, and it does
not need re-running per ladder step — so the honest plan is: full model for the reference, built
once overnight; full model for every drawn sample. The closed form can be retired rather than kept
as a fast path, which removes a whole class of "two models disagree" defects.

### The three anchors to wire, in order

1. **Set-point** — median 20.0°C, IQR 19–21 (sd ≈ 1.48), replacing the unanchored 20.5/1.2.
2. **Set-point conditioned on fabric** — the 17.2–19.3°C spread by EPC. This is the one that changes
   answers, because it *cancels part of the fabric effect* and corrects an insulation ceiling that is
   currently overstated where it matters most.
3. **Schedule conditioned on presence** — 8h30 / 7h00 / 6h00 median hours and 48% / 60% / 77% twice-
   a-day, joined to the people layer's daytime-occupancy rate, which already exists and is
   EFUS-anchored.

### What it does to the number, predicted before building

**N should rise, and for the first time for a reason that is not a stratum.** Set-point and schedule
are the first household properties that are *independent of fabric and weather* — they break the
collinearity that currently leaves seven axes carrying three axes' worth of information. My estimate
is a **2–4× rise** from breaking the r ≈ 0.99 degeneracy, on top of the ~3,000 already measured. That
is a guess about a mechanism I have just measured, and it is written here so it can be wrong.

### What it does to the use case, which is the point

*A customer who wants to budget needs to see the daily cost effect of changing their thermostat or
their timer.* Today the model cannot answer that question at all: turn-down is a fixed 1°C applied
identically to everyone, and the timer does not exist as an input. After the change the answer is a
direct simulation output — re-run `simulate_premise` with the changed set-point or schedule and
difference the fuel. **That is the acceptance test for this work, and it is better than any coverage
number: the model must respond correctly to a thermostat change, not merely reproduce a total.**

### One thing I recommend against

**Do not hand-set the missing flow-temperature or TRV terms to make the model look complete.** They
need a source — the published flow-temperature trial results the housing ruling already names — and
inventing them would put a fabricated efficiency curve underneath the cheapest recommendation we
would make to a real customer.

### The separation test he proposed, and how to run it

Summer gas should be hot water plus cooking, largely occupancy-driven and roughly flat. **We cannot
run it on our own data today** — NEED gives annual totals only, so there is no summer/winter split
per household. It becomes available the moment the model produces half-hourly gas, at which point it
is a *validation* rather than a discovery: the modelled summer base must match the published 12–25%
hot-water share, and the disagreement between published sources is wide enough that our own number
would be a contribution rather than a check.


---

## REFUTED 2026-09-08, the same week — the prediction in section 4 was wrong

Section 4 says: *"N should rise, and for the first time for a reason that is not a stratum...
My estimate is a **2–4× rise** from breaking the r ≈ 0.99 degeneracy."* It is kept above rather
than revised, because a wrong prediction next to its result is the only evidence the experiment was
designed before the answer was known.

The occupancy-driven half of that build has landed and been measured one variable at a time, on two
reference populations:

| reference | sample as a share of it | hot water and occupancy OFF | ON |
|---:|---:|---:|---:|
| 20,000 | 34% | 6,813 | 6,816 |
| 120,000 | 7.4% | 8,820 | 8,822 |

**Two households in 8,822.** Not a small effect — a wrong mechanism.

**What the prediction got wrong** is worth more than the number. "Independent of fabric and weather"
was TRUE of occupancy and IRRELEVANT, because the acceptance test does not score fabric and weather;
it scores seven output quantities, and occupancy is not one of them. A stratum multiplies N because
coverage is owed within it; an axis raises N because a dimension is added; **a DRIVER does neither**
— it moves households around inside a shape already being reproduced.

**Set-point and schedule are not yet tested and the prediction is NOT transferred to them.** They
have the same problem: unless they change a quantity the sample is scored on, they will move the
count by nothing either. On today's evidence the honest expectation for the rest of section 4's
build is **no rise in N and a real gain in fidelity** — which is what the hot-water term
delivered (0.883× → 0.992× against metered gas). Full account:
`adding_a_driver_is_not_adding_an_axis.md`.
