**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS_stale_copy_refusal`

*LATENT and not BLOCKING deliberately: the grader defect is REPAIRED and landed with this note, and
the residue it exposes — 7 paths whose door does not exist yet — is already held BLOCKING for this
lane by the two findings cited below. A second BLOCKING row for the same subject would double-count
one obstruction and block a lane twice for it.*

# The stale-copy census named a door that took ZERO of its 27 rows

**Claim:** `clear-the-sixteen-remaining-armed-reverts-now-the-census-reads-true`. Filed 2026-09-22 by
the delivery seat.

**NOT A NEW CLAIM ABOUT THE SHUT DOOR.**
`WORKER_RESULT_ONE_CARRIED_LINE_VOUCHED_A_FIFTY_TWO_LINE_REVERT_AND_THE_DOOR_THE_CLOCK_RULE_NAMES_IS_SHUT_FOR_ITS_WHOLE_POPULATION_2026-09-22.md`
already established that the clock rule's named door is shut for its whole population, and
`WORKER_RESULT_THE_THREE_CLEARABLE_REVERTS_ARE_GONE_AND_THE_TWO_LEFT_NEED_A_DOOR_THAT_ENACTS_THE_BASE_WINNING_2026-09-22.md`
named the missing enactment. What is new here is **why nothing in the census could see it**: the
grader built to catch a remedy that refuses was scoped past that population by its own filters.
That half is §(b) below, and it is the part that is repaired rather than reported.

---

## What was drawn, and what the premise turned out to be

The item said the census was READABLE for the first time in ten listings — `origin/main` an ancestor
of HEAD at 0 ahead, 0 behind — and that its count of 25 was therefore the first comparable number.

**That premise was already spent when it was drawn.** The tree was 1 behind and 2 ahead, and the
doorbell's own path-check carried the caveat inverting the holder-work reading. The first move was
therefore not the work but the base: `surgical_land --merge origin/main` refused on one conflicted
path, `site/data/value_arms.json` — a generated feed, where picking a side is the wrong move. It was
**regenerated from the merged generator** in a scratch worktree and landed through `--resolve` as
`a315a0b73`. `origin/main` is now an ancestor of HEAD.

On that honest base the census read **27**, not 25.

---

## The finding: the census's own named remedy took none of its rows

Every one of the 27 rows printed a REMEDY naming a door. Run against all 27, the doors answered:

| door verdict | rows | what it means |
|---|---|---|
| `refused_no_reader` | 7 | `.md` / `.yaml` — **no reader exists and never will** |
| `refused_supplies_names_head_lacks` | 10 | a JSON leaf name carries its value, so an edited value reads as a new key |
| `refused_replacement_no_landable_hunk` | 8 | `--keep` has no legal selection and **`--content` would land a revert** |
| `refused_holder_has_it_staged` | 2 | genuinely another lane's, staged |

**27 of 27 refused. Nothing was written.**

Two halves of this are worth separating, because they fail differently.

**(a) The census told me to `--content` eight paths that `--content` would REVERT.** The census
graded those rows HOLDER WORK on a name count. `refresh_to_head`'s `REPLACEMENT` state — built in
2026-09-08 precisely to name this — says every hunk carrying a new name also deletes one the base
has, so *both* doors are wrong and which implementation survives is a judgement. Following the
printed remedy on those eight would have landed eight reverts.

**(b) The grader built to catch exactly this was scoped past the population it mattered most for.**
`door_verdicts` asked the named door only when `loss.is_rival`, or when the row was holder work and
`.py`. `is_rival` is `self.gains is not None and not self.novel` — **False for every clock-only
loss**, which is the entire `.md`/`.yaml` population, because no symbol reader reads those suffixes.
Those rows reach the `by_clock` branch of `remedy()`, which names `refresh_to_head` just as loudly,
and that tool answers `refused_no_reader` for `.md` **by construction**.

So the census printed a permanently-shut door as an actionable remedy for 7 paths, and its own
door-checker — whose docstring opens *"THE FINDING THIS EXISTS FOR IS A REMEDY THAT REFUSED"* — was
structurally unable to notice. Scoped twice: once by the population filter (`is_rival`), once by the
type filter (`.py`). Each hid the other.

### The repair

`Loss.names_the_refresh_door` — keyed to **which branch of `remedy()` prints the tool's name**, not
to a suffix list that would rot the moment `READABLE` moves and would be a second implementation of
a condition already written above it.

Live census before: **2** shut-door markers. After: **14** (7 `no_reader`, 5 `supplies_names`, 2
`staged`). Twelve remedies that read as actionable now say so when they are not.

Mutation-proven, each leg against the mutation written for it, no residue left in the shared tree:

- `names_the_refresh_door` → `is_rival` (the original scoping) reds
  `test_a_row_whose_remedy_names_the_refresh_door_is_GRADED_against_that_door`, alone.
- `names_the_refresh_door` → `True` reds `test_a_holder_work_row_is_NOT_sent_to_the_refresh_door`,
  alone — the leg that stops the first from being satisfied by a grader that says yes to everything.

The oracle is the remedy text the reader actually meets, so neither leg pins today's count.

---

## Disposition, per file — 27 → 20

Seven disarmed. **No verdict was batched across the class**; each names its own door and reason.

### Disarmed (7)

| path | door taken | reason |
|---|---|---|
| `tests/background/test_a_live_record_read_from_a_linked_worktree_reads_the_shared_tree.py` | `--base-wins` | `predates_landing` vs `e9ad946cd`; 4 names supplied are the older draft of the 6 dropped |
| `tests/background/test_an_episode_held_open_by_its_queue_is_not_an_unbroken_outage.py` | `--base-wins` | `predates_landing` vs `8dfb28f9f`; 1 of its "new" names re-creates a deliberate deletion — the base winning IS the correct enactment |
| `tests/simulation/test_phase25a_eac_solar.py` | `--base-wins` | `predates_landing` vs `febf7e51f` |
| `tests/tools/test_couple_value_based_pricing.py` | `--base-wins` | `predates_landing` vs `c4809c5fc`; 7 names the older draft of 19 dropped |
| `tests/tools/test_value_cycle_ab_noise_floor.py` | `--base-wins` | `predates_landing` vs `964036259` |
| `tools/generate_value_arms_data.py` | `--base-wins` | `predates_landing` vs `a315a0b73` — the merge landed this turn; 2 names the older draft of 32 dropped |
| `site/data/value_arms.json` | **regenerated** | a generated artefact's honest door is to rebuild it, not pick a side; mtime now postdates the landing, so the clock excludes it by construction |

Every `--base-wins` copy is preserved and recoverable at
`refs/preserved/refresh-to-head/base-wins-2026-09-22-<file>`. Nothing was discarded irreversibly.

### Residue (20), with a named per-file reason

**`refused_no_reader` — 7, and these are PERMANENTLY unresolvable through the named door.**
`docs/data-sources/weather.md`, `docs/design/ANNUAL_REPORT_IMPORT_DEBT.md`,
`docs/design/simplifications/A49_the_ceiling_comes_before_the_programme_on_r3_and_r4.yaml`,
`docs/institutional/knowledge_map.md`, and three `docs/staging/SEAT_RESULT_*.md`.
`refresh_to_head` has no reader for `.md`/`.yaml` and an unavailable check is a failed check. The
census now SAYS so on each row, which is the whole of this turn's repair — but saying so is not a
move. **These need a door that does not exist yet**, and minting one is the next item, not this one.

**`refused_supplies_names_head_lacks` — 5 JSON carriers.**
`docs/market_research/domestic_shift_response_arc.json`,
`docs/observability/self_clearing_alarm_census.json`, `docs/observability/svt_drift_belief_grade.json`,
`docs/reports/ladder_churn_factors.json`, `docs/reports/ladder_churn_factors_svt_segment_decisions.json`.
The leaf-name test cannot tell a new key from an edited value — deliberately, and that is
fail-closed and right. For the four that are **generated**, the door is the one used on
`value_arms.json` above: regenerate. `ladder_churn_factors*` is a full ladder-churn run and is too
expensive for a bounded tick; `domestic_shift_response_arc.json` appears hand-maintained and needs a
person's judgement, not a rebuild.

**`refused_replacement_no_landable_hunk` — 1 left.**
`tests/architecture/test_year_keyed_rate_table_census.py`. `--base-wins` correctly **refused** it:
its clock verdict is `predates_landing_carrying_some` (PARTIAL), not `predates_landing`, so the copy
may be built on the landing and nothing but my word says otherwise. That word is what the flag exists
not to take. **Left deliberately. This is a judgement between two implementations and the seat should
make it with the file open, not from a census row.**

**`refused_holder_has_it_staged` — 2.** `site/test_the_baseline_comparison_reaches_the_reader.py`,
`site/test_the_selection_legs_bias_size_reaches_the_reader.py`. Another lane has these staged right
now — a live holder, not a stale copy. Hands off.

**Genuine holder work, unlanded — 4.** `simulation/premise_population.py`,
`tests/background/test_publish_gate_wedge_draw.py`, `tests/tools/test_generate_value_arms_data.py`,
`tests/tools/test_the_concordance_curve_says_what_it_could_have_seen.py`, `tools/run_value_cycle_ab.py`.
These supply live names and `--content` is licensed. Each is a separate landing and each costs a full
gate cycle; they did not fit this turn. **One caveat that must not be lost:**
`test_publish_gate_wedge_draw.py` references `background.supervisor.PUBLISH_GATE_WINDOW_SECONDS`,
**which no tree supplies, committed or not** — that is not a pair, it is a reference to something
that does not exist anywhere, and landing it reds every lane.

---

## The prediction I am recording before the next listing

The class size is **20** on a base `origin/main` is an ancestor of. I predict the next listing
**does not fall below 14 without a new door being built**, because 7 `no_reader` rows have no move
at all and 2 are a live holder's. If it reads lower than 14, either someone minted the missing door
or the rows left by another route — and which it was is the thing to ask, not the number.

The three earlier readings of 17, 22 and 25 were taken through a stale base and remain
incomparable to this one and to each other. The comparable series starts at **27 → 20**, today.
