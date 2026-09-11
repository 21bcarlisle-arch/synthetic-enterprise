**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# RESULT — P6 is taken. The chosen book's gross margin is 2.45% BELOW the cull's, and the sign is against the change

**Filed 2026-09-11, delivery seat.** Grades **P6** of
`SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md`, which
`3957ba848` recorded as **WITHHELD** with the words *"it is the first thing the next turn should
take, and until it is taken nobody should claim this change is P&L-neutral or P&L-positive."*

---

## P6, as it was written before the answer was known

> **P6 — the P&L moves, and I cannot predict the sign.** The settled book's total gross margin
> moves by **more than 1.0%** in absolute terms against the baseline. Direction not predicted.

## The measurement

Two full 2016–2025 runs at one HEAD (`3957ba848`) with **one variable**.

| | ARM A — cull | ARM B — chosen | Δ | Δ % |
|---|---:|---:|---:|---:|
| **Gross margin** | **£383,688.97** | **£374,295.73** | **−£9,393.25** | **−2.45%** |
| Revenue | £676,791.53 | £661,157.87 | −£15,633.67 | −2.31% |
| Bad debt | £11,675.76 | £14,400.86 | +£2,725.10 | **+23.34%** |
| Capital cost | £6,601.94 | £6,298.29 | −£303.65 | −4.60% |
| Net margin | £147,954.26 | £139,439.50 | −£8,514.76 | −5.75% |
| Net after cost to serve | £98,643.67 | £90,409.10 | −£8,234.57 | −8.35% |
| Final treasury | £397,954.26 | £389,439.50 | −£8,514.76 | −2.14% |
| Customers over the run | 251 | 235 | −16 | −6.37% |
| Bills issued | 10,924 | 10,841 | −83 | −0.76% |

**P6 HOLDS: |Δ| = 2.45% against a >1.0% band.** The direction was explicitly not predicted, and it
is **negative** — the chosen book earns less.

## The settled books these figures are over

At the **run's own base seed, 20260724** (`live_population._DEFAULT_BASE_SEED`), both arms face the
same 500 funnel wins and the same 0.1826 rate:

```
ARM A cull      91 settled   1,195.1 customer-years   uniform_count
ARM B chosen    83 settled   1,194.9 customer-years   chosen_weighted
```

**91 of 500 is the number the drawn item itself names.** The two books spend the same customer-year
budget to within 0.2 of a customer-year and buy **eight fewer accounts** with it.

## What I can attribute and what I cannot

**I cannot say how much of the −2.45% is FEWER accounts and how much is DIFFERENT accounts.** Two
things moved together: the book shrank from 91 to 83 settled accounts (251 to 235 customers over
the run), and the accounts are drawn from different homes. One run cannot separate them.

What the numbers do bound: **gross margin fell by 2.45% while the customer count fell by 6.37%**,
so per customer the chosen book is *richer*, not poorer. The chooser spends the same customer-year
budget on fewer, longer-tenured accounts. That is a consequence of the design and not a surprise —
`customer_years` is one of the choosing axes — but it means "the chosen book is worse" is the wrong
sentence. **The right sentence is that it is smaller at the same cost, and the total follows the
size.**

The one-variable follow-up that would separate them is a third arm: the cull, truncated to 83
accounts at the same customer-year spend. Filed as the next item rather than guessed at here.

**The bad debt leg is the one I would not have predicted and did not.** +23.34% on a book 6.37%
smaller. The chooser deliberately pulls in tails, and on this world the tails pay worse. That is
exactly the kind of fact the pre-registration said was being measured rather than argued, and it is
a finding about the WORLD, not about the chooser. It is not graded here because no prediction was
filed about it — recorded so that the next person to look does not mistake it for something that
was expected.

## Why the arms are believable

**The toggle is the documented fallback, not a second code path.** ARM A patches
`simulation.settlement_choice.choose_settled_sample` to return `None`, which is the branch
`net_new_acquisition` already takes when a candidate has no home the axes can be evaluated on. It
is byte-for-byte the systematic 1-in-1/r count cull this change replaced. Nothing else differs:
same HEAD, same seed, same world, same company plan, same funnel. `world_identity` is identical
between the two run outputs.

**The toggle reproduces `3957ba848`'s OWN published arms, exactly.** Each arm re-resolves the
campaign at **seed 42** — the measurement seed that commit used — after its run:

```
              this turn            3957ba848 published
ARM A cull    90 settled 1195.4 cy   90 settled 1195.4 cy
ARM B chosen  84 settled 1197.0 cy   84 settled 1197.0 cy
```

Both to the decimal, from a separate process on a separate day. A toggle that reproduces both arms
of an independent measurement is not selecting a convenient branch.

**Determinism was checked, not assumed.** `_campaign(_pre_growth_book(20260724), 20260724)`
resolved standalone gives 83 settled / 0.1826 / 500 funnel wins / `chosen_weighted` — identical to
what the full run wrote to `book_growth_campaign.json`. The 84-vs-83 gap between this turn's early
probe and the run is **two different seeds, not nondeterminism**: 42 is the measurement seed,
20260724 is the run's.

## What is NOT claimed, and one check still in flight

* **These are not the published figures.** Both arms ran with `SIM_FAST_MODE=1` (deterministic mock
  risk committee, no LLM calls) — identically, so the *difference* is clean, but the absolute
  pounds are not comparable to `docs/reports/run_output_latest.json`. P6 is a claim about a
  difference and is graded as one. Nothing here should be copied onto a page as a headline.
* **The two arms ran CONCURRENTLY in one worktree.** They share a `docs/observability/` directory
  and each writes `book_growth_campaign.json`. Nothing in the run path reads that record back —
  it is written "for generators in later processes" and the only in-repo readers are separate
  tools — so the runs cannot have crossed through it. **That is an argument, not a measurement**,
  so ARM A is being re-run ALONE as a falsifier: if it does not return £383,688.97 to the penny,
  this whole table is contaminated and must be withdrawn. **At the time of filing that re-run had
  not finished.** It is handed on, and until it lands this result should be read as one arm pair,
  not as a reproduced one.
* P6 says nothing about whether the chooser is right. It says the P&L moved and by how much. The
  case for choosing was never a margin case — it was 1.553× on worst-axis KS — and this result is
  the price of that, now measured instead of assumed.

## The harness

Lives at `/var/tmp/p6_arm.py`, outside the repository, because it is a measurement and not a
control and an orphan module in `tools/` would be a worse thing to leave behind. Reproduced in full
so the measurement can be re-run without it:

```python
import json, os, sys, time
ARM, OUT = sys.argv[1], sys.argv[2]
if ARM == "cull":
    import simulation.settlement_choice as _sc
    # net_new_acquisition imports this INSIDE the function body, so patching the module
    # attribute here is what the call site resolves at run time.
    _sc.choose_settled_sample = lambda *a, **k: None
os.environ["SIM_FAST_MODE"] = "1"
from tools.run_annual_report import (
    extract_report_data, reconcile_and_stamp, run_phase4c_on_phase2b)
raw = run_phase4c_on_phase2b(report_end=None)
data = reconcile_and_stamp(extract_report_data(raw), code_commit="p6-arm-" + ARM)
from simulation import live_population as lp
camp = lp._campaign(lp._pre_growth_book(42), 42)          # the 3957ba848 cross-check
data["_p6_campaign"] = {
    "settled_wins": sum(r["wins"] for r in camp["by_year"]),
    "customer_years_committed": camp["customer_years_committed"],
    "settlement_selection": camp.get("settlement_selection"),
    "settlement_sample_rate": camp.get("settlement_sample_rate")}
json.dump(data, open(OUT, "w"), indent=2)
```

Run as `PYTHONPATH=<tree> setsid python3 /var/tmp/p6_arm.py {cull|chosen} <out.json>`. Each arm
takes ~13 minutes (760.6s and 771.7s measured).

## Where this leaves the pre-registration

Of the ten predictions, **seven now hold, three fail, none is withheld.** P6 was the only one
outstanding and it holds. The three failures (P2, P3, P9) are graded in
`SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md` and none is disturbed by this.
