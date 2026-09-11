**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** unminted

*LATENT, not BLOCKING: nothing is refused, no gate is red, and the world runs. It is a fidelity
defect in a live world mechanism, and it silently bounds a counterfactual the mission depends on.*

# Seventy-one percent of households have a boiler that can never be replaced, and the dial that looks like the fix does not touch it

**Found:** 2026-09-06, delivery seat, during the DISCOVER/FRAME pass on
`W2_24_housing_phase3_houses_change_on_their_own_timeline`. Full working:
`docs/design/W2_24_HOUSING_PHASE3_FRAME.md` §1. Filed separately because the repair belongs to
live phase-0 world behaviour and must not wait on an unauthorised phase.

---

## The measurement

`draw_premise_population(3000, base_seed=42, as_of=2016-01-01)`, life events over 2016–2025:

```
  gas-heated                       2,727  (90.9% of the drawn population)
    heat-pump ELIGIBLE             2,136  (78.3% of gas)  boiler_replaced =   0   (0.0000/household/10y)
    heat-pump ineligible             591  (21.7% of gas)  boiler_replaced = 214   (0.3621/household/10y)
```

Zero, not few. **71% of all households have a boiler that cannot be replaced in ten years.**

---

## The cause

`simulation/life_events.py:455` ff.:

```python
if (household.hp_eligible
        and heating in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM)):
    ...                                   # heat pump, prob 0.001-0.006/yr
elif heating in (HeatingSystem.GAS_BOILER_COMBI, HeatingSystem.GAS_BOILER_SYSTEM):
    ...                                   # boiler replacement, prob 0.09 / 0.04 / 0.01 by age
```

The `elif` is gated on the **eligibility condition**, not on whether the heat-pump draw fired.
`hp_eligible` is `residential and not a flat and bedrooms >= 2` (`simulation/household.py:146`),
so for the large majority the first arm is entered every year at a 0.1–0.6% probability and the
9%/4%/1% branch is never evaluated at all.

## The part that makes it worse

`adoption_eligibility_multiplier` is the existing director-facing dial for turning low-carbon
adoption down. Over 1,068 eligible gas households (`base_seed=7`):

```
  multiplier 1.00   heat pumps 41   boiler replacements 0
  multiplier 0.17   heat pumps  4   boiler replacements 0
  multiplier 0.00   heat pumps  0   boiler replacements 0
```

Turning the heat pump **completely off** leaves the boiler branch just as dead: the suppression is
structural, not probabilistic. This matters now because the housing ruling of 2026-09-05 carries a
standing exclusion — *"Heat pump is out of all three phases until the director says otherwise"* —
and setting this dial to zero is the obvious way to honour it. Doing so would produce a world with
no heat pumps **and** no boiler replacements, and nothing would report the second half.

## Why it costs something real

`boiler_age` sets combustion efficiency in `fabric_physics._fuel_for` via `_BOILER_EFFICIENCY`
(OLD 0.80, MID 0.86, NEW 0.90). An OLD→NEW replacement cuts gas for space heat and hot water by
`1 - 0.80/0.90` = **11.1%**, permanently, with no company involvement — an unprompted saving that
71% of households cannot experience. That is the counterfactual the mission's value-CREATED side is
measured against: a world where efficiency only ever improves because we sold something cannot
distinguish value created from value claimed.

## Why no control caught it

- `tests/simulation/test_phase_b_life_events.py:263` tests `apply_events` on a hand-built
  `boiler_replaced` event. That proves the **applier** and says nothing about the emitter.
- `:858 test_multiplier_leaves_non_adoption_events_untouched` uses a semi-detached — an *eligible*
  household — and asserts non-adoption events are byte-identical across multipliers. For that
  household the boiler-replacement list is empty on both sides, so the assertion passes **vacuously
  over the very event its own comment names**.

CLAUDE.md, on exactly this: *when a branch exists to be taken rarely, assert it CAN be taken before
asserting what it does.* No control asserts the boiler branch is reachable for the population it
covers.

---

## The repair, and what it must carry

Evaluate the boiler branch independently of the heat-pump arm — the two are mutually exclusive
*given the draw outcome*, not *given eligibility*. Order within a year needs stating rather than
inheriting: a household that installs a heat pump in March should not also replace a gas boiler in
November, and `heating`/`boiler_age` are already carried forward in the loop, so the guard is on
the post-draw state.

**The repair is not complete without a reachability control** over the eligible population, written
before any control of what the branch does, per the rule the vacuous test above broke.

**Predicted effect, filed before the run:** mean gas demand falls and its cross-population variance
rises, and the `H_GAP_fabric_belief_truth_gap` ledger moves, because the company's thermal inference
is fitted against consumption that today contains no boiler-replacement steps for the majority. If
the gap does not move, my model of what that ledger reads is wrong.

**Not repaired in this turn**, and the reason is scope rather than difficulty: the frame pass that
found it is DISCOVER-only under epoch gating, and a world-behaviour change of this size wants its
own turn, its own before/after numbers and its own reachability control — not a hunk carried in on a
documentation commit.
