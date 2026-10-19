**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` — director ruling 19 Oct 16:37

# Pre-registration: what 400 founder households cost in memory and time, measured on small books

Filed before any measurement. It answers the condition in
`docs/staging/advisor/DIRECTOR_RULING_FOUNDERS_ARE_400_HOUSEHOLDS_2026-10-19.md`: *"Households, as
long as it doesn't create a memory problem"*.

## 0. What is being counted, and what was found before measuring

`founder_accounts: 400` in `docs/design/FOUNDER_BOOK.yaml` counts **records**, which are supply
points (`_founders_spread_through_the_year` fills `wanted` records a whole home at a time). On
`origin/main` 2fe180d52, seed 20260724, `founder_book()` gives these, read without a run:

| Founder records | Homes | Dual homes | Dual share | Committed cy to 2026-01-01 |
|---|---|---|---|---|
| 171 | 100 | 71 | 0.710 | 1,619.1 |
| 344 | 200 | 144 | 0.720 | 3,256.7 |
| 400 (today) | 233 | 167 | 0.717 | 3,793.5 |
| 697 | 401 | 296 | 0.738 | 6,603.0 |

**The ruling's condition is memory, but memory is not the only thing that binds.**
`SETTLEMENT_CUSTOMER_YEAR_BUDGET` (5,000, `simulation/net_new_acquisition.py`) is charged with the
founders' own committed customer-years (`existing_cy` in `live_population._resolve_campaign`).
400 households commit about 6,603 cy, which is more than the whole budget. **At today's budget, a
400-household book would admit no campaign win at all.** The 9 Oct production shape left about
1,200 cy for growth (4,994 committed against 3,793 for the founders). The budget is a
director-approved curriculum value (9 Oct), so this turn does not move it.

## 1. The measurement (R8: small books, then scale up)

Two founders-only points: `tools/settlement_ceiling_probe` at budget 0, full window. This is the
live path's own compute, in a scratch worktree at `origin/main`, with `founder_accounts` set to 171
(100 homes) and then 344 (200 homes). The points run one after the other, never side by side, so
neither competes with the other for memory or time. One unit runs both through
`background.launch_long_job`, which reserves memory against the one box budget (R7). The reaper
is untouched.

The scale-up, to be applied AFTER the points are read:
`peak(400 homes, budget B) = founder line at 6,603 cy + campaign marginal × max(0, B − 6,603)`.
The founder line is fitted through the two points. The campaign marginal is the 9 Oct
1.134 MB/cy and 2.29 s/cy. The allowance is the probe's own: 0.25 × the guest's total memory,
which is 6,008 MB at 24,032 MB.

## 2. Predictions

- **H1.** Peak RSS is linear in founder committed cy. The 200-home point is 1.5–2.3× the 100-home
  point.
- **H2.** At 100 homes the peak is 1,400–2,600 MB. At 200 homes it is 2,200–3,800 MB.
- **H3.** The founders-only wall clock is 1,500–3,500 s at 100 homes and 2,500–5,500 s at
  200 homes.
- **H4.** Extrapolated to 400 homes at budget 5,000 (founders only, since the budget is
  exhausted), the peak is 4,500–6,500 MB. **I cannot predict which side of 6,008 MB it falls.**
  That is why this is being measured.
- **H5.** With the budget raised to keep the campaign's 9 Oct room of about 1,200 cy (B ≈ 7,800),
  the extrapolated peak exceeds 6,008 MB.

## 3. Branches, decided now

- **Fits** (400 homes at budget 5,000 extrapolates under 6,008 MB, with the line's two points
  inside H1): the memory condition is met. But the switch at budget 5,000 ends campaign growth,
  and the director has not ruled on that. So the switch is still brought to him first: the
  measurement, plus a recommendation on the budget.
- **Does not fit:** do not switch. Report the largest household count that fits, and what would
  close the gap.
- **Either way:** nothing in `FOUNDER_BOOK.yaml` changes until he has seen both constraints
  together.

## 4. Grade

*(To be filled in below this line, beside the predictions. No prediction is edited.)*
