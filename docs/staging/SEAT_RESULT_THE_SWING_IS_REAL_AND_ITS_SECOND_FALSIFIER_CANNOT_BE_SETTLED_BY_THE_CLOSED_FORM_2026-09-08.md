**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`
· **Class:** measurements_that_mirror

**Knowledge:** `how-many-synthetic-households` — landed at `3745b9c0d`. This is the result of the
pre-registration that page's second named limit points at; the page is not amended yet, because
falsifier 2 is unresolved and half a result is not a publication.

# The seasonal swing is real and independent; its second falsifier cannot be settled by the closed form

**Result of `SEAT_PREREG_A_REAL_SEASONAL_SWING_IS_COMPUTABLE_FROM_DATA_ALREADY_ON_DISK_2026-09-08`
(`0b34576c4`), measured within hours of filing it.** One of the three predictions holds, one is
unanswerable for a reason the pre-registration did not anticipate, and the third was not reached.

---

## Falsifier 1 — HELD, decisively

**A real swing is computable from data already on disk, and it is not another copy of the level.**

| axis | \|r\| with `weather_sensitivity` | \|r\| with headcount |
|---|---:|---:|
| the invented `seasonal_swing` | **1.0000** | 0.0005 |
| computed, set-point 20 °C | **0.3792** | 0.1508 |
| computed, base 15.5 °C | **0.1797** | 0.2157 |

Predicted below 0.85, and it comes in between 0.18 and 0.38 depending on the variant. Against an
exact duplicate, either is a genuine axis. **The prediction that cell geography alone would not be
enough also held**: the cell-only cold-half share correlates −0.9217 with annual degree-days, and
what breaks that is the per-household gains — solar aperture and internal gain, which vary
p10-to-p90 by 1.96–7.51 m² and 0.136–0.520 kW.

**And a method result worth more than the number.** The first run of this probe split an annual
gains total using a MEDIAN household rather than each household's own. Falsifier 2 came out at
**0.081 — a clear FAIL**. With the real per-household gains it came out at **0.216 — a PASS**.
The approximation destroyed the exact signal it was there to measure, and it looked entirely
reasonable. A convenience in a probe is a finding about the probe.

## Falsifier 2 — UNANSWERABLE, and that is the finding

It passes at 0.216 and fails at 0.151 depending on which variant is used, and **the two variants
differ only in a choice the closed form cannot make correctly.** The occupancy signal enters through
the hot-water share of the annual total, and that share is 15.9% in one variant and 8.7% in the
other, because the annual LEVEL is wrong in both:

| model | median modelled gas | ÷ observed NEED annual gas |
|---|---:|---:|
| observed (NEED meters, same households) | 10,100 | — |
| **current: 1 Oct – 31 Mar, 20 °C** | 9,948 | **0.985** |
| full year, base 15.5 °C | 7,404 | 0.733 |
| full year, set-point 20 °C | 13,567 | 1.343 |

**The current model's agreement with the meters depends on the truncation, not on the physics.**
Running the same closed form over the whole year — the more complete thing to do — makes it
34% too high; correcting that with a heating base temperature instead of the set-point makes it 27%
too low, because a low base temperature *is* the shorthand for "set-point minus what the gains
cover", so doing both counts the gains twice. That was my own first error here and it is why the
0.733 row exists.

There is no third choice available to a monthly closed form. The balance point is a household
property that moves through the year, and reproducing it needs the sub-daily model.

## What this does to the pre-registration's claim

The pre-registration said: *"the invented axis can be replaced with a measured one first, cheaply,
and the two are not the same piece of work."* **That is half right and the half that is wrong
matters more.**

The axis IS computable and IS independent — falsifier 1 settles that. But an axis is a ratio of
a numerator and denominator that the closed form cannot both get right over a full year, so
**shipping it now would replace an invented constant with a real quantity computed on a 1.34× level.**
That trades a visible fabrication for an invisible one, which is worse: nobody re-checks a number
that looks derived.

**So the axis is NOT wired, and falsifier 3 — does N rise — is not run.** Running the ladder
on a level known to be a third out would produce a figure whose movement could not be attributed,
which is the error this session has now corrected three times.

## What IS landed from this work

The enabling data path, because it is additive, correct, and the reason the fabrication survived:

* `weather_cell_drivers.drivers()` returns **`monthly_temp`** and **`monthly_sun`** — the full
  (12, 245,077) normals. The loader read that array and returned only an annual mean and a winter
  mean, so for a year nothing downstream could tell January from July. **That is why the swing was
  invented: the quantity was computable and there was no accessor for it.**
* `demand_case_coverage.demand_grid()` carries `cell_monthly_temp` and `cell_monthly_sun` in the
  same cell order as every other array it builds.
* `demand_vector_coverage.generated_population()` returns `solar_aperture_m2` and
  `internal_gain_kw` per household, which is what made the median-household error above visible.

## What is next, in order

1. **The `simulate_premise` build**, now with a sharper reason than the use case alone: it is the
   only thing that can produce a full-year level the swing can be a ratio of. The constraint named
   in the pre-registration still stands — only four locations have a daily archive, covering
   2.0% of GB households on all three drivers, so this is executable for the book's households and
   not across the coverage instrument's 194,865 cells without synthesising weather that does not
   exist. **That remains a fidelity decision for the director.**
2. **Then falsifiers 2 and 3**, in that order, on a level that has been validated against the
   meters over a full year rather than a window.
3. The knowledge page's "second limit" paragraph is **correct as published** and stays as it is:
   the vector still declares seven axes and carries five.
