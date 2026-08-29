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
