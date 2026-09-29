**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The reconciler graded nothing because one predating control refused a whole row, and two of the 28 rows name a subject a director ruling abolished

Answers `docs/staging/records/SEAT_PREREG_HOW_FAR_THE_28_UNGRADABLE_LEVEL_ROWS_CAN_BE_DISCHARGED_2026-09-25.md`.
Five predictions, recorded below **beside** the results, not instead of them.
Follows `SEAT_FINDING_THE_MAPS_SILENCE_IS_UNFALSIFIABLE_...2026-09-25.md`, which established that
`tools/level_zero_contradicted_by_its_own_controls.py` returns population 28, **graded 0**, and that
the map's silence is therefore unfalsifiable. That finding asked *why* the instrument weighed
nothing. This answers it.

## The answer, in one paragraph

**The instrument was not conservative, it was wrong about its own stated property.** Its docstring
says the named set is evidence "when the atom's own build is what wrote the set" — but the code
asked the opposite question, *is anything in the set older than the row*, and refused the row ENTIRE
on a single yes. That is the ordinary shape for any atom that EXTENDS an existing suite rather than
writing a new one. `KNIFE3_wall_crossing_paydown` names twelve controls: **nine were born after the
row, by its own build, and three before it** because the atom cut into suites that already existed.
Nine pieces of the atom's own evidence were discarded for three that carry none. Fixed in this
commit: a row is ungradable for age only when EVERY named control predates it.

## What was measured

Instrument: `tools/level_zero_contradicted_by_its_own_controls.py --json`, at `54a7b6242`.

| | population | graded | ungradable |
|---|---|---|---|
| before | 28 | **0** | 28 |

Six of the 28 carried `CONTROL_PREDATES_ROW`. Their named controls, dated against the row's own
minting commit:

| row | controls | predating | atom-own |
|---|---|---|---|
| `KNIFE3_wall_crossing_paydown` | 12 | 3 | **9** |
| `D27_belief_window_saturates_on_this_book` | 1 | 1 | 0 |
| `D9_worse_than_blind_chip_is_metric_blind` | 1 | 1 | 0 |
| `H41_the_map_ratchet_has_no_ongoing_drain` | 2 | 2 | 0 |
| `W2_31_people_phase1_the_physical_layer_stands_alone` | 1 | 1 | 0 |
| `A50_the_supplier_use_case_register_is_published_with_a_status_per_item` | 1 | 1 | 0 |

Only KNIFE3 has a mixed set, so only KNIFE3 changes verdict. The other five have **no** atom-own
control and stay ungradable — the relaxation does not touch them, which is the point: H41's shape,
the one the module docstring works through at length, is preserved exactly.

**The convention the tool declined to trust is present and decisive.** Its docstring says dating
settles provenance "without trusting a commit-message convention". Asked directly, three of the six
predating controls were last edited after their row by a commit whose subject **names the atom**:

- `tests/architecture/test_epistemic_wall_ratchet.py` ← `fda6565e4` *"KNIFE3 step 3: the first seven crossings are actually cut…"*
- `tests/simulation/test_renewals_approval_routing.py` ← `22f1f98b2` *"KNIFE3 B7: land the renewal-desk cut…"*
- `site/capabilities/test_capabilities_door.py` ← `fb2fa09eb` *"the supplier use-case register reaches the reader, and an item is testable"* (A50's deliverable, the day after its mint)

Declining to trust the convention was a defensible call; not pricing what it cost was not. It is
recorded here and **not acted on** — the fix landed is the age leg, which needs no convention at all.

## The fix, and why it loosens nothing

`if predating:` → `if predating and not atom_own:`.

CONTRADICTED still requires the **whole** named set to pass, predating entries included. So a
predating control can only ever SILENCE a row; it can never be the thing that refuses one. The
fail-closed direction — "the refusing verdict is the one that demands work, so it is the one that
must be earned" — is unchanged.

Four controls, each proven to fire on its own named mutation:

| control | mutation | result |
|---|---|---|
| `…ONE_control_its_own_build_wrote_is_GRADED…` | restore `if predating:` | RED |
| `…controls_ALL_predate_it_is_still_ungradable_ENTIRE` | drop `predating and` | RED |
| `…PREDATING_control_that_FAILS_still_silences_a_mixed_row` | `runner(atom_own or controls, …)` | RED |
| `…UNDATABLE_control_beside_an_atom_own_one_is_still_PROVENANCE_UNKNOWN` | `if undatable and not atom_own:` | RED |

**One mutation came back GREEN and it was an equivalence, established rather than assumed.** The
first draft computed `atom_own` as `p not in predating and p not in undatable` and claimed the
fourth control guarded that subtraction. Removing the `undatable` term was green, because the
`if undatable:` leg below fires on ANY undatable entry and had already decided the verdict. The term
was dead code. It is deleted and the control is re-keyed to the mutation that actually reaches it.
A third control was red under its mutation but red on a **`KeyError` in the injected runner**, not on
its own assertion — the flattering reading. Its runner now answers any subset, so the assertion is
what fires.

## The second finding: two rows name a subject that was abolished, not mislaid

`ungradable_causes` classifies an absent named path by asking `_path_known_to_git` — "did this ever
exist on any ref" — and turns any `True` into **`POINTER_ROT`**, whose printed repair is *"repoint
`file_scope` at where the path lives now"*. Exactly two of the 28 rows carry it, and for both the
repair **cannot be followed**:

- `SITE3_wall_exhibit_url_rename` — names `site/now/index.html`, `site/wip-flow/index.html`, `site/company/index.html`
- `C_supply_start_consumer_routing` — names `site/customers/index.html`, `site/company/index.html`

All five were deleted by **one** commit, `03dd8c49e` (2026-08-20), *"The five tabs are the site now:
eleven pages deleted"* — a director ruling: *"I don't want hidden pages… no permanent limbo."*
There is no *now* to repoint at. The path did not move; the subject was abolished.

**`SITE3` is worse than unrepairable — it is superseded, and it is still winning draws.** Its
deliverable was to rename the `/customers/` URL and 301 the old path. `03dd8c49e` deleted the page
outright and 301'd `/customers/` → `/explore/`, doing more than the atom asked. Its exit criterion
(3) names `site/test_no_links_to_redirected_urls.py` as the class guard — that file is not on disk.
Its criterion (2) requires `site/_redirects` to 301 the old path; `site/_redirects` now carries **two
rules**, and its own header records the ruling that abolished the other thirty-eight: *"no one has
ever visited those URLs. There is no history to protect, so stop protecting it."* The atom sits at
`level_current: 0`, `loop_stage: build`, five weeks after its work was completed and its remaining
requirements repealed. **This is precisely the defect the reconciler exists to catch, and the
reconciler cannot see it.**

**`C_supply_start_consumer_routing` has an unsatisfiable R11 wall.** Its exit criterion (3) is
stated as a wall: *"done means fetching the live poesys.net C1_2 surface and asserting the rendered
'Customer since' reads the real activation date."* No such surface exists. `Customer since` appears
nowhere in any served page — only in `site/data/proof.json` and `site/data/simplified.json`, which
are feeds. Neither successor page absorbed it: `site/explore/index.html` and
`site/capabilities/index.html` contain **zero** matches for `tenure`, `Customer since`, `acquired` or
`cust-who`. The deletion commit's "their content moved" is true of each page's *purpose* and false
of this atom's *subject*. An atom whose stated wall cannot be satisfied will never close.

**Neither row is edited by this commit, deliberately.** The pre-registration committed to repairing a
row only for the reason the tool names, and to leaving alone any row that cannot be honestly
repaired. Repointing either at `explore` or `capabilities` would put a path in the map that does not
carry the subject — the rot this instrument exists to detect, written by the hand repairing it.

## The predictions, against the results

| | prediction | result |
|---|---|---|
| **P1** | ≥1 row is neither map defect nor pass defect — its subject was abolished, and `POINTER_ROT`'s repair is unfollowable | **CONFIRMED** |
| **P2** | the abolished class is 2–3 rows, concentrated in `site/` paths from `03dd8c49e` | **CONFIRMED EXACTLY** — 2 rows, both `site/`, both that commit |
| **P3** | `graded` moves off zero but only to 1–3; the 13 `CONTROL_NEVER_WRITTEN` rows cannot be discharged by editing the map | **REFUTED on the first half, and the refutation is the rest of this finding.** `graded` is STILL 0. The second half holds. |
| **P4** | ≥1 row, once gradable, comes back CONTRADICTED | **REFUTED**, for the same reason as P3: no row became gradable, so nothing could come back contradicted |
| **P5** | the four `NAMES_ONLY_A_SCOPE` rows cannot be discharged by naming files; the item's "largest class" moves the number by ZERO | **CONFIRMED, and it is the item's own frame that is refuted** — the item ranks directory-scopes as the largest repairable class, but naming a file an unbuilt atom has not written is a prediction dressed as a declaration. The row would read `HONESTLY_UNBUILT`: more honest, still not graded. |

**What the item got wrong, stated plainly.** It framed all 28 rows as repairable rows under three
classes and said to work down the printed list. Two of its three named classes move `graded` by
zero, a fourth state it does not name exists and holds two rows, and the one change that moves the
number at all is in the INSTRUMENT, which the item does not consider. The tool's own per-row repair
lines were followed and they led here: for the six `NOTHING_IN_THE_ROW` rows the tool says *"do not
edit `file_scope`, because nothing in it is wrong"* — and it is right. The refusal was in the pass.

## P3 is refuted, and the reason is a SECOND blocker on the same row

Re-measured after the fix, over the live map:

| | population | graded | ungradable | contradicted |
|---|---|---|---|---|
| before | 28 | 0 | 28 | 0 |
| after | 28 | **0** | 28 | 0 |

**The fix worked and the number did not move.** KNIFE3 changed verdict — from
`CONTROL_PREDATES_ROW` to `RUN_UNAVAILABLE`, *"timed out after 900s"*. The age leg no longer holds
it. `DEFAULT_TIMEOUT_S` now does.

This is the finding's real shape and it was invisible from either end. **Two independent blockers
sat on the only gradable row in the partition, and each hid the other.** While the age leg refused
KNIFE3 the pass never reached the run, so the timeout could not be observed; now the run is reached,
the timeout is what refuses. A single measurement of `graded == 0` is consistent with both, with
either, and with neither — which is exactly why "0 of 28" was worth nothing as a reading, and why
the remedy the item drew (edit the rows) could not have moved it whatever was edited.

It also means **I cannot yet attribute the pass's emptiness to one cause**, and I am not going to
pretend otherwise. What is established: the age leg was one blocker, it is gone, and it was blocking
the only mixed-set row in the partition. What is not established: whether the timeout is the LAST
blocker on KNIFE3, because a run that times out reports no verdict about the suites underneath it.

**The timeout is not raised in this commit, deliberately.** 900s is a number, and replacing it with
a bigger number chosen because 900 was too small is exactly the move this project has a rule
against. What KNIFE3's twelve suites actually cost is being measured; the value goes in the record
and the change is made against it, or the conclusion is that a twelve-suite row cannot be graded in
one invocation and the instrument owes a per-suite breakdown instead. Either way it is a separate
change with its own evidence, not a constant edited on the way past.

## What is owed next

1. **`SITE3_wall_exhibit_url_rename` should be closed as superseded**, with `03dd8c49e` as the
   evidence. Not done here: closing an atom is the phase-close procedure and is its own turn.
2. **`C_supply_start_consumer_routing`'s R11 wall needs a ruling**, because it cannot be met as
   written. The substance (routing tenure consumers off the term anchor in `simulation/` and
   `saas/`) is live and real; only the *rendered-surface* half is unsatisfiable. It is not the
   seat's call to drop a wall the atom set itself.
3. ~~**KNIFE3's 900s timeout, priced rather than guessed**~~ — **WRONG CONSTANT, corrected in
   `docs/staging/records/SEAT_RESULT_KNIFE3_IS_DISCHARGED_BY_MEASUREMENT_AND_THE_TIMEOUT_I_NAMED_IS_NOT_THE_ONE_PRODUCTION_USES_2026-09-25.md`.**
   900s is the standalone default; the only production caller passes `_LEVEL_ZERO_TIMEOUT_S = 60`,
   deliberately, and should keep it. The suites were measured anyway: **1078s, 2.44 GB**, and **2 of
   them are red at HEAD and have been for 19 days**, so KNIFE3's verdict is **SILENCE** — the row is
   right to read 0. One of the 28 is weighed and P4 is refuted on the merits. What is actually owed
   is a fail-closed short-circuit on the red-at-HEAD register, read that record before acting here.
4. **`ungradable_causes` needs a cause it cannot currently express** — a named path DELETED at
   `HEAD` and not relocated is not `POINTER_ROT`, and printing an unfollowable repair for it is the
   undifferentiated-count failure that function was written to end, reopened one state along. Not
   done here: it is a second change to the same module and this commit's is already load-bearing.
