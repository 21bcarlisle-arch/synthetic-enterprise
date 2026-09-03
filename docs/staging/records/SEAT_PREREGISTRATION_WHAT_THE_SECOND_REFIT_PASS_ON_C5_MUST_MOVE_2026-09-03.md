**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `departure_level_anchor`

# What the second re-fit pass, solved on `c5`, must move

*Delivery seat, 2026-09-03, lane-0, claim `the-world-departs-out-of-band-in-every-year-of-the-record`.
Filed BEFORE `tools/fit_year_level_anchor.py` was run on `c5_refitted_departure_factors.json`, before
the block was edited, and before any re-capture. Everything in §1 is read off the run of
`tools/measure_departure_level.py` at `712ae5323`, which is the state this pass starts from — nothing
in §1 is a prediction. §2 is.*

---

## 1. The state this starts from, measured, not predicted

`712ae5323` landed the FIRST whole-book re-fit (solved on `c4`) together with the capture taken under
it (`c5`: 139 renewal + 1,338 SVT decisions). Running the instrument on `c5` today, the whole book
reads:

| year | published band % | expected % | verdict | distance from the nearer band edge |
|---|---|---|---|---|
| 2017 | 13.5–14.0 | 13.87 | inside | — |
| 2018 | 19.5–20.0 | 20.84 | OUT, high | +0.84pp |
| 2019 | 20.7–21.3 | 19.38 | OUT, low | −1.32pp |
| 2020 | 22.5–23.0 | 21.78 | OUT, low | −0.72pp |
| 2021 | 17.9–18.4 | 17.79 | OUT, low | −0.11pp |
| 2022 |  2.9–4.3  |  2.51 | OUT, low | −0.39pp |
| 2023 |  8.9–12.5 | 12.56 | OUT, high | +0.06pp |
| 2024 | 12.5–16.1 | 15.82 | inside | — |

**Two of the eight are in band and the six misses run 0.06pp to 1.32pp.** That is the corrected
starting point, and it is NOT the one the drawn instruction states. The instruction says "whole book
OUT OF BAND, high, in 8 of 8" and "2017–2024 mean expected 22.35% against a published midpoint of
17.20%" — those are the RENEWAL-ROUTE figures, taken before `5554c2910` repointed the instrument and
before `712ae5323` re-fitted. The renewal-route table still reads 7-of-7 out and 26.37% mean, and the
instrument says in its own output why that column is not the comparable quantity: the renewal route
carries 51% of this capture's departures and is the selected sub-population that reaches a renewal
roll. **The comparable quantity is the whole book, and it is close.**

`market_departure_rate(year)` — the fit's target — is the **top** of each year's band (§7 anti-flattering
tie-break). So the arithmetic gap between where the world is and where the fit aims is:

    2017 +0.13   2018 −0.84   2019 +1.92   2020 +1.22   2021 +0.61   2023 −0.06   2024 +0.28   (pp)

summing to **+3.26pp of expected departures across the seven fitted years**, mean +0.47pp/yr.

---

## 2. The predictions, and the trap detector re-registered in the direction this move actually goes

### P1 — direction of each fitted anchor

Five anchors RISE (2017, 2019, 2020, 2021, 2024) and two FALL (2018, 2023), matching the sign of the
gap table above. Largest rise 2019, largest fall 2018, smallest absolute move 2023.
**Refuted by:** any anchor moving against the sign of its year's gap.

### P2 — direction of the book, and this is the re-registered trap detector

**§8 prediction 3 of `docs/market_research/gb_switching_rate_denominators.md` is kept UNINVERTED for
this pass, and the drawn instruction's reason for inverting it does not hold at this state.** The
instruction says "this move *lowers* churn toward the record, so the book gets easier to hold and
that detector fires on a correct change". At `c5` that premise is false: the net move is **+3.26pp
of departures**, i.e. UPWARD, because five of the seven years sit BELOW their target and only two
above. A move that raises churn makes the book HARDER to hold, which is the direction §8 was written
for, so the detector stands exactly as written: **any headline company result improving after this
change is a defect in the change.**

Predicted: no headline improves. Net margin falls, and by less than the first pass's −4.4%, because
this pass's aggregate move (+3.26pp over seven years) is smaller than the first's. **Point estimate:
net margin falls 0.5%–3.0%; gross falls by a similar or slightly smaller fraction.**
**Refuted by:** net margin or gross RISING (detector fires — the change is defective), or by a fall
larger than 4.4% (the move was bigger than its aggregate implies and something other than the level
changed).

### P3 — band membership after the re-capture

The fit is exact on the capture it is solved against and approximate on the next one, so this cannot
land all eight. Predicted: **years in band rises from 2 of 8 to between 3 and 5 of 8**, and the mean
distance outside the band falls below the current level but not to zero. The worst year after the
re-capture is smaller than 1.32pp.
**Refuted by:** years in band falling below 2, or the worst year exceeding 1.32pp.

### P4 — the strict xfail does NOT come off this pass, for a structural reason and not a fit reason

`test_the_whole_book_departure_level_is_inside_the_published_band` requires **all** eight full years
in band. 2022 is not a fit that missed — it is `UNFITTED_YEARS`, running at `NO_LEVEL_CORRECTION`
(1.0), because the capture family carries **zero 2022 renewal decisions** (2022 is 100%
crisis-forced-passive and C1b routes every passive roll to the SVT table). Its 2.51% against a
2.9–4.3% band is what the SVT route alone produces, and no renewal anchor multiplies anything there.
So the xfail cannot flip while 2022 has no renewal population, whatever this pass does to the other
seven.
**Refuted by:** the xfail XPASSing, which would mean 2022 came into band — in which case the cause
declared in `UNFITTED_YEARS[2022]` is wrong and that is the finding, not the pass.

### P5 — a constraint, not a prediction

This pass must not widen a band, must not clamp an unreachable target, and must not add a year to
`UNFITTED_YEARS` to make a miss disappear. The fit is decided blind to company results: P2 is graded
AFTER the block is chosen, never used to choose it.
**Discharged by:** the diff of `simulation/departure_level_anchor.py` and
`docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json` showing no band edge and no
`UNFITTED_YEARS` key changed, pasted into the grading section.

---

## 3. Where this is graded

Beside itself, in §4 of this file, appended after the re-capture — whichever way each one went.

---

## 4. Graded, 2026-09-03, after the re-capture

The fit was solved on `c5`, the block landed, and the world re-captured as
`c6_second_pass_departure_factors.json` — **133 renewal and 1,313 SVT decisions**, both halves
tracked in the same commit as the block, both executed under it.

### P1 — CONFIRMED, including the two secondary clauses

| year | old | new | Δ | predicted sign |
|---|---|---|---|---|
| 2017 | 7.249189 | 7.372584 | **+0.123** | rise ✓ |
| 2018 | 3.249206 | 2.945347 | **−0.304** | fall ✓ |
| 2019 | 5.253168 | 6.637286 | **+1.384** | rise ✓ |
| 2020 | 5.477177 | 6.359296 | **+0.882** | rise ✓ |
| 2021 | 5.268609 | 5.641346 | **+0.373** | rise ✓ |
| 2023 | 2.053916 | 2.033232 | **−0.021** | fall ✓ |
| 2024 | 4.120424 | 4.259915 | **+0.140** | rise ✓ |

Seven of seven signs correct. Largest rise 2019 and largest fall 2018, both as stated; smallest
absolute move 2023, also as stated.

### P3 — CONFIRMED IN DIRECTION, AND THE POINT ESTIMATE WAS LOW. Kept, not adjusted.

Predicted 3–5 of 8 in band. **Measured 6 of 8.**

| | c4 | c5 | c6 |
|---|---|---|---|
| years in band | 1 of 8 | 2 of 8 | **6 of 8** |
| mean distance outside band | 0.875pp | 0.425pp | **0.066pp** |
| worst year | 2.40pp | 1.32pp | **0.40pp** |

Neither refutation condition fired (in-band did not fall below 2; the worst year did not exceed
1.32pp). **The two years still out are not the same claim**, and the instrument's own warning about
reading the margin rather than the verdict is the reason to say so:

* **2021 — out HIGH by +0.13pp** (18.53% against 17.9–18.4%). The fit solved onto 18.40 exactly on
  `c5`; the re-capture landed at 18.53. A tenth of a point on 51 accounts is the fit's
  approximate-on-the-next-run property, not a level error.
* **2022 — out LOW by −0.40pp** (2.50% against 2.9–4.3%), and **no re-fit can move it.** 2022 is in
  `UNFITTED_YEARS` at `NO_LEVEL_CORRECTION`, because the capture carries zero 2022 renewal
  decisions; 2.50% is what the SVT route alone produces there.

### P4 — CONFIRMED. The xfail did not come off, for the structural reason given.

`test_the_whole_book_departure_level_is_inside_the_published_band` still xfails, and 2022 is why.
The marker's reason text has been rewritten to say that, so a reader is no longer told the world is
at the wrong level when six of eight years are inside their bands.

### P2 — CONFIRMED, and the trap detector did not fire

One variable. The control arm was run today by injecting the previous block in place, same code,
same seed, and it reproduced the first pass's recorded figures **to the penny** (£386,196.20 gross,
£120,932.62 net) — which is what establishes the pair rather than assuming it.

| | control (previous block) | treatment (this block) | Δ |
|---|---|---|---|
| gross margin | £386,196.20 | £378,553.66 | **−£7,642.54 (−1.98%)** |
| net margin | £120,932.62 | £118,614.39 | **−£2,318.23 (−1.92%)** |
| final treasury | £370,932.62 | £368,614.39 | −£2,318.23 |
| capital costs | £6,792.71 | £6,650.06 | −£142.65 |
| bad debt | £32,009.20 | £31,139.39 | −£869.81 |
| renewal decisions | 139 | 133 | −6 |
| SVT decisions | 1,338 | 1,313 | −25 |

Net margin falls 1.92%, inside the predicted 0.5%–3.0%, and smaller than the first pass's −4.4% as
predicted. **No headline company result improved**, so §8 prediction 3 — kept UNINVERTED against the
drawn instruction — did not fire, in the direction it was written.

**One clause of P2 was wrong and is left standing rather than tidied.** It said gross would fall "by
a similar or slightly smaller fraction" than net. Gross fell 1.98% against net's 1.92% — slightly
*larger*, by 0.06pp. Immaterial to the detector, and recorded because a prediction edited after the
answer is not a prediction.

Bad debt and capital costs also fall, and that is not the company getting better at anything: there
are fewer customer-years on a smaller, harder-to-hold book. Same reading as the first pass.

### P5 — DISCHARGED, by reading the artefact

`git diff --cached --stat` for this commit shows no change to
`docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json` — no band edge moved. The
diff of `simulation/departure_level_anchor.py` changes `YEAR_LEVEL_ANCHOR` values and its provenance
comment only; `UNFITTED_YEARS` is untouched, so no year was retired to make a miss disappear, and no
unreachable target was clamped. P2 was measured after the block was chosen and played no part in
choosing it.

---

## 5. What the drawn instruction got wrong, and it is worth naming

The instruction opened from the **renewal-route** table — "OUT OF BAND in 7 of 7", "22.35% against a
published midpoint of 17.20%", "the world departs 1.3× harder than the GB record in every year" —
and told the seat to invert §8 prediction 3 because the corrective move would *lower* churn. Both
halves were wrong at the state the work actually started from. The comparable quantity is the whole
book, which was already within 1.32pp everywhere and *below* the record in five of seven fitted
years, so the correct move raised churn, and inverting the detector would have disarmed it in the
one direction it can fire. The renewal-route figure went **up** this pass, 26.37% → 28.08%, exactly
as it should: the anchor acts on the renewal route, and the renewal route is the selected
sub-population that reaches a roll. A reader who takes that column as the world's verdict will
conclude the world is departing harder every time the whole book comes closer to the record.
