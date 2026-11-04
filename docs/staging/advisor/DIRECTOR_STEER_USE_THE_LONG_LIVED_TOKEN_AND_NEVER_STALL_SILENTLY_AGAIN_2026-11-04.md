**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Use the long-lived token, and never stall silently again (2026-11-04)

**Type:** STEER, through the advisor channel. These are the director's words from chat on Wed 4 Nov:

- 08:22 GMT: "I needed to login and authorise again. Can we avoid this?"
- 08:33 GMT, after generating the token over SSH: "Done"

## What happened

- The machine landed nothing from **Tue 3 Nov 09:15 to Wed 4 Nov about 08:20 GMT, about 23 hours.** Usage was at 26%, so the cause was not the plan limit.
- The cause was that **the interactive Claude Code login expired.** The director had to log in and authorise again by hand.
- Nothing told him. He found out only when he asked the advisor how progress was going.

## What the director has done

- **This was his to do (G5: live credentials).** He ran `claude setup-token` on Skynet over SSH on 4 Nov at about 08:30 GMT.
- **Where the token is:** in `~/.config/synthetic-enterprise/.env.claude` as `CLAUDE_CODE_OAUTH_TOKEN=…`, with permissions 600.
- **He tested it.** The test ran with `ANTHROPIC_API_KEY` unset.
- **Its life is one year, so it expires around 4 Nov 2027.**
- **Never read, print, log, copy or commit the token's value.** Only refer to the file.

## Ask 1: wire the token in (today)

1. **Load the token file in every unit that spawns a `claude` session.** Do this through `EnvironmentFile=%h/.config/synthetic-enterprise/.env.claude` in the systemd units, or the launcher's equivalent. Systemd user services do not read shell profiles.
2. **Make sure `ANTHROPIC_API_KEY` is absent** from those environments. If it is present, it takes precedence and bills separately.
3. **Know the limits of this token, and confirm nothing depends on them.** It authenticates model requests on the director's subscription. It cannot start Remote Control sessions, and it cannot load claude.ai connectors. Locally configured MCP servers still work. Confirm that no unattended spawn needs anything the token cannot do. Also, `--bare` ignores this variable.
4. **Prove it end to end.** Restart the services. Run one spawned session under the token. Record in Done that it authenticated through the token and not through the interactive login, for example with `/status` or the equivalent check. Then leave the interactive login alone, so that it is no longer load-bearing.
5. **Record the expiry, and warn ahead of it.** Record the creation date (2026-11-04) and the expiry (about 2027-11-04). Raise a `for_the_director` row **30 days before** expiry, and again 7 days before, telling him to rerun `claude setup-token` and replace the file.

## Ask 2: a watchdog that does not need Claude (this week)

A silent stall must reach the director within hours, not when he happens to ask. Design it so that it **runs without any `claude` session**, because the failure it watches for is exactly the one that stops sessions. Prompts follow; you decide:

1. **Detect the problem.** Watch for two things:
   - **authorisation failures:** a 401, "invalid bearer token", "please run /login", or a spawn that exits on authentication;
   - **silence:** no landed commit on origin for N hours while work is drawn, with N about 3–4 in waking hours.
2. **Alert him.** Send one plain message: what failed, since when, and the one action that fixes it.
   - **The channel is the director's call (G5: real people and accounts).** Propose the simplest options:
     - revive the mothballed NTFY to his phone;
     - an email;
     - a GitHub issue that notifies him.
   - Raise the choice as one `for_the_director` row with your recommendation.
   - Until he rules, write the alert to the site's status banner and to `docs/status/`, so the advisor sees it.
3. **Avoid alert storms.** Alert once per incident, with a reminder after a fixed interval. Send an all-clear when it recovers.
4. **Prove the check can fail.** Under R15, the check must be shown to fail: simulate an auth failure and a silent period, and show that the alert fires.
