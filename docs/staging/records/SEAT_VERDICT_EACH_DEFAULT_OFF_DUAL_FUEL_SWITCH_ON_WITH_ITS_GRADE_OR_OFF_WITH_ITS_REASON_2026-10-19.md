# Verdict: each default-off dual-fuel switch, on with its grade or off with its reason

**Written 2026-10-19 ~16:30Z by the delivery seat.** Direction item
`each-default-off-dual-fuel-switch-goes-on-with-its-grade-or-stays-off-with-its-reason`, from the
director's 19 Oct 16:28 question "Is dual fuel sorted?" (relay:
`docs/staging/advisor/done/DIRECTOR_READING_USAGE_5PCT_MONDAY_PM_2026-10-19.md`).

Three switches are default-off. **None is "off because nobody got to it".** Each has its own reason.

| Switch | Built | Verdict | The grade or reason | What turns it on |
|---|---|---|---|---|
| `household_budget.BUDGET_DECIDES_PAYMENT` | `718a631a1` | **OFF** | Graded on the paired off/on run: R1 and R3 refuted high (`c43df1237`). The income-move exit then closed the spell (U1–U4 held, `a1235d427`), but the pre-crisis level is still +1.0 to +2.7 points of heads every year 2016–2021 over the off arm. | The latent finding `WORKER_FINDING_THE_BUDGET_SPENDS_THE_NORMATIVE_FLOOR_IN_FULL_BEFORE_ENERGY_SO_THE_PRE_CRISIS_HEADS_RUN_HIGH_2026-10-19.md` is answered (the budget spends what households actually spend, not JRF's normative floor in full), and a re-run shows the 2016–2021 heads within the off arm's band. |
| `DecisionPolicy.save_offer_decides_per_household` | `c002699e7` | **OFF** | **Unwired, so it has no grade and cannot have one.** `company.crm.save_offer.save_rates_for_decision` has no production caller on `origin/main` (checked by `git grep` at the time of writing). Switching it on today changes no byte of a run. | Two builds, in order (finding `WORKER_FINDING_THE_COMPANY_DECIDES_A_DUAL_HOUSEHOLD_PER_LEG_AND_C35_CHARGED_IT_TWO_RISES_FOR_ONE_BENEFIT_2026-10-18.md` §5): **1b** the run reads the switch and answers both notices; **1c** the world weighs the save on the combined bill (a world fidelity choice under the §8a GAP, decided blind to company results). Then the switch-on run pre-registered in §2 below. |
| `DecisionPolicy.dd_review_offsets_dual_fuel_legs` | `b529875b1` | **ON** (graded in §3) | N1–N5 (`f00fdb040`) graded how often the right arises, not what the switch does. The on-arm figures in fuel page §8b were read after the fact, with no prediction. | §1 pre-registers the on arm on the held `ad8afadc5` run and states the rule in advance. |

## 1. The offset: the on arm, pre-registered before it is read

**The run.** `docs/reports/run_output_ad8afadc5_20261019T132751Z.json`, the first completed run with
split campaign homes. The publisher holds it for the 26 Oct window, so this grade is on an
**unpublished** run, and it says so. The 8b6fea024 on-arm figures (8 offsets, £263.91, never-seeks)
have been read. These predictions are made with that in view, on a different book (about 4% fewer
dual households).

**The book.** `build_dd_balance_book(bills, opening, closed, seek_balance_at_review=…,
offsets_dual_fuel_legs=…, **forecast_inputs_from_run(run))`, with `closed_ids_from_bills(bills)`.
This is the same builder `tools/dual_leg_opposite_signs` uses. Four books: never-seeks and seeks,
each with offsets off and on. The standing policy is never-seeks (`REVIEW_SEEKS_BALANCE = False`).

**O1. Size, never-seeks.** The only action is a closed leg's final bill. Offsets: **4–14 (point 8)**,
totalling **£100–£500 (point £250)**.

**O2. The bar does not move on the standing policy.** On the never-seeks arm, the SLC 21BA bar at
each final bill is taken before the offset, and no earlier action exists that could settle old debt
first. So `barred_at_final_bills_gbp` and `barred_at_reviews_gbp` are **equal on and off, to the
penny**. If they differ, my reading of the code is wrong.

**O3. Nothing before the right.** No offset row is dated before 2021-01-22. On the never-seeks arm,
every trajectory point dated before 2021-01-22 is identical on and off.

**Seeks arm, as a result only.** The review bars fall, as on 8b6fea024 (£26,750 → £26,041).

**The rule, stated before reading.** If **O2 and O3 hold**, the offset on the standing policy moves
no money through the bar, and its offsets come only from debt the household owes and cannot have
barred. The household is then never worse off: each pound of its debt that is cleared takes a pound
of its own credit. The company is spared chasing a debt while it refunds a credit. **Then the
verdict is ON for the standing policy.** The seeks arm, which moves the bars, stays a separate
question for when `REVIEW_SEEKS_BALANCE` itself is decided.
If **O2 fails**, the verdict is OFF until the bar's interaction is explained.

*Why ON is not "erring for our thesis" (F11).* Over a whole run the money is about £250 and, per O2,
none of it comes through the bar. The GAP that stays open is how many suppliers net without being
asked. One large supplier's terms (EDF cl. 17.e) do; the licence (SLC 27.8D) makes it the customer's
right. The household is assumed to accept, and nothing published gives a share who decline (§8b).

## 2. The household save: the switch-on run, pre-registered before it exists

Nothing can be measured until 1b and 1c land. Pre-registered now, so the first on-run is read
against something written before it:

- **P0 (today).** On and off produce identical runs, because nothing reads the switch. This is
  checked by reachability (no production caller), not by a run.
- **P1 (after 1b, before 1c).** The world still weighs the save on electricity's rate alone, so dual
  retention does not move: the on arm's dual departures are within ±2 of the off arm's on one seed.
  The gas leg's term rate falls by the save on retained dual homes. That is a transfer to the
  household with no retention bought. **The switch stays OFF at this stage whatever the margin
  reads.**
- **P2 (after 1c).** With the household weighing the combined bill, more of the saves offered to
  dual leavers are taken on the on arm than on the off arm. The change is retention among dual
  leavers offered a save, on one seed with its own interval. The verdict is ON only if the
  retention gain is outside that interval **and** the household summed margin stays ≥ 0 on the
  retained homes (the floor the build already enforces).

## 3. Grade of §1

*To be written below this line from the four-book reading. Do not edit §1 above.*

**Graded 2026-10-19 ~16:40Z (seat), on the unpublished `ad8afadc5` run.** Run end 2025-06. The run
records no seek setting (`null`); the standing review never seeks. Four books from one builder,
4.7 s and 340 MB:

| | bars at reviews | bars at final bills | offsets | £ offset | households | step-ups |
|---|---|---|---|---|---|---|
| never seeks, off | £0.00 | £24,335.76 | 0 | — | — | 0 |
| **never seeks, on** | £0.00 | **£24,335.76** | **8** | **£263.65** | 8 | 0 |
| seeks, off | £26,277.55 | £2,477.44 | 0 | — | — | 1,136 |
| seeks, on | £25,593.99 | £2,370.61 | 73 | £2,448.71 | 63 | 1,091 |

- **O1 (4–14, point 8; £100–£500, point £250): HELD.** 8 offsets, £263.65, all at final bills.
  The largest is £110.86 and the median about £24. This is close to 8b6fea024's 8 and £263.91. The
  campaign split barely touches leavers who are dual and on DD on both legs.
- **O2 (bars equal to the penny): HELD.** Final-bill bars are £24,335.76 on both arms, and no
  household's bar differs. The reason is stronger than the one I gave: **no trajectory point
  differs at all** on the never-seeks arm. Every offset falls on a final bill where both legs close
  together, so the credit leg has no later bill for the offset to move.
- **O3 (nothing before the right): HELD.** The earliest offset is 2021-09-27, and no point before
  2021-01 differs.
- **Seeks arm (result).** Review bars fall £683.56 and final-bill bars £106.83. 45 step-ups are
  never made. This is the same shape as 8b6fea024 (£26,750 → £26,041).

**Verdict: ON for every standing policy.** The rule stated in §1 was met. The default is now
`True` in `company/policy/decision_policy.py`. The control is keyed to the property
(`test_every_standing_policy_offers_the_offset`): the default set back to `False` reds all seven
standing policies, which was run in a scratch worktree. On the standing review this changes only
what a dual leaver's two final bills say: the debt sought and the credit refunded each fall by the
same £263.65 over the whole run. The seeks arm moves bars, so it is a transfer question and
belongs to whoever decides `REVIEW_SEEKS_BALANCE`. The policy comment says so.

**What is still open on dual fuel after this record:** the household save (1b, 1c), the budget's
level, and the C35/C34 gas-leg probe (`the-decision-probe-writes-a-dual-households-gas-leg-at-its-electricity-roll`).
The practitioner question in fuel page §8b, whether suppliers net without being asked, is still
GAP. The verdict does not depend on it, because on the standing review the household is never worse
off.
