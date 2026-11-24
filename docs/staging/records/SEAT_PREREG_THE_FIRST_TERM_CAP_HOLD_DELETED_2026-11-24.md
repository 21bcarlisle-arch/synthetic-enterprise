**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome` · **Claim:** `the-fixed-first-term-leaves-the-cap-hold-pre-registered`

# Pre-registration: the acquisition rule that holds a fixed first term at the cap is deleted

*Worker, 2026-11-24, in an `origin/main` worktree at 37a2b72834. This record lands before any book
carries the change. The switch is `FIRST_TERM_CAP_HOLD_DELETED` in
`company/pricing/renewal_rate_chain.py`, and it is False in the same commit. Its control is
`tests/company/pricing/test_the_first_term_cap_hold_comes_off_by_one_switch.py`. Mutations: the
flag set True gives 2 red; a predicate that ignores the flag gives 1 red; the rule emptied without
the switch gives 2 red. Each mutation was restored byte-identically.*

## What the probe measured

`/var/tmp/se-caphold-probe/probe.py` and `probe2.py`, with outputs `probe_run1.out` and
`probe2.out`. Seed `run_base_seed()`. The predictions were filed first, in `PREDICTION.md` beside
them.

1. **The campaign** (`live_population._resolve_campaign`) was run twice, with the switch off and with
   it taken.
2. **Each won fixed, domestic electricity prospect** had its first term struck the way the run
   strikes it: `renewals.price_fixed_term`, which goes through `quote_renewal`. That term then went
   through `decide_renewal_rate` at `term_index` 0, both with and without the hold.
3. **What the probe leaves out.** The chain ran with an empty portfolio history, so it applies no
   portfolio premium. On the 6af7fd0bfd book that premium ranges from −5% to +15% (p05/p95, n = 892).

| year | quotes priced / declined | median quote vs cheapest fix (hold on = off) | wins | fixed domestic elec wins | clamped by the hold | median clamp, % of strike | contracted vs cheapest, hold on / off | first-year £ per win the hold removes |
|---|---|---|---|---|---|---|---|---|
| 2016 | 296 / 0 | +24.7% | 21 | 10 | 0 | – | +7.7% / +7.7% | 0 |
| 2017 | 311 / 0 | +14.9% | 27 | 16 | 0 | – | +0.6% / +0.6% | 0 |
| 2018 | 310 / 0 | +40.0% | 20 | 9 | 0 | – | +25.2% / +25.2% | 0 |
| 2019 | 290 / 30 | +15.2% | 26 | 17 | 0 | – | −0.6% / −0.6% | 0 |
| 2020 | 312 / 5 | +15.9% | 21 | 16 | 0 | – | −4.9% / −4.9% | 0 |
| 2021 | 163 / 141 | +20.4% | 23 | 14 | **10** | 20.5% | +0.0% / **+31.6%** | 65.6 |
| 2022 | 10 / 77 | −4.4% | 6 | 1 | 1 | 7.0% | +0.0% / +7.5% | 5.7 |
| 2023 | 117 / 31 | −4.5% | 30 | 15 | 0 | – | −31.3% / −31.3% | 0 |
| 2024 | 254 / 0 | −5.1% | 48 | 39 | 0 | – | −18.0% / −18.0% | 0 |
| 2025 | 97 / 0 | −5.5% | 20 | 14 | 4 | 4.4% | +1.6% / +1.6% | 5.5 |
| **all** | **3,089 quotes** | | **242** | **151** | **15** | | | **6.8 (£1,652 in all)** |

**The campaign does not read the hold.** With the switch off and taken, all 3,373 offers asked,
all 3,089 quotes issued (02eacf24b's pin) and all 242 winners, ids and dates included, are
identical. `quote_first_term` gates on `should_attempt_acquisition` against the default, and
neither of them calls `held_at_published_cap`.

## What this changes about the direction

The direction said that while the hold remains, the campaign's wins are priced by a rule the
flat-rules twin shares. **That is no longer true, and it has not been true since 22 Nov.** Wins are
decided on the quote, and the quote never reads the hold. Deleting the hold moves no win.

The hold does bind, but on a different thing. A won first term is **contracted on a different
strike from the one it was quoted on**:

- **Quoted on** the ladder, plus the operating-cost line, gated at the default.
- **Contracted on** `quote_renewal`, which is spot-led at the notice date, with no ladder and no
  operating-cost line.

In 2021 Q3–Q4 the contracted strike reached ×1.54 the cap. The hold is the only thing that brings
those 10 terms back down to the price the household was shown. The gap also runs the other way: in
2023–24 the contracted first term sits 18–31% under the cheapest fix while the quote sat 4.5–5.1%
under it. That is margin given away by a strike nobody quoted (M2: transfer, not creation).

**Deleting the hold before the first term is contracted at its quoted strike would contract 10 of
14 households won in 2021 above the default their quote was gated under, at up to ×1.54 of it.
The hold takes off a median 20.5% of the contracted strike, and up to 35%.** No
supplier can bill above the price it quoted. The switch therefore stays off on a stronger ground
than the direction gave, and the order gains a step before it: **one strike for the quote and the
contract** (`SEAT_FINDING_A_WON_FIRST_TERM_IS_CONTRACTED_ON_A_STRIKE_IT_WAS_NOT_QUOTED_2026-11-24.md`).

## Predictions, scored against the first book whose producing commit has the flip as an ancestor

The predictions assume the flip lands **without** the one-strike change, since that is the only
change this switch makes. If the one-strike change lands first, P2 and P3 below are void and must be
rewritten against the new strike before the flip.

- **P1. Wins (exact).** Campaign wins, quote count and the per-year rows equal those of the same
  commit with the switch off. At this commit: 242 wins and 3,089 quotes. Any difference refutes "the
  campaign does not read the hold".
- **P2. Legs the hold touches.** Won fixed domestic electricity first terms whose contracted rate
  rises: 15 at this seed, range 10–30. The +15% portfolio premium can only add legs near the cap,
  and the −5% one can only remove them. 2016–20 stay at 0, because there is no cap before 2019 and
  2019–20 strikes sit under it. 2021 carries most of them.
- **P3. First-year margin per win.** It rises by £6.8 at this seed, range £3–£20, averaged over all
  wins. It is concentrated in 2021 at about £150 per clamped win. A first term whose rate rises
  above the quote is also a household paying more than it agreed to, so whatever margin P3 shows is
  **transfer, not value**. It is graded as a defect if it is ever observed on a book.
- **P4. MSC legs.** Won switches between 2022-04-14 and 2024-03-31 equal the switch-off count: 44 at
  this seed. The hold moves no win, so it moves no gainer leg. It does move 1 contracted rate inside
  the window, PROS-2022-0137 on 2022-04-24.

**Off-rule.** The switch is not flipped while a won first term is contracted on a strike other than
the one quoted. If P1 is refuted, the flip is reverted and the campaign's read of the hold is traced
first.

## GAPs

- **The portfolio premium on a first term** is left out of the probe; P2 and P3 carry its range.
- **The campaign quotes electricity only** (§7). Gas first terms are unmeasured.
- **The half-hourly SSP cache ends 2025-06-07.** 2025 wins after that date are not in this
  measurement.
