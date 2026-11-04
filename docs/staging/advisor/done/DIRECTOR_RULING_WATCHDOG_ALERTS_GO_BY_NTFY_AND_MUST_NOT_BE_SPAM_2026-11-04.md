**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

**Knowledge:** none -- a governance ruling on how alerts reach the director; it states no domain understanding a Knowledge page would carry

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

## Done

*Worker, 4 Nov 2026.*

**The channel.** The phone path is `background/phone_watchdog.py`, run by `phone-watchdog.timer`
every 15 minutes, with no Claude session needed. It sends through the existing topic and the
existing `.env.ntfy`. No topic or credential was created.

**One path to the phone.** It is now the only code that sets `_phone=True`. The dead-man's
`[DEAD-MAN]` push no longer reaches the phone; it goes to the mirror only. That way the 3-a-day cap
covers every message.

**What may alert.** Only three things:
- a login failure;
- a stopped machine, meaning no lane alive and no work commit for 3 hours;
- token expiry, 30 and 7 days before 2027-11-04.

Each limit maps to code:
- **Once per incident:** one alert, one reminder after 12 hours, one all-clear.
- **The cap:** at most 3 sends in any rolling 24 hours, all incidents together. Anything over the
  cap is written to `docs/status/WATCHDOG.md` and not phoned.
- **Quiet hours:** nothing between 22:00 and 07:00 UK. A message held overnight goes at the first
  check from 07:00, if it is still owed.
- **Content:** two plain lines, "what failed since when." and "Fix: ...".

**No banner on the front door.** His 22 Oct ruling removed the front-door banner, so the
status-page copy is `docs/status/WATCHDOG.md`.

**Tests (R15).** `tests/background/test_phone_watchdog.py` has 8 tests:
- the first proves that every kind can page;
- the others prove the once-per-incident rule, the single reminder, the all-clear, quiet hours,
  the cap going to the status page, one-shot expiry warnings, and the two-line content.

Five mutants were run against the tests: cap set to 99, quiet hours off, repeated reminders, an
auth detector that never closes, and live lanes counting as stopped. All five go red. The
repeated-reminder mutant survived at first, because its check fell in quiet hours; the test was
fixed and the mutant then went red.

**Real test message.** One real test message was sent on **Wed 4 Nov 2026 at 09:12:42 GMT**, and
the NTFY delivery state shows `delivered: true`. It is counted against that day's cap.
