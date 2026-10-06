**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `supplementary-heater-operating-pattern-discover` (Lane 0 delivery)

# The supplementary heater now runs when HES and EFUS say it does; its power and cycling stay unsourced

## Pre-registration (written before any trace was run)

The change (below) keeps the energy (1,505 kWh/yr × HDD/normal) and only moves WHEN in the day it
falls, and how long the session is. Predictions, on the harness's drawn 60:

1. **L1.2 (day-to-day shape correlation), P0050:** falls from 0.777, by at least 0.1, *if* P0050 is
   drawn as an irregular user (about 70% of owners). If it is drawn regular, it stays above 0.7.
2. **L1.1 (texture), the two owners at 0.1045 and 0.1166:** each moves by **less than 0.01**. L1.1
   is median |step| over the mean. The heater adds a lot of energy to the mean and few steps, and
   moving a flat block in time does not change that. If this holds, the "artefact" label on L1.1
   was partly wrong: a real heater-owner's meter is also calmer on this statistic. Only thermostat
   cycling could add steps, and that is not sourced.
3. The L2 spread cell (1.96) moves by less than 0.05.

## Results

(filled in after the run, below this line; the predictions above are not edited)

All three predictions held.

| | Before (flat block) | After | Prediction |
|---|---|---|---|
| L1.2 worst home | P0050 0.777 | P0023 0.578; P0050 below it | P0050 falls ≥0.1 if irregular: **held** (drawn irregular) |
| L1.1, P0023 (set-time) | 0.1045 | 0.1056 | moves <0.01: **held** |
| L1.1, P0050 (irregular) | 0.1166 | 0.1197 | moves <0.01: **held** |
| L1.1 counts under real p10/p25/p50/p75 | 0, 2, 4, 31 | 0, 1, 4, 31 | |
| L2.4 spread | 1.96 | 2.007 | moves <0.05: **held** (barely) |

P0050 crossing the real p25 line (0.117) is a 0.003 move. It is not progress.

## What was sourced, and what was not

Read at source, 2026-10-06:

- **When:** HES (Intertek R66141), Appendix IX, p.560, "Heater (individual)". It covers 46 monitored
  heaters and gives daily average load curves for workdays and holidays. The workday curve is about
  69% between 18:00 and 23:59, with its peak at 21:00 and a blip at 08:00. The holiday curve has a
  second peak at 09:00–12:00. Only the shape is used, read by eye to about ±100 W on each bar. The
  46 heaters are in homes of every main fuel. §15.3's Figures 544–545 are NOT this: they cover all
  heating, storage heaters included.
- **How long:** EFUS 2017 §3.6. Daily users run the heater for a median of 4 h on a weekday (IQR
  2.5–6) and 5 h at the weekend (IQR 4–8). The tails are not published, so draws are held at the
  quartiles.
- **Set times or not:** EFUS 2011 Report 5 §3.3.3. Of weekly users, 28% run the heater at set times
  and 65% do not; 7% mix the two and are drawn as irregular. Of set-time users, 30% change their
  times at weekends. Report 5's start-time categories for set-time users (weekday: wake-up 20%,
  daytime 14%, home-time 56%, evening 33%) agree in direction with HES. They are not used, because
  HES's hourly curve is finer.
- **Placement:** HES gives when the energy falls, not when sessions start. Start weights are
  therefore recovered by Richardson–Lucy deconvolution of HES's curve with EFUS's lengths. Across
  many days, the model's hourly share stays within 2.4 points of HES on workdays and 3.9 points on
  holidays. The remaining gap is HES's one-hour features, which a session of at least 2.5 h cannot
  draw.
- **NOT sourced, and so not modelled:** the heater's power when on and its thermostat cycling. Each
  session spreads the day's HDD-scaled energy evenly. On a 0 °C day that is **3.3 kW for 4 h**
  (normal year 1,785 HDD at C1), which is above a typical 2–3 kW nameplate. HES's energy and
  EFUS's hours are in tension at the cold end. HES's 1,505 kWh/yr may cover more than one heater
  per home, or a heater used for longer than EFUS's daily-user median. Which of the two applies is
  not established, and nothing here clips the power, because no on-power was read to clip it to. Cycling is the one thing
  that could still move L1.1, and only measured heater-level data at a resolution under 30 minutes
  could source it. HES's 2-minute appliance data would be the source; it was not read here.

## What this changes in the harness's reading

The L1.1 "artefact" label was partly wrong. Sourcing the timing moved the two owners by 0.001 and
0.003. Their calm on L1.1 is the heater's energy raising each home's mean. That is a real load, and
a real heater owner's meter would read calmer on this statistic too. Cycling is what is left to
source. The L1.2 artefact was real, and it is closed for irregular users. A set-time home now
repeats its session, as EFUS says such a household does.
