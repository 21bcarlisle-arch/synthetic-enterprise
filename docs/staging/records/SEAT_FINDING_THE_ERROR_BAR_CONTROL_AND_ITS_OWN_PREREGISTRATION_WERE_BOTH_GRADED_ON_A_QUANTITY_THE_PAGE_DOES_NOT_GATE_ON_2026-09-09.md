**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — resolve the selection leg by seeds because the ranking cut already names its sign) · **Class:** controls_that_cannot_fail

# The error-bar control and its own pre-registration were both graded on a quantity the page does not gate on

**Written 2026-09-09T10:13Z, while the nine-seed floor run is still in flight.** `ps` says PID
704091 has been going 1h08m, 5 of its 27 passes are done, and
`docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json` does not exist yet. **Nothing
below is a reading of that run's output.** The correction to the pre-registration is therefore
filed *before* the answer, which is the only condition under which a correction to a prediction is
worth anything.

---

## One quantity, two graders, and neither of them is the page's

`site/data/value_arms.json` carries two different verdicts about the selection leg, and they are
computed from different numbers by different rules:

| | quantity | rule | value today | who reads it |
|---|---|---|---|---|
| **the page's gate** | `realised.split.selection_gbp` = **+£319.10** | `_resolvable`: `\|point\| > stdev` | £319.10 vs £2,291.98 → **refuses** | `generate_value_arms_data._selection_sentence`, `_leg_in_this_world` — every directional clause on the page |
| **the floor's own key** | `selection_gbp_spread.mean` = **−£426.96** | `\|mean\| > 2·SEM` | £426.96 vs £2,646.55 → **false** | **nothing rendered** |

The two point at numbers of **opposite sign**. `grep -rn distinguishable_from_zero site/` returns
the feed and one test assertion, and no page.

### Instance 1 — the site control (fixed in this commit)

`site/test_the_baseline_comparison_reaches_the_reader.py::test_the_error_bar_says_the_instrument_cannot_resolve_it`
opened with

```python
assert eb["distinguishable_from_zero"] is False
```

directly beneath a docstring whose entire subject is that this control **stopped** pinning today's
answer, because "a control keyed to a sentence goes red when the sentence improves and stays green
when the claim rots -- exactly backwards." The paragraph was right and the line under it was the
same defect one quantity along.

**It would have wedged the tree on the very result this delivery item was drawn to produce.**
`2·SEM` shrinks as 1/√n; the page's gate does not move with n at all. At n = 9 the floor's key
flips to `true` on `|mean| > 0.667 × sd` — entirely reachable — while the page's refusal, and every
sentence this test then asserts, is **unchanged**. A site red wedges every lane, so publishing the
nine-seed floor could have been the thing that stopped the nine-seed floor landing.

**The repair** keys the precondition to the page's own gate: `spread_to_point_estimate_ratio >= 1`
is exactly `_resolvable(...) is not True`, since the ratio is `|stdev / point estimate|`. It reds
the day the spread narrows past the estimate while the page still says it cannot resolve — the
claim rotting — and stays green while the page becomes more honest. `distinguishable_from_zero` is
still asserted, as the property that the producer *declares* it (a stub artefact fails) rather than
as the answer it declares.

*Proven able to fail:* poison round at 10:12Z — threshold moved `>= 1.0` → `>= 100.0`, test RED at
line 726 carrying the live value `7.182626564872851`; restored, whole file **117 passed, 1
skipped**.

### Instance 2 — the pre-registration filed this morning (corrected, not rewritten)

`SEAT_PREREGISTRATION_WHAT_SIX_MORE_SEEDS_DO_TO_THE_SELECTION_LEGS_SIGN_2026-09-09.md`, committed
`c066c114b` at 10:04:45 — thirteen seconds before the run started — states P6's falsification
condition as:

> at n = 9 the page can state a direction iff |mean| > 2·sd/√9, i.e. iff **sd < 1.5 × |mean|**. At
> the current mean of −426.96 that needs an sd below **£640**

That is the floor key's arithmetic, over the floor's mean. **The page's condition is `sd <
£319.10`** — over the point estimate, of the opposite sign. P6's published threshold is **2.007×
too permissive**.

It does not change P6's verdict *this time*: P4 predicts sd ∈ [1,200, 2,400] and both thresholds
refuse across that whole band. It is wrong anyway, and it bites in a named window — **an sd landing
in (£319.10, £640.44] scores P6 "refuted, the page now states a direction" while the page in fact
still refuses.**

## The consequence that changes a decision, not just a document

The pre-registration's §"what would actually settle it" prices the remedy at

    n = (2 · sd / |mean|)² = 116 seeds ≈ 48 hours of compute

That figure is from the same wrong rule. Under the gate the page actually applies, **the required
seed count does not exist.** `E[s] → σ` at every n; only the uncertainty in `s` shrinks. The gate
needs `s < £319.10` against a σ that three seeds put at £2,291.98 — a factor of 7.18. The chance a
sample sd lands below the threshold by luck alone, if σ really is £2,291.98:

| n | P(s < £319.10) |
|---|---|
| 9 | 1.4 × 10⁻⁶ |
| 20 | 7.8 × 10⁻¹⁴ |
| 116 | 5.5 × 10⁻⁷⁶ |

So **48 hours of compute buys 5.5 × 10⁻⁷⁶ of a chance at the answer it is being bought for, and it
should not be bought.** The live page has been saying the correct half of this unconditionally the
whole time (`MORE_SEEDS_WOULD_NOT`: *"re-drawing the dice measures this spread again, it does not
shrink it"*) — and the pre-registration cited neither it nor the ratio the same feed publishes
(`spread_to_point_estimate_ratio: 7.18`), which is the threshold, already derived, already on the
surface.

## What the nine-seed run is therefore worth — stated before it lands

It is still worth its hours, and for a different reason than the one it was commissioned under:

1. **σ at 8 degrees of freedom instead of 2.** Seed 22222 sits at 98.6% of the maximum leverage a
   three-point sample geometrically permits. Whether £2,291.98 is σ or is one draw's doing is
   unresolved and answerable, and it is the input every remedy is priced from.
2. **P5, the sign test, is untouched by any of this** — it counts seeds above zero and needs no
   threshold.
3. **`_sign_determined` becomes an independent branch for the first time.** `generate_value_arms_data`
   records, by exhaustion, that at n = 3 and n = 4 "every member of a zero-straddling family
   exceeding its own sample sd" is arithmetically impossible, so the field can only fire where
   `stable` is already False. At n ≥ 5 it can fire alone. A nine-seed floor is the first artefact
   for which that is true, so a `no_sign` clause appearing on the page after publish is the branch
   working, **not a regression.**

What the run **cannot** deliver is a stated direction, and that was true before it started.

## What is next

- **Do not commission the 116-seed run.** The remedy for the selection sign is a lower-variance
  estimand, or the `method_skill.fixed_horizon` cut standing on its own evidence — not more dice.
  Both are open work and neither is this item.
- **Publish the nine-seed floor when it lands** (~15:45Z on the current pass rate) and let
  `_resolvable` rule, exactly as the delivery item says. Expect the refusal to stand; the
  publishable result is §"what the run is worth" above, on the surface and not in a footnote (R12).
- **Grade P1–P5 and P7 as written.** Grade **P6 against £319.10**, not against £640.44, and record
  that the threshold was corrected before the figure existed.
