# Where reading tokens go: always-loaded context and shell output, and no few files dominate

**Written 2026-11-14 by a worker tick.** Direction item `reading-token-measurement-released-2026-11-14`.
Steer: `docs/staging/advisor/done/DIRECTOR_STEER_MEASURE_WHERE_READING_TOKENS_GO_BEFORE_SPLITTING_ANY_FILE_2026-11-07.md`
("Measure it"). Released 14 Nov by `DIRECTOR_RULING_RELEASE_THE_READING_TOKEN_MEASUREMENT_FROM_BEHIND_THE_EXIT_TEST_2026-11-14.md`.
This is measurement only: it splits no file and moves no rule.

**Re-run:** `python3 -m tools.tick_burn_rate --reading 2026-11-07T06:00 2026-11-14T06:00`.

## What is counted

- **Window:** 7 Nov 06:00 to 14 Nov 06:00 UTC. It covers 22,150 API calls across every session and
  subagent transcript of every seat kind. Each message is counted once, by its id.
- **Context tokens** = fresh input + cache write + cache read, summed per call. Over the window that is
  45k fresh input + 50.0m cache write + 2,112m cache read. Output was 12.6m. **Cache read is 98% of
  context tokens by count.** Each class is given in its own unit. Nothing here is a share of the
  allowance, and the allowance is not estimated.
- **What a read costs.** A tool result is cache-written once, on the next call. It is then cache-read
  by every later call in the same context, until a compaction. The tool found 3 compaction drops in
  the window.
- **Tokens per character** were measured from the same transcripts, not typed in: **0.416**
  (quartiles 0.392–0.448). The fit uses 329 call gaps that each added at least 20k characters of tool
  result.
- **The classes overlap and do not sum.** They are disjoint only in the attribution check below.

## The answer, ranked by share of the week's context tokens

| Class | Share |
|---|---|
| All shell (Bash) output | **39.1%** |
| Always-loaded: the first call's whole context (system, tools, CLAUDE.md, memory, prompt), carried by every call | **37.0%** |
| … of which `CLAUDE.md` | 9.8% |
| … of which the opening prompt (a tick's drawn work, a seat's charter) | 4.9% |
| … of which the `MEMORY.md` index | 1.1% |
| Shell file reads (cat/head/tail/sed) | 16.6% |
| Search/census done in an Opus context | **12.5%** |
| Search/census done in a Haiku/Sonnet context | 0.1% |
| Repeat reads across sessions (35 files, each read in 10 or more sessions) | 7.2% |
| Python runs' output (tools, daemons, inline scripts) | 4.9% |
| A file re-read within one context | 2.9% |
| Whole-file reads (Read with no offset/limit, or a bare `cat`) | 2.0% |
| The Read tool, all results | 1.6% |
| Generated data (observability, site/data, market feeds, JSON) | about 0.4% |
| Path-scoped rules | 0.2% |
| *Remainder: the model's own output carried forward, and attachments* | 21.6% |

**Per seat kind** (the route table in the tool output):

- **seat_executor and worker_tick** look alike. Shell output is 40–41%, the first-call context
  35–37%, and Opus search/census 13%.
- **delivery_seat** is 77% first-call context. Its turns are short, so the fixed load is most of what
  they carry.

## The steer's three questions

1. **Reading against writing and reasoning.**
   - Tool results are at least 41% of context tokens. Most of that is shell output, because the seats
     read through Bash, not the Read tool.
   - The fixed context is 37%.
   - The model's own output, carried forward, is about 22%.
   - Output tokens are 12.6m, against 2,162m context tokens.
2. **The files read most often and at greatest cost** (Read plus single-file shell reads, each file
   under one name across worktrees):
   - 1,588 distinct files together account for 16.6% of context tokens.
   - The costliest is `simulation/arrears_engine.py` at 0.89%. The top five are 2.8%, the top fifteen
     5.3%.
   - `docs/direction/DIRECTION.yaml` was read in 66 sessions, and the correctness ruling in 77.
3. **Do a few files dominate? No.** Under the steer's own clause 3 that is a full answer: **no split
   is proposed.** Splitting the five largest files would reach at most 2.8% of context tokens, before
   the cost of the split.

## What the numbers do name (for the director to choose from; nothing is changed here)

- **The fixed load is the largest single lever:** 37% of all context tokens, carried by every call.
  - CLAUDE.md alone is 9.8%.
  - The drawn opening prompt is 4.9%. This tick's doorbell, for example, carries the whole staging
    list.
  - The rest, about 21%, is the system prompt, tool schemas and listings, which this repo does not
    control.
  - These are the held reading-cost steers' subject, and this measurement names them. Trimming them
    is their call, not this one's.
- **Search and census run almost entirely in Opus contexts:** 12.5% of context tokens, against 0.1% in
  Haiku/Sonnet subagents.
  - **Caveat.** A subagent pays its own first-call context, about 36k tokens a call on average here.
    So moving a small grep out is not a saving.
  - Only a census with a large output, read once and not needed again, is worth delegating.
- **Cross-session re-reading is 7.2%.** The same 35 files are read fresh by most sessions.
- **These are small and not worth a mechanism:** re-reads within one context (2.9%), whole-file reads
  (2.0%) and generated data (0.4%).

## Limits

- "Whole-file" means no excerpt was asked for. Whether an excerpt would have done is a judgement this
  tool does not make.
- A shell command is classed by its first verb. A shell read is tied to a file only when it names
  exactly one file.
- Generated data in shell output is counted only on lines that start with a generated path. A
  `python3 -m` dump of a JSON store is counted as a python run, not as generated data.
- Thinking tokens that are not carried forward make the per-character ratio, if anything, low.
