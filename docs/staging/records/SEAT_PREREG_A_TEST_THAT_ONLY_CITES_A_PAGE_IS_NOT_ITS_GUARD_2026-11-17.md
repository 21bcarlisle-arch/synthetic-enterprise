**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: a test that only cites a markdown page stops being selected for it (2026-11-17)

*Filed before any selection was measured under the new rule. Drawn on
`gate-selection-docstring-citation-cut`, the residue named in
`docs/staging/SEAT_FINDING_THE_COMMIT_GATE_HOUR_IS_ONE_SERIAL_PYTEST_AND_ITS_KILL_LEFT_NO_RECORD_2026-11-17.md`.*

## The change

`tools/pre_commit_test_gate._names_it_outside_comments` gives the same answer for tests as
`_names_it_outside_prose` already gives for modules, but only when the staged file is markdown. A test is
selected for a `.md` page only if code it evaluates holds the page's name as a path: a string with no
whitespace, not a docstring and not a bare string statement. For every other suffix, a test docstring
still counts, as before.

**Why:** a test that never opens the page cannot change its verdict when the page's prose changes.

## The README case, re-keyed first

`test_a_non_store_design_doc_is_still_pure_data` asserted that `docs/design/simplifications/README.md`
selects exactly `tests/design/test_simplifications_store.py`, because "its content can red that test".
**That is false.** The test names the README in its module docstring (line 6) and in one test docstring
(line 138). It never opens it: the grep finds no other use. The property the test exists for is "no
contract SUITE, only what actually reads the file". So it is re-keyed to: every test the README
selects holds the README's name outside its docstrings.

## Predictions, written before measuring

1. `docs/design/simplifications/README.md` selects no test at all.
2. `docs/market_research/home_moves.md` loses
   `tests/simulation/test_a_dual_fuel_movers_gas_follows_it.py` and
   `tests/simulation/test_a_dual_fuel_household_is_one_account_across_both_fuels.py`, the finding's
   954 s, and at least one more simulation test (`test_a_movers_final_bill_is_the_exit_draw.py`, 116 s).
3. Across every tracked `docs/**/*.md`, fewer than 15% of the (page, test) selection pairs are dropped.
   Most tests that are selected for a page by name hold its path to read it.
4. No test that opens the page with a path literal is dropped. A spot-check of five dropped pairs
   finds no `open`/`read_text` of the page in any of them.

## Results (measured after the predictions above were written)

`data_surface_tests` was run under HEAD's rule and the new rule, at the same tree.

| Page | Tests before | Tests after |
|---|---|---|
| `docs/market_research/home_moves.md` | 21 | 1 (`tests/tools/test_pre_commit_test_gate.py`, which holds its path) |
| `docs/design/simplifications/README.md` | 1 | 0 |
| `docs/design/THE_MODEL_ON_A_PAGE.md` | 6 | 6 (its readers reach it through `tools/model_on_a_page_picture.DOC`) |
| `docs/design/DIRECTOR_CANON.md` | 12 | 10 (drops `test_growth_mandate`, a docstring citer; `test_surgical_land`, a fixture line) |
| `docs/market_research/bad_debt_provisioning.md` | 4 | 0 (four citers in docstrings and comments) |

1. **Held.** The README selects nothing.
2. **Held, and wider than predicted.** home_moves.md drops all 20 of its citers: both 954 s files, `test_a_movers_final_bill_is_the_exit_draw.py`, and 17 more.
3. **Refuted.** On the direct test route, 562 of 814 (page, test) pairs across 11,245 tracked `docs/**/*.md` pages are dropped. That is 69%, not under 15%. Most tests that name a page do so to cite it, not to read it. The route was mostly citation, and the predicted share had it the wrong way round.
4. **Held on the spot-check.** Of the dropped tests, `test_growth_mandate`, `test_crisis_bad_debt_validator`, `test_the_arrears_overlay_reads_the_companys_own_book`, `test_a_dual_fuel_movers_gas_follows_it`, `test_generate_payment_ledger_data` and `test_delivery_lane` were read. None opens its page; their `read_text`/`open` calls read other files. Of the 562, 49 hold the page's name in a sentence-shaped string that code evaluates. These are error messages, fixture text and shell transcripts. The one that read a page (`test_model_on_a_page_picture`) is still selected through its module.

**Mutations.** Removing the markdown delegation reds three tests. Delegating for every suffix reds the per-branch control on its data-file leg.

**The residual risk, stated:** a test that opens a page only through a path assembled from parts that contain whitespace, or held in a variable imported from another test file, is no longer selected for that page. The census found no such test. The page's next commit can still red it, and the publish gate's full run still catches it.
