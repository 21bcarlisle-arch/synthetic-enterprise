**Severity:** RECORDED · **Lane:** A_strategy_governance · **Atom:** the value arms error bar

# The fixed bar was the wrong number rather than a second opinion, and the disagreement on the live feed was not about bars at all

**Answered:** 2026-09-18, delivery seat, claim
`one-question-answered-twice-and-oppositely-in-the-error-bar`. Landed as `376499319`.

**The work, as drawn.** *"Make ONE rule govern whether the selection leg's mean clears zero, in
`tools/fold_noise_floor_family.py` and `tools/generate_value_arms_data.py`. Adopt the size-derived
bar in the floor artefact too and keep the reconciliation block as the record of why it changed. Key
the control to the property — no two keys in one payload may answer this question oppositely — never
to today's two numbers."*

---

## 1. The drawn scope named two files; the rule had FOUR homes and three of them were outside that scope

The item's premise is correct and its file list is one short of the rule. `grep` for the bar:

| home | spelling | who reads it |
|---|---|---|
| `run_value_cycle_ab.SEMS_TO_STATE_A_SIGN = 2.0` | a module constant | the two inline verdicts below |
| `run_value_cycle_ab.noise_floor` | `> SEMS_TO_STATE_A_SIGN * sem`, inline | writes `selection_distinguishable_from_zero` |
| `run_value_cycle_ab.fold_floors` | the same line again | the same key, other door |
| `run_value_cycle_ab.distance_to_a_sign` | `sems_needed: float = SEMS_TO_STATE_A_SIGN` | **a DEFAULTED PARAMETER** |
| `fold_noise_floor_family._DISTINGUISHABLE_SEMS = 2` | a restatement, pinned by a test | writes the folded family's verdict |
| `generate_value_arms_data` | `sems_to_state_a_sign(n)` | the page — already correct |

Changing only the two named files would have left the producer at a fixed 2.0 and the fold at
t(n-1), which is the same defect one door along: the fold's own pinning test compares its
recomputation against the producer's published summary, so the two would have drifted under a
control built to stop exactly that.

**The defaulted parameter is the one worth naming.** A retired constant reachable only through a
default is a home nobody greps for, and `distance_to_a_sign` publishes
`sems_needed_to_state_a_sign` — the bar itself — onto every floor artefact. Leaving it would have
put a fifth answer in the payload while the commit message claimed there was one.

## 2. Nothing on disk flipped, and that was measured BEFORE the change, not asserted after

Every floor artefact under `docs/observability/` re-graded under both rules:

```
artefact                                          n    sems    t(n-1)   at 2.0   at t(n-1)
value_cycle_ab_s1_noise_floor.json                9    2.852   2.306    True     True
value_cycle_ab_s1_noise_floor_20260909b.json      9    1.787   2.306    False    False
value_cycle_ab_s1_noise_floor_20260910.json       9    2.852   2.306    True     True
value_cycle_ab_s1_noise_floor_20260910b.json      9    0.548   2.306    False    False
value_cycle_ab_s1_noise_floor_2026083*.json       3    <1.24   4.303    False    False   (x6)
value_cycle_ab_s1_noise_floor_except_20260829     3   6076.9   4.303    True     True
the live folded family                           18    2.495   2.110    True     True
```

**Twelve families, zero flips.** This is a repair to the RULE and not a restatement of any published
figure — which is the thing a reader most needs told, because a bar move that silently re-graded a
live claim would have been the more expensive event.

**And it makes the obvious control useless, which is the finding.** Re-freezing either bar to 2.0 is
an EQUIVALENCE on every artefact in the tree: a control watching the boolean stays green through the
exact mutation this change exists to prevent. Per the standing rule — *a mutation that does not fire
is either a missing test or an equivalence, establish which* — this one is both, at different
layers. The missing test is keyed to the BAR
(`test_the_folds_bar_is_the_one_the_family_size_earns_and_is_published_beside_the_verdict`), and it
reds on the mutation in one line.

## 3. The live `agree: false` was NOT about the bars, and the page published the wrong cause

This is the part the drawn item could not have known, and it inverts half of its premise.

At the 18-seed family the page's own numbers are `sems_from_zero = 2.4954` against a bar of `2.1098`.
**It clears.** Both rules said the mean is distinguishable from zero. Yet
`selection_leg.sign_is_stateable` was `false`, so the reconciliation reported `agree: false` and
published:

> *"THESE TWO RULES DISAGREE ... this page asks whether it clears 2.110 and says False."*

That sentence is false on the payload's own arithmetic. `sign_is_stateable` answers a **bigger
question** than the producer's key: it also withdraws the sign when the family and the published run
were measured over different BOOKS, which is what happened on 2026-09-18 and which the producer's
rule cannot see. The reconciliation was comparing a statistic against a
statistic-plus-a-publishing-rule and attributing the difference to the one thing it was not.

**A true refusal published under an invented cause is the failure that survives longest**, because
the headline answer looks right and nobody re-checks it. Had the bars simply been harmonised as
drawn, `agree` would have stayed `false` on the live feed and the item's DONE — *one question, one
answer* — would have been unmet while looking met.

**The repair is a definition, not a threshold.** Per *before measuring a thing, say what it is*:

- `clears_its_own_bar` — the statistics alone. The only key the producer's may be reconciled against.
- `sign_is_stateable` — the statistics AND one book. May withhold, never overstate.
- `sign_withheld_despite_clearing_the_bar_because` — what the second added to the first, named,
  non-null only when the two differ.

`seeds_needed_to_state_a_sign` moved onto `clears_its_own_bar` for the same reason: seeds buy off a
mean too near zero and buy **nothing** against a family drawn on the wrong book, so quoting a
machine-hour price against a book refusal sends a reader to spend hours on a thing hours cannot fix.

## 4. What the control asserts, and why it is not pinned to today's answer

`test_NO_TWO_KEYS_in_the_payload_answer_the_clears_zero_question_oppositely` scans the real feed's
boolean leaves for a distinguishability vocabulary, requires every hit to be classified
`STATISTICAL` / `CONSERVATIVE` / `DERIVED` / `REASON` / `META`, and refuses if two STATISTICAL keys
answer differently or a CONSERVATIVE one answers more boldly. **A fifth home reds it by name.**

The predicate is a FUNCTION rather than a run of `assert`s, so it can be pointed at a payload that
IS defective: `test_the_control_FIRES_on_a_payload_whose_two_homes_disagree` enters all five refusal
branches on constructed payloads. A whole-payload check that only ever meets the real feed passes,
and nobody can say whether it passed because the payload is sound or because it cannot fire.

## 5. A prediction kept beside its result, and it was half right

The 2026-09-11 version of `test_the_two_bars_are_READ_from_their_own_modules_and_not_retyped_here`
ended with `bar_sems != bar_sems` and this note:

> *"the day someone harmonises them the assertion below says so rather than going quietly
> tautological ... delete it or restate why two rules are still kept"*

That day was today and it said so. **Right that harmonising would red it. Wrong that two bars were
worth keeping** — one of them was simply the wrong number, and a standard error estimated from the
same draws as the mean cannot be graded by a constant at more than one family size. Both halves are
recorded in the test, not quietly revised.

## 6. A door test was pinned to today's answer twice over, and would have reddened on the repair

`site/test_the_baseline_comparison_reaches_the_reader.py` asserted `str(bar_sems) in rendered`. That
passed only while the bar was the integer `2`:

- the page prints the bar to **three decimal places**, so `str(2.1098155778333156)` is in no sentence
  a reader ever sees — it would have reddened the moment the producer adopted the honest bar, i.e.
  when the page became MORE correct;
- and it would have reddened again as the literal `"None"` on every family folded before the
  producer began stamping the bar it graded at.

It now asserts the property it meant to: the threshold reaches the reader, or the page says plainly
that the artefact never recorded one. **A control pinned to today's answer goes red when the code
becomes more honest and stays green while the claim rots** — the third instance of that shape on
this one panel.

## 7. What is NOT done, and why it was left

**The live folded artefact was not re-folded.** `value_cycle_ab_s1_noise_floor_folded18_single_arm_
20260917.json` predates the stamp, so it carries its verdict without the threshold that produced it.
The reconciliation reports that honestly — `the_two_rules_are_one_rule: null`, with prose saying the
artefact does not state the bar it was graded at, **never** that the two agree. Re-folding it would
have rewritten a published artefact for a cosmetic gain, and the 12-seed family replacing it will
carry the stamp by construction. Fail-closed and stated is the right resting state here.

## 8. Landing note

Landed by `surgical_land --content` with `--drops` on two paths. The shared working copies of
`tools/run_value_cycle_ab.py` and `tests/tools/test_fold_noise_floor_family.py` were **251 and 19
lines adrift of HEAD in both directions**: a pathspec commit would have swept a sibling lane's
product-gate census work and reverted three HEAD commits. `isolate_hunks` built HEAD-plus-mine — the
producer landed at 103 changed lines, not the 739 the dirty working copy showed.

The stale-copy guard then refused twice more, correctly, because these bytes delete
`SEMS_TO_STATE_A_SIGN` and `_DISTINGUISHABLE_SEMS` and supply no name HEAD lacks. That deletion is
the point of the commit, so `--drops` declares it and the landing prints it.

The ruff ratchet was measured **on the tree this commit creates**, per the SHRINK LOG's standing
rule: I001 1308, unchanged. The dirty shared tree reads 1307; that -1 is another lane's and is not
banked here.
