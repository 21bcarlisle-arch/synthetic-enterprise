# WORKER FINDING — the mirror's fidelity gate was denominated in kW/K; the verdict it guards is denominated in GBP

**Severity:** LATENT · **Lane:** H_harness

**Atom:** `H_GAP_fabric_belief_truth_gap` (lane H_harness, level 2, loop_stage build)
**Date:** 2026-08-11 · **Expert Hour #3 on this atom's caveat machinery**
**Status:** CLOSED as a MECHANISM. Level stays 2 per the atom's own termination condition.

## The question this Hour was told to start from

The previous Hour's record ended: *"the next Hour starts by asking what
`panel_mirror_register_infidelity` is a ratio OF."*

It is a ratio of

```
|mean_i|register_i − truth_i|_after  −  mean_i|register_i − truth_i|_before|
────────────────────────────────────────────────────────────────────────────
                  mean_i|register_i − truth_i|_before
```

— a **difference of two aggregates**, divided by one of them. Three things follow, all
measured, none of them what the term is named after.

## Leg 1 — the numerator is preserved by algebra on the only branch either population takes

`_reflect_level` is `2*prior − value`, so every premise's `|register − truth|` is
algebraically identical after reflection. Measured: `|Δmean|` = **0.000e+00** (authored 15)
and **1.4e-18** (drawn 200, float noise). Infeasible premises: **0 of 15, 0 of 200** — so the
log-fallback branch, the only branch on which the term can be non-zero, never fires on either
published population.

The previous Hour anticipated the objection and answered it by computing the quantity from the
built panel rather than assuming it. That does not help: **measuring an algebraically-zero
quantity does not make it failable.** The gate was a constant PASS.

## Leg 2 — even on the fallback branch the shape is wrong

`|mean(e′) − mean(e)| ≤ mean|e′ − e|`, with equality only when every breach shares a sign.
Under the log fallback each premise's error scales by `register/truth` — **below** one where
the register under-states, **above** one where it over-states — and both published populations
are mixed-direction (the register over-states on 1 of 15 authored, **74 of 200** drawn). So the
breaches cancel.

Measured on a real 20-premise subpanel of this atom's own drawn population:

| | value |
|---|---|
| shipped term (difference of means) | **4.36%** — inside the 5% band, "faithful" |
| the promise, measured per premise | **44.51%** |
| understatement | **10.2x**, in the passing direction |

## Leg 3 — the dimension the mirror actually moves is not in the term, and it is the one the verdict is denominated in

The gate guards `panel_mirror_money_favours`, a comparison of forgone GBP. `money_consequence`
is built on `annual_heat_kwh` — through both arms and through the actionability test. The
mirror rescales every premise's `annual_heat_kwh` by `truth′/truth`:

* drawn 200: **0.151x to 9.518x — a 62.9x spread**

To separate the mirror's *signal* from this *re-composition*, build the mirror's own null:
take the mirrored row's heat, keep the original truth and both beliefs. Every premise's
register error is then identical to the unmirrored panel — **there is no sign flip in it at
all** — so anything that moves is the weight channel alone.

| | forgone epc | forgone inferred |
|---|---|---|
| base | 4,125,796 | 3,376,166 |
| **weight-only null (no signal)** | 4,695,016 (**+13.8%**) | 4,037,974 (**+19.6%**) |
| mirror | 4,705,917 (+14.1%) | 4,048,875 (+19.9%) |

**~98% of the mirror's money movement is re-composition.** Meanwhile the gate read
`register-arm error disturbed 0.0000%, attributable=True`.

Neither the mirror nor the null flips the ranking on either population, so **no published
ranking was wrong**. What was wrong is the attributability claim: a no-flip from an instrument
that applied almost no signal to the deciding quantity is not evidence of no composition
effect — which is the exact reading `panel_mirror_is_attributable` exists to prevent.

## Mechanised

* `_register_mad` — mean **per-premise** disturbance. Cannot cancel. It is the gate's numerator.
* `weight_null_panel` — the null above. A harness instrument, never published as a world (the
  same kind of object as the existing `mirror_decision_confidence`).
* `panel_mirror_weight_artefact` — the null's share of the mirror's movement in the deciding
  margin. Zero corner **split**: nothing-moved-anywhere is 0.0 (robust), but a mirror whose net
  zero is a large re-composition and a large sign flip annihilating is `inf`. A first cut
  returned `inf` for both and called a perfectly faithful identity mirror unattributable — the
  suite caught it.
* `panel_mirror_is_attributable` reads **both** dimensions.
* `_why_unattributable` names **every** reason that fired, and raises if the gate is red with
  no reason — the gate and its disclosure cannot come apart. Without this the row would have
  printed *"the mirror moved the register arm's own error by 0.0%"* as the ground for
  INCONCLUSIVE on both published populations.
* INCONCLUSIVE is raised only where there is a **decisive** money headline to protect; on a
  `neither` verdict the sentence was literally *"did NOT move the money verdict off neither"*.

**R15: six source mutations, each firing its own named test, md5 byte-clean restore.** The
gate is failable both ways — it passes on a panel where the sign flip does the work
(`test_the_WEIGHT_ARTEFACT_GATE_CAN_PASS_so_it_is_not_an_ALWAYS_RED_DETECTOR`), so it is not
an always-red detector.

**No published figure moved:** gap 0.4269 / 0.4042 re-taken on the row's declared population.
Both published populations now correctly read INCONCLUSIVE (weight artefact 91.5% authored,
100% drawn at 28.62 p/kWh; 90% at the ledger's 7.4 p/kWh).

## R10 CLASS

**A fidelity term must be denominated in the unit its consumer's verdict is denominated in.**
A control that certifies a GBP ranking by measuring kW/K is not a weak control, it is a
control over a different subject — and it will read as rigour for exactly as long as nobody
asks what its ratio is a ratio of. Companion to the standing class *a fidelity term shaped as
a ratio measures its denominator*: this is the same defect one level out, in the **units**
rather than in the **algebra**.

Sibling class, from the same Hour: **a promise made per element cannot be audited by a
difference of aggregates** — the breaches are allowed to cancel, and on any mixed-direction
population they do.

## Termination condition (unchanged in form, still falsifiable)

An Hour on this caveat machinery that finds nothing NEW moves the level; one that finds
something lands the finding and the level stays. **Three consecutive Hours have now found the
same family — a disclosed number that is not the quantity it is named after.** The next Hour
starts on `panel_mirror_normaliser_drift` and the two `_favours` materiality thresholds: ask
what population each is a property of, and whether `VERDICT_MATERIALITY` — which decides
"neither", and therefore decides whether any of this machinery speaks at all — has ever been
measured against anything.
