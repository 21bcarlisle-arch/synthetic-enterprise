**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# What the live-world bound makes the page say

*Delivery seat, 2026-09-03, lane-0, claim `the-baseline-was-beaten-in-a-world-that-no-longer-exists`.
Written at 12:5xZ while `se-noise-floor-all-20260903b` is still running and
`value_cycle_ab_s1_noise_floor_20260903.json` does not exist. The sibling pre-registration filed P6
and P7 on the floor artefact's own keys; this one is about the figure the PAGE states, which is a
different contrast, and it is filed because wiring the bound in without predicting its verdict first
would leave the verdict ungradeable.*

---

## 1. A correction to P7, made before its answer is in hand

P7 reads:

> The live-world `value_advantage_gbp` is **£2,335.87**. Against a live-world floor near £5,923 that
> is 0.39× — comfortably inside.

**£5,923.04 is the spread of `selection_gbp`. £2,335.87 is `value_advantage_gbp`.** Those are two
different contrasts, and their ratio is not a quantity — it is this project's most-recorded
publication defect, committed inside the sentence that was warning against committing it. The two
contrasts are not interchangeable and never have been: on the same 2026-08-29 seed family they
differ by 2.6× (`value_advantage` 990.45, `selection` 2,577.80), which is why
`_seed_spreads`/`_spread_for` key every bound to its own contrast.

P7's *stated claim* — `selection_distinguishable_from_zero` stays false — is about the floor
artefact's own key on its own contrast and stands unaffected. Only the arithmetic offered as its
support is withdrawn. **P7 is graded on its stated claim, not on this sentence**, and this
correction is recorded here rather than by editing P7, because a prediction edited after it was
filed is not a prediction.

## 2. The basis

Same-world all/only/except triples, per contrast, `stdev_gbp` at n=3:

| world | contrast | `all` | `only` | `except` | (only²+except²)/all² |
|---|---|---:|---:|---:|---:|
| 2026-08-29 | `value_advantage_gbp` | 990.45 | 414.85 | 554.21 | 0.489 |
| 2026-08-29 | `selection_gbp` | 2,577.80 | 2,092.29 | 0.21 | 0.659 |
| **live (39a192ce)** | `value_advantage_gbp` | *pending* | **991.46** | **0.00** | — |
| **live (39a192ce)** | `selection_gbp` | *pending* | **5,923.04** | **0.00** | — |

If the legs partitioned the variance exactly, `all` would equal `sqrt(only² + except²)` — £991.46 for
`value_advantage` in the live world. They did not partition exactly in the one world where all three
have been measured: the observed ratios of 0.49 and 0.66 mean `all` came in **wider** than the
partition sum by 1.23×–1.43×. The decomposition artefact's own reading says a ratio between roughly
0.3 and 3 is what n=3 alone produces, so this is sampling noise and not a structural finding.

> **P8 — the undecomposed leg's `value_advantage_gbp` spread.**
> **Predicted:** `stdev_gbp` between **£990 and £1,450**, central estimate **£1,150** — the live
> `only` leg's £991.46, widened by the 1.0–1.43× the 2026-08-29 triple showed.
> **Refuted if:** outside **£600–£2,400**. That band is deliberately wide: at n=3 a standard
> deviation carries 2 degrees of freedom and roughly ±50% of itself, and a narrow band here would be
> false precision dressed as rigour.
> **Direction, stated plainly:** the live-world bound on this contrast is predicted to be
> **less than half** the old world's £2,291.07.

## 3. The verdict, and it is the flattering one

The page's rule is `_resolvable`: a contrast clears when `abs(value) > stdev` **of the same
contrast**. £2,335.87 against a predicted £990–£1,450 clears it.

> **P9 — the current-world contrast RESOLVES, and `resolved` becomes `True`.**
> **Predicted:** once `value_cycle_ab_s1_noise_floor_20260903.json` lands and is wired in,
> `current_world.bound_available` becomes `True` and `current_world.resolved` becomes **`True`** —
> the per-customer advantage of £2,335.87 clears its own live-world seed spread.
> **Refuted if:** `resolved` comes back `False`, which needs `stdev_gbp` ≥ £2,335.87 — inside P8's
> refutation band but above its predicted one, so P8 and P9 can fail independently.

**THIS IS THE FLATTERING DIRECTION AND THAT IS WHY IT IS WRITTEN DOWN HERE.** The direction for this
claim says: *"A result that moves the advantage the flattering way, unpredicted, is a defect in the
re-run and not a win."* So it is predicted, before the artefact exists, with its mechanism named:
the advantage did **not** grow — it collapsed from £12,071 to £2,336 — and it is predicted to clear
only because the *bound* is predicted to collapse further, from £2,291 to about £1,150. **A smaller
advantage that resolves is a smaller claim, not a bigger one**, and the page must not be allowed to
read as though the company got better. What improved is the instrument's resolution in a world where
fewer households leave, so each seed re-draw moves the book less.

**What would make me distrust a `True` here:** a bound below about £600 — that would be the
instrument losing variance it should have, not gaining precision, and P8's lower refutation bound is
placed there for that reason rather than symmetrically.

## 4. Constraints on the wiring, registered before it is written

- The bound for `value_advantage_gbp` is the seed spread of `value_advantage_gbp`. **No cross-contrast
  pairing**, which is §1's defect in code form.
- Admission is on the floor's **world digest** AND its **`redraw_scope.mode == "all"`**. The `only`
  leg is live-world and on disk now; admitting it would publish the wrong leg's spread, which is the
  precise move the sibling pre-registration calls *"the same move as quoting the old world's floor
  because it is the one on disk"*.
- A run that dies and leaves a refusal stub at `--out` must not be read as a floor: a floor needs a
  `generated_at` and at least two seed rows.
- **`resolved` stays `None`, never `False`, whenever no live-world `all` floor is present.** "Not
  measured" and "measured and did not clear" are different states and only the second is a verdict.

## 5. How this is graded

When the leg lands: rebuild the feed, read `current_world.bound_available`, `resolved` and the spread
it used, and record the outcome **beside** P8 and P9 above, refutation kept. If the leg OOMs again
and writes nothing, that is recorded here as *ungraded*, not as either answer.
