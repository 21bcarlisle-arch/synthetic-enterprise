**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The roster price is bounded at its producer — the FOURTH instance — and the drawn item was spent

**Severity note:** the unbounded count this claim names was live on the published feed and on the
capabilities page, and is now withheld with a named reason, with the withholding rendered to the
reader and proved against the published bytes. No instrument in this area is left untrustworthy by
this document: the fourth instance identified by 964036259 is the one closed here, and the residue
it leaves is a readability defect named under "Filed, not fixed" below.
**Filed:** 2026-09-22, delivery seat.
**Claim:** `the-producer-still-writes-an-unbounded-seed-count-into-every-artefact-it-draws`
**Pre-registration:** `docs/staging/records/PREREG_BOUNDING_THE_ROSTER_PRICE_AT_ITS_PRODUCER_2026-09-22.md`

---

## First: the drawn item's premise IS SPENT, and that is recorded rather than re-worked

The item asked for the census of `seeds_needed_to_state_a_sign`'s readers and the bound at its
producer, `run_value_cycle_ab.distance_to_a_sign`. **That landed as 964036259**, which is an
ancestor of `origin/main`, two commits behind this turn's base. I re-measured rather than trusting
the draw's own note:

* `distance_to_a_sign` publishes `seeds_needed_to_state_a_sign` gated on `clears_bar`, with
  `seeds_at_the_point_estimate`, `seeds_needed_interval` and a named withholding beside it —
  verified by reading the function, not the commit message.
* The test the item said must be kept, and feared would be deleted, exists:
  `test_the_seed_count_and_the_published_verdict_are_the_same_inequality`, re-pointed at the point
  estimate so it spans the whole partition.
* The item's duplicate-work note was right: the id was already held. The work under it was done.

**So the drawn item bought nothing.** What it bought instead is below: 964036259's own census
**filed a fourth instance and did not fix it**, and that was live on the feed until this commit.

## The fourth instance, which is what this turn actually did

`tools/generate_value_arms_data._rosters_to_state_a_sign` published
`rosters_needed_to_state_a_sign` as a bare integer — **live on `site/data/value_arms.json` as `4`**,
and rendered on the capabilities page as *"Price of a sign — about 4 independent rosters"*.

It is `ceil((1.96 / |sds_from_chance|)^2)`. `sds_from_chance` is `(auc - 0.5) / null_sd`: an
estimate, in the denominator. It is asked only where the reading has failed `clears_its_own_null`,
which IS the statement that the denominator's interval at that bar covers zero. A denominator that
may be zero gives a quotient with no upper bound. **4 is the worse number to publish**, for the same
reason 1,744 was in 5742edb1c: it is small enough to read as a cheap, costed, considered answer.
The live reading sits 1.084 null SDs from chance against a 1.96 bar — it fails its own null, so the
count was being quoted in precisely the state where no finite count exists.

This is **the fourth instance of one rule**: 06e316ae4 (page key), 5742edb1c (second page key),
964036259 (money-leg producer), and now this. The VAT shape CLAUDE.md names.

## The census, run first and in full, as the direction asked

Seven sites hold the name. **None re-derives the value; every one copies it** — which is why
copying is again what stopped.

| Site | What it is | Disposition |
|---|---|---|
| `generate_value_arms_data.py:2695` `_rosters_to_state_a_sign` | THE PRODUCER | bounded here |
| `generate_value_arms_data.py` prose builder | copies it into a sentence | withholding branch added |
| `site/capabilities/index.html` render | copies it into the panel | withholding branch added |
| `site/data/value_arms.json` | the artefact on disk | regenerated |
| `tests/tools/test_generate_value_arms_data.py` monotonicity leg | asserts price falls with distance | KEPT, re-pointed at the point estimate |
| `site/test_the_baseline_comparison_reaches_the_reader.py` fixture | CONSTRUCTED feed, clearing state | untouched and still green |
| `generate_value_arms_data.py:430` | a comment | no action |

## What is published instead

The rule `_seed_price_interval` established, in this leg's own unit: an integer **only** where the
reading clears its own null — where the count is at most the one roster in hand — otherwise `None`,
a named withholding, and `rosters_needed_interval` carrying the arithmetic and the two endpoint
prices one exact null SD either side. The arithmetic is renamed, not deleted:
`rosters_at_the_point_estimate` carries it in **both** states.

**One difference from the money leg, stated so it is not read as an oversight.** The money leg's
error is `sd/sqrt(n)`, estimated from the same draws, so its bar is a t point that widens with `n`.
`null_sd` here is `sqrt((n1+n2+1)/(12*n1*n2))` — exact, estimated from nothing. So the error unit is
exact, the bar is the normal point, and the denominator's interval is `sds_from_chance ± 1` in
standardised units. The gate is keyed to the same inequality the artefact's per-seed verdict
publishes, so the two cannot drift.

## Pre-registered, then measured. All eight held.

Filed before the change:
`docs/staging/records/PREREG_BOUNDING_THE_ROSTER_PRICE_AT_ITS_PRODUCER_2026-09-22.md`.

| | Prediction | Result |
|---|---|---|
| P1 | live count `4` → `null` | held |
| P2 | `rosters_at_the_point_estimate` carries `4` | held |
| P3 | endpoints 545 and 1, in the opposite order to the bounds | held |
| P4 | the "at its own sign bar" wording, not the bare one | held |
| P5 | monotonicity leg reds with `TypeError`, not an assertion | held exactly |
| P6 | the site render test stays green **unedited** | held |
| P7 | prose stops saying "about 4 independent ROSTERS" | held |
| P8 | bare unbounded roster counts on the feed: 1 → 0 | held |

P3 is the evidence the quantity diverges rather than interpolates: **545 against a point estimate of
4**, from a denominator moved one exact null SD. P4 is worth naming — this family's *one-error*
interval [0.084, 2.084] does **not** contain zero, but its interval *at its own sign bar* does, so
the conditional wording had to fire the second way. A bare "contains zero" would have been false.

## The rendered page, which is what done means

Against the **published (index) bytes** — the door reads the index by design, not the working tree,
and rendering before staging asked the old feed and read as a no-op:

> **The price of a sign cannot be stated for this reading.** NO ROSTER COUNT IS PUBLISHED FOR THIS
> READING AND NO LARGER ONE WOULD CHANGE THAT. […] At the point estimate the arithmetic returns 4;
> one exact null SD either side of the distance it returns 545 and 1. […] **Neither leg of this
> comparison carries a price.**

`about 4 independent rosters` is gone from the rendered page.

**The `NEITHER LEG` branch is the right reading and it is new.** Both legs of that sentence are now
withheld — the money leg already was, after 964036259. The prior text said *"The rank question is
costed and the money one cannot be"*, which **became false** the moment this leg was bounded. A
remedy sentence elsewhere on the page going false when a neighbouring estimate is repaired is a
shape this project has paid for before; it was caught here by reading the branch, not by a test.

## The control, mutation-proven on six mutations

`test_MUTATION_the_roster_price_is_published_ONLY_where_its_denominator_excludes_chance` asserts the
partition is **inhabited on both sides before it asserts anything about either** — a gate that
withheld everything would otherwise satisfy every withholding leg and read in the log exactly like
the mechanism working (CLAUDE.md's rare-branch trap).

Three mutations (`clears_bar := True`, `:= False`, and republishing the count unconditionally) all
fire on the partition leg. **That is the flattering reading on its own** — one leg catching
everything means the downstream legs might be unreachable — so three further mutations were run that
keep the partition inhabited and break one downstream claim each. Each fired, on its own leg, with
its own message: withholding loses its reason; the interval's point estimate drifts from the block's;
the clearing state still carries the unbounded interval. The tree was restored and byte-compared.

## Filed, not fixed

`rosters_needed_unavailable_because` and the money leg's `seeds_needed_unavailable_because` both
name their sibling field in backticks, so the literal JSON key `rosters_at_the_point_estimate`
renders on the page inside backticks. This leg matches the money leg's existing published behaviour
rather than diverging from it mid-repair. It is a readability defect of the **class**, in two places,
and belongs in one change that fixes both.

## Evidence

459 passed, 1 skipped across `tests/tools/test_generate_value_arms_data.py` and
`site/test_the_baseline_comparison_reaches_the_reader.py`.
