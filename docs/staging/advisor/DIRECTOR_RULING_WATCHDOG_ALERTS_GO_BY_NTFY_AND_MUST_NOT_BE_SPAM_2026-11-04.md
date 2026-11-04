**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Watchdog alerts reach the director by NTFY, and they must not be spam (2026-11-04)

**Type:** RULING, through the advisor channel. These are the director's words from chat on Wed 4 Nov:

- 08:39 GMT: "Ntfy is fine. As long as it isn't spam"

This answers the alert-channel choice in Ask 2 of `DIRECTOR_STEER_USE_THE_LONG_LIVED_TOKEN_AND_NEVER_STALL_SILENTLY_AGAIN_2026-11-04.md`. Do not raise it as a `for_the_director` row.

## The ruling

- **Channel.** Revive the mothballed NTFY path to the director's phone for the watchdog only. Use the existing topic and configuration. If a topic or credential has to be created, ask before creating it, because that is G5.
- **Not spam.** These limits are binding:
  1. **What may alert.** Only two things: a stall that needs his action (an authentication or login failure, or the machine fully stopped), and a token-expiry warning (30 days and 7 days before). Nothing else uses this channel. That means no progress updates, no findings and no publish results.
  2. **Once per incident.** One alert when the incident starts. At most one reminder after 12 hours if it is still open. One all-clear when it recovers.
  3. **Rate cap.** No more than 3 messages in any 24 hours, all incidents together. If the cap is reached, the rest go to the site banner and `docs/status/` only.
  4. **Quiet hours.** None between 22:00 and 07:00 UK time. An incident that starts overnight alerts at 07:00 if it is still open.
  5. **Content.** Each message is one or two plain lines: what failed, since when, and the one action that fixes it. No internal codes.
- **Test.** Under R15, prove the alert fires on a simulated failure. Prove the cap, the quiet hours and the once-per-incident rule hold. Then send one real test message, and record in Done when it was sent.
