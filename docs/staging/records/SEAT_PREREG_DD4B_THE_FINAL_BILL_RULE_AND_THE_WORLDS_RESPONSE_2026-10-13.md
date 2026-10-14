**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**What:** does the final-bill DD rule move the world's DD4b response? Pre-registered before the runs · claim `dd4b-final-bill-rule-reaches-the-arms-tool-and-the-world-response`
**Status:** PRE-REGISTERED 2026-10-13, before launch. GRADED at low and high: R2-R5 hold; R1 holds in shape, but its counts came from another base.

# The final-bill rule and the world's DD4b response

## The question

The final-bill rule (`dbee6809d`, re-applied to trunk under this claim) changes which reviews the
household is told in the loop (`simulation/dd_review_in_loop.py`). It stops telling 9 leavers whose final
bill falls on a month-end, and starts telling 8 continuing accounts at the run's last settled day
(`2025-06-07`). Does that move anything the world does in response?

## Derived before the runs, from the saved pre-rule runs (not a measurement of the new code)

From `/var/tmp/dd4b_runs/il/f200-low-ownbills/` (the told stream is byte-identical at low and high):

- The 9 removed told reviews include **one** material rise (over 15%): `SYN-2016-201`, +110.1% at
  `2021-09-30`. Its bills are all `standard_credit`. DD4b answers only a direct-debit household, so
  this rise was never answered.
- The 8 added run-end reviews include **no** material rise. The largest is +5.4%.

So no review that DD4b answers enters or leaves the told stream.

## Predictions, 200 founders, budget 0, base seed

There are four runs, `il_run.py {low,high} 200 0`. Each setting runs once with the rule OFF (a worktree at
origin `de3a33eb3`) and once with it ON (the same base plus `dbee6809d`'s diff). Nothing else differs
between OFF and ON.

| # | Quantity, ON vs OFF at the same setting | Prediction |
|---|---|---|
| R1 | told in the loop | ON 800 = OFF 801 - 9 + 8; reconcile ON: matched 800, only_in_loop 0, only_post_loop 0 |
| R2 | material told rises | ON = OFF - 1 |
| R3 | DD4b responses (`world.json` `responses`) | identical lists |
| R4 | mandates cancelled, complaints, DD failed collections | identical |
| R5 | total net and bad debt (`summary.json`) | identical to the penny |

**The rival.** The told amount could reach the world through some path other than DD4b's answer, such as
the collected DD amount or an RNG draw keyed on the told stream. If so, R4 and R5 would move by small
amounts concentrated on the 17 affected households. R3 would then still hold. If R3 fails, my
derivation of which reviews DD4b answers is wrong.

## Grade — low (OFF finished 18:23, ON 22:48; `/var/tmp/dd4b_runs/il/grade_frule.py`)

| # | Prediction | Result at low | Verdict |
|---|---|---|---|
| R1 | ON 800 = OFF 801 - 9 + 8; ON reconciles 800/0/0 | OFF **788**, ON **786** = 788 - 9 + **7**; ON reconciles 786/0/0 (material 286 = 286, max rise gap 0.0) | **Shape holds, counts wrong** |
| R2 | material told rises ON = OFF - 1 | OFF 273, ON 272 (-1); the one removed is `SYN-2016-201` at 2021-09-30, +124.1% | holds |
| R3 | DD4b responses identical | identical, 198 = 198; every response identical | holds |
| R4 | cancelled, complaints, DD failed identical | 5 = 5, 5 = 5, 162 = 162; the `dd_books` block is identical | holds |
| R5 | net and bad debt identical to the penny | £159,383.74 = £159,383.74; £1,515.34 = £1,515.34 | holds |

**R1's miss, stated plainly.** I took the counts 801, 9 and 8 from `f200-low-ownbills`, a run on a different
base. At `de3a33eb3`, OFF tells 788. The rule removes 9 month-end leavers' final-bill reviews, as predicted.
It adds **7** run-end reviews, not 8, and all 7 fall at `2025-06-07`: `OCC-1c8219f382dd`, `OCC-65ba18e30c91`,
`OCC-9300f4b99ba7`, `SYN-2016-131`, `SYN-2016-137`, `SYN-2016-140` and `SYN-2016-143`. None is a material rise;
the largest is +5.7%. The derivation held on every point except the population size, and the derived
population came from another base. The two runs review almost the same customers: 197 of the earlier
run's 200 are reviewed here too. But at `de3a33eb3` a different set of accounts has a review falling due
inside the last stub. The earlier run also reviewed 6 of these 7 accounts, though not at the run end, so the run-end set
depends on the base's review dates, not only on the book. I have not traced which change since that base
moved those dates.

## Grade — high (OFF finished 22:48, ON 23:48)

| # | Result at high | Verdict |
|---|---|---|
| R1 | OFF 789, ON 787 = 789 - 9 + 7. The same 9 removed and the same 7 added at `2025-06-07` as at low. ON reconciles 787/0/0, material 286 = 286 | shape holds, counts wrong (as at low) |
| R2 | material told rises 273 -> 272 (-1, `SYN-2016-201`) | holds |
| R3 | DD4b responses identical, 198 = 198 | holds |
| R4 | cancelled 30 = 30, complaints 37 = 37, DD failed 224 = 224, `dd_books` identical | holds |
| R5 | net £159,203.94 = £159,203.94, bad debt £1,838.63 = £1,838.63 | holds |

## What it says

**The world's DD4b answer did not move.** At both settings, the rule changes which reviews the household
is told and nothing the world does in response. The one material rise it removes was told to a
`standard_credit` payer, so DD4b never answered it, and none of the 7 run-end reviews it adds is a
material rise. The rival (a non-DD4b path from the told amount into the world) is refuted at this
resolution: R4 and R5 are identical to the penny, not moved by small amounts.

The rule is a billing-accuracy correction that the world cannot price, because no response in this
world reads a non-material review or a final bill. The 9 month-end leavers are no longer told a new monthly
amount at their final bill. The run-end households now told a review number 7 at this base, not the
8 the note counted on an earlier one.
