# FRAME — W1_24: the drivers that wait on a population

*DISCOVER/FRAME pass, 2026-09-06. No BUILD code: this atom is epoch-gated
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1) and the ruling registers it as
**decided, not authorised**. Nothing here authorises a pull.*

Source: `docs/staging/DIRECTOR_RULING_WEATHER_CELLS_HEAT_LOAD_SEGMENTATION_PHASE1_2026-09-05.md`
§2 item 3. Sibling: `docs/design/W1_23_WEATHER_PHASE2_FRAME.md`.

---

## 0. What the atom is, in one line

Three weather drivers — relative humidity, wind direction, driving rain — that
are **inert until something else in the world exists to consume them**, held on
the map so that the condition which would wake them is watched by something
rather than remembered by someone.

---

## 1. FINDING 1 — the opening condition is watched by nothing, which is the failure the row was minted to prevent

The ruling's opening condition, verbatim: *"opens when the drawn population's
heat-pump share makes it material, or the fabric layer takes on solid-wall
moisture."*

Two limbs. **Neither is computed anywhere.** No test, no daemon, no gate and no
orientation pass evaluates either one. The row's own registration note says the
failure mode without the row "is not that the work happens too soon; it is that
nobody is watching the condition" — and the row as minted reproduces exactly
that, because a condition in prose in a `map_notes` field is not a watcher.

This is the parked-atom class the ruling itself invokes, one level up: the atom
is no longer parked, but its *trigger* is.

**Limb (a) is measurable today.** `simulation/adoption_geography.py` carries the
national heat-pump curve, and it runs:

| year | heat-pump share of GB homes |
|---|---|
| 2016 | 0.20% |
| 2020 | 0.51% |
| 2022 | 0.81% |
| 2024 | 1.30% |
| 2025 | 1.63% |

*(`national_adoption_share("heat_pump", y)`, printed at real inputs.)*

So limb (a) is a one-line call away from being checkable — but it is not
checkable, because **"material" is not defined**. The ruling names no threshold.
Differencing an undefined concept is this project's most expensive recurring
shape; I am not picking a number to fill the slot. See §4 for what I recommend
instead.

**Limb (b) has no measurable subject at all.** "The fabric layer takes on
solid-wall moisture" describes a capability `simulation/fabric_physics.py` does
not have and no row currently claims. There is no field, flag or module whose
state answers it, so limb (b) cannot be evaluated even in principle until
something mints it.

---

## 2. FINDING 2 — wind direction has no opening limb, and that is a gap in the ruling, not in the row

Line the drivers up against the limbs:

| driver | its stated consumer | which opening limb is that? |
|---|---|---|
| relative humidity | heat-pump defrost regime | **limb (a)** |
| driving rain | solid-wall moisture | **limb (b)** |
| wind direction | "property orientation crossed with cells" | **neither** |

Wind direction's precondition is named in the driver list and appears in no
opening condition. The phase can therefore open on either limb with wind
direction still inert, or wind direction's own precondition can be met while the
phase stays shut. This is a real discontinuity in the ruling and it is the one
thing in this frame I would put in front of the director (§4).

**Limb (a) also has a second gate the ruling does not state.** Humidity matters
only through a defrost regime; heat pump is **out of all three housing phases**
until the director says otherwise (housing ruling §2 item 3). So a material
heat-pump share is necessary and not sufficient — at 5% share with heat pump
still outside the housing phases there is still no defrost regime to consume
humidity. Two gates, one stated.

---

## 3. CORRECTION — the registered note's orientation claim is wrong, and the truth is more useful

The row's `origin_note` says wind direction needs property orientation *"which
the premise draw does not carry at all."* **That is false**, and I am correcting
it beside the claim rather than quietly.

`Household.roof_aspect` exists (`simulation/household.py:117`) and is read in
three places (`premise_trace.py:1089` transposes PV by it, `life_events.py:413`
and `:640`). What is actually true is narrower and more load-bearing:

1. It is a **roof aspect, not a facade bearing.** Wind exposure needs a bearing;
   a roof aspect is not one.
2. It is **not drawn.** `household.py:371–382` is a deterministic lookup from
   `home_type`: `rural_detached`→`south`, `suburban_semi`→`east_west`, flats and
   all commercial→`na`, everything else→`east_west` by default. There is no
   randomness and no anchor behind it.
3. Its vocabulary is `{south, east_west, north, na}` — **no degrees**. And
   `premise_population.py:661` is coarser again: `"na"` if flat, else
   `"east_west"` for every property in the drawn population.
4. `fabric_physics.py:129–140` already registers the matching open simplification
   from the *other* side: solar aperture is orientation-blind, "no such function
   exists anywhere in the tree", and `roof_aspect` "is read by nothing in this
   module".

So the accurate statement is: **orientation exists as a field, is a roof aspect
rather than a bearing, is derived rather than drawn, and is effectively constant
across the drawn population.** Wind direction cannot be crossed with it today —
not because the field is absent, but because it carries no bearing and no
variation. That is a different and smaller piece of work than "the premise draw
does not carry orientation", and it is worth knowing before anyone scopes it.

---

## 4. RECOMMENDATIONS — what I am doing, and the one thing that is the director's

**Mine, done or decided here:** the correction in §3 is landed against the row.
No threshold is invented for "material" (§1). No pull is authorised.

**For the director — the wind-direction discontinuity (§2).** My recommendation,
which I will treat as adopted unless he says otherwise, is that wind direction's
opening limb should read *"or property orientation acquires a bearing and a
distribution"* — i.e. it opens on the same event that would make it consumable,
which is the shape the other two drivers already have. That is a one-line
amendment to the ruling and it makes all three drivers symmetric.

**On "material":** I recommend the threshold be set not as a share but as the
point where **heat pump enters a housing phase at all**, because that is the gate
that actually controls whether a defrost regime exists (§2). A share threshold
alone can be met while the driver stays inert, which is the failure this row
exists to catch. This collapses limb (a)'s two gates into the one that binds.

---

## 5. Level definitions and exit criteria (so `level_target: 3` is checkable)

- **L0 (now).** Decision registered, opening condition in prose, watched by
  nothing.
- **L1.** The opening condition is a **function that runs** — one callable that
  answers, per limb, "is this open?", returning a named `None`/"cannot tell" for
  limb (b) while it has no subject, never a default `False` that reads as a
  settled "no". Exit: a control that asserts the callable can return open **and**
  closed over its partition (one control over the whole partition, not a leg per
  limb — the guard that refuses everything passes a per-leg suite).
- **L2.** Data availability established for all three variables against the
  published CEDA catalogue, with each variable's source named or its absence
  recorded as a finding. Exit: no variable in this atom carries an unattributed
  availability claim.
- **L3.** The drivers are pulled, celled and coverage-curved on the phase-1
  method, *after* an opening limb is met. Exit: as W1_14 — a stated coverage
  figure per driver, not a hope.

---

## 6. PREDICTIONS — filed now, before the answers, so they can refute me

1. **Relative humidity is published by HadUK-Grid and the other two are not.**
   The fetcher knows only `("tas", "sfcWind", "sun")`
   (`tools/fetch_haduk_grid.py:62`), so all three are unestablished here.
2. **Wind direction is not a published grid product in the phase-1 source**, and
   will need a different anchor (ERA5, already in the repo for cross-checks)
   — making it the same *kind* of problem phase 1 hit when it found HadUK
   publishes no irradiance product and sunshine is a duration in hours
   (`tools/weather_cell_drivers.py:25`).
3. **Driving rain is a derived exposure index, not a raw grid** — a third kind of
   problem again, needing a computed standard rather than a pull. I have a
   candidate standard in mind and am deliberately not naming it as established;
   see §7.
4. **Limb (a) will not be met by share growth before it is met by a curriculum
   decision.** At 1.63% and this curve's slope, the housing-phase decision
   arrives first.

If (1) is wrong and HadUK carries all three, this atom is much cheaper than
§5-L2 assumes and I will say so here.

---

## 7. What this pass did NOT establish

- **Whether HadUK-Grid publishes relative humidity, any wind-direction product,
  or a driving-rain index.** Not answered from memory. This is a catalogue check
  against CEDA and it is the first move of L2. An honest gap here is worth more
  than a plausible variable list, because a variable list would be read as
  established.
- **The standard behind a driving-rain index.** There is a British Standard for
  driving-rain exposure; I have not opened it and am not citing a number from it.
- **What "material" means** (§1) — recommended, not decided.
- **Whether the phase-1 cells are even the right cut for these three.** Same
  question W1_23 raises for phase 2, and it cannot be asked before the phase-1
  coverage curve exists.

---

*Frame only. `level_current: 0`, `loop_stage: idle`, unchanged. The row's target
stays 3 and nothing here moves it.*
