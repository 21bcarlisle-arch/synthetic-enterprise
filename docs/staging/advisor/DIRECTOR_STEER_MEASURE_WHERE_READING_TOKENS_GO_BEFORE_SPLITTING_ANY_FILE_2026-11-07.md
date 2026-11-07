**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Measure where reading tokens go before splitting any file (2026-11-07)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sat 7 Nov:

- 06:18 GMT: "Do we use abstractions? Would it help with token efficiency?"
- 06:19 GMT, on the advisor's recommendation to measure first and refactor only where the numbers say: "Measure it"

**When:** behind the correctness exit test. Rank it yourself.

## What the advisor found (as of `482b50dee`, 5 Nov; check it)

- **About 1.2m lines of Python:**
  - `company/`, `saas/`, `sim/` and `simulation/`: about 210k;
  - `background/` and `tools/`: about 332k;
  - `tests/`: about 618k;
  - `site/`: about 33k.
- **Single files of extreme size:**
  - `tools/generate_value_arms_data.py`: 18,431 lines;
  - `tools/couple_w2_11_d5.py`: 14,976;
  - `tests/tools/test_generate_value_arms_data.py`: 14,045;
  - `background/process_run_complete.py`: 11,600;
  - `saas/reporting/annual_report.py`: 11,325.
- **Abstractions already in use:**
  - the seam (`company/interfaces/sim_interface.py`);
  - `tools/capability_index.py`;
  - skills;
  - the memory index cut to pointers on 23 Oct, which halved opening context;
  - the map register.

## The question

**Where do the tokens spent *reading* go, and would narrow, tested interfaces on a few files pay back?**

1. **From your own session records, measure:**
   - the share of tokens spent reading files against writing and reasoning;
   - the files read most often and at greatest cost;
   - how much of each big file a typical session actually reads.

   Say what each number counts: per session, per turn or per route.
2. **Only if a few files dominate, propose splitting the worst ones** behind small interfaces. Each interface has a short description of what it promises, and a check that proves the description true, so an agent can rely on it without reading the body. If the description cannot be trusted, agents read the body anyway and nothing is saved. Give the expected token saving and the one-off cost of the split.
3. **If reading is not where the tokens go, or no few files dominate, say so and stop.** That is a full answer.

## Not wanted

- No refactor before the measurement.
- No change to behaviour. A split is mechanical and proven by the existing tests.
- No new gate.

## Risk

Touches: a read of session records, and later only the files the numbers name.
Blast radius: none until a split is proposed and done. A split of a hot file such as `process_run_complete.py` touches the publish path, so prove it on the existing tests and one publish.
Probable failure mode: counting a cached re-read of a file as if it were a fresh read, or the reverse, which would overstate or understate the saving. Separate cached tokens from fresh tokens.
Proportionality: reversible and narrow — just do it.

— Director steer, 7 Nov 2026, his words above; the census and drafting are the advisor's.
