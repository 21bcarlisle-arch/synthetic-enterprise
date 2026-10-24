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
