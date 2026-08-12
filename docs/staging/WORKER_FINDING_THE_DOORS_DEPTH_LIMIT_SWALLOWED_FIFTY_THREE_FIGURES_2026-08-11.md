# WORKER FINDING — the door's depth limit swallowed 53 published figures

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-11, H27 Expert Hour #18 (worker tick, `H27_payment_belief_gap` 2→3 HARDEN draw)
**Class:** a repair reintroducing its own defect one level down · **Disposition:** mechanism landed on the door
**Answer to the draw:** still **L2**. Eighteen Hours, eighteen defects.

## The lead, and what pulling it found

Hour #17's lead 1 (atom D35): *"the sweep stops at this process's edge. It sees only strings this
module's own `score_triad` returns. The same five figures are re-rendered by `measure_and_write`
into `coupled_gap_ledger.json`, by the dashboard and by the Proof-door page — writers this sweep
never runs. Whether any of those renders at a precision the epsilon does not know about has not
been measured."*

It has now been measured, on the rendered pixel. **The precision question is answered and it is
negative.** The walk to get there found something else.

## Half one: the precision answer, measured and NEGATIVE

Driving the real payload (`tools/generate_proof_data.py::_coupled_gaps` off the live ledger)
through the page's own JavaScript, and looking for the ledger's own detection figure
(`0.0859375`) in the rendered row at every precision from 1 to 17 dp:

```
 3dp  '0.086'   <div class="gap-val">   -- the door's headline number, fmtGap()   UNDECLARED
 4dp  '0.0859'  "detection balanced error 0.0859" in the note -- format_detection_summary, DECLARED
 1dp  '0.1'     rejected: five occurrences, none of them this figure (the discrimination rule)
```

**No downstream writer renders any of the five figures FINER than declared.** The one undeclared
downstream render — the Proof door's own headline, `fmtGap` at 3dp — is *coarser* than the declared
4dp, so no epsilon moves and no band, floor or collapse certified on any dimension is disturbed.
The declared precisions all survive the trip: `measure_and_write` composes the note out of the
declared formatters, and the door escapes and prints that note verbatim.

Two things the walk pins that were not previously written down:

* `to_ledger_entry` writes the headline **unrounded** into `coupled_gap_ledger.json`, and
  `_coupled_gaps` carries it unrounded into `proof.json`. That is a **carrier**, not a render —
  but the register's rule ("the epsilon is half a step of the FINEST render") has no way to *say*
  so, and applied literally to a JSON hand-off it collapses to 1e-17. The rule needs a stated
  boundary between a render and a carrier, and has never had one.
* The door renders **every** component number at 4dp via `fmtComponent`, integer counts included
  (`caught: 31.0000`, `n_negatives: 1408.0000`).

## Half two: THE DEFECT. A repair reintroduced its own failure one level down

`fmtComponent` exists because this door was serving `[object Object]` for a nested component —
found by `site/live_pixel_verify.py` driving the LIVE page. Its own comment states the standard:

> *On a door whose whole proposition is "every figure walks to its evidence", a component that
> renders as [object Object] is a figure that cannot be read at all.*

The repair carried a depth limit — `if (depth >= 2) return "…"` — and **the limit reintroduced
exactly that failure one level down.** Measured on the rendered pixel:

| row | numbers published in `components` | elided as `…` | readable nowhere on the row |
|---|---|---|---|
| `W1_11_fabric_physics_core` | 160 | 22 | **21** |
| `W1_12_premise_trace_generator` | 160 | 22 | **22** |
| `W2_11_payment_behaviour_source` | 48 | 9 | 0 |
| the other 11 rows | 250 | 0 | 0 |
| **total** | **618** | **53** | **43** |

Every `two_level.cells.*` reading on both fabric rows — `value`, `worst_value`, `resolution` —
was served to the public door as an ellipsis. The producer nests them one level below the limit.

**Why it was invisible on the row anybody was reading.** H27's own six attributed measures are
elided in this block too:

```
measures=ageing.mean_bucket_displacement=…, ageing.overstated_arrears_rate=…,
ageing.understated_arrears_rate=…, arrears_view.unpursued_arrears_rate=…,
detection.false_flag_rate=…, detection.missed_failure_rate=…
```

They survive **only** because `format_remittance_attribution_summary` happens to repeat them in the
note prose. That redundancy is an accident — nobody designed it as a safety net, no control knows
it exists, and it does not exist on the fabric rows. The D17 discrimination lists
(`fully_attributed_measures=…`, `partially_attributed_measures=…`) and `unpursued_counts` were
elided with nothing rescuing them. So the whole D8 attribution reached the door as several hundred
words of caveat with every number it caveats replaced by a dot-dot-dot.

**Nothing asserted otherwise.** The panel's R11 test checks that each row's *gap* renders at 3dp.
No control had ever asked whether a published **component** number reaches the reader at all.

## What landed (HARDEN, `site/**`)

* **The depth limit goes on bounding STRUCTURE and stops bounding NUMBERS.** Past the limit the
  numeric leaves beneath are flattened path-qualified rather than dropped. Raising the limit to 3
  would have been an instance fix (R10) — a payload nested one deeper comes straight back.
* **The spin guard moves to an explicit NODE BUDGET.** The depth limit was carrying it and never
  could: a two-deep cycle spins *inside* the limit. Proven by building a cycle in the harness
  rather than asserting the comment.
* **Non-numeric leaves past the limit still elide** — this is a narrowing of the elision, not its
  removal, and the narrowing is tested.
* **The control:** every finite number in a row's `components` must appear in **that row's**
  rendered components block. Per-row deliberately — a panel-wide substring search passes on a
  number legible two rows away, which is the accident that hid this one. Both vacuity halves
  guarded: the sweep raises if it finds too few numbers, and raises if none of them sits past the
  structural limit (a control the payload never exercises is a failed control).

**R15 — four mutations, firing by name.** The pre-repair `return "…"` restored in a mutated copy of
the page, asserted to lose **53** numbers on **both** named fabric rows (a count, not a boolean — a
change in it is a movement to re-read, not a number to update); a figure nested one level deeper
than anything shipped, asserted legible; a deep subtree with no numbers, asserted still elided;
a cyclic payload, asserted bounded by the budget with the figure before the cycle kept.

**R11:** `618 of 618` published component numbers now render in their own row. Verified by executing
the page's own inline JavaScript against the live generated payload, before and after.

**R12:** no published number moved. This changes what the door PRINTS, never what anything computes.

`site/proof/` 15 passed · `site/proof/ + tests/tools/test_generate_proof_coupled_gaps.py` 123 passed
· `site/test_live_pixel_verify.py` 16 passed.

## Why still L2

L3 means Expert Hour says "this is real". Eighteen Hours, eighteen defects, and Hour #4's
stated-in-advance criterion of **two consecutive clean Hours** has still not been approached. This
Hour did not change the instrument's numbers — but it changed a published surface those numbers
reach, and it found that 43 figures on the company's own Proof door had not been readable at all.
A promoter who takes 2→3 on the tick that discovered that is promoting on the reputation of the
door as it was believed to be.

## Hour #19 leads, in order

1. **D35 is still unbuilt as scoped, and now has a sharper brief.** Its file_scope is
   `tools/couple_w2_11_d5.py`; this Hour answered its QUESTION from the artefact side and left the
   register untouched, deliberately — declaring the door's 3dp site without extending
   `measure_component_render_sites` past this process's edge would red
   `check_component_render_sites` ("a site the register declares and the sweep cannot find is a
   debt entry outliving its debt"). The register and the sweep have to move together.
2. **The render/carrier boundary is undefined.** "The epsilon is half a step of the finest render"
   collapses to 1e-17 the moment the walk reaches a JSON hand-off. No field distinguishes a
   reader-facing render from a machine carrier, and until one does the rule cannot be extended
   past this process at all.
3. **Whose defect is the fabric rows'?** 43 unreadable figures were W1_11/W1_12's, found from
   H27's chair. The door is fixed for everyone; whether those atoms' own evidence claims rested on
   figures nobody could read is *their* Hour, not this one's, and no one has asked.
4. **D34 and D33 are still unbuilt** (per-figure resolution floors for `detection`,
   `detection_latency`, `ageing`; the bit-equality movement predicate). Four reshape atoms now sit
   at L0 behind this instrument, each minted by an Hour and none built.
5. **Carried forward, still untaken:** the interior collapses have no owner of their own (Hour
   #11's lead 1, six times deferred); Hour #8's pinned generated value
   `assert c["n_recon_detected_undated"] == 0`; and whether the other dimensions' normalisation
   notes have the same gap between what they DENY and what they ESTABLISH.
