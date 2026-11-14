**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` · **Claim:** `the-first-baseline-comparison-is-pre-registered-before-a-book-passes` (Lane 0 delivery)

# Pre-registration: the corrected renewal belief against the flat supplier, on the first book the gate passes (2026-11-11)

Written 2026-11-11 at origin `1b69ca1270`. **Nothing has run.** No arm below has been launched on
any book carrying the close-refund fix, and no book has yet passed the publisher's gate. This record
changes no code, no policy default and no book. It exists so that the thesis comparison is
designed before its answer is known, and so it can start the day a book passes.

## How the 26 Oct ruling is kept

The ruling (`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`)
says "Correctness comes first. No new feature work is drawn until the steps below are done." Its exit
test is a fresh book with zero unexplained breaches, eight Explore slots that are valid or honestly
empty, and one cold read that finds no new class of error, "Report this in a reading, and only then
resume the ruled order."

- **This record is a design, not a lever.** It flips no switch. `CURRENT_POLICY.renewal_belief_by_ending_term`
  stays `False`. It adds no code, and no run is launched or armed by it.
- **Launch condition, both legs required.** (1) `background.process_run_complete._domain_invariant_gate_permits_publish(<sha>)`
  returns True on pages the publisher itself built, not through the scratch `grade.py` chain, which
  read a blind row as a pass on 068b5e3cc8 (`SEAT_FINDING_THE_068B5E3CC8_BOOK_DOES_NOT_PASS_..._2026-11-11.md`).
  (2) The ruling's exit-test reading is on origin. Until both hold, no arm here touches a book.
- **The arms never reach the published book.** Each arm runs in its own worktree through
  `tools/per_customer_switch_arms.py` and `policy_scope`. The publisher keeps serving `CURRENT_POLICY`'s
  book. A switch-on comes only from the decision rule in §6, after the grade, under the 23 Oct ruling.

## 1. The book

**The first book the gate passes.** When this was written, the candidate was `longjob-book-crfix-<sha>`, armed by
`SEAT_PREREGISTRATION_THE_FIRST_BOOK_CARRYING_THE_CLOSE_REFUND_FIX_2026-11-11.md`. If that book is refused, the
candidate is the next book the gate passes. The book's sha and its gate verdict line are written into §8 at launch,
before any arm output exists. All arms on all seeds run from **one** worktree at exactly that sha. A member whose
stamp disagrees is refused, not pooled.

The shape is the production shape at that sha: 400 founders, the default population seed and the full 2016–2025
window. It is **not** EP17's varied-population grade. Population seeds 61113–61118 are still unlisted in
`book_seed_authorisation`, so this design needs none of them. It varies only the dice (§3). A population-varied
grade stays EP17's, and nothing here may be quoted as that grade.

## 2. The arms, and the one variable

| arm | policy | what it is for |
|---|---|---|
| **P** `all_on_ending_term` | `CURRENT_POLICY` + the three per-customer switches + `renewal_belief_by_ending_term` (the §12 prior form) | the per-customer supplier with the **corrected** renewal belief deciding who gets a retention offer at the roll |
| **F** `flat` | `FLAT_SUPPLIER_POLICY`: no targeted retention for anyone and one framing, with current's tone (`94b281af7e`) | the flat-rule baseline, with no per-customer view |
| **A** `all_on` | P without `renewal_belief_by_ending_term` | the attribution arm: the per-customer supplier with the **live** belief |

**Stated plainly: P − F is not one variable.** It is the per-customer view as a whole: the retention gate, offer
framing, the save decided per household, and the belief. The thesis asks that question, so it is the primary
contrast. **The one variable is P − A, and only `renewal_belief_by_ending_term` differs there**
(`tools/per_customer_switch_arms.ENDING_TERM_FIELDS`). A P − F lead that A − F already carries is the per-customer
machinery, not the corrected belief, and it is reported that way.

Both of these are the same in every arm: hedging, `renewal_margin_arm="flat_rules"`, the save on a loss notice
(`price_match`), every regulatory duty, the world and D1's treasury feedback.

**What the belief can and cannot move.** `next_best_action_decides_at_renewal` still records only (`decision_policy.py:316`):
nothing is sent and the world is unmoved. So the belief reaches the world only through **who gets a retention offer,
and how deep the offer is**. It does not reach the renewal price itself. "Per-customer renewal decisions" in this
record means exactly that and nothing wider.

## 3. Seeds

The book is held. The dice are re-drawn with `--dice-seed N`, which covers every renewal roll and every payment draw
(§14 of `SEAT_PREREG_THE_PER_CUSTOMER_SWITCHES_ON_TOGETHER_AGAINST_FLAT_2026-10-21.md`). Seeds 1–5 were read on an
earlier book, so they are not reused. **The seeds are 6 to 13: eight seeds, all three arms each, 24 members.**

**Why eight, not four.** On seeds 2–5, P − F `departure` by net was +£1,696 ± £2,336. The half-width was 1.4× the
mean, so the interval held zero. With the same spread, the half-width scales by (t₇/√8)/(t₃/√4) = 0.836/1.591 =
0.53. That gives about 0.74× the same mean, which clears zero if the mean holds. Six seeds gives 0.66, about 0.92×,
which is too close to the line to answer the question. Eight is the smallest count that can.

**Held, and therefore not bounded by these seeds:** the elasticities, the SVT-inertia roll (who leaves the default
tariff) and the population.

## 4. Held-back years (B11)

`forward_clv.DEFAULT_CUT_YEAR = 2020`. The years are **fit 2016–2020 and held back 2021–2025**. Every per-customer
CLV figure below is the realised value in the held-back years of households already supplied at the cut, read
beside the B11 forecast made from the fit years only (`forward_clv.run_backtest`, cut 2020). The arm comparison is
graded on the whole window and again on the held-back years alone. The held-back reading is the thesis reading:
a belief that only pays inside the years it was fitted on has not been shown to know anything.

## 5. Outcomes and predictions

Each outcome is in its own unit and never converted to pounds. Each is paired by seed, as mean ± 95% half-width
(t, 7 df). An interval that holds zero reads **cannot tell**, and F11 applies: **a tie counts against the thesis.**
Each line is graded held, refuted or cannot tell. A refuted line is kept beside its prediction.

### O0. Validity (graded first; a failure voids the seed pair)

| # | prediction | confidence |
|---|---|---|
| O0a | F makes 0 retention offers on every seed. Any offer means F is not flat, and that seed is void. | 0.97 |
| O0b | Every member's book passes `_domain_invariant_gate_permits_publish` on publisher-built pages. If a member does not, it is graded apart, never excepted to fit. 24 of 24 pass. | 0.70 |
| O0c | **The belief's aim (the reason the switch exists).** On the book's 2019+ default-term desk states, the corrected belief's in-run AUC is 0.80 (range 0.74–0.86) and its clustered lower bound is above 0.5. The live belief reads below 0.5 (point 0.35, range 0.25–0.45). If the corrected AUC is under 0.70, the switch is not the switch that was measured, and the grade stops at O0. | 0.80 / 0.75 |

### O1. CLV per customer: realised net per home, £, by `per_cid_pnl[...]["net"]`

| # | measure | predicted P − F | predicted P − A | confidence |
|---|---|---|---|---|
| O1a | whole-window net per home, summed over the book's homes | +£1,500 per book, range −£500 to +£4,000; interval **holds zero** | +£1,200 per book, range −£800 to +£3,500; interval holds zero | 0.60 |
| O1b | the `departure` channel by net (`tools/grade_per_customer_switch_seeds.py`) | **mean > 0 and interval floor > 0** (+£1,700, half-width ≤ £1,500) | mean > 0; interval holds zero | 0.55 / 0.60 |
| O1c | held-back years (2021–25) share of O1b's P − F | **≤ 50%**, because the switching collapse after 2021 leaves fewer departures to prevent (B11 slices 6–7: held-back switch rate 0.35× fit) | — | 0.60 |
| O1d | B11 forecast rank on held-back years (forecast vs realised net per home, cut 2020), per arm | the arms differ by < 0.03 AUC. The forecast is made before the arms diverge most, so the arm moves the outcome, not the forecaster's skill | — | 0.70 |

The book-level provision line is printed beside the channels and never allocated to a household (§14's
household-net reading).

### O2. Churn: departures, in households

| # | measure | prediction | confidence |
|---|---|---|---|
| O2a | departures, P − F per seed | between −6 and +3 on every seed; mean −1.5; interval **holds zero**. The money moves through *which* households leave, not how many | 0.65 |
| O2b | switches and moves counted apart | **cannot be split.** The world's home moves are off (`forward_clv.LIMITATION_NO_MOVE_REGISTER`), so every departure is all-cause. Reported as that limitation, never as a figure | 0.95 |
| O2c | retention offers per seed (P / A) | P 110–135, A 105–125, F 0 | 0.70 |

### O3. Money, the household side, in £, never netted against O1

| # | measure | prediction | confidence |
|---|---|---|---|
| O3a | retention discount paid to households (sum `retention_cost_gbp`), P | £2,600–£3,500 per seed. This is a **transfer** (M2), and it is reported as transfer | 0.70 |
| O3b | "household paid us" per home-year supplied | reported per arm, **never differenced as household value**. A leaver under F stops appearing in `bills`, and what it pays its next supplier is not in the run (§4 F5 of the 21 Oct record). The household side of retention is a GAP on this design | 0.95 |
| O3c | **cost vs cash flow** (M3): the share of stayer home-months on a fixed term, P − F | +1 to +6 points. The `parity` channel moves stayers onto fixes. Certainty is graded by this share. Cash flow (instalment size and timing) has no per-arm instrument and is reported as None with that reason | 0.55 |

### O4. Time, in household minutes

**None, `LIMITATION_NO_MINUTES_INSTRUMENT`.** C31 is a GAP: it is published as perception plus a phone queue,
not as minutes per activity (`knowledge_map.md` row C31). Effort events are reported as counts per home: retention
letters, save contacts and switches. P − F letters equal O2c's offer count (F sends none), at 0.95. No minutes figure
is printed.

### O5. Carbon, kg CO2e

Settled kWh per home × the DESNZ factor per fuel. **|P − F| is under 0.5% of F, and the interval holds zero (0.75).**
Retention changes who is supplied, not how they heat. A fall that comes with a higher unit rate is classified as
rationing, not saving (CO1; `test_carbon_not_a_target`).

### O6. The floor

Comfort and health are a floor, not a currency (M3). The floor is graded by O0b and is not traded against O1–O5.
A per-arm breach the other arm does not carry is a finding against that arm, whatever its money.

## 6. Decision rule, fixed now

**The switch `renewal_belief_by_ending_term` is turned on in `CURRENT_POLICY` only if all four of these hold:**

1. O0 passes on at least 7 of 8 seeds.
2. The P − F `departure` channel **by net** has an 8-seed 95% interval above zero.
3. The P − F whole-window mean net is ≥ 0.
4. The P − A `departure` mean by net is > 0. The corrected belief must add to the per-customer machinery, not ride
   on it.

If all four hold, the switch-on is the machine's under the 23 Oct ruling, point 2. It goes on one record with this
grade and a control that reds if the default reverts. If any fails, the switch stays off, with the failing leg named
(point 3). **This rule may not be rewritten once any arm is read.** More seeds would be a new pre-registration.

Even if the rule is met, the result is reported as "the retention desk's aim creates margin that the company can
detect". It is **not** reported as "the per-customer view creates household value". O3b is a GAP, O4 is None and
O3a is a transfer. The household half of M2 is not answered by this run. That is stated beside the result, not in a
footnote.

## 7. Known confounds both arms share

- **D1's treasury feedback** moves renewal rates in every arm (`1b69ca1270`). It is the same in each arm and is not
  an arm effect.
- **The 2021–23 arrears step-up** lands in winter pounds. O1 is also reported with 2022-10 to 2023-06 excluded. A
  P − F that exists only inside that window is the world's shape.
- **The tone.** F keeps current's tone since `94b281af7e`, so tone is not a variable here.
- **Acquisition is not an arm.** The "finding" half of the mission (M4) is not tested here.

## 8. Launch addendum (written at launch, before any output; empty now)

- Book sha / gate verdict line: —
- Exit-test reading on origin: —
- Worktree, commit, units: —

## Reverse

Delete this file. Nothing outside `docs/staging/records/` is touched.

---

## Amendment, 2026-11-13: checked against this week's fixes, before any arm is read

Read at origin `363aebbd95`. **Still nothing has run.** No arm has been launched or read, so §6 may still be
amended (it says "once any arm is read"). This amendment keeps every line above unchanged. It adds the
following. Written by the delivery seat under claim
`the-baseline-comparison-pre-registration-is-checked-against-this-weeks-fixes`.

### A1. The runner: no change

`tools/per_customer_switch_arms.py` has not changed since `94b281af7e` (24 Oct). `git diff 1b69ca1270 origin/main`
is empty for it, and also for `tools/grade_per_customer_switch_seeds.py`, `company/policy/`,
`simulation/run_phase2b.py`, `simulation/customer_events.py` (the renewal roll) and
`tools/grade_world_debt_against_ofgem.py` (the payment dice). `arm_policy` still builds P (`all_on_ending_term`),
A (`all_on`) and F (`flat`) from `ENDING_TERM_FIELDS` / `ALL_ON_FIELDS` / `FLAT_SUPPLIER_POLICY`. `run_arm` calls
`simulation.run_phase4c_on_phase2b.main(policy=...)` at the worktree's own sha. So **every world and page fix
below reaches every arm with no flag and no runner change, provided the arms run at the book's sha** (§1's one
worktree). The 16 Nov book, built from origin after these commits, descends from all of them. The arms therefore
run through this runner on a sha that book descends from.

### A2. Commits since `1b69ca1270` on a path the arms, the book or the decision rule read

| commit | path read | what reads it | effect on this record |
|---|---|---|---|
| `cab13bbd18` close-refund fix (s.8.8c/d) | `simulation/arrears_engine.py`, run wiring | every arm, the book | §1's `crfix` book was refused (068b5e3cc8 finding). See A3 |
| `ccdfb652d7`, `9392920e60`, `1c66aceab6` | `simulation/arrears_engine.py` | every arm, the book | close/cure walk. Level shift, shared by every arm (A5) |
| `bd58577a2c` | `simulation/world_payment_truth.py` | every arm | as above |
| **`3af02a2dd1` N29 set-off** | `simulation/arrears_engine.py`, `credit_refund_events.py`, `run_phase4c_on_phase2b.py`, `company/billing/credit_refund.py`, seam | every arm (`main` re-walks with `set_offs=`), the book | O1 levels (A5). Its ceiling falls on the fresh book: **O0b** (A4) |
| **`e4d06e2a10`** | `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml` | the gate (launch leg 1, O0b) | `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` excepted at `max_breached: 1` (A4) |
| **`37d9342869` final-bill net** | `background/live_payment_triad.py` (imported by `run_phase2b`) | every arm | leaver cash: 195 legs, £4,715.67 on 6fe7827ab2 (A5) |
| **`40a48b5d84` publisher supersede** | `background/process_run_complete.py` | launch leg 1 | `_domain_invariant_gate_permits_publish` is **unchanged**. Only the landing of a regenerated publish changed. The leg's meaning stands, and a passing book can now actually publish |
| `7d43952ff7` | `company/compliance/domain_invariants.py` | the gate, O0b | N28 narrated sentences are now derived from bills. Fewer false breaches. Shared |
| `0849f1427e`, `940b6e2423` | carbon page, grid-mix history | not O5 | O5 is settled kWh × the DESNZ factor per fuel. Neither is read |
| `e5e0cdcae7` | `simulation/premise_population.py` | — | comment only. "No world behaviour changed" |
| `6e994b119f`, `038bdef0ea`, `3a26ca9fa9`, `cbd8ace4ff` | archive, docstring, publisher inputs | — | no arm, book or rule effect |

**Item 1's refund clock** (`refund-clock-issued-final-bill`, and the old-credit-netted-at-close half): **not on
origin** at `363aebbd95`. No commit since `e4d06e2a10` touches `simulation/arrears_engine.py` or
`simulation/credit_refund_events.py`. If it lands before the book, A4's reasoning applies to it too: its own
finding predicts reg 6D request days move and breaches appear.

### A3. §1, the book: amended

The candidate is now **the 16 Nov 04:00 book** (DIRECTION: "one book carrying N29, the s.9 fixes, the final-bill net
and the refund clock"), not `longjob-book-crfix-<sha>`. The added launch requirement: the book's `producing_commit`
**descends from `3af02a2dd1` and `37d9342869`**, and from the refund-clock commit if one has landed. A book that
does not is not this test's book. The rest of §1 stands: one worktree at exactly the book's sha, and a stamp that
disagrees is refused.

### A4. O0b, and how it meets §6 leg 1: amended prediction, and one reading fixed now

The gate's exception ceilings were set by name on **one** draw of the dice. `max_breached` counts breaches, and the
`scope` text names households. The arms re-draw every payment and renewal roll, so a different household can fall
into the same traced class:

- `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` is at ceiling 1 (SYN-2016-139, refund clock). A seed that puts two
  households into the old-credit-netted-at-close class refuses.
- `INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT` is at 60 now. Its `retired_by` lowers it to the fresh
  book's count (29 ± 3 predicted, `SEAT_PREREG_THE_16_NOV_BOOK_ON_THE_N29_ROWS_2026-11-12.md`). With the ceiling
  at the book's own count, about half of the re-drawn members would sit above it on dice alone.

**Amended O0b: 24 of 24 pass, confidence 0.70 → 0.30.** The 0.70 line is kept above as the original.

**Fixed now, before any arm is read:** an O0b failure **is** an O0 failure. It voids that seed's triple under §6
leg 1. The other reading (excepting a closing-refund overshoot because it "is the world's, not the arm's") is the
except-to-fit that O0b forbids. The F11 direction also says to take the stricter reading. So:

- **New prediction (0.55):** if §6 fails, it fails at leg 1. It fails through the two closing-refund rows, not
  through an arm-specific breach.
- **If leg 1 fails only through rows whose every breach is a closing household's refund or set-off**, the result
  is reported as **"cannot tell: the world's account close is not yet sound enough to grade this comparison"**.
  It is not a refutation of the belief, and the switch stays off (§6). Any re-run on a book where those rows read
  0 is a **new** pre-registration, as §6 requires.
- A per-arm difference in those rows' breach counts is still graded under O6 as a finding against that arm.

### A5. O1: predictions unchanged, attribution note added

N29 and the final-bill net move a **leaver's** money in opposite directions. The set-off lowers a dual-fuel
closer's write-off, which makes leaving look cheaper. The final-bill net stops the world collecting a final bill's
face that the page said credit covered, which takes cash off leavers that the desk had counted. Only the P − F
difference matters here, and O2a predicts the arms' departures differ by −6 to +3 households per seed. At
£4,715.67 / 195 ≈ £24 per affected leg, the differential is of order £10²: an order below O1b's ±£1,500
half-width. **O1a–O1d and §6 legs 2–4 stand.** I cannot yet say the sign of the net differential, and no
prediction is filed on it. The seeds 2–5 spread that §3's eight-seed sizing uses was measured on a book without
these fixes, so the sizing is an estimate carried across books. That was already true on 11 Nov.

O0c (the belief's AUC), O2, O3, O4 and O5 read nothing these commits changed (A1, A2). **No change.**

### A7. The insulation change (e17ebc596), 2026-11-14, before any arm or the 16 Nov book exists

This amendment is about e17ebc596 only. It changes the world's insulation draw (72.1% POOR → 15.2%). The one-variable book A/B, e17ebc596^ against e17ebc596, same seed, neither arm carrying ceeefa5960 or 69866925b (`docs/staging/records/SEAT_RECORD_WHAT_THE_INSULATION_CHANGE_CAN_MOVE_IN_THE_16_NOV_PREREGISTRATIONS_2026-11-13.md`).
- **§8's gate-verdict leg, fabric can move it:** 27 unexcepted breaches across 5 rows (7 excepted) → 19 across 5
  (7 excepted). The publish is refused at both commits. Fabric moves the count and not the verdict. Whether the 16 Nov
  book passes is decided by the other changes it carries, not by fabric.
- **The arms, fabric cannot bias the P − F difference:** both arms run on one book and one world, so the fabric
  draw is shared, a §7 confound. It does change the level the arms are read from: 166 of 358 campaign accounts are
  replaced, and 246 of 673 founders' P&L moves. The §3 sizing was taken on pre-e17ebc596 books and is now one more
  book removed. That is the same caveat as A5.
- If the book passes, the §8 addendum names e17ebc596 among the book's ancestors, beside 3af02a2dd1 and 37d9342869.

**Amendment, 2026-11-14 (later, still before the 16 Nov book): can S6b or the statement walk move it too?** 
- **The gate count, S6b can move it, and only downward.** S6b (69866925b) changes one thing: a leaver's money-in day, which only `generate_credit_refund_log` reads, to date the refund's paid day. The set-offs take that date too. On the r98 replay (`docs/design/REPAYMENT_POSTING_AREA_MAP_2026-11-14.md` s.8, P4/P5) the closing balance is identical on all 850 legs and the refund amount is identical on all 178 refunds. 3 paid days move, every one earlier. None of the 3 carries a set-off. The only rows it can reach are the ones that read a refund's paid day. The one named row is `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO`'s SYN-2016-139 exception, `max_breached: 1`, and S6b exists to clear it. Paid days only move earlier, so S6b cannot add a breach. The verdict changes only if S6b and the other changes together bring the unexcepted count to 0.
- **The statement walk cannot move it.** The statement walk (84a44b51c) changes only `statement_export.account_events`. Its own measurement found `tools/domain_invariant_runner.py --ledger` byte-identical, because the runner reads `raw_account_export.account_events`. It also found `statement_digest` moving on the 84 set-off legs only. The gate is the runner's verdict.

### A6. What this amendment does not do

It launches nothing, arms nothing and flips no switch. `renewal_belief_by_ending_term` stays `False`. §8 stays empty
until launch.
