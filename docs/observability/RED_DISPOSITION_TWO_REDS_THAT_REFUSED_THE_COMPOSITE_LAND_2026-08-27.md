**Severity:** MEDIUM · **Lane:** H_harness · **Date:** 2026-08-27

# Both reds that refused the composite land are pre-existing at clean HEAD, and neither was caused by the widened world

`docs/observability/three_arm_composite_run.log` ends `END rc=1 PHASE=land` at 19:55:59Z after
`2 failed, 485 passed in 621.40s`. The land was blocked on two reds, and nobody had established
whether the working-tree diff **caused** them or merely **exposed** them. That one check decides
the disposition, so it was run first.

## Method

A throwaway detached worktree at clean `HEAD` (`62596694d`), `git status --porcelain` = **0
modified paths**, verified in-log before either test ran. Each red was then run there alone. The
worktree was removed afterwards — it is deliberately not a fourth entry in the standing
undeclared-worktree accretion alarm.

Every claim below is labelled `observed` or `inferred` per R9.

---

## Red 1 — `test_the_run_emits_a_treasury_drawdown_register`

**Verdict: PRE-EXISTING. The widened world did not cause it. `observed`.**

At clean HEAD the test fails on the **identical assertion at the identical line** —
`tests/simulation/test_run_phase2b.py:359`, "no year in this window distinguishes accumulation
order from date order" — in 48.97s, with no working-tree diff present. The doorbell's hypothesis
that this "may well be the widened world changing the book" is **refuted by observation**.

### Root cause — and the null control is RIGHT, not stale

The control was suspected of having "stopped discriminating". It has not. It is a correct R15
control that is correctly firing, and what it is reporting is true. Measured on the same
2016–2017 fixture (`/var/tmp/probe_treasury.py`, run with `gap_ledger_path` routed to tmp;
live ledger md5 `b690924b…` unchanged before and after):

| quantity | value |
|---|---|
| `all_records` | 13,486 rows (8,251 of them folded, so the fold IS wired) |
| register points | 325,841 |
| book drawdown events | **0** |
| register drawdown events | **0** |
| treasury path | £250,000 → £254,242 over the whole window |

`_drawdown_events` (`saas/reporting/annual_report.py:229`) records only peak-to-trough falls of
at least `DRAWDOWN_THRESHOLD_PCT = 0.10`. **This window contains no 10% drawdown at all.** With
zero events on both sides, the containment assertion above the null control —
`for year, events in book_events.items(): for event in events: assert event in reg_events…` —
iterates over nothing and asserts nothing. The null control exists precisely to say so, and it
does.

Note what is *not* the cause: the book is **not** already in date order (`already sorted: False`,
12,024 duplicate keys). The ordering premise is alive. Both orderings simply yield `[]`.

**The defect is the fixture WINDOW, not the control.** The window was truncated from the full
decade to 2016–2017 as a throughput optimisation. That truncation removed every year in which the
treasury actually draws down, silently converting a real control into a vacuous one — and the null
control is the only reason anybody found out. `inferred`, from the truncation comment at
`tests/simulation/test_run_phase2b.py:205-217` plus the measured 0/0 above.

### Where its control still runs

Nowhere else — and that is the point. It is not excluded from any gate; it is selected whenever
`simulation/run_phase2b.py` is touched (`tests_for()` → `test_run_phase2b.py`). It has been red at
HEAD for some time without blocking commits only because no commit had touched that file. Landing
`run_phase2b.py` is what surfaced it.

### Repair — QUEUED, deliberately not done here

The legal fix is to give the containment assertion a book that actually contains a drawdown,
without paying the full decade in the hot path. It is **not** to lower the 10% threshold, delete
the null control, or exclude the file — all three would be weakening a control that is telling the
truth. This is its own piece of work with a real design choice in it (extend the window to the
cheapest year containing a ≥10% drawdown, versus split the containment property onto a constructed
book and keep only the fold/size assertions on the fast window). Sizing that choice needs a search
over windows, which is exactly what does not belong inside a land.

---

## Red 2 — `test_pass_through_customer_in_fast_run`

**Verdict: PRE-EXISTING. The widened world did not cause it; it changed where it fails. `observed`.**

At clean HEAD this test dies at `live_ledger_guard` — the guard correctly refusing a test process
writing the live coupled-gap ledger, with no route past it because `main()` had no
`gap_ledger_path` parameter. Red either way. Measured in the same clean-HEAD worktree:
`background.live_ledger_guard.LiveLedgerWriteUnderTest`, `1 failed in 734.93s (0:12:14)` — so the
whole 12-minute pipeline is spent to reach a refusal that has nothing to do with what the test is
for. With the diff it reaches its real assertion and fails
there instead (`C_IC3 should have settlement records in fast mode`, `assert 0 > 0`), already
recorded in `docs/staging/done/WORKER_FINDING_THE_PASS_THROUGH_IC_CUSTOMER_PRODUCES_NO_RECORDS_AND_NO_GATE_CAN_SEE_IT_2026-08-27.md`.

Moving a red from an infrastructure refusal to the defect it was masking is strictly an
improvement, but it is still a red, so the test file cannot land until C_IC3 is fixed.

### The R4 comparison that finding asked for, now done

The nearest working analogue is `C_IC1`, same roster, sibling test passes. The diff, `observed`:

- `C_IC3` **is** in the roster (`saas/customers.py:189`) — not absent.
- `sim/hh_data/C_IC3.csv` **exists**, 3,447 rows, `2016-01-01` → `2025-06-07` — **byte-range and
  row count identical to `C_IC1.csv`**. Not a missing or short data file.
- It **is** present in `EFFECTIVE_EAC_KWH` (`simulation/run_phase2b.py:240`), which resolves its
  `eac_kwh=None` from the HH data like every other HH customer.
- `SIM_FAST_MODE` does **not** filter the roster — its only effect anywhere is swapping the risk
  committee for a deterministic mock (`sim/risk_committee_agent.py:180`). Fast mode is not
  excluding it.

So it is **dropped at a seam downstream of EAC construction**, and the only roster field that
distinguishes it from the passing analogue is `tariff_type: "pass_through"`. `inferred`.

### Repair — QUEUED

Locating that seam is the cheaper subject the finding asks for, and per the drawn direction it is
explicitly **not** this item. No fourth gate exclusion was added.

---

## What landed, and what did not

**Landed** (`13ecd0186`, on `origin/main`): `simulation/customer_events.py` +
`tests/simulation/test_price_sensitivity_reaches_the_price_response.py` — the `_bill_scale_for`
fix confining the domestic switching curve to the segment its evidence covers. Its gate set is
`test_customer_events.py`, `test_customer_events_basis_risk.py` and
`test_price_sensitivity_reaches_the_price_response.py`: **94 passed in 0.57s**.

**Not landed:** `simulation/run_phase2b.py` and `tests/simulation/test_phase40a_pass_through.py`.
These are the only two paths whose `tests_for()` selection contains the two reds.

### The lesson the composite land actually teaches

The composite pathspec was never a single unit. `tests_for()` is per-path, and the four paths have
disjoint gate sets:

| path | selects | red? |
|---|---|---|
| `simulation/customer_events.py` | 2 files | no |
| `tests/…/test_price_sensitivity…py` | itself | no |
| `simulation/run_phase2b.py` | `test_run_phase2b.py` +2 | **yes** |
| `tests/…/test_phase40a_pass_through.py` | itself | **yes** |

Bundling all four made a 0.57s gate into a 621s one and then threw the result away. The clean half
was landable the whole time. **Compute the gate set per path before choosing the pathspec** — the
split is free, and it is what turned "the land is blocked" into "half of it was never blocked".
