**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the third arm, Opus 5.5 alone against Opus 5.5 with a Fable 5.2 advisor, on the naive organ's loop diagnosis (2026-11-10)

*Seat executor, 10 Nov 2026, written before either run. This is step 2 of
`docs/staging/advisor/done/DIRECTOR_STEER_A_THIRD_ARM_OPUS_WITH_A_FABLE_ADVISOR_AFTER_CHECKING_THE_MAX_PLAN_ALLOWS_IT_2026-11-10.md`.
Step 1 (it is on the plan, overage is disabled for the org, and 2.1.319's `fable` is Fable 5.1) is
recorded in that file. No routing changes because of this test.*

## The question

On one long, already-closed diagnosis with a known answer, does adding a `claude-fable-5-2` advisor to
an Opus 5.5 session change the quality of the diagnosis, and what does it cost in main tokens, advisor
tokens, allowance and time?

## The task: fixed before any run

**The naive organ's loop.** Symptom: `background/naive_organ.py` asked no new question after
2026-08-10T07:48Z; every log entry after that is a decline. Closed on 2 Nov by `1f731c537a`, whose fix
and control (`tests/background/test_the_naive_organ_asks_again_and_never_reads_its_own_questions.py`,
five mutants) confirmed the causes, and the 3 Nov finding confirmed the repaired organ reaches its
debounce on live state.

**What each arm sees.** A `git archive` of the pre-fix commit `312ccd504d`, with no history:
`background/`, `docs/status/` (LATEST.md as it stood), `docs/observability/naive_organ_log.jsonl`
(31 MB, 26k+ entries), `docs/design/NAIVE_ORGAN_DESIGN.md`, `tests/background/test_naive_organ.py` and
its fixtures. Nothing from `docs/staging/` and no later commit, so neither the advisor's 2 Nov
hypothesis nor the fix is visible. Checked: no file in the extract names the self-feed, the steer or
the diagnosis. Each arm gets its own fresh copy (`/var/tmp/third-arm/task_a`, `task_b`).

**The prompt** gives only the symptom, never the hypothesis. It is identical in both arms, byte for
byte, and is saved beside the readings as `prompt.txt`.

## The answer key

| # | Cause | Strict credit needs |
|---|---|---|
| K1 | **Self-feed.** `process_run_complete` publishes the organ's open questions (`render_digest_section`) into `LATEST.md`, and T3/T4 read `LATEST.md` as claims, so the organ's own questions come back as triggers | the loop from the organ's output, through LATEST.md, back into its trigger input |
| K2 | **Cap starvation.** In `run_system_organ` a purpose decline spends a `max_new=3` slot, so three self-fed lines quoting "north star"/"enterprise value" fill every slot ahead of any real trigger | a decline consuming the per-cycle cap, so real triggers are never reached |
| K3 | **No debounce on declines.** Only `open` questions are debounced; the same declines are re-logged every cycle (about 144 a day) | declines re-written every cycle because the debounce covers only open questions |
| K0 | *Symptom, not a cause:* `is_purpose_claim`'s substring tokens decline those lines | counted, not scored: the advisor already knew it on 2 Nov |

Per arm and per key row: **strict** (mechanism named), **lenient** (right file and function, mechanism
missing or wrong), **miss**. Findings outside the key are listed and checked against the code at
`312ccd504d`; each is graded true or false.

## Method

- **CLI:** 2.1.322 from the isolated prefix `/var/tmp/cc-2-1-322` for **both** arms, so the advisor is
  the only difference. The installed CLI and `~/.claude/settings.json` are not touched.
- **Flags, both arms:** `-p --model claude-opus-5-5 --effort high --restricted --strict-mcp-config
  --tools Read Grep Glob --output-format stream-json --verbose`, prompt on stdin, cwd the arm's extract.
  The advisor arm adds `--advisor claude-fable-5-2`. A smoke call under exactly these flags, before this
  file, was served by `claude-fable-5-2` as advisor (7,823 input tokens, uncached).
- **Order:** alone first, then advisor, sequential, so each run's rate-limit reading is its own (other
  lanes still draw on the same windows, which this cannot remove).
- **Served model, the validity rule** (as in the Fable reader test): a run counts only if `modelUsage`
  holds exactly `claude-opus-5-5` (alone arm) or exactly `claude-opus-5-5` + `claude-fable-5-2`
  (advisor arm), and it is not an error. The advisor arm also needs at least one `advisor` tool call;
  with none it is void and reported as such, since it did not test the advisor.
- **Blind grading.** Each run's final report is saved under a random id. Any sentence that mentions an
  advisor is redacted before grading. The id-to-arm map is a separate file. The grader is a fresh agent
  given the key, the code at `312ccd504d` and the two redacted reports, and not the map.

## Reported apart, never blended

1. **Quality:** strict and lenient against K1–K3 per arm; extra findings true/false.
2. **Main-model tokens** (input, cache read, cache write, output) and **advisor tokens** separately.
3. **Allowance drawn:** not observable per call. Two proxies: the five-hour window's `utilization`
   from the stream's `rate_limit_event` at the start and end of each run (0.01 granularity, polluted by
   concurrent lanes), and API-equivalent dollars from tokens at the published per-MTok prices (Opus 5.5:
   $4 in, $20 out, $0.20 cache read, $8 one-hour cache write; Fable 5.2: $8, $40, $0.20, $16).
4. **Time:** `duration_ms`.
5. **Advisor calls:** count, and whether the guidance changed the outcome. If the stream carries the
   advice redacted (`advisor_redacted_result`), "changed the outcome" can only be read from what the
   main model did next; if even that is unreadable, it is reported as "cannot tell".

## Prediction, written before either run

- **Quality.** Alone: K1 strict, K2 strict or lenient, K3 strict; 2 to 3 strict of 3. Advisor arm: 2 to
  3 strict of 3. **One run per arm cannot separate them.** A gap of one key row either way is reported as
  "cannot tell"; even a gap of two is one sample of one task.
- **Main-model tokens** within ±30% of each other.
- **Advisor:** 1 to 4 calls; advisor input 30k to 300k tokens, all uncached (each call re-reads the
  transcript).
- **API-equivalent cost:** the advisor arm costs 1.2 to 2.5 times the alone arm.
- **Time:** the advisor arm takes 1.0 to 1.6 times as long.
- **Changed the outcome:** no, or cannot tell.
- **Refuted if** the advisor arm scores 2 or more strict rows above the alone arm (a benefit larger than
  predicted), or costs under 1.2 or over 2.5 times, or the main model never calls the advisor on a task
  this long (the docs' "long multi-step task" case would then not engage it unprompted).

## What one task can and cannot decide

It can show a large effect on one long diagnosis. It cannot rank the configurations. Deciding more
needs several closed long tasks (three or more diagnoses or design reads with confirmed keys), both arms
on each, order alternated, and a pre-set decision rule such as "advisor adopted for long diagnoses only
if it gains at least one strict key row on a majority of tasks at under 2x cost".

## Result (seat executor, 10 Nov 2026, about 21:40 GMT)

*The file above was landed as c5732f9b9 before the reading. Its sha256 was recorded at 21:15:18Z, before the
alone run started at 21:15:37Z. The alone arm ran 21:15:37 to 21:19:23Z, and the advisor arm ran 21:19:31 to
21:25:17Z. Raw streams, reports, prompt and map are in `/var/tmp/third-arm/`, outside the repo.*

**Both runs are valid.** In the alone arm, `modelUsage` was `claude-opus-5-5` only. In the advisor arm it was
`claude-opus-5-5` plus `claude-fable-5-2`. Neither run is an error, and the advisor arm made one `advisor` call.
`advisorModel` is absent from `~/.claude/settings.json` afterwards. Only the per-session flag was used, and the
installed CLI was not touched.

**Blind grade.** A fresh agent did the grading. It had the key and the code at `312ccd504d`, and it did not have the
map. The map was opened only after the grade came back: `13fa1c59` = alone, `b9cf4952` = advisor.

| | Opus 5.5 alone | Opus 5.5 + Fable 5.2 advisor |
|---|---|---|
| K1 self-feed | strict | strict |
| K2 cap starvation | strict | strict |
| K3 no decline debounce | strict | strict |
| **Strict / lenient of 3** | **3 / 3** | **3 / 3** |
| Extra claims | All true or plausible. One side-claim is blurred: "the stale tag defeats the debounce" is a real effect but not why the declines recur | All true but one: "open questions are never closed" is false, since 7 were answered. It adds a supported account of why the stall began on 10 Aug and not in July, and it shows LATEST.md lines 2588 to 2591 are eligible but absent from the log |
| Grader's verdict | | "slightly better … bordering on cannot tell" |
| Main model: input / output | 52 / 23,506 | 48 / 19,402 |
| Main model: cache read / write | 1,341,902 / 84,843 | 1,442,438 / 90,271 |
| Advisor: input (uncached) / output | n/a | 83,480 / 13,950 |
| API-equivalent $, main / advisor / total | 1.417 / n/a / **1.417** | 1.399 / 1.226 / **2.625** (1.85×) |
| Five-hour window, start to end | 0.67 to 0.68 | 0.68 to 0.70 |
| Seven-day window | 0.28 to 0.28 | 0.28 to 0.28 |
| Time | **225 s**, 53 turns, 52 tool calls | **345 s** (1.53×), 36 turns, 35 tool calls + 1 advisor |
| Advisor calls | n/a | 1, at tool call 33 of 36, after the search and before the write-up |

**Against the prediction.** Every predicted range held, and no refutation condition was met.
- **Quality:** 3 of 3 strict in both arms. That is the top of the 2-to-3 range, and the arms cannot be told apart.
- **Main-model tokens:** within ±30%. Output was 17% lower with the advisor, and cache read 7% higher.
- **Advisor:** 1 call and 83k uncached input, inside the predicted 1 to 4 calls and 30k to 300k tokens.
- **Cost:** 1.85×, inside the predicted 1.2 to 2.5.
- **Time:** 1.53×, inside the predicted 1.0 to 1.6, but near the top.
- **The main model consulted the advisor unprompted**, once. It did so in the "before declaring done" position the
  docs describe, not before committing to an approach.

**Did the guidance change the outcome? Cannot tell.** The stream holds the advice only as `advisor_redacted_result`
(encrypted), and the main model's thinking is redacted too. What can be seen is that after the call the main model
ran three more searches. All three counted the three standing declines by their exact claim text. It then wrote
the report. Those counts back the "why 10 Aug and not July" account that the grader gave as the advisor arm's edge.
So the advice may have prompted that section, but nothing observable separates "the advisor asked for it" from
"Opus would have checked it anyway".

**Allowance.** Neither window shows a per-run draw at better than 0.01. The five-hour window moved 0.01 across the
alone run and 0.02 across the advisor run. Other lanes were drawing at the same time, so these readings bound the
draw and do not measure it. On API-equivalent dollars, the advisor's single call cost 87% as much as the whole main
session.

## What this decides, and what it would take to decide more

**Decided:** on this task the advisor bought no measurable quality. Both arms found the full key. It cost 1.85×
in API-equivalent dollars and 1.5× in time. **Not decided:** whether the advisor helps when the main model would
miss something. This task was too easy to show that: Opus alone found all three mechanisms in under four minutes,
so the ceiling was hit. One task decides little.

Deciding more would take three or more closed tasks that Opus alone gets wrong, or only partly right, on a first
pass. Each task needs a confirmed multi-part key; candidates are among the 17 Oct labelled commits that Opus missed
strictly. Both arms would run on each task with the order alternated, under a rule set beforehand, for example:
"adopt the advisor for long diagnoses only if it gains at least one strict key row on a majority of tasks at under 2×
cost". Until then the routing stays as it is, Opus alone. No class uses the advisor. Since the advice is encrypted,
whether it changed the outcome can only ever be read from behaviour, so any later test should log the main model's
actions immediately after each call.
