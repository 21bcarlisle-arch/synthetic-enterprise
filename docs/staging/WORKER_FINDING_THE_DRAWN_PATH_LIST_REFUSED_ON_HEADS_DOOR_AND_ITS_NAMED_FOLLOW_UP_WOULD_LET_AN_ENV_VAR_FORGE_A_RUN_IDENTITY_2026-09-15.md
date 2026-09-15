# The drawn path list refused on HEAD's door, and its named follow-up would let an environment variable forge a run identity

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — H_harness, drawn-item accuracy

**Found:** 2026-09-15, landing the delivery item "the blind envelope the reader gets is the one the
arms were re-run for". That half is done and landed as `5421e028e`: the published value-arms feed
on origin/main now carries `blind_envelope.available: true`, a three-arm span, and ARM C' excluded
by name. Both things below are about the *instructions*, not the work, and neither blocked it.

*(No repo path is backticked in this header on purpose — the header block is `landed_manifest_check`'s
claim surface, and a `ref:path` token cited here reads as "this commit lands it". It refused this
finding once for exactly that.)*

## 1. The stated path list was a strict subset of the change, and landing it would have refused

The drawn item was explicit: *"both paths are staged together"*, and *"use `python3 -m
tools.surgical_land` with the two paths"* — `site/data/value_arms.json` and
`docs/design/blind_envelope_arms_2026-09-11.json`.

Landed with exactly those two paths, `surgical_land` refused:

```
FAILED site/test_the_baseline_comparison_reaches_the_reader.py::
       test_MUTATION_a_verdict_that_TURNS_ON_the_second_hand_arm_is_marked_differently
E  AssertionError: no line carries a robustness verdict, so the column is UNAVAILABLE and an
   unavailable check is a failed check
```

This is the right refusal and the gate was working. `surgical_land` gates the tree the commit
*would* create — HEAD plus the named paths — so it ran **HEAD's** copy of the door against the
**new** feed. HEAD's copy of that control picks its subject out of the live feed:

```python
subject = next((ln for ln in block["lines"]
                if ln.get("survives_dropping_the_second_hand_arm") is not None), None)
assert subject is not None
```

The new feed has no such line, and correctly so: ARM C' was the only second-hand arm, it is now
excluded for its houses, so there is nothing left to drop and the producer withholds the column
and says why in `why_no_robustness_column`. **The control was pinned to yesterday's answer and went
red because the feed became more honest** — the exact shape CLAUDE.md names under *"key a control
to the property, not to today's answer"*.

The repair already existed, staged and unmentioned, in four more paths. The whole change is six:

| path | what it carries |
|---|---|
| `docs/design/blind_envelope_arms_2026-09-11.json` | the arms |
| `site/data/value_arms.json` | the feed |
| `tools/generate_value_arms_data.py` | `_blind_envelope_homes_refusal`, the exclusion |
| `tests/tools/test_generate_value_arms_data.py` | the producer's controls |
| `site/capabilities/index.html` | **the renderer** — HEAD has no `excluded_arms` and no `why_no_robustness_column` at all |
| `site/test_the_baseline_comparison_reaches_the_reader.py` | the repaired door + three new controls |

`isolate_hunks --survey` on all six showed every hunk belonged to this one change and none to
another lane, so they were landed together. The six-path land passed.

**The generalisation, and it is the reusable half:** a drawn item that names a path list is making
an unre-asked prediction about which files the change spans. Here the two named paths were the
*data* and the other four were the *mechanism that makes the data legal* — and a data-only land
is precisely what a door keyed to the old data shape refuses. Before trusting a stated path list,
ask `git diff --cached --name-only` what else is staged in the same subject, and survey the hunks.
The cost of not asking is one full gate cycle: ~5 minutes of test-gate plus the site lane.

## 2. `execution_mode.fast` and `execution_mode.sim_fast_mode` must NOT be declared as run identity

The drawn item's first follow-up, called non-blocking:

> add `execution_mode.fast` and `execution_mode.sim_fast_mode` to `run_identity_fields` in
> `tools/run_annual_report.py` — the census reads only `execution_mode.risk_committee`, so the one
> field the arms' comparability claim actually rests on is stamped and unread

**This was not done, because the producer had already refused it in a dated comment
(`tools/run_annual_report.py`, above `run_identity_fields`) and the refusal is correct.** Verified
against the census rather than taken on the comment's word:

```
execution_mode.fast                resolves=None                   tokens_injected=[]
execution_mode.sim_fast_mode       resolves='2026-09-15'           tokens_injected=['2026-09-15']
execution_mode.risk_committee      resolves='deterministic mock -- tokens_injected=[]
```

- **`fast` is inert.** `_resolve_declared_field` ends `if isinstance(node, bool) or node is None
  or isinstance(node, (dict, list)): return None`. `fast` is a bool, so declaring it contributes
  nothing *and says nothing about contributing nothing* — a declaration that reads as coverage
  and is not.
- **`sim_fast_mode` is a forge.** It is `os.environ.get(FAST_MODE_ENV)` — the raw, arbitrary
  environment string. `_RUN_IDENTITY` matches `\b20\d{2}-\d{2}-\d{2}\b` among others, so a run
  launched `SIM_FAST_MODE=2026-09-15` would inject the run-identity token `2026-09-15` into the
  set the census grades claims against. An environment variable would be able to tell the census
  which run the artefact is. That is strictly worse than the gap it was meant to close.

**The premise is also false.** The follow-up says the field the arms' comparability claim rests on
is "stamped and unread". The comparability claim is that all arms ran the deterministic mock
committee rather than the LLM one — and that fact is carried by `risk_committee`, which *is*
declared and *is* read, resolving to a sentence containing no date and no SHA. It was chosen for
exactly that property. What is unread is `fast` and `sim_fast_mode`, and the correct state for
both is published-but-not-declared, which is what they already are.

**Do not redo this.** The next session that reads the same follow-up should stop here. If the
declaration ever needs to cover more, the change is to `_resolve_declared_field` (teach it to
render a bool as a non-identity token) and not to `run_identity_fields`.

## What is next

- The real uncovered gap named in `_execution_mode`'s own docstring is `--end-year`, which
  "truncates the simulation window and is equally fatal to comparability, and it is not stamped".
  That is a genuine hole in the comparability claim and it is not the one the follow-up named.
- Section 1's control repair is landed, but the class is not swept: other door tests keyed to
  today's feed shape will red the same way the next time a producer becomes more honest.
