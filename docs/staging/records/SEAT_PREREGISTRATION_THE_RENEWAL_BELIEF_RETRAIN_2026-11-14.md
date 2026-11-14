# Pre-registration: the renewal churn belief, retrained

**Written 2026-11-14 by the delivery seat, after the 12-draw family's grade landed (`7c613a1bd1`,
`docs/design/THE_VALUE_TEST_REDESIGN.md` §7) and before any retrain code exists.** Claim:
`the-renewal-belief-retrain-is-preregistered-before-it-is-built`. No code was written and nothing
was scored for this file. I deliberately did **not** read the ending-term mix of the value test's
renewals, because that mix nearly *is* the AUC predicted in §3 (see §2). This file is therefore the
last moment that prediction can be made blind.

**The family grade it was written after.** In the 12-draw family the belief's AUC against who left
under the flat price is **0.530 to 0.572** (mean 0.549), on about 250 scored renewals per seed with
35 to 38 leavers. Believed minus realised retention is **−0.21**. The whole advantage is **£5.24 per
household-year, 95% interval −£3.34 to +£14.35**, across households. Roll noise is 4.6% of the
per-household variance, so a £3 effect needs about 4,860 households. The baselines below are the
ones the item names. On 2019's 268 desk states the belief scores **0.333**. On the published 8 Oct
run it scores **0.52 (0.41 to 0.65)**.

## 0. What already exists, and a correction to the item's framing

The item reads as if no corrected belief exists. **One does, and it is default off.**
`DecisionPolicy.renewal_belief_by_ending_term` (`7a7ad95dc`, 21 Oct) scales today's belief by the
company's own observed-over-expected losses for each **type of term the renewal ends**: a fix, a
default stint, or a default stint entered by refusing our fix at an earlier roll. The multiplier is
shrunk towards 1 using the published width (`switching_gradient_by_tariff_and_payment_what_the_record_can_grade.md`
§5, §5a). How it scored:

- out of sample on the 268 2019 desk states, fit on pre-2019 history: **0.819 [0.757, 0.877]**;
- in-run, with the §5a prior: **0.806 [0.745, 0.860]** (`a7fc5c728`);
- in money, run against flat in §14 and again on the clean book (`5cdb72eb3`): net +£2,781 ± £2,277,
  but the departure interval straddles zero, so the switch stayed off.

**It has never run inside the value test.** The value test's per-customer arm carries today's
unconditioned belief. That is the belief scored at 0.52 and at 0.53 to 0.57.

So "the retrain" is defined here as **two changes on top of that switch**. §1 states them. The 2019
AUC prediction in §3 is weakly informative, because the switch's 0.819 is already known. The
prediction that carries information is the one on the value test.

## 1. What the retrained belief would change

**The 0.819 is almost entirely one binary split.** On the 2019 states, 40 of 46 leavers (87%) were at
the end of a fix, and 170 of 222 stayers (77%) were not. A classifier that knows only "is this the
end of a fix" scores 0.87 × 0.766 + ½(0.87 × 0.234 + 0.13 × 0.766) = **0.818**. Today's belief adds
no ranking within a type, and inside the switch it still sets the ranking within each type. That
fixes what the retrain must do.

| | Today (live) | Switch (`7a7ad95dc`, off) | Retrain (this file) |
|---|---|---|---|
| Ranking feature | rate change, tenure, consumption, shock count, payment behaviour, satisfaction (`get_churn_estimate`, `sim_interface.py:248`) | the same, × a per-type multiplier | **type of term ending** (fix / default / default after a refused fix), plus **price position at the roll**: the company's renewal rate against the published cap for that period and against its own acquisition tariff on sale that day |
| Level (calibration) | believed retention 0.64 against realised 0.85 to 0.86 | unchanged inside each type | **fit to the company's own closed renewal outcomes**, so the level is learned, not inherited |
| Model | hand-set rate-sensitivity curve, max() with the payment model, capped at 0.95 | as today, × m(type) | a per-type base rate (Jeffreys, shrunk to the §5a prior) × a single learned price-position slope, in survival space |
| Training window | none (constants) | closed renewal years before the desk date | **expanding window of closed renewals strictly before the desk date**. In 2016 there is no own history, so the §5a prior alone decides, and that is stated, not hidden |

**What a real supplier can see at each desk state.** Each is one of its own records or a publication.
None comes from the world.

- The ending term's tariff type and dates, and whether we offered a fix at an earlier roll and it
  was refused. These are the company's own contract records.
- The rate it is about to bill, the rate it billed before, and its own acquisition tariff that day.
  These are company pricing (`CompanyTariffEngine`, imported at `sim_interface.py:22`).
- The default-tariff cap for the period. This is an Ofgem publication.
- Tenure, payment method (`get_payment_method`, `sim_interface.py:176`), arrears state as of the
  desk date, and the shock count.
- **The training label is the loss event alone**: the account leaving supply, as reported through
  `notify_churn` (`sim_interface.py:212`) and `churn_notifications`. **The retrain must never read
  `sim_churn_probability`**, which that same call carries as a world ground-truth field. The retrain
  is exactly the code most likely to reach for it. Its exit test must fail if any training row is
  built from it.
- **Not visible, and not proxied:** the household's elasticity, its competitor quotes, the
  world's `churn_roll`, and any segment label (the D-SEGMENT wall).

**Excluded, with the reason.** A fix refused **at this roll** is never a feature. It is written only
for a household that stayed, so it would label the non-leavers (§5 of the knowledge page).

## 2. Why the value test should score lower than 2019

1. **The window spans 2021 to 2023.** Fixes all but vanished and leaving collapsed then, so the end
   of a fix stops predicting departure in those years. Pooling years with different base rates
   pulls the AUC down.
2. **In 2016 to 2017 the multiplier is shrunk to about 1** (there is no own history). Those renewals
   rank with the shape of today's belief.
3. **The scoring population differs.** The value test's 0.53 to 0.57 is not 2019's 0.333, so its
   renewals are not 2019's mix. The leavers' share at the end of a fix is the quantity that sets
   the AUC, and I have not looked at it.

## 3. Predictions

All intervals are 95%, clustered on accounts, as the redesign's rules require. The point and range
given are for the **point estimate**.

- **R1. 2019 desk states (268, fit before 2019): AUC 0.82, range 0.79 to 0.86.** This is the
  switch's 0.819, give or take what price position adds. The predicted gain over the switch is
  **+0.00 to +0.04**: §9's roll type + price read 0.742, and the ending-term term beat it by +0.077
  [−0.01, +0.17], so price adds little once type is known.
  - Refuted below 0.79 (the refit level or price slope *costs* ranking) or above 0.86.
- **R2. Value test, against who left under the flat price** (the households the per-customer arm
  did not price, the "held-back" set the item names; about 250 renewals, 35 to 38 leavers): **AUC
  0.68, range 0.60 to 0.78**, and the interval's lower end is **above 0.50**.
  - Refuted if the point estimate is under 0.60 (the type split does not travel beyond 2019), or if
    the interval includes 0.50.
  - Also refuted above 0.78, which would mean the crisis years did not dilute it. I would then
    distrust the pooling before believing the belief.
- **R3. Calibration on the same set: believed minus realised retention between −0.06 and +0.06**,
  against today's −0.21. It is fit on its own outcomes, so it should be close.
  - Refuted outside ±0.06.
- **R4. Money: the whole advantage per household-year in the value test, with the retrained belief
  in the per-customer arm, is +£3 to +£9** (point **+£6**), against the family's +£5.24 (−£3.34 to
  +£14.35) and the published +£2.86. Its interval **still includes zero**.
  - Why so small. The belief's only act is the retention offer and its framing (§17 of the per-customer
    switches record, `1044c8fe0`). Through §14 and its clean-book re-take, the switch moved net money
    by +£1,556 and +£2,781 on the whole book over the run, so about **£1 to £1.50 per household-year**.
    Better calibration also stops offers to households that were never leaving, and offers cost
    money (§12: 122 offers cost £2,968).
  - **Refuted if the point estimate is below +£3** (the retrain moves no money: ranking was not the
    binding constraint). **Also refuted if the interval excludes zero on the positive side.** That
    would be the thesis's first evidence, and I do not expect it from a 272-household book. §7 says
    a £3 effect needs about 4,860.

## 4. Which family result makes the retrain not worth running

The retrain is worth building only if a better ranking can turn into money the test can see.
**Do not build it if the `churn_roll` family (the next measurement §7 names) shows both of these:**

1. **Roll noise is still under a quarter of the per-household variance.** The book-size arithmetic
   then stays at about 4,860 households for £3, and R4's whole predicted range (+£3 to +£9) is below
   what a 272-household book can resolve. The retrain could only produce "not distinguishable from
   zero" again, which tells us nothing.
2. **Re-drawing who leaves moves the belief's flat-arm AUC by less than ±0.03.** That would mean the
   2019 inversion is a property of 2019's mix rather than of the belief, and the coin reading in
   the value test is what the belief really does there.

**Also stop if the published-configuration re-run** (§2's second test, which separates (a) from (c))
shows that the value arm's level leg is set by something other than the belief's offers. In that
case the money that R4 is about is not the money the belief governs, and the first lever is the
price level, not the belief.

**Build it if** the `churn_roll` family puts roll noise above half, or the book is resized to the
thousands. Then a +£6 effect is inside reach, and R1 to R4 are graded on that book.

## 5. What this does not do

It does not switch on `renewal_belief_by_ending_term`, write the retrain, or launch a run. Those
wait for §4's family results and the seat's ranking after the 16 Nov reset (DIRECTION `not_now`:
"Building the renewal belief retrain now"). It grades nothing. R1 to R4 are graded only by the run
that first carries the retrained belief, and that run's record must cite this file's commit.
