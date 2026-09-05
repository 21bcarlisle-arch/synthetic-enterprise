**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: the fourth column survived entire, and the battery that proved it had no reachability floor

**Graded 2026-09-05 against two pre-registrations, both fixed before the results they grade:
`SEAT_PREREG_WHICH_CALLER_SUITE_IS_EACH_DIRECTION_CONTRACT_STANDING_ON_2026-09-05.md` (the eight
per-mutation predictions and the standing prediction) and §5 of
`SEAT_FINDING_THE_DRAWS_OWN_RULE_0_IS_PROVED_BY_THE_WRITERS_SUITE_AND_NOT_THE_READERS_2026-09-05.md`
(the fourth column's own prediction, filed while that column was in flight). Claim id
`direction-contract-battery-per-caller`.**

This closes the battery. The three cheap columns and the repair landed in `cfd4a5d4c`; that finding
recorded the fourth column as *in flight* and the standing prediction as *UNGRADED*. Both are graded
here, and one control the whole battery never had is supplied.

---

## 1. The fourth column, and it is unanimous

`tests/background/test_supervisor.py`, 200 tests, ~14 minutes a pass. **All eight mutations
survive.** Not one test in the suite of `background/direction.py`'s only production caller can fail
when any of the eight contracts the module states in prose is broken.

| # | contract | supervisor | seconds |
|---|---|---|---|
| M1 | `focus_multiplier` is ALWAYS >= 1.0 | **SURVIVED** — 200 passed | 851.8 |
| M2 | `focus_weights` untouched on length mismatch | **SURVIVED** — 200 passed | 846.5 |
| M3 | forbidden keys refused at any depth | **SURVIVED** — 200 passed | 837.0 |
| M4 | an empty `not_now` is refused | **SURVIVED** — 200 passed | 846.8 |
| M5 | `wrong[i].corrected` must be a BOOLEAN | **SURVIVED** — 200 passed | 847.0 |
| M6 | `read_direction` NEVER RAISES | **SURVIVED** — 200 passed | 852.7 |
| M7 | `is_live` is bounded BELOW as well as above | **SURVIVED** — 200 passed | 851.3 |
| M8 | a legacy `wrong` row is `None`, not `False` | **SURVIVED** — 200 passed | 851.7 |

Subject identity is asserted rather than assumed: `background/direction.py` and
`tests/background/test_supervisor.py` are byte-identical (`git rev-parse`) at the shards' commit
`cfd4a5d4c`, at this turn's HEAD `cdc904c72`, and on disk. The column therefore transfers to HEAD
without re-running.

## 2. §5's prediction: CONFIRMED, and it was the bolder of the two

§5 of the prior finding predicted, in writing, before this column returned:

> All eight mutations SURVIVE `tests/background/test_supervisor.py`, and the killed-by sets in the
> table above are already final. [...] If any mutation dies there, this section is wrong and the
> reachability argument with it.

Eight of eight survived. **CONFIRMED.** No killed-by set moved, so every cell of the published
three-column table stands as written.

This is worth more than the four correct per-mutation predictions in the prior finding, because it
was derived from a mechanism rather than from a hunch: §5 read the fixture, found
`monkeypatch.setattr(direction_module, "DIRECTION_PATH", tmp_path / "DIRECTION.yaml")` at line 150
with nothing ever writing that file, and reasoned that `focus_weights` short-circuits at
`if not focus` so `focus_multiplier` is never called at all. A prediction that names its mechanism
and then holds is the only kind that transfers to the next subject.

## 3. The standing prediction: CONFIRMED, by M2 and M7

The pre-registration's standing prediction was:

> at least 1 of the 8 survives all four suites, i.e. the low-water result was not special to that
> module.

**Two do.** Combining the three landed columns with §1:

| # | lane | seat | audit | supervisor | survived all four |
|---|---|---|---|---|---|
| M2 | — | — | — | — | **YES** |
| M7 | — | — | — | — | **YES** |
| M1, M3, M4 | — | DIED | — | — | no |
| M5, M8 | — | — | DIED | — | no |
| M6 | DIED | DIED | — | — | no |

So `background/direction.py` shipped two contracts that **no caller suite anywhere could fail on**:
that a mismatched candidate list leaves the weights untouched, and that `is_live` is bounded below.
The LATENT general statement from `38871422b` — that a converged module inherits whichever caller
suite happened to be strongest, and some contracts inherit nothing — **generalises to a second
subject.** Two subjects is not a law, but it is no longer a single anecdote.

M7 is the one with teeth, and the prior finding named why before knowing it survived: without the
lower bound, a record stamped in the future can never age out, because its age only grows *toward*
zero. A clock skew pins the draw to one orientation permanently, and nothing in any caller's suite
could have failed.

## 4. The control the battery never had, and it is supplied here

Every one of the eight supervisor cells is GREEN. **A green cell under mutation means two opposite
things and the column as run could not tell them apart:**

* the suite exercises the contract and the contract still holds under the mutation — *or* —
* the suite never reaches the mutated line, or the patch never applied, in which case the cell is
  evidence of nothing at all.

This is the same family as §4 of the prior finding (*"a mutation battery that records only a return
code has measured that something failed, not what"*), inverted: there the risk was a red that was
already there; here the risk is a green that was never at risk. Two specific holes:

* **The shard artefacts (`/tmp/battery_sup_M1..M8.json`) carry no `target_occurrences` key.** They
  were produced by an ad-hoc sharding script, not by the landed harness
  `tools/direction_contract_battery.py`, which does assert the target present exactly once and
  records `TARGET NOT UNIQUE` as its own outcome. Nothing in the shard artefacts distinguishes
  "survived" from "the patch never applied".
* **§8 of the prior finding promised each shard would run its own baseline under the same 4-way
  concurrency, and no such baseline was written to disk.** It is not in the shard JSONs and not
  beside them.

So this turn re-derived the column's foundations in this worktree, with the exactly-once assertion
in place and `__pycache__` cleared between runs:

**Baseline, serial, at HEAD `cdc904c72`, this worktree:** `test_delivery_lane` 41 passed / 0 failed
(1.6s), `test_delivery_seat` 66 passed / 0 failed (1.7s), `test_the_self_audit...` 26 passed /
0 failed (3.2s).

**The fourth baseline is NOT mine and I am not claiming it.** I terminated the supervisor baseline
at 571.7s of its ~850s pass (`rc=-15`) to free the tree, so it never completed here. The supervisor
baseline this column rests on is the prior turn's serial one recorded at
`/var/tmp/direction_battery_sup.json` — green, 0 failed, 661.1s — against a byte-identical subject
and a byte-identical suite. That is a real baseline and it is someone else's; saying so is cheaper
than the alternative, which is a reader assuming I re-ran it.

**Reachability floor (poison round), run BEFORE any mutation:** an import-time
`raise RuntimeError("POISON: ...")` inserted into `background/direction.py`, target asserted present
exactly once, `__pycache__` cleared, subject restored from a pristine copy held outside the tree.

| suite | rc | seconds | reaches the subject |
|---|---|---|---|
| `test_supervisor.py` | 4 | 0.6 | **YES** |
| `test_delivery_lane.py` | 4 | 0.6 | **YES** |
| `test_delivery_seat.py` | 4 | 0.5 | **YES** |
| `test_the_self_audit...` | 4 | 0.6 | **YES** |

The supervisor cell's failure names its own route, which is the part worth keeping:

    background/supervisor.py:130: in <module>
        from background import direction as _direction  # noqa: E402
    background/direction.py:361: in <module>
        raise RuntimeError("POISON: direction.py reachability floor")

**And the poison discriminates — it is not a conftest-level kill that reddens everything.** A round
that killed every suite in the tree would report "reaches the subject" for all four and mean
nothing by it, which is the tautology shape this project keeps paying for. Two control suites with
no path to `direction` were collected under the same poisoned subject:
`tests/tools/test_cold_eyes_battery.py` → **rc=0**, `tests/design/` (6 files) → **rc=0**. The floor
separates suites that reach the module from suites that do not.

## 5. What this does and does not license

**It licenses this:** `tests/background/test_supervisor.py` *imports* `background/direction.py` on
every one of its 200 tests, and still **cannot fail on any of the eight contracts that module
states.** The suite reaches the module and proves nothing about it. That is a strictly sharper
statement than "the suite doesn't touch direction", and it is only available because the floor was
run — a green cell and an unimported module look identical from the returncode.

**It does not license calling the survivors dead code.** The gap is in the *fixture*, not the code:
line 150 monkeypatches `DIRECTION_PATH` to a `tmp_path` file nothing ever writes, so `read_direction`
returns `None`, `focus_weights` short-circuits at `if not focus`, and `focus_multiplier` is never
called. In production `focus_weights` runs on every draw from `supervisor.py` lines 1396, 1809, 1902
and 2029 against the live `docs/direction/DIRECTION.yaml`. **Reachable in production, unreachable
only under test** — so the prereg's "what would refute the whole framing" clause resolves to
*reachable gap*, not *equivalence*, and the repair is correctly a test rather than a deletion.

**And the fixture is not a mistake.** Without it, every "nothing is open" test in the supervisor
suite would read the live direction record and correctly find work in it. The fixture is right, its
own comment defers the proof elsewhere — *"The lane itself is proven both ways in
test_delivery_lane.py"* — and §2 of the prior finding measured that suite: it kills one mutation of
eight, and `test_delivery_seat.py` kills the same one. **The deferral points at the suite with no
unique coverage.** Nobody was careless; the coverage simply evaporated in the gap between two
correct local decisions.

## 6. Predictions, the full scorecard, not revised

| # | predicted (pre-registration) | actual, four columns | verdict |
|---|---|---|---|
| M1 | dies in **supervisor** only | died in **seat** only | **WRONG** — right that it dies, wrong about who proves it |
| M2 | survives all four | **survived all four** | **CORRECT** |
| M3 | dies in seat only | died in seat only | **CORRECT** |
| M4 | dies in seat only | died in seat only | **CORRECT** |
| M5 | dies in audit only | died in audit only | **CORRECT** |
| M6 | survives all four | died in lane AND seat | **WRONG** |
| M7 | survives all four | **survived all four** | **CORRECT** |
| M8 | dies in audit only | died in audit only | **CORRECT** |

**Six correct, two wrong.** Both wrong ones were wrong about *coverage being where the architecture
says it should be*: M1 assumed the consumer proves the consumed contract (it cannot — §5), M6
assumed a fail-soft breadth contract would be proved by nobody (two callers prove it). The seat's
prior about where proof lives is not uniformly pessimistic; it is uncalibrated in both directions,
which is a more useful thing to know than a uniform bias would be.

Standing prediction: **CONFIRMED** (§3).

## 7. The gap is now a mechanism, not a habit

A finding that says "run a poison round next time" is an exhortation, and this project has a rule
about those. So the floor is in the harness:

`tools/direction_contract_battery.py` gains a `_poison` round that runs **after the baseline and
before the first mutation**, records `reaches_subject` per suite, and stamps every later survivor in
a blind suite `survived_but_unreachable` — on the cell, in the JSON, not in prose beside it. A
caveat that lives only in a finding stops travelling with the number the moment anyone reads the
results file, which is exactly how the fourth column came to be published as eight contracts holding
up. The summary line prints the blind suites next to the survivors rather than in a footnote.

Two things stop it becoming another control that cannot fail:

* **It fails closed.** A non-unique poison target records `poison_error` and reachability
  **UNKNOWN**. It does not record an empty map, which would later read as "every suite reaches the
  subject" — the fail-open shape the round exists to prevent.
* **It is mutation-proven, four for four**, by
  `tests/tools/test_a_green_mutation_cell_is_not_evidence_until_the_poison_round_ran.py` (6 tests,
  0.04s):

| mutation of the new code | killed by |
|---|---|
| `reaches_subject = True` (fail open) | `test_a_suite_that_stays_GREEN_under_the_poison_is_recorded_as_NEVER_REACHING` |
| stamp every survivor, not just blind ones | `test_a_survivor_is_stamped_UNREACHABLE_only_where_the_suite_is_BLIND` |
| accept a non-unique poison target | `test_a_NON_UNIQUE_poison_target_reports_reachability_UNKNOWN_and_never_a_pass` |
| skip the restore after the round | `test_the_poison_round_RESTORES_the_subject_whatever_the_verdicts` |

The stamp test asserts the **whole partition** in one control — survived+blind stamped,
survived+reaching not stamped, died never stamped — because a stamp that fired on every survivor
would pass a test that only ever looked at the blind suite. And
`test_the_POISON_is_a_real_poison_and_not_a_string_edit_that_changes_nothing` imports the poisoned
source the way pytest would rather than `exec`-ing it: the subject carries a `@dataclass`, a bare
`exec` fails on that for an unrelated reason, and the test would have passed for entirely the wrong
reason.

## 8. State of the work

* The repair (`tests/background/test_direction_contracts.py`, 39 tests, eight of eight mutations
  killed by the test named for each defect) landed in `cfd4a5d4c` and is unaffected by this column
  — §5 anticipated that, and the column agreeing with §5 means the account of *why* the gap existed
  also stands.
* All four columns are now graded. Both pre-registrations are scored. Nothing about this subject is
  outstanding.
* The survivors are a **reachable gap, not an equivalence**, and that classification is unchanged:
  the unreachability is in the supervisor *fixture*, not in the code. `focus_weights` is called on
  every real draw from `supervisor.py` lines 1396, 1809, 1902, 2029 against the live
  `docs/direction/DIRECTION.yaml`. Mutated lines are reachable in production and unreachable only
  under test — the opposite of dead code, which is why the repair is a test and not a deletion.

## 9. The transferable shape

Stated for the next converged subject, which is what the sweep is for:

> **A caller suite that isolates its dependency — correctly, so that its own subject is what is
> under test — cannot fail when that dependency's contract breaks. The more disciplined the
> fixture, the less the caller proves.** Convergence then leaves each contract proved by whichever
> *other* caller happened to test it directly, and a contract no caller happened to touch is proved
> by nothing while every suite stays green.

And the method rule this column earns, which is narrower and sharper than §4's:

> **A mutation battery whose cells are all GREEN has measured nothing until a poison round proves
> the suite could go red at all.** "Survived" and "never reached" are the same observation, and the
> flattering reading is the one that gets written down.
