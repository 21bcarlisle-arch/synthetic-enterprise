**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# The first fresh-context design read: two blind readers on THE_VALUE_TEST_REDESIGN.md raise seven defects in common, all seven confirmed, and two of them undercut the first step the director ordered (2026-11-02)

*Delivery seat, for part 2 of the 2 Nov goldfish-read steer
(`docs/staging/advisor/done/DIRECTOR_STEER_THE_NAIVE_ORGAN_HAS_REFUSED_EVERYTHING_SINCE_10_AUG_AND_DESIGNS_GET_A_GOLDFISH_READ_2026-11-02.md`).
This is the design read live on its first qualifying proposal. It is not an edit of the note.*

## How it was read

- **Readers.** Two `phase-close-evaluator` agents with no write or edit tools, given the note's path only, primed
  differently: A as a goldfish reader of assumptions and claims, B as a GB-energy and experimental-design skeptic
  asking "can this test lose?". Both read the code and data the note cites, including the 8 Oct run files
  `value_cycle_ab_s1_{three_arm,noise_floor}_20261008r.json`.
- **Blindness, and its limit.** Both were told not to open `docs/staging/`, `docs/direction/`, `docs/status/` or the
  git history. That was an instruction, not an extract: unlike `two_reader_review`'s `git archive` packet, they ran
  in the repo. They also saw the note's own two in-place corrections, which are part of the note.
- **Vote.** The two-reader rule: a finding is filed only when both raise it. The seat did the pairing by hand, not a
  tool-less matcher. One pair (1 below) joins two different reasons about the same claim, and it is marked as such.
- **Verdicts.** A NEEDS_WORK (9 findings), B NEEDS_WORK (14). Both are in the trust ledger as
  `design-read-2026-11-02:THE_VALUE_TEST_REDESIGN@efc8340b5:arm{A,B}`.

## Raised by both, each checked by the seat on the files (7 of 7 confirmed)

1. **The "published draw outside its family" anomaly, and prediction 1, are mis-framed.** *Two reasons, both true.*
   - A: the value arm sits inside its family. Published £240,832, re-draws £240,401–£241,270.
   - A: the control arm does not. Published £235,588, re-draws £229,503–£231,026. The level arm doesn't either:
     £229,488 against £232,674–£235,953. So £5,244 is low because the flat £2/MWh control earned at least £4.5k more
     than on any re-draw. It is not about how choosing was split.
   - B: a fourth draw lands outside the range of three with probability 2/(n+1) = 50%. £5,244 is inside the
     three-draw 95% prediction interval (£3,832–£16,727). So the 12-draw test refutes prediction 1 often under the
     null and cannot separate cause (a) from cause (b).
   - *Checked:* the per-seed nets in `value_cycle_ab_s1_noise_floor_20261008r.json` (`control_net_gbp`,
     `value_arm_net_gbp`, `level_arm_net_gbp`) against `value_cycle_ab_s1_three_arm_20261008r.json` (`*_arm.total_net_gbp`).
2. **Prediction 5 (PROS-2016-0098 under today's write-off rule) is already answered on disk, and on the wrong
   contrast.**
   - Its selection contribution is −£17.60 on every one of the three 8 Oct seeds (`selection_by_account_gbp`).
   - The −£5,344.10 the note carries is the `root_cause` distance. That case lives in the level arm:
     `p_retain_level_arm_by_seed` is 0.34 and 0.64, against 0.758–0.788 in the other arms.
   - B puts its whole-advantage share at −£2,555. That is £95 under the £2,650 threshold, so the prediction was not
     made blind.
3. **§4 misstates the write-off rule, and the 8 Oct run is not on today's rule.**
   - `post_write_off_recovery_share` returns 1 − `prov_coverage_final_bill_over_90d`. For q3 it raises
     (`simulation/arrears_engine.py:264-287`).
   - The convention was `final_bill_due_date` at 45122d156. It is `company_closed_account_write_off` since 2b70102f9e,
     29 Oct.
   - The DD-timing change is 1b82c3c0e3, 28 Oct.
   - So "under the current rule" cannot be one variable at 45122d156, and §6 step 1 as written is not a
     one-variable run.
4. **The 2,490 are term boundaries, not households.**
   - `decisions.decisions_that_existed.what_each_denominator_counts` says `renewals_the_world_offered` counts "every
     TERM BOUNDARY … including … a price-cap revision".
   - So "where most of the book is" does not follow.
   - Prediction 3's "decides 107" is the 18 Sep run's count, and rule 1 forbids mixing runs. The 8 Oct run reads
     272/278/107 depending on the field.
5. **Rule 6 cannot return a loss and has no margin for "no worse".**
   - Its only verdicts are "settled" and "we cannot tell". A reliably worse arm also reads "cannot tell".
   - "No worse" carries no equivalence margin.
   - Prediction 6 contradicts the rule's own "measured axes" clause.
6. **Book sizing from the family's spread is not grounded.**
   - The re-draw changes elasticity for 72 of 272 accounts (`accounts_redrawn` 72, settled 272, on all three seeds).
   - That spread measures the instrument on one roster. It is not variance between households, so a power
     calculation on N cannot rest on it.
7. **The EBIT allowance is not "the best a flat supplier could do" for renewals.**
   - The repo's own artefact says the allowance governs the default tariff, not a fixed term a customer chooses
     (`docs/domain_artefact_library/regulatory/price_cap_ebit_allowance.md:136-139`).
   - Flat-margin profit is not monotone in margin: the level arm at £61.75/MWh earned £229,488, below the £2/MWh
     control's £235,588.
   - The best flat rule is an empirical optimum, and a margin sweep (`tools/run_price_ladder.py`) finds it.

## Raised by one reader only (not filed under the vote; kept for the 11 Nov review)

- A#8 (MAJOR): the tariff-placement arm assumes the world draws an SVT household's take-up of an offer. The cited
  `CUSTOMER_NEEDS_BEYOND_THREE_CURRENCIES.md` §5 does not show that, and the feed calls the conversion desk unbuilt.
- A#9 (MINOR): reading 5's 0.264–0.8 ratio is the 18 Sep run's and is not labelled with its run.
- B#2 (BLOCKING by B): choosing at a matched price level can itself be a transfer, by charging inelastic
  households more. `household_side` has households paying 13.2% over the cap on the value arm against 11.3% on
  control. The renewal arm has no household-share pass/fail rule.
- B#4 (MINOR): 1.9% is of cap costs excluding headroom, VAT and the allowance itself, not of revenue. The post-Oct
  2023 allowance is not a flat £44.
- B#9 (MAJOR): §6 publishes a sign against the £2 control (step 2) before the sourced baseline exists (step 4).
- B#10 (MAJOR): the acquisition-only tariff ban (SLC 22B, Apr 2022 to Mar 2027) and the pre-2017 four-tariff limit
  are not applied to the renewal or acquisition arms.
- B#11 (MAJOR): prediction 4 forecasts a pure transfer and does not say whether confirming it counts for or against
  the thesis.
- B#12 (MINOR): the cap baseline for the tariff-placement arm has no 2016–2018 plan. A#7 adds that the prepayment
  cap from Apr 2017 exists.
- B#14 (MINOR): prediction 2's bar is t(0.975, n−1), and no seed count is fixed, so the author can steer it.

## Measured like the code review

- **Precision:** 7 of 7 filed pairs confirmed. Pair 1 counts once, though its two halves give different reasons.
- **Coverage:** 2 of A's 9 findings and 7 of B's 14 were left out by the vote and were not checked. On a first
  read, nothing here says whether the vote discarded signal.
- **Prior in-turn reads:** they did not catch any of the seven. The note's own §2 shows they caught the
  reading-4 misread and the "in full, no recovery" write-off error. Pair 3 shows that correction was itself
  incomplete.
- **What this says about the judge, not the note:** n = 1 design. Nothing here is a rate.

## What it changes

Pairs 1, 2 and 7 reach the director's 18:38 ruling. He ordered two one-run measurements first: the 12-draw
family, and PROS-2016-0098 alone. He also set the renewal baseline at the EBIT allowance.
- The first measurement tests a framing the read refutes.
- The second is already answered on disk.
- The baseline is one the repo's own artefact says does not apply to fixed terms.

These are changes to something he ruled (G9), so they go to him as a proposal: `for_the_director` row
`the-design-read-of-the-value-test`. Nothing in the note is edited until he answers. Pairs 3–6 are
factual or method corrections inside his frame. They land with the note's amendment, after his answer, as one pass.
