**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `H15_publish_gate_failure_alert`

## Class registration

Belongs to `publish_gate_and_wedge`. Declared rather than left to the title regex, because the
mechanism named here is a COUPLING between two shared objects and the class's own source documents
that a mechanism-named title carries no `wedge`/`publish`/`gate` token reliably.

**LATENT and not BLOCKING, deliberately.** No instrument is lying: `tools/level_promotion_gate.py`
was right on all seventeen refusals and its verdict is untouched. The instance is discharged in
this same commit. What remains is a structural coupling that will recur, and marking it BLOCKING
would hold every level raise in `H_harness` for a hazard with no live false reading.

# A level staged in the shared map wedges every lane's publish indefinitely, because the publisher can never carry the source the declaration points at

**Found:** 2026-08-31, on the Lane 0 delivery draw sent to clear a 17.9-hour publish wedge
(17 consecutive refused episodes, `blocking_tests: []`, `total_red: 0`).

Born archived: `publish_gate_and_wedge` is an existing class with 53 instances. This is the 54th,
and unlike most of them it is not a defect in the gate. **The gate is right. The wedge is
structural, and this document names the structure.**

---

## The instance

`docs/observability/.publish_gate_state.json` at the moment of the draw:

```json
{"blocking_tests": [], "cited_findings": [], "episode_failures": 16,
 "red_census": "fail_fast_only", "total_red": 0, "wedge_since": 1788067679.7378433}
```

That tell — an accusation with no accused — is this class's own signature and my memory names it:
*any publish path that fails WITHOUT running the suite is filed as `test_regression` by default.*
So the refusal was not a red. It was in `docs/observability/sim-runner-log.md`, verbatim, at four
separate cycles (lines 216167, 216280, 217037, 217184) and again at 23:43Z as episode 17:

> §0: level_current 0->2 on `PB3_book_growth_as_earned_outcome` declares a level for source this
> commit does NOT contain -- its file_scope holds program text that is not landing:
> `simulation/run_phase2b.py`

`tools/level_promotion_gate.py`'s SECOND control, built 2026-08-10 after three instances in three
days of a level being declared for code no commit held. Its predicate is the porcelain **Y**
column over `file_scope`, scoped to source suffixes. Reproduced exactly, at the draw:

```
file_scope: ['simulation/net_new_acquisition.py', 'simulation/run_phase2b.py',
             'tests/simulation/test_net_new_acquisition.py',
             'simulation/market_switching_propensity.py',
             'simulation/acquisition_funnel.py', 'simulation/live_population.py']
dirty source: ['simulation/run_phase2b.py']
```

One file. **And it is not PB3's work.** `git diff` on it is 160 lines of another lane's in-flight
C1b: an SVT-inertia departure branch, plus the `tariff_type=c.get(...) or "fixed"` repair. Neither
is acquisition. `run_phase2b.py` is simply large enough to appear in many atoms' `file_scope`.

## Why "land the source instead" was refused, and it was measured, not judged

The obvious move is to land `simulation/run_phase2b.py` in its own commit and let the declaration
stand. That was checked against HEAD and it is an ImportError:

| symbol the in-flight `run_phase2b.py` imports | defined at HEAD? | defined in |
|---|---|---|
| `DEPARTURE_OCCASION_SVT_SEGMENT` | **no** | `simulation/customer_events.py` (dirty, unstaged) |
| `inertia_hazard_for_term` | **no** | `simulation/svt_product.py` (dirty, unstaged) |
| `departure_event`, `CAUSE_SVT_INERTIA`, `DECLARED_SENSITIVITY_SCALE`, `year_level_anchor` | yes | — |

Both missing definitions live **outside** PB3's `file_scope`, so the very predicate that demands
`run_phase2b.py` land does not demand its two dependencies land with it. Landing the one file
alone puts an ImportError at HEAD in a module imported by 200+ files, and this class already
carries `WORKER_FINDING_THE_COMMIT_GATE_SELECTS_TESTS_BUT_AN_IMPORTERROR_COSTS_THE_WHOLE_SUITE`.
The cheap-looking option was the expensive one; the table is why.

So the level was backed out to `0` in `docs/design/maturity_map.yaml`, with the reason written
beside it and a standing instruction to re-declare it in the seat commit that carries its source.
**Nothing about PB3's L2 work is retracted.** What is retracted is a claim the repository could
not reproduce, which is exactly what §0 exists to prevent.

## The structural half, which is the point of this document

Every other instance in this class is a gate that misreported, mis-scoped, or mis-timed. This one
is a **coupling between two shared objects**, and no fix to the gate touches it:

1. `docs/design/maturity_map.yaml` is a SHARED file. Any lane can stage a level move into it.
2. `background/process_run_complete.py` — the publisher — is the process that commits it, because
   the map is inside the publish pathspec.
3. **The publisher can never carry source.** Its pathspec is `site/`, `docs/`, generated state. It
   has no basis to decide that another lane's half-finished `simulation/*.py` should land, and it
   would be a wall violation of the worst kind if it did.
4. Therefore a level move whose `file_scope` touches ANY file another lane is mid-edit on is a
   refusal the publisher **cannot ever discharge by retrying**, and it re-fires every cycle.

The consequence that makes it worth a class entry rather than a fix note: **the wedge is not
clearable by priority.** The self-refilling draw ranks work; this item's blocker is not a piece of
work that was ranked too low, it is a commit the ranked process is structurally incapable of
making. Seventeen episodes over 17.9 hours is what "however high its priority" looks like on the
clock. The previous direction's argument — that a worker tick already held the wedge at rung 1,
priority zero, so a second writer would be redundant — was a mechanism argument, and the sixteen
refusals that followed refuted it.

**Where the refusal belongs instead: at the WRITER, not at the publisher.** §0 already refuses in
two places for exactly this reason (`record_level_up_self_certified` and the gate) because "the
ledger row and the map move are separate acts, sometimes days apart". This is the third act in
that sequence — the map move and the COMMIT are also separate acts, and the mover is not the
committer. A level move should not enter the shared index at all unless the mover is in the same
turn committing the source it declares. That is the mechanism this finding owes; it is named here
rather than left to be rediscovered as instance 55.

## Reversibility

`git show HEAD:docs/design/maturity_map.yaml` holds the `2`. Re-declaring is a two-character edit
plus the source commit the gate has been asking for all along.
