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

## Raised by one reader only (not filed under the vote; each checked by the seat at HEAD `80d4422589`, 2 Nov)

- A#8 (MAJOR): the tariff-placement arm assumes the world draws an SVT household's take-up of an offer. The cited
  `CUSTOMER_NEEDS_BEYOND_THREE_CURRENCIES.md` §5 does not show that, and the feed calls the conversion desk unbuilt.
  **Confirmed.** §5 lists traits the world "should draw as a joint distribution", and that note's §3 says it "makes
  no claim about the code". `decisions.decisions_that_existed.outside_it` (`product_not_upliftable`) calls the
  conversion "a desk this company has not built". The world's `svt_conversion_event`
  (`simulation/customer_events.py:512`) records a household leaving the SVT at a term boundary. It is not a drawn
  response to an offer the supplier makes.
- A#9 (MINOR): reading 5's 0.264–0.8 ratio is the 18 Sep run's and is not labelled with its run.
  **Confirmed.** `control_as_share_of_regulated_allowance` sits under the feed's `decisions` block (18 Sep,
  b329e702b). Reading 5's row omits the block name, so its run cannot be read from the row.
- B#2 (BLOCKING by B): choosing at a matched price level can itself be a transfer, by charging inelastic
  households more. `household_side` has households paying 13.2% over the cap on the value arm against 11.3% on
  control. The renewal arm has no household-share pass/fail rule.
  **Confirmed in substance. The 8 Oct figures do not show it on the choosing leg.**
  - The numbers are right: value −13.20%, control −11.34% (`household_side` in
    `value_cycle_ab_s1_three_arm_20261008r.json`).
  - But the level arm is −13.47%. On that run, matched-level choosing left households 0.27 points *better* off
    than flat at the same level. The rise against control is the level leg's.
  - The 18 Sep run's `household` block in the feed goes the other way: value −20.07% against level −19.43%. There,
    choosing cost households 0.64 points.
  - So the mechanism is live and the two runs disagree on its sign. Each percentage is over its own arm's book
    (1,779 and 1,724 customer-years on 8 Oct), so they are not one population.
  - The missing rule is real. Rule 6's customer-cost axis is a "no worse" test in name only: it has no margin and
    cannot return a loss (pair 5).
- B#4 (MINOR): 1.9% is of cap costs excluding headroom, VAT and the allowance itself, not of revenue. The post-Oct
  2023 allowance is not a flat £44.
  **Confirmed.** `docs/domain_artefact_library/regulatory/price_cap_ebit_allowance.md` §B quotes the base as
  "excluding headroom, VAT and the EBIT allowance itself". §C gives a fixed £19.76 plus 1.3975% of the cap level,
  £45.16 in 11a. The note's "1.9% of revenue" and "about £44 per customer a year" misstate both.
- B#9 (MAJOR): §6 publishes a sign against the £2 control (step 2) before the sourced baseline exists (step 4).
  **Confirmed.** Step 2 says the runner "alone lets the page state the sign its family already carries", and that
  sign is against £2/MWh. The artefact's §D calls that control a fraction of the allowance. The fix need not
  reorder the steps. A sign published at step 2 can say on its face that it is against a sub-allowance control.
- B#10 (MAJOR): the acquisition-only tariff ban (SLC 22B, Apr 2022 to Mar 2027) and the pre-2017 four-tariff limit
  are not applied to the renewal or acquisition arms.
  **One of its three legs confirmed.**
  - *Acquisition arm: confirmed.* The note never names SLC 22B, and a per-prospect margin not open to existing
    customers breaches it from 1 Apr 2022. The check exists to reuse: `NO_ACQUISITION_ONLY_TARIFF`
    (`company/compliance/domain_invariants.py:990`).
  - *Renewal arm: refuted.* The Market-wide Derogation from 14 Apr 2022 expressly permits "bespoke, retention-only
    deals" at the end of a fixed term (same file, :974-980).
  - *Four-tariff limit: refuted for this world.* Ofgem stopped enforcing the RMR rules on 14 Apr 2016
    (`docs/market_research/tariffs_and_the_default_tariff_2026-10-25.md` §6). No renewal in the run predates that.
    The formal removal date is unverified there.
- B#11 (MAJOR): prediction 4 forecasts a pure transfer and does not say whether confirming it counts for or against
  the thesis.
  **Confirmed, with one refinement.** Prediction 4 fixes signs only: households pay less and company margin falls.
  It does not say how the thesis reads either outcome. "Pure transfer" over-reads it, though. Created against moved
  turns on the size of the household's gain against the company's loss, and the prediction states neither.
- B#12 (MINOR): the cap baseline for the tariff-placement arm has no 2016–2018 plan. A#7 adds that the prepayment
  cap from Apr 2017 exists.
  **Confirmed.** Rule 4's 2016–2018 GAP is written under the fixed-term bullet only. The CMA prepayment charge
  restriction ran from Apr 2017 to Dec 2020. Its levels are already a named GAP in
  `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md:144-147`, and the note does not cite it.
- B#14 (MINOR): prediction 2's bar is t(0.975, n−1), and no seed count is fixed, so the author can steer it.
  **Confirmed.** The feed's `distance_to_a_sign.sems_needed_is_derived_from_the_family_size` is true, and the bar is
  4.30 = t(0.975, 2). At 12 seeds it would be 2.20. Prediction 2 names no n. The feed's own text says "the seed
  set is fixed before the draw", so the fix is one number in the pre-registration.

**What the unpaired check says.**
- 7 of 9 hold in full, B#2 holds in substance, and B#10 holds on one of three legs. None is wholly refuted.
- On this design, the both-raise vote dropped about as much true signal (8) as it kept (7).
- n = 1 design, so this is not a rate. It is one data point for the 11 Nov two-reader review.
- **The director's row `the-design-read-of-the-value-test` is unchanged.** Neither B#2 nor B#10 touches what he
  ruled: the first step's two measurements and the renewal baseline. Both are fixes inside his frame. They join
  pairs 3–6 in the one amendment pass after his answer: a household-share rule on the renewal arm, and SLC 22B on
  the acquisition arm.

## Measured like the code review

- **Precision:** 7 of 7 filed pairs confirmed. Pair 1 counts once, though its two halves give different reasons.
- **Coverage:** 2 of A's 9 findings and 7 of B's 14 were left out by the vote. *Correction, beside the claim:* they
  were unchecked when this was first written. They have now been checked above, and 8 of 9 hold at least in
  substance, so on this read the vote did discard signal.
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
