**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: what predicts a confirmed defect in our own history, for the 11 Nov reader review (2026-11-07)

*Delivery seat, 2026-11-07 ~23:50 GMT, written before any observable below was computed for the
defect set or the population. The result goes in a separate record that cites this one. Steer:
`docs/staging/advisor/done/DIRECTOR_STEER_CALIBRATE_THE_READERS_ON_OUR_HISTORY_AND_SAY_WHAT_EACH_GATE_HAS_CAUGHT_2026-11-05.md`.*

## The defect set D (chosen before measuring)

A commit is in D when a recorded source traces a confirmed defect to it as the commit that introduced it:

- **Reader trial of 17 Oct, labelled bad:** `09e2bf07f`, `b8767ebc1`, `5f6a4f15f`, `f9a22843d`, `ac6b841fb`.
  `58ec2d508` (VAT) is left out of the main set because the trial itself doubts its label.
- **Reader trial, labelled clean but a defect was confirmed on it:** `471ab8960`, `2d3b87a6b`, `1aa97f1a4`.
- **Head-red bisect of 4 Oct (17 turning commits):** `b50a03519`, `2d3b87a6b`, `6f5bb8b68`, `2bb03a094`,
  `3bf64c4e7`, `fc390b918`, `7e9c2c935`, `c3939e7b1`, `f9c1bf956`, `b6136796b`, `7be8cec09`, `92d75a690`,
  `08c696269`, `d029477c7`, `05add41ab`, `c5e9a1b5c`, `178259c6b`.
- **A fix commit names it as the cause:** `d127468fd8`, `41cdd5b51`, `f4b504e6c`, `e16f00de5`.
- **Two-reader review, findings confirmed:** `c89a199faf`, `2dbafe2d23`, `34b764a0fd`. These were chosen by
  the new-module selector, so they are reported with and without, never only with.

The class documents name fix commits, not introducing ones. Their instances are not traced here, and
that is said in the result.

The population is every commit reachable from `origin/main` since 2026-06-01. Each observable is
read from the diff against the first parent, never from the message.

## Predictions

1. **Size predicts.** Commits of 500 lines or more are over-represented in D by at least 1.5 times their
   population share. Confidence: moderate. The head-red set carries world moves and the 357-path
   run-complete commit.
2. **Small is not safe.** At least 5 of the D commits are under 150 changed lines.
3. **A new non-test module is over-represented in D**, but its interval includes no effect once the
   three two-reader commits are taken out. Confidence: low.
4. **Touching `company/` or `saas/` does not predict.** The ratio of D share to population share lies between 0.67 and 1.5.
5. **A long gap since the touched file last changed does not predict.** Same band.
6. **No single observable separates D cleanly.** The best one has a ratio below 3.

Wrong predictions stay beside their results.
