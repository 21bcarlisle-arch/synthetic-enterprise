# The QEP refit lands with its arms, and its floor is refused as a different book on one churn-counted field

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `land-the-qep-refit-once-the-one-process-floor-finishes` (Lane 0 delivery)

## Premise, re-measured at draw

`longjob-qep3-arms-floor` was `inactive` at 10:53Z. Its artefact
(`value_cycle_ab_s1_noise_floor_20261004r.json`, 08:48Z) parses and carries no `floor_run_refused`.
Both it and the three-arm name producing commit `96517e68c` and world `cdba75ebb9197b33`, the same
digest `world_level_identity()` returns with the refit applied. The duplicate claim the draw named is
this item's own id, written by the draw itself. The only other process on the subject was this seat.

## What landed (one commit, the shape of `c3939e7b1`)

- The refit patch from `/var/tmp/se-qep-arms2`, applied cleanly at origin `d8f4f2de2`. Its three
  `simulation/`/`company/` blobs are byte-identical to the files the run imported.
- `test_a_refuted_commons_artefact_cannot_quietly_become_current.py` is retired with its subject.
- The six verdicts are regenerated on G. Rung 1 still reads 0 of 6 years in band, worst −8.49pp
  (was −9.2pp), so its shape is unchanged.
- `CURRENT_WORLD_*_PATH` → `20261004r`, `site/data/value_arms.json` regenerated, and
  `CURRENT_WORLD_CHANGED_SINCE_THE_LAST_READING` rewritten. It says this is a different world, with
  about forty commits between the readings, and attributes nothing.
- Three exemptions in `value_arms_substrate_exemptions.json` cover the refit's own paths, keyed to
  the blobs this commit carries.
- 11 controls re-keyed. 4 site rungs read the committed feed, which now carries the regenerated copy.
  4 fixtures (a mirror, a creation-leg withheld subject, and two floor-code helpers) stamp the live
  digest onto their pinned pairs, the way `c3939e7b1` did, because the world is incidental to what
  they test. The undriven-pointer recipe for `_against_the_panels_figure` also opens
  `_realised_book_pairing`.

## What the page says now: nothing about the current world's sign, and it says so twice

1. **Not HEAD's code.** Seven paths moved on origin after `96517e68c`. No exemption covers them, and
   none was argued, because they are real staleness: `collections_journey`,
   `payment_observation_consumer`, `payment_plan`, `sim_interface`, `default_belief`,
   `plan_offer_response`, `run_phase2b`. The currency claim is withdrawn and the measurement stays.
2. **No bound.** `_realised_book_pairing` refuses the floor as a different book from the arms.

## The finding: the refusal rests on the one field its own docstring says moves with churn

| field | floor (3 seeds) | control | value | level |
|---|---|---|---|---|
| billing_accounts_settled_in_window | 127..127 | 127 | 127 | 127 |
| with_an_electricity_leg | 111..111 | 111 | 111 | 111 |
| with_a_gas_leg | 64..64 | 64 | 64 | 64 |
| dual_fuel | 48..48 | 48 | 48 | 48 |
| **accounts_at_end_of_window** | **42..42** | **44** | 56 | 50 |

Four of the five fields agree exactly. That is the evidence the guard's docstring uses for "same
book". The disjoint field is the VALUED subset at the window's edge, which depends on who churned.
In the 1002c pair the floor's 40 equalled the control arm's 40 by coincidence, so the guard was never
tested on a near miss.

Two things about the floor are odd, and I cannot yet say which explains it:

- **The floor reads 42 on all three seeds**, although it re-draws every household's elasticity. A
  re-draw that moves who churns should move this count. In the `next12` family it moved 54..55.
- **The floor sits BELOW the control arm.** If the floor re-draws the value arm or the control arm,
  its own seed-11111-equivalent should land on 44 (control) or 56 (value).

Explanations, ranked by evidence:

1. **The floor runs a different arm configuration from the three-arm's control.** It might be
   without the level arm, or under a different campaign memo (`e825975e8` keys the memo on what
   shapes the book). Four identical fields and one shifted one fit this.
2. **This count is insensitive to the elasticity re-draw in this world.** `bf0d37c2f`'s debt
   objection and the collections journey might dominate who leaves, which would make the seed-flat
   42 real.
3. **The guard is right and these are different populations.** That does not fit four
   exactly-equal settled counts.

**Prediction, filed before measuring:** the floor's seed rows will show the floor's base arm is the
value or level arm under a `--redraw-mode all` code path that skips one end-of-window filter the
three-arm applies. If so, explanation 1 holds and the guard should compare like-for-like arms
rather than floor-vs-all-arms.

## Next

Hand-off `the-20261004r-floor-book-mismatch-is-explained`. Read the floor's per-seed rows and the
noise-floor code path for which arm it drives. Establish which explanation holds before touching
`_realised_book_pairing`.
