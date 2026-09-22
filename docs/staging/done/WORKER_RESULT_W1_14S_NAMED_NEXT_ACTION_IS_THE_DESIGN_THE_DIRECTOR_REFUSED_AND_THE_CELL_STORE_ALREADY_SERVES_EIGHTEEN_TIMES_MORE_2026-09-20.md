# W1_14's named next action is the design the director refused, and the cell store already serves 18x more households

**Severity:** BLOCKING
**Lane:** W1_market_weather

BLOCKING is lane-scoped and every other lane proceeds untouched. It blocks here because W1_14's
own `block_reason` ordered the next action, that action is the design the director refused in
writing, and a lane that draws this atom again before reading this will rebuild the refused thing.

Drawn 2026-09-20 as LANE 1 BUILD, `W1_14_weather_cells_for_household_heat_load`, level 1→3.
Pre-registration, written before the measurement and archived to records/ by a daemon mid-turn:
`docs/staging/records/WORKER_PREREG_W1_14_HOW_MUCH_OF_THE_HOUSEHOLD_POPULATION_THE_CELL_STORE_ALREADY_SERVES_2026-09-20.md`.

## 1. The drawn item's own instruction could not be followed, twice over

W1_14's `block_reason` names a two-step sequence: *"re-land `_has_archive` from `16a127b74`
FIRST... then pull."* Both halves are false at HEAD.

**`16a127b74` does not carry `_has_archive`.** `git grep` finds the string in that commit in
exactly one file — `docs/design/maturity_map.yaml`, i.e. the prose describing the function, not
the function. Searching *every* ref (`git log --all -S"_has_archive"`) returns three commits and
**none of them contains the implementation**. The only surviving trace of the code is a single
CALL SITE, in a test, in the *earlier* salvage `8730d1b96`:

    8730d1b96:tests/simulation/test_weather_cell_siting.py:260:
        assert resolved == customer["customer_id"] or weather_inputs._has_archive(resolved), (

The 2026-09-06 map note asserted *"Both halves of that are now mechanical instead of remembered.
`_weather_source_customer_id` steps 1 and 2 both check `_has_archive`."* That was a claim about
work sitting uncommitted in a worktree that then died; `fork_salvage` captured
`test_weather_cell_siting.py` and `weather_cell_siting.py` across two salvages and never captured
`weather_inputs.py`. **So the map recorded a repair as landed, the repair was never landed, and
the recovery instruction pointed at the wrong commit for code that is in no commit at all.**

**And the second step — "then pull" — is the design the director refused in writing.** Since
2026-09-16/17 the tree says so in two places:

- `sim/weather_world.py` carries the refusal verbatim: *"The world exists, and a property reads
  its conditions from it... Two households in the same cell must experience identical weather —
  that's what makes the difference in their demand attributable to fabric and people rather than
  to two separate downloads."*
- `simulation/fabric_demand_path.py:133` records that the remedy sentence read *"pull that
  coordinate"* **until 2026-09-17**, when it was replaced precisely because *"a refusal that names
  the wrong remedy is worse than one that names none — it recruits the reader into rebuilding the
  design."* The live remedy is `ADD_THE_CELL_REMEDY`: extend the per-cell store, **never a
  per-property pull**.

W1_14's `block_reason` is the recruiting text that replacement was written to stop. It was
last revised 2026-09-07, nine days before the ruling.

## 2. What the cell store already does — and both my predictions were wrong

`sim/weather_world/` holds **221 cells**, with `cell_id_for` snapping a coordinate to the nearest
held cell and refusing beyond `MAX_SNAP_KM = 5.0`.

| population | resolves | pre-registered prediction | verdict |
|---|---|---|---|
| supply book (18 premises) | **16/18** | 18/18 | **REFUTED** |
| drawn households (seed 7, `draw_region=True`, 210 drawn, all sited) | **78/210 = 37.1%** | 50–90% | **REFUTED (low)** |
| directional: store ≫ four per-property sites | **37.1% vs 2.0% = 18x** | >10x | confirmed |

Snap distance across the drawn population: min 0.00, p25 3.16, **median 7.23**, p75 16.54, p90
29.72, max 67.25 km. The typical drawn household is seven kilometres from the nearest cell the
store holds, so this is not a near-miss — the store covers the cells the *book* occupies and the
drawn frame is much wider.

**The two the book loses are C_IC1 and C_IC2 — Birmingham, 7.35 km from the nearest held cell.**
Birmingham is the coordinate W1_14's history has named as un-archived through three restatements
of its blocker. It is still un-archived, now in the new store rather than the old one.

I predicted 18/18 on the book because the store was built from the book's cells; that reasoning
was sound and the answer is still no. The build set and the book have diverged, and nothing was
watching.

## 3. What landed

`simulation/weather_inputs.py` — `_has_archive` and `weather_source_customers`, written fresh
against HEAD's design rather than recovered (there was nothing to recover, and the salvage bytes
belong to the losing frame-cut design that `7f9362ceb` deliberately dropped). The weather-source
predicate now asks the **property** — is `sim/weather_data/{id}.csv` on disk — where it inferred
the archive from `commodity == "electricity" and segment == "resi"`. That proxy was wrong in both
directions:

- it **admitted** C7/C8/C9, which are resi electricity and hold no CSV. Each shares its exact
  coordinate with C1/C2/C3, which precede them in the book, so the right answer came out by book
  ORDER. A reorder, or retiring C1, resolves a premise to an id with no file — and
  `load_weather_means` returns an **empty dict** for a missing file, so that is no weather, no
  error and no refusal, on any surface.
- it **excluded** any archived premise that is not resi electricity. Birmingham and Teesside each
  hold two premises at one identical coordinate, none resi electricity, so an archive pulled for
  the first could never have answered the second.

Every live premise resolves exactly as before — **18/18 unchanged**. The repair is an equivalence
on today's book and a correction on any other.

### The controls, and why two of them bind their own roster

`tests/simulation/test_weather_inputs.py`, three new controls. Mutation: restore the proxy,
in-process (no shared-tree write).

| control | under the mutation |
|---|---|
| `test_a_premise_with_no_csv_cannot_be_a_weather_source_however_early_it_sits` | **RED** |
| `test_an_archived_premise_is_a_source_whatever_its_commodity_and_segment` | **RED** |
| `test_the_live_book_names_every_source_it_holds_and_no_id_without_a_file` | **RED** |
| the four PRE-EXISTING live-roster controls | **all GREEN** |

That last row is the finding inside the finding. **On the live book this repair is unmutatable**:
the archived ids precede the un-archived ones at every shared coordinate, so resolution is right
for the wrong reason and no control keyed to the real roster can tell the two predicates apart.
The discriminating pair is therefore bound in the test, where no acquisition or world-repair can
take the subject away.

The split is worth keeping rather than collapsing: **membership** of the source list *is*
observable on the live roster (the third control fires with *"C9 is a weather source with no
archive on disk"*); only a bound pair can see which id a premise actually **resolves** to when an
archived and an un-archived premise sit at one coordinate.

## 4. What W1_14's level is, and what its real remaining work is

**Level stays at 1. No move, and this is not a close call.** L2 is "mechanically real"; a level
move now would be exactly the reachable-but-not-chosen error the atom's own comment warns about.
`weather_inputs` still resolves per-property and **does not read `sim.weather_world` at all** — so
whatever the store's coverage is, the household heat load this atom exists to drive is still not
driven by it. The 37.1% is a measurement of a store this seam is not wired to.

The remaining work, in order, and none of it is a per-property pull:

1. **Migrate `weather_inputs` onto `sim.weather_world`** — the seam resolves to a CELL, not to a
   customer_id with a CSV. This is the piece that makes L2 truthful, and it is where the 37.1%
   starts mattering.
2. **Extend the store to the cells the book occupies** — starting with Birmingham, which the book
   holds and the store refuses at 7.35 km. Two premises, one cell.
3. **Then decide what the drawn frame needs**, which is a coverage judgement (221 cells serve 37%
   of drawn households; the median household is 7.2 km out) and not a code question.

`block_reason` is corrected in the map to say this, with the version it replaces kept beside it.

## 5. Owed elsewhere

- **The map recorded a repair as landed that was never landed.** `fork_salvage` captured two of
  the three files a dying worktree held, and the map's prose asserted all three. Nothing compares
  a map claim of the form "X now checks Y" against whether `Y` is in any ref. That is a
  rule-class finding and an empty instance list would not clear it — this instance sat unexamined
  for thirteen days and sent a draw at a commit that does not contain the code it names.
- **`simulation/run_phase1b_weather_pull.py` is the refused design, still executable**, and it
  loops the whole book writing one CSV per customer. Nothing in it or beside it says the director
  refused per-property pulls. Left as found, named here: deleting a runner is a judgement for the
  lane that owns the migration in §4.1, not a side-effect of this repair.
