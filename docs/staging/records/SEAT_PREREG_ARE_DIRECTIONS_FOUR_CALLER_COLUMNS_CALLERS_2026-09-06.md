**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# PRE-REGISTRATION: are direction's four caller columns actually callers, and what does the answer do to the published verdict

**Filed 2026-09-06, delivery seat, isolated worktree. Claim id
`direction-battery-four-columns-are-direct-importers`. Fixed BEFORE the deselect run and BEFORE the
family census in §4. The parts already measured are marked ESTABLISHED and are not predictions.**

---

## 0. The question, and why it is not the obvious one

`tools/direction_contract_battery.py` scores `background/direction.py` over four caller suites, and
**all four import `background.direction` at module level.** The census that found this
(`b3938b313`) also found why the obvious gate on that fact would have been wrong: a suite that
imports the subject can still be the legitimate dedicated suite of a module that *calls* it. The
item drawn from that census says the real discriminator is *"whether the suite NAMES a contract of
the subject, which is not statically decidable."*

**That is half right, and the half that is wrong is the whole of this turn.** "Names a contract" is
not decidable at FILE granularity, which is where the battery scores. It is decidable at TEST
granularity, and by a stricter property than naming: *does this test function call the subject's
own API and assert on what it returns.* That is an AST property.

## 1. ESTABLISHED — the per-test census (measured, not predicted)

AST over the four suites, counting test functions that reference `<direction alias>.<attr>`:

| suite | tests | touch `direction.*` |
|---|---|---|
| `test_supervisor.py` | 167 | **0** |
| `test_delivery_lane.py` | 41 | 2 |
| `test_delivery_seat.py` | 43 | **17** |
| `test_the_self_audit_..._carried_it.py` | 13 | 5 |

`test_supervisor.py` imports the module only to `monkeypatch.setattr(direction_module,
"DIRECTION_PATH", ...)` in a fixture. It is a pure caller suite — and it is the one the poison round
already proved never reaches the subject.

The other three are MIXED FILES. `test_delivery_seat.py` carries 17 tests that call `d.validate`,
`d.focus_multiplier`, `d.focus_weights`, `d.current_focus`, `d.read_direction`, `d.focus_was_drawn`,
`d.WRITE_SCOPE`, `d.FORBIDDEN_KEYS` and assert on the return, with `MUTATION (must fire)` docstrings
that restate M1, M2, M3, M4, M6 and M7 almost verbatim.

## 2. ESTABLISHED — every published kill's first-failure node is one of those tests

From the cells already on disk (`/var/tmp/direction_battery_sup.json`, the run behind the published
result). `-x` is on, so `failed` names the FIRST failure only:

| M | published `killed_by` | first-failure node | calls the subject directly? |
|---|---|---|---|
| M1 | seat | `test_direction_can_NEVER_make_an_atom_harder_to_draw` | yes — `d.focus_multiplier` |
| M3 | seat | `test_a_record_carrying_a_TARGET_is_refused...[benchmark]` | yes — `d.validate` |
| M4 | seat | `test_a_direction_that_REJECTED_NOTHING_is_refused` | yes — `d.validate` |
| M5 | audit | `test_an_error_with_NO_CORRECTION_STATE_is_refused[yes]` | yes — `d.validate` |
| M6 | lane, seat | `test_a_MISSING_or_BROKEN_record_offers_nothing` / `test_a_BROKEN_direction_record_leaves_the_draw_byte_identical` | yes — `d.unreachable_focus` / `d.focus_weights` |
| M8 | audit | `test_the_recorded_audit_reads_in_BOTH_shapes_and_never_invents_a_verdict[...]` | yes — `d.wrong_rows` |

**Six of six. Not one kill in direction's published caller table has a first-failure node that
exercises a caller.**

**This does not settle it, and the reason is `-x`.** The run stopped at the first failure, so a
CALLER test later in the same file may also have failed and would never appear. "The first failure
is the subject's own test" and "no caller test can fail" are different claims, and only a re-run can
close the gap. That is what §3 measures.

## 3. THE PREDICTIONS — the deselect run

Re-run all eight mutations against the three mixed suites with the subject-asserting tests
DESELECTED, so a kill can only come from a test that exercises a caller. ~2.5s a cell; the whole
round is about two minutes.

- **P1 (the headline). Zero caller kills survive.** All eight rows go to `survived_all: true` on a
  caller-only population. *Mechanism, not hunch:* the only file with zero subject-asserting tests —
  `test_supervisor.py`, 167 tests — already survived all eight, and §2 shows the other three files'
  every recorded kill entering through the direct-assert half.
- **P2. The most likely refutation is M6 on the lane**, via
  `test_EXPIRED_direction_offers_NOTHING`, which asserts `d.unreachable_focus(...) == []` AND
  `dl.next_item(...) is None` in one body. It is a MIXED TEST — caller evidence and subject
  evidence in one node — and deselecting it throws away real caller evidence while keeping it lets
  a subject assert masquerade as a caller kill. If a row's only surviving kill is a mixed test, the
  honest verdict is INDETERMINATE, not `false`.
- **P3.** The repair column `test_direction_contracts.py` is untouched: it already kills 8 of 8 and
  is scored outside the caller population by construction, so **no contract loses its proof.** What
  moves is only the claim about who proves it.

**If P1 holds, the published headline is wrong in the same direction and by more than
`segment_vocabulary`'s was.** `SEAT_RESULT_THE_FOURTH_COLUMN_SURVIVED_ENTIRE...` published *"two
contracts that no caller suite anywhere could fail on"* (M2, M7). The caller-only answer would be
**eight of eight** — and since the sole pure caller column is also the UNREACHABLE one, the true
statement is stronger still: *no caller suite anywhere can see `background/direction.py` at all,
and every contract it has is proved by its own tests.*

## 4. THE FAMILY CENSUS — unknown, and predicted here

Run the same AST census over every caller suite of all five specs in the sweep.

- **P4. At least two of the other four specs have a mixed file in `suites`** — a caller suite
  carrying at least one test that asserts on the subject's own API. *Reasoning:* the sweep's
  subjects were chosen for being converged, and a converged module's contracts get tested wherever
  someone first needed them, which is a caller's file. `direction` was not built differently.
- **P5. `test_supervisor.py`'s zero is not typical.** Median subject-asserting tests per caller
  suite across the family is ≥ 1.

## 5. What done means

The discriminator becomes a MECHANISM (`tools/subject_asserting_tests.py`) rather than a judgement
recorded in prose, direction's spec declares the answer, the engine honours it, and the published
verdict is corrected beside its original claim. A prose ruling that "these two are really the
subject's own" would rot within a week; the census can be re-run against the tree.

**Prediction P1 is filed before the run. If the deselect round produces a caller kill, P1 is wrong
and this section stays exactly where it is.**
