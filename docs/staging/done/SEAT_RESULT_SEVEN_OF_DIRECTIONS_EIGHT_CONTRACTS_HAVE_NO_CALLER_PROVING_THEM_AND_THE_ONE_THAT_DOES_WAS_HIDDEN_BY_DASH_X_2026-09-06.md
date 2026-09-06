**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# RESULT: seven of direction's eight contracts have no caller proving them, and the one that does was hidden behind `-x`

**Graded 2026-09-06 against `SEAT_PREREG_ARE_DIRECTIONS_FOUR_CALLER_COLUMNS_CALLERS_2026-09-06.md`,
fixed before the run. Claim id `direction-battery-four-columns-are-direct-importers`. Results at
fingerprint `2d872733982b`, `/var/tmp/direction_battery_2d872733982b.json`.**

**The headline prediction P1 was REFUTED, and the refutation is the finding.**

---

## 1. The question the drawn item asked, and the answer

All four of `background/direction.py`'s caller suites import it at module level. The census at
`b3938b313` found that the obvious gate on that fact would have condemned a correct spec, and
concluded that the real discriminator — *does the suite NAME a contract of the subject* — "is not
statically decidable."

**It is not decidable at FILE granularity, which is where the battery scores. It is decidable per
TEST, by a stricter property: does the body call the subject's own API and assert on what comes
back.** `tools/subject_asserting_tests.py` is that census.

| suite | tests | assert on `direction`'s API | mixed | verdict |
|---|---|---|---|---|
| `test_supervisor.py` | 200 | **0** | 0 | CALLER SUITE |
| `test_delivery_lane.py` | 41 | 1 | 1 | MIXED FILE |
| `test_delivery_seat.py` | 43 | **16** | 1 | MIXED FILE |
| `test_the_self_audit_..._carried_it.py` | 13 | 5 | 0 | MIXED FILE |

So the answer to the drawn question is **neither of the two the item offered.** Not one column is
"really the subject's own", and not all four are callers. Three are MIXED — `test_delivery_seat.py`
holds 17 tests calling `d.validate`, `d.focus_multiplier`, `d.focus_weights`, `d.current_focus`,
`d.read_direction`, `d.focus_was_drawn` with `MUTATION (must fire)` docstrings restating the
battery's own M1, M2, M3, M4, M6 and M7 — *beside* 26 that genuinely exercise the seat.

**`direct_suites` could not express this and that is why it was missed.** That field moves a whole
file. Move `test_delivery_seat.py` and the seat's 26 real caller tests stop counting; leave it and
16 subject tests grade the subject. Both answers are wrong, and a file-level field can only choose
between them. The repair is per-node: `subject_asserting_nodes` deselects the subject's own tests
from the caller cell, so what remains in the cell is caller evidence and nothing else.

## 2. The caller-only verdict

Three mixed columns re-run at fingerprint `2d872733982b` with the subject-asserting tests
deselected. `test_supervisor.py` transfers without re-running: zero deselections, nothing about its
cell changed, and `background/direction.py` and `test_supervisor.py` are byte-identical
(`git rev-parse`) at the published run's commit `cfd4a5d4c`, at this turn's HEAD and on disk.

| # | contract | lane | seat | audit | supervisor | proved by a caller? |
|---|---|---|---|---|---|---|
| M1 | `focus_multiplier` is ALWAYS >= 1.0 | — | — | — | — | **no** |
| M2 | `focus_weights` untouched on length mismatch | — | — | — | — | **no** |
| M3 | forbidden keys refused at any depth | — | — | — | — | **no** |
| M4 | an empty `not_now` is refused | — | — | — | — | **no** |
| M5 | `wrong[i].corrected` must be a BOOLEAN | — | — | — | — | **no** |
| M6 | `read_direction` NEVER RAISES | — | — | — | — | **no** |
| M7 | `is_live` is bounded BELOW as well as above | — | — | — | — | **no** |
| M8 | a legacy `wrong` row is `None`, not `False` | — | — | **DIED** | — | **YES** |

**Published: two of eight unproved by any caller. Measured on a caller-only population: seven of
eight.** Every one of the six kills in the published table entered through the direct-assert half,
so five of the six "proved" cells were the subject grading itself wearing a caller's filename.

No contract lost its proof. The repair suite `test_direction_contracts.py` still kills 8 of 8 and
is scored outside the caller population by construction. What moved is only the claim about *who*
proves them — which is the entire question this sweep exists to ask.

## 3. P1 was wrong, and `-x` is why

> **P1.** Zero caller kills survive. All eight rows go to `survived_all: true`.

**REFUTED. M8 survived the deselect and died anyway**, on
`test_the_published_panel_SPLITS_open_from_corrected_from_not_recorded` — a genuine caller test. It
calls `page.what_it_got_wrong()` on `tools/generate_delivery_page.py` and asserts on the rendered
panel; `wrong_rows`, M8's target, runs for real inside it.

The mechanism of the refutation is the one §2 of the pre-registration flagged as its own limit.
`-x` names the FIRST failure only. In the published run the audit column's first failure was
`test_the_recorded_audit_reads_in_BOTH_shapes...` — a subject test — and pytest stopped there. Deselect
it and the run walks on to a caller test that also fails. **The published cell was not merely
mis-attributed; it was concealing a real caller kill behind a subject one**, and the concealment ran
in the direction that flatters the reduction (a subject kill masquerading as caller evidence) while
the truth underneath was that the caller evidence was real all along, for that one row.

**A prediction filed before the run and refuted by it is worth more than the four correct ones.**
P1 was derived from a mechanism — supervisor's 200 caller tests already survived all eight — and the
mechanism was sound about the two suites it had seen and blind to a third caller nobody had scored.

## 4. The correction to the spec's own comment

`tools/direction_contract_battery.py` said, at the head of `SUITES`:

> `tools/generate_delivery_page.py` is the fourth first-party caller and **has no suite that imports
> it AND direction**, so the fourth row here is the self-audit suite — the closest thing the module
> has to one of its own.

That comment is why the audit column was thought of as a near-own-suite. It is **wrong in the way
that mattered**: the self-audit suite *does* exercise `generate_delivery_page` as a caller, at
`test_the_published_panel_SPLITS_...`, and that test is the source of the only genuine caller kill
in the whole battery. The column the spec undersold as "the closest thing to its own" is the only
column carrying real caller evidence.

## 5. The other predictions

- **P2 (mixed tests). Not exercised, and reported rather than claimed.** Two mixed tests are
  declared (`test_EXPIRED_direction_offers_NOTHING`, `test_the_decision_log_is_APPEND_ONLY`).
  Neither killed anything in the caller-only run, so `killed_by_a_mixed_test` is empty on every
  row. The INDETERMINATE state did not fire here; it is proved reachable by
  `test_a_kill_by_a_MIXED_test_is_flagged_and_never_read_as_a_caller_verdict` rather than left to
  the reader to assume it works.
- **P3 (no contract loses its proof). CONFIRMED.** §2.
- **P4 and P5 (the family). REFUTED, both.** The census over all five specs finds **zero**
  subject-asserting tests in any other spec's caller population — none of the other four specs'
  caller suites even imports its subject. P4 predicted at least two would be contaminated; the
  answer is none. `direction` is the only spec in the family with this defect, exactly as the drawn
  item said and against the reasoning filed here. The `direct_suites` repairs at `b3938b313`
  already moved every file-level case out, and this is the residue those repairs structurally could
  not reach.

> **CORRECTED 2026-09-06, after the merge with the other lane's independent census.** The counts
> here read 16 in the seat file and 22 in total. Both were one low. A second lane measured this
> concurrently and hand-built its list; the two agreed on 22 rows and disagreed on one --
> `test_the_decision_log_is_APPEND_ONLY`, which this census filed as MIXED and theirs as the
> subject's own. **Theirs was right.** The test does `d.append_decision(record, path)` and then
> asserts on what `path` now contains, so the subject wrote through an ARGUMENT and a taint pass
> following only RETURN values could not see it. The census now models out-parameters, the two
> lists agree at 23, and the only remaining mixed row is
> `test_EXPIRED_direction_offers_NOTHING`. **No measured cell moves** — the corrected row was
> deselected under both readings, and the caller-only verdict re-runs identically on the merged
> spec: M8 alone, on the same caller test.

## 6. What is now mechanical

- `tools/subject_asserting_tests.py` — the census. Three classes, local taint (`problems =
  d.validate(x)` then `assert any(... for p in problems)` — four of the six published kills are
  that shape and a syntactic read filed every one as caller evidence), helper following to a
  fixpoint, `pytest.raises`, and class-qualified node ids.
- `BatterySpec.subject_asserting_nodes` / `.mixed_nodes`, both in the fingerprint. A row scored
  before a node was deselected may carry that node's kill and must not be resumed into a run that
  claims otherwise.
- `tests/tools/test_the_caller_population_excludes_subject_asserting_tests.py` — refuses a spec
  whose declaration has drifted from the census, **in both directions**. Over-declaring would
  deselect real caller tests and manufacture the unflattering answer, which is still a finding the
  instrument produced rather than the tree; it just happens to be the one nobody would question.
- Every leg mutation-proven, and one control (`test_an_assert_made_through_a_HELPER...`) was written
  because a mutation *survived*: the helper branch was an equivalence on all five specs'
  populations, so a synthetic member was added to make it reachable rather than leaving it
  unproved. **It then found a live defect in the census** — a test whose only assertion sat inside a
  helper had no `ast.Assert` node at all and was being filed as caller evidence.

## 7. What is NOT established

- The supervisor column at this fingerprint is **transferred, not re-run**. The byte-identity
  argument in §2 is the whole basis; `survived_all` reads `None` on every row in
  `/var/tmp/direction_battery_2d872733982b.json` and the run printed
  `NOT YET GRADED ON EVERY SUITE` honestly. Re-running it is ~113 minutes and is handed off.
- **No null round exists for this subject**, so whether any kill above came from a suite reading
  `direction.py`'s TEXT rather than running it is UNKNOWN, not ruled out. The run says so on its
  own last line.
- `test_delivery_lane.py` and `test_delivery_seat.py` now sit in the battery's
  `SUITES THAT REACH THE SUBJECT AND STILL PROVE NOTHING` list. They import it, the poison floor
  reddens them, and on a caller-only population they kill nothing at all.
