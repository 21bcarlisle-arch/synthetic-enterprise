**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage at 42% on Thu 5 Nov, 05:55 GMT: on pace

**Type:** READING, through the advisor channel. The director's words, from chat:

- Thu 5 Nov, 05:55 GMT: "How is progress and pace 42% used"

## The reading

- Plan usage was **42%** at Thursday 05:55 GMT, 74.9 hours after the Monday 03:00 reset. The next reset is **Mon 9 Nov 03:00 GMT**, 93 hours away.
- The average burn so far is **0.56 points an hour** [derived].
  - That average includes the roughly 23 hours stalled on the expired login, Tue 09:15 to Wed 08:20.
  - Over working hours alone the burn was about **0.8 points an hour** [derived].
- **Sustainable to the reset: about 0.62 points an hour** (58 points over 93 hours) [derived].
  - At the working rate, usage would reach 100% around **Sat 7 Nov, early afternoon** [derived].
  - At the all-in average, it would reach about 94% by Monday.

## What to do with it

- **Keep the correctness stretch first.** It is finding and fixing real defects at a good rate.
- **Hold the working rate to about 0.6 points an hour.** Concretely:
  - one fresh run at a time;
  - no parallel drafting fan-outs;
  - the cold read only on a book that carries new fixes.
- **The 9 Nov publish must run.** Leave headroom for the Monday run and its grading before the 03:00 reset.
- **Last weekend the director reserved weekend headroom (from 80%).** He has not asked for that this week. If he does, a reading will say so.

## Done

Actioned Sat 7 Nov at 15:26Z by a worker tick, through the dial. This is 2.4 days after the
reading: no earlier tick had drawn it.

    python3 -m background.tick_mode slow --until 2026-11-09T03:00Z --then normal

- **Why slow, and why now.** The reading projected 100% around early Saturday afternoon at the
  working rate. It is now Saturday afternoon. No later reading exists, so I cannot say where usage
  stands, and I have not estimated it. `slow` spaces worker-tick and seat-executor spawns 4h apart
  and delivery-seat 12h apart. That is the dial's nearest setting to "hold about 0.6 an hour", and
  it protects headroom for the 9 Nov run and publish. At 03:00Z on Monday the dial reverts to normal
  by itself, ahead of the run.
- **Correctness stays first.** Nothing about the order changed. The other advisor steers sit behind
  the correctness exit test, or are due at the 11 Nov review, and none of them was fanned out.
- **Not added to `POINT_READINGS`.** That list has stopped at 25 Oct, and 42% was read after the
  2 Nov reset. One point after a reset gives `usd_per_point()` nothing it can fit.
- **To reverse:** `python3 -m background.tick_mode normal`.
