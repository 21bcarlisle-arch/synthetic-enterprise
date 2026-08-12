# WORKER FINDING — a value test decided whose render the door was

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-12, H27 Expert Hour #21 (worker tick, `H27_payment_belief_gap` 2→3 HARDEN draw)
**Class:** a value comparison standing in for a provenance answer · **Disposition:** mechanism landed (atom D37)
**Answer to the draw:** still **L2**. Twenty-one Hours, twenty-one defects.

## The leads, and why they were one repair

Hour #20 minted two and took neither:

> 1. `D37_the_door_gate_decides_provenance_by_value` — `has_door_carrier` admits a figure to the
>    door surface only where its carrier **equals** the panel row's value … and it now excludes four
>    figures from a surface that demonstrably renders them, since the door prints the whole composed
>    note; they pass only because the `note` site carries the same precision, which is coverage by
>    coincidence one level down.
> 2. `D38_the_doors_numeric_render_is_a_surface_neither_sweep_can_express` — the door renders every
>    numeric component of that entry at 4dp (`fmtComponent`/`flattenNumbers`, integer counts
>    included) … the component sweep searches only strings the entry carries, and the door html is
>    searched for `detection` alone.

They are one repair. Lead 2 is unreachable *while* lead 1 stands: the components block only becomes
searchable once the door stops being one string admitted to one dimension, and once it is split by
region, the numeric-component region is simply one of the four with an owner. Building the split is
what measured lead 2's actual consequence.

## The defect

```python
# tools/couple_w2_11_d5.py, as shipped from Hour #19 to Hour #21
has_door_carrier = (
    door_state.get("available") is True
    and all(v is not None for v in door_carriers)
    and all(a is not None and b is not None and float(a) == float(b)
            for a, b in zip(values, door_carriers))
)
```

This is a **value test doing provenance work** — the exact shape Hour #19 named when it built
`cross_attributed` ("a match inside another figure's renderer is a value coincidence until something
other than the digits says otherwise"), sitting unrepaired in the gate one level up, in the same
function.

It fails in **both** directions:

* **It excluded four of the five figures from a surface that renders them.** The door prints the
  composed note verbatim — this instrument already asserts that every run — and each companion's own
  renderer's digits are inside it. Measured on the rendered pixel: `ageing` at 3dp, `belief` at 4dp,
  `belief_population_mix` at 4dp, `detection_latency` at 2dp, all in the panel's note region. None of
  them was searched there. Their coverage came from the entry's `note` one hand-off upstream, at the
  same precisions — **coverage by coincidence**, which is exactly what Hour #20 named as the shape
  that let a wrong epsilon stand for three Hours.
* **It would have handed the whole panel to any companion that happened to equal the headline.** The
  gate admits on digits alone, so a companion whose carrier matched on both books would have been
  credited with `fmtGap`'s 3dp *and* every 4dp numeric component — a figure's epsilon moved on the
  strength of another figure's render. That is not hypothetical for this register: the mix figure
  already collides with belief's per-case disagreement rate on every book measured (Hour #19).

## What landed (atom D37)

1. **The headline is answered by IDENTITY, at the seam it actually crosses.** `_publish_one_book`
   spies `write_gap_entry` as the composer holds it and records the `GapResult` **object** handed
   downstream, then matches it by `is` against the scorer's five. Fails closed both ways — nothing
   captured, or more than one dimension matching, raises; an unresolved headline owns nothing
   (`<ambiguous>` matches no dimension, so every region cross-attributes and the register cannot
   resolve it into silence).
2. **The door is four regions, not one string**, split off the rendered HTML by the door's **own**
   class attributes and keyed `door:coupled-gaps#gap-val` / `#note` / `#components` / `#basis`:
   `gap-val`, `components` and `basis` are owned by the headline (they render the number the composer
   handed the writer); `note` is every figure's, because the panel prints that string unchanged.
3. **The register corrected FROM the measurement.** All five figures now declare their door site;
   `detection`'s single `door:coupled-gaps` entry at 3dp *and* 4dp splits into the two different
   surfaces it always was. **No epsilon moved** — every door render is at a precision the figure
   already had (R12: 4/4/4/2/3 unchanged).
4. **The verbatim seam, stated in this instrument's own units.** `note_verbatim` tests the seam on
   the note's first 60 characters. The new check tests it where it is load-bearing: every precision
   at which the door's note renders a figure must be a precision at which the **entry's** note
   renders it, and vice versa. Without it the companions' door coverage is a coincidence and not the
   seam it is claimed on.
5. **Fail-closed on the door's own shape.** A class in the row this walk cannot name is an
   unclassified region — a reader surface nobody searches, which is this instrument's entire subject
   — and fails the walk. So does a named region that came back empty, because a region that vanished
   reads to a value sweep exactly like a region the figure does not appear in. (The census fired
   immediately on `chip blue`, a `classifyGap` severity the first draft had guessed wrong.)
6. **Lead 2, measured.** `#components` is now a named, owned, searched region. `fmtComponent` /
   `flattenNumbers` re-render every finite numeric leaf of the headline's components at 4dp, and
   **none of the five published figures is among them** — so no epsilon rests on that surface today.
   That is now a measurement rather than an absence of one: a component that did land there would be
   found, and if it were not the headline's it would cross-attribute.

## R15

Mutations, each firing a **named** finding: the value gate restored and pointed at a companion made
equal to the headline (it admits, provenance does not); the composer no longer crossing the ledger
seam (raises, never falls back to digits); a door grown a fifth region (`gap-audit`); a named region
emptied; the door's note diverging from the entry's note at one figure's precision; plus the Hour-#19
and Hour-#20 mutations re-run against the region keys (`fmtGap` at 6dp, the withheld note, the
dropped renderer string, the unreachable door, the carrier read as text).

## R12

No published number and no published string moved. The door's regions render every figure at a
precision it already carried, so every epsilon, band, floor and collapse this instrument certifies is
unchanged.

## Still L2

Twenty-one Hours, twenty-one defects. Hour #4's two-consecutive-clean-Hours criterion is not
approached.

## Leads minted, not taken

1. **`D39_the_bar_is_a_scaled_render_no_sweep_can_express`** — the door's `gap-bar` span is
   `width: <barPct.toFixed(0)>%`, i.e. the headline rendered at 0 decimals *of a value scaled by 100*,
   which is 2dp of the figure. Coarser than the declared 4dp, so nothing moves — but every sweep in
   this module searches **unscaled** literals only, so a scaled render finer than the declaration
   would be invisible. Expressing scaled renders means deciding which scalings are in the population,
   which is a design question, not an edit.
2. **`D40_the_region_census_is_a_hand_typed_keyset`** — `_DOOR_ROW_KNOWN_CLASSES` is a hand-typed
   list, which is the construct this module records having been escaped by nine times. It fails
   *closed* rather than open, so it is the safe direction of that mistake; the open question is
   whether the row's regions can be derived from the door's own render instead of enumerated.
