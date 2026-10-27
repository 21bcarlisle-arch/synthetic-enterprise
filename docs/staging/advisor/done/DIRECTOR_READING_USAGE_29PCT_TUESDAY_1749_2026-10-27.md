**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage at 29% on Tue 27 Oct, 17:49 GMT: at this burn the week runs out on Saturday

**Type:** READING, through the advisor channel. The director's words, from chat:

- Tue 27 Oct, 17:49 GMT: "29%"

## The reading

- Plan usage was **29%** at Tuesday 17:49 GMT, 38.8 hours after the Monday 03:00 reset.
- The previous reading was 10% at Mon 13:27. Over the 28.4 hours between them the burn was about **0.67 points an hour** [derived]. That figure includes the advisor's own share.
- At that rate the remaining 71 points last about 106 hours, so the allowance would run out around **Sat 31 Oct, 03:00–04:00**. That is about two days before the Mon 2 Nov 03:00 reset [derived].
- A sustainable rate to the reset is **≤ 0.55 points an hour** (71 points over 129 hours) [derived].
- Last week ended about 35–40 points unspent. This week runs the other way: the correctness stretch is drawing heavily, and that is the right thing to spend on.

## What to do with it

Pacing is yours to decide under the director's 15 Oct delegation. What is wanted:

- **Keep the correctness stretch first.** Do not cut it to save tokens. Last night's and today's work found real defects:
  - prepayment SVT priced at the direct-debit level;
  - the standing charge stepping on 1 January, not on the cap's own dates (Jan–Mar 2022 electricity at 1.70× its cap);
  - EBSS credit;
  - life events landing outside the supply window.

  That is what the spend is for.
- **Cut what is not correctness.** Hold any work in the held steps until the exit test is met. Do not run fresh full runs in parallel; one at a time, each pre-registered. Hold the cosmetic site work: the 2 Nov deferrals can wait for the Monday publish.
- **Aim for ≤ 0.55 points an hour.** Re-read at the next director reading. If the burn is still above 0.6, narrow to the exit test's three legs and nothing else.
- The advisor will hold its own spend to the Monday cold read and replies to the director.

## Done

*2026-10-27, worker tick (pacing under the 15 Oct delegation).*
- **The tick dial stays `normal`.** `slow` would space worker and executor ticks to 4 h and the
  seat to 12 h. That is far more than the ~18% cut from 0.67 to 0.55 points an hour, and it would
  starve the correctness stretch, which the reading says not to cut. Re-read at the next director
  reading. If the burn is still above 0.6 points an hour, narrow to the exit test's three legs, as
  the reading says.
- **This tick spent serially.** It closed the lane-D blocking finding, and its last runner residue
  was a correctness fix. It did **not** spawn the BUILD fork for W2_36, so no second context
  stream ran. W2_36 is step 2 and is not held by the stretch, so a later tick draws it.
- **Already in force, and checked:** the draw refuses held steps 6–13 (cd59b84f9c). Fresh runs go
  one at a time, each pre-registered, as the 2eeb3f0b3 run was.
- **The ruling of 26 Oct stays open in `advisor/`**, because its exit test is not met (third leg:
  `DIRECTION.yaml` `thesis_read`).
