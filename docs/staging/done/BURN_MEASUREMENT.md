[PROJECT] Burn reporting must be MEASURED, not estimated. Rich does not trust the percentages -- correctly.

RULE: no burn figure appears in an NTFY unless it comes from a named, measured source. "~X% consumed" from intuition is banned; say "burn: unmeasured" instead if no source is available. A wrong number is worse than no number.

MEASURED SOURCES, in preference order:
1. /usage inside the Claude Code session -- reads the actual plan usage from Anthropic. Capture its output programmatically if possible (capture-pane after invoking it in-session), or read it at session start/end and log it.
2. The token-proxy (tmux session token-proxy, built to intercept API responses and accumulate real usage fields). Verify it is actually running and accumulating; if it drifted or died, repair it. Its counter is the continuous source between /usage readings.

CALIBRATION ANCHOR: Rich's authoritative reading from his Claude app: 44% of weekly used as of Saturday ~18:30 BST, reset Monday 04:00. Log that as the anchor point. All proxy-derived percentages calibrate against it (and against each subsequent /usage reading -- recalibrate at every session start).

REPORTING FORMAT in every phase-completion NTFY: "burn: X% weekly (source: /usage at HH:MM)" or "burn: ~X% weekly (source: token-proxy, last calibrated /usage HH:MM)" or "burn: unmeasured". The source tag is mandatory.

Also: reconcile whatever method produced the recent estimates against the 44% anchor and state the discrepancy honestly in the next NTFY -- if prior estimates were guesswork, say so plainly. Per the harness rules: claims must match artifacts; a burn percentage is a claim.
