# FRAME — W2_24: houses change on their own timeline

*DISCOVER/FRAME pass, 2026-09-06. No BUILD code: this atom is epoch-gated
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1) and the ruling registers it as
**decided, not authorised**. Nothing here authorises a build.*

Source: `docs/staging/DIRECTOR_RULING_HOUSING_VALUE_CEILING_AND_SAMPLE_PHASE1_2026-09-05.md`
§2 item 1. Siblings: `docs/design/W2_23_HOUSING_PHASE2_FRAME.md` (the observation
layer this phase is supposed to make fall behind),
`docs/design/W2_26_PEOPLE_PHASE3_FRAME.md` (the people-side twin),
`docs/design/W1_24_WEATHER_PHASE3_FRAME.md`.

---

## 0. What the atom is, in one line

The unprompted change axis of the house — boilers dying, PV and EV arriving,
extensions, the physics moving and the EPC falling behind — of which **the
physics half is built and working, the EPC half is already happening and nobody
is measuring it, one element has no route at all, and the element the row is
named after is unreachable for 78% of the population it describes.**

---

## 1. FINDING 1 — the boiler branch cannot be taken by 78% of gas-heated households, and the director's own heat-pump dial does not restore it

The row's `real_world_twin` is *"the boiler that died in February and was replaced
by whoever could come on Tuesday."* Measured on the real draw
(`draw_premise_population(3000, base_seed=42, as_of=2016-01-01)`, events over
2016–2025):

| population | n | `boiler_replaced` over 10y | per household |
|---|---|---|---|
| gas-heated, **heat-pump eligible** | 2,136 (78.3% of gas) | **0** | 0.0000 |
| gas-heated, heat-pump **ineligible** | 591 | 214 | 0.362 |

Gas-heated is 90.9% of the drawn population, so this is **71% of all households
whose boiler can never be replaced.**

The cause is one keyword. `simulation/life_events.py:455` ff.:

```python
if (household.hp_eligible
        and heating in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM)):
    ...                                   # heat-pump draw, prob 0.001–0.006/yr
elif heating in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM):
    ...                                   # boiler replacement, prob 0.09/0.04/0.01 by age
```

The `elif` is gated on the **eligibility condition**, not on whether the
heat-pump draw fired. `hp_eligible` is `residential and not a flat and bedrooms
>= 2` (`simulation/household.py:146`) — the overwhelming majority. So for those
households the first arm is entered every year, at a probability between 0.1% and
0.6%, and the 9%/4%/1% boiler branch is never evaluated at all.

**And the exclusion dial cannot fix it**, which is the part that matters for
sequencing. `adoption_eligibility_multiplier` is the existing, director-facing
lever for turning low-carbon adoption down, including to zero. Run over 1,068
eligible gas households (`base_seed=7`):

| multiplier | heat pumps | boiler replacements |
|---|---|---|
| 1.0 | 41 | **0** |
| 0.17 | 4 | **0** |
| 0.0 | 0 | **0** |

Turning the heat pump *completely off* leaves the boiler branch just as dead,
because the suppression is structural rather than probabilistic. Anyone applying
the standing exclusion by setting this dial to zero — the obvious move — would
get a world with no heat pumps *and* no boiler replacements, and nothing would
say so.

**Why no control caught it.** `tests/simulation/test_phase_b_life_events.py`
tests `apply_events` with hand-built `boiler_replaced` events (`:263`), which
proves the applier and says nothing about the emitter.
`test_multiplier_leaves_non_adoption_events_untouched` (`:858`) uses a
semi-detached — i.e. an eligible household — and asserts the non-adoption events
are byte-identical across multipliers; for that household the boiler-replacement
list is empty on both sides, so the assertion holds vacuously over the very
event it names in its own comment. This is CLAUDE.md's rule exactly: *when a
branch exists to be taken rarely, assert it CAN be taken before asserting what it
does.*

**The size of what is lost.** `boiler_age` is not decorative — it sets combustion
efficiency in `fabric_physics._fuel_for` via `_BOILER_EFFICIENCY`: OLD 0.80, MID
0.86, NEW 0.90. An OLD→NEW replacement cuts gas for space heat and hot water by
`1 − 0.80/0.90` = **11.1%**, permanently, with no company involvement. That is
precisely the counterfactual the atom's `gain` says makes *"we saved them money"*
falsifiable, and 71% of households cannot experience it.

---

## 2. FINDING 2 — the EPC is already falling behind, on the wrong side of the wall, and nothing measures it

The ruling scopes *"the physics and ceiling updating, the EPC falling behind"* as
work to build. Half of it is built and the other half is already happening by
accident.

**The physics half is genuinely built.** `fabric_physics.fabric_parameters`
derives U-values, infiltration and capacities from `household.insulation` and
`household.build_era` (`:630` ff.), and
`fabric_demand_path.household_segments` segments the demand path by household
state *at date* (`:173–191`), fed from `life_events.household_at_date` through
`household_demand.py:96`. So when `insulation_upgraded` fires, the heat-loss
coefficient really does move, mid-run, on the correct date. Nothing to build.

**The EPC half is already diverging.** `Household` carries **both**
`epc_rating` (a letter) and `insulation` (a level). At the draw they agree by
construction — `premise_population._draw_premise:640-643` picks the band from the
fitted joint and sets `insulation = _EPC_TO_INSULATION[letter]`. `apply_events`
rebuilds the household from a state dict that mutates `insulation` and **never
writes `epc_rating`**. Measured over the same 3,000-household draw:

| as of | households whose `insulation` disagrees with their own `epc_rating`'s implied level |
|---|---|
| 2016 (draw) | **0** (0.0%) |
| 2025 (after events) | **318** (10.6%) |

The divergence is entirely event-driven, and it is exactly "the EPC falling
behind". **It is already the world's behaviour and no code reads it.**

Three consequences, and the second is the one that changes the phase:

1. **Do not build a mechanism for this. Build a measurement of it.** The stale
   certificate exists; what is missing is anyone asking how stale.
2. **Both fields sit on `Household`, which is SIM ground truth.** A stale EPC is
   only interesting as something *the company* believes and the world has moved
   past. Today the staleness lives entirely inside the world, where no one can be
   misled by it. Making it a real observation gap is W2_23's job (its Finding 1
   already names two disagreeing company-side EPC copies), not this phase's — so
   **this phase's EPC element is downstream of W2_23's convergence, not parallel
   to it.** The row's `depends_on` already lists W2_23; the reason is stronger
   than the row states.
3. `premise_population.DrawnPremise` carries `epc_lodged`, a real lodgement date
   with a published-shaped age distribution, and it has exactly **one**
   non-test consumer in the tree (`tools/couple_fabric.py:401`). The clock the
   staleness measurement needs already exists and is nearly unused.

---

## 3. FINDING 3 — extensions have no route, and it is structural

`floor_area_m2` (`fabric_physics.py:619`) is `base[property_type] +
per_bedroom × (bedrooms − 2)`. Floor area is therefore a pure function of
`property_type` and `bedrooms`, and **no event in `EventType` writes either
field.** `apply_events` builds its state dict from the household's fields and the
twelve event branches touch solar, battery, EV, heating system, boiler age,
insulation, smart meter and income stress — nothing dimensional.

So "extensions" is not an extension of the existing stream. It needs a new
mutable dimension on `Household`, an anchored rate (English Housing Survey /
planning-application statistics would be the place to look; **not established
this pass and no number is offered**), and a decision about whether an extension
changes `bedrooms`, `floor_area` directly, or the exposed-envelope fraction —
which are three different physics edits with different U-value consequences.

This is the same shape as W2_26's children finding, in the same week, from the
same instruction: *the ruling scopes as "extending the stream" a thing for which
no seam exists.* Two instances is a pattern worth naming for the third ruling —
**the life-event stream can change what a household HAS and cannot change what it
IS.**

---

## 4. FINDING 4 — the standing exclusion and the row's reading of it are not the same instruction

The ruling's sentence is, verbatim (§3 item 3): *"**Heat pump is out of all three
phases until the director says otherwise.**"* It sits at the end of the clause
headed **"Levers in phase 1 (technical ceiling per house, hidden truth)"** — a
list of what the company may model as an intervention: PV, battery, EV charging,
insulation, flow temperature, behavioural actions, tariff fit.

The row's `block_reason` widens it to: *"any adoption curve minted here that
includes one is the defect."*

Those are different bars, and the tree makes the difference material.
`heat_pump_installed` is already live, already anchored
(`_HEAT_PUMP_INSTALL_PROB_BY_YEAR`, 0.1% in 2016 rising to 0.6% in 2025), and
already emitted with no company involvement whatsoever — 81 installs across
2,136 eligible households over ten years. Read as a **lever** exclusion, nothing
in the world changes and the bar binds the phase-1 ceiling set. Read as an
**adoption-curve** exclusion, an existing anchored world mechanism has to be
switched off — and per Finding 1 the obvious way to switch it off silently leaves
71% of households with an immortal boiler.

**Recommendation to the director, treated as adopted unless he objects:** the
exclusion binds the **lever and ceiling set** — the company may not model a heat
pump as something it offers, advises or prices — and does **not** bind the
world's own unprompted adoption stream, which is fidelity and is what lets us
tell a heat pump we sold from one that arrived anyway. If he means the stronger
reading, it is his call and it costs the boiler-replacement repair in Finding 1
first, not after.

Either way the row's `block_reason` and the ruling should say the same thing.
Not edited here: rewriting the director's exclusion to match my reading of it,
before he has read the reading, is the wrong order.

---

## 5. PREDICTIONS — filed before the answer, so they can refute me

1. Repairing Finding 1 (evaluating the boiler branch independently of the
   heat-pump arm) will raise gas demand *variance* across the population and
   *lower* mean gas demand, because ~71% of households gain access to a
   one-way 11.1% efficiency step they currently cannot take.
2. It will move the `H_GAP_fabric_belief_truth_gap` ledger, because the company's
   thermal inference is fitted against consumption that currently contains no
   boiler-replacement steps for the majority.
3. The 10.6% EPC divergence at 2025 is a **floor**, not the answer: it counts only
   insulation, because that is the only fabric field any event writes. Once the
   boiler branch is reachable it will not move (boiler age is not in the band
   mapping) — so if the divergence *does* move when Finding 1 is fixed, my model
   of the band mapping is wrong.

---

## 6. Level definitions and exit criteria (so `level_target: 3` is checkable)

The row carries `level_target: 3` and no level definitions. Proposed, for
ratification when the phase opens:

- **L1 (DISCOVER)** — the change census: every field of a house any mechanism can
  move, what moves it, at what anchored rate, and which of them the fabric model
  reads. Findings 1–3 are its first three rows. *Exit:* one register, and every
  row naming either its anchor or its absence.
- **L2 (BUILD, when authorised)** — every element of §2 item 1 reachable and
  proven reachable: a boiler-replacement rate that fires for the eligible
  population; extensions with a mutable dimension and an anchored rate; a
  reachability control per branch **before** any control of what the branch does.
  *Exit:* a poison round — each unprompted-change branch removed in turn kills a
  named control.
- **L3 (the target)** — the unprompted timeline is *measurable against the
  company's belief*: the EPC staleness gap published with the bound its sample
  earns, on the `H_GAP_fabric_belief_truth_gap` pattern, non-zero and moving.
  *Exit:* a per-signal figure a reader can act on, and a counterfactual split of
  saving-we-caused from saving-that-happened-anyway.

**Proposed `file_scope`** (currently `[]`): `simulation/life_events.py`,
`simulation/fabric_physics.py`, `simulation/premise_population.py`, and the
control file the build writes. Held as a proposal — a level-0 row's `file_scope`
is checked by nothing, so naming files no build has written is itself a defect.

---

## 7. What would make this phase wrong

- **Building "the EPC falls behind" as a new mechanism.** Finding 2. It already
  falls behind. The deliverable is a measurement across the wall, and the wrong
  outcome is a second staleness model beside the one the world already has.
- **Applying the standing exclusion with the existing dial.** Finding 1's table.
  It is the obvious move and it is silently wrong.
- **Treating extensions as a rate.** Finding 3. The rate is the last question;
  the first is which physical quantity an extension changes.
- **Fixing Finding 1 as part of this phase.** It is a live defect in *phase-0*
  world behaviour, ahead of and independent of this atom. It should be repaired
  where it lives, under its own finding, not folded into an unauthorised phase —
  otherwise the repair waits on a director decision it does not need.
- **Starting it.** The phase is registered, not authorised; W2_18 and W2_23 have
  not landed. This document is the whole of what is permitted.

---

## 8. What this pass did not establish

- **Any anchor for an extension rate.** Named as a gap, deliberately without a
  number (CLAUDE.md: an honest absence beats a plausible figure).
- **Whether the `if`/`elif` was deliberate.** No comment, commit message or test
  in the tree states an intent that a heat-pump-eligible household should not
  replace its boiler, and the module docstring at `:10` describes
  `boiler_replaced` without qualification — but absence of a stated intent is not
  proof of an accident. Treated as a defect to file, not as settled.
- **The population-level demand consequence of Finding 1.** Predicted in §5,
  not measured. It needs a run, not a read.
- **Whether `epc_rating` on `Household` is read anywhere the company can see.**
  Only the SIM-side divergence was measured. The company-side EPC objects are
  W2_23's subject and its Finding 1 already says there are two of them.
