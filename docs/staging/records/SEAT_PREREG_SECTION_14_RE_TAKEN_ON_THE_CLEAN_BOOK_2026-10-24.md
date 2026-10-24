# Pre-registration: section 14 re-taken on the clean book (ending_term against flat, dice seeds 2–5)

**Written 2026-10-24 ~06:10 BST. No arm of this run had started when this was written.** Claim `section-14-is-re-taken-on-the-clean-book`
(Lane 0, seat). The parent record is
`SEAT_PREREG_THE_PER_CUSTOMER_SWITCHES_ON_TOGETHER_AGAINST_FLAT_2026-10-21.md` §14. Its four-seed
grade was landed in `427e5f021`: ending_term − flat had mean net +£1,556 ± £2,104 and `departure`
+£3,618 ± £4,924, an interval of [−£1,306, +£8,542], so the switch stayed off. It is a new file
rather than §18 of the parent because the shared tree's copy of the parent is 153 lines behind
origin.

**Why this run.** `49a577707` called every pound figure on the 2–23 Oct books untrusted until a
clean book existed. `d909b6933` then made one: standard-variable bills above the cap fell from 5,488
of 18,398 to 104 of 24,597 on the fresh run. §14's arms ran at `bc1e6ad78`, which is before
`4bc21e920` (the incoming occupant was priced as non-domestic), `4ef70aba9` (the EPG on the
household bill) and `1e358809b` (a default term is billed at one rate, not a ToU pair). This run
grades the renewal belief conditioned on the term ending (`renewal_belief_by_ending_term`) on that
clean book.

## 0. What runs, and one correction to the item that asked for it

- **Code.** Every arm runs from one locked origin worktree, `/var/tmp/se-s14clean-wt`, detached at
  `ff8437814e`. That commit has `4bc21e920`, `4ef70aba9` and `1e358809b` as ancestors. Arms:
  `tools/per_customer_switch_arms.py {flat,all_on_ending_term} OUT --dice-seed N`, for N = 2, 3, 4
  and 5. These are §14's graded seeds; seed 1 was void there and stays out. Outputs go to
  `/var/tmp/se-s14clean-out/s{N}/{flat,all_on_ending_term}.{json,log,rc}`.
- **Correction: "change one thing only: the bill fixes" cannot be met as written.** Between
  `bc1e6ad78` and `ff8437814e` there are 29 commits under `simulation/`, `company/`, `saas/` or
  `sim/`. Several of them are default-on and change the book in both arms:
  - the annualised advance (`82f4b20bc`);
  - money held toward a bill counted as a part payment (`6b81d3b25`);
  - profile-class settlement for homes without half-hourly settlement (`ed0717246`, `e5d99e249`);
  - EBSS netting (`d8129f3f6`);
  - no gas billed after a dual household leaves on electricity (`2b81e1466`);
  - the collections step after the top rung and the statute-bar write-off (`94b281af7`);
  - the ToU invoice registers (`50001b0b7`);
  - the EPG on a void-stub estimate (`ce35a25e2`).

  The default-off ones (the C30 re-fix and letter, the E6 overlay, the gas floor, the §15 and §16
  guards) are not switched on by either arm. Rolling back only those commits would create a code
  state nobody runs, and the clean book is the book on trunk. So **this run changes the code from
  `bc1e6ad78` to `ff8437814e`. The bill fixes are the reason for the change, but they are not the
  only thing that changed.** A shift against §14 therefore **cannot be attributed to the bill
  fixes.** It is read as "§14 on today's book" and graded on its own four seeds. It is never pooled
  with §14's seeds.
- **The collections tone is identical between the arms, not just inert.** §14 noted that flat and
  the offer arms differed in `tone_mode`, and that the tone reached no payment because
  `world_payment_truth.UNIFIED = True`. The item asked this file to state that the tone is inert
  unless item 1 had landed. It has landed: `94b281af7` ("the flat arm keeps current's tone").
  `FLAT_SUPPLIER_POLICY` now keeps `CURRENT_POLICY.tone_mode`, and `UNIFIED = True` still stands at
  `ff8437814e` (`simulation/world_payment_truth.py:54`). So the arms differ in the retention offer,
  its framing and the ending-term belief, and in no tone.
- **Order and the box.** One arm at a time, eight in all, at about 55 minutes and about 7 GB each
  (§14's seed 5 logs). The driver is `/var/tmp/se-s14clean-out/drive.sh`. First it waits with
  `tools/wait_for.py --pattern` until no process is writing `/var/tmp/c30-seeds-out` (the nine C30
  letter-and-refix seed arms, all queued at writing) or `/var/tmp/crisis-overlay-out` (the E6 crisis
  arm, queued). Then it launches each arm through `background.launch_long_job`, following each to
  its end. When the last arm's `.rc` exists, it runs the grade.
- **The grade is §14's tool, unchanged:** `tools/grade_per_customer_switch_seeds.py`, last changed in
  `94b281af7` (as of `ff8437814e`). It needs three arms, so the ending_term output also fills the
  save_odds slot. This makes **save_odds − ending_term a placebo that must read £0.00 in every
  channel**. save_odds − flat repeats ending_term − flat and is not read. Output:
  `/var/tmp/se-s14clean-out/grade.txt`. Beside it, `over_ceiling.txt` holds
  `tools/grade_svt_invoices_over_ceiling` for every output.

## 1. Setup facts, already read (not predictions)

§14's outputs were graded for over-cap SVT invoices at `bc1e6ad78`:

| output | graded | above ceiling | share | households |
|---|---|---|---|---|
| s2 flat | 24,382 | 6,827 | 28.0% | 308 |
| s2 ending_term | 24,494 | 6,862 | 28.0% | 310 |
| s3 flat | 25,096 | 6,994 | 27.9% | 319 |
| s3 ending_term | 25,083 | 7,015 | 28.0% | 318 |

So the defect sat on both arms almost equally: 20 to 35 invoices apart out of about 7,000. The arm
difference was formed by subtracting two equally overcharged books. I expect the fix to move the
difference much less than it moves either book. That expectation is R5, below.

## 2. Predictions (no output of this run read)

- **R0, the placebo.** save_odds − ending_term reads £0.00 net and 0 households in every channel on
  every seed: 99%. If it fails, the grade is void and the grader is read before anything else.
- **R1, the fixes reached every arm.** Every one of the eight outputs has `above_household_ceiling`
  ≤ 300, against about 6,800–7,000 at `bc1e6ad78`: 85%. A seed above 1,000 means the arm did not
  run the clean code. That seed is void and its worktree HEAD is checked.
- **R2, the dice reach the world.** For every pair of seeds, the flat arms' `churned` (account,
  `event_date[:10]`) sets have a symmetric difference ≥ 20: 90%. A pair below 20 voids the later
  seed of the pair. This replaces P14a′'s comparison with seed 1, which ran on another book.
- **R3, departure (gross, §14's rule).** ending_term − flat `departure` gross is positive on at least
  3 of 4 seeds: 70%. Mean in [£0, +£6,000], point +£2,500. That is below §14's +£3,618, because a
  household saved in the offer arm no longer pays an overcharged default bill afterwards. The
  4-seed 95% interval contains zero: 70%.
- **R3n, departure by household net** (the §14 addendum's column). Positive on at least 3 of 4
  seeds: 70%. Mean point +£1,200. The interval contains zero: 75%.
- **R4, money.** ending_term − flat mean net has a 4-seed interval containing zero: 70%. Point
  +£1,000.
- **R5, the size of the shift.** |mean net here − £1,556| < £2,104 (§14's half-width): 75%. This
  says only that the two four-seed means are within noise of each other. It is not attributed to
  the bill fixes (§0).

## 3. Decision rule, fixed now

This is §14's rule, kept as the primary rule: `renewal_belief_by_ending_term` is proposed for
CURRENT_POLICY only if its `departure` gross against flat has a 4-seed 95% interval above zero AND
its mean net against flat is ≥ 0. Because §14's addendum showed a departure is worth about half its
gross, **the same must also hold for `departure` by household net**. Both legs are required. If
they disagree, the switch is not proposed, and the disagreement is reported (F11: err against the
thesis). A positive net carried only by `parity` or `same_choice` is a transfer (M2) and is not
proposed. Under the director's 23 Oct ruling (point 2), a grade that meets this rule is the
machine's switch-on. One that does not stays off on this record with its reason (point 3).
**Predicted: not proposed, 75%.**

**What this run cannot answer.** The household side of the per-customer offers (F5 of the parent
record) is still a GAP. These are four dice seeds on one book, not EP17's blind grade. The renewal
churn belief's ranking of leavers (`churn_model_performance` in the flat outputs) is reported
beside the grade. It is **not** predicted here, so it is not a test.

## 4. Launch

Launched with `python3 -m background.launch_long_job --detach --job s14clean-driver`. No arm starts unless this file is on `origin/main`; the driver checks that and refuses otherwise. The unit log
is `/var/tmp/se-s14clean-out/drive.log`. A seat continuation, `grade-section-14-on-the-clean-book`,
is handed off to write the grade into this file once `grade.rc` exists.
