# Pre-registration: the run reads the household-save switch and answers both of a dual household's notices

**Written 2026-10-19 ~23:45 BST, before the build.** Claim
`the-save-offer-run-reads-its-switch-and-answers-both-notices` (Lane 0, seat direction). Step 1b of
`docs/staging/WORKER_FINDING_THE_COMPANY_DECIDES_A_DUAL_HOUSEHOLD_PER_LEG_AND_C35_CHARGED_IT_TWO_RISES_FOR_ONE_BENEFIT_2026-10-18.md`
§5. No caller code exists yet, and no run was read to write this. The build is a later commit.

## What is being built

- **The switch** is `DecisionPolicy.save_offer_decides_per_household`. It was landed at `c002699e7`,
  default False, declared `run_argument`. On `origin/main` it has no run consumer.
- **The caller.** At the save site in `simulation/run_phase2b.py` (a churned, domestic, fixed-term
  departure with save offers active), the run builds one `SaveLeg` for the decision leg and one for
  each other point whose term starts on the same date on a fixed tariff. It hands them to a new
  door function in `company/interfaces/save_offer.py`, which keeps only the legs whose Invitation the
  company holds and calls `company.crm.save_offer.save_rates_for_decision`.
- **The decision leg's rate** is the household decision's. The world re-asks the roll at it, as it
  does today.
- **Carry.** If saved, each other leg's save rate is billed on that leg's term when it is priced
  (only if it is below the rate the chain struck).
- **Off** takes the existing `request_save_offer` path, untouched.
- **Not built:** step 1c (the world weighing the combined bill). Knowledge: fuel page §8a, "Where
  the run answers both notices", landed with this file.

## Predictions

**O1, off arm.** A run at the build's sha with the switch off equals a run at its parent, byte for
byte (`cmp` on the run-output JSON), at a fixed seed, on the short window to 2017-06-30. Any
difference refutes the build.

**S1, the short window cannot decide a save, on either arm. Said before the run, from the code.**
- No Invitation to Intervene is emitted before CSS (requests from 18 July 2022).
- The per-fuel published default is None before 2019.
- The published best-deal gap is 0 from 2021-Q4 to 2023-Q2.

So on the window to 2017-06-30:
- **households decided on one offer: 0**
- **households decided on two offers: 0**
- every save-log row has `invitation_held` False.

The on arm equals the off arm in every top-level key, except for the new per-row fields on
`save_on_loss_notice_log`. Those fields record zero legs answered on every row.

**This means the directive's count ("one offer against two, on the short window") is 0 against 0 by
construction.** It is not evidence that the branch decides. That evidence is:

**D1, the on branch decides (the control, not a run).** A control drives the door with a held pair
of notices on a dual household after 2023-Q3. Before it asserts anything else, it asserts that the
on branch reaches a decision answering **both** points. Then it asserts:
- a single-fuel household is answered on one point;
- off answers only the decision leg, as `price_match_save_rate`;
- a leg whose notice is not held is left out.

**P1, a window that can decide (not part of DONE, graded when such a run is read).** These are
predictions for a run to at least 2024-06-30 (saves can be offered from 2023-Q3). Dual households
are about 76% of the book. So:
- of households decided on the on arm, **at least 60% are decided on two offers**;
- on the off arm, **every** decided household is answered on one offer.

The verdict record's P1 holds too. The world weighs only the decision leg, so the count saved does
not rise by more than the decision leg's own rate move explains. The gas leg's term rate falls on
retained dual homes, which is a transfer to the household and not created value.

## How it will be graded

O1, S1 and D1 are graded in the build commit. P1 needs a run past 2023-Q3, which is not part of DONE
for this claim. If no such run is read, P1 stays ungraded here, and this file says so.

## Grade, 2026-10-19 (build commit; short window to 2017-06-30, CURRENT_POLICY, fixed seed)

The prereg landed as `b244ae11e`. All three arms ran on that commit: the parent from a clean
worktree, and the build as that commit plus the three code files.

- **O1 held.** The off arm at the build and the run at its parent give run-output JSON that is
  byte-identical (`cmp`, 5,636,752 bytes each).
- **S1 held, digit for digit.**
  - The on arm equals the off arm in all 89 top-level keys except `save_on_loss_notice_log`.
  - Its 12 rows equal the off arm's once the two new fields are stripped.
  - 12 departures reached the save site. 0 held an Invitation, so 0 households were decided on one
    offer and 0 on two.
- **Not predicted, read from the same run:** the run built two legs for 10 of the 12 departures and
  one leg for 2. So the leg assembly finds the riding gas term on real schedules, which the window
  could not show through a decision.
- **D1 held** (`tests/simulation/test_the_household_save_answers_both_notices_at_the_roll.py`). The on
  branch reaches a decision answering both points, and that is asserted first. Five mutations each
  turned it red:
  - the held-notice filter dropped (1 red);
  - the riding leg never built (2);
  - the door ignores the switch (1);
  - a default-tariff riding leg admitted (1);
  - the decision leg's own Invitation not required (1).
- **An equivalence, not a missing test:** passing kWh where MWh is wanted stays green. Both legs scale
  together, and the household rule reads only the sign of the summed headroom.
- **Not shown by any run here: the carry.** That is the other leg billed its save when it is priced.
  No save can be taken before 2023-Q3, so the carry is first exercised by P1's run.
- **P1 is not graded.** It needs a run past 2023-Q3.
