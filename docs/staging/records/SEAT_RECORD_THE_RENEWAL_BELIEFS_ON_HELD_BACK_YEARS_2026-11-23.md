**Severity:** S3 (a baseline, not a defect: it moves no switch and repairs nothing). Predictions filed in 9527c646a; results in §4.

# The two renewal beliefs on held-back renewal years, on the 20 Nov book

**Written 2026-11-23 by the delivery seat, for the claim
`the-renewal-belief-switch-on-has-a-held-back-baseline-from-the-20-nov-book`.** This is the baseline
for the read `read-the-ending-term-belief-grade-on-the-coming-book`
(`SEAT_PREREG_THE_ENDING_TERM_BELIEF_ON_THE_COMING_BOOK_2026-11-22.md`). It is filed before any
`run_output` built from a commit that descends from `59cd5ebda` exists. The policy file is read, not changed. No switch moves.

## 0. Premise check, done before reading any outcome

- **No earlier record gives a per-year held-back ranking for both beliefs.** `427e5f021` and
  `5cdb72eb3` grade §14's departure channel: paired arms, money, pooled across seeds. §10 of the
  arms record (`7a7ad95dc`) gives one held-back year, 2019: 0.819 conditioned against 0.333 live, on
  a 21 Oct arms book. The 22 Nov pre-registration pools 2019–2024 into one AUC. So the item is not
  already spent.
- **The 20 Nov book (`6a588a832f`, `docs/reports/run_output_latest.json`) carries no
  `desk_belief_log`.** The 22 Nov pre-registration found this and its grader refuses the book
  by name. The item's word "its desk states" therefore names nothing on disk. What the book
  does carry is 570 renewal events in `customer_events`, each with the desk belief
  (`company_churn_estimate` is the same `company_est_pre` that `desk_belief_log` writes at
  `simulation/run_phase2b.py:5148`) and its outcome. This record rebuilds the desk rows from those
  events, as stated in §1. It labels every figure as coming from **rebuilt rows**. None of them is
  a reading of the field the coming book will carry.

## 1. Method (fixed before the run)

The rebuild is one row per renewal event that carries `company_churn_estimate`:
- `account_id` is `household_of(customer_id)`.
- `term_start` is `event_date`.
- `desk_churn_belief` is `company_churn_estimate`.
- `left` means `event_type == "churned"`.
- `desk_asked` is True. Every one of these events carries a belief, and the book does not record
  whether the desk was asked.
- **`ending_term_type`** is read off the world's own roll gate. The run sets `departure_rolled`
  False only when the previous term was an SVT segment (`departure_rolled_at_renewal`,
  `simulation/customer_events.py:493`). So:
  - a row with `departure_rolled` False is `default`, or `default_after_declined_fix` when the
    same supply point's previous renewal event was `declined_fix`;
  - every other row is `fixed`.

  This is a rebuild. It can differ from `ending_term_type()` in the run in two ways. (a) A
  previous term that was neither a fix nor the default (deemed, pass-through) is typed `fixed`
  here, where the run gives None. (b) The splice flag is inferred from the order of events, not
  read.

Those rows go into the grader that landed with the 22 Nov pre-registration, unchanged:
`tools.grade_ending_term_belief_on_a_book.grade`. Its outcome is a `churned` row in
`customer_events` within 365 days. Its conditioned belief is the online ending-term ledger fed
only by earlier years. Its interval is an account-clustered bootstrap (1,000 draws, seed 7).

Per renewal year 2019–2024, I take the grader's `_point` and `_clustered_bounds` on that year's
states. I report the AUC of each belief, the paired difference, the number of states and the
number of leavers. A year with fewer than 15 leavers is reported but marked **void**, not graded.
That is the grader's own floor, applied per year.

As a secondary, the outcome widened to include the book's separate `svt_departures` list. That
list holds the drift exits, and the grader does not read it on this book.

## 2. Predictions (filed 2026-11-23 10:20Z, before the run)

| | prediction | confidence |
|---|---|---|
| **P1** pooled 2019–2024 live AUC | 0.30–0.58, point 0.45 | 70% |
| **P2** pooled conditioned AUC | above the live AUC; point 0.70 | 70% |
| **P3** pooled paired lower bound | above 0 | 60% |
| **P4** years with ≥ 15 leavers | at most two of the six | 80% |
| **P5** every non-void year's paired interval | includes 0 (too few states for a per-year call) | 65% |

Why these are lower than the 22 Nov file's Q1/Q3: this book has 570 renewal states over ten years,
and many years in 2019–2024 hold fewer than 70 of them. The rebuilt types also add noise.

## 3. What each result does

Nothing here meets the switch-on rule: paired arms with a `departure` interval above zero. So
**nothing here flips the switch**. The record is the baseline that the coming book's read cites.
- If the coming book's per-year figures fall inside these intervals, the world has not moved the
  ranking since 20 Nov.
- If they fall outside, the s.12g commits moved it, and that read must say so.
- If the rebuilt `fixed` and `default` counts here differ by more than 10% from the coming book's
  `by_type`, the rebuild is wrong, and the read must cite this record for its counts only.

## 4. The read

Run 2026-11-23 about 10:25Z on `docs/reports/run_output_6a588a832f_20261120T134224Z.json`, which is
byte-identical to `run_output_latest.json`. The script is in the appendix. I compute
`within_fixed` after the predictions, as a decomposition (§4.2). It was not pre-registered.

### 4.1 Per renewal year (rebuilt rows; outcome is the grader's: a `churned` event within 365 days)

| year | states | leavers | live AUC [95%] | conditioned AUC [95%] | paired cond − live [95%] | live AUC within `fixed` [95%] | |
|---|---|---|---|---|---|---|---|
| 2019 | 90 | 9 | 0.509 [0.341, 0.655] | 0.840 [0.742, 0.919] | 0.331 [0.226, 0.453] | 0.729 [0.526, 0.903] | void (< 15 leavers) |
| 2020 | 60 | 15 | 0.427 [0.282, 0.557] | 0.875 [0.787, 0.951] | 0.447 [0.324, 0.585] | 0.731 [0.531, 0.898] | **graded** |
| 2021 | 67 | 11 | 0.642 [0.493, 0.773] | 0.876 [0.783, 0.951] | 0.234 [0.127, 0.352] | 0.731 [0.496, 0.929] | void |
| 2022 | 0 | 0 | — | — | — | — | no renewal event carries a belief this year |
| 2023 | 30 | 0 | — | — | — | — | void, no leaver |
| 2024 | 59 | 14 | 0.237 [0.132, 0.363] | 0.927 [0.847, 0.991] | 0.690 [0.567, 0.808] | 0.262 [0.000, 0.738] (17 states, 3 stayers) | void |
| **pooled** (the grader, unedited) | 306 | 49 | 0.452 [0.377, 0.528] | 0.857 [0.811, 0.901] | 0.405 [0.341, 0.470] | 0.648 [0.551, 0.747] (105 states) | |

Pooled extras from the grader:
- 195 accounts.
- `leavers_at_fix_end_share` is 1.0.
- `multiplier_for_2019` is fixed 0.864, default 0.025, default_after_declined_fix 0.808.
- `secondary_left_at_roll` is live 0.452, conditioned 0.857.
- By type: fixed 105 states / 49 leavers, default 173 / 0, default_after_declined_fix 28 / 0.

Secondary outcome, adding the book's `svt_departures`: pooled live 0.477 [0.400, 0.555], conditioned
0.839 [0.789, 0.886], paired 0.362 [0.293, 0.430], 53 leavers. Of those, 3 are default-type, in
2019 and 2021. 2020 is unchanged. 2019's paired interval is [0.093, 0.416]. 2021's is
[0.034, 0.304].

### 4.2 What the conditioned belief's lead is made of

**Every one of the 49 leavers ended a fix.** None of the 201 default-type states left within 365
days by the grader's outcome. With `svt_departures` added, 3 did. The world rolls no departure at a
default anniversary (`departure_rolled_at_renewal`, P10c). A default household's exits go through
the SVT-segment hazard into `svt_departures`, a list the grader does not read on this book.

So the conditioned belief's lead is the type split. The online multiplier for `default` reaches
0.025 by 2019 and 0.009 by 2024. That pushes every default state below every fix-ending one. Within
a type, `condition_on_ending_term` preserves order, so within `fixed` the two beliefs rank the same
(conditioned = live). Within the fix-ending states, the live belief ranks leavers at **0.648
[0.551, 0.747]** pooled, and 0.73 in each of 2019–2021. It is not backwards there. Its pooled 0.452
is mostly a between-type error: it gives a default-anniversary household a leaving risk that the
world never rolls at that moment.

A real supplier can see this split in its own book, so learning it crosses no wall. Whether the
world's rule is true of GB households is a fidelity question (P10c), not one this record answers.

### 4.3 Predictions

- **P1 held.** Live 0.452, inside 0.30–0.58.
- **P2 held in direction.** Conditioned 0.857 > live. The point estimate of 0.70 was low.
- **P3 held.** Paired lower bound 0.341.
- **P4 held.** One year, 2020, has ≥ 15 leavers.
- **P5 refuted.** 2020's paired interval [0.324, 0.585] excludes 0, and so do all three other years
  with a figure. The type split is large enough to show in a single year.

On the rebuilt rows, the 22 Nov pre-registration's Q1–Q6 would all pass:
- Q1 0.857 is at the top of its 0.68–0.86 range.
- Q2 0.452.
- Q3 lower bound 0.341.
- Q4 share 1.0.
- Q5 default 0.025, fixed 0.864.
- Q6 306 states / 49 leavers.

### 4.4 For the reader of the coming book (`read-the-ending-term-belief-grade-on-the-coming-book`)

1. **Baseline.** The pooled and per-year figures above are the 20 Nov world's, on rebuilt rows. If
   the coming book's figures fall outside these intervals, the commits since `6a588a832f` moved the
   ranking. Say which way.
2. **Rebuild check.** Compare the coming book's `by_type` with 105 / 173 / 28 states, scaled by its
   own 2019–2024 state count. A share more than 10% off means this rebuild mistyped rows. In that
   case cite this record for its counts only.
3. **Report `within_fixed` beside Q1.** Q1 and Q3 passing will mostly re-measure the
   no-departure-at-default rule, as they do here. The live belief's skill within the fix-ending
   states (0.648 here) is the figure that says whether a better belief inside the type at risk is
   still owed. That is the retrain's subject (14 Nov pre-registration).
4. **Check where drift exits sit on that book.** If they are still only in `svt_departures`, the
   grader's 365-day outcome cannot see a default household leaving.

## Appendix: the script (run from the repo root with `PYTHONPATH=.`)

```python
"""Rebuild desk rows from a book's renewal events and grade both beliefs per renewal year."""
import json, sys
from collections import defaultdict
from tools.grade_ending_term_belief_on_a_book import (grade, _ledger, online_conditioned_beliefs,
    _states, _point, _clustered_bounds, MIN_LEAVERS)
from simulation.household import household_of

book = json.load(open(sys.argv[1]))
ev = sorted((e for e in book["customer_events"] if e.get("company_churn_estimate") is not None),
            key=lambda e: e["event_date"])
last_occ = {}
rows = []
for e in ev:
    sp = (e["customer_id"], e["commodity"])
    if e.get("departure_rolled") is False:
        t = "default_after_declined_fix" if last_occ.get(sp) == "declined_fix" else "default"
    else:
        t = "fixed"
    last_occ[sp] = e["departure_occasion"]
    rows.append({"account_id": household_of(e["customer_id"]), "term_start": e["event_date"],
                 "fuel": e["commodity"], "desk_churn_belief": e["company_churn_estimate"],
                 "desk_asked": True, "left": e["event_type"] == "churned", "ending_term_type": t})

def run(b, tag):
    b = dict(b); b["desk_belief_log"] = rows
    out = {"pooled": grade(b)}
    ledger = _ledger(rows)
    states = _states(rows, online_conditioned_beliefs(rows, ledger), b)
    per = {}
    for y in range(2019, 2025):
        sub = [s for s in states if s["year"] == y]
        lv = sum(s["left"] for s in sub)
        r = {"states": len(sub), "leavers": lv, "accounts": len({s["account"] for s in sub}),
             "by_type": {t: [sum(1 for s in sub if s["type"] == t), sum(s["left"] for s in sub if s["type"] == t)]
                         for t in ("fixed", "default", "default_after_declined_fix")},
             "multiplier": {t: ledger.ending_term_multiplier(t, y)[0] for t in ("fixed", "default", "default_after_declined_fix")}}
        if lv and lv < len(sub):
            p = _point(sub)
            r.update({"auc_live": round(p[0], 3), "auc_cond": round(p[1], 3), "paired": round(p[2], 3)})
            (bl, bc, bd), used = _clustered_bounds(sub)
            r.update({"live_95": bl, "cond_95": bc, "paired_95": bd, "draws": used})
        fx = [s for s in sub if s["type"] == "fixed"]
        fl = sum(s["left"] for s in fx)
        if fl and fl < len(fx):
            r["within_fixed_auc_live"] = round(_point(fx)[0], 3)
            r["within_fixed_live_95"] = _clustered_bounds(fx)[0][0]
        r["void"] = lv < MIN_LEAVERS
        per[y] = r
    out["per_year"] = per
    fx = [s for s in states if s["type"] == "fixed" and 2019 <= s["year"] <= 2024]
    out["pooled_within_fixed"] = {"states": len(fx), "leavers": sum(s["left"] for s in fx),
        "auc_live": round(_point(fx)[0], 3), "live_95": _clustered_bounds(fx)[0][0]}
    return out

res = {"primary": run(book, "primary")}
b2 = dict(book)
b2["customer_events"] = list(book["customer_events"]) + [
    {"customer_id": e["customer_id"], "event_type": "churned", "event_date": e["event_date"]}
    for e in book.get("svt_departures") or []]
res["secondary_with_svt_departures"] = run(b2, "secondary")
print(json.dumps(res, indent=1, default=str))
```
