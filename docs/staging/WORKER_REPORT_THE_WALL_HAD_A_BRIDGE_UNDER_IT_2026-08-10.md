# KNIFE3 step 8 — the wall had a bridge under it (72 → 75 crossings, and that is the result)

**Severity:** RECORDED · **Lane:** W4_the_wall

**Lane:** `KNIFE3_wall_crossing_paydown` (AO5 pass 3 of 4), level deliberately still 0 of 2.
**Register:** `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` §3b
**Plan:** `docs/design/KNIFE_HOTSPOT_PASSES.md` § Pass 3, step 7

## The one-line version

The crossing count went **up**, 72 → 75, because three crossings existed that no instrument in
this programme could see. This tick cut nothing on purpose.

## What was wrong

`tools/epistemic_wall.py` has carried this sentence since the step-1 extraction:

> *routing a dependency through a package the walker does not walk (`tools/`) moves the
> measurement rather than the dependency, and ... KNIFE pass 1 refused that move.*

True, correct, and **never measured**. Nothing had asked whether the tree already contained such a
route. It did — three, all class (b), all leaving `simulation/run_phase2b.py:95`:

```
simulation.run_phase2b -> company.billing.account_ledger
simulation.run_phase2b -> company.billing.arrears_engine
simulation.run_phase2b -> company.billing.payment_observation_consumer
```

reached through `background.live_payment_triad` and `tools.couple_w2_11_d5`. Invisible to the
ratchet, absent from the KNIFE ledger, and absent from the register that claims to examine every
crossing. **A hazard named in prose and left unmeasured is R15's third killer pattern** — the check
that passes because nobody ran it.

## Why the instrument had to land before the cut, in a commit that cuts nothing

`A_composition_lift` is the 65-edge bulk of what remains. It moves thin scenario harnesses out of
`simulation/` and above both layers — which in this repo means into `tools/`. That is a **cut**
only if nothing walked still reaches the company through the moved file; otherwise it is exactly
the laundering the register refuses in writing (§2b). The pass could not honestly make that move
while `tools/` was an unmeasured channel. So the instrument lands alone, direct allowlists
byte-unchanged — step 1's rule applied to its own consequence.

## Proven able to fail, on the real tree

A laundered route injected into `simulation/settlement.py` through a throwaway `tools/` module
reds exactly three tests in the new module (`test_no_new_indirect_crossings`, the frozen census,
and the per-bridge verdict for `tools` — `background` and `interface` stay green), **while
`test_epistemic_wall_ratchet.py` passes 12/12 on the same injected route**. That green direct
ratchet is the measurement, not the argument, for what was missing. Second mutation: dropping
`background` from the census reds the census-coverage test.

## Three things the build itself turned up

1. **The shortest chain is a redundant-channel trap.** Every one of the three is carried by
   **both** bridges, so cutting the one route a checker printed removes nothing and reads as a
   failed cut. `IndirectEdge.entries` now names every entry point; one test pins the property, a
   second pins today's concrete redundancy so its disappearance is a visible event.
2. **The union hid a fail-open the moment it was introduced.** `measure_crossings` with an empty
   direct walker still returned 3, so the "ZERO crossings is a failure" guard stopped firing on
   it. Neither source may be refused for being zero alone — an empty indirect set is this pass's
   *goal state* — so the guard stays on the total and the **breakdown** is printed
   (`72 direct, 3 indirect`). Caught by the existing suite going red.
3. **A mutation point had drifted off the live code path.**
   `test_main_returns_nonzero_when_an_edge_is_unexamined` patched `measure_crossings` while `main`
   had moved to `measure_crossings_split`. It failed loudly rather than passing green against a
   ghost it was no longer injecting.

## What is now true

| Instrument | Before | Now |
|---|---|---|
| ratchet (GATE) | 72 direct | + `test_epistemic_wall_indirect_ratchet.py`, 20 tests, own dated shrink-only allowlist |
| register (EXAMINATION) | 88 rows / 72 live | 91 rows / 75 live |
| KNIFE ledger (REPORT) | `75 edges` | `75 edges`, `72 direct + 3 indirect` |

**Class (a) via a bridge is at ZERO** — measured here for the first time, not inherited. `interface/`
is in the census despite the ratchet's standing claim that it "cannot host a wall edge nor launder
one": that claim was about *direct* edges and had never been tested for indirect ones. It holds, by
measurement now, and every bridge gets a named verdict so a clean one is explicit rather than silent.

## `A_composition_lift` is unblocked, and its per-file measurement is taken

AST census, not grep (the mentions in `run_phase1c_full_window` / `1c_renewals` / `1d` / `4c` are
docstrings, not imports):

* **Nine of the ten** shape-A harnesses have **zero importers anywhere inside the wall**.
* Only `run_phase2b` has walked in-edges (`run_scenario`, `run_phase3a`, `run_phase4b`, `run_phase4c`).
* Seven are 75–153 line files that are `main()` plus its private helpers.

That criterion — *a lift is a cut iff nothing walked still reaches the company through the moved
file* — **derives §2b's own refusal for `run_phase2b`** rather than contradicting it, which is why
it is worth trusting. The next step is those seven, 16 edges, under the instrument that can now
tell the difference.

## One thing queued, not fixed (SELF_INTERRUPT_DISCIPLINE)

`python3 tools/epistemic_verifier.py` raises `ModuleNotFoundError: No module named 'tools'` — the
file has no `sys.path` insert and imports `tools.epistemic_wall`. **Pre-existing at HEAD, and not
live**: every caller in the repo (`.claude/settings.json`, both `.claude/rules/` files,
`background/worker_seat.py`) uses `python3 -m tools.epistemic_verifier`, which works. Latent only,
recorded rather than fixed on sight.

## Evidence

* `python3 tools/wall_crossing_dispositions.py` → `75 live crossings (72 direct, 3 indirect via a
  bridge package); 91 ruled (cut 16, owed 75, grandfathered 0)` — **OK**, rc 0.
* `--at-head` → identical, **OK**, rc 0.
* `python3 tools/knife_hotspot_measure.py` → `wall_crossings 14 files (-19 vs baseline) 75 edges`,
  note `72 direct + 3 indirect`; **KNIFE LEDGER: OK**.
* `tests/architecture/` 60 passed. Combined run (architecture + the three `tests/tools/` wall
  modules + `tests/controls/`): **320 passed, 1 xfailed**, rc 0.
* `python3 -m tools.epistemic_verifier` **PASS**, 539 `company/`+`saas/` files.
* Ruff `I001` fixed at source, never by raising the frozen baseline.
