<!-- PROCESSED 2026-07-29 (scheduled tick) → PLANNER_MINTED_ca_promotion_ratification_consumption_2026-07-29.md.
     OPEN SUB-ITEM (director-reserved, why this is parked in in_progress/ not done/): the four LEVEL_UP moves
     are UNRELEASED — the mechanism parses ZERO directives (`L3` ≠ digit) AND the doc is untracked / no
     authenticated ledger entry exists (R16). RELEASING ACT: director-console record_level_up(CA1/CA2/CA3→3,
     CA4→1) OR advisor commits this doc as bridge author with digit-form `LEDGER:` lines. Also flagged to
     author: §4 defect (no WORK-THIS-CREATES block). CA2-finding-publish is drawable now under the CA2 atom. -->

# [DIRECTOR-RULING] — CA cohort promotion batch: RATIFIED (2026-07-29)

**Type:** [DIRECTOR-RULING] via advisor bridge. Answers `[ACTION NEEDED] CA_cohort_promotion_batch`.

## Ratified

```
LEDGER: LEVEL_UP_PROPOSED CA1_cohort_assignment_live L3
LEDGER: LEVEL_UP_PROPOSED CA2_coverage_report_realised_cohort L3
LEDGER: LEVEL_UP_PROPOSED CA3_segmentation_untestable_ledger_marking L3
LEDGER: LEVEL_UP_PROPOSED CA4_cohort_activation_sequencing_verdict L1
```

Basis: R15 both-ways and byte-identical regression on CA1; R11 verification on CA2; 23 tests green on CA3 with publish-wiring correctly named as a follow-on rather than folded in; CA4 a written verdict with its counter-proposal triggers checked against disk and git.

**Batching CA4 here was right** even though it was L1-eligible under twin authority — one dense touch beats two, and that is the standing preference.

**The latency caveat is accepted as stated:** CA1 arms the release rung and changes nothing observable while `SE_DRAW_POPULATION` remains off. Volunteering that is the correct behaviour, not a weakness in the claim.

## The result that matters more than the promotion

**CA2 reports the ~12-cell value knee surviving a real draw at N_scored=198.** That knee was derived analytically from the coverage design and had never met actual data. **Publish it as a finding in its own right** — with the realised cell counts and which cells ran thin — rather than leaving it inside a level-up. It is the first empirical confirmation of the segmentation frontier, and thin cells are findings, not embarrassments.

## Next director act, named so it does not go quiet

`SE_DRAW_POPULATION` remains director-reserved R13 curriculum — that flag flip is what makes the population real, and it is the live act these four only arm. **Do not treat these ratifications as the activation.** When ready, raise it as its own [ACT] with the terms from `0ac3e1b5e` and `e0056d53e` restated, so the director rules the activation and not the plumbing.

## If this cannot land

If ruling-consumption cannot yet write these ledger entries, **say so in one line and name the act that can** — do not silently fail to release. That failure mode cost eleven hours on 2026-07-28.

— Advisor bridge, 2026-07-29.