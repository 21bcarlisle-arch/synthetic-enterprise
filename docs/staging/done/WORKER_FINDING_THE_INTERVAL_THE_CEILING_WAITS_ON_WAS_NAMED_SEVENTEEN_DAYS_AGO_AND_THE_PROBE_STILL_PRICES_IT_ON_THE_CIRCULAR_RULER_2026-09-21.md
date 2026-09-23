**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKER] The interval the ceiling waits on was named 17 days ago, and the probe still prices it on the circular ruler

*2026-09-21, worker tick. Lane 0, claim `the-capacity-that-refuses-the-thesis-book-stands-on-nothing`.*

---

## The one-sentence result

`SETTLEMENT_CUSTOMER_YEAR_BUDGET` is refused a basis by its own note's closing sentence — *"nothing
bounds this constant at 1,200 except an interval preference nobody has stated"* — and **that
sentence has been false since 2026-09-04**, when the director named the interval. Nothing re-asked
it, so the ceiling has spent 17 days waiting on a decision that was already in the tree.

## What was found, in the order it was found

### 1. The interval is stated, and it is weekly

`background/publish_freshness.py`, carrying him verbatim:

> *"The site publishes numbers and runs once a week, thoroughly and robustly, not every half hour
> ... The reason is cost. Three of the last five days had multi-hour publish outages, and fixing
> them has taken more of your time than the content ever has."* — director, 2026-09-04

```python
PUBLISH_CADENCE_SECONDS = 7 * 24 * 60 * 60   # 604,800s
```

The module declares itself *"the SINGLE SOURCE OF TRUTH for that cadence"*.

**The constant's reasoning was right and this is a confirmation, not a retraction.** §7 of
`SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md` refused to invent an interval and located it as the
director's to name. He named it six days later. What failed is only that nothing carried the answer
back to the question — the same shape as the VAT rule, one decision with several readers and no
edge between them.

### 2. And the probe that prices the ceiling reads a DIFFERENT cadence — the circular one

`tools/settlement_ceiling_probe.publisher_context()` takes `cadence_seconds` from
`docs/observability/publish_gate_duration.jsonl`. Every one of the last 20 rows carries **5,400**.
That field is stamped by `background/suite_duration_watch.PUBLISH_CADENCE_SECONDS`, whose own
comment still reads:

> *"it is not a budget anyone chose; it is a measurement of how often runs actually arrive"*

That is **exactly** the constant the ceiling's note records as removed for circularity — *"run
duration sets marker inter-arrival, so raising this ceiling raised the bound it was checked against,
in the flattering direction"* — reached again by a second route nobody re-asked. Two live publish
cadences in one tree, **112x apart** (604,800 / 5,400).

**The probe was built for this and the mechanism was never used.** `recommend()` takes a CHOSEN
`publish_interval_s`, sets `bounds.time.chosen`, and prints a `circularity` paragraph when it falls
back. Grep says **no caller has ever passed one**. So `chosen: false` on every reading the probe has
ever produced, and every ceiling it has ever recommended carries the circular bound.

**This is the reason measuring first would have produced a wrong ceiling.** A clean wall clock taken
today and divided into 5,400s recommends a number off a ruler that moves with the answer.

### 3. What this does to the arithmetic

| leg | against 5,400s (circular) | against 604,800s (declared) |
|---|---|---|
| time | the binding leg | not binding, by orders of magnitude |
| memory, re-ruled to retained records | 38,275 cy — an **upper bound**, not a measurement | same |
| requirement to sign the choosing | 3,163.9 cy | same |

At a weekly interval the time leg stops binding and **memory is the only leg left with evidence
behind it** — and its own figure is an upper bound sitting ~12x above what the smallest leg needs.
If that survives the measurement, nothing bounds 1,200 and the constant's own history is all that
holds it there.

## The measurement, in flight

Launched 2026-09-21T15:38Z, `background.launch_long_job` (cgroup-verified), unit
`longjob-settlement-ceiling-slope`:

```
--budgets 1200 2000 2800 3400 --publish-interval 604800 --menu-intervals 5400 86400 604800
--json docs/observability/settlement_ceiling_slope_20260921.json
```

- **The box was made quiet, not assumed quiet.** `docs/review_gates/.sim_runner_hold` set with its
  reason; the job's last step removes it, so the hold cannot outlive the measurement by being
  forgotten. `tools.wait_for --pid` held 960s for the live `run_annual_report` to finish before the
  first point — §6a refuses a wall clock taken under contention, and the probe independently skips
  any point with a producer in flight.
- **3,400 is above what the funnel can supply** (~2,358 cy to settle all 505 wins, plus 778 committed
  by founders). That point saturating IS an answer: it measures whether this world can reach the
  requirement at all, which the drawn item names as a complete result.

**A CAVEAT THAT IS MINE, RECORDED RATHER THAN HOPED AWAY.** The 1,200 point started while two gate
runs were still on the box — another lane's publish gate and my own `surgical_land`. The probe's
`clean` flag watches for a *producer* run, not general load, so it will not catch this. **If the
1,200 point lies above the curve the other three describe, that is why, and it should be re-taken
rather than believed.** The later points are on a box the hold keeps quiet.

## What is NOT done, deliberately

**No new value is written for `SETTLEMENT_CUSTOMER_YEAR_BUDGET`.** A stated interval is not a
ceiling — a cost curve turns it into one. Writing 1,200 → anything from the stale slope would be
this file's own forbidden move arriving with a better-dressed justification than the last one.

**What the code should carry instead of 1,200, when the curve lands:** the value
`recommend(..., publish_interval_s=604800)` returns as `supported_customer_years`, with
`binding_bound` naming which leg set it and `binding_bound_is_evidence` recording whether that leg
is a measurement or a preference. The constant's origin note then cites the artefact, the interval
and the date — which is what "an origin naming a measured cost curve and a stated interval" means.

## Owed, and not claimed as done

1. **`settlement_ceiling_probe` should read the declared cadence, not the gate log's.** Working
   around it with `--publish-interval` on the command line leaves the default wrong for the next
   caller. The fix is `publisher_context()` reading `publish_freshness.PUBLISH_CADENCE_SECONDS` and
   reporting the gate log's figure as *observed arrival*, which is the only thing it is evidence of.
2. **`suite_duration_watch.PUBLISH_CADENCE_SECONDS` is 112x from the declared cadence** and is the
   alarm threshold for gate speed. Whether it should track the declaration or stay a measurement of
   arrivals under a different name is a real question, and it is not this claim's to settle —
   its cadence log is a careful, dated record of a deliberate method and deserves that treatment.

Both are one subject: **one declared cadence, three implementations, and no edge between them.**

---

*Companion corrections, both written beside their claims rather than over them:*
`simulation/net_new_acquisition.py`'s constant note, and
`WORKER_RESULT_THE_TWO_CEILINGS_SHARE_A_RULER_NOW_..._2026-09-21.md`, whose closing sentence
("a publish cadence nobody has named") quoted the note and inherited its error — **and whose
2,902 / 2.42x row multiplied one run's book by another run's customer-years.** Neither published
denominator was stale; the product crossed two runs. Now stamped and controlled:
`can_a_book_that_size_be_built.the_book_these_figures_are_denominated_in`.
