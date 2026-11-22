**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] A profile-first speed track for runs, gates and tests (2026-11-22)

**Type:** STEER, through the advisor channel. It runs inside the efficiency track (`docs/operations/EFFICIENCY_BACKLOG.md`). The director's words, from chat on Sun 22 Nov:

- 06:45 GMT: "This article inspired me to ask you if a similar logic could be used to target the slowest or most memory consuming part sof our code and process? To help run more accounts and more simulations and more tests more often. https://github.com/EL4CTEO/fast-anything"
- 06:50 GMT, on the advisor's recommendation below: "Yes, stage it"

## What the advisor found (check it)

**The source.** EL4CTEO/fast-anything (MIT, 13 stars): "Don't rewrite it in Rust. Rewrite the 5% that's slow." Its method:
1. Profile the whole real app and rank functions by share of time.
2. Record up to 500 real calls of the chosen function.
3. Port only that function.
4. Replay every recorded call, plus shrunk variants, until "every case matches: same values (floats within 1e-9), errors where the original errors".
5. Time the whole app, original against new, in interleaved runs.
6. Keep it switchable (`FAST_ANYTHING_DISABLE=1`).

Its own lesson: porting the outer loop beat porting a small inner function (35× against 1.9× on the whole app). The results are the author's own measurements.

**Why speed matters here, in his words:** "more accounts and more simulations and more tests more often".
- More accounts and worlds per run strengthen "survival judged worst-case over the sampled set" (23 Jul canon) and the 18 Nov ranking-validity test.
- Faster gates mean more landings a day. `background/delivery_seat.py` records a landing that "lost all 3 attempts in 2637 s: each re-cut re-ran the full gate (~880 s)".
- A faster suite means more tests per change.

**Profiling status:** the advisor found no standing profile of a run, the gate chain or the suite. A few modules mention profiling in passing. Confirm or correct.

## The outcome wanted

1. **Profile three workloads, time and peak memory, before changing anything:**
   1. a standard book run at today's account count;
   2. the full commit gate chain, gate by gate;
   3. the test suite, top files and fixtures by time.

   Use sampling profilers that need no code change: py-spy for CPU; memray or tracemalloc for memory. Record the machine state, since the WSL guest's memory moves. Rank hotspots by share of the whole workload, not by per-call cost.
2. **Fix the top one, one at a time.** For each fix:
   - **Write a prediction first:** the expected whole-workload saving.
   - **Identical results, proven.** Record real inputs and outputs of the target before changing it, and replay them after. Floats within a stated tolerance, errors where the original errors, plus the 20 Nov property tests where they apply. A speedup that changes a world result is a fidelity change, not a speedup. It is refused here and must go through R13 if wanted at all.
   - **Time the whole workload,** before against after, interleaved, with the spread over repeats.
   - **Keep it reversible:** a switch or a clean revert, named.
3. **Python first; Rust or another compiled port last.** Exhaust the cheap wins first: repeated reads, caching, vectorising with numpy, avoiding recomputation, lighter imports in gates. A compiled port is proposed only for a proven hotspot that Python cannot fix. It must say what the toolchain adds to the gates, the epistemic verifier and the REUSE rule.
4. **Report the gain in his terms,** not seconds:
   - accounts and worlds per run within the same memory;
   - landings per day at the gate time saved;
   - tests per change.

   Record each fix as a row in the efficiency backlog, with the model and CLI version per the 17 Nov steer.
5. **Feed the gate profile to the 20 Nov work.** Judging from the base, and reusing a gate verdict when the files it reads are unchanged (the ABFS idea logged on 18 Nov), both depend on knowing which gates cost what.

## Rules

- **Fidelity-neutral by construction.** Any change to a world or company result is out of scope here.
- **One variable at a time;** a whole-workload measure for each.
- **The company has no route to the real world.** Profilers run on the harness, and nothing new is fetched at runtime.
- **The sandbox profile is not widened** for profiling. If a profiler needs a privilege the machine lacks, use one that doesn't (py-spy can run without root on a child process), or say so.

## Reading-log entries to append

| Date | Source | Shared by | What we took | Verdict |
|---|---|---|---|---|
| 2026-11-22 | EL4CTEO/fast-anything (MIT): profile, port only the hot 5%, prove identical on recorded calls, time the whole app, keep it switchable | Director | The method, not the Rust: profile-first, identical-results proof, whole-workload timing. Outer loops matter more than inner functions. | ADOPT (speed track) |
| 2026-11-21 | Google, NeuralGCM docs (hybrid physics and ML global weather and climate model, arXiv 2311.07222) | Director | Too coarse for GB (~75–300 km). The real record (ERA5, HadUK, extension to ~1980) beats it for fidelity; UKCP18 for drift. Later only, behind the Met Office's UNSEEN method, for extremes beyond the record. | LATER |
| 2026-11-21 | Huang et al., AtlasKV (arXiv 2510.17934v2): billion-fact knowledge graphs injected into an open LLM's attention in under 20 GB | Director | Needs model weights we don't have, at a scale we don't need, on a GPU we lack (12 GB). | NOT FOR US |
| 2026-11-21 | Summary of Tom Blomfield's 2026 YC and Startup School talks on AI-native companies (unverified) | Director | We already embody most of it. The most valuable unrecorded knowledge is the director's own practitioner knowledge (K4). He raises the question whether a public repo gives away the moat; that is his call. | NOTED |
| 2026-11-18 | google/abfs (Apache): content-addressed sources and per-action read tracking for cached builds | Director | Reuse a gate's verdict when none of the files it read changed. Feeds the re-gating cost and item 5 above. | BACKLOG |

## Risk

Touches: profiling runs (read-only), then single hotspot fixes in harness, sim or company code.
Blast radius: per fix, the module changed, guarded by the identical-results replay.
Probable failure modes:
- **A speedup that silently changes a result.** Mitigated by the recorded-call replay and property tests; a mismatch refuses the fix.
- **Optimising a per-call hotspot that barely moves the whole run.** Mitigated by ranking on whole-workload share and timing the whole workload.
- **Profiling on an unrepresentative day.** Record the machine state and repeat.

Proportionality: harness measurement, then reversible fixes. Implement directly.

— Director steer, 22 Nov 2026, his words above; the reading and drafting are the advisor's.
