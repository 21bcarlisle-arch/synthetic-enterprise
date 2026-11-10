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
