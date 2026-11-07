**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage at 49% on Sat 7 Nov, 16:15 GMT, and no machine commit since the reboot

**Type:** READING, through the advisor channel. The director's words, from chat:

- Sat 7 Nov, 16:15 GMT: "49%"

## The reading

- Plan usage was **49%** at Saturday 16:15 GMT. The previous reading was 46% at 08:36.
- Burn over those 7.6 hours was about **0.4 points an hour** [derived]. Most of it was the advisor's two research passes; the machine was down or rebooting for most of the window.
- The reset is Mon 9 Nov 03:00 GMT, about 35 hours away. Keeping about 10 points for Monday leaves about **41 points**, so up to **about 1.2 points an hour** is affordable [derived].
- **Do not slow down.** The 46% reading stands: work at normal pace. There is room to spend more than normal, on correctness first, then on reading the two evidence packs staged at 16:11 (unpaid debt; household reactions to pain points).

## The thing to fix first

- The last machine commit on origin is **15:29 GMT**. The Windows host rebooted at about 15:46, and nothing has landed since (checked 16:15).
- If the worker seat (tmux `claude`) is up but idle, resume the queue. If any unit failed to come back after the reboot, say which one, and restart it if that is within the harness's own reach.
- Name the cause in the next commit, so a reboot that leaves the machine idle is caught by the watchdog, not by the director.

## Done

(seat executor, 7 Nov ~16:40Z, claim `grade-the-fd91027799-book-through-the-whole-invariant-gate`)

- **Every unit came back.** `systemctl --user` lists the nine services running and none failed, and the timers are
  armed. No unit needed a restart.
- **Why nothing reached origin between 15:29 and ~16:35. It was two causes, neither a dead unit:**
  1. **The dial was `slow`** from 15:26Z to 15:56Z (the 15:29 commit's "slow until Mon 03:00Z"). Under it,
     worker-tick and seat-executor spawn at most every 4h and delivery-seat every 12h. So after the reboot, only
     this seat-executor (spawned 15:55Z) was working. It set the dial back to `normal` at 15:56Z.
  2. **This seat's first landing raced origin.** Each `surgical_land` gate takes about 10 minutes. The advisor's
     own commits moved origin twice in that time (931dfcc27, then 43797d15c), and the promote refused both times
     as not fast-forward. It reached origin as a66e97829 (the N20 fix, landed as 8178e2421) at about 16:35Z.
- **What would catch this next time without the director:** the on-box dead-man's switch only measures the
  commit clock. It fired nothing because 45 minutes had not passed. The off-box check the advisor added is the
  right tool for a reboot that leaves the machine idle. No new control is proposed. The `slow` setting was
  deliberate, and it was wrong only because the 46% reading overtook it.
- **Pace:** normal, as the reading asks. The evidence packs staged at 16:11 come after the correctness work in
  hand, per this reading's own order.
