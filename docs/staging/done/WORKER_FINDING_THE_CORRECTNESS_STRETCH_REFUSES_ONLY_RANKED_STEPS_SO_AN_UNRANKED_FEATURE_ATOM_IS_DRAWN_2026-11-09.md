**Severity:** LATENT · **Lane:** E_finance_treasury · **Epoch:** 3 · **Atom:** `G15_forward_curve_series_to_backtest_hedging_by_physics`

# The correctness stretch refuses only atoms in ranked steps 6-13, so an unranked feature atom is still drawn to BUILD (2026-11-09)

**Found by.** The worker tick at about 11:15 GMT on 9 Nov. The BUILD lane drew
`G15_forward_curve_series_to_backtest_hedging_by_physics` (lane E, dial 45, level 0 to 3) while the director's ruling
`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md` was still open.

## What it is

The ruling says: "No new feature work is drawn until the steps below are done." The ruling names the forward years, the
asset world and advice as examples. `priority_order.yaml` encodes the ruling as `correctness_stretch.ahead_of_steps:
[6..13]`. `supervisor.correctness_stretch_refusals` refuses only the atoms listed in those steps.

Measured at f10a33894b:

- `correctness_stretch_refusals()` refuses **4 atoms** (EP16, SPINE_1, C4, W1_10). Steps 8 to 13 list no atoms.
- **79 of the 102 live atoms are in no step at all**, and that includes 28 at `loop_stage: build`.
- `_follow_the_priority_order` returns the unordered set unchanged when no ranked candidate survives the earlier
  filters. So once steps 1 to 5 have nothing drawable, the stretch holds nothing back from the BUILD primary.

G15 is plainly feature work. Its own map note says: "RANKED BELOW STAGE 1 ... no use case is built until the world and
billing are done, so this buys the ability to TEST later, not to build now." It also needs a delivery axis that
the published Ofgem forward does not carry (101aa40485).

## What this tick did

It did **not** build G15. It held the atom on the ruling's own words and wrote this finding. That decision is
reversible: a later draw can build G15 once `exit_met` is recorded.

## Recommendation (for the seat; a sequencing call under the 15 Oct delegation, not the director's)

Add a `holds:` list to `correctness_stretch` and have `correctness_stretch_refusals` refuse those ids as well as the
ranked steps' atoms. Seed it with G15 and the other unranked use-case pulls that sit at `build`. Do **not** refuse every
unranked atom. Many of the 79 are correctness and harness work that the stretch needs, so a blanket refusal would
starve the draw and break Rule 0. The control is one assertion: a `holds` id is refused while `exit_met` is unset, and
the same id is drawable once it is set.

Until then, expect G15 to be drawn again on later ticks. Each one should hold the atom the same way and cite this file.

## Done (2026-11-09, worker on the seat's Lane 0 call)

`correctness_stretch.holds` in `docs/direction/priority_order.yaml` names seven atoms in no step, each with a
one-line reason, and `supervisor.correctness_stretch_refusals` refuses them while `exit_met` is unset (live:
4 refusals became 11). Held, on the test "builds a new capability and corrects nothing already in a book": G15,
A50, A51 (the use-case programme), B8 (a retention holdout), and W1_14, W2_18, W2_19 (asset-world phase 1,
which is step 8's subject). Deliberately NOT held: W3_3 (it is in step 4 and corrects a cost basis), W2_21
(it corrects implausible joint draws already in the book), D46, W2_30, W2_40, W1_6b, W1_29, DD_seasonal and
every harness/site atom. The control is
`test_a_held_unranked_atom_is_refused_until_the_exit_and_an_unheld_one_never_is`; dropping the holds loop
reds it and the live-read test.
