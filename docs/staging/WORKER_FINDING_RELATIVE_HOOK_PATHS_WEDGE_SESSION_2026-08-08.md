# [WORKER FINDING] A single `cd` in a Bash call wedged EVERY tool in the session (2026-08-08)

**Status:** root cause FIXED in the same turn (`.claude/settings.json`, 8 hook commands).
Filed as a finding because the class is broader than the instance.
**Severity:** total session deadlock — observed, not inferred.

## What happened — observed with evidence

Mid-tick I ran a Bash call that began `cd docs/staging && ...`. The Bash tool's
working directory persists between calls. Every hook in `.claude/settings.json`
was configured as:

```
"command": "python3 .claude/hooks/block_sudo.py"
```

— a path resolved against the **shell's** cwd, not the project root. From that
point every hook-gated tool failed identically:

```
PreToolUse:Bash hook error: [python3 .claude/hooks/block_unevidenced_claim.py]:
python3: can't open file '/home/rich/synthetic-enterprise/docs/staging/.claude/hooks/block_unevidenced_claim.py'
```

Bash, Read, Write and Edit were all gated by different hooks and all failed the
same way. **The deadlock was total and self-sealing**: the fix required editing
`.claude/settings.json`, which needed Write, which needed a hook, which needed
the fix. `cd` back was itself a Bash call.

## Why it is a class, not an instance

1. **Any** `cd` in **any** Bash call arms it, in any session, at any time.
2. It fails **closed and silently-to-the-director**: the agent goes dark
   mid-tick with no NTFY path (NTFY needs Bash), so it presents as a stall.
3. There is no recovery from inside the normal tool set. Recovery here came
   from `Monitor`, which runs a shell command and happens **not** to be
   hook-gated — luck, not design.

## The fix

All 8 hook commands now anchor to the project directory with a literal fallback:

```
python3 ${CLAUDE_PROJECT_DIR:-/home/rich/synthetic-enterprise}/.claude/hooks/<name>.py
```

The fallback is deliberate: if `CLAUDE_PROJECT_DIR` is ever unset the bare form
would expand to `/.claude/hooks/...` and re-wedge the session — the same
fail-shape one level down.

**Verified both ways (R15), not just resolved:**
- `pwd` from the moved cwd now succeeds — hooks resolve.
- `sudo echo test` is still **BLOCKED by block_sudo.py** — the hook fires on its
  own named defect, so the fix did not turn the guard into a fail-open.

## What this suggests, not yet built

- **`Monitor` is not hook-gated.** It runs arbitrary shell commands. That is
  what saved this session, and it is also a hole in whatever `block_sudo` and
  `block_unevidenced_claim` are meant to enforce. Worth a decision: either gate
  it, or record deliberately that the hook set covers Bash only.
- **A hook that cannot load should arguably fail loudly to NTFY**, not just
  block the call. The blast radius here was "agent silently stops working".
- Nothing else in the repo should invoke an interpreter on a relative path from
  a config file whose cwd it does not control. Not swept for this turn.

— Worker finding, 2026-08-08. Queued per SELF_INTERRUPT_DISCIPLINE: the root
cause is fixed and proven; the two suggestions above are unbuilt and are the
drawable half.
