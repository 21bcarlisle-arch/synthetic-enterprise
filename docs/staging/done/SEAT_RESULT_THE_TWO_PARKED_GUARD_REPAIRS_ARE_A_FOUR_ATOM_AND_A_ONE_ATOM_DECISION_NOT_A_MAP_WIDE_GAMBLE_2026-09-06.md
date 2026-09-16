**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** EP9_adapter_n3rgy_consented_metering
· **Class:** controls_that_cannot_fail

*RECORDED, not BLOCKING: the atom that prompted it is dispositioned and out of the draw, and
nothing here refuses work. The two guard repairs are still NOT made — but the reason they were
parked (no blast-radius measurement) is now spent, and both turn out to be small.*

# RESULT: the two parked guard repairs are a four-atom and a one-atom decision, not a map-wide gamble

**Found:** 2026-09-06, delivery seat, woken by a LANE 3 doorbell drawing
`EP9_adapter_n3rgy_consented_metering` for a **third** DISCOVER/FRAME pass. Found by checking the
draw before doing it, not by the work failing — the same way the sibling finding was found.

**Answers the question parked in**
`SEAT_FINDING_THE_PASS_CEILING_IS_ON_THE_DRAW_NOBODY_CALLS_2026-09-06.md` §"The two siblings,
stated and NOT repaired", which declined both repairs in as many words because *"reversing a
recorded decision needs the measurement of what those 22 rows are, which this tick does not
have"* and *"keying it to disk instead would change the verdict on every framed atom in the map
at once"*. That measurement is below. **That document is not edited by this one** — it was
untracked and its lane may still be in flight; a second copy of a live finding is the two-rooms
trap. This is a result against it, not a restatement of it.

Measured on the live map at HEAD `0533a77ac`: **336 atoms, 1,273 evidence entries.**

---

## 1. The headline

> Sibling 2 (`_is_frame_saturated` keyed to the evidence list, not to disk) would flip
> **4 atoms**, not "every framed atom in the map". Two of the four are already out of the draw
> on the pass ceiling, so the operational change is **2**, and only **one** needs a judgement
> call.

And a **third mechanism** the sibling finding did not name, because EP17 does not exhibit it:

> **Annotation blindness.** An evidence entry written as `path (annotation)` never resolves to a
> file, so the guard cannot see a FRAME doc the map **does** cite. 225 of 1,273 entries are
> annotated-and-unresolvable; 86 resolve once the annotation is stripped; 3 of those are FRAME
> docs under `docs/design/`; and exactly **one** of those atoms is drawable-for-ever.

---

## 2. Three mechanisms that look like one

The population that matters is the 18 atoms that are `idle`, gapped, unblocked and un-saturated —
the only ones a change to this guard can starve, and the only ones drawable for ever today.

| # | mechanism | who | fixed by |
|---|---|---|---|
| (a) | **No FRAME-named file exists.** FRAME work is complete but lives inside `*_DISCOVER.md`, which the guard excludes *by design* | `EP9` | only the `frame_saturated` override |
| (b) | **FRAME doc on disk, absent from `evidence`** — the proxy/property split the sibling finding named | `EP3`, `EP16`, `EP17` | keying the guard to disk |
| (c) | **FRAME doc cited but annotated**, so the path never resolves | `EP5` | parsing the path before the annotation |

**14 of the 18 have no FRAME doc on disk at all** — genuine FRAME work remains and no repair
here reaches them. That is the number that makes the parked repairs safe: the starve direction
the guard's docstring calls its expensive one has a floor of 4, not 18.

### (b) — the blast radius that was missing

```
currently drawable idle atoms (the only ones a change can starve): 18
  -> would FLIP to saturated (FRAME doc on disk, not in evidence):  4
  -> unchanged, still drawable (no FRAME doc on disk):             14

  FLIPS  passes= 2  EP3_pricing_engine_late_truth   docs/design/frame/EP3_PRICING_ENGINE_LATE_TRUTH_FRAME.md
  FLIPS  passes= 0  EP5_settlement_true_ups         docs/design/EP5_SETTLEMENT_TRUE_UPS_DISCOVER_FRAME.md
  FLIPS  passes= 5  EP16_anchored_generators        docs/design/frame/EP16_ANCHORED_GENERATORS_FRAME.md
  FLIPS  passes= 6  EP17_varied_population_draw     docs/design/frame/EP17_VARIED_POPULATION_DRAW_FRAME.md
```

`EP16` and `EP17` are **already excluded by the pass ceiling** (5 and 6 passes since a move), so
flipping them changes nothing operationally — the sibling finding says so itself. `EP5` is
genuinely framed (§4 of its own doc is titled *"FRAME — the walls this atom is built inside"*,
and its pass 2 closed both open questions, recording that *"the correction is owed to the code,
not to the framing doc"*). **That leaves `EP3_pricing_engine_late_truth` as the single atom
needing a judgement call** — and the sibling finding already records that EP3's own draw was
legitimate at 2 passes, so the honest next step is to read EP3's FRAME doc and decide, which is
an atom-sized question rather than a map-sized one.

### (c) — annotation blindness, newly named

`EP5`'s evidence **does** name its FRAME doc. The guard still reads it as unframed, because the
entry is `docs/design/EP5_SETTLEMENT_TRUE_UPS_DISCOVER_FRAME.md (2026-08-17 DISCOVER/FRAME, level
held at 0: ...)` and that string is not a path. The annotation convention is widespread and
deliberate — this is the guard failing to read the map, not the map being wrong.

```
evidence entries on the live map:            1273
unresolvable ONLY because of an annotation:   225
  ...of which the stripped path DOES exist:    86
  ...of which are FRAME docs under docs/design/: 3
      EP5_settlement_true_ups   <- drawable-for-ever: TRUE
      PB1_population_target_and_its_price       (not drawable)
      PB2_opening_book_won_not_assigned         (not drawable)
```

**Blast radius of that repair: one atom.** Note it is the *same* atom as one of (b)'s four, so
(b) and (c) together are still a 4-atom change, not 8.

---

## 3. What was actioned, and what deliberately was not

**Actioned — `EP9` only.** `frame_saturated: true` set on its map row: the documented R11 escape,
for precisely its documented case. The supervisor's own docstring records that the other live
`frame_saturated: true` atoms are this same shape (*"carry DISCOVER-named docs"*); nobody had set
it here. Its FRAME is real — L1/L2/L3 with falsifiers, pass 1 §7, restated and extended with
precondition EP9-P0 in pass 2 §4. Only BUILD remains, and BUILD is epoch-3 gated: the saturated
condition exactly. Reversible by deleting the line; auto-clears when the BUILD gate opens.

**Proven, both directions** — the property, not today's answer:

```
EP9 returned by the live idle DISCOVER/FRAME draw in 400 draws:  0
draw still returns work (not starved):  True -> EP3_pricing_engine_late_truth
idle candidate pool: 18 -> 17           (exclusion, not collapse)
```

The second line is the leg that matters: an "excluded" that emptied the draw would look identical
on the first line alone.

**Not actioned, each for a stated reason:**

- **No control code changed.** Both repairs are now measured, but making them needs R15 mutation
  proof against the starve direction, and that is more than a bounded doc-lane tick carries. The
  measurement is the deliverable; the repair is the next tick's, and it is now cheap.
- **`EP5` was NOT given an override.** It would have worked, and it would have been wrong: its
  defect is (c), and an override masks the annotation bug and makes the real repair unverifiable.
- **`EP19_counterparty_qualification_paths` was checked and DELIBERATELY LEFT DRAWABLE.** It
  carries two DISCOVER-named docs and looks like EP9 from the outside. It is not: neither doc has
  a FRAME section, and both carry open items forward. Marking it would **starve a genuinely
  unframed atom** — the fail-toward-starve direction the guard's own docstring names as its
  expensive one. The distinction between EP9 and EP19 is the whole reason this was done by
  reading the docs rather than by sweeping every atom with a DISCOVER doc.

---

## 4. The undercount that let the third draw happen

Separately from the guard: `tools.discovery_pass_ceiling` counts passes as `len(notes)` from the
simplifications store. **EP9's pass 2 landed its document and appended no note**, so the ceiling
read **1 pass when 2 had landed**, against a ceiling of 5.

This is not EP9-only. `EP5` has two landed DISCOVER docs and read **0 passes**. The five FRAME
passes that landed in the last day (`W1_23`, `W1_24`, `W2_24`, `W2_25`, `W2_26`) all read **0** —
they are covered only because their FRAME doc *is* in evidence, so the saturation guard answers
first. **Two guards, one property: when the first answers, the second's undercount is invisible.**

EP9's store is corrected to 3 (pass 2 recorded late and labelled as such, plus this pass), and
`simplifications_count` on the map row moved 1 → 3 to match.

The general shape — *a pass that lands a doc without appending a note is invisible to the control
that exists to make the discovery lane finite* — is stated here and **not** separately minted: it
is the same subject as the sibling finding this document answers, and belongs with it.
