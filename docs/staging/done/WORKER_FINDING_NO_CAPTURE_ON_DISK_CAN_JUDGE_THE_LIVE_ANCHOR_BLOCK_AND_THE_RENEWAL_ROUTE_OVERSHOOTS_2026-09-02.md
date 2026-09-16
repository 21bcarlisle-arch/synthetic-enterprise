**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# FINDING — no capture on disk can judge the live anchor block on the whole-book quantity, and on the one route that IS readable the world overshoots the record

**Found 2026-09-02, delivery seat, on the drawn Lane 0 item.** Pre-registered before the run in
`WORKER_PREREGISTRATION_WHETHER_ANY_CAPTURE_ON_DISK_CAN_JUDGE_THE_LIVE_ANCHOR_BLOCK_2026-09-02.md`;
every prediction is graded there beside its filed text, misses kept.

## First: three of the drawn direction's premises are stale, verified not assumed

The item was drawn to take the level-anchor collision decision. **That decision has already been
taken**, at `d374b1977`, and the two follow-on items the direction names as owed are also already
repaired:

| Direction says | Measured at HEAD |
|---|---|
| the tree carries a ten-year block; the seven-year fit exists only in a staged document | `git status --porcelain simulation/departure_level_anchor.py` is **empty**; HEAD carries the **seven-year** block plus the FITTED/`UNFITTED_YEARS` partition |
| "land that document first, it is in no commit" | `docs/design/UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md` is committed at `9238075d9`, byte-identical to HEAD |
| `population_anchor.py:490` still resolves a measured zero, "verified still present" | the `.get("sim_churn_rate", 0.0)` is **gone**; it reads `.get("sim_churn_rate")` with a named `rate_2022_unavailable` refusal |

The collision is answered in the module: 2016/2025 take the reference year's anchor as years the
fit never claimed; 2022 takes `NO_LEVEL_CORRECTION` as a year the fit claimed and could not
identify; the capture scope of the zero-rows premise is stated on the entry itself. What was **not**
settled, and is what this stretch establishes, is whether that answer can be **checked**.

It cannot.

## The finding: the two properties needed to judge the block live in different artefacts

To judge `YEAR_LEVEL_ANCHOR` on the quantity the published band is actually about — the whole-book
union over accounts — a capture must have **both** (a) a readable SVT sibling, so both departure
routes can be seen, and (b) an as-run `sim_level_anchor` column carrying the live block, so the
reading is about the table now committed. Measured across every capture on disk, from a clean
`git archive HEAD` stem:

| capture | rows | SVT sibling rows | fitted years matching the live block | whole-book readable |
|---|---|---|---|---|
| `c2_departure_factors.json` | 148 | **0** | **7 / 7** | **no** |
| `ladder_churn_factors.json` | 144 | **1266** | **0 / 7** | **yes** |
| `c3_shown_price_departure_factors.json` | 459 | 0 | 0 / 7 | no |

**`c2` ran under the live block but cannot see the SVT route. `ladder` can see both routes but ran
under the retired ten-year table.** No capture has both. The whole-book leg
`test_the_whole_book_departure_level_is_inside_the_published_band` therefore cannot be discharged
from anything on disk, and its refusal is the honest answer rather than a gap a re-fit closes.

This is not a drift that crept in. It is the direct consequence of the capture chain HEAD's own
docstring records — ten-year block → `ladder` capture → seven-year block → `c2` capture — because
`c2` was taken **without** the SVT sibling that `ladder` has. The fit's input and the fit's judge are
one step out of phase with each other, permanently, until a re-capture runs under the live block
*with* its sibling.

**The honest disposition is "we cannot tell", and it belongs on the surface.** Neither table can be
justified on the whole-book quantity from artefacts already here.

## And on the route that IS readable, the world OVERSHOOTS — six years above, one below

This refuted my own filed prediction, which is the reason it is worth reporting. I predicted all
seven readable years would sit BELOW the band, on the strength of the 3.45x-short framing that runs
through the anchor module's docstring and through the drawn direction itself. Measured, from the
byte-identical capture, at both `f97c34eb0` and HEAD:

| year | renewal-route reading | published band | direction |
|---|---|---|---|
| 2017 | 15.12% | 13.5–14.0% | **ABOVE** by 1.10pp |
| 2018 | 25.77% | 19.5–20.0% | **ABOVE** by 5.80pp |
| 2019 | 28.10% | 20.7–21.3% | **ABOVE** by 6.80pp |
| 2020 | 38.89% | 22.5–23.0% | **ABOVE** by 15.90pp |
| 2021 | 23.40% | 17.9–18.4% | **ABOVE** by 5.00pp |
| 2023 | 2.81% | 8.9–12.5% | BELOW by 6.10pp |
| 2024 | 22.34% | 12.5–16.1% | **ABOVE** by 6.20pp |

**The marker's seven numbers were already exactly right and are unchanged.** I first read them as
sign-flipped and that was my error, corrected here rather than quietly: `band_margins` returns
`(value - lo, hi - value)`, the marker quotes whichever element came back negative, and all seven
reproduce to the digit. What the marker did not carry is the **direction**, because a bare negative
does not say which edge it came off — and the list is the HIGH element in six years and the LOW
element in only one.

That omission is load-bearing rather than cosmetic. Every surrounding narrative primes the reader
the wrong way: the module docstring's *"the world still ran 3.45x below the published record"*, the
block's *"moves hard AGAINST the company — from losing 4.50% per renewal to the record's 15.50%"*,
and the drawn direction's own restatement of the same. A reader meeting `2020 -15.90pp` in that
frame reads *15.9pp short*. It is **15.9pp over**. The discharge instruction the marker carries —
*"re-fitting `YEAR_LEVEL_ANCHOR` against the committed capture"* — must therefore **lower** the
anchor in six years and raise it in one; taking the sign on trust moves six of seven the wrong way.

The direction is now stated in the marker reason, with the readings and both commits it was measured
at. The margins, the verdict and the leg's subject are untouched: this adds a disclosure, it does not
re-key the leg to today's answer.

### Why the overshoot is expected once the two populations are separated

It is not evidence the block is wrong. The anchor is fitted by `fit_year_anchor_on_book` onto a
**whole-book** target — both routes unioned within an account, meaned over ACCOUNTS. The leg that
overshoots reads `world_realised_rate_pct`, a mean over renewal **DECISIONS**, which post-C1b is the
selected sub-population that took a fixed deal, i.e. the households who demonstrably shop. Applying a
whole-book calibration to the shoppers and comparing against a whole-population published rate
overshoots by construction. That is the same definition split this project keeps paying for, and it
is exactly why the whole-book leg was written. It also means **the overshoot cannot be repaired by
re-fitting either** — the quantity is mismatched to its band, not miscalibrated.

## What is owed, and what must not be done

* **A re-capture under the live block WITH its SVT sibling** is the only thing that discharges the
  whole-book leg. Until it runs, "we cannot tell" is the verdict.
* **Do not widen the band. Do not re-key either leg to today's readings. Do not clamp or interpolate
  2022.** Both legs stay strict `xfail`; both must break loudly on the day they are genuinely fixed.
* **Do not read the renewal leg's overshoot as a reason to lower the block.** The block is fitted to
  a different population than that leg reads; lowering it to satisfy the leg would fit the world to
  the shoppers, which is the defect the whole-book union was built to remove.

## Constraint check, discharged by reading the artefact

No constant was pasted, edited or deleted in `simulation/departure_level_anchor.py`:

```
$ git status --porcelain simulation/departure_level_anchor.py tools/population_anchor.py
(empty)
$ git diff --stat -- simulation/departure_level_anchor.py
(empty)
```

The only code change in this stretch is the added direction paragraph in the `xfail` reason at
`tests/architecture/test_switching_rate_commons.py`.
