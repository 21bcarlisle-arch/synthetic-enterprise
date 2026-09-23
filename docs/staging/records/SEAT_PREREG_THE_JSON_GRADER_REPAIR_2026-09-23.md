**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — pre-registration for the
JSON key-versus-value grading repair

# Pre-registration: what I expect the repair to move, written before I measured it

Registered **before** running the novel-key/edited-value split on any file, and before writing a
line of the repair. The item that commissioned this
(`a-regenerated-json-artefact-can-never-be-graded-superseded`) cites three publishing-chain files
with 234 / 2,706 / 14,236 "names HEAD lacks". Those three are **already identical to HEAD** on the
shared tree — the previous stretch's `--base-wins` landing spent them — so this is measured on the
two `.json` copies the census still names, and the item's own figures are not reproducible. That is
recorded here rather than in the result, so nobody can read it as a fact discovered after the
answer.

## The claim under test

`_json_leaf_names` keys a leaf as `keypath=<digest of value>`. `refresh_to_head.judge_copy`'s data
branch then computes `work_names - head_names` and calls the result *"JSON leaves HEAD does not
have"*. An edited number at a key the base already holds lands in that set. So the phrase names two
different things and the refusal cannot tell them apart.

## Predictions

1. **`docs/market_research/domestic_shift_response_arc.json`: novel KEY PATHS = 0.** Every one of
   the 5 "supplied" leaves is an edited value at a key path HEAD already has. Evidence already in
   hand: the `--base-wins` survey prints `+ named_gaps[0]=7da12f90` and `- named_gaps[0]=23da7e4a`
   in the same listing. Confidence: high.
2. **`docs/observability/self_clearing_alarm_census.json`: novel KEY PATHS = 0.** Lower confidence
   than (1) — `functions_scanned` is a top-level key and may genuinely be absent from HEAD. If it
   is novel, this prediction is refuted and the count is 1.
3. **Dropped KEY PATHS are NOT zero for (2).** The copy supplies 1,778 value-bearing names and drops
   3,490; if the first figure is entirely edits, the list is genuinely shorter in the copy and
   ~1,712 key paths exist in HEAD and not in the copy. That is a real structural loss and the base
   should still win.
4. **The census LOSS COUNT does not move: 18 before, 18 after.** The census's `.json` rows come from
   `clock_judge`, which never computed `gains` at all — this repair is in `judge_copy`'s data
   branch. A census count that moves means I changed something I did not intend to.
5. **`simulation/premise_population.py`'s verdict is byte-identical before and after.** It is `.py`;
   the repair touches `DATA_SUFFIXES` only. It is the item's named control and a change there means
   the repair leaked.
6. **Neither JSON file becomes writable without `--base-wins`.** I am repairing the GRADE, not
   removing the consent gate on a door that destroys bytes. If they become refreshable bare, I
   widened something I did not mean to.

## What would refute the whole approach

If prediction 1 fails — if `named_gaps[0]` is genuinely absent from HEAD — then the conflation I am
repairing is not what produced these counts, and the cause is somewhere else.
