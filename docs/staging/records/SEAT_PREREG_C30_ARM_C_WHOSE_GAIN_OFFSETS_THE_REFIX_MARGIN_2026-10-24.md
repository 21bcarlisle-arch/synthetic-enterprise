# Pre-registration: C30 arm C, whose gain offsets the re-fix margin

*Delivery seat (executor), 2026-10-24. Claim `c30-whose-gain-offsets-the-refix-margin`. Written
before either arm below was launched. Follows the graded pair in
`SEAT_PREREG_C30_THE_ONCE_PER_STINT_SVT_LETTER_GRADED_ON_BOTH_SIDES_2026-10-23.md` (Result).*

## Question

The pair gave H = +£1,749 to re-fixed households and ΔC = B − A = −£389 to the company. On transfer
arithmetic alone the company should be near −H. So £1,360 is offset somewhere. Is the offset in the
re-fix itself (B − C), or in the letter's departures (C − A)?

## Arms (one variable each)

All arms run at **0481ad381**, the commit the A/B pair ran on, in a detached worktree. Origin has
moved since then (4ef70aba9 puts the EPG on the household bill, 1e358809be bills a default-tariff
term at one rate), and both change the books. Arm C at HEAD would therefore not be comparable with
A/B. Full window, seeds as standing, `/var/tmp/c30-arms-out/arm2.py` (arm.py with the re-fix switch
as an argument).

- **C:** B's policy (`cmoc_letter`, `svt_contact_once_per_stint=True`) with
  `A_WOKEN_SVT_STAYER_REFIXES` **off**.
- **A′:** A replayed (no letter, re-fix on). This is the comparability control and it is not
  optional. If A′ ≠ A, the old pair is not reproducible at 0481ad381 and nothing below is graded.

## What is measured

- B − C and C − A on `total_net` (£, whole book; these add exactly to the pair's −£389).
- C's sends, re-fixes, SVT departures by cause, against B.
- Per-customer exit dates in `svt_departures` across A, B and C. These show whether the letter's
  `price_position` exits are customers who leave in A anyway (moved earlier), and whether a re-fix
  keeps a customer who leaves in C.

## Predictions

1. **A′ reproduces A exactly** (`total_net` £556,707.93 to the penny, same 257 departures).
2. **C:** 0 re-fixes. Sends 780–825 (B: 803). SVT departures 254–262, of which `price_position`
   7–12 (B: 9).
3. **B − C ≤ −£875.** The re-fix costs the company at least half the household gain H, so most of
   the £1,360 offset sits in C − A, which comes out at **≥ +£486**. My reason: the letter's exits move
   leavers earlier. Where they happen in years when the default ran below cost, an earlier exit is a
   saving to the company, not a loss. I do not favour the other reading, that the re-fix pays for
   itself through retention, because B and A have equal departures (257). Refutation: B − C > −£875.
   That would mean the re-fix returns margin through something the transfer arithmetic leaves out,
   such as retention past the fix end or hedging. If so, the per-customer exit table is the next
   read.
4. If |C − A| < £200 and B − C ≈ −£389, the letter's departures cost nothing and the whole puzzle is
   in the re-fix. That outcome refutes 3.

Grading reads the letter as "not shown to destroy value" unless B − C and C − A are each explained
by named rows. A single total-net difference with no named rows is not attributed (F11).

## Result (2026-10-24, same claim; predictions above unedited)

C and A′ ran in parallel at 0481ad381, full window, ~55 min each (`/var/tmp/c30-arms-out/C.json`,
`A2.json`; per-customer exit table `exits.py`).

| | A (no letter) | C (letter, no re-fix) | B (letter + re-fix) |
|---|---|---|---|
| letters sent | 0 | 786 | 803 |
| re-fixes | 0 | 0 | 20 |
| SVT departures | 257 (all `svt_inertia`) | 262 (253 + 9 `price_position`) | 257 (248 + 9) |
| `total_net` | £556,707.93 | £548,455.68 | £556,319.35 |

**B − C = +£7,864. C − A = −£8,252.** Sum −£389, as the pair gave.

1. **A′ reproduces A: held.** It matches to the penny, with the same 257 departures, so 0481ad381
   is the pair's code.
2. **C's counts: held.** 786 sends, 0 re-fixes, 262 departures, 9 `price_position`.
3. **B − C ≤ −£875: REFUTED, and by a wide margin.** The re-fix is worth +£7,864 to the company,
   not a cost.
4. **Refuted as well**, since 3 was.

**Both differences are explained by named customers, at one value per customer-year.**

- **C − A, the letter alone, is 9 `price_position` exits.** Three move a leaver earlier
  (OCC-dfb3e7d88e36 2019→2016, PROS-2016-0024 2021→2017, SYN-2016-283 by 10 days). Six are
  customers who never leave in A. One A leaver (OCC-8da6d995632c) leaves 0.18 years later on C's
  path. Net: **30.85 customer-years lost, £268 each.**
- **B − C, the re-fix alone, is exactly 5 customers:** PROS-2019-0027, SYN-2016-137, -260, -477 and
  -517. Each leaves through `svt_inertia` in both A and C, on or just after the segment where B
  re-fixes them, and none of them leaves in B. Net: **34.91 customer-years kept.** Before the £1,749
  given to the re-fixed households, that is £9,613, or **£275 each.**
- £268 and £275 come from disjoint customers and disjoint arm pairs, and they agree within 3%. So
  the knock-ons through hedging and pricing that the pair could not rule out are small beside the
  customer count. **The £1,360 that the pair could not place is retention.** The re-fix keeps 5
  households that would have left without any letter.

**Why prediction 3 was wrong.** I read "257 departures in both A and B" as "no retention". It was a
coincidence of composition. The letter adds 6 new exits and moves 3 earlier. The re-fix removes 5,
and one A exit drifts off on B's path. 6 − 5 − 1 = 0.

**What it means on M2.**
- **The letter without the re-fix costs the company £8,252** and records no household gain. The 9
  leavers' saving at a rival is a world GAP, so that gain is not zero but unmeasured. As built, the
  letter alone pushes 9 customers out to rivals.
- **With the re-fix, the company side is a difference of two transfers of about £8–10k each.** One
  is customers lost to rivals and the other is customers kept from them. Moving a customer between
  suppliers is market share, not creation (M2). That leaves the company at −£389, which is the sum
  of 9 exits and 5 retentions at 0.03–8.4 customer-years each. A swing of one customer is
  £0–£2,300. So **the sign of ΔC is not established on one path.**
- **The household side splits.** £1,420 of H goes to 15 re-fixed households that stay with us in
  every arm, and the default is their right counterfactual. £329 goes to the 5 retained households,
  whose counterfactual is a rival's tariff, not our default. That £329 is therefore an overstatement
  of unknown size.
- **Reading (F11):** letter plus re-fix is "not shown to destroy value". It gives at least £1,420 to
  households who stay, and the company side's sign is unestablished. The letter alone is shown to
  cost the company. The re-fix is what makes the letter defensible, so the two should not be
  switched on separately.

**A number to check, not chase:** £270 of `total_net` per electricity customer-year. Published
supplier margins are tens of pounds per dual-fuel account a year (Ofgem's supply market
indicator), so `total_net` is probably not net of opex. That does not move the attribution, which
is a ratio within one book. It does mean £8k should not be quoted as a profit figure.

**Next (one variable):** the seed. ΔC's sign rests on 14 named customers on one path. Replicate the
A/B/C triple on further book seeds (`SE_POPULATION_SEED`, EP17; unset is this book), and bound ΔC before any claim
that the letter creates value for the company.

## Status (2026-10-25): the seed replication runs at one commit

All nine seed arms are re-running at 9bb30c4de5, the fix for a home move on a term boundary. The
fix alone moves A_61102's `total_net` by +£14,441, more than this record's ΔC of −£389 or its
£8,252. Grading across commits would therefore measure the world change, not the arm. The
comparison and the queued grade are in
`SEAT_PREREG_C30_THE_LETTER_AND_REFIX_COMPANY_SIDE_ACROSS_BOOK_SEEDS_2026-10-24.md` (Status
2026-10-25). The verdict against this record waits for `at-9bb30c4de5/grade.txt`.

## Verdict across seeds (2026-10-25, grade.txt at 9bb30c4de5)

The full table is in the seeds record's Result. Against this record:

- **"The £1,360 that the pair could not place is retention": true on the default book, not
  general.** The re-fix keeps 4, 0 and 1 households on seeds 61101, 61102 and 61103. B − C is
  +£1,360, −£3,574 and −£890.
- **"£268 and £275 agree within 3%, so knock-ons are small": refuted on two of three seeds.** B − C
  leaves −£4,079, −£2,678 and −£213 unattributed once retention and H are priced. On 61102 nobody
  moves, yet B − C is four times H.
- **"The letter alone is shown to cost the company": held on every seed.** C − A is −£7,211,
  −£6,345 and −£3,975, through 7–8 `price_position` exits, at £180–£304 per customer-year.
- **"The re-fix is what makes the letter defensible": withdrawn.** ΔC = B − A is −£5,851, −£9,919
  and −£4,865. The households that stay gain £896–£1,410 of H, and that is a transfer.

## Correction (2026-10-25): the retention counts missed the fixed-renewal route

This record's "5 kept" and the seeds' "4, 0, 1 kept" counted SVT departures only. A re-fixed
household's next exit is a fixed-renewal roll at the fix's end, and several leave there. Counting
both routes, the re-fix's customer-years are +32.59 on this book (was +37.76) and +7.57, −12.78 and
−3.38 on the seeds (were +28.76, 0 and +4.25). On 61102, the "−£2,678 with no customer moving" is
two renewal-route leavers, −£1,637 and −£980, and there is no booking defect. `total_net` and so ΔC
are unchanged. The exact split is in the seeds record, "The −£2,678 on 61102: result".
