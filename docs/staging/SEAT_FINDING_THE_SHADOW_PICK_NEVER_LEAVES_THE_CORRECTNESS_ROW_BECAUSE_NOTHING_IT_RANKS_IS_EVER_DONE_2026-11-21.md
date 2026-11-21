**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 5 · **Atom:** `unminted`

# The shadow pick never leaves the correctness row, because nothing it ranks is ever done

*Delivery seat, 2026-11-21, building `retire-the-maturity-map-dials-from-the-draw-at-cutover`.*

**What was read.** The live side-by-side log (`docs/observability/.work_items_shadow.jsonl`,
shared tree): 484 draws, 2026-11-20T13:42 to 2026-11-21T09:28. All 484 picked the `correctness`
row, and every one of them gives the reason as "0 of 0 landed this week".

**Why.** D6 step 3 ranks rows by `shares[row] - landed[row]/total`, counting items whose `state` is
`done` with a `closed_at` this week. In shadow every item is DERIVED (staging findings, and since
this commit the map's atom steps), and a derived item is never `done`. So the total is always 0,
every deficit equals its share, and the largest row that has a candidate wins: correctness at 42%.
This happens on every draw, while any correctness finding is open.

**What it costs.** The day side by side (D9 step 2) cannot show the share table working. In
particular, the atom steps this commit adds to the shadow (`maturity_map: shadow`) will be ranked
but never picked, so the log cannot yet show the share table replacing the retired dials. A
low `ladder_names_pick` count measures this artefact, not a disagreement between the two draws.

**Not the fix to make silently.** Two shapes are possible, and they have different consequences:
(a) in shadow, count landings from the commits that `delivery_lane --landed` binds, mapped to a
row; (b) accept that the share deficit only becomes live at cut-over, when items are written and
closed, and state that on `--compare`. Erring against our own thesis, (b) is the honest default
until (a) is built: the comparison should say "the deficit is inert in shadow", not report a
share result that rests on 0 of 0.

**Done means.** `--compare` either reports picks across more than one row on a real day, or it
prints, by name, that the deficit is inert because no item is done.
