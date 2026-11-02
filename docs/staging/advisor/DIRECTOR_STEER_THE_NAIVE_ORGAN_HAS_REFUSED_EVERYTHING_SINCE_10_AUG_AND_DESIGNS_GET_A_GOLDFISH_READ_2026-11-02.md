**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The naive organ has refused everything since 10 Aug, and design proposals get a fresh-context read before they are built (2026-11-02)

**Type:** STEER, through the advisor channel. The director's words, from chat on Mon 2 Nov:

- 06:39 GMT, sharing Google's Elephant-Goldfish model (https://github.com/google/elephant-goldfish-model): "Do we still have naive organ ?"
- 06:40 GMT, on the advisor's recommendation to diagnose the organ and add a fresh-context read of designs before build: "Stage it"

## 1. The organ is silently dead (measured by the advisor on 2 Nov; check it)

From `docs/observability/naive_organ_log.jsonl`:
- **26,691 entries since 13 Jul.** Only **111** asked a question. **7** were answered.
- **The last question asked was 2026-08-10T07:48Z.** Every entry since then is declined, about 165–177 a day: 26,580 in total, all with "THE LINE: purpose/values/fitness is the director's and is not falsifiable".
- **The last 2,000 entries fire on only 3 distinct claims.** All three are the organ's own earlier T3_inherence questions, resurfacing as "[unanswered >24h]". Each contains "enterprise value" or "north star", which `is_purpose_claim`'s substring token match declines.

The advisor's reading, which is a hypothesis for you to test: the organ's own unanswered questions are fed back to it as claims, and a keyword filter on purpose words then blocks them for ever. So the organ loops on its own output and asks nothing new. Because the decline comes before any model call, it has cost log growth and not tokens. But for twelve weeks nothing has questioned the system's own claims, and no control noticed.

This is the shape CLAUDE.md names: "a guard that refuses *everything* passes all of" the tests of whether it refuses correctly. Your job:
- Establish the real cause.
- Then either **repair** the organ or **retire** it with a reason. Repairing means: the purpose line still holds, the organ can be shown to ask again, it never re-feeds its own questions as claims, and a control proves both branches (asks, and declines) are reachable on real input. Retiring is fine if the two-reader review and cold reads now do its job better. Say which, with evidence.
- Whichever you choose, the log stops growing with repeats.
- Look for the same shape elsewhere. Any other organ or watcher whose recent output is 100% one verdict is a candidate. List them with counts.

## 2. A fresh-context read of a design before it is built

Google's Elephant-Goldfish model (Apache-2.0, reported in use by thousands of its engineers, no published metrics) uses fresh reviewers at the design stage. The "elephant" holds the context and drafts the specification. "Goldfish" reviewers read the draft and the material it cites without the conversation that produced it, and surface unstated assumptions and risks before any code is written. Our fresh-eyes reading today happens after code: the two-reader review, the phase-close evaluator and the cold reads. Nothing reads a design proposal cold before build. Proposals that would have qualified recently:
- the map design proposal;
- `THE_IMPROVEMENT_LOOP.md`;
- the M3 scoring change.

Wanted: a design proposal of real scope gets a blind fresh-context read before the build is drawn. The reader sees the proposal and its cited sources, not the session that wrote it. Findings are filed when they are confirmed, the same way as the two-reader review. Use what exists (the phase-close evaluator, the naive organ if repaired, the two-reader machinery) rather than a new organ. Borrow from EGM's skills if they help, since the licence allows it. Measure it like the code review: confirmed findings against noise, through `judge_validation`.

## Not wanted

- No new commit gate.
- No weakening of the purpose line. The organ never questions purpose, values or the fitness function.

## Done means

- The organ's cause established, and the organ repaired or retired, with a control proving the rare branch is reachable.
- The scan for other single-verdict watchers, with counts.
- The design read live on the next qualifying design proposal, with its first findings in the stretch log.

## Risk

Touches: `background/naive_organ.py` and its log, `background/process_run_complete.py` (its step), and the path design proposals take before build.
Blast radius: harness only. Nothing in the world or the supplier.
Probable failure mode: a repair that only removes the three looping claims (keyed to today's answer) and leaves the feedback route or the substring filter as it was. Key the fix to the property.
Proportionality: reversible and narrow — just do it.

— Director steer, 2 Nov 2026, his words above; the measurement and drafting are the advisor's.
