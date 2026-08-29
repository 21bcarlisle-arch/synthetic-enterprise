# Prediction, written after the chase-ON arm and BEFORE the chase-OFF arm finished

Written 2026-08-29, with `docs/observability/ladder_chase_on_founder_2021.json` on disk and the
OFF arm still running (`/tmp/pair_driver.log` shows `ON END rc=0`, no `OFF END`). A prediction
filed after the answer is not a prediction, so this is filed here, against a clock, before the
comparison can be run at all.

## What the ON arm alone already shows

The window extension did what it was asked to do **for the ledger** and nothing at all **for the
measured table**, and those are different populations:

* **The ledger** now carries 453 renewal decisions across 2016–2021 and realised losses in every
  year 2017–2021 (`1, 9, 6, 2, 4` at rung 0). Only the 4 losses in 2021 are wasted. Under the
  2019 window the extra departures fell in the final year and bought nothing; they now do.
* **The ladder's paired table** is still **16 decisions, and all 16 have term starts in
  2016–2018** (3, 8, 5). Not one of them is later than 2018.

The reason is rung-driven attrition inside the intersection, and it is visible in one line of the
artefact. The value arm prices, by term-start year:

| rung | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|
| 0.0 | 3 | 9 | 8 | 6 | 6 | 3 |
| 2.0 | 3 | 9 | 7 | 2 | — | — |

**The top rung has no book left after 2019.** The common population is the intersection across
rungs, so it can never contain a decision the top rung never priced. Lengthening the window adds
rows at the bottom of the ladder and none at the top, and the intersection is unmoved.

## The prediction

The beliefs of those 16 decisions read `_closed_window` over years **strictly earlier than
2016–2018** — that is, 2016 and 2017 only. Those years are the same two years they were under the
2019 window. So:

1. **The number of rungs whose mean belief differs between the two worlds will be the same as the
   2019-window pair's — most likely exactly one, and I do not expect more than two.** The window
   extension is not reaching the population being measured.
2. **The ON arm's own per-rung belief column will reproduce the 2026-08-28 pair's ON column** —
   `0.215 / 0.373 / 0.555 / 0.856` — because the measured decisions and the evidence years behind
   them are the same. *(This half is already confirmed: the ON arm printed exactly those four
   figures. It is stated here because it is the mechanism the rest of the prediction rests on, and
   because it is the thing that would have looked like a null result if it had not been chased.)*
3. **If it moves at more rungs than one, the cause will be the 2017 loss count**, which is the only
   evidence year the deeper book added below 2018 — and the census will show a `*` there.

## What would refute me

The comparison printing three or four moved rungs. That would mean the deeper book changed the
evidence in 2016–2017 enough to shift several of these early beliefs, and my account of the
bottleneck — the intersection, not the window — would be wrong.
