**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `B10_competitor_switching_response`

# Preregistration: what the two floor legs must show, and what to do when they land

**Filed 2026-08-29 21:46, before the legs finished.** Landed in `5cf66b5ba`. The full arithmetic,
the price table and the prediction are in
`docs/observability/value_arm_floor_decomposition_prediction_20260829.md` — this file exists so the
next seat picks the result up instead of leaving it in `/tmp`.

## What is running

```
systemd-run --user --unit=vcab-floor-legs      # launched 21:46:43, ~3h, log /tmp/vcab_legs.log
```

Two legs of `tools/run_value_cycle_ab.py --noise-floor-seeds 11111,22222,33333`, full window, one
process, sequentially:

| leg | writes |
|---|---|
| `--redraw-mode only` | `docs/observability/value_cycle_ab_s1_noise_floor_only_20260829.json` |
| `--redraw-mode except` | `docs/observability/value_cycle_ab_s1_noise_floor_except_20260829.json` |

then `--decompose` over those two, the published `..._noise_floor_20260829.json` and
`..._s1_three_arm.json`, writing `docs/observability/value_cycle_ab_floor_decomposition.json`.

## The prediction, on the record before the answer

1. **The priced side is the SMALL half** — under the 50.4% threshold, so
   `larger_settled_book_would_resolve_it` returns `false` and the arm comparison cannot be resolved
   at any book this world can legitimately produce.
2. **The reconciliation lands inside 0.3–3.0×.** Outside that the two legs are not two halves of
   one thing and NOTHING is published from them — the finding is then about the legs.
3. **`share_is_decisive` is true.**

If (1) is wrong the page gets its remedy back with the price stated, and the prediction stays in the
record beside the result saying I called it the other way.

## STATE AS OF 2026-08-29 23:55Z — read this first

The `only` leg landed at 23:07Z; the `except` leg is still running and is expected around 00:28Z.
Two commits are in against this (`fcc6a90f9`, `c02c8c86c`) and **the only thing outstanding is the
reconciliation and the publish**. What is already settled, so it is not re-done or re-argued:

* **Prediction (1) is REFUTED and marked as such** beside its own number in
  `docs/observability/value_arm_floor_decomposition_prediction_20260829.md`. The priced side is the
  **LARGE** half: sd 2,092.29 against 2,577.80 undecomposed = **65.9%** against a 50.4% threshold.
  The prose that read as agnostic is marked too. **Do not re-open this; do not soften it.**
* **The reconciliation target is filed in advance**: the `except` leg's `selection_gbp` stdev must
  come out near **£1,505.78**, pass band roughly **£930–£2,190** (the prereg's 0.3–3.0× on the
  ratio). Written before the leg landed, so it is a prediction. Record the result beside it either
  way.
* **The denominator is named.** 10 accounts = the independent draws and the only sample size;
  20 = decisions (2.00/account, sharing one draw); 90–103 = call sites, because
  `price_elasticity_for_customer` is a pure function of `(customer_id, seed)`. The multiplier is
  invariant (**4.25×**); the counts are not. `remedy_price_table` now derives both counts from the
  multiplier and every row names its `independence_unit`. The table is reprinted in the
  observability note.
* **The n=3 caveat is wired into the consumer.** The split will clear `share_is_decisive` by
  **0.005** (0.1550 vs a 0.150 bar), so the page's price now carries the seed count and that
  distance automatically. Nothing further is needed to satisfy "with its n=3 caveat".

**What is left, in order.** (1) `python3 -m tools.run_value_cycle_ab --decompose <all> <only>
<except> <three_arm>` per the step below. (2) Check sd(except) against £1,505.78 and the band —
**if it falls outside, publish NOTHING from the legs and the finding is about the legs.** (3)
`python3 -m tools.generate_value_arms_data`; the remedy branch flips on its own. (4) Commit the
except leg artefact, the decomposition artefact and `site/data/value_arms.json` by pathspec.

**Launch long jobs with `systemd-run --user --unit=`.** A `nohup`'d `surgical_land` was killed with
this tick's cgroup and reported exit 0 while landing nothing; HEAD was unchanged. That cost one
cycle here.

## What to do when the unit exits

1. `systemctl --user is-active vcab-floor-legs` → inactive, then read the tail of
   `/tmp/vcab_legs.log` for the printed decomposition. **A leg that RAISED is a result, not a
   failure to retry:** `re-drew NO household` means the priced roster matched no elasticity call
   and the id convention moved.
2. `python3 -m tools.generate_value_arms_data` — the headline's remedy clause is derived from the
   decomposition artefact and will change branch on its own. Nothing else needs editing.
3. Commit the two leg artefacts, the decomposition artefact and the regenerated
   `site/data/value_arms.json` by pathspec, then
   `python3 -m background.delivery_lane --landed grade-the-pages-own-escape-clause-before-spending-two-hours-on-it`.
4. Write the outcome next to the prediction in the observability note — **beside it, not over it.**

## What this settles for the queue behind it

The lifted-budget re-run that three directions have queued behind "a larger settled book" should
not launch until this returns. If (1) holds, that run buys nothing: every priced decision on this
book belongs to the static roster and not one to a drawn `SYN-*` household, so more drawn
households add churn cascade — the half of the floor that never shrinks — and no priced decisions
at all. **The lever is a product, not a size.**
