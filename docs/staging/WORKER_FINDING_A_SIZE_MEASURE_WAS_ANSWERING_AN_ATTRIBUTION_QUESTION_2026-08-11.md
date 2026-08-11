# WORKER FINDING — a size measure was answering an attribution question

**Atom:** `H_GAP_fabric_belief_truth_gap` · **Sixth Expert Hour** (worker tick, L2→L3 draw)
**Date:** 2026-08-11 · **Outcome:** IT FOUND SOMETHING, SO THE LEVEL STAYS 2
**Subject:** `background/fabric_gap_ledger.py::_normaliser_caveat` and `MIRROR_FIDELITY_BAND`

This is the eleventh time this atom has surfaced something by RUNNING a thing rather
than reading it. This time what it refuted was the Hour's own opening hypothesis.

---

## 0. The opener, verbatim from the fifth Hour

> NOT CLOSED: `MIRROR_FIDELITY_BAND` serves two subjects (the kW/K gate AND the
> normaliser-drift disclosure) — named, not repaired, and the next Hour's opener; the
> `weight_null` money totals are still published with no interval.

Both were taken up. The first is repaired below. The second is measured, sized, and
handed on — see §6.

## 1. Confirmed: two subjects, opposite in polarity, on one constant

`MIRROR_FIDELITY_BAND = 0.05` gated BOTH:

| consumer | quantity | unit | what crossing the band MEANS |
|---|---|---|---|
| `panel_mirror_is_attributable` | `panel_mirror_register_infidelity` | kW/K, a ratio | the instrument is **broken** |
| `_normaliser_caveat` | `panel_mirror_normaliser_drift` | normalised gap | the instrument is **working** |

The constant's own comment asserts the firewall it did not have:

> One constant serving both would mean a change made for a money reason silently
> re-graded every mirror ever run.

This is the FOURTH Hour's `VERDICT_MATERIALITY` finding one level down, inside that
Hour's own replacement machinery. A documented firewall is not a firewall.

## 2. The hypothesis — and its refutation by the existing suite

The Hour opened by measuring the drawn population and reading its silence as a
**fail-open**:

```
drawn(200):  drift 1.87% (inside the 5% band -> caveat SILENT)
             register MAE  0.044773900 -> 0.044773900   (moved +0.000e+00)
             gap figures   0.4269 -> 0.4351             (an apparent 3.8% worsening)
             => 100% of the visible difference is the yardstick
```

The level-preserving reflection `2*pivot - value` preserves the numerator **by
algebra**, so on both published populations the whole of the difference is artefact
while the drift reads only 12.4% / 1.87%.

Wiring the caveat to that attribution alone made it fire on
`test_the_caveat_list_is_EMPTY_on_a_population_with_nothing_to_caveat` — a fixture an
EARLIER Hour had already retuned to a 1.1% residual precisely so that "nothing to
caveat" would mean something.

**The refutation is exact.** Under a level-preserving reflection the attribution is
100% *by algebra* whenever the two gaps differ at all, so attribution alone makes the
caveat **unconditional on the common path**. And 1.87% of the larger figure is a
difference too small to mislead anybody. Silence on the drawn row was RIGHT — for a
SIZE reason, not the reason the code gave.

> **R10 CLASS: a size measure and an attribution measure are both real and neither
> answers the other.** Collapsing the repaired pair back onto one number would have
> been the same defect wearing the repair's name.

## 3. The defect that survived measurement — a FALSE published claim

The gate read the DRIFT (a size measure). The sentence it releases makes an
ATTRIBUTION claim:

> "the two gaps are not on one scale and the difference between them is not an
> accuracy change"

Under the level-preserving reflection those agree. In the **log fallback** — the one
real code path where the reflection does not preserve the register arm's error — they
come apart. Measured over 300 fallback panels:

```
101 of 300 fired the old gate while the MAJORITY of the difference
              was a genuine change in the register arm's error
worst case:   the sentence printed "not an accuracy change"
              over an 18.2% difference that was 68.6% exactly that
```

That is a false statement published, not merely a missing one — a stronger finding
than the one the Hour opened with, and it only appears in the regime the opening
hypothesis was not looking at.

## 4. Mechanised — five terms, two bands, all in the ledger row

Carried IN the row rather than behind a flag (R11 — a reader who has to ask for the
artefact will not ask):

- `panel_mirror_gap_difference_real` — the yardstick-free remainder, measured against
  the **first** figure's baseline (the one the reader is anchored on).
- `panel_mirror_yardstick_share` — a **bounded** attribution,
  `|yardstick| / (|yardstick| + |real|)`. The first cut divided by the observed move
  and read **283%** on a panel where the two contributions oppose and partly cancel;
  a share that can exceed its own whole is not a share.
- `panel_mirror_gap_difference_relative` — the SIZE half, as a share of the larger.
- `YARDSTICK_SHARE_BAND = 0.50` and `YARDSTICK_MATERIAL_DIFFERENCE = 0.05` — a FOURTH
  and FIFTH constant, never a reuse.
- `GAP_RENDER_DP = 4` — a vacuity guard set by what the CONSUMER renders.

**The vacuity guard is on the DIFFERENCE, not on the pair**, and a panel proves the
distinction: gaps of `0.0002499999` and `0.0002500500` RENDER as `0.0002` and `0.0003`
while differing by `5.0e-08`. A pair-shaped guard would publish a caveat about a
difference its own sentence prints as `+0.0000`.

Populations either side of every band:

```
                                    relsize   share    verdict
PUBLISHED authored(15)              12.37%   100.00%   FIRES
PUBLISHED drawn(200)                 1.87%   100.00%   silent (size)
proportional 0.80/0.90              40.00%   100.00%   FIRES
nothing-to-caveat fixture            1.10%   100.00%   silent (size)
infeasible default (LOG)            11.35%    60.71%   FIRES
low-share LOG (rogue .10/.90/n10)   17.37%    27.26%   silent (attribution)
fixed_offset (additive)              0.00%      None   silent (vacuity)
near-exact 0.9999                    0.02%      None   silent (vacuity)
```

## 5. R15 — seven source mutations, and three of the first four controls were theatre

Every mutation fires its OWN named test; md5 byte-clean restore after each.

| # | mutation | test that dies |
|---|---|---|
| M1 | gate reverted to the DRIFT (the original defect) | `..._SILENT_when_the_difference_is_mostly_a_real_change` + `..._INDEPENDENT_subjects` |
| M2 | vacuity guard deleted | `..._VACUOUS_when_the_two_figures_RENDER_the_same` |
| M3 | attribution against the AFTER baseline | `..._REAL_REMAINDER_is_measured_against_the_FIRST_figures_baseline` |
| M4 | unbounded ratio (divide by the observed move) | `..._SILENT_when_the_difference_is_mostly_a_real_change` |
| M5 | SIZE gate deleted (attribution alone) | `..._SILENT_on_a_difference_too_SMALL_to_mislead` + `..._EMPTY_on_a_population_with_nothing_to_caveat` |
| M6 | real remainder forced to zero | `..._SILENT_when_the_difference_is_mostly_a_real_change` |
| M7 | size gate re-collapsed onto the fault constant | `..._INDEPENDENT_subjects` |

**THE SWEEP IS WHAT CAUGHT THE WEAK CONTROLS**, and this is the reusable part:

1. The **vacuity** test used only a bit-identical panel, so the `magnitude == 0` float
   check caught it and the rendering guard could be DELETED with the suite green.
2. The **silent** test's fixture had its two contributions AGREEING IN SIGN, which
   makes the bounded attribution and the discarded ratio *numerically identical* — so
   the mutation swapping them survived.
3. The **fires** test was written on a panel where the old gate fires too, so it
   pinned the repair without being able to fail on the defect that motivated it.

Each was repaired by **searching for the population that separates them**, not by
inventing one.

**ONE RESIDUAL, NAMED NOT HIDDEN:** the `<=` boundary on `YARDSTICK_SHARE_BAND`
survives mutation. It needs a panel with `|yardstick| == |real|` to the bit — an exact
knife-edge no reachable population sits on, and fabricating one would pin a generated
value.

## 6. Not closed — the next Hour's opener

The `weight_null` money totals are **still published with no interval**, and they are
not decorative. `panel_mirror_weight_artefact` is a ratio of differences of two GBP
SUMS:

```
authored(15):  artefact 0.6893   totals GBP 29,722 epc / 12,835 inferred
drawn(200):    artefact 0.9043   totals GBP 622,902 epc / 560,165 inferred
```

It is above its 0.50 band on both, which is what puts **both published populations on
MIRROR INCONCLUSIVE today**. That is the fifth Hour's own class — *a sum has no error
bar* — sitting on the gate that decides whether this atom's mirror may be read at all.

## 7. What did NOT move

No published figure and no published caveat changed: authored still fires the
yardstick sentence, drawn is still silent, `0.2184 / 0.2492` and `0.4269 / 0.4351`
re-taken, `money_favours` = `inferred` on both. The whole repair lands in the fallback
regime and in the constant-sharing — the honest report, not a softened one.

**Suite:** 253 passed, 2 xfailed (atom scope) · 176 passed (downstream consumers).
