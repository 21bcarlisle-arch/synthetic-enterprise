# [PLANNER-MINTED / GOVERNANCE] — Finding severity, class consolidation, blocker precedence, the armed interleave, and named ageing (2026-08-12)

**Provenance:** processing `DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12.md`
(`f3b86b07a`, clause 5 appended in `2d9c5193f`) as a mint source, per §2+§4 of
`DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`. One atom per named deliverable in the
ruling's own `WORK THIS CREATES` block, plus one for clause 5, which carries its own exit test.

**Coverage checked before minting, not assumed:** no existing atom in `docs/design/maturity_map.yaml`
and no existing `PLANNER_MINTED_*` document covers any of the six. `grep` for
`severity|interleave|consolidat` over the map returns only unrelated prose (an Expert-Hour finding's
use of the word "severity", the `AO5`/`AO6` code-consolidation atoms). The superseded count-based
trigger from `DIRECTOR_PRIORITY_BACKLOG_TRIAGE_AND_INTERLEAVE_2026-08-10` was never minted either.
**All six are therefore NEW mints; none is a re-mint.**

## Deliverable → atom

| # | Deliverable (ruling's words) | Atom | Lane | Level | Deps |
|---|---|---|---|---|---|
| 1 | The severity field, applied across the existing staging root — one pass, every finding classified | `OPS9_finding_severity_field` | H_harness | 0 → 2 | — |
| 2 | Class consolidation for the five named families, with instance lists and cumulative cost | `OPS10_finding_class_consolidation` | H_harness | 0 → 2 | OPS9 |
| 3 | The lane-level refusal mechanism for BLOCKING findings, provably failable | `OPS11_blocking_lane_refusal` | H_harness | 0 → 2 | OPS9 |
| 4 | Blockers wired ahead of the disposition queue | `OPS12_blockers_ahead_of_disposition` | H_harness | 0 → 2 | OPS9 |
| 5 | The interleave armed and its draws visible in the tick digest | `OPS13_product_interleave_armed` | H_harness | 0 → 2 | — |
| 5b | **Clause 5** — anything untouched 72h in the staging root is named daily with its age | `OPS14_aged_staging_named_daily` | H_harness | 0 → 2 | — |

`OPS9` is the spine: three of the other five read the severity it parses, so it is the only one with
downstream dependants and it draws first. `OPS10`, `OPS13` and `OPS14` are independent of each other.

## Two things found while minting, carried into the atoms' exit criteria rather than fixed on sight

**1. The daily digest can already go quiet, which is clause 5's named failure mode.**
`background/sanity_daemon.py::_maybe_send_daily_digest` fires at most once per UTC date **and**
returns without sending when any new finding fired its own NTFY that cycle (deliberate, 2026-07-11:
"an alarm that repeats unactionably trains me to ignore all alarms"). Under that code an aged-document
line is dropped for the day whenever the daemon has something newer to say — exactly the digest that
"can go quiet while old documents remain" the ruling forbids. `OPS14`'s exit criteria name this branch
and require the ageing block to be non-suppressible by it, rather than leaving the new clause to
inherit an existing suppression path.

**2. `mtime` is not a usable clock for "untouched" on this tree.** Concurrent daemons rewrite files in
the shared working tree continuously (107 modified paths at this tick's start, almost all daemon
exhaust), so a document nobody has opened can carry a fresh mtime. `OPS14` therefore requires
"touched" to mean a real disposition event — the last commit touching the path, or an explicit
disposition record — and requires that choice to be tested against a file a daemon rewrote without
anyone reading it.

Both are queued as exit criteria, not fixed here, per `SELF_INTERRUPT_DISCIPLINE` (queue by default;
interrupt only when the machine is blocked — it is not).

## Registration

Six atoms appended to `docs/design/maturity_map.yaml` (287 → 293), written under `tree_lock`.
`tests/design/test_maturity_map_contract.py` + `test_maturity_map_facets.py`: **36 passed**.

The value-stream hygiene control (C3, the default-dumping-ground check) **refused all six on first
run** — working as designed, since a ruling absorbed in one pass is exactly when the default slips in.
Each is classified in `REVIEWED_CLOSE_TO_LEARN` with its own reason: all six act on how the machine
reads its own findings and what it may build on top of them; none prices, bills, meters or settles
anything. `OPS13` schedules product work but builds none, so filing it under `meter_to_cash` or
`price_to_bill` would claim a revenue flow the atom does not touch.

Map size after the append: 393,123 bytes against the 409,600 ceiling — `tools/size_ratchet_gate.py`
exits 0, so `H41`'s drain is still holding and this mint did not re-red it.

## What this mint does NOT do

- It does not classify any existing finding. That is `OPS9`'s own build (deliverable 1 is a pass over
  ~103 documents, not a side-effect of registering the atom that performs it).
- It does not consolidate any family. `OPS10`.
- It does not enforce clause 2 or clause 3 yet. Until `OPS11`/`OPS12` land, the refusal and the
  precedence are prose, which by `MAKE_IT_STICK` means they will decay — that is the reason those two
  are minted at all rather than absorbed as policy text.

— Planner mint, from `DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12`, 2026-08-12.
