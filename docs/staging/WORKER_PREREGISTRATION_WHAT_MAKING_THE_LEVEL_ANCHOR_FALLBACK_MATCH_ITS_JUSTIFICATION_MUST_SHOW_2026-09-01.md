**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

*RECORDED, not LATENT: a pre-registration refutes nothing on its own. It exists so the measurement
filed beside it can be shown to have been designed before its answer was known.*

# PREREGISTRATION — what making `year_level_anchor`'s fallback match its own justification must show

**Filed 2026-09-01, delivery seat, Lane 0. BEFORE the edit and BEFORE running anything. Nothing
below is known.**

---

## What was found, by inspection, before this file was written

The drawn item said the native SVT capture had been dead for three stretches and told me to verify
first rather than take its word. **It has not been dead**: `/tmp/svtcap/capture.log` ends `EXIT_RC=0`
with 156 renewal rows and 1373 SVT decisions, the dead third run's corpse is kept separately at
`capture.DEAD-run3-1147Z.log`, and every clause of the item's "done means" was discharged by earlier
lanes before this tick opened — the five predictions are graded at `68ec6825b`, corrected at
`39967d018`, the docstring the item asks me to fix was corrected at `342d72159` and is correct at
HEAD, and the whole-book fit emitted. So this stretch follows the interconnection instead, which is
what `9a03f3b44` left open in one sentence: *"the attribution is unearned, and the one-variable run
has not been done."*

**The one-variable question needs no run. It is answerable from the committed table**, and the
answer is a defect in `simulation/departure_level_anchor.py`:

```python
return YEAR_LEVEL_ANCHOR.get(year, YEAR_LEVEL_ANCHOR[MULTIPLIER_REFERENCE_YEAR])
```

The fallback's **condition** is *absence from the fitted table*. The fallback's **justification**,
in the docstring directly above it, is *"OUTSIDE THE RECORD IT IS THE REFERENCE YEAR'S"* and rests
entirely on the year being a synthetic future where `market_switching_multiplier(year)` already
carries the level movement. **Those are two different sets.** Today they coincide exactly — both are
`2016..2025`, checked:

```
record years (_published_departure_rates): [2016..2025]
fitted years (YEAR_LEVEL_ANCHOR):          [2016..2025]
record - fitted: []    fitted - record: []
```

Coinciding is why nobody has noticed. **The native capture is the proof they can come apart**:
`9a03f3b44` measured `year_level_anchor(2022)` at `3.053619` in the native run against `1.524110` in
the clean-tree run, because the run's uncommitted block was missing 2022 — a year squarely *inside*
the record — and it silently took the reference year's value under a justification written only for
years outside it. Nothing said so. There is no warning, no `None`, no observable.

**The docstring's directional claim is false on the case it actually fired on.** It says the
fallback *"fails toward the record rather than toward the 3.45x-short world, which is the direction
a fallback should fail in."* Measured against the committed table, the reference year's anchor over
each year's own fitted anchor is:

| year | record % | fitted anchor | fallback ÷ fitted |
|---|---|---|---|
| 2016 | 17.60 | 4.597312 | 0.657 |
| 2017 | 14.00 | 4.256902 | 0.710 |
| 2018 | 20.00 | 3.345826 | 0.903 |
| 2019 | 21.30 | 3.228064 | 0.936 |
| 2020 | 23.00 | 4.425742 | 0.683 |
| 2021 | 18.40 | 3.219914 | 0.938 |
| **2022** | **4.30** | **1.524110** | **1.982** |
| 2023 | 12.50 | 2.091517 | 1.444 |
| 2024 | 16.10 | 3.020806 | 1.000 |
| 2025 | 17.90 | 2.118624 | 1.426 |

The fallback **overshoots on three of the nine non-reference years and undershoots on six**. It has
no direction. And on 2022 — the record's *lowest* year, the one year the published record is
loudest about — it nearly **doubles** the anchor, which pushes departures *up*, i.e. **away** from
the record's 4.30%. The claim "fails toward the record" is defensible only against the alternative
of no anchor at all, which is not the live alternative; against the year's own fitted value it is
backwards on exactly the case that fired.

This is the class *a fallback justified for one domain applies silently to a different one*, and
the sibling function two files over already gets it right: `market_departure_rate` branches on
`if year in published`, not on membership of a fitted artefact, and says so — *"INSIDE THE RECORD IT
IS THE RECORD ... OUTSIDE IT, the savings curve."*

## What is being changed

`year_level_anchor` branches on **the record window** instead of on the fitted table's keys. A year
inside the record with no fitted anchor **fails closed with a named reason**; a year outside the
record keeps the reference-year fallback, where the docstring's argument does hold and is unaltered.

**No constant is added, removed or edited.** `YEAR_LEVEL_ANCHOR`'s ten values are untouched — the
standing constraint from both prior preregs is honoured by not touching the table at all, and I have
checked that against the file rather than against my own intentions (`git diff` on the table lines
must be empty; pasted in the grading below).

## The predictions

### G1 — no published figure moves, because the guard is unreachable at HEAD

All ten record years are present in the fitted table, so the new branch never fires for any year the
world actually runs. Predicted: `year_level_anchor(y)` returns a float **identical to the current
value, bit for bit**, for every `y` in `2016..2025`.

*Refuted by:* any year returning a different value.

Confidence: high. This is arithmetic, not a run.

### G2 — the outside-record path is preserved exactly

Predicted: `year_level_anchor(2030)` still returns `3.020806`, the reference year's value, unchanged.
The docstring's argument survives on the domain it was written for.

*Refuted by:* a raise, or any other value.

### G3 — the guard can fail, and its magnitude is the measured one

MUTATION: with `2022` deleted from `YEAR_LEVEL_ANCHOR`, predicted: `year_level_anchor(2022)`
**raises**, and the message names the year and names the record. Before this change the same
mutation returns `3.020806` silently — **1.982x** 2022's own fitted `1.524110`.

*Refuted by:* the mutation still returning a number, or a message that names neither.

This is the leg that makes the control able to fail. A guard that is unreachable at HEAD and never
mutation-proven is the shape this repo has a catalogue of.

### G4 — no existing test breaks

Predicted: the suites over the touched files stay green.

**This is the one I am least sure of, and I am saying so before the answer.** A test that
monkeypatches `YEAR_LEVEL_ANCHOR` down to a subset of years — a plausible fixture shape for
`test_year_keyed_rate_table_census.py` or `test_switching_rate_commons.py`, both of which import
this module — would have been passing on the silent fallback and will now raise. **I have
deliberately not grepped for it before filing.** If G4 is refuted, the refutation is informative:
it would mean a control was reading the fallback value and calling it a fitted one.

*Refuted by:* any red that is not present at clean HEAD.

## What must NOT happen when this is scored

Named in advance so the flattering repair is not available afterwards:

1. **No constant is pasted into, edited in, or deleted from `YEAR_LEVEL_ANCHOR`** — including
   "while I was in there". The ten values are out of scope for this stretch entirely.
2. **If G4 is refuted, the failing test is not silenced and the guard is not narrowed to let it
   pass.** The finding moves to what that test was asserting.
3. **The reference-year fallback is not deleted.** Its justification is sound outside the record and
   removing it would be a second change wearing this one's evidence.
4. **The docstring's false directional sentence is corrected, not deleted.** A reader needs to know
   the claim was made and why it was wrong, which is the same reason `342d72159` dated its
   correction rather than silently applying it.

---

# GRADED 2026-09-01, delivery seat, Lane 0

**The text above is untouched. The miss below is kept where it was filed, not revised.**

## G1 — CONFIRMED, bit for bit.

Every one of the ten record years returns a float **identical** to its committed value:

```
G1 every record year bit-identical: True
```

Checked as equality against the ten literals, not as "close enough". No published figure moves,
because the new branch is unreachable while every record year is fitted.

## G2 — CONFIRMED, exactly.

`year_level_anchor(2030)` returns `3.020806` — the reference year's value, unchanged. The
outside-record path is preserved and the docstring's argument survives on the domain it was
written for. Leg (c) of the new control re-checks this *while the guard is armed*, so a future
edit cannot buy the refusal by breaking the fallback.

## G3 — CONFIRMED, and DRIVEN rather than described.

With `2022` removed from `YEAR_LEVEL_ANCHOR`, `year_level_anchor(2022)` raises `ValueError` naming
both the year and `INSIDE the published` record. The magnitude leg asserts the year chosen is one
the fallback distorts by more than 1.5x before it accepts the raise — it is 2022 at **1.982x**.

**The guard was mutation-proven, not assumed.** Neutering the branch condition to `if False:` —
i.e. restoring the exact prior behaviour — turns the control red:

```
>           with pytest.raises(ValueError, match=f"{victim}"):
E           Failed: DID NOT RAISE <class 'ValueError'>
FAILED tests/simulation/test_departure_risks.py::test_a_year_inside_the_published_record_with_no_fitted_anchor_refuses_instead_of_falling_back
1 failed
```

Restored: `22 passed`. Run under `python3 -B` throughout, because a mutation harness reporting
SURVIVED off a stale `.pyc` is a class this repo has already paid for.

## G4 — CONFIRMED on its stated refuter, and the refuter earned its keep.

The prereg named G4 as the one it was least sure of and predicted a monkeypatching fixture might
break. **Two tests are red** across the five suites that import this module:

```
FAILED tests/architecture/test_switching_rate_commons.py::test_the_worlds_realised_departure_rate_is_inside_the_published_band
FAILED tests/architecture/test_switching_rate_commons.py::test_the_instrument_prints_the_distance_to_both_band_edges_and_not_only_the_verdict
AssertionError: only 7 years had their margins checked -- a control over an emptied subject reports a constant PASS
```

The stated refuter is *"any red that is not present at clean HEAD"*, so the reds were run against a
clean extract (`git archive HEAD` into `/tmp/cleanhead`) rather than by disturbing this tree:

```
2 failed, 24 passed, 1 xfailed   # identical failures, identical assertion, at clean HEAD
```

**Both reds are pre-existing and identical. G4 is confirmed.** Had I graded G4 on the working tree
alone I would have filed a false refutation against my own change — the same shape as this
document's predecessor, which reached a verdict against something other than its subject twice.

**But the pre-existing red is not incidental to this finding, and recording it as "not mine" and
moving on would be the flattering read.** `tests/architecture/test_switching_rate_commons.py`
classifies `YEAR_LEVEL_ANCHOR` and `year_level_anchor` under `_HELD_INDIRECTLY` — explicitly *"held
through its EFFECT -- the world's realised departure rate, which is `_PRINCIPAL_SUBJECT` above and
is band-checked every run"*. **That band check is one of the two tests currently red**, and its own
assertion message says why it is red: *"a control over an emptied subject reports a constant PASS"*,
with 7 years of margin instead of 8. So the single indirection the register relies on to hold this
quantity accountable is, at HEAD, not holding it. That is what made a silent 1.98x on 2022 survive a
capture, a fit and two preregistrations. **It is outside this stretch's pathspec and is recorded as
owed, not repaired here.**

## Constraints honoured — checked against the file, not against my intentions

1. **No constant pasted, edited or deleted.** `git diff -U0` filtered to `YEAR_LEVEL_ANCHOR` and any
   year line returns **empty**. The ten values are byte-identical. *(Both prior preregs on this file
   certified this same constraint by recalling what their author had not done, and `9a03f3b44`
   established both were wrong — the file had been dirty since 2026-08-31 carrying a seven-year
   block in no commit. So this one is discharged by reading the artefact.)*
2. **G4 was refuted-shaped and nothing was silenced.** No test was skipped, narrowed or xfailed, and
   the guard was not weakened to buy a green. The two reds are pre-existing and are named above with
   what they cost.
3. **The reference-year fallback is not deleted.** It is retained for years outside the record and
   G2 pins it.
4. **The false directional sentence is corrected, not deleted.** The docstring now carries what the
   old claim was, that it was measured false on the case it fired on, and the ratio table that
   refutes it.

## What is owed next

1. **Repair the band control's emptied subject** (7 years, not 8). It is the only thing holding the
   level anchor accountable and it is red at HEAD. Outside this pathspec.
2. **Re-fit and land a `YEAR_LEVEL_ANCHOR` block from a capture whose producer is in git.** The
   native capture's block is still recorded-not-adopted, and `/tmp/svtcap2`'s clean-tree run wrote
   an **empty** SVT sibling (2 bytes), so the whole-book route currently has no reproducible fit.
3. **Grade `9a03f3b44`'s "exactly 2.00x".** It is 3.053619 / 1.524110 = **2.0035x**, not exactly
   2.00x. The mechanism it names is unaffected; the word "exactly" is not earned.
