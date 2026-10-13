**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**What:** DD4b re-sited from the renewal to the supplier's annual DD review, told in the loop; its world predictions at the toggles' low and high ends · claim `dd4b-answers-the-told-amount-at-the-in-loop-review-then-freeze-at-the-range-ends`
**Status:** GRADED 2026-10-13 01:05. 11 of 13 hold; P11's bad-debt leg and P13 are wrong. Neither refutation clause fires as registered (P4 = 0, 2022 answered 34). But P4's gloss, "the in-loop chain is the post-loop chain", is only true on KEYS: 365 of the 847 matched reviews carry a different current DD. See "The grade" below

# DD4b at the review the household meets: predictions at its range ends

## What changed (the build this grades)

`WORLD_FREEZE_DD_SHOCK_SAVE_AND_MOVER_AT_THEIR_RANGE_ENDS_2026-10-12.md` s1: DD4b answered a rise only at
a renewal, 10 of the world's 299 material rises on 200 founders and none of the 122 in 2022-23. Now
`simulation/dd_review_in_loop.py` asks the company's review door (`annual_dd_review_view`, the one the
post-loop review uses) over each leg's bills as they post. A DD household told a rise over 15% answers
it through `respond_to_told_amount` before that month's collection. The renewal-site call is retired, so
one rise is answered once.

**This is not the prerequisite item's move.** `four-principles-the-dd-review-and-dunning-move-to-the-supplier`
(landing as `9f5ea4e5e` at the time of writing) moves the review's RULE into `company/` with identical
output. It does not move WHEN the review is asked: the post-loop call in `run_phase4c_on_phase2b.py`
stays. This item asks the same door in the loop instead. It needed only the door, which already existed.

**Already measured (not predictions), 40 founders, budget 0, probe setting:** 34 shocked reviews answered
across 16 households (was 2), 16 of them in 2022-23 (was 0). By year: 2017 2, 2018 9, 2019 3, 2020 1,
2021 2, 2022 8, 2023 8, 2025 1. The post-loop review on the same run has 52 leg-level rises over 15%.
That count includes non-DD legs, and a dual-fuel household counts twice.

## Predictions, 200 founders, budget 0, base seed

Runs: `/var/tmp/dd4b_runs/il/il_run.py {default,low,high} 200 0`, from this claim's worktree. Only DD4b's
three strengths differ between them. Low = (cancel 0.01, uplift 0.25, complaint 0.02). High = (0.10, 3.0,
0.24). Earlier baseline at the renewal trigger: total net 146,396.48 and bad debt 3,070.03 (`f200-probe`),
on an older origin, so it is not this run's control. The control is `default` on the same code.

| # | Quantity | Prediction | Why |
|---|---|---|---|
| P1 | shocked reviews answered (low run's book) | 150 to 260 | about 0.65 of the 299 leg-level rises, the 40-founder ratio (34 / 52) |
| P2 | ...in 2022-23 | 60 to 110, and at least a third of P1 | 122 of the 299 rises fall then; 16 of 34 at 40 founders |
| P3 | share of answered reviews at LOW stress | 0.5 to 0.9 | was 10 of 10 at the renewal; the review reaches the default-tariff households a renewal never met |
| P4 | in-loop vs post-loop, same run: reviews told in the loop that the post-loop review lacks | 0 | causal by construction; any mismatch is the bill basis (loop revenue grossed up at VAT, against the billed estimate) |
| P5 | material-rise agreement on matched reviews | at least 90% | the same basis question |
| P6 | low: mandates cancelled | 0 to 10 | 0.01 x relativity (1 / 4 / 11.7) over about 200 |
| P7 | low: complaints | 1 to 9 | 0.02 x about 200 |
| P8 | high: mandates cancelled | 15 to 70 | 0.10 x relativity, capped at 1 |
| P9 | high: complaints | 30 to 65 | 0.24 x about 200 |
| P10 | high: DD failed collections over default | +60 to +300 | 4x a 1.7% base (144 / 8,687 in `f200-probe`) over about 200 household-years, more where stretched |
| P11 | low: total net and bad debt against default | within 0.3% and within 5% | small responses on a small share |
| P12 | high: total net against default | lower, by under 2% | failures are mostly collected late, not lost |
| P13 | high: bad debt against default | higher, by 0 to 30% | the stretched households carry the uplift |

**What would refute the build rather than the numbers:** P4 above 0, which would mean the in-loop chain
is not the post-loop chain; or no answered review in 2022 (P2 at 0).

## Run state, 2026-10-12 19:2x

- `default`: finished 18:26, 36 min, 3.1 GB peak. Total net 148,258.89, bad debt 1,243.83. `told.json`
  is empty because every strength is 0 and the in-loop review is behind `not off`, so P4/P5 can only be
  graded on `low` and `high`. The post-loop review on this run has 847 reviews, 299 of them material,
  which matches the WORLD_FREEZE note's 299.
- `low`, `high`: relaunched as `longjob-dd4b-il200-{low,high}` from the locked worktree
  `/var/tmp/se-dd4b-il200`, the one `default` ran from. Its `dd_review_in_loop.py`, `run_phase2b.py` and
  `dd_shock_response.py` are byte-identical to `71c324b6d`, so the control and both arms run the same code.
  Outputs go to `/var/tmp/dd4b_runs/il/f200-{low,high}/`. Grade with `python3 /var/tmp/dd4b_runs/il/grade200.py`.

## The grade, 2026-10-13

`low` and `high` were relaunched at 23:46 because the 19:2x launchers had died queued, with no unit
ever created. They were held behind another lane's commit gate until 00:15 and finished at 01:05, from
the same locked worktree. `dd_review_in_loop.py`, `run_phase2b.py` and `dd_shock_response.py` there are
byte-identical to `71c324b6d`. Output is from `python3 /var/tmp/dd4b_runs/il/grade200.py`.

| # | Prediction | Result | Grade |
|---|---|---|---|
| P1 | 150 to 260 answered | 208 (111 households) | holds |
| P2 | 60 to 110 in 2022-23, at least a third of P1 | 81 (2022: 34, 2023: 47), 39% | holds |
| P3 | LOW share 0.5 to 0.9 | 0.885 (184 LOW, 16 MODERATE, 8 HIGH) | holds, at the top |
| P4 | told in the loop and missing from the post-loop review = 0 | 0, and 0 the other way; 847 / 847 matched | holds as registered (see below) |
| P5 | material-rise agreement on matched reviews of at least 90% | 771 / 847 = 91.0% | holds, narrowly |
| P6 | low: 0 to 10 cancelled | 5 | holds |
| P7 | low: 1 to 9 complaints | 4 | holds |
| P8 | high: 15 to 70 cancelled | 33 | holds |
| P9 | high: 30 to 65 complaints | 38 | holds |
| P10 | high: +60 to +300 DD failures over default | +74 (149 to 223; cancelled_other 26 to 67) | holds, at the low end |
| P11 | low: net within 0.3%, bad debt within 5% | net -0.145%; **bad debt +17.3%** (1,243.83 to 1,458.72) | **net holds, bad debt WRONG** |
| P12 | high: net lower by under 2% | -0.254% (148,258.89 to 147,882.25) | holds |
| P13 | high: bad debt higher by 0 to 30% | **+37.2%** (to 1,707.02) | **WRONG** |

**The build is not refuted.** No review is told in the loop that the post-loop review lacks. Rises are
answered in 2022, 34 of them.

**What the two wrong predictions say.** Bad debt moves about four times further than "small responses
on a small share" allowed. In low, 14 extra failures came with +£215 of bad debt. The base is only
£1,244, so a few stretched households carry the whole percentage. I cannot yet say how much of the
move is the response and how much is path divergence. Any change in a household's payment path can
move the draws downstream, and there is no placebo arm on this code: `f200-probe` ran on an older
origin. The one-variable control is a `probe` arm (it records every shock and changes nothing) from
the same worktree. If bad debt moves by more than about 5% there, the bad-debt legs of P11 and P13
measure noise, not DD4b.

**FINDING (severity LATENT): P4 is graded on keys, and the content diverges.** The registered gloss
was "the in-loop chain is the post-loop chain". On keys it is: the same 847 (customer, month)
reviews. On content it is not:

- the current DD is the same in 482 of 847 matched reviews, and in all 217 of window 0's;
- annual spend, in-loop over post-loop: total +1.6%, median 1.000, p10 0.934, p90 1.047, and
  668 / 847 within 5%. The tail reaches 3.8 times (£1,710 against £451), far beyond the VAT
  gross-up the pre-registration expected;
- the material count ties at 299 and 299 only because 38 reviews flip each way;
- `reconcile` is identical in `low` and `high`, so the response strengths do not cause this.

Window 0 agrees exactly, so the opening door is shared. The split comes from the bill basis: the
loop's settled revenue grossed up at VAT, against `build_monthly_bills`' estimated-then-trued-up
totals. Once one window's recommendation differs, every later window's current DD differs too. The
households are told the in-loop figures. The post-loop review publishes the other set (the WORLD_FREEZE
note's 299). Until the tail is explained, those are two descriptions of different reviews. This
does not block freezing DD4b's strengths at the range ends: P6-P10 hold and are counted on the in-loop
reviews the household actually met. It does block quoting the post-loop census as "what the household
was told".
