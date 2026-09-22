# WORKER RESULT — the error-bar repair was already landed, and the docstring above it still asserted the defect

**Severity:** RECORDED · **Lane:** A_strategy_governance

The drawn item was BLOCKING; it is discharged by work already on `origin/main`, and the residual
this turn landed is a false comment, not a false figure.

**Claim:** `value-arms-error-bar` · **Date:** 2026-09-19 · **Drawn:** LANE 0 DELIVERY

---

## The drawn item's premise was true when written and is spent

The item asked for `_floor_admission` in `tools/generate_value_arms_data.py` to stop pairing a
floor spread to a figure on the DECLARED half of the book identity — `served_segments:
["resi","SME"]`, which every run this company has ever done declares, so the rule reported to the
reader as `declared_book, admitted: true` was a constant that could separate no two runs.

**That repair is already on `origin/main`.** `_realised_book_pairing` exists, is ANDed into
`admitted`, and pairs on disjoint ranges of the five realised counts. The named test
`test_the_pairing_is_on_the_DECLARED_half_and_never_on_the_realised_counts` no longer exists; its
replacement is `test_the_realised_counts_ADMIT_an_honest_re_run_and_REFUSE_a_different_book`,
which asserts the partition rather than a leg per branch.

## Both "finished when" clauses measured at HEAD, on the gate's own pair

The gate is `build(_read(THREE_ARM_PATH), _read(NOISE_FLOOR_PATH), ...)` at
`generate_value_arms_data.py:12383`. Measured against `value_cycle_ab_s1_three_arm.json`, whose
realised book is `billing_accounts_settled_in_window: 154..155`:

| floor | settled | `admitted` | disjoint on |
|---|---|---|---|
| `..._folded18_single_arm_20260917.json` (the real 09-18 pair) | 164..164 | **False** | `billing_accounts_settled_in_window` |
| `..._next12_at_18327d977.json` (a genuine same-book floor) | 154..154 | **True** | — |

So the repaired admission **refuses the real 09-18 pair** and **admits an honest same-book
re-run** — which is the whole partition the item asked to be proved, and the exact failure it
warned about (an admission that now refuses every pair) is refuted by the second row.
`pytest tests/tools/test_generate_value_arms_data.py -k "realised or pairing or admission or book"`
— 29 passed.

## A MISPAIRING I MADE AND CORRECTED, recorded because the next reader will make it

My first measurement used `CURRENT_WORLD_THREE_ARM_PATH` (`..._three_arm_20260908.json`, a
164/165 book) and reported all five fields disjoint. **That is not the gate's pair.** The
`error_bar` and `contrast_bounds` blocks are fed from `THREE_ARM_PATH`
(`value_cycle_ab_s1_three_arm.json`); `CURRENT_WORLD_THREE_ARM_PATH` feeds
`_current_world_contrast` only. Two constants on this module differ by ten accounts, and a check
assembled from the wrong one produces a confident refusal that the live page does not make. The
rule this module states everywhere applies to the people checking it too: **measure the producer at
its own call site, never at a pair you assembled.**

## What was actually left live, and is fixed here

The `_floor_admission` docstring still carried, in the present tense and directly above the code
that does the opposite:

> *"PAIRS ON THE DECLARED HALF AND NEVER ON THE REALISED ONE, which is the producer's own
> instruction … a consumer comparing them would refuse every honest re-run."*

The function has paired on both halves since 2026-09-18. The paragraph is not deleted — a reader
who meets only the corrected code will re-derive the producer's instruction and re-apply it — but
it is now dated, kept as the superseded reason, and followed by why one field's behaviour
(`accounts_at_end_of_window`, which genuinely does move across seeds of one book) was generalised
to five, and by the disjoint-range rule that answers the honest-re-run fear on real magnitudes.

## Interconnection: the sibling lane's uncommitted constant move is correct

The shared working copy carries another lane's live, uncommitted move of `NOISE_FLOOR_PATH` from
`folded18_single_arm_20260917` to `next12_at_18327d977` (mtime 14:01). Its block argues the move
restores the value and level legs the blanket refusal was withholding. **Measured above, that is
right:** folded18 refuses on the gate's own pair, next12 is admitted. Their bytes were not touched
or carried — this landing is my hunk only, isolated from HEAD.

## Disposition

`--release value-arms-error-bar`. The repair, the test rewrite and the live refusal all predate
this turn; what this turn adds is the corrected record beside the claim.
