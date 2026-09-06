**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: seven of `direction`'s eight contracts are proved only by tests of the subject itself

**Graded 2026-09-06 against
`docs/staging/records/SEAT_PREREG_WHETHER_ANY_TEST_WHOSE_SUBJECT_IS_A_CALLER_PROVES_ANY_DIRECTION_CONTRACT_2026-09-06.md`,
fixed before the run. Claim id `direction-battery-four-columns-are-direct-importers`. Battery
fingerprint `ef6ece4e233b`, `/var/tmp/direction_battery_ef6ece4e233b.json`.**

This settles the Lane 0 question: **no, three of `direction`'s four caller columns do not belong in
`survived_all` as whole files** — and the reason is not the one the question assumed.

---

## 1. The question, and why the file grain had no answer

`b3938b313` closed the file-grain defect on `segment_vocabulary` and `fuel_mix` and deliberately
shipped **no** gate on "imports the subject", because on `direction` that gate would have condemned
a correct spec: all four columns import `background.direction` at module level and all four are
legitimately the dedicated suite of a module that calls it. It left the question open.

The question has no file-grain answer because the premise is false. `tests/background/
test_delivery_lane.py` holds **one test of `direction` and one test of the lane that uses it**. Both
readings of that file are correct and no file-level split can keep both.

Asked per TEST it is decidable, and the discriminator is the one the open question named — does the
test NAME a contract of the subject: *its assertions run against `direction`'s API and it never
calls the module its file is named for*. AST census over the four files:

| file | the subject's own tests | genuine caller tests using `direction` |
|---|---|---|
| `test_supervisor.py` | **0** | 0 — its only reference is the fixture's `monkeypatch.setattr(DIRECTION_PATH, ...)` |
| `test_delivery_lane.py` | 1 | 1 (`test_EXPIRED_direction_offers_NOTHING`, calls `dl.`) |
| `test_delivery_seat.py` | 17 | 0 |
| `test_the_self_audit_...py` | 5 | 1 (`test_the_published_panel_SPLITS_...`, calls `page.`) |

23 nodes. The recorded cells could not settle what follows, because every cell ran under `-x`: each
names one `FAILED` node and its tail says `stopping after 1 failures`, so a caller-subject test may
have gone red behind the one named and never been collected. Only a re-run could close it.

## 2. The result, and the prediction it refutes

Three cheap columns re-run at `d700de016` with the 23 deselected, baseline green on all four
(41/66/26/39 tests), poison floor green→red on all four:

| # | contract | published `killed_by` | after deselection |
|---|---|---|---|
| M1 | `focus_multiplier` >= 1.0 | seat | **survived every caller** |
| M2 | weights untouched on length mismatch | — | **survived every caller** |
| M3 | forbidden keys refused at any depth | seat | **survived every caller** |
| M4 | an empty `not_now` is refused | seat | **survived every caller** |
| M5 | `corrected` must be a BOOLEAN | audit | **survived every caller** |
| M6 | `read_direction` NEVER RAISES | lane **and** seat | **survived every caller** |
| M7 | `is_live` bounded below | — | **survived every caller** |
| M8 | a legacy `wrong` row is `None`, not `False` | audit | **DIED — `test_the_published_panel_SPLITS_open_from_corrected_from_not_recorded`** |

**P1 and P2 predicted 8 of 8 unproved. The answer is 7 of 8. WRONG, and kept here beside the
result.** P3 named M6 as the single prediction most at risk and gave the mechanism; M6 held and
**M8 was the one that moved**. Being wrong about *which* one, having named a specific one, is worse
than being wrong about the count.

**The refutation is the best evidence the discriminator is not rigged.** M8's killer calls
`page.what_it_got_wrong()` in `tools/generate_delivery_page.py` and monkeypatches
`page.direction_mod.read_decisions` — a test whose subject is a caller, which the census correctly
declined to deselect, sitting in the same file as five it did deselect. The census kept a test that
then refuted the prediction the census was built to serve. A discriminator that only ever removed
evidence would have taken it too.

**P5 CONFIRMED.** Two of eight → seven of eight unproved: less caller evidence than published and
never more, the third subject to move that way. A mixed population is guaranteed to bias in that
direction.

## 3. What is NOT graded, and it is not a footnote

`survived_all` is **`null` on all eight rows** and the summary line says `NOT YET GRADED ON EVERY
SUITE`. `tests/background/test_supervisor.py` costs ~850s a mutation (~1.9h for the column) and was
not run this turn. The engine refuses a verdict without it and that refusal is correct.

**P4's a-fortiori argument is exact rather than approximate, and it is stated as an argument, not
banked as a cell.** `direction` declares no node in `test_supervisor.py`, so
`spec.deselect_for("tests/background/test_supervisor.py", red) == red` — verified, `True`. The
supervisor cell is therefore the identical computation to the published one, which was green on all
eight. It cannot turn a survivor into a kill. But the fingerprint correctly refuses to resume rows
scored under the old split, and *"the computation is identical"* is not *"the run happened"*. The
column is **outstanding work**, named here rather than assumed away.

So the honest statement of §2 is: **seven of eight are unproved by any of the three callers that
were graded, and the eighth is proved by one caller test.** Whether the fourth column changes that
is answered by an argument and not yet by a run.

## 4. The mechanism, and what stops it becoming a control that cannot fail

`BatterySpec.direct_nodes` — the node-grain twin of `direct_suites`, deselected from caller columns
only. `tests/tools/test_the_caller_column_deselects_the_subjects_own_tests.py`, 6 tests, **five of
five mutations killed by the test named for each defect**:

| mutation | killed by |
|---|---|
| drop the node exclusion entirely | partition control + `..._only_from_the_FILE_IT_NAMES` |
| deselect the nodes from the subject's OWN columns too | partition control + `..._OWN_columns_keep_their_own_tests` |
| drop the filename filter (every caller loses every node) | partition control + `..._only_from_the_FILE_IT_NAMES` |
| drop `direct_nodes` from the fingerprint payload | `..._changes_the_FINGERPRINT` |
| revert the poison call site to the baseline reds alone | `..._EVERY_ROUND_THAT_GRADES_A_COLUMN_HONOURS_THE_DESELECTION` |

The partition control runs first and asserts all four deselection outcomes are distinct, because
three of the five mutations above would satisfy a leg-per-branch suite.

**The fail-open the last leg closes was real and is the one worth keeping.** The poison round
decides `reaches_subject`, and every survivor in a blind column is stamped
`survived_but_unreachable` off that verdict. Run the floor over the full file while the mutations
run the deselected subset, and a column whose only subject-reaching tests are `direct_nodes` is
stamped *reaches* on the strength of tests no later round executes — so its survivors read UNPROVED
when the honest reading is UNREACHABLE. That is exactly the confusion the floor exists to prevent,
let in through the floor itself. All four grading rounds (poison, hard poison, null, mutation) now
route through `deselect_for`, asserted over the source so a fifth round hand-rolling `known_red`
reds rather than silently regressing it.

`test_every_declared_node_NAMES_A_TEST_THAT_EXISTS` guards the other way: `--deselect` silently
accepts a node id for a test that no longer exists, so a rename would quietly stop excluding
anything and the column would drift back to grading the subject with the subject's own tests with
no run ever saying so.

## 5. The transferable shape

> **"Is this file the subject's own suite" is the wrong grain, and on a converged module it can
> have no answer at all.** A caller's dedicated suite is where the subject's own contract tests
> actually get written — they are near the code that motivated them, and nobody is careless in
> putting them there. `test_delivery_seat.py` holds seventeen tests of `direction`, each with a
> `MUTATION (must fire)` docstring written against `direction`'s code, and it is still the correct
> home for them. The population question is per TEST: *does this test's assertion run against the
> subject, or against something that uses it?*

And the narrower rule this run earns:

> **A battery scored under `-x` cannot tell you who else would have died.** Every cell names its
> first failure; the ones behind it were never collected. Any re-reduction that turns on *which*
> test killed a mutation is unanswerable from those cells and needs the run.

## 6. State of the work

* Landed: `direct_nodes` on the engine, all four grading rounds routed through it, the 23 declared
  on `direction`'s spec, the control and its five-for-five battery, this result and its
  pre-registration.
* **Outstanding: the `test_supervisor.py` column at fingerprint `ef6ece4e233b`** (~1.9h). Until it
  runs, all eight `survived_all` rows are `null` and §2 stands on three columns.
* The published `SEAT_RESULT_THE_FOURTH_COLUMN_SURVIVED_ENTIRE_...2026-09-05.md` table of
  `killed_by` sets is **superseded by §2** — every kill in it but one came from a test of the
  subject. Its §5 reachability account and its §9 transferable shape are unaffected and stand.
