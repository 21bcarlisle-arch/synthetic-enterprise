# Pre-registration: the price match against risk tiers, from 2019, where a published default exists

*Written 2026-10-14, before any arm runs. Item `price-match-pre-cap-published-default`, handed off by
c65f5b205. The predictions below are not edited after the result; the result goes beneath them.*

## Why this is the comparison and not the one the item offered first

The item asked first whether a real supplier could read a published default-tariff level before the cap,
per fuel and ex VAT. It could read one: Ofgem published the large-legacy-supplier average SVT every month,
2012-2018. But that was a **dual-fuel annual bill** (inc VAT, direct debit, typical consumption). It was
never published per fuel or as a unit rate. The research is in
`docs/market_research/svt_rates_active_passive_2016_2025.md` §1a. The match compares a per-fuel ex-VAT unit
rate, so before 2019 it has no input it can read. Splitting the dual-fuel bill into two unit rates would
need a fuel split and a standing-charge split, and neither was published. That would be a picked number,
so `published_default_rate_ex_vat` stays `None` before 2019, and the reason is now stated beside it.

So the item's second branch applies: re-grade restricted to 2019 onwards. Restricting the WINDOW would not
do it. The two arms would still enter 2019 with different books, because the tiers made offers in
2016-2018 that the mute match did not. The comparison here makes the arms identical before 2019 by
construction:

- **`risk_tiers`**: production, unchanged.
- **`match_where_published`**: runs under risk_tiers, and on every renewal where the company reads a
  published default (from 2019, the cap), it sizes the cut by the price match instead. It is the policy a
  supplier could actually run: match where a default is published, tier where none is.

The difference between the two is the match's effect from 2019 alone. Script: `/var/tmp/regrade4/cut_arm.py`
under `/var/tmp/regrade/seeded_arm.py`, HEAD 58e1e8905, worktree /var/tmp/se-rc4. Book seeds 61109-61112,
400 founders, budget 0, to 2025-06-07: the same design as 5074f1d40's re-grade, re-run at this head
because `simulation/` has moved since 5e5358092.

## Controls (must hold, or the comparison is void)

- **C1:** the two arms are identical before 2019 on every seed: `offers_pre2019`, `cost_pre2019_gbp` and
  `renewal_departures_pre2019` are equal.
- **C2:** on every seed, both legs of the swap are taken: `swaps["matched"] > 0` and
  `swaps["tiered_no_default"] > 0`. A swap that never fires, or always fires, grades nothing.

## Predictions

- **P1:** from 2019, the hybrid makes fewer offers than the tiers on at least 3 of 4 seeds.
- **P2:** |hybrid net - tiers net| < GBP 2,000 on every seed. Basis: on 61109 the inc-VAT match was
  -108 against the tiers (5074f1d40), and 57 of its 67 offers fell before 2019.
- **P3:** the sign of hybrid - tiers is mixed across the four seeds, not 4 of 4 the same way.

## Decision rule, fixed now

"Spread" here means the PAIRED difference on the same seed. The result record of 2026-10-14 asked for
that to be defined before the rule was used again.

- If the hybrid nets more than the tiers on **4 of 4** seeds (one-sided sign test p = 1/16), AND the
  pounds of renewal cut customers receive from 2019 are not lower on 3 or more seeds: propose
  `match_where_published` as the retention cut (to the director, since it changes a policy he can see).
- If the hybrid nets less on 4 of 4: matching the market does not create value at the retention lever
  in this world from 2019 either. Record that as the M2 answer.
- Anything else: no evidence either way. Stay on `risk_tiers` (F11).

## Result, 2026-10-14 10:00 BST: not run

The eight arms above were never launched. /var/tmp/regrade4/queue.sh is ready and its grader is
/var/tmp/regrade4/grade4.py, so no prediction here is graded. A different pair, tiers muted before
2019 against the match, ran on 61109 only. Its paired difference from 2019 was GBP 0.00. It is
recorded beside the decision in
docs/staging/done/SEAT_RESULT_THE_RENEWAL_CUT_STAYS_ON_RISK_TIERS_THE_MATCH_LOSES_NET_ON_EVERY_SEED_AND_GIVES_CUSTOMERS_LESS_2026-10-14.md.
Run this design only once writer one's floor basis lands, since both arms read the floor d30dafffe found
double-counted.

## Addendum 2026-10-14: re-taken on writer one's basis

*Written 2026-10-14 09:50 BST. No regrade5 arm has run yet and none produced an artefact. Nothing
above this heading is edited.*

**What changed in the base.** The eight arms run from an origin worktree carrying e3b5ed01a, not
58e1e8905. That commit changes two things both arms read:

- **Writer 1's premium.** It now reads the unit-rate margin against the margin its own strike priced
  for. Before, it counted the standing charge as margin against an 8% literal, and took the full -5%
  off 21 of 21 held electricity renewals.
- **The floor.** The cut and the save share one floor, `renewal_offer.term_cost_floor`, which now
  includes capital. Row 433's floor moves from 194.15 to 196.63.

The regrade4 queue (/var/tmp/regrade4) was stopped before any arm produced an artefact. Its reason is
in /var/tmp/regrade4/queue.log.

**Same design.** C1, C2, P1-P3 and the decision rule above stand unedited. Same seeds 61109-61112,
400 founders, budget 0, report end 2025-06-07. Arm script /var/tmp/regrade5/cut_arm5.py is
regrade4's cut_arm.py with the save's counts added and nothing else changed. Grader:
/var/tmp/regrade5/grade5.py. The arms are armed by `longjob-regrade5-arm-behind-focus-one`. That unit
starts them only once e3b5ed01a and this addendum are both on origin/main.

**Folded in, so one set of arms answers all three:**

- **d5ba38b12's renewal-cut re-take.** d5ba38b12 kept the cut on risk tiers because the match lost
  net on every seed. That comparison read the old floor and the old -5%. The match_where_published
  against risk_tiers pair above, on the new base, is that re-take in the only form a supplier could
  run.
- **The save.** It has been live by curriculum since 2026-10-10, so both arms run it. Each artefact
  records `save_offers_made`, `saves_taken` and `save_offers_by_year`.
  - **S1:** on the risk_tiers arm, the save makes at least 1 offer on at least 3 of 4 seeds. The
    basis is the finding that the save never fired because renewals sat on or below their own floor.
    With the blanket -5% gone they should sit above it.
  - **S1 failing** means the floor account of the inert save is incomplete.
  - **Not answered here:** whether the save creates value. That needs a save-off arm per seed, and
    it waits on S1. A save that never fires has no value to measure.

**Duplicate-work note.** The claim `writer-one-margin-basis-and-one-floor-for-the-save` is focus one
itself: the fix and its seed-61109 grade. This item, `the-renewal-cut-and-save-are-re-taken-on-writer-ones-basis`,
is the four-seed re-take that runs on top of it. They are different work, and neither is released
for the other.
