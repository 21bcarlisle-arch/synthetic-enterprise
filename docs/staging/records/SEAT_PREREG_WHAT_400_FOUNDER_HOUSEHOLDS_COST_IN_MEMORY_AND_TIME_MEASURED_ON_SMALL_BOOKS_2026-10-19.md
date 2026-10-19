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

### Measured (longjob-founder-households-memory-probe, 15:54–17:28Z, scratch worktree at 2fe180d52, seed 20260724)

Founders-only, budget 0, full window, the live path's compute. Both points are clean: exit 0, ten
years reported, no producer in flight at start or end, and the campaign record agrees.

| Point | Committed cy | Peak RSS | Peak anon | Wall | Accounts after 2025 |
|---|---|---|---|---|---|
| 100 homes (171 records) | 1,630.2 | **1,905.6 MB** | 1,808.1 MB | **1,240.9 s** | 777 |
| 200 homes (344 records) | 3,267.8 | **2,656.2 MB** | 2,521.3 MB | **2,682.4 s** | 967 |

**Cross-check against the box.** A 2-second sampler on the unit's cgroup `memory.stat` read an
anon peak of 2,530 MB during the 200-home point, which matches the child's own 2,521 MB. No
process outside the probe's view holds memory. The unit's `memory.peak` of 5.27 GB, read during
the 100-home point, includes page cache, so it is not the figure R7 budgets.

**A third point, on current code, from production.** Today's `ad8afadc5` run used 400 records and
the campaign at a budget of 5,000. It peaked at 4,065.4 MB in 5,743 s (`sim-runner-log.md`). The
founder line puts its 3,793.5 founder cy at 2,897 MB. That leaves about 1,170 MB for the
campaign's roughly 1,200 cy, about 0.97 MB per campaign cy. The 9 Oct marginal was 1.13. **A
campaign customer-year costs about twice a founder customer-year.**

### Scale-up (R8)

The founder line through the two points is **peak ≈ 1,160 MB + 0.458 MB/cy**. Wall time grows
slightly faster than linear (×2.16 for ×2.00 cy), so time is scaled as a power of committed cy,
with exponent 1.11.

| Shape, 400 homes (697 records, 6,603 founder cy) | Peak RSS | Wall | Campaign wins |
|---|---|---|---|
| **A.** Budget held at 5,000 (founders exceed it, so no win is admitted) | **≈ 4,180 MB** | ≈ 5,850 s | **0 in every year** |
| **B.** Budget raised to ≈ 7,800 (the campaign keeps today's ~1,200 cy) | **≈ 5,350–5,540 MB** | ≈ 8,600 s | about today's (221 of 613 funnel wins on 9 Oct) |
| Allowance: 0.25 × guest 24,032 MB | **6,008 MB** | weekly publish, so time does not bind | |

### Grade

- **H1 refuted, low.** The 200-home peak is 1.39× the 100-home peak, not 1.5–2.3×. A fixed base of
  about 1,160 MB was larger than I allowed for. Wall time is 2.16×.
- **H2 holds.** 1,906 MB is inside 1,400–2,600, and 2,656 MB is inside 2,200–3,800.
- **H3 half refuted.** 1,241 s is below 1,500–3,500 (faster). 2,682 s is inside 2,500–5,500.
- **H4 refuted, low.** About 4,180 MB, below the 4,500–6,500 band. It sits about 1,830 MB under
  the allowance.
- **H5 refuted.** With the campaign's room kept, the peak is about 5,350–5,540 MB, which is
  *inside* 6,008 MB by 470–660 MB (8–11%). I predicted it would exceed. The two-to-one cost of
  campaign customer-years against founder ones is what I did not know.

**Branch taken: it fits.** As decided in §3 before measuring, nothing in `FOUNDER_BOOK.yaml`
moves yet. At today's budget, 400 households admit no campaign win in any year. That is a second
consequence of the ruling, beyond the memory condition. It goes to him as a `for_the_director`
row with a recommendation. **I recommend B:** households, with the budget raised alongside to
about 7,800. This is the same move as his 9 Oct approval, which raised the budget "alongside
because the founders' own committed years count against it". The first production run on B is
the confirming measurement, and the reaper stays as the safety net.

**Not measured, and said so.** The scale-up extrapolates the founder line twofold past its upper
point. A power-law fit (exponent 0.48) would put A at about 3,720 MB, so the linear figure is the
conservative one. B's campaign term borrows the per-cy cost of campaign customer-years from
`ad8afadc5` and 9 Oct, not from a run at 400 homes.
