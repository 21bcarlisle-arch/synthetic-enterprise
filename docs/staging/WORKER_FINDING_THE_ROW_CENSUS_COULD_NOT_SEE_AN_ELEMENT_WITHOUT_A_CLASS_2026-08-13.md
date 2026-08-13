# WORKER FINDING — the row census could not see an element without a class

**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/tools/test_couple_w2_11_d5.py::test_a_classless_element_the_door_grows_fires`, `tests/tools/test_couple_w2_11_d5.py::test_the_row_census_is_the_rendered_elements_and_the_register_is_clean`, `tools/couple_w2_11_d5.py` — the population is now the rendered elements, and the mutation that grows a classless render fires by name.

**Found:** 2026-08-13, H27 Expert Hour #27 (worker tick, `H27_payment_belief_gap` 2→3 HARDEN draw)
**Class:** a census keyed on an attribute is blind to every element that does not carry it · **Disposition:** mechanism landed (atom D40, and D39 answered with it)
**Answer to the draw:** still **L2**. Twenty-seven Hours, twenty-seven defects.

## Why this Hour, and where

Hour #26 closed with a warning it owed the next tick: H27's remaining questions — D35's
scoped build, D39, D40, and Hour #21's vacuous-in-isolation sibling control — **are all
payable by a BUILD draw on this box**, and nobody had taken one for six Hours. It also
measured that six of the twenty-four recorded Hours left no trace in any file this atom
declares. This Hour is on the atom's own `file_scope` (`tools/couple_w2_11_d5.py` and its
test), on the instrument, and it takes two of the four owed leads.

They are one repair, for the same reason Hour #21's own two leads were.

## The defect

`_DOOR_ROW_KNOWN_CLASSES` enumerates every class the door's row is known to carry, and
`_door_row_regions` refuses any class outside it. Its stated guarantee, in its own comment:

> the row is required to contain no class this walk cannot name — a door that grows a
> fifth region fails the walk instead of rendering a figure nobody searches.

**That guarantee is false for any region the door renders without a class, and the row has
five such elements today.** Measured on the rendered pixel, driving the live page's own
JavaScript:

```
<div>                                        (the head's left column)
<div style="text-align:right">               (the head's right column)
<span style="width:12%;background:…">        (the bar's fill)
<details> / <summary>                        (the components block)
```

`re.findall(r'class="([^"]*)"', row)` returns nothing for any of them. They are not classes
the census cannot name; they are elements it never looked at. A census keyed on an
attribute cannot express the population of elements that do not carry the attribute.

**One of the five renders the headline.** The bar's fill span is
`width:<barPct.toFixed(0)>%` — the figure clamped to [0,1], scaled by 100, rounded to 0dp.
Measured across the two published books: `0.11818…` → `width:12%`, `0.12931…` → `width:13%`.
It is invisible twice over: to the class census because it carries no class, and to every
literal sweep in this module because all of them search **unscaled** digits, and `12` is
not among any rendering of `0.118`. That is D39, arrived at from the population side
instead of the precision side.

**And the census cannot tell a wrapper from a region.** Its only response to any door
change is the same stop-the-world refusal, which a maintainer discharges by appending a
string to the tuple — the same one-line discharge available whichever it was. Its own
comment says as much ("a class that turns out to be a severity is a one-line correction,
while a class that turns out to be a new render region is the defect this Hour exists
for") and nothing tells the maintainer which one they are holding.

## The second instance, on a region that IS declared

The same shape one level in. `basis` is one of the four named regions, owned by the
headline and searched for its digits every run. On both published books it renders:

```
baseline g0 0.500 · raw 0.000 · measured 2026-08-13
```

**It is inert.** Everything it prints is a designed constant, a quantity that renders 0.000
at the door's own 3dp, or the run stamp. To the two-book discrimination rule every sweep
here turns on, an inert region is indistinguishable from a region that does not render the
figure at all — so this surface can never credit any figure with a site, and its declared
ownership buys nothing. The guard one level up cannot see it, because it tests for a region
that came back **empty**, and a constant is not empty. Reported, not tuned (R12).

## What landed (atom D40)

1. **The population is the rendered elements**, walked with the page's own HTML as the
   browser builds it (`_DoorRowWalker`, `_door_row_surfaces`), path-keyed, each element
   carrying the text it owns itself — a nested element's text belongs to the nested
   element, so a wrapper is inert unless it prints something itself.
2. **NOT derived from the door.** Deriving the known-set from the render would make the
   subject its own population — every class the door emits would be known by construction,
   which is the fail-**open** direction of the same mistake. D40's open question therefore
   has a negative answer, and it is the answer that matters: what gets derived is the
   population; what stays declared is what each surface **is**.
3. **The classification is MEASURED, not enumerated.** Across the two books already walked:
   does the element's own text move? do any of its attributes move? A wrapper is invariant
   by construction; a render moves. The same two-book rule both sweeps here already turn
   on, applied one level up — to the surfaces rather than to the literals inside them.
4. **Attributes are in the population**, because a render need not be text. That is what
   makes the bar expressible.
5. **The scaled render is held to the pixel** (D39). The declaration states the scaling and
   the clamp; the check **predicts** the rendered literal from the carrier and confirms it
   against the artefact on every book, and compares the precision the scaling implies
   (`decimals + log10(scale)` = 2dp) against the epsilon the figure is set from (4dp).
   Coarser, so **no epsilon moves** — and that is now a measurement rather than an absence
   of one.
6. **The inert `basis` region is declared with its reason**, and a declared region measured
   inert with no stated reason is itself a finding. A limit of this instrument is said out
   loud, not declared away.

## R15

Ten mutations, each firing a **named** finding, nine of them by mutating the **door's own
source** and re-rendering rather than by editing the measurement:

* a classless `<span>` grown on the row rendering the figure — and the **old class census
  is proven silent on it in the same test**, which is the defect stated as a control;
* a declared structural wrapper (`gap-bar`) that starts printing the figure;
* a searched region (`note`) gone constant — with the shipped empty-region guard proven
  silent, because the region is present and non-empty;
* a declared surface the door stopped rendering (a declaration outliving its element);
* a render arriving in an **attribute** the declaration does not allow (`title`);
* the bar rendered at `toFixed(2)`, so the declared scaling no longer predicts the pixel;
* the bar at `toFixed(3)` **with the declaration moved to match** — the prediction passes
  and the epsilon alarm fires alone, at an effective 5dp against a 4dp epsilon;
* a row whose SHAPE is the book's (an untested entry: no bar span, a different chip) —
  refused, because aligning what two books have in common would report the elements they
  agree about and stay silent about the one only one of them renders;
* a walk that reached the door and recorded no census (**fail-silent**);
* a single book (refused: one row cannot tell a wrapper holding a constant from a region
  rendering the figure).

**Not always-red:** the shipped register describes the shipped door exactly — every
rendered element has a declaration, every declaration has an element, zero findings on the
real books and on the fixture. The fixture's population is asserted **equal** to the
declared one rather than assumed, and the three-way split (3 text-movers, 1 attribute-mover,
15 inert) is asserted as a measurement rather than a restatement of the declaration.

## R12

No published number and no published string moved. This Hour touched no scorer: the change
is entirely in what the reader-surface walk can see.

## Still L2

Twenty-seven Hours, twenty-seven defects. Hour #4's two-consecutive-clean-Hours criterion
is at zero. The 2→3 is drawable, unblocked and not taken here, for the reason every release
has given: this Hour changed what the instrument can see. But the honest reason is narrower
than most — nothing it did makes the five published figures better or worse, and no epsilon,
band, floor or collapse moved. What it establishes is that a surface of the public door has
been rendering the headline, at 2dp, to a census that could not have found it.

## Leads minted, not taken

1. **`raw 0.000` on the public basis line** while the gap reads 0.118. Either the raw gap
   really is ~0 and the basis line is telling the reader something surprising, or it is the
   render of a quantity that is not being carried. Nobody has asked; it is on the Proof
   door today.
2. **The clamp is a limit nobody states.** Outside [0, 1] the bar renders nothing that
   moves — a `worse than blind` gap (>1) and a leak (≤0) are pixel-identical at the bar to
   a gap of exactly 1 and 0. The door has a `classifyGap` band for both.
3. **The other rows.** This census is the H27 row's. The panel renders seven pairs through
   the same code, and no other pair's row has ever been walked element by element — which
   is Hour #18's unanswered question ("whose Hour are the fabric rows' 43 unreadable
   figures?") in its population form.
4. **Still owed, a seventh Hour running:** D35's scoped build, and Hour #21's
   vacuous-in-isolation sibling control (`test_a_composer_that_stops_carrying_a_renderers_string_fires`).
5. **D37–D43 exist only in this register's prose and in no map cell**, a sixth Hour running.
