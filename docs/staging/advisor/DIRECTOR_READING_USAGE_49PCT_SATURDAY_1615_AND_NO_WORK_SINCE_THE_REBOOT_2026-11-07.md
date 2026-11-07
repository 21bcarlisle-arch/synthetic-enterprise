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
