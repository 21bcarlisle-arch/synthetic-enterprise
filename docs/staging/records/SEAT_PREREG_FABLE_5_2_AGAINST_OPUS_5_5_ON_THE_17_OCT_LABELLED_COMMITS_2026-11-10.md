**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: Fable 5.2 against Opus 5.5 as a blind reader of seven commits whose defects we already know (2026-11-10)

*Seat executor, 10 Nov 2026, about 07:00 GMT. This answers item 2 of
`docs/staging/advisor/DIRECTOR_STEER_TEST_FABLE_5_2_AGAINST_OPUS_5_5_ON_OUR_OWN_WORK_2026-11-10.md`.
It was written and committed before any reading ran. No model choice changes because of it. The
default stays Opus until this reports.*

## The question

On one real task of ours with a known answer, a blind code read, does Fable 5.2 find the defect we
later paid for at least as often as Opus 5.5? And what does each model cost in tokens, in API-equivalent
money and in time?

## The task set: fixed before any run

These are the 17 Oct reader trial's labelled commits
(`docs/staging/advisor/done/ADVISOR_TRIAL_WOULD_A_READING_REVIEWER_HAVE_CAUGHT_OUR_KNOWN_BAD_COMMITS_2026-10-17.md`).
The trial left out the contaminated VAT commit, and so does this test.

| # | Commit | The answer key: the defect we later confirmed |
|---|---|---|
| 1 | `09e2bf07f` | The NESO carbon series is spliced across the 2020-04-27 basis step, and its post-2020 values are labelled loss-corrected |
| 2 | `b8767ebc1` | It keeps the first 200 characters of hook output, but the verdict is printed last |
| 3 | `5f6a4f15f` | It adds a module-level import and does not update the hand-kept fixture `_MODULES` tuple. Also confirmed: `launch_liveness.check()` fills its 10 preservation slots, and a later corruption is lost |
| 4 | `f9a22843d` | A flat, unsourced `RETENTION_EFFECTIVENESS = 0.20` that takes no account of discount size |
| 5 | `ac6b841fb` | The standing charge is counted in settlement revenue and counted again by `bill_generator` |
| 6 | `471ab8960` | `measure_ageing_resolution` ages paid-off failed bills that the scorer does not age, so the reader and the scorer age different populations |
| 7 | `2d3b87a6b` | Draw-ledger writers in `delivery_lane` load, modify and save without the claim lock |

A **refusal-only probe** is added as task 8: `abec13046a`, the commit that added
`background/model_tier.py`. It has no answer key. It is there because it is harness work about
model routing, the nearest thing we have to the `frontier_llm` refusal line that Anthropic's fallback
page names.

## Method

- **Reader:** the two-reader lane's own reader, unchanged (`background/two_reader_review.py`:
  `_extract`, `_brief`, `reader_prompt`). The commit's own tree comes from `git archive`, with no
  history. The packet holds the commit message, the stat and the `.py` diff. The reader runs
  `claude -p --restricted --tools Read Grep Glob` with that directory as its cwd. Each model reads
  each commit once, from a fresh extract.
- **Effort held equal at `high`.** That is Fable 5.2's default. Opus 5.5 is raised from its default
  of `medium`. This answers the steer's confound. A second setting is not run.
- **Models:** `--model claude-opus-5-5` and `--model claude-fable-5-2`. `--output-format json` gives
  token use, duration and stop reason.
- **Blind grading.** Each reading is saved under a random id. The id-to-model map is written to a
  separate file that is not opened until every reading is graded.
- **Grade per reading, against the key above:**
  - **strict** if a finding names the mechanism;
  - **lenient** if a finding points at its file and function but not at the mechanism;
  - **miss** otherwise.

  On commit 3, either confirmed defect counts. Findings outside the key are counted, but not graded
  true or false in this test.

## The four numbers, reported apart and never blended

1. **Quality:** strict catches out of 7, and lenient catches out of 7, per model.
2. **Tokens:** input, cache read, cache write and output (with thinking, where reported), summed per
   model.
3. **Allowance drawn:** this **cannot be observed per call**. The subscription does not report a
   draw per session. The proxy is API-equivalent dollars, recomputed from tokens at the published
   per-MTok prices:
   - Opus 5.5: $4 input, $20 output, $0.20 cache read, $8 for a 1-hour cache write;
   - Fable 5.2: $8 input, $40 output, $0.20 cache read, $16 for a 1-hour cache write.

   **Not the CLI's own `total_cost_usd`.** CLI 2.1.319 does not recognise `claude-fable-5-2`
   (`unrecognized_model`, `costBasis: unknown`). It priced a smoke call at Opus rates: $0.0027096
   for 1,948 cache-read, 279 one-hour cache-write and 4 output tokens. That matches the Opus table
   exactly, and Fable's table would give $0.0048.
4. **Time:** `duration_ms` per reading, summed per model.

Also reported: every non-`end_turn` stop reason and every refusal on Fable, with the task that
triggered it.

## Prediction, written before any reading

- **Quality.** Opus: strict 2 to 4 of 7. Fable: strict 2 to 5 of 7. The 17 Oct trial had Opus at 1
  of 5 strict on commits 1 to 5, and commits 6 and 7 are easier because both defects sit inside the
  diff. **Seven cases cannot separate the two models unless they differ by 3 or more strict
  catches.** A smaller gap, either way, will be reported as "cannot tell", not as a ranking.
- **Tokens.** At equal effort, Fable's output tokens per reading are within ±30% of Opus's.
- **API-equivalent dollars.** Fable costs 1.5 to 2.5 times Opus per reading. Its prices are double,
  and its token use is roughly equal.
- **Time.** Fable is no more than 1.5 times Opus per reading.
- **Refusals:** 0 of 8. None of these tasks is cyber or biology work. Task 8 is the one that could
  trip `frontier_llm`.
- **Refuted if:**
  - Fable is 3 or more strict catches below Opus. A cheaper or faster model would then have shown
    a quality loss, and the asymmetric loss rules it out for reading work.
  - Fable's API-equivalent cost falls outside 1.5 to 2.5 times Opus's.
  - Any refusal fires.

## What this can and cannot decide

It can show a large quality gap on one kind of work, a blind code read. It cannot show that Fable
is better at diagnosis or design reads. A null result here leaves the routing as it is: Opus is the
default, and no Fable class is added on this evidence alone. Proving that the fallback fires needs
a refusal to occur. If none occurs, the fallback is **not** proven, and any Fable class would have
to carry `--fallback-model claude-opus-5-5` and be tested on its first refusal.

## Added after filing: the fifth reported fact, which model served each reading

*Added 10 Nov, about 08:00 GMT, on the director's 07:42 steer
(`DIRECTOR_STEER_PROVE_FABLE_SERVED_EVERY_FABLE_READING_AND_USAGE_AT_21_PERCENT_2026-11-10.md`).
This is a validity condition, not a changed prediction. It was written before any reading was graded.
The 16 readings had already run (07:10 to 07:24). The seat that wrote this section has seen the
id-to-model map, so it does not grade. The grading goes to a reader that has not seen it.*

**5. Served model.** A reading counts only if the CLI's `modelUsage` for that call holds **exactly**
the requested model, with no second key, and the call is not an error. Any other reading is void,
is reported as void, and is never counted. A rerun replaces it.

**Why "exactly", proved on a real substitution (CLI 2.1.319, 07:57 to 07:59 GMT).**
A one-word prompt, `--output-format stream-json`, reading the API's own `message.model`:

| Requested | `message.model` (from the response) | `modelUsage` keys |
|---|---|---|
| `claude-fable-5-2` | `claude-fable-5-2` | `claude-fable-5-2` |
| `claude-opus-5-5` | `claude-opus-5-5` | `claude-opus-5-5` |
| `opus` (alias) | `claude-opus-5-5` | `claude-opus-5-5` |
| `claude-fable-5` | **`claude-opus-4-8`** | `claude-fable-5` **and** `claude-opus-4-8` |

The last row is a substitution. `claude-fable-5` took 17,785 cache-write tokens and wrote 0 output
tokens, and `claude-opus-4-8` answered. A check that asked "is the requested model in `modelUsage`?"
would have passed it. The exact-set check, or `message.model`, catches it. So the check can fail,
and it does fail on a real substitution.

The `unrecognized_model` warning on `claude-fable-5-2` comes from the CLI's own price table. The
server did serve Fable 5.2: its `message.model` and `modelUsage` both name it, and only it. The CLI
can reach Fable 5.2, so no CLI update is needed for this test.

**Result over the 16 readings in `/var/tmp/fable-trial/readings/`:**
- **8 of 8 Opus readings** were served by `claude-opus-5-5` alone.
- **8 of 8 Fable readings** were served by `claude-fable-5-2` alone. **No substitution occurred.**
- **2 Fable readings are void.** Those are commit 6 (`471ab8960`) and commit 7 (`2d3b87a6b`). Both
  returned `is_error` with "You've hit your 5-hour limit · resets 8:20am". That is a usage-limit
  stop. It is **not a refusal**, so it is not counted against the refusal prediction. Both are rerun
  after the reset and checked by the same rule.

Usage reading at the time: the director's 21% of the weekly allowance at 07:42 GMT. Under P12 that
leaves the two reruns and one blind grading pass well inside what remains.

## Graded (worker tick, 10 Nov 2026 ~19:30 GMT)

**The two void readings were rerun** at 18:36 to 18:49 GMT, after an earlier rerun at 08:21 died mid-call with
nothing written. Both reruns are valid under fact 5: `modelUsage` holds `claude-fable-5-2` alone, and neither is an
error. Every reading counted below is valid: **8 of 8 per model**.

**Grading was blind.** A fresh agent graded the 16 readings from `READINGS.md`, which carries reading ids and commit
shas only, against the answer key above. It was told not to open the mask and was given no route to the model
names. The grades were joined to the mask afterwards. Where it was torn between lenient and miss, it gave the lower
grade, as instructed; it named two such cases, both graded miss.

| Commit | Opus 5.5 | Fable 5.2 |
|---|---|---|
| 1 `09e2bf07f` | miss | miss (torn: it points at the step's constant, not the splice) |
| 2 `b8767ebc1` | miss (torn: right function, other defect) | **strict** |
| 3 `5f6a4f15f` | strict (the 10 slots) | strict (the 10 slots) |
| 4 `f9a22843d` | miss | miss |
| 5 `ac6b841fb` | strict | strict |
| 6 `471ab8960` | strict | strict |
| 7 `2d3b87a6b` | **strict** | miss |
| 8 `abec13046a` (probe) | normal reading | normal reading, **no refusal** |

**The five reported facts, apart and never blended:**

| | Opus 5.5 | Fable 5.2 | Fable / Opus | Prediction | Graded |
|---|---|---|---|---|---|
| 1. Quality, strict of 7 | 4 | 4 | | Opus 2–4, Fable 2–5; under 3 apart is "cannot tell" | **held: cannot tell** |
| 1. Quality, lenient of 7 | 0 | 0 | | | |
| 2. Output tokens, 8 readings | 107,847 | 261,115 | **2.42×** | within ±30% | **refuted** |
| 2. of which thinking | 60,791 | 181,723 | 2.99× | | |
| 2. Cache read / 1-hour cache write | 8.71M / 0.55M | 13.42M / 1.15M | 1.54× / 2.10× | | |
| 3. API-equivalent $, recomputed | 8.28 | 31.53 | **3.81×** | 1.5–2.5× | **refuted** |
| 4. Time, summed `duration_ms` | 1,102 s | 2,915 s | **2.65×** | ≤ 1.5× | **refuted** |
| 5. Served by exactly the model asked | 8 of 8 | 8 of 8 (2 after rerun) | | | **valid** |
| Refusals | 0 | 0 of 8, task 8 included | | 0 of 8 | **held** |

Per reading, Fable wrote more output than Opus on **all eight** commits (2.0× to 3.1×) and took longer on all
eight (2.1× to 3.4×). So the token and time ratios are not carried by one long reading, and the two reruns' later
hour does not explain them.

The CLI's own `total_cost_usd` puts Fable at $17.11, because CLI 2.1.319 prices it at Opus rates. The recomputed
$31.53 is the figure, as the method said.

**What I got wrong, beside the prediction.** I predicted Fable's tokens would be about Opus's at equal effort, so
its cost would be its price ratio. At `--effort high` Fable thinks about three times as much as Opus does at the
same setting. "Equal effort" was equal flags, not equal work.

**What it means.** On a blind code read, Fable 5.2 found no more of our known defects than Opus 5.5. Each found one
the other missed, so the two are not the same reader. It drew about 2.4 times the tokens and took about 2.6 times as
long. Seven cases cannot rank two readers 4 apiece. They can show that Fable is not a cheaper or faster reader for
this work. Under the asymmetric loss, nothing here argues for routing reads to Fable.

**Recommendation for `model_tier.py` (steer item 3).** No change to the default model: Opus stays the default and
the fallback. No Fable class for reading work on this evidence. Fable stays a candidate where depth compounds:
diagnosis, design reads and end-to-end checks. That needs a long-task test, and the third-arm steer
(`DIRECTOR_STEER_A_THIRD_ARM_..._2026-11-10.md`) is that test. The fallback is still **not proven**, because no
refusal fired. Any future Fable class must carry `--fallback-model claude-opus-5-5`, with the fallback proved on
its first refusal.

**Spend on the record:** 16 valid readings at $39.81 API-equivalent, plus 2 void and 4 probe calls. At 18:55 GMT the
API's own rate-limit event read 0.25 of the seven-day window and 0.40 of the five-hour window used.
