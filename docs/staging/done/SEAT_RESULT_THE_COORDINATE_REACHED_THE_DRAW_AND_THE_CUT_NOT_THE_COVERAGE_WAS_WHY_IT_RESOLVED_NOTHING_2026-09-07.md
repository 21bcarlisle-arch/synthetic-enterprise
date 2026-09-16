**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_14_weather_cells_for_household_heat_load

# SEAT RESULT — the coordinate reached the draw, and the CUT, not the coverage, was why it resolved nothing

**Date:** 2026-09-07
**Scores:** `docs/staging/SEAT_PREREG_DID_THE_COORDINATE_REACH_THE_CELLS_2026-09-07.md`
**Measured on real disk before the artefact was re-cut.**

## The scores

| | prediction | outcome |
|---|---|---|
| **P1** | with `draw_region=True`, 100% of drawn households carry a non-None `lat`/`lon` | **TRUE** — 201/201 seed 7, 195/195 seed 11, 183/183 seed 42 |
| **P2** | the share `cells_for_location` RESOLVES is "low, well under 10%", near ~2–3.5% | **FALSE — by a category, not a margin** |
| **P3** | flipping `draw_region=True` in the tripwire turns it red | **superseded** — a concurrent lane had already rewritten the tripwire (`f27695607`) |
| **P4** | `test_derive_reproduces_the_committed_artefact` is pre-existing at HEAD, unrelated to W2_18 | **verdict TRUE, stated cause WRONG** |

## P2 is the one worth reading

The predicted answer was 2–3.5%. **The true answer was 0%** — not one of 579 drawn households across
three seeds resolved — and after the re-cut it is **100%**.

The prereg's own escape hatch names the error exactly: *"If this comes back near 100% I have misread
what the artefact's coverage counts."* It did, and the misreading is this project's most expensive
recurring shape — **two different quantities wearing one name**:

* `cells_for_location` asks **is this coordinate in the artefact at all** — a property of the CUT.
  The artefact was cut over seven locations, so the answer for any drawn household was 0%, and no
  coverage figure entered into it.
* `cell_matched_site` asks **does an archive site share all three cells** — a property of ARCHIVE
  BREADTH. That is the ~2% figure, and it is a share of GB households, not of the draw.

The prereg predicted the second number for the first question. **The forecast nobody wrote is the
right one:** resolution is 0% until the artefact is re-cut and 100% the moment it is, because the
cut is a property of an artefact, not of the world. Recorded here as a scored miss rather than
quietly revised.

## The two numbers still must not be differenced

After the re-cut, drawn households reaching an archive site: **2/201, 0/195, 2/183 — 4/579, ~0.7%**.
The artefact publishes `all_three = 2.0%`, and the frame block says **200 of 139,938 cells (0.14%)**
reach one.

All three are correct and they count different sets: 2.0% is household-weighted over GB, 0.7% is
over the ten regions the curriculum draws, 0.14% is unweighted over frame cells. Differencing any
pair produces a number that counts nothing. Named because they sit one word apart on every surface.

## P4 — right answer, wrong reason, and the reason mattered

The red WAS pre-existing and WAS unrelated to W2_18. But the prereg diagnosed *"the signature of a
degraded local pull"*, and it was not: the placement moved from postcode centroids to the OS Open
UPRN address record on 2026-09-06 (**121,668 → 175,188 occupied cells**). Coverage fell because the
denominator got bigger and more honest. Acting on the "degraded pull" reading would have re-pulled
data that was already correct and left four published percentages a method behind.

*A right verdict resting on a wrong cause still needs correcting: the next reader inherits the
cause, not the verdict.*

## Two lanes reached this independently, and that is the strongest part of the evidence

`f27695607` (a concurrent seat) regenerated the artefact onto the UPRN placement and moved the four
percentages, hours before this landed. This lane derived the same artefact independently. **Every
shared key is byte-identical** — `occupied_land_cells`, `archive_sites`, `locations`, `coverage`,
and the same re-chosen reachability witness at (50.4689, −4.1492). Two independent derivations
agreeing exactly is better evidence for those figures than either run alone.

They diagnosed the cut and named the remedy in their refusal text; this commit builds it. The
artefact is now cut over all 139,938 drawable coordinates (0 dropped, max 6.6 m), and their
`test_a_drawn_household_...` leg 3 fired exactly as its docstring said it would — deleted, not
weakened, per that instruction.

**One correction to their figures, and it is a rounding convention, not a measurement:** the
artefact holds `annual_sun = 0.1725` and every surface that PRINTS it renders **17.2%**; the
docstring and map row said 17.3%. Aligned to what the code emits. The witness distance likewise
moves 301 km → **304.2 km**, now `furthest_matching_frame_cells`' own output rather than a hand
measurement, so it travels with the artefact instead of beside it.
