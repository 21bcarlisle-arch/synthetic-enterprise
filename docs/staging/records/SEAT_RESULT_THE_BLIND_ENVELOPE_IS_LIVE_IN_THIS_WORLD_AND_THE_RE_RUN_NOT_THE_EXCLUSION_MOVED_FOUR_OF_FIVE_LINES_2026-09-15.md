# The blind envelope is live in this world, and the re-run — not the exclusion — moved four of five lines

*Seat result, 2026-09-15. Landed on top of `dc024bed3`.*

## What the page said this morning, and what it says now

`site/data/value_arms.json` at origin carried `blind_envelope.available: false` with a `why_not`
naming five books that had no record of which houses they ran on. It now carries a span over three
blind books, all stamped `35f8efe8ff02f245` — this tree's live home stock — with the fourth blind
book excluded by name and by reason on the page.

The mode stamp the drawn item made step (1) **was already landed** before this turn started, and
the grep it asked for says so: `tools/run_annual_report.py:208` `_execution_mode`, wired into
`run_identity_fields` at `:378`, reading `SIM_FAST_MODE` through the same predicate
`sim.risk_committee_agent.invoke` branches on. All four first-hand arms carry it. So did the four
re-runs, filed in `dc024bed3`. Steps (3) and (4) were also already done for four of the five arms.

**What was actually blocking the reader was none of those.** It was that
`_blind_envelope_homes_refusal` refused the WHOLE block while ANY arm lacked a home stamp — and
ARM C' can never have one. Its run output is on a fork that never reached origin, and re-running it
here would be a different arm, not that one. So the guard was withholding three arms that had met
the precondition on account of the one arm that never can. **A precondition one subject can never
meet is a wall, not a control.**

## The change

A MISSING home stamp is now an **exclusion**, named on the page with the arm's own reason. A WRONG
one is still a **refusal** of the whole block. That asymmetry is the whole of the repair and it is
what stops "drop the arm that cannot be placed" sliding into "drop the arm that spoils the answer":
no arm that states a world can ever be dropped for stating the wrong one.

The floor is counted AFTER the exclusion, so five filed arms two of which cannot be placed is a
three-arm envelope and is refused, not published as though the floor had been applied.

## The result, and it is not the one the 09-11 record published

| line | span | chosen | position |
|---|---|---|---|
| gross margin | £378,405.65 – £383,215.23 (1.27%) | £381,542.41 | INSIDE |
| revenue | £679,554.13 – £690,290.81 (1.58%) | £675,945.72 | BELOW all, by −0.53% |
| bad debt | £8,331.16 – £10,814.12 (29.80%) | £8,359.26 | INSIDE |
| net margin | £144,101.90 – £148,282.17 (2.90%) | £148,623.22 | ABOVE all, by +0.23% |
| net after cost to serve | £94,836.00 – £97,948.85 (3.28%) | £99,380.18 | ABOVE all, by +1.46% |

**Two things changed at once, so I measured them one at a time rather than attributing.** The
09-11 figures are recoverable at `ea9400037`; positions recomputed over the same `_blind_line`:

| line | (a) 09-11, four arms | (b) 09-11, C' dropped | (c) re-run, C' dropped |
|---|---|---|---|
| gross margin | inside | **below all** | inside |
| revenue | inside | **below all** | below all |
| bad debt | above all | above all | **inside** |
| net margin | below all | below all | **above all** |
| net after cost to serve | below all | below all | **above all** |

**(a)→(b) is the exclusion alone: it moves two lines AGAINST the chosen book and nothing in its
favour.** (b)→(c) is the re-run alone, and it moves four of the five lines in the chosen book's
favour, including both of the ones the exclusion had just moved against it.

**So the flip is attributable to the re-run in this tree's housing stock, not to dropping C'.** The
prediction worth writing down before anyone reads more into it: **what a fabric-sighted book is
worth is a property of the housing stock, not a constant.** The stock moved from 109 distinct
fabric vectors to 105 with worst-axis KS 1.553→1.661 through `2212d0eed`, and the value of seeing a
home moved with it, by enough to reverse the sign of the headline. That is a claim about this
world's houses and it is refutable: re-draw the stock again and the positions should move again.

**The distances are thin and must not be read as the spread is.** Net margin clears every blind
book by 0.23% against a span 2.90% wide. It is one seed and an ORDERING, not an interval, and
`one_seed` says so on the page under the table. The only line where the chosen book clears the
blind ones by a distance comparable to the span is net after cost to serve (+1.46% against 3.28%).

## Correcting the 09-11 headline, beside it

`SEAT_RESULT_ON_GROSS_MARGIN_THE_CHOSEN_BOOK_IS_INSIDE_THE_BLIND_SPREAD_AND_ON_NET_MARGIN_IT_IS_BELOW_EVERY_BLIND_ARM_2026-09-11.md`
said the surviving cost of choosing was bad debt, and through it net margin, and that both cleared
the blind envelope outright. **In this tree's houses neither does.** Bad debt is inside the span
and net margin is above every blind book. A correction note is filed at the head of that record
rather than editing its claim — the prediction is worth more kept next to the result that refuted
it. Its gross-margin finding survives: "2.45% worse on gross margin" is still inside the blind
span and still not available as a cost of choosing.

## The tautology this could have shipped, and the control that stops it

With C' out of the span, `first_hand_blind == blind`, so the robustness column
(`survives_dropping_the_second_hand_arm`) would have read "holds without it" on all five lines —
TRUE BY CONSTRUCTION, about an arm that is not in the span at all, on the one row built to stop
this block flattering itself. The producer now withholds the column and says why
(`why_no_robustness_column`), the page renders that sentence, and
`test_the_robustness_column_is_WITHHELD_when_there_is_nothing_left_to_drop` fires if it comes back.
Its other half — `..._IS_reported_when_a_second_hand_arm_IS_in_the_span` — exists because the first
is satisfied by never reporting the column at all.

The heading counted its books in WORDS ("Against four books that cannot see a single home") and
would have gone on saying four over a table of three with nothing on the page to disagree. It reads
`blind_arm_count` now, under a both-branch mutation control.

## What is outstanding

* **ARM C' is not coming back.** It is an honest absence with its reason on the page, as the drawn
  item asked, and this is its settled state rather than an outstanding task.
* **A fourth first-hand blind arm would restore the robustness column** and take the span off its
  own floor. The span is over exactly three books, which is the minimum, and every verdict above is
  as narrow as that makes it.
* **The re-draw prediction above is unrun.** Nothing here tests that the positions move when the
  stock moves; it is filed as a prediction so that the next re-draw can refute it.
* Two reds were live in the shared working tree while this landed and neither is in this commit:
  `test_the_published_supplier_claim_answers_THE_SAME_from_HEADs_committed_bytes` (another lane's
  uncommitted `docs/reports/run_output_latest.json`) and the two ruff-baseline census tests
  (another lane's uncommitted `tests/tools/test_generate_maturity_map_data.py`). Both are green in
  a clean `HEAD` extract.
