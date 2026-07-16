# H18 — Harness-self mutation audit (FRAME)

**Atom:** `H18_harness_self_mutation_audit` · lane `H_harness` · dial 3 · level_target 2
**Loop stage:** FRAME (this doc). BUILD-gated per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md
Rule 1 — no BUILD code is written by the turn that produced this artifact; the
atom **stays at L0** until its BUILD draw is opened. This FRAME defines the
work so the eventual BUILD is against a settled design, not invented at build
time.
**Provenance:** RETRO_ACTIONS_THE_THREE_GAPS.md ATOM 2 (director-approved QUEUE).
**Authored:** 2026-07-16 (Lane-3 DISCOVER/FRAME, H17 draw).

---

## 1. The gap, in one paragraph

R15 (`CONTROLS_THAT_CANNOT_FAIL.md`) says a control counts as evidence only if a
**mutation test** proves it fires on its own named defect. H12 applied that
inward as far as the **object-level** controls: the compliance invariants, the
Tier-1 gates, the R14 basis-label gate, the epistemic verifier, the Qwen
backstop (`tests/controls/test_control_mutation.py`), plus the **daemon
scheduling loops** — cadence/cooldown/backoff timers
(`tests/controls/test_daemon_loop_mutation.py`). What H12 did **not** audit is
the layer above those: the **verdict organs / meta-controls** — the components
whose *whole job is to decide whether something else is healthy, honest, or
alive*. A meta-control that cannot fail is the most dangerous control in the
stack, because everything downstream trusts its verdict as external truth (this
is the `EXTERNAL_TRUTH_WALL.md` law S0 applied to the watchers themselves: a
watcher's self-report is not evidence of the watcher working). H18 points R15
**inward at the watchers**, as a *class*, and closes it the R10 way — extend the
kill-list/mutation discipline to cover the meta-control class so the entire
class fails automatically, not one instance patched.

## 2. Scope — the meta-control class (the five named organs + the boundary)

Each row: the organ, the file, **the verdict it emits** (what downstream trusts),
and **the defect it exists to catch**. The mutation test (section 4) must prove
the organ's verdict *flips* when that defect is injected.

| # | Meta-control | File | Verdict it emits (trusted downstream) | Defect it exists to catch |
|---|---|---|---|---|
| M1 | **Dead-man's switch** | `background/deadmans_switch.py` | "the stack is making forward progress" (most-recent git COMMIT timestamp; deliberately NOT pane-inspection) | the whole stack went dark — no commits, no auto-process — and nothing alarmed (the real 22:12→04:00 blackout, director P0) |
| M2 | **Naive organ** | `background/naive_organ.py` | "this claim/plan survived an amnesiac Opus falsify" (interrogate/falsify verdict) | a self-certified claim that a codebase-blind skeptic would immediately break; also: the organ silently not running |
| M3 | **Claim hook** | `.claude/hooks/block_unevidenced_claim.py` | "this completion claim carries cited evidence" (blocks an unevidenced "done") | a "done"/"passing"/level-bump claim published with no fetchable artifact behind it |
| M4 | **Supervisor draw** | `background/supervisor.py` | "there is work to draw / the map is/ isn't blocked" (Rule-0 self-refill, `_maturity_map_draw_*`, `diagnose_map_blocked_set`) | an idle turn while atoms are available (a false "nothing to draw"), or a false "blocked" that freezes the loop |
| M5 | **Publish-gate failure alert** | `background/process_run_complete.py` (H15) | "the publish pipeline is healthy" (fires on a publish/gate failure with threshold+cooldown) | a publish gate failing silently — the pipeline stalls and no alert fires |

**Boundary with H12 (no overlap — audit this, not that):** H12 already owns the
compliance invariants, Tier-1/R14 gates, epistemic verifier, Qwen backstop, and
the *scheduling-timer* behaviour of the daemons (cooldown-stuck-open,
backoff-never-resets, loop-never-fires). H18 owns the **verdict logic of the
organs above** — the *decision* each emits, not its cadence. Where an organ has
both (M1 the deadman: its timer is H12's, its "what signal counts as progress"
verdict is H18's; M4 the supervisor: its cooldown is H12's, its draw/blocked
*verdict* is H18's) H18 takes the verdict half and cites H12 for the timer half,
so the two audits compose without double-covering.

## 3. Doctrine — the three killer patterns, aimed at a watcher

Same three patterns from `CONTROLS_THAT_CANNOT_FAIL.md`, re-read for a verdict
organ. For each meta-control the BUILD must construct all three mutants and
prove the organ's verdict does the right thing:

- **TAUTOLOGY** — the organ derives its health verdict from *the same signal it
  is judging*, so it can never disagree with it. Killer example to guard: a
  deadman that inferred "alive" from *its own last-run timestamp* rather than an
  independent progress signal (git commits) would pass forever while the stack
  is dark. Test: the health signal MUST be independent of the thing judged —
  mutate the judged thing to its failed state and assert the verdict flips.
- **FAIL-OPEN** — the organ emits the healthy verdict on missing / zero / empty /
  malformed input. Killer example: the supervisor draw returning "nothing to
  draw" (→ idle, which reads as "all done") when the map file is unreadable or
  empty, rather than raising. Test: feed empty/malformed/missing input and
  assert the verdict is the SAFE one (alarm / escalate / hold), never the
  reassuring one.
- **FAIL-SILENT** — the organ passes when *the organ itself* is unavailable (an
  unavailable check is a FAILED check, R15). Killer example: the naive organ
  reporting "claim survived" when the Opus subprocess never actually ran
  (Ollama/Claude down), or the claim hook being disabled and thereby admitting
  every unevidenced claim. Test: make the checker unavailable and assert the
  system treats it as a FAILURE (alarm on checker-unavailability), not a pass.

## 4. The BUILD deliverable (what L2 requires — specified, not built here)

A new `tests/controls/test_meta_control_mutation.py` (sibling to the two H12
mutation files), plus a **meta-control row per organ in the existing control
registry** (`docs/design/control_registry.json`) and the kill list
(`docs/design/CONTROL_KILL_LIST.md`) so the class is inventoried, not ad hoc.
For each of M1–M5, the file constructs the minimal CORRECT input, then injects
each applicable killer-pattern mutant and asserts the organ's verdict FIRES
(and, per the daemon-loop precedent, a *second* assertion that on correct input
the organ stays QUIET — so both a never-fires and an always-fires mutant die).

Concretely, per organ:

- **M1 deadman** — mutate the git-commit-progress signal to "last commit is
  stale beyond threshold" → assert alarm fires; mutate the progress signal
  fresh → assert quiet; **independence probe**: prove the alarm does NOT read
  the deadman's own heartbeat as the progress signal (the fail-silent
  regression already fixed 2026-07-14 gets a standing mutant so it can't
  regress again).
- **M2 naive organ** — stub the Opus invocation to (a) return a break verdict →
  assert the claim is flagged; (b) be *unavailable* → assert unavailability is
  surfaced as a failed check, never a silent "survived"; assert
  `is_purpose_claim()` still declines a purpose claim BEFORE any call (the LINE
  is load-bearing, mutate a purpose claim in and prove it is declined not
  falsified).
- **M3 claim hook** — feed an unevidenced completion claim → assert blocked;
  feed an evidenced one → assert admitted; **fail-open probe**: empty/garbled
  claim text must not slip through as "no claim detected → allow".
- **M4 supervisor draw** — with atoms available, mutate the map read to
  empty/unreadable → assert the draw does NOT report a reassuring "idle/nothing
  to draw" (fail-open) but raises/escalates; with a genuinely all-idle map,
  assert `route_blocking_decision` does not falsely freeze (the Rule-0 "empty
  feasible set is a DEFECT IN THE DIALS" law made into a mutant).
- **M5 publish-gate alert** — inject a publish/gate failure → assert the alert
  fires exactly once within the cooldown and re-fires after it; make the alert
  writer's sink unavailable → assert fail-closed (the H15 pattern already
  built; H18 adds the *meta* mutant that the alert cannot itself fail silent).

**Where an organ is an LLM judge (M2):** it cannot be deterministically
mutation-tested end-to-end, so per R15's LLM-judge clause it is
**outcome-tested** — a naive-organ "survived" verdict that a later stage breaks
is logged as a judge miss (`docs/observability/naive_organ_log.jsonl` already
exists as the sink); the BUILD adds the miss-counter, not a fake determinism.

## 5. Definition of done + honest level statement

- **L0→L1 (Skeletal):** the meta-control class inventoried in the registry +
  kill list; one organ (propose M3 claim hook — smallest, deterministic) has a
  passing fire+quiet mutation pair.
- **L1→L2 (Functional):** all five organs M1–M5 have their applicable
  killer-pattern mutants built and green in
  `tests/controls/test_meta_control_mutation.py`; the LLM-judge organ (M2) has
  its outcome-miss counter wired; the class is added to the standard control
  suite so a future new meta-control without a mutation test is itself flagged
  (the class fails automatically — R10 closure, not instance closure).

**Level this turn: HELD at L0.** This is a FRAME artifact only; L1 requires
BUILT, green mutation tests, which a Lane-3 doc-only turn does not and must not
produce (BUILD-gated). Nothing here claims a level move — the design is settled,
the code is not written. Coupled-triad note: H18 is itself a HARNESS-lane
control, so when built it must satisfy its own doctrine — the meta-control
mutation suite must be able to fail (a mutant of the suite that never fires is a
smell), which is why each organ gets the *both-directions* (fire AND quiet)
assertion rather than a single fire assertion.

## 6. Related laws / cross-links

- `EXTERNAL_TRUTH_WALL.md` S0 — a watcher's self-report is not evidence of the
  watcher working; H18 is the mutation-test instantiation of that law for the
  five named organs.
- `CONTROLS_THAT_CANNOT_FAIL.md` (R15) — the parent doctrine; H18 extends its
  three killer patterns to the meta-control class.
- H12 (`test_control_mutation.py`, `test_daemon_loop_mutation.py`) — the
  object-level and scheduling-timer precedent H18 sits above; section 2 states
  the exact no-overlap boundary.
- `G4_unified_failure_register` — the strike-counter that should record a
  meta-control miss as a first-class failure class once both are built.
