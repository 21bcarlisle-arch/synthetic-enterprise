# FINDING — a leave-one-out judged by the gate's own verdict measures the guard, not the reading

**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/harness/test_premise_two_level.py::test_the_SWITCH_COST_is_measured_on_the_homes_that_DID_NOT_force_it` — the leave-one-out is judged on the homes that did not force the switch, not by the gate's own verdict
<!-- DISCHARGED 2026-08-12 by a worker tick drawn at RUNG 1c. This document reported a
     defect AND its repair in the same breath; its severity header stated the state the
     Hour FOUND, and nothing re-read it afterwards, so it went on refusing level-raises in
     H_harness after the instrument it named was trustworthy again. The falsifier below was
     RUN GREEN before this line was written. -->
<!-- Severity normalised 2026-08-12 by a worker tick: `MEDIUM` is not one of the three tokens
     OPS9 defines, so this was UNCLASSIFIED. BLOCKING on the document's own evidence -- the
     carriage guard measures the guard rather than the reading, and 'the number the reader
     sees is not the number the gate reads' (GBP 292 -> GBP 66 per premise). -->

**Atom:** `H_GAP_fabric_belief_truth_gap` (level 2, L2→L3 draw) — FIFTEENTH Expert Hour
**Date:** 2026-08-12
**Subject:** `background/fabric_gap_ledger.py::InstrumentSwitch`, the carriage guard the
fourteenth Hour built.

---

## The directed question, and both halves are answered

The fourteenth Hour left this: *the guard uses `MIN_HOMES_FOR_DIVERSITY` on the movers while
the algebraic floor for naming an arm at all is FOUR, so a five-mover reading is certified with
one home of headroom and nothing measures how close to that floor a certified reading sat; nor
whether `borne_by` should be published beside it as a RATIO.*

**Half one — the floor was borrowed, and certified rows sit on it.** `MIN_HOMES_FOR_DIVERSITY`
is an *input sufficiency floor on a panel*: the number of homes `between_home_correlation` and
`timing_diversity` refuse to judge below. It is five. The number of MOVERS a paired percentile
bootstrap needs before `favours` can exclude zero is the smallest `m` with `e**-m` under the
2.5% tail — `m > ln(2/alpha)` = 3.689, therefore **four**. Two subjects, one constant, adjacent
by coincidence: this atom's sixth-Hour class. Measured over 1,200 randomised fallback draws:
of 164 rows the channel certified, **23 are carried by exactly five movers and 37 by six** —
14% ON the floor, 37% within one home of it — and nothing in the row said so.

**Half two — yes, and the measurement is the argument.** Both readings are means over
`borne_by` premises, most of which may be ties. Appending 200 homes **both arms treat
identically** to this atom's own certifying fixture — inferred belief equal to the register,
same interval, same basis, so the paired advantage is exactly 0.0 and they carry neither
reading — changes nothing about the instrument comparison. The published per-premise cost falls
from **GBP 292 to GBP 66** anyway (a factor of 4.4, `observed-with-evidence`), while the ratio
the gate actually reads moves from **0.4523 to 0.4291** (5.1%). *The number the reader sees is
not the number the gate reads*, and only one of them is dilution-invariant.

---

## The finding that nearly went the other way, and it is the transferable one

`carried_by` is a COUNT and the reading it guards is a weighted MEAN, so the obvious next move
was the eleventh Hour's own instrument: a Kish effective sample size, refusing a row whose
movers are concentrated. **The concern is real** — over 500 randomised draws, 24% of certified
rows have an effective carriage below the guard's own number and 1.5% below the algebraic floor
of four. The searched worst case (`_concentrated_forced_population`) is certified with
`carried_by == (8, 5)` and an effective carriage of **3.11**.

The evidence for building the guard was assembled first in the wrong unit. Asking *does one
home decide this row?* as **"does the channel's `resolution` change when the heaviest carrying
home is removed?"** gives **94% of low-carriage certified rows against 14% of the rest** — a
number that would have justified shipping a concentration guard on the spot.

Asking the same question in **GBP** — *does either arm change, or does the cost move past its
own 95% error bar?* — gives **6% against 2%**, on the same rows and the same removals. On the
searched fixture: removing the home carrying most of the counterfactual leaves both arms at
`epc`/`epc` and moves the cost by **GBP 51 against an error bar of GBP 544** (9%).

**The 94% was the guard tripping on the row it was already gating.** Any row at
`carriage_margin` 0 unresolves when a mover is removed, whatever the money does — the criterion
is a function of `CARRIAGE_FLOOR`, which is the thing under test. R15's first killer pattern
(the checked value derived from the same source it checks) with the guard as its own evidence,
and this atom's third-Hour law — *a verdict must be judged in the unit it is published in* —
read in a new place. **No concentration guard was built.** It is pinned as a refutation instead,
so the next Hour does not re-derive it from memory.

---

## Mechanised

* `_mover_floor_for_a_named_arm(alpha)` — the floor **derived from `MONEY_VERDICT_ALPHA`**, not
  chosen; `MOVER_FLOOR_FOR_A_NAMED_ARM` = 4, `CARRIAGE_MARGIN_HOMES` = 1,
  `CARRIAGE_FLOOR` = 5. **Same number as the constant it replaces, so no verdict moved
  anywhere** (R12: the statistic was wrong, not the threshold) — different subject, so a panel
  input floor re-tuned for its own reasons can no longer reach the money guard.
* `InstrumentSwitch.carriage_margin` — how many homes above the floor the thinner reading sat;
  `None` where no reading was taken. Published as `panel_mirror_switch_carriage_margin`.
* `InstrumentSwitch.cost_ratio` / `carriage_share` — the gate's own dilution-invariant reading,
  and the carriage as a fraction of the homes the GBP figure is divided by. `cost_ratio` is
  `None`, and prints as *unformable*, where the error bar is zero: a ratio against nothing is
  not a small one.
* `_carriage_margin_text` prints a zero margin **in words** ("AT — one home of these becoming a
  tie unresolves this comparison without any money moving"), because a zero in a list of counts
  is the easiest thing in a row to skim past and the only one that changes what the
  certification means.
* Both sentences carry it — the disclosure on rows the mirror **certified** as well as refused
  (the twelfth Hour's rule), and the refusal clause now names the derived floor rather than the
  borrowed constant.

**R15: TEN source mutations, each firing its own named test, all RED**, md5 byte-clean restore
(`da3ae4ece4858ac7710df85384b83060`) — margin folded to zero / floor off by one / floor written
as a literal / the guard reads the panel-diversity constant again / margin measured from the
wrong floor / an unavailable margin reads as ample / a zero error bar fails open to `0.0` /
the gate's reading published as a difference / a zero margin printed as a bare integer / the
disclosure drops the ratio.

**One of them survived the first pass and the survival is a second lesson:** the
difference-instead-of-ratio mutation passed because the dilution test divided a relative move by
a **signed** base, and the mutated base is negative, so every comparison against it passed. Both
denominators are now absolute, and the comparison is between the two moves (77% against 5.1%)
rather than against a tolerance somebody picked.

**Not always red, searched, on synthetic and real data:** the atom's certifying fixture still
certifies at `carriage_margin` 2 and 50 of 66 certified rows in 500 draws sit at or above the
floor's effective equivalent.

**No published figure moved**, measured end-to-end by A/B of `tools/couple_fabric.py --json`
against committed HEAD in **two clean checkouts** (the dirty working tree is not the baseline):
on BOTH published populations, exactly **two added keys, both `null`** — the level branch does
not have a switch — and **zero moved values**. Gaps 0.4269/0.4042 (drawn 200) and 0.2184/0.2624
(authored) unchanged.

**Suite:** 293 passed / 2 xfailed on the atom (was 284/2), 372 passed / 2 xfailed across it and
its sibling suites, ruff clean, epistemic PASS on 557 files.

---

## R10 classes

1. **A LEAVE-ONE-OUT JUDGED BY THE GATE'S OWN VERDICT MEASURES THE GUARD, NOT THE READING.**
   Signature: a sensitivity study whose outcome variable is the classification the control
   produces, rather than the quantity the control is about. It will report the threshold's own
   discontinuity as evidence for the threshold, at any threshold. Re-ask it in the published
   unit before building anything on it.
2. **A CONSTANT BORROWED FROM AN ADJACENT SUBJECT HIDES BEHIND AGREEING BY COINCIDENCE.** Four
   and five are one apart, so nothing ever read wrong; the coupling is invisible until the
   other subject is re-tuned. Derive the floor from the thing that decides it, and prove the
   decoupling by mutating the constant it used to read — not by reading the value.
3. **A CONTROL'S INVARIANCE CAN HIDE BEHIND A PUBLISHED FIGURE THAT IS NOT INVARIANT.** The gate
   read a scale-free ratio and the row published a scale-dependent point, so the disclosure and
   the verdict were denominated differently and only the disclosure moved.

## Opener for the sixteenth Hour

`carriage_margin` is published and the `resolution` it describes still steps at zero, so the
row now DISCLOSES a discontinuity it does not otherwise treat: nothing has asked whether a row
at margin 0 should be certified with a qualifier rather than cleanly, or whether the two
readings' margins should be published separately (they are 3 and 0 on the searched fixture, and
only the minimum is reported). Also still open, and now the oldest item on this atom: **FOUR
retained-but-superseded fidelity statistics defended only by their docstrings.**
