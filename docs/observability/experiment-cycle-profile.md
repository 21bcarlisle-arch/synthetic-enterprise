# Experiment-cycle profile + Epoch-4 feasibility gap (COMPOUNDING_WORK_FIRST.md, MEASURE FIRST)

**Measured 2026-07-13. R4: measured, not guessed.**

## Where the time actually goes (one inner-loop experiment cycle)
| Stage | Cost | Source |
|---|---|---|
| **Full sim run** | **~500s** (this marker) – 594s (recent) ≈ **8–10 min** | run_complete marker `Duration:` field |
| Full test suite | **17,671 tests**, ~133–183s (fast mode) | live collect + observed runs |
| Publish pipeline (regen + gated test + commit) | ~3–5 min (test-gated) | process_run_complete |
| **Dominant term: the sim run.** The suite is the second term; publish rides the suite. |

## The Epoch-4 feasibility gap (the number = the size of the problem)
Epoch 4 (the evolutionary tournament) needs the company to **live and die many times** —
N variants × G generations = N·G "lives", each life = one full sim run.

- At **500s/life, single-threaded**: 1,000 lives = 500,000s = **5.8 days ≈ a week — PER GENERATION** (director's arithmetic, confirmed).
- A *modest* tournament (100 variants × 20 generations = 2,000 lives) = **~11.6 days of pure sim wall-clock**.
- A *meaningful* one (200 × 50 = 10,000 lives) = **~58 days**.

**Target, working back from "a 10,000-life tournament within one week" (168 h):**
required cycle time = 168·3600 / 10,000 = **~60s per life**.
**GAP: 500s → ~60s = ~8–10× too slow** (single-threaded). Equivalently, ~8–10× effective
parallelism, or any product of the two. **The evolutionary tournament is arithmetically
impossible at today's cycle time; ~10× is the size of the problem.**

## The biggest lever (and why it belongs to ARCH1)
The ~500s is a FULL sim run. For inner-loop company testing, a **typed wall interface
(ARCH1) lets the company be tested against a MOCKED interface** — no full sim run — cutting
the inner loop from ~500s to **seconds**. Same work, three returns: modularity, parallelism,
fast tests. Design the mock as a first-class ARCH1 citizen from day one.

Secondary levers (weigh after the mock): parallel sim execution; caching deterministic stages;
tiered test selection (full suite only at integration — already partly decided); a reduced-fidelity
fast-mode for inner checks.

## Non-negotiable (enforce mechanically, fail-closed)
A fast-mode / mocked-interface run is a DEVELOPMENT tool: it may **never** publish, promote an
atom, or feed the board pack. Cycle time is a DIAGNOSTIC, never a target gamed by deleting tests
(R15 stands — controls must still fire).
