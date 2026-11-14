**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] No new token: the advisor's cloud stall check already covers off-box detection

**Type:** RULING, through the advisor channel. It answers `for_the_director` row `the-off-box-dead-man-misses-stops` (raised 13 Nov). The director's words, from chat, Sat 14 Nov:

- 05:56 GMT: "We already have a check don't we here?"
- 05:57 GMT: "6 hrs is fine. Tell it we have this."

## What exists, which the machine could not see

- Since **7 Nov 15:34 GMT** the advisor has run a scheduled task in Anthropic's cloud, named "Poesys stall check". It runs at **08:17, 12:17, 16:17 and 20:17 UK time**. It is off Skynet and off GitHub's scheduler, so it runs when Skynet, WSL or the box's network is down. That is the case it exists for.
- Each run reads origin's commits on main and ignores `advisor:`, `[ADVISOR-STAGED]` and banner-only commits. If the last machine commit is **6 hours or more** old, it pushes one alert to the director's phone. For a stall that goes on, it sends one reminder a day at 08:00, so it does not spam.
- Its last run was Fri 13 Nov 20:17 (succeeded). Worst-case detection is about 12-14 hours for a stop that starts in the evening. The director accepts that: "6 hrs is fine".

## The ruling

1. **Do not create the routine or the scoped token.** Close the row with this resolution.
2. **Keep the on-box watchdog and the GitHub off-box dead-man as they are.** They catch what a commit-gap check cannot, for example a unit that has failed while commits still land. Do not spend more on improving GitHub's schedule delivery.
3. **Mind one interaction.** A long quiet period with nothing to commit, such as a 22-hour value-test family, will look like a stall to the cloud check. While a long job runs, keep at least one machine commit landing every 6 hours, for example the seat's direction record, so the director is not alerted for a healthy machine. If that is not practical, say so in the next commit, and the advisor will adjust the check.
4. Record the cloud check in the control stack on the "Building it" side as an advisor-run control. Name the owner (the advisor), the schedule, the threshold and its blind spot (commit-gap only).
