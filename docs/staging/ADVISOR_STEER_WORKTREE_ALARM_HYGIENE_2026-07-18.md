# ADVISOR STEER — Worktree-undeclared pings are noise; alarm on persistence, not transients (director, 2026-07-18)

**Type:** [STEER] — absorb and carry on.

**The director, verbatim:** *"Still getting several undeclared worktree warnings. If they are fine, I don't need to see them; if they need action we need to act!"*

**The problem:** WORKTREE UNDECLARED pings fire every scan on worktrees that are healthy in-flight fork transients (they show MERGED and get reaped moments later). Today's mirror shows ~10 such pings, none actionable. That violates transition-only alerting (R5) and the terse-trigger-wire channel model: an alarm that is always fine trains the director to ignore alarms.

**The requirement (mechanism is your design):** page only when a worktree state is genuinely anomalous — e.g. persists beyond the normal fork lifecycle, is NOT merged, or the count grows abnormally. Healthy transients (declared-or-mergeable, mid-lifecycle, about to reap) are logged, not paged. If a ping fires, it should mean something needs doing; otherwise silence. Same fail-closed spirit as everything else: genuine accretion must still page loudly — the fix is signal quality, not deafness.

— Advisor, via the staging channel.
