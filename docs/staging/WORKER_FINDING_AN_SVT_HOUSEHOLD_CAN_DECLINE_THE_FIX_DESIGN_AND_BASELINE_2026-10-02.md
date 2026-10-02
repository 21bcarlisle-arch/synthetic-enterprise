**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `an-svt-household-can-decline-the-fix-and-stay-on-default`, then `an-svt-household-can-decline-the-fix-build-the-splice` (Lane 0 delivery)

# An SVT household can decline the fix: the premise holds, the rule is designed and pre-registered, and the code waits for the retake

Pre-registration: `docs/staging/records/WORKER_PREREG_A_HOUSEHOLD_THAT_STAYS_NEVER_CONTRACTS_A_FIX_ABOVE_ITS_DEFAULT_2026-10-02.md`.

## Where this stands

- **The premise holds at `0a410a961`.** No code reads the offered rate at an SVT conversion. A
  dual-fuel gas leg has no decision of its own at any boundary.
- **Baseline, from the 2f6a9ea05 harness.** 16 of 40 value-arm conversions sit above the
  household's default with renewals capped, and 36 of 38 with them uncapped. Every 2017–18
  conversion sits above it, by up to +59%. That excess is `portfolio_premium` plus `value_arm`
  over a base strike near the SVT. It is not the world's reference.
- **The rule needs no invented size.** A stayer never contracts a fix above its default. The
  destination is SLC 22/23. **The decline-versus-leave share is a declared gap (`None`):** no
  published series conditions on a rejected incumbent offer. The rule leaves every existing leave
  route as it is.

## Why no code landed this turn

1. **The world-D retake is running** (`longjob-arms-floor-d-head-1002b`, floor started 05:56 UTC,
   about 08:35 UTC to exit). Landing `simulation/` now would withdraw it on the page. This is the
   same reason item one's diff is held.
2. **Item one lands first and touches the same block.** `restore-the-journey-decision-for-an-svt-conversion`
   adds `_journey.record_decision` to the conversion branch. Its diff is embedded in
   `WORKER_PREREG_AN_SVT_CONVERSION_RECORDS_A_STAYED_DECISION_ON_ITS_JOURNEY_2026-10-02.md`.
3. **The decline needs a splice, not a flag.** The faced rate comes from `decide_renewal_rate` in
   the run loop, and `all_terms` is static. A declined term has to be replaced by
   `build_svt_schedule` segments in a 4,000-line loop, without moving the PB6 seed alignment. The
   pre-registration names the three hazards and the R13 byte-identity control.

## Owed, in order

1. After the retake exits and item one lands: build the splice and the decline event, plus the one
   partition control (accept / `declined_fix` / churned), mutation-proven.
2. Run the default world and the value arm serially at one commit. Grade P1–P6.
3. Write the `decline_versus_leave_share` gap into `docs/institutional/knowledge_map.md`'s
   retention row when the code lands, so the gap and the rule land together.

## 2026-10-02 (later): the splice is built and landed SWITCHED OFF; P1-P6 are not yet graded

Claim `an-svt-household-can-decline-the-fix-build-the-splice`. Built on origin/main `5a4807d9a`.

**What landed.** `customer_events.renewal_outcome` is the rule: churned stands, else a stayer whose
offer sits above its own fuel's default (`position_vs_default`, i.e. `_svt_position`) is
`declined_fix`, else `accepted`. `declined_fix_event` writes the row. Its `event_type` is
`renewed`, its occasion is `declined_fix`, `unit_rate_gbp_per_mwh` is None, and the refused rate
and position each have their own field. `run_phase2b` takes the decision at one place, after
stay/leave is known. On the decision leg that is after the roll (fixed→fixed) or the conversion
row. On a leg that does not decide, it is after the renewal block. A decline then replaces the
term with `build_svt_schedule` segments, pushed onto a heap keyed `(term_start, cid, seq)`.
**The switch `run_phase2b.DECLINE_A_FIX_ABOVE_THE_DEFAULT` is False**, so this commit changes no
world output. The pair of runs flips it in-process.

**The three hazards, as built.**
1. *Seed alignment.* A spliced segment carries `_DECLINED_FIX_SPLICE`, does not advance
   `term_indices`, and takes the index of the term it replaced. C1b's roll on it is seeded on
   `(account, segment start)`, not on the index.
2. *Declined-offer state.* The code restores the prior rate. It undoes the bill-shock count when
   this term added one, withdraws the account-state row, and restores `_last_tariff_type`, so a
   conversion's decline continues the SVT stint and a fixed→fixed decline opens one. The rival
   ledger never observes a refused offer. **Kept, deliberately:** the chain's own logs (the company
   did strike that quote), and the renewal window's surveys, complaints, retention offer and
   journey advance (the household did have the renewal).
3. *Byte identity.* With nothing spliced, the heap pops in the same order as the stable sort it
   replaced.

**Control.** `tests/simulation/test_a_household_that_stays_never_contracts_a_fix_above_its_default.py`.
It asserts `outcomes >= {accepted, declined_fix, churned}` before it asserts what each does, plus
a chain leg that `_main` calls the rule at both sites. Mutations: dropping the decline branch,
declining at parity (`>= 0`), and dropping churned's precedence each turn it red (1 failed each).

**A smoke, NOT the graded pair.** 2016–2018 window (`report_end="2018-12-31"`, `SIM_FAST_MODE=1`),
run serially while another world run was on the box. Timing is meaningless; the outputs are
deterministic.
- *Rule off vs origin/main code:* `cmp` of the full sorted-JSON result (168 MB): **byte-identical.**
  P6's shape, on a short window.
- *Rule on, default world:* 8 `declined_fix`. 2017: 1 conversion, 1 electricity fixed→fixed, 1
  gas-only fixed→fixed, 1 dual-fuel gas leg. 2018: 3 conversions, 1 fixed→fixed. **P5 on the run's own account-state rows: 0 of 28 retained
  domestic fixed terms at term_index ≥ 1 sit above the default, against 8 of 36 with the rule off.**
  Churned billing accounts 30 → 31, total net £18,964 → £18,890. Conversions declining: 4 of 18.
  That is P2's side, but only just, and it is not graded here.
- *Value arm, same window, rule off vs on:* rule off, **31 of 36** retained domestic fixed terms
  sit above the default. Rule on, **33 `declined_fix`** (2017: 8 fixed→fixed, 5 conversion or gas
  leg; 2018: 2 fixed→fixed, 18 conversion or gas leg), offers +0.7% to +59.6% over the default.
  **No accepted `svt_conversion` row is left in 2017–18**, and P5 is 0 of 5. Total net £24,969 →
  £23,099; churned 31 → 32. These are P1's and P4's directions, not their grading.
- First smoke caught a defect, fixed before landing: `roll_lifecycle_event` writes no
  `departure_rolled`, so a fixed→fixed decline carried None. The constructor now sets True.

**Item one is still not on origin.** `restore-the-journey-decision-for-an-svt-conversion` is
held by another seat (`land-the-journey-decision-for-an-svt-conversion-now`). Its diff edits the
`if not _rolled:` conversion branch, which this commit split into a declined arm and an accepted
arm. **Resolution for whoever rebases: put `_journey.record_decision(..., switched=False)` above
both arms.** A household that declined the fix also stayed, so the journey decision is the same.

## Owed, in order (replaces the list above)

1. Once item one is on origin and no world run is on the box: run the default world and the value
   arm, each with the switch off and on, at one commit. Grade P1–P6 here. P5 is DONE's condition.
2. If they hold, set `DECLINE_A_FIX_ABOVE_THE_DEFAULT = True` in a separate commit that cites this
   grading. Before that flip, audit the readers that select renewals by `departure_occasion ==
   "renewal"` (`tools/population_anchor._churn_by_year` and kin): a fixed→fixed decline moves out
   of that occasion while still rolled, so it leaves a renewal-occasion denominator. Select it back
   by `departure_rolled`, or keep it out by name. Decide which per reader.

## Reader audit before the flip (autonomous worker, 2026-10-02, base `6547ac55e`)

**No production reader selects on `departure_occasion == "renewal"`.** `git grep` over
`simulation/ company/ saas/ tools/ site/` finds the occasion constants only in
`customer_events.py`, `run_phase2b.py` and tests. `tools/population_anchor` counts by
`event_type`, not occasion, so a fixed→fixed decline stays in its renewal denominator as a
`renewed` row. The owed item's worry about a renewal-occasion denominator has no reader behind it.

**The readers that count `event_type` do have a defect, on one of the three producers.** A
conversion decline *replaces* the `svt_conversion` row, and a fixed→fixed decline *replaces* the
rolled row, so both are net zero for every counter. The **riding leg** is different. That is the gas
leg of a dual-fuel household, which takes no stay-or-leave decision, and before the splice it wrote
no row at all. Its decline was *appended* to `customer_events` as `renewed`, under the gas leg's
own id, so:

- every renewal-decision counter gained a decision nobody took (`population_anchor`'s
  `sim_churn_rate` is a published gate metric, plus `churn_accuracy_report` true negatives and
  the annual report's "Renewals (retained)"); and
- `departure_population.union_by_year` gained an *account* (`Xg`) that is present only in the
  years it declines. That shape is what `account_denominator_refusal`'s interior-gap leg refuses
  on, so the whole-book rate could go unreadable for a reason that has nothing to do with the
  world.

The default-world smoke above shows this producer firing: one dual-fuel gas leg in 2017.
**Fixed in this commit:** those rows now go to their own result key, `declined_on_the_riding_leg`.
This follows the precedent `svt_departures` set for the same reason. Control:
`test_a_decline_on_the_leg_that_does_not_decide_is_not_a_renewal_decision`. Pointing the append
back at `customer_events_log` reds it (mutation run, 1 red).

Other readers checked and left alone:

- `tools/project_portfolio_to_2026` falls back to `tariff_max` when a last row has a `None` rate.
  A decliner is on the default, so the fallback is the right price.
- `tools/generate_customer_data` guards `None`.
- `grade_renewal_churn_belief` grades a rolled decline as retained, which is correct because it
  stayed. It skips conversion declines as `no_logged_belief`, as it already skipped
  `svt_conversion` rows.
- `_main`'s summary `continue`s on `departure_rolled is False` before it indexes
  `churn_probability`.

**Still owed:** item one on origin, then the P1–P6 runs at one commit, then the flip.
