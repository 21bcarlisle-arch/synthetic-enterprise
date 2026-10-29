**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Prediction: the desk cures no journey on the due date of a bill it still holds (filed 2026-10-29, before the next fresh run)

**The change.** `company/billing/collections_journey._owes_a_bill_due_by`. A journey cures only
when no bill due on or before that day is still owed oldest-first. Reasoning and sources:
`docs/market_research/debt_and_collections.md` §7.6.

**The case.** SYN-2016-550 on 209c3350ab. Its journey "cured" on 15 Dec 2024 while £258.83 was
owed. Then it reopened the next day, the same pattern as every month of 2024.

**Baseline: the 209c3350ab book's journey record** (`p2b__collections_journeys.pkl.gz`, measured
before the fix).

| Count | 209c3350ab |
|---|---|
| journeys | 3,563 |
| exit cured / write_off / open | 3,413 / 103 / 47 |
| cured with `days_overdue == 0` (the defect's signature: a positive balance whose oldest FIFO-unpaid bill is due that day) | **2,510** (239 of 394 accounts with a journey) |
| of those, a new journey opened the next day | 2,295 |
| journeys reaching final_notice / prepayment_offered | 287 / 158 |
| debt stories the Explore slot's fourth check refuses (209c pages built at 8c55d9b6cb) | 94 of 402 |

**Predictions for the next fresh run on a commit carrying this fix.** Other changes land between
runs, so only P1 is attributable to this change alone. P2 to P4 give a direction and a range, and
if they move I cannot yet attribute the movement.

- **P1 (exact).** Zero journeys end `cured` with `days_overdue == 0`. Any non-zero count refutes the
  fix.
- **P2.** There are fewer journeys, because the rolling-arrears accounts merge into one long
  journey each. The prediction is 1,000–1,700 against 3,563. Below 1,000 would mean something else
  also moved.
- **P3.** More journeys climb the ladder, because they stop resetting every month. final_notice
  rises above 287 and prepayment_offered above 158. More journeys stay open at the run's end:
  above 47.
- **P4.** The fourth check refuses at most 10 of the next book's debt stories, against 94. The
  residue is where the page's per-invoice allocation and the desk's FIFO disagree on which bills
  are still owed.

**How to grade.** Over the new run's `p2b__collections_journeys.pkl.gz` (a list of
`{account_id, stages, exit}`), count the journeys with `exit == "cured"` whose last stage has
`days_overdue == 0`, the exits, and the journeys holding each stage. For P4, run
`tools.generate_explore_cast._debt_page_failures` over the rebuilt pages. Write the result beside each prediction here, including the
predictions it refutes.
