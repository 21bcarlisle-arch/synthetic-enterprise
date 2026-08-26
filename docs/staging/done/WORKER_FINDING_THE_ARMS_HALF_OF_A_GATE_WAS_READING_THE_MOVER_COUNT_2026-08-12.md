# FINDING — the direction half of the instrument gate said it "needs no threshold to read", and the threshold it was reading was the mover count

**Severity:** LATENT · **Lane:** H_harness

**Atom:** `H_GAP_fabric_belief_truth_gap` (lane H_harness, level 2 → 3, loop_stage build)
**Date:** 2026-08-12 · **The FOURTEENTH Expert Hour on this atom** · worker tick, L2→L3 draw
**Module:** `background/fabric_gap_ledger.py` · **Suite:** `tests/harness/test_premise_two_level.py`

**SEVERITY: BLOCKING, DISCHARGED ON LANDING** (`DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12`
clause 2). It says a gate was reading a sampling artefact and calling it a mechanism, so
it is BLOCKING by construction. It is discharged by the repair in this same commit —
guarded, disclosed, re-searched, R15 both ways — and no published figure was ever
affected, which is MEASURED and not asserted: both published populations take the level
branch, where the whole quantity does not exist, and an end-to-end A/B of
`tools/couple_fabric.py` against committed HEAD moves NOTHING on either
(one added key, `panel_mirror_switch_carried_by: null`; gaps 0.4269 / 0.4042 and
0.2184 / 0.2624 unchanged). No level-raise rests on it: this atom's level has stayed 2
for fourteen consecutive Hours. The residue in the opener below is **LATENT**.

## The directed question, and it was half right

The thirteenth Hour left this: *the instrument channel refuses when the two readings name
different arms, and every disagreement measured is a RESOLUTION crossing in which one side
says `neither` — so the gate refuses a row for having had LESS evidence under an instrument
it did not use, and in 31 of 130 measured cases the direction runs the other way. Whether a
resolution crossing should refuse at all, and whether its two directions are the same
finding, has not been asked.*

It should refuse, and the two directions are one finding with two claims (§5). But the
question could not be answered as posed, because on the panels it was asked about the
crossing was not a disagreement between instruments at all. **ONCE AGAIN THIS ATOM SURFACED
SOMETHING BY RUNNING A THING RATHER THAN READING IT** — the docstring's own claim was
falsifiable in four lines of arithmetic and nobody had run it.

## 1. The defect: `favours` below four movers is a reading of the mover count

`InstrumentSwitch.resolution` has two halves. The docstring says of the first:

> the two instruments name DIFFERENT ARMS on the same homes — the instrument decided what
> this mirror says, **which needs no threshold to read**

`favours` is `neither` iff the reading's 95% percentile-bootstrap interval contains zero.
A paired money advantage is **exactly 0.0** on every premise both arms forgo the same money
on. So for `m` movers in `n` rows, the probability a resample draws none of them is
`(1 - m/n)**n → e**-m`:

| movers | P(resample draws no mover) | 97.5th percentile | names |
|---|---|---|---|
| 1 | 36.6% | exactly 0.0 | `neither` |
| 2 | 13.2% | exactly 0.0 | `neither` |
| 3 | **4.7%** | exactly 0.0 | `neither` |
| 4 | **1.65%** | −12,658 | `epc` |

Measured with **GBP 1,000,000 on every mover**: at three movers the verdict is
GBP −37,975 per premise and names `neither`; at four it names `epc`. **Below four movers a
paired money verdict cannot name an arm however much money is on the table**, and no panel
size repairs it — the limit does not depend on `n` (0.0388 at n=20, 0.0470 at 79, 0.0496 at
1,000, all above the 2.5% tail). Bigger panels make a three-mover verdict *less* resolvable,
so a guard sized on the panel has the sign of its own protection backwards.

## 2. The gate's own fixture for that half was one of these

`_disagreeing_forced_population` was **searched for** by the thirteenth Hour and shipped as
the evidence that the direction half fires. Of its 79 borne homes, **four carry the published
reading and three carry the counterfactual**; the counterfactual's interval ends at exactly
`0.0`. The "different arms" it certifies the gate with is the mover count crossing 3 → 4.
The money difference between the two instruments there is GBP 38 against the reading's own
error bar of GBP 171.

## 3. How much of the gate was this — 5,000 fresh draws

| | count |
|---|---|
| fallback-branch draws, each with one forcing home | 5,000 |
| arms disagree | 1,003 |
| ...of which two *different resolved arms* | **0** (reconfirms the thirteenth Hour on an independent sample) |
| ...of which BOTH readings carried by ≥ `MIN_HOMES_FOR_DIVERSITY` | **15** (1.5%) |

**98.5% of what the direction half was firing on was the mover count.**

## 4. And the fail-open is the larger half

Separately, 3,000 draws: **2,373 rows have a reading carried by fewer than five movers, and
1,930 of them CERTIFIED** — 1,682 off a reading carried by one home or none. In its purest
form, and live on this file's own fixtures: where both arms forgo identical money on every
premise, both readings are exactly GBP 0.00 with a zero-width interval and the magnitude
half asked **`0.0 > 0.0`** and said `attributable`. R15's second killer pattern by name — a
control that passes on empty.

**That reaches the twelfth Hour's release.** It certified five of twelve stocks and counted
them; all five have `carried_by == (0, 0)`. The twelfth Hour's own claim is untouched (no
row there is refused by a kW/K reading of the stock, and its channel still says either word
across the twelve) — but the five it released were released into a GBP channel with no GBP
in it. Ten of the twelve now stop at `unresolved`; the two whose register over-states, six
carrying homes each, still certify.

## 5. The directed question, answered

**Should a resolution crossing refuse?** Yes — on a carriable panel it is the honest form of
the channel's own claim: how decisive this mirror is was set by an instrument chosen by homes
outside the comparison.

**Are its two directions the same finding?** One finding, two claims — and the answer
inverts under carriability. Among all 1,003 crossings the reading the row USED is the one
that names an arm, **935 to 68**. Among the fifteen carriable ones it is **1 to 14**: the
instrument the row actually used made it *less* decisive, not more. The thirteenth Hour
flagged that minority direction as unexamined; once the artefact is removed it is almost the
whole population. So the refusal sentence now NAMES its direction — "an arm is named under
the one they could have had and not under this row's reflection" — rather than asserting the
majority one at a reader in the other case.

## 6. Mechanised

* `InstrumentSwitch.carried_by: tuple[int, int] | None` — the movers behind each reading,
  from the two `MoneyVerdict`s already computed. No new bootstrap, no new constant.
* `resolution` refuses to read a comparison it did not make: `unresolved` when either
  reading is carried by fewer than `MIN_HOMES_FOR_DIVERSITY` movers, **checked before both
  existing halves** so a thin panel is never told a real mechanism decided it.
* `panel_mirror_switch_carried_by` in the ledger row; the carriage printed in
  `_switch_cost_caveat` (on certified rows too, the twelfth Hour's rule) and in
  `_why_unattributable`'s new clause; the arms clause names its direction.
* `_disagreeing_forced_population` **re-searched** onto one of the 15 carriable crossings
  (79 borne, 8 and 9 movers, cost GBP 48 inside a bar of GBP 123 — still firing the arms
  half WITHOUT the magnitude half, which is the property the fixture exists for). The old
  one is KEPT as `_thin_disagreeing_forced_population` and pinned as the defect.
* `test_the_STOCK_COARSENESS_DISCLOSURE_...` repointed off a `carried_by == (0, 0)` row onto
  `_certifying_forced_population` (11 and 7 carrying homes).

**ONE-DIRECTIONAL BY CONSTRUCTION:** `unresolved` is not a pass, so this can only ever take
certification away — proven over a searched family, not asserted.

**NOT ALWAYS RED, on synthetic and on real data:** 627 of 3,000 draws are carriable on both
readings, 445 certifying and 182 refusing; the two over-stating stocks of the twelve certify;
both published populations are untouched (level branch, no switch).

**R15:** NINE source mutations — guard counts the panel / clause deleted / reads `max` /
checked after the arms half / off by two / zero-carriage reads clean / sentence loses its
direction / carriage clause reports one reading twice / disclosure drops the carriage — each
firing its own named test, all RED, md5 byte-clean restore (`993754f85490764fd7fd8080ddf73a44`).

**Suite:** 284 passed / 2 xfailed on the atom (was 274/2); 397 passed / 2 xfailed across it and
its four sibling suites (`test_couple_fabric`, `test_gap_ledger_reconciler`,
`test_lcl_household_anchors`, `test_band_null_sweep`); ruff clean; epistemic PASS 557 files.

## 7. R10 classes

1. **A LABEL COMPARED TO A LABEL INHERITS THE THRESHOLD THAT MADE THEM.** "Different arms
   needs no threshold to read" was true of the comparison and false of the operands. Signature:
   a gate whose two inputs are each a thresholded verdict, fired on a difference in
   *classification* that no difference in *quantity* supports.
2. **A GUARD SIZED ON THE PANEL CANNOT PROTECT A STATISTIC CARRIED BY A SUBSET** — the TENTH
   Hour's class, recurring verbatim in a channel built three Hours after it was closed on a
   different statistic. R10 says a class fix extends the invariant library; that one was
   applied to `panel_mirror_weight_artefact_interval` alone. The eleventh Hour *asked* the
   question of its own term and correctly found the class did not reach it; the thirteenth
   built a new resampled statistic and did not ask.
3. **A CONTROL THAT DIVIDES OR COMPARES CAN PASS ON TWO ZEROES.** `0.0 > 0.0` is False, and
   False reads as clean. Any gate of the form `cost > bar` needs to know whether either was
   ever measured.

## Opener for the fifteenth Hour

The carriage guard uses `MIN_HOMES_FOR_DIVERSITY` on the MOVERS, and §1 shows the algebraic
floor for naming an arm at all is **four** — so on a five-mover reading the guard passes a
verdict whose resolution has exactly one home of headroom, and nothing measures how close to
the floor a certified reading sat. Whether `borne_by` should be published beside it as a
*ratio* (nine movers of 59 is a different object from nine of nine) has not been asked
either.

Also still open, now the oldest item on this atom: **FOUR retained-but-superseded fidelity
statistics defended only by their docstrings.**
