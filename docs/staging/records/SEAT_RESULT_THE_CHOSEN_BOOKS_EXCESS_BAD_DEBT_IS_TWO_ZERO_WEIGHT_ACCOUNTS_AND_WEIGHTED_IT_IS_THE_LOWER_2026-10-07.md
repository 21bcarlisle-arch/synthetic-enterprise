**Severity:** MATERIAL · **Lane:** delivery (lane 0) · **Direction item:** `chosen-book-bad-debt-read-against-what-the-company-could-see` · **Claim:** released on landing

# The chosen book's excess bad debt is two zero-weight accounts, and weighted it is the lower

**Verdict.** Neither of the two answers the item offered. B's excess bad debt sits in two accounts
that **B's own sampler weights at 0.0**. They were settled to cover the support of the fabric
space and stand for no commercial wins. The published totals sum the settled book **unweighted**,
so those two accounts count in full. Weighted by the sampler's own weights, B's bad debt per
commercial win is **£47.1 against C's £54.7**: B is the *lower*. The excess is a property of how the
figures are summed. It is not an inference gap and not an honest loss of a per-customer view.

> **Re-graded 2026-10-09 on the corrected world (23fca0567, 54dbd5650): the headline no longer holds, and the comparison it rested on no longer exists in the same shape.** Same recipe (`arm_baddebt.py chosen|cull57`, `SIM_FAST_MODE=1`, the `arm_rerun.py` patches, run's own campaign memo seed `20260724`), at origin `46951a0ee`; `analyse.py` (minus its `per_cid_pnl` block, which reads the old arm files) and `weighted.py`. Wall time 25-50 min an arm on a contended box. Total bad debt B £14,267 -> **£3,397**, C £6,988 -> **£722**. B now settles **204** accounts, not 52 (the settlement budget rose since, `358d59a42`), so B against C (57) compares a 204-account sample with a 57-account one, and the move cannot be attributed to the arrears correction alone. PROS-2016-0098 is still settled at weight 0.0 and now carries **£0** bad debt; PROS-2020-0002 is not settled. B's bad debt is spread (largest account £698, PROS-2020-0013). **Weighted, B's bad debt per win is £18.0 against C's £3.0, so B is now the higher, not the lower**; both are small beside net per win (B £826.6, C £831.9), and the weighted net gap is -£5.3/win, not -£174. Conclusion changed: the "two zero-weight accounts" explanation and the "weighted it is the lower" sign are both gone; the gross-margin-per-win deficit (§4) has all but vanished at this book size.

The selection was never the company's. ARM B's "chosen book" is `simulation/settlement_choice.py`,
the world-side sampler that picks which of the company's ~500 wins this machine settles in full.
Its acquisition decisions are near-identical in every arm: 2,721–2,730 attempts, 499–501 wins,
£60.4–60.5k spend. The spread is small, and I did not establish its cause. So "what the company could see at the moment of selection" is a question about a
decision the company did not make. I answer it anyway (§3), because the item asked for it.
**Correction beside the item's WHY:** this comparison does not test "the company beats flat rules".
It tests whether a fabric-aware *sample* of one company's book reads differently from a blind one.

Fast mode, one seed, one world. Pounds are diagnostics, not publishable figures.

## 1. B's deductions from gross against A: all £16,244 accounted for, remainder £0

Measured, not fitted: `total_net_gbp` is gross − capital − bad debt − electricity policy −
electricity network − gas policy − gas network. Acquisition spend and fixed cost sit outside it.
The identity closes to the penny in all four arms.

| line | A cull (62) | B chosen | B − A |
|---|---:|---:|---:|
| gross margin | 362,430 | 370,874 | +8,444 |
| bad debt | 8,484 | 14,267 | **+5,783** |
| electricity network | 115,516 | 122,254 | **+6,737** |
| electricity policy (RO +3,109, FiT +832, CM +172, CfD +25, mutualisation −83) | 85,865 | 89,919 | **+4,055** |
| capital | 6,781 | 6,633 | −149 |
| gas network | 29,772 | 29,600 | −172 |
| gas policy | 111 | 101 | −10 |
| **deductions from gross** | 246,530 | 262,774 | **+16,244** |
| net margin | 115,900 | 108,100 | −7,800 |

The non-bad-debt £10.8k is electricity pass-through on volume: B billed 2,313,984 kWh of
electricity against A's 2,142,930. Its recovery sits *inside* revenue and therefore inside gross,
and its cost sits below gross. So B's higher gross is mostly pass-through recovery. After
pass-through, B is £2.2k *below* A before bad debt is counted. Gross margin, as published, flatters
a high-volume book.

Against C (cull57) the same identity gives B − C deductions of +£23,361: bad debt +7,280,
electricity network +10,677, electricity policy +7,486, gas network −1,954, gas policy −37,
capital −91.

## 2. Where the bad debt is (exact, from an instrumented re-run)

Both arms were re-run on the identical harness (`arm_rerun.py` patches, `SIM_FAST_MODE=1`, the
`fc47cd363` archive). Each re-run dumped every record's `bad_debt_gbp` by account and month, plus
the run's own campaign memo. Both reproduced the filed totals exactly: B £14,267.49 / net
£108,100.21, C £6,987.70 / £123,248.88.

- B − C bad debt **+£7,280** = B-only accounts **£10,313** − C-only accounts **£3,037**. The 79
  founder accounts carry £3,871 / £3,868, a £3 difference, and the 8 shared acquired accounts
  carry £83 in both arms.
- **Two B-only accounts carry £8,654, which is 119% of the excess:**

| account | bad debt | written off | sampler weight | signup record (company) | company's payment score before write-off |
|---|---:|---|---:|---|---|
| PROS-2016-0098 (elec) | £5,337 (£5,076 at departure) | 2021-09 | **0.0** | DD, band MEDIUM, South West; registry 30,684 kWh/yr; opening DD £321.52/mo | POOR from its first scored decision (2018-03); **CRITICAL from 2019-03**, 30 months before the write-off; on-time 22%, DD-failed 27%; renewed 2020-03 and 2021-03 |
| PROS-2020-0002 (dual) | £3,317 (gas leg £2,866 at departure) | 2024-12 | **0.0** | DD, band HIGH, East Midlands; gas registry 13,239 kWh/yr; opening DD £54.39 + £38.77/mo | electricity leg FAIR/GOOD throughout, **gas leg CRITICAL** (on-time 32%, DD-failed 17%); every DD review a large increase |

The other six zero-weight B accounts carry £524 between them. The remaining B-only bad debt is
spread across 42 accounts at £0–£476 each. The full per-account dump, B and C, is in
`~/.cache/seat_lane0_20261007_baddebt/records_{chosen,cull57}.json` (`rows`, `campaigns`).

## 3. What the company could see at the moment of selection, and after

Observables only: the prospect record at signup, the registry kWh, the DD book, and the company
CRM's payment score. The score is `cx_desk.behavioural_record`, built from observed ON_TIME / LATE
/ DD_FAILED outcomes (`company/crm/payment_behaviour_analytics.py`). The world's `income_stress`
is not used.

- **At signup, nothing separated them.** Signup payment method: B 38 DD / 14 other, C 43 DD / 14
  other. Mean signup EAC of B-only accounts was 2,709 kWh against 2,710 for C-only. Both big
  write-offs were DD at signup, which is the *lower*-risk signal. **On the narrow question the
  item asked, the risk was not observable at selection.**
- **After signup, it was.** PROS-2016-0098 sat at CRITICAL in the company's own record for 30
  months and was renewed twice. For PROS-2020-0002, the company's departure-side decisions read
  the electricity leg's score (FAIR), while the gas leg, which carried the debt, was CRITICAL.
  That is an observable the company held and, on this record, did not act on. Whether any
  collections step ran on either account is **not established here**: I did not read the arrears
  engine's action log.

## 4. Weighted, the net sign survives but its cause changes

The settled acquired accounts, weighted by the run's own `settlement_weights`. B's weights run from
0.0 (8 accounts) to 49.67; C's are uniform at 8.72. Both sum to 497 wins.

| per commercial win | B | C | B − C |
|---|---:|---:|---:|
| revenue | 4,866.8 | 5,276.0 | −409.1 |
| gross margin | 2,562.0 | 2,792.1 | **−230.1** |
| electricity policy | 502.1 | 525.9 | −23.8 |
| electricity network | 658.5 | 688.9 | −30.4 |
| capital | 61.0 | 63.8 | −2.8 |
| bad debt | **47.1** | **54.7** | **−7.6** |
| net margin | 899.2 | 1,073.3 | **−174.1** |

Weighted, B is still below C on net, by 16% per win. **The whole of that is gross margin per
win**, which is lower revenue per weighted win. Bad debt and pass-through both favour B. **I cannot
yet say why** B's weighted revenue per win is lower. The candidates are tenure, the weight fit's
own error, and volume mix. That is the unexplained part of the deficit, and it is a different
question from the one drawn.

## 5. A defect the re-run surfaced: ARM C is not count-matched to B

The run's own campaign (memo key seed `20260724`) settles **52** accounts in B and **57** in C.
The "57" that `cull57` was matched to is `_p6_campaign.settled_wins`. `arm_rerun.py` computes it
from a *separate* seed-42 cross-check campaign (`lp._campaign(lp._pre_growth_book(42), 42)`),
whose winners are different accounts. So the filed artefact's claim that ARM C is
"count-matched to B (57)" is false for the run. `cull52` is the count-matched arm. The artefact's
`re_run_2026-10-06.verdict_2026-10-07` records this beside the claim. The B-only/C-only lists above
compare 52 against 57 accounts, and 5 of C's extra accounts are part of why C has 644 more settled
acquired account-months (4,570 against 3,926).

## Predictions, graded

Written at 2026-10-06T23:31:53Z, before any per-account or per-line data was read
(`~/.cache/seat_lane0_20261007_baddebt/prediction.txt`):

- **P1 held.** The largest non-bad-debt component is volume-scaling electricity pass-through
  (network £6.7k + policy £4.1k), not acquisition spend. Remainder £0 < £1k.
- **P2 half held.** Concentration held: 84% of B-only bad debt sits in 2 accounts. The count
  prediction was wrong: there are 44 B-only billing accounts, not fewer than 20.
- **P3 held in letter and missed the point.** The risk was not observable at signup. But the
  selection is not the company's, the company *did* see the risk afterwards, and under the
  sampler's weights the excess disappears. My prediction framed the question the same wrong way
  the item did.

## What this changes, and the next step

1. Any blind-envelope comparison of B against the blind arms on **unweighted** totals compares a
   sample chosen for *difference* with self-weighting samples. That ordering is not evidence
   about the company. The envelope should compare **weighted per-win** figures. This is the next
   item, ahead of any further reading of the B-below-blind sign.
2. The CRITICAL-and-renewed pattern (§3) is a real company-side question: a payment score the
   company computes reaches no collections or retention decision on this record, and a dual-fuel
   account's departure decisions read only one leg's score. It needs its own item, after checking
   the arrears engine's action log.
3. Re-run ARM C as `cull52`, or have `arm_rerun.py` read the count from the run's own campaign memo.

Recipe: `~/.cache/seat_lane0_20261007_baddebt/` — `arm_baddebt.py <arm> <out>` (≈19 min, ~5 GB
each, two in parallel), then `analyse.py` and `weighted.py`.
