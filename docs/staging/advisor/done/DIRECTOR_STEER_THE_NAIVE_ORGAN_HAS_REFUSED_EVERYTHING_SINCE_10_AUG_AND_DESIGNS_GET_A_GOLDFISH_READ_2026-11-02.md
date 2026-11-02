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

## Done (part 1, 2 Nov; the file stays here until the design read has run once)

**Cause, measured on the live log and a no-model dry run of the detectors.** The advisor's hypothesis
holds, and it was half the cause.
- *Self-feed.* `process_run_complete` publishes `render_digest_section()` into `LATEST.md`, and T3 and
  T4 read `LATEST.md` as claims. On 2 Nov, 74 of the 85 live T3 triggers were the organ's own questions.
- *Cap starvation (not in the hypothesis).* `run_system_organ` counted a purpose decline toward
  `max_new=3`. Three self-fed lines quote GOAL_CONST's "north star" and are declined, so they filled
  all three slots ahead of every real trigger on every cycle. The 40 un-asked triggers never got a slot.
- *No debounce on declines.* Only `open` was debounced, so the same three declines were re-logged
  about 144 times a day. The total is 27,663 declines. Since 2026-08-10T07:49Z there have been 17,390
  entries, and every one is `T3_inherence`/`declined_purpose`.

**Repaired, not retired.** Each fix is keyed to its property, not to the three claims.
- `without_own_output` drops any line carrying a question the organ logged. It matches on the
  question's text, not on the digest's layout.
- Only a model call spends the cap.
- A decline already on record is not written again.
- The purpose line is unchanged: `is_purpose_claim` and its tokens are untouched.

Control: `tests/background/test_the_naive_organ_asks_again_and_never_reads_its_own_questions.py`.
- Input: the three real looping questions, verbatim, plus one ordinary claim and one purpose claim,
  with `max_new=1`.
- One test covers the partition: it asserts one ask and one decline, and that a second cycle writes
  nothing.
- Five mutants each turn it red: self-feed restored, declines spend the cap, declines re-logged,
  everything declined, nothing declined.

**A refuted prediction, kept.** I predicted that after the repair at least one never-asked trigger
would be askable on live state. None is.
- The 10 triggers left are all questions asked before 10 Aug that are still `open`.
- The last three days' 66 commit subjects carry none of T3's tokens.

So the organ is unblocked but has nothing new to ask today. The 104 open questions from July and
August are what it is waiting on. Answering or closing them is the next lever, and it is not done here.

**Single-verdict scan** of every `docs/observability/**/*.jsonl` with 50 or more rows, over the last 2,000:
- `naive_organ_log.jsonl`: `verdict=declined_purpose` 2000/2000. This is the organ above, now fixed.
- `model_tier_log.jsonl`: `outcome=SPAWNED` 1999/1999 (3,635/3,635 lifetime). This is constant by
  construction: `log_decision` defaults it and its only caller (`worker_tick.py:549`) passes nothing
  else. It is a launch record, not a verdict.
- `heavy_job_deferrals.jsonl`: `admitted=False` 2000/2000 (4,521/4,521 lifetime). This is a deferral-only
  log by construction. The content is worth reading: 1,994 of the last 2,000 defer `sim_run`, the
  latest on "landings come before experiments".
- Six other logs carry no verdict-like field and are not graded by this scan: `decision_log`,
  `instructions_loaded_log`, `size_ratchet_warnings`, `staging_root_resurrection`,
  `test_execution_log` and `token-usage-log`.

**Still owed (part 2).** The fresh-context design read. Its first qualifying proposal is
`THE_VALUE_TEST_REDESIGN.md`, which does not exist on 2 Nov. It runs through the phase-close
evaluator or the two-reader machinery (no new gate) and is measured through `judge_validation`.

## Done (moved to done/, 2 Nov, worker tick)

Read against its signed bytes (1a20efa5d). The later commit 1f731c537 is unsigned, and it changes none of the
director's text: it only appends the part 1 Done section above. Part 1 is landed in 1f731c537a. The organ is
repaired, not retired. Its control is
`tests/background/test_the_naive_organ_asks_again_and_never_reads_its_own_questions.py`, and the single-verdict scan
is above.

Part 2, the fresh-context design read, is still owed. It does not need this file to stay in the channel, where the
unsigned edit made the doorbell refuse it on every tick. `docs/direction/DIRECTION.yaml` carries it:
- focus item 2 (`the-capabilities-page-and-the-value-test-redesign`) writes `THE_VALUE_TEST_REDESIGN.md`;
- that release unblocks the queued `the-design-read-runs-on-the-value-test-redesign`, the first qualifying design
  for the read.

Its first findings go to the stretch log, as the steer asks.
