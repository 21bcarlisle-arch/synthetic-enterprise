**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# The corrected record makes the world look WORSE, not better — and the page was comparing shoppers to everybody

**Measured:** 2026-09-09, delivery seat, from artefacts already on disk. Closes the Lane 0 delivery
item *the-world-lets-customers-leave-twice-as-readily-as-the-record-and-the-record-is-itself-disputed*
on all three of its ordered legs. **Class:** `figures_on_a_superseded_clock`.

## The one-sentence result

The drawn item asked whether the world still departs at ~2x once the switching band is corrected;
the answer is that **on the quantity the page publishes it gets worse — 1.63x becomes 1.80x — and on
the quantity the record actually counts it is 1.14x**, because the page has been comparing a mean
over households who demonstrably shop against a band stated over every account.

## Leg 1 — the two findings are ONE defect, and the duplicate dispositioned itself

`SEAT_FINDING_THE_SWITCHING_RATE_ARTEFACT_IS_REFUTED_BY_ITS_OWN_PUBLISHER_IN_EIGHT_OF_TEN_YEARS_2026-09-07.md`
already carries the reconciliation in its own header: two lanes reached the same conclusion
concurrently, `f706dbf3d` landed first, and **that document was rebased to be additive rather than a
second account.** It says so, names what it adds that the other does not — the machine-readable
`values_refuted_by_the_publisher` block and its control, the root-cause correction in
`churn_price_elasticity.md` §1, the knowledge-map row, and the ElectraLink fuel scope — and discards
its own artefact text in favour of the other lane's.

**So there is no duplicate to dispose of and nothing to work twice.** The drawn item's leg 1
predicted a disposition; what it found is a disposition already made, correctly, by the losing lane
about itself. Recorded rather than quietly skipped, because the item's own ranking rested on the
belief that two documents were narrating one discovery, and the interesting fact is that the
mechanism for that already fired without anybody drawing it.

The premise check the doorbell ran is also confirmed spent in the direction it warned about:
`f706dbf3d` is an ancestor of `origin/main`, and so is `a82112ac2`, the second lane's landing.

## Leg 2 — the commons was NOT re-sited, and that is the third lane to measure the same reason

Both 2026-09-07 findings measured, independently, that correcting `rates` in place is not a
standalone edit: `simulation/departure_level_anchor.py`'s `YEAR_LEVEL_ANCHOR` is fitted to each
band's HIGH endpoint, `tools/fit_year_level_anchor.py --internal-return` refuses outright against
the corrected record, and six committed verdict blocks derive from a world capture produced under
these rates. Re-checked here rather than taken on trust: **`tests/architecture/test_switching_rate_commons.py`
is 101 passed / 2 xfailed at HEAD today**, and every containment control in it reads `rates` live.
The hazard is unchanged and the deferral stands.

**What was WRONG about the deferral is that it also bought silence.** Two documents in the staging
root said the standard was refuted; the commons said so about itself in a machine-readable block; and
every consumer in the tree — this instrument, the level anchor, the value-arms page — went on reading
`rates` and only `rates`. A refutation nobody can read past does not delay a wrong number, it
publishes one for longer. **That is what this landing fixes, and it is not the re-siting.**

`tools/measure_departure_level.py` gains `publisher_rates()`, `band_is_refuted()` and
`publisher_comparison()`: the same levels, same years, read against DESNZ QEP 2.7.1's own figures as
the artefact already tabulates them. The module that owns the denominators owns this too — a second
implementation on the page would have been a second answer within a week.

## Leg 3 — the verdict, stated both ways because which record you take changes the answer

**On the reading the page publishes** — the world's mean expected departure at a renewal decision:

| year | world % | refuted band % | publisher % | vs band | vs publisher |
|---|---|---|---|---|---|
| 2017 | 23.96 | 13.5–14.0 | 18.195 | 1.74x | **1.32x** |
| 2018 | 25.97 | 19.5–20.0 | 19.064 | 1.32x | **1.36x** |
| 2019 | 31.70 | 20.7–21.3 | 20.822 | 1.51x | **1.52x** |
| 2020 | 40.98 | 22.5–23.0 | 20.213 | 1.80x | **2.03x** |
| 2021 | 26.05 | 17.9–18.4 | 15.569 | 1.44x | **1.67x** |
| 2023 | 15.75 | 8.9–12.5 | 6.332 | 1.47x | **2.49x** |
| 2024 | 32.12 | 12.5–16.1 | 9.028 | 2.25x | **3.56x** |
| **mean** | **28.08** | 17.20 | **15.60** | **1.63x** | **1.80x** |

**The corrected record moves the world FURTHER from the standard, not toward it.** The commons' own
`what_this_block_does_not_settle` predicts the opposite — *"the record is about to move TOWARD the
world"* — and it is right about the subject it names (`departure_level_anchor`'s fitted years sit
BELOW their bands) and wrong about this one. **Two readings of "the world's switching" disagree in
SIGN, and the artefact records only the flattering one.** The refuted band was the kinder standard
in every year and by 3.6x in 2024.

## And the reason both figures are the wrong question

`tools/measure_departure_level.world_book_rate_pct`'s own docstring calls itself *"the comparable
quantity, at last"* and says of the column the page actually publishes that **"a mean over shoppers
is not the book's departure level"** — post-C1b, a renewal decision is a household who took a fixed
deal. The page's `denominator` field nevertheless declared *"over all GB domestic electricity
accounts"*. **It declared one quantity and published another, against a band stated on the first.**

Every departure the world expects on either route, over the accounts on the book:

| year | whole book % | publisher % | ratio |
|---|---|---|---|
| 2017 | 14.00 | 18.195 | 0.77x |
| 2018 | 20.00 | 19.064 | 1.05x |
| 2019 | 21.30 | 20.822 | 1.02x |
| 2020 | 22.97 | 20.213 | 1.14x |
| 2021 | 18.53 | 15.569 | 1.19x |
| 2022 | 2.50 | 3.056 | 0.82x |
| 2023 | 12.40 | 6.332 | 1.96x |
| 2024 | 15.96 | 9.028 | 1.77x |
| **mean** | **15.96** | **14.03** | **1.14x** |

**The drawn premise does not survive the comparable quantity.** "Customers leave twice as readily as
the record" is 1.14x on the population the record counts, and 6 of 8 years sit inside even the
refuted band. Most of the gap this page has been reporting is the population it was measured over.

**WHAT MUST NOT BE CONCLUDED IS THAT THE WORLD IS FINE**, and this is written before anyone can file
it as a win. The whole-book column is the anchor's own fitted target, so its agreement with the
*refuted* band is by construction and says nothing; its 1.14x against the *publisher* is the live
question, 2023 and 2024 run 1.8–2.0x, and 2021 and 2022 sit outside the band in opposite directions.
How much of that is the world is exactly what the re-capture is for and **is not established here.**

## What landed

* `tools/measure_departure_level.py` — the publisher-side reader, the refutation predicate, and the
  comparison; printed by the CLI beside the band table so a human reading the instrument cannot
  stop at the refuted half.
* `tools/generate_value_arms_data.py` — the page block gains `against_the_publisher`, the comparable
  `whole_book` reading with its own publisher comparison, and a composed `bounding_statement`. The
  false `denominator` sentence is **corrected in place, beside the number it describes.**
* `site/capabilities/index.html` — the caveat and a per-year publisher table reach the reader.
* `site/test_the_baseline_comparison_reaches_the_reader.py` — two controls: the reader is told the
  band its own publisher refutes, and a null rung proving the page is not printing a constant. Four
  mutations fire; a fifth is established as an equivalence rather than assumed to be one.

**Keyed to the artefact's declaration, not to today's answer.** When the re-capture lands and
`values_refuted_by_the_publisher` goes with it, `publisher_comparison` returns unavailable, the
caveat leaves the page, and the control asserts it is GONE. Nothing here can rot into a stale
apology somebody has to remember to delete.

## What is next

1. **Re-site the page's headline onto the whole-book reading.** Filed as its own finding, not done
   here: it moves a published figure from 1.63x to 1.14x and a headline move needs a preregistration
   written before the number, not a paragraph in a result document that already knows it.
2. **The re-capture landing** is unchanged and still owns the band itself — correct `rates`,
   re-capture, regenerate the six verdict blocks, re-fit `YEAR_LEVEL_ANCHOR`.
3. **The commons' `what_this_block_does_not_settle` names one direction and there are two.** It
   should say that the sign of the move depends on which reading of the world you take, and that the
   published one moves away. Not edited here — the block is another lane's landing and the correction
   belongs beside the re-capture that resolves it.
