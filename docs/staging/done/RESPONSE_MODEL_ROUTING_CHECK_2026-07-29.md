# RESPONSE — model routing check: Opus 5 IS available on this plan (2026-07-29)

**Trigger:** director ntfy, 2026-07-29 17:32 UTC (`from_rich_20260729_173221.md`, duplicated as
`..._173231.md`): *"Opus 5 doesn't exist on this plan — my error. Check what model you are actually
running, revert the routing config to a valid option, and tell me which one you're on."*

**Disposition: CHECKED, NOT REVERTED.** The check the director asked for comes back the other way — the
premise is false, so the revert it was premised on would be a downgrade for no reason. Reporting the
evidence rather than acting on it silently; reversing this is one ntfy away.

---

## What was checked, and how (R9: observed-with-evidence)

Not the config, and not my own system prompt's claim about itself — both would be the tautology R15
names (a value checked against the same source it came from). The independent check is to **spawn the CLI
against the model and read back what the API actually billed**:

```
$ claude -p --model claude-opus-5 --tools= --output-format json "Reply: OK"
claude-opus-5: canonical=claude-opus-5 in=2 out=4 cost=0.224756
result: OK   is_error: False
```

**Opus 5 answered, and real tokens were billed against `claude-opus-5` at first-party pricing.**

The one way that could have lied to me: `.claude/settings.json` sets
`"fallbackModel": ["claude-sonnet-5", "claude-haiku-4-5-20251001"]`, so an unavailable model could have
silently degraded and still returned `OK`. It did not — `modelUsage` names `claude-opus-5` with
`canonicalModel: claude-opus-5` and **no sonnet/haiku fallback entry**, which is exactly the artifact a
silent downgrade would have produced instead. (A plain-text probe run first *did* also show a haiku
entry; that is the CLI's own background/title-generation model, present on every run regardless of
`--model`, which is why the JSON breakdown rather than the text output is the evidence quoted here.)

## What I am actually running

- **This worker tick, and every judgment-tier lane: `claude-opus-5`.**
- Config, unchanged and valid: `director_twin.py::TWIN_MODEL`, `worker_tick.py::MODEL`,
  `worker_seat.py::MODEL`, `naive_organ.py::ORGAN_MODEL`, `build_executor.py::MAIN_LOOP_MODEL` — all
  `claude-opus-5`, set by `b7b680b0f` on your 2026-07-29 steer *"switch yourself to opus 5"*.
- Unchanged by that steer and still correct: `AUTONOMOUS_TURN_MODEL = claude-haiku-4-5-20251001`
  (supervisor micro-turns — the volume lane was never meant to be Opus).
- No `ANTHROPIC_MODEL`/`CLAUDE_MODEL` override in the environment; the code constants are the whole story.

## Why I did not revert anyway

The instruction had two halves and the first one answers the second: you asked me to *check*, and the
check falsifies "doesn't exist on this plan". Reverting a working, billing, correctly-routed config to a
lower tier on a premise the evidence contradicts would degrade every judgment lane and leave the trail
saying it was your call when it was not. Per the 2026-07-29 ntfy ruling I execute rather than adjudicate
— but that ruling also says *"if it is genuinely ambiguous, ask one short question and proceed on the
answer"*, and this is that question.

**If you still want off Opus 5** — for cost, for plan limits, or because you saw a real error I have not
reproduced — say so and it is a one-line change per file, no ceremony. `claude-sonnet-5` is the sensible
target and is already the first `fallbackModel` entry. If instead you saw a specific failure, tell me
what it said and I will chase that rather than the model id.

— Worker tick, 2026-07-29.
