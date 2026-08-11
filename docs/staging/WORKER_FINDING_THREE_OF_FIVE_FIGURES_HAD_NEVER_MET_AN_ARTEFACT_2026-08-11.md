# WORKER FINDING — three of the five published figures had never met an artefact

**Found:** 2026-08-11, H27 Expert Hour #19 (worker tick, `H27_payment_belief_gap` 2→3 HARDEN draw)
**Class:** a population control with no per-member vacuity guard · **Disposition:** mechanism landed
**Answer to the draw:** still **L2**. Nineteen Hours, nineteen defects.

## The leads, and why they were one repair

Hour #18 left two:

> 1. *"D35 is still unbuilt as scoped … declaring the door's 3dp site without extending
>    `measure_component_render_sites` past this process's edge would red
>    `check_component_render_sites`. The register and the sweep have to move together."*
> 2. *"The render/carrier boundary is undefined. 'The epsilon is half a step of the finest
>    render' collapses to 1e-17 the moment the walk reaches a JSON hand-off."*

They cannot be pulled separately. The walk out to the door **crosses** the JSON hand-off, so lead 1
without lead 2 collapses every epsilon this instrument publishes; and lead 2 has nothing to be a
boundary *of* until the walk crosses something. Building the walk found the actual defect.

## Half one: THE DEFECT. A population control with no per-member guard

`measure_component_render_sites` finds **zero render sites** for `belief`, `detection` and
`detection_latency` — three of the five published figures — and `check_component_render_sites`
**says nothing about any of them**:

```
ageing                 1 site   (ageing.ordinal_direction_caveat @6dp)
belief_population_mix  1 site   (belief_population_mix.note @4dp)
belief                 0 sites  declared 4dp   <- control silent
detection              0 sites  declared 4dp   <- control silent
detection_latency      0 sites  declared 2dp   <- control silent
findings: []
```

Every finding that control can emit is keyed either to a site it **found** or to a site the register
**declared**, and those three declare no `component_renders`. So the artefact-side half of D34/D35 —
the half whose entire purpose is independence from the AST read — **passed vacuously on 60% of its
population**, and those three figures' reader precisions were an AST read of one named function and
nothing else.

Its only vacuity guard is a **global** `any(row["sites"] for row in out.values())`. That is Hour
#18's own finding one level up, inside the instrument that found it: the door's per-panel substring
search passed on a number legible two rows away; this passes because *some other dimension* has a
site. A population control needs its guard per member.

**Why it could not be fixed in place.** Per-dimension vacuity is *unsatisfiable* in-process: those
three figures reach their reader through the note `measure_and_write` composes and through the Proof
door, both past this process's edge. Which is lead 1 — and lead 1 crosses the carrier, which is
lead 2.

## The boundary, and it is a TYPE rather than a declaration

* a **RENDER** is the figure's digits inside a **string** a reader is handed. Some code chose that
  precision, so it *is* a precision, and it sets the epsilon.
* a **CARRIER** is the figure as a **number** in a machine hand-off. Nobody chose the digits in the
  serialised bytes — they are the double's — so a carrier can never set an epsilon. It must be
  **walked through** to the render beyond it, and a carrier reaching no render is a figure the
  reader is never shown, which is a thing to report rather than a thing to pass.

No register field says which is which, deliberately: a declaration is the hand-typed keyset this
module has now been escaped by nine times. The walk classifies by the **type of the hand-off it is
holding** and never searches serialised text. That one restraint is the whole of lead 2, and it is
load-bearing — restoring the text search in a mutation brings the 18dp site straight back
(`json.dumps` of seed 7's headline is `0.014505119453924915`), which is an epsilon of 5e-19, fourteen
orders of magnitude below the shipped one.

## Half two: the second finding. The two-seed rule cannot see a SIBLING

The discrimination rule tells a figure from a **constant** — `"0.0"` is in half the strings this
module publishes and is a render of nothing. It cannot tell a figure from a **sibling quantity that
moves with it**.

`belief_population_mix` (a population TV distance) equals belief's **per-case disagreement** rate on
every book measured:

| seed | 7 | 11 | 23 | 101 | 999 |
|---|---|---|---|---|---|
| `belief_population_mix` | 0.0800 | 0.1033 | 0.0767 | 0.0867 | 0.0767 |
| per-case disagreement | 0.0800 | 0.1033 | 0.0767 | 0.0867 | 0.0767 |

So the mix figure's digits appear inside `format_belief_summary`, **which does not render it**. They
are genuinely different quantities — the D19 note records that they separate under a permutation of
which account holds which severity belief (TV held at 0.0713 while per-case agreement fell 0.9287 →
0.6432) — and no real book performs that permutation, so no value-only sweep can ever separate them.
A value-only walk would have moved this figure's epsilon on the strength of another figure's render
precision.

**The repair is provenance, not a better value test.** A site in a figure's own declared renderer,
or on the door it was handed to as a carrier, is a render *of* that figure. A match inside another
figure's renderer is **cross-attributed** and fails closed: the register must resolve it in one of
two directions and neither may be silent — `reader_renders` ("it really is rendered there, move the
epsilon") or `value_collisions` ("that is a different quantity that happens to equal mine", with the
reason).

## What landed

* **`measure_reader_render_sites`** — the walk past the component strings, over two surfaces the
  component sweep structurally cannot see: each figure's **own declared renderer's output** (the
  string `measure_and_write` concatenates verbatim into the ledger note), and the **Proof door**,
  rendered by the page's own inline JavaScript from the ledger carrier. The chain is walked by
  calling the shipped code at every step — `to_ledger_entry` → `coupled_gap_ledger.json` →
  `_coupled_gaps` → the page's script — because a hand-built row is the harness supplying the call
  list it is meant to be auditing.
* **The door site, declared at last.** `fmtGap` renders the carrier at **3dp** — the first render
  site any sweep of this module has found outside its own process. Coarser than the declared 4dp, so
  no epsilon moves; it is now measured on the rendered pixel every run instead of having been looked
  at once by hand in Hour #18.
* **Per-dimension vacuity**, over the union of both sweeps — because the surfaces are complementary
  (`belief_population_mix` has no callable module-level renderer and passes on its component site;
  `detection` has no component site and passes on its renderer and the door). What may not happen is
  a figure found *nowhere*, which is what three of the five were.
* **The note-verbatim seam is now asserted.** Four of five figures are measured on their renderer's
  output, and that is a reader surface *only* because the door concatenates the string unchanged —
  something Hour #18 verified once by hand and nothing had asserted since.
* **An uncallable declared renderer is recorded, not skipped** (`measure_and_write` is a method, so
  no call on a bare result reproduces the string its reader is handed).

**R15 — seven mutations each firing a NAMED finding, plus one proving the carrier boundary
load-bearing.** The carrier read as text (18dp site returns, epsilon
5e-19); the door's `fmtGap` moved to 6dp in a mutated copy of the page (fires: "sets its epsilon from
4dp while a reader surface renders it at 6dp"); the door no longer printing the note verbatim; a
declared reader site the walk cannot find; the door unreachable (fires rather than reading as a clean
door); each of the three zero-site figures named by the vacuity guard; the mix figure's collision
declaration removed; and the shipped three-of-five silence recorded as a fact so a future component
render moves it rather than passing.

**R12:** no published number moved — epsilons unchanged at ageing 5e-7, belief/mix/detection 5e-5,
latency 5e-3. This Hour changed what is *measured*, never what is computed.

**R11:** the door site is verified by executing the page's own inline JavaScript against a payload
built by the real generator off a real scoring, and asserting the rendered pixel.

## Why still L2

L3 means Expert Hour says "this is real". Nineteen Hours, nineteen defects, and Hour #4's
stated-in-advance criterion of **two consecutive clean Hours** has still not been approached. This
Hour found the artefact-side control — the independent half of the pair D34/D35 were both minted to
build — passing vacuously on three of its five members, and a discrimination rule that cannot see a
sibling. Neither is a figure moving; both are the instrument not having been looking.

## Hour #20 leads, in order

1. **The sibling hole is a CLASS, and only one instance is closed.** `value_collisions` now names one
   coincidence. Nothing has swept the other four figures against every other published quantity for
   the same shape, and the component sweep — which has no provenance notion at all — is still
   attributing purely on value. Its `ageing.ordinal_direction_caveat` and
   `belief_population_mix.note` sites happen to be self-owned, but nothing checks that.
2. **The permutation that separates the mix figure from per-case disagreement is described in a
   note and has never been run by any control.** It is the only thing that makes them two
   quantities; if it were wrong, the D19 reshape rests on it.
3. **Whose defect is the fabric rows'?** Carried from Hour #18, still untaken: 43 unreadable figures
   were W1_11/W1_12's, found from H27's chair, and no one has asked whether those atoms' evidence
   claims rested on figures nobody could read.
4. **D34 and D33 are still unbuilt** (per-figure resolution floors for `detection`,
   `detection_latency`, `ageing`; the bit-equality movement predicate). Four reshape atoms sit at L0
   behind this instrument, each minted by an Hour and none built.
5. **Carried forward, still untaken:** the interior collapses have no owner of their own (Hour #11's
   lead 1, now seven times deferred); Hour #8's pinned generated value
   `assert c["n_recon_detected_undated"] == 0`; and whether the other dimensions' normalisation
   notes have the same gap between what they DENY and what they ESTABLISH.
