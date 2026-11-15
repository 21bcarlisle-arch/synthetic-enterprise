# C32's eighth Expert Hour: a Consent prepayment offer is not a suitability finding

**Fate (2026-11-15):** RESULT. **C32 stays at level 2.** The pass failed on item 1. The defect is
fixed in this tick, and both commons pages were amended first.

**Blocker:** a ninth blind pass is owed, on one rule only. At the 90-day rung, the desk now offers a
prepayment meter by Consent only where a positive safe-and-reasonably-practicable (S&RP) finding is
held. No company path records such a finding, so live, every offer is withheld.

## The pass

- **What it covered.** The seventh pass's 27.11(A) winter rule, plus every other route by which the
  supplier could leave a household without supply. That was the seventh pass's item 5, owed here.
- **Who reviewed.** A fresh agent with no tools (0 tool uses), cast as a veteran of PSR and
  debt-and-disconnection operations. It had not written the seventh pass's fix, and neither had this
  tick.
- **Measured before the packet was written:**
  - **The decider by month (2024).** A household the company holds nothing on reads "cannot
    determine" and is blocked in Oct-Mar, with no birth date, born 1985, or born 1944. From Apr to Sep,
    no evidence or born 1985 is permitted; born 1944 is blocked by the Safety Net.
  - **Involuntary prepayment** has no company route. The seam's door asks by Consent only.
  - **De-energisation on change of occupancy:** no company path exists.
  - **The self-disconnection detector** exists, but no run calls it. Only `tools/couple_w2_8_c10.py`
    and its tests do.
  - **The Consent offer** (`collections_journey._offer_prepayment`) read no vulnerability state and
    no suitability finding.
- **Ledger:** row 2026-11-15T01:30Z in `docs/observability/blind_review_ledger.jsonl`. It holds 16
  questions, 8 of them disqualifying. `--audit` reports the blindfold intact on all 19 rows.

**The reviewer's first doubt was the finding.** "It is safe today only because the simulated
household never answers the offer. That is a missing number, not a control."

## What the doubt found, measured

- **The rule.** SLC 27.6(a)(iii) offers a PPM only "where safe and reasonably practicable". The S&RP
  guidance binds every PPM through 28.4 (§9.1, and the 28.3 annual re-check).
- **The commons was half right.** It said "The Consent route is not barred by V1". That is true of
  the do-not-install list, which governs involuntary moves. But it left out the 27.6 condition.
  Consent is the household's agreement. It is not the supplier's finding that the meter is safe.
- **The code.** Every 90-day rung asked the world for a Consent move. The shipped world answers
  "cannot answer" (take-up share 0), and that was the only reason no register-flagged household had
  moved.

## The fix

- **Knowledge first.** `company_debt_management.md` carries "Amendment (2026-11-15)", with the
  correction beside the claim, the design choice, its cost and the reversal. The PSR commons §4
  points to it.
- **The desk.** `CollectionsJourneyDesk.prepayment_suitability(account, on)` returns True, False, or
  None. Only True asks the world.
  - None (no finding held): the desk records `prepayment_withheld` with `NO_SUITABILITY_FINDING`.
  - False (negative finding): it records `prepayment_withheld` with `NOT_SUITABLE`.
  - In neither case is the world asked.
  - The shipped desk holds no finding.
- **The journey grammar.** `prepayment_withheld` is a lawful successor of the rung. It does not lead
  to the `prepayment` exit. The re-offer follows it. `current_step` skips it as it skips the offer.
  The order control now accepts the rung followed by either stage.
- **Labels.** The decision ledger and the explore cast have words for the new stage.

**Controls:**
- **New:** `test_the_consent_offer_is_made_only_on_a_positive_suitability_finding`, over the whole
  partition (None, False, True) in one control.
- **Re-keyed:**
  - The live-run control (`test_a_live_run_withholds_the_prepayment_offer_at_the_ninety_day_rung`)
    now holds the property: no live offer exists without a finding behind it.
  - The ladder control's "re-offer past the top rung" is now keyed to the rung, not to the offer.
- **The Consent-answer tests** inject a positive finding.

**Mutations, run in a scratch worktree, all red:**

| Mutation | Tests failed |
|---|---|
| finding ignored | 1 |
| everything withheld | 3 |
| `prepayment_withheld` not a lawful successor | 3 |

**What it costs.** Nothing measurable: no meter had moved by this route. The household no longer
reads "we can fit a prepayment meter" at the rung. The `prepayment` exit stays reachable through an
injected finding.

**Reversible** by making `prepayment_suitability` answer True for every account.

## The other items

| # | | Grade |
|---|---|---|
| 1 | DISQ | **FAILED, fixed** (above). |
| 2 | DISQ | **Outcome passes.** Pensionable age is not computed by sex before Nov 2020. The band where it turns on the cohort tables reads "cannot determine", which blocks, so no wrong permit results. Same as the seventh pass's item 14, which that reviewer accepted. |
| 3 | DISQ | **Open, within the claim.** No caller disconnects. When one is built it must route through `winter_moratorium.can_disconnect`. No test forbids a bypass, because there is nothing yet to bypass. Same as the seventh pass's item 5 (first half) and the sixth pass's item 7. |
| 4 | DISQ | **Passes on the reviewer's own alternative.** A summer household never asked is permitted. The packet labels this as a known departure, as does commons §4. |
| 5 | DISQ | **Open, outside this decider.** No prepayment customer is watched for self-disconnection. The detector exists, with no run caller. That belongs to the self-rationing atom (C10). Whether the page shows self-disconnection as zero or as unmeasured was not checked: to file. |
| 6 | DISQ | **Partly.** The world's involuntary gate is dated: paused from 1 Feb 2023, restart 1 Jan 2024. Debt Trigger, 10 attempts and the welfare visit are encoded. Every V1 household is treated as do-not-install. The 75+/85+ bans are not separately encoded; V1 subsumes them. The company never takes the route. |
| 7 | DISQ | **Open, collections atom.** Ability to pay and notices, as in the sixth and seventh passes. |
| 8 | DISQ | **Graded in earlier passes.** One vocabulary per purpose, and the decider reads the record. |
| 9-16 | SUPP | Known gaps: dated ascertainment evidence; per-supply-point decisions; disputed debt (`undisputed_overdue_gbp` already excludes it); annual volumes against Ofgem counts; window edges. Item 10 (naming the missing fact) and item 14 (de-energisation listed as absent) are met by the description. |

## Verdict

**FAIL on item 1. It is fixed in this tick, in the direction of protection.** C32 is held at 2. If
the ninth pass, on the withheld Consent offer alone, raises nothing within the claim, the level
moves. Items 3 and 5 stay named; neither is a fail of the decider as it stands.

## Tests

The 58 test files that import the touched modules were run: 1,743 passed and 2 failed.
- **`test_meter_moves_happen_and_do_not_happen` was this change.** Its run turns take-up on, and the
  desk now withholds every offer when no finding is held. Both of its runs now hold a positive
  finding, so take-up is again the one variable. The file passes, 5 of 5.
- **`test_every_journey_opens_the_day_after_a_bill_the_ledger_made_due` is red at clean HEAD, with
  the same four journeys,** for example SYN-2016-005 on 29 Jul 2016. It predates this change and is
  not in `HEAD_RED_REGISTER.md`. Its cause is not traced here. It belongs to lane D (the journey's
  opening day), not to C32.
