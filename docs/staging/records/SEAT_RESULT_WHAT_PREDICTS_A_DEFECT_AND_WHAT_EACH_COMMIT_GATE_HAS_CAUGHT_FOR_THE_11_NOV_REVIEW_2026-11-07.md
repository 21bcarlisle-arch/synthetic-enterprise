**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# For the 11 Nov reader review: what predicts a confirmed defect here, and what each commit gate has caught (2026-11-07)

*Delivery seat, 2026-11-07/08, claim `calibrate-the-readers-selector-for-the-11-nov-review`. This answers both
items in the director's steer `docs/staging/advisor/done/DIRECTOR_STEER_CALIBRATE_THE_READERS_ON_OUR_HISTORY_AND_SAY_WHAT_EACH_GATE_HAS_CAUGHT_2026-11-05.md`.
The pre-registration is `docs/staging/records/SEAT_PREREG_WHAT_PREDICTS_A_CONFIRMED_DEFECT_IN_OUR_OWN_HISTORY_2026-11-07.md`
(landed `b47a73b6d` before any observable was computed). The earlier reading that the publisher's refusal records
cannot answer item 2 is `docs/staging/records/SEAT_READING_THE_REFUSAL_RECORDS_COVER_ONLY_THE_PUBLISHERS_CYCLES_FOR_THE_11_NOV_GATE_REVIEW_2026-11-07.md`.
No gate was added, changed or proposed.*

## The short answer

- **Size predicts weakly once you compare like with like.** Against every commit, 500+ changed lines is 2.9 times
  over-represented among commits that introduced a confirmed defect. That figure is mostly a confound: the population
  is 60% docs-and-data commits, and almost every defect commit is a code commit. Against code commits only, the
  ratio is 1.6 (p = 0.07). The strongest like-for-like signals are **10 or more files (2.6×, p = 0.009)**,
  **touching `simulation/` or `sim/` (2.4×, p = 0.003)** and **touching published artefacts (2.3×, p = 0.045)**.
  These are 13 observables tested on 25 cases, with no multiplicity correction, so only the first two would survive one.
- **Today's selector, "adds a non-test module", does not predict.** Among code commits it is *under*-represented in
  the defect set: 16% of defects against 23% of commits (ratio 0.71). It caught 4 of the 25 traced defects.
- **Small was not safe here either,** but less often than Mc Gowan found: 3 of 25 code defects came from commits
  under 150 lines.
- **Gates (item 2).** The publisher's records cannot name a single gate: all 13 refused cycles since 25 Sep are
  `UNATTRIBUTABLE (hook block not retained)`. I rebuilt per-gate refusals from 1,054 session transcripts, which
  cover **30 days, not three months**, because transcripts older than about 8 Oct no longer exist. In that window
  there were 784 refusal events and 1,157 landing events. Real catches appear in a judged sample for seven gates:
  RED TEST, three test-gate checks (the walker-invisible wall channel, the wall-crossing register and the
  landed-path claim), the orphan ratchet, the annual-report import ratchet, startup-anchor freshness. One more
  catch came where the chain was named but the gate was not. The three commit-msg gates make up 230 of the 784 events.
  The sample found them catching paperwork only, which is by design. **Thirteen hook gates refused nothing in the
  window: "no evidence".** The data cannot tell dead from deterrent, so I propose no retirement. The site-lane
  gate is the costliest step, at about 150 s per commit. In 6 sampled refusals it caught nothing real and was at
  fault 4 times. That is a question for the review, not a finding yet.

## Section 1 — what predicts a confirmed defect

### The defect set D, and what it is not

31 introducing commits, fixed before measuring, from four sources:
- the 17 Oct reader trial: 5 labelled bad, plus 3 labelled clean where the trial confirmed a defect;
- the 4 Oct head-red bisect: 17 turning commits;
- fix commits that name their cause: 4;
- the two-reader review's confirmed findings: 3.

`2d3b87a6b` appears in two sources and is counted once. The trial's VAT commit `58ec2d508` is left out because its
own label is in doubt.

**What D under-samples.** The class documents (`CLASS_*`) name the commits that *fixed* each instance, not the ones
that introduced it. Their instances are **not traced**, and so are not in D. The trial's "pointed at by a fix
commit" census could be extended by blame on the fix diffs (SZZ). I did not do that this turn, so this D leans
towards defects that turn a test red (17 of 31). That kind skews towards commits that touch many files, because
a stem-mismatched test elsewhere goes red. This is a reason to discount the "10+ files" signal, not to trust it more.

**Population.** All 14,844 commits on `origin/main` since 2026-06-01 (159 days). That is 1,567 merges and
4,902 non-merge commits that touch a `.py` file. Every observable is read from the diff against the first
parent (`git diff --numstat -M`), never from the message. Gap is the longest time any touched `.py` file had gone
untouched. It was measured for D and for a random sample of 600 population commits.

### The like-for-like table (non-merge commits touching `.py`; the three two-reader commits left out: 25 against 4,902)

| observable | in D (95% Clopper–Pearson) | in population | D share ÷ population share | Fisher p |
|---|---:|---:|---:|---:|
| under 150 changed lines | 3/25 (12%; 3–31%) | 1,225 (25.0%) | 0.48 | 0.17 |
| 150–499 lines | 11/25 (44%; 24–65%) | 2,338 (47.7%) | 0.92 | 0.84 |
| 500–1,499 lines | 8/25 (32%; 15–54%) | 1,049 (21.4%) | 1.50 | 0.22 |
| 1,500 lines and over | 3/25 (12%; 3–31%) | 290 (5.9%) | 2.03 | 0.18 |
| **500 lines and over** | 11/25 (44%; 24–65%) | 1,339 (27.3%) | **1.61** | 0.07 |
| 200+ changed `.py` lines | 18/25 (72%; 51–88%) | 2,420 (49.4%) | 1.46 | 0.03 |
| **10+ files** | 8/25 (32%; 15–54%) | 613 (12.5%) | **2.56** | **0.009** |
| adds a non-test `.py` module (today's selector) | 4/25 (16%; 5–36%) | 1,111 (22.7%) | **0.71** | 0.63 |
| touches `company/` or `saas/` | 9/25 (36%; 18–57%) | 1,272 (25.9%) | 1.39 | 0.26 |
| **touches `simulation/` or `sim/`** | 11/25 (44%; 24–65%) | 917 (18.7%) | **2.35** | **0.003** |
| touches `site/data/` or `docs/state/` | 6/25 (24%; 9–45%) | 524 (10.7%) | 2.25 | 0.045 |
| a touched `.py` file untouched 30+ days (sample of 232) | 6/27 (22%; 9–42%) | 25/232 (10.8%) | 2.06 | 0.11 |
| a touched `.py` file untouched 60+ days (sample of 232) | 1/27 (4%; 0–19%) | 14/232 (6.0%) | 0.61 | 1.0 |

**Against every commit, not like for like**, the same set reads very differently. 500+ lines is 2.87×,
`simulation/` 5.0×, `company/` 3.15× and a new module 2.99×, all with p ≤ 0.004. Under 150 lines is 0.18×. Those
figures say "defects live in code commits". They do not say which code commits. The full output, including D
with the two-reader commits in, is reproducible from the scripts named at the end.

**One thing the table cannot carry:** "a second implementation of something the tree already computes". That
needs a reader or an index, not a diff statistic. **No evidence** either way.

### Scoring the pre-registration (kept beside the predictions, as written)

| # | prediction | result |
|---|---|---|
| 1 | 500+ lines over-represented by at least 1.5× | **Held, narrowly:** 2.87× against all commits, 1.61× like for like (interval wide, p = 0.07) |
| 2 | at least 5 D commits under 150 lines | **Wrong:** 3 (`41cdd5b51` 63 lines, `d029477c7` 82, `b6136796b` 141) |
| 3 | new module over-represented, with no effect once the two-reader commits are out | **Held, and stronger than predicted:** like for like it is *under*-represented (0.71) |
| 4 | `company/`/`saas/` ratio between 0.67 and 1.5 | **Wrong** against all commits (3.15). **Held** like for like (1.39). I had not separated the two populations when I wrote it |
| 5 | gap does not predict (ratio between 0.67 and 1.5) | **Partly wrong:** 30+ days is 2.06 (p = 0.11, outside the band), 60+ days is 0.61. No signal survives |
| 6 | no observable has a ratio of 3 or more | **Wrong** against all commits (`sim/` 5.0). **Held** like for like (best 2.56) |

### Which selector the evidence supports (over non-merge code commits: 4,902 in 159 days, about 31 a day)

| selector | commits selected | traced defects it would have selected (95% CP) |
|---|---:|---:|
| adds a non-test module (today's rule) | 22.7% over Jun–Nov; **2.0%** of all non-merge commits in the trial window (10 of 508) | 4/25 (16%; 5–36%) |
| 500+ changed lines | 27.3% | 11/25 (44%; 24–65%) |
| 200+ changed `.py` lines | 49.4% | 18/25 (72%; 51–88%) |
| touches `company/`, `saas/`, `simulation/` or `sim/` | 37.9% | 14/25 (56%; 35–76%) |
| 200+ `.py` lines **and** touches `company/`/`saas/`/`sim` | 21.1% | 11/25 (44%; 24–65%) |

**Recommendation for the review.** The evidence does not support keeping the selector as it is. At 16% of traced
defects it is the weakest rule here. I recommend widening it to **200+ changed `.py` lines that touch
`company/`, `saas/`, `simulation/` or `sim/`**: 21% of code commits, about 6.5 a day, and 44% of traced defects.
I prefer that to "500+ lines", which selects 27% to catch the same 44%. At the trial's own cost, two Opus readers
of 50k–137k tokens of context each, that is roughly 0.65–1.8M tokens a day. Every number here rests on 25
cases with intervals some 40 points wide. Read the recommendation as "the current rule is the weak one", not "this
rule is right". A held-out check is due once the two-reader review has run a few weeks under any new rule.
**This is the review's decision, not mine.** It changes a standing spend.

### Skipped commits

Over the trial window (26 Oct to now), 508 non-merge commits landed on origin, and the selector qualified 10. Of
those, 8 were read by the shared tree's reader (`.two_reader_readings.jsonl`, 13 attempts). Not selected:
**498 non-merge commits**, each for one reason, "adds no non-test module". **All merges** are excluded by
construction. Of the 25 traced defect commits in this study, 21 would have been skipped by today's rule, for that
same reason. The rule is mechanical, so a missed defect traces back to it from the diff alone. No per-commit skip log
exists; `qualifying_commits()` re-derives the qualifying list from git on demand, and `two_reader_review --status` prints its share.

## Section 2 — what each commit gate has caught

### What each number counts

- **refusal event:** one tool result in a main-session transcript (shared-tree sessions, or the isolated executor)
  that reports a commit refusal: `[surgical-land] REFUSED`, a gate banner, or the chain's red-test summary.
  Re-reads of the same refusal within 20 minutes in one session are collapsed into one event. Results that echo
  refusals rather than report them are dropped: grep over sources, reading `.jsonl`, source-code text. Of 790 events,
  2 named more than three gates and are excluded as echoes.
- **window:** 2026-10-08 22:35 to 2026-11-07 23:17 UTC, the whole transcript record. Transcripts expire after about
  30 days, so **the steer's three-month window cannot be met from this source.**
- **attributed gate:** the banner table the publisher already uses (`process_run_complete._REFUSING_GATE_BANNERS`),
  plus the test gate's own banners, plus the `[tag]` of the three commit-msg gates. When surgical_land's retained
  excerpt does not contain the banner, the event is counted as "gate not in retained excerpt" and is never
  guessed into a gate.
- **sample judged:** up to 6 events per gate, chosen at random (seed 11), 159 in all. A Sonnet reader judged each one
  from the refusal text and what the agent wrote next. **real:** the change was wrong and was fixed. **rule:**
  paperwork, the message or a file's place. **fault:** the gate was wrong, or the red was not this commit's.
  **not a refusal:** an echo, or a misattribution. **unclear.** The rubric is in `/var/tmp/gate_review/` (see the end).
  6 per gate gives a real share no tighter than about ±40 points: 0 of 6 is consistent with anything up to 46%.
- **refusals are not divided by commits.** In the same transcripts there are 1,157 landing events, but a landing
  can follow several refusals, and some commits are not made through surgical_land. 784 refusals beside 1,157
  landings is two counts side by side, not a rate.
- **publisher:** `tools/commit_refusal_attribution.py` over the shared tree's runner log: 13 `commit_refused`
  cycles since 2026-09-25, **all 13 `UNATTRIBUTABLE (hook block not retained)`**. The publisher adds nothing per gate.

### The table (hook-chain order)

| gate | refusal events (shared / isolated) | last refusal | judged | real | rule | fault | not a refusal | unclear | last real catch seen | time per commit |
|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| status-honesty | 2 (1/1) | 15 Oct | 2 | 0 | 0 | 0 | 2 | 0 | **no evidence** | 0.03 s |
| stale-copy guard | 58 (27/31) | 5 Nov | 6 | 0 | 3 | 0 | 0 | 3 | none in sample (see note) | 0.07 s |
| ukds-microdata guard | 1 (1/0) | 2 Nov | 1 | 0 | 0 | 0 | 1 | 0 | **no evidence** | not timed |
| test gate: finding-class consolidation | 9 (8/1) | 7 Nov | 6 | 0 | 2 | 2 | 1 | 1 | none in sample | within 0.8 s |
| test gate: finding-severity header | 9 (4/5) | 4 Nov | 6 | 0 | 6 | 0 | 0 | 0 | paperwork only | within 0.8 s |
| test gate: staging rooms | 13 (0/13) | 27 Oct | 6 | 0 | 6 | 0 | 0 | 0 | paperwork only | within 0.8 s |
| test gate: work item chains to the map | 44 (18/26) | 3 Nov | 6 | 0 | 6 | 0 | 0 | 0 | paperwork only | within 0.8 s |
| test gate: walker-invisible wall channel | 13 (5/8) | 3 Nov | 6 | 3 | 0 | 2 | 0 | 1 | 26 Oct (new wall crossings) | within 0.8 s |
| test gate: wall-crossing register | 5 (3/2) | 17 Oct | 5 | 4 | 0 | 0 | 0 | 1 | 17 Oct (undeclared sim→company crossings) | within 0.8 s |
| test gate: a landed-path claim | 6 (3/3) | 7 Nov | 6 | 4 | 0 | 0 | 1 | 1 | 7 Nov (a finding claiming a file landed that had not) | within 0.8 s |
| test gate: rulebook full | 0 | — | — | — | — | — | — | — | **no evidence** | within 0.8 s |
| test gate: reference resolves | 1 (0/1) | 29 Oct | 1 | 0 | 0 | 1 | 0 | 0 | **no evidence** | within 0.8 s |
| test gate: RED TEST | 191 (112/79) | 7 Nov | 6 | 4 | 0 | 1 | 0 | 1 | 3 Nov (seam test, census, coupled twin) | control set ~155 s + selected tests |
| level-promotion gate | 11 (9/2) | 26 Oct | 6 | 0 | 6 | 0 | 0 | 0 | paperwork only | 0.06 s |
| site-lane gate | 38 (25/13) | 2 Nov | 6 | 0 | 0 | 4 | 2 | 0 | **none in sample** | **~150 s** |
| startup-anchor freshness | 3 (0/3) | 28 Oct | 3 | 1 | 0 | 0 | 0 | 2 | 28 Oct (a stale orientation date) | 1.8 s |
| knowledge-layer gate | 13 (6/7) | 4 Nov | 6 | 0 | 0 | 2 | 0 | 4 | none in sample (merges of origin's own files) | 0.03 s |
| moap-coherence gate | 0 | — | — | — | — | — | — | — | **no evidence** | 0.05 s |
| ruling-archive-question gate | 0 | — | — | — | — | — | — | — | **no evidence** | 0.03 s |
| consolidation-rhythm gate | 0 | — | — | — | — | — | — | — | **no evidence** | 0.06 s |
| size-ratchet gate | 0 | — | — | — | — | — | — | — | **no evidence** | 0.06 s |
| orphan-ratchet | 11 (9/2) | 4 Nov | 6 | 2 | 3 | 0 | 0 | 1 | 24 Oct (modules nothing ran) | 23 s |
| company-network-isolation | 0 | — | — | — | — | — | — | — | **no evidence** | 5.4 s |
| file-scope-generated-paths | 2 (2/0) | 12 Oct | 2 | 0 | 0 | 0 | 0 | 2 | **no evidence** | 4.5 s |
| annual-report-import ratchet | 2 (2/0) | 21 Oct | 2 | 2 | 0 | 0 | 0 | 0 | 21 Oct (forbidden imports of the annual report) | 4.6 s |
| half-hourly-dependency ratchet | 0 | — | — | — | — | — | — | — | **no evidence** | 0.3 s |
| running-total-order gate | 0 | — | — | — | — | — | — | — | **no evidence** | 3.0 s |
| scope-evidence ratchet | 0 | — | — | — | — | — | — | — | **no evidence** | 0.8 s |
| commons-source-supersession | 0 | — | — | — | — | — | — | — | **no evidence** | 0.04 s |
| commons-citation-provenance | 0 | — | — | — | — | — | — | — | **no evidence** | 0.04 s |
| commit-msg: write-time gate (REUSE) | 13 (3/10) | 4 Nov | 6 | 0 | 6 | 0 | 0 | 0 | paperwork only | not timed |
| commit-msg: next-step gate | 163 (100/63) | 7 Nov | 6 | 0 | 6 | 0 | 0 | 0 | paperwork only | not timed |
| commit-msg: director-document gate | 54 (25/29) | 7 Nov | 6 | 0 | 5 | 0 | 1 | 0 | paperwork only | not timed |
| *chain timed out (3,600 s)* | 15 (8/7) | 15 Oct | 6 | 0 | 0 | 4 | 2 | 0 | — | 3,600 s each |
| *pre-commit chain, gate not in excerpt* | 25 (15/10) | 5 Nov | 6 | 1 | 1 | 2 | 0 | 2 | 25 Oct | — |
| *commit-msg chain, gate not in excerpt* | 13 (8/5) | 7 Nov | 6 | 0 | 4 | 0 | 1 | 1 | — | — |
| *test gate, check not in excerpt* | 3 (3/0) | 25 Oct | 3 | 0 | 0 | 0 | 3 | 0 | — | — |
| *unattributable* | 14 (6/8) | 7 Nov | 6 | 0 | 2 | 0 | 4 | 0 | — | — |

The landing door's own refusals are not hook gates, but they cost the same cycle:
- shared HEAD behind origin: 59 events, 58 of them on the shared tree;
- no paths given: 8;
- git plumbing failed: 6;
- merge conflict: 6;
- lost the compare-and-swap race three times: 2.

In the sample all of them were faults or races, except "no paths given", which was operator error.

**Time per commit** is one step-by-step timing (`commit_hook_step_timings.jsonl`, 18 Sep, `49e08b13b`), taken on
the publisher. Steps the file marks as floors are floors. The whole pre-commit chain over 253 publisher commits
(25 Aug to 3 Nov) has a median of 388 s and a p90 of 556 s. The 14 since 8 Oct have a median of 666 s. The
commit-msg gates have never been timed. surgical_land runs them before the tree gate, so their refusals cost
seconds, not a cycle. A refusal by any pre-commit gate costs a full chain re-run.

### What the table says

- **Paperwork gates refuse the most.** The next-step, director-document, write-time, level-promotion, work-item,
  staging-rooms and severity gates make up 307 of 784 events. Every sampled refusal was paperwork, and that is
  their design. They are not "dead". Whether the paperwork earns its keep is a judgement about the process, which
  this data cannot make.
- **Real defect catches concentrate in six places.** RED TEST, the two wall-crossing checks, the landed-path claim
  check, the orphan ratchet and the annual-report import ratchet. Each has a dated catch inside the window.
- **Stale-copy guard: 58 refusals and no real catch in the 6 sampled.** In 3 of those, the reverted bytes were a
  deliberate deletion, cleared with `--drops`. The guard refused correct work that needed a declaration. The other
  3 are unclear. Six cannot say the guard never catches a real revert, and that is its whole purpose. Judge 20 more
  before reading anything into it.
- **The site-lane gate is the one to look at.** It is the dearest step, about 150 s on every commit. In the sample
  it caught nothing real, and 4 of 6 refusals were its own fault: `/tmp` exhaustion, and a red already on origin
  blocking every site commit. 0 of 6 is consistent with a real-catch share of up to 46%, so this is a reason to
  judge all 38, not to retire it.
- **Thirteen gates with no evidence:**
  - rulebook full;
  - moap-coherence;
  - ruling-archive-question;
  - consolidation-rhythm;
  - size-ratchet;
  - company-network-isolation;
  - half-hourly-dependency;
  - running-total-order;
  - scope-evidence;
  - the two commons gates;
  - with 1 or 2 events, all unclear or not refusals: status-honesty and file-scope-generated-paths.

  A gate that never refuses in 30 days is dead, redundant or deterring, and refusal records alone cannot tell which.
  Agents pre-run the cheap gates, as CLAUDE.md tells them to, which hides deterrence. The test that separates them
  is the one this repo already uses: plant each gate's own defect and see whether *another* gate also refuses it.
  If one does, it is redundant. If none does and nothing has been refused, it is a deterrent or dead weight.
  **I propose no retirement on this evidence.** A retirement needs that test first, and it goes to
  `for_the_director` once it has been run.
- **On the mothball-audit trigger.** This reconstruction could be its standing trigger only if its source lasted.
  Transcripts expire in about 30 days, and the publisher's own records named no gate in 13 of 13 refusals. As
  things stand, a three-month look cannot be repeated. Whether to keep a durable per-gate refusal record is a
  question for the review. Keeping one would be a new mechanism, so I have not built it.

## Reproducing this

The scripts are outside the repository, in `/var/tmp/gate_review/`, as one-off measurement scaffolding:
- `scan_refusals.py` builds the events;
- `canon.py` maps raw tags to gates;
- `sample.json` and `verdicts.json` hold the judged sample, with each verdict's reason;
- `observables.py` and `analyse.py` produce Section 1, with full output in `sec1_full.txt`.

They are not committed, so they will not outlive the machine's `/var/tmp`. Every definition they use is stated
above, so the tables can be rebuilt from git and the transcripts while the transcripts last.
