# [WORKER-REPORT] OPS13 — the product interleave is armed, and the pair it drew is named every tick (2026-08-13)

**Severity:** RECORDED · **Lane:** H_harness · **Status:** the mechanism is landed and proven both
ways; nothing here is owed.

**Atom:** `OPS13_product_interleave_armed` **L0 → L2**, self-certified into
`gate_authorizations.jsonl` (R16). Deliverable 5 of the WORK THIS CREATES block in
`DIRECTOR_RULING_FINDING_SEVERITY_AND_INTERLEAVE_2026-08-12`, clause 4 — the last of the five.

## What landed

The interleave was prose. Clause 4 armed it "NOW, UNCONDITIONALLY" on 2026-08-12; until this tick
nothing in `background/` read the word. It now lives in the three-lane draw:

- **`_apply_product_interleave()`** runs on every grant, after the fork-budget cap (so it sees the
  grant that is actually going out) and before the per-lane counts are logged (so those counts
  report the post-interleave truth). It reads three things and nothing else: what this grant drew,
  what the previous grant left owed, and clause 2.
- **`_product_side_draw()`** fills the product side by running the **real** BUILD and DISCOVER/FRAME
  draws with a narrowed picker, so dependency-met, externally-blocked, build-in-progress,
  unmerged-work, coupled-triad and anti-livelock filtering all stay in one place. A second copy of
  that ladder is how a draw filter drifts out of agreement with the draw it mirrors, and this
  project has filed that class before.
- **`product_interleave_digest_line()`** renders one line that `find_work()` logs **every cycle,
  before any of its returns** — paired, violated, armed-and-found-nothing, clause-2 substituted, or
  no atom drawn at all.

## The trade, stated because it is one: the interleave ALTERNATES, it does not WIDEN

`MAX_CONCURRENT_FORKS` is 1 (TOKEN BUDGET IS BINDING AGAIN, 2026-08-03 — SERIAL BY DEFAULT, because
cache-read volume is the bill and every extra concurrent context stream re-reads its whole context
each turn). Adding a second fork every time a harness atom draws would buy the pairing with exactly
the spend that ruling cut. So the product atom **takes the slot**: a harness-only grant records the
harness atom as OWED, and the next grant's product side is forced, with the displaced harness atom
simply not granted that cycle (it was never drawn, so it is not owed). Where width genuinely exists
the pair is drawn in the same grant. One product atom per harness atom either way — the ruling's
ratio holds; only the concurrency doesn't move.

The arm fires on **free width or on a debt**, never on every harness grant. The first
implementation displaced every time, and the live check against the real map caught what that
means at fork budget 1: the product side always wins and the harness side never draws — 0:1, not
1:1 (`SITE2_two_sided_wall_exhibit` displaced by `EP7_adapter_elexon_insights` with nothing owed
either way). Re-verified live over three consecutive draws after the fix: **harness
(`SITE2_two_sided_wall_exhibit`, violation named, owed 1) → forced product
(`EP9_adapter_n3rgy_consented_metering`, slot taken, owed 0) → harness
(`KNIFE3_wall_crossing_paydown`, owed 1)**. The alternation, on the real map, not a fixture.

An idle/parked product atom is legitimate product-side work, but it is drawn into the **DISCOVERY**
lane and never BUILD — otherwise the pairing rule would order BUILD code on an epoch-gated atom to
satisfy itself.

## Exit criteria, each with the test that would go red without it

| # | Criterion | Evidence |
|---|---|---|
| 1 | Arm unconditional; no staging-depth term survives | `test_r15_the_arm_does_not_move_with_staging_depth` runs the same grant at **0 and 200** staging documents and asserts the granted atom list AND the rendered line are identical |
| 2 | Per session; an unpaired grant is NAMED, not quiet | `test_two_harness_atoms_and_no_product_atom_is_named_a_violation` (the criterion's own example) + `test_the_owed_harness_atom_forces_the_next_grants_product_side` (the pairing is MADE, not just reported) |
| 3 | The digest carries the pair actually drawn | `test_the_digest_names_the_pair_actually_drawn` (record equals the post-arm grant, not the pre-arm intention) + `test_a_clause_2_blocker_takes_the_product_side_slot_and_is_named` |
| 4 | Silence is the failure | `test_the_digest_line_is_never_empty_on_any_path` (renderer) + `test_r15_the_digest_line_can_never_be_suppressed` (call site, through the real `find_work`, on all three shapes of cycle) |
| 5 | R15 both ways | mutations A and B below, run against the real module |

**Per grant is stricter than per session.** A grant is one drawn doorbell and one worker invocation
— the finest boundary the supervisor actually has — so enforcing the pairing per grant enforces it
per session by construction, and it makes the criterion's own example directly checkable.

## R15 — the mutations were RUN, not asserted

| Mutation | Result |
|---|---|
| **A** — re-couple the arm to a document count (`if len(list(STAGING_DIR.glob("*.md"))) >= 20: return record`) | kills `test_r15_the_arm_does_not_move_with_staging_depth`, **1 failed, 15 passed** |
| **B** — the `find_work` digest-line log replaced with `pass` | kills `test_r15_the_digest_line_can_never_be_suppressed`, **1 failed, 15 passed** |
| **C** (extra) — `record["violation"] = False`, unpaired grants pass quietly | kills the violation test, the alternation test and the harness-blocker direction, **4 failed, 12 passed** |

Each mutation was applied to the real `background/supervisor.py` and the file restored
byte-identical from a backup afterwards (`diff -q` clean each time). The whole file is 16 named
tests, all green.

## What this proves and what it does not

**Measured live population at landing:** `python3 -m background.finding_severity` reports **99
documents, 0 BLOCKING, 55 LATENT, 44 RECORDED, 0 UNCLASSIFIED**. So the clause-2 substitution path
lands **quiescent** — it is proven on synthetic populations only, and the first real BLOCKING
finding in a product lane is what will exercise it in anger. Same caveat OPS11 landed with, for the
same reason.

**The withdrawn trigger is struck at its source too.**
`docs/staging/in_progress/DIRECTOR_PRIORITY_BACKLOG_TRIAGE_AND_INTERLEAVE_2026-08-10.md` carried the
`<20 files then auto-arm` condition as its parking reason; it now carries the withdrawal at the top.
Its **drain is still live work** — only its role as the interleave's gate is gone.

**Two isolation leaks found and closed on the way**, because this is the sixth instance of a class
`tests/background/conftest.py` already documents five times:

1. The first run of the new file wrote synthetic atom ids into the **live**
   `docs/observability/.atom_stall_tracker.json` and the tests then read each other's writes (two
   draws of the same product atom flagged it stalled; the next test's arm found nothing to draw).
   The new file's autouse fixture redirects the tracker.
2. The owed ledger leaked the other way, directory-wide: `test_supervisor_blocker_precedence.py`
   exercises the draw, so it wrote `{"owed": ["H1_test_atom", "H1_test_atom"]}` into the live
   `docs/observability/.product_interleave_state.json`. `tests/background/conftest.py` now pins that
   path to an absent tmp file for the whole directory (the sixth entry in that fixture), the live
   file was deleted, and a re-run of the three relevant suites leaves it absent.

**HEAD was already red on a control this landing had to repair to get in.** The first gate run
refused the commit on `tests/design/test_simplifications_store.py::test_counts_match_file_contents`.
It reproduces on a **pure HEAD checkout**, with nothing of mine in it:
`H27_payment_belief_gap: map simplifications_count=28 != store file count=26` and
`D33_the_collapse_predicate_is_bit_equality: map declares simplifications_count=1 but has no store
file`. Both are the unlanded-evidence class — a lane bumped the count in the map, landed that, and
left the store files untracked on disk. A third (`H_GAP`, 42 vs 41) appears only in the commit tree,
because the map's H_GAP hunk is a concurrent lane's staged half riding this pathspec. The repair is
to land the artefacts the map already claims: `D33_…yaml`, `H_GAP_…yaml`, and the three archive
rolls (`H27_…017/018`, `H_GAP_…014`). Verified by building the resulting tree in a HEAD worktree and
running the four store/map suites there: **82 passed**.

**Left as a finding, not fixed on sight** (SELF-INTERRUPT DISCIPLINE): the stall tracker is still
NOT isolated directory-wide, and this tick removed **ten** non-map ids from the live file
(`H1_test_atom`, `B1_test_atom`, `OPS_surgical_landing_tool`, …). Pinning it in the conftest would
enlarge candidate sets in tests that currently run against real stalled state, so it wants its own
draw rather than a drive-by.

**Not done, deliberately.** The owed ledger is not validated against the map — a phantom id costs at
most one extra forced PRODUCT draw before it pays off, which is the direction the ruling wants erred
in. And the interleave line is logged to the tick log rather than appended to the returned doorbell
string, which would have broken the byte-preserved lone-BUILD-atom message that existing NTFY/log
parsing depends on.

## The five deliverables of the ruling are now all landed

OPS9 (severity field) · OPS10 (class consolidation) · OPS11 (lane-scoped refusal) · OPS12 (blockers
ahead of the disposition queue) · **OPS13 (the interleave, this one)**. Clause 5's OPS14 (72-hour
ageing named daily) landed alongside them.

— Worker tick, 2026-08-13.
