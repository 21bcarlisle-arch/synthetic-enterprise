**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `thirteen-background-controls-are-red-at-head-and-the-gate-selects-none-of-the-changes-that-broke-them`)

# A keep-both merge dropped a `return` INSIDE a retained symbol, a symbol-set superset cannot see that, and the census's own fail-open shape has a second door

**Filed 2026-09-17, delivery seat.** Working the Lane 0 item naming thirteen red controls in
`tests/background/`. **§1–§3 are observations read off failing assertions whose answers the
tracebacks already held — not predictions. §5 IS a pre-registration, written before the change it
describes was made.**

---

## 1. Eight reds, one lost line, and a merge that could not see it

`background/self_clearing_alarm_census.py::shared_loader_answers` built its `out` list and fell off
the end, returning `None` where its own signature says `list[str]`. All eight assertions in
`tests/background/test_one_answer_standing_on_several_census_rows.py` died on that `None`.

Attributed by `git log -L`, not guessed: added in `8cd3bfc25`, deleted in `98a9a090c`
(2026-09-09) — a **hand three-way merge of a genuine rival copy, "five conflicts, all keep-both"**.
The conflict hunk ended at the last `out.append(...)` and the next symbol's insertion swallowed the
`return`.

**The generalisable half.** That commit's own recorded evidence reads *"the result is a strict
superset of both symbol sets"*. That is **true, and it is precisely why nothing caught this**: a
superset of SYMBOL NAMES says nothing about the statements inside a symbol both sides retained.
**A merge graded at symbol granularity is structurally blind to a deleted statement within a kept
function.** The consumer, `main()`, reads `if shared:` — so `None` was indistinguishable from "no
rows share an answer". The rung was **fail-silent for eight days, in a module whose entire subject
is other controls falling silent.**

Nothing in the tree currently looks for this shape, and it is not specific to this file.

## 2. A control pinned to today's call text, hiding a worse defect

`test_the_landing_tool_actually_brackets_its_gate` did `src.index("run_gate(checkout, hook_rel)")`.
`run_gate` gained a `gated_tree=` keyword, so the control went red **because its subject became
more careful** — the bracket was where it belonged the whole time.

Rewriting it surfaced a second, worse defect. The assertion was `bracket_at < gate_at`, a
comparison of **text offsets**, and that is not enclosure: a bracket opened and closed ABOVE an
unwatched gate run satisfies it. **That is the only arrangement the control exists to refuse.**
Measured, with the gate call dedented out of the `with` block:

| control | verdict on an unwatched gate run |
|---|---|
| old (`bracket_at < gate_at`) | **PASSES** — blind to its own subject |
| new (AST walk of the `with` body) | **FAILS**, naming the arrangement |

Strictly stronger, not a re-pin, and no longer keyed to a spelling. `tools/surgical_land.py` was
restored byte-identical after that mutation run.

## 3. CORRECTION, beside the claim: the live-tree reds were not landing artefacts

The drawn item instructed: *"at least one hit (`.publish_landing_in_flight.json` undispositioned)
was an artefact of a landing in flight and that file no longer exists, so the live-tree rungs must
be re-read with no land running."*

**Refuted, and the reasoning was inverted.** The census derives its subject from **code**, by AST —
never from the file's presence on disk. Re-measured with the file absent from the tree: 4 writers,
6 readers, `hit: true`. The hit stands as long as `process_run_complete.py:6423` declares
`LANDING_IN_FLIGHT_FILE`, and **waiting for a quiet tree could never have cleared it.** Treating it
as an artefact would have left a real row unwritten. It is now dispositioned `benign` from the
module's own code, with the fail-open direction argued rather than assumed.

## 4. The census's documented fail-open shape has a SECOND door: a resolver's RETURN

`eroded_dispositions` reports `.launch_records.json` — **10 writers, 0 readers**. Its own docstring
names the class: the 2026-09-05 loader sweep routed reads through a shared helper and the key "died
at the parameter seam". `_attribute_through_parameters` was built to close exactly that, walking a
keyed ARGUMENT into the callee's PARAMETER to a fixpoint.

It does not walk a **return value**. `background/launch_liveness.py` reads the register as:

```python
resolved = _resolved_path(path)              # -> Path(shared_tree_live_record(path or RECORDS_PATH))
return load_list_prior(resolved, item_type=dict)
```

`resolved` is a local bound from a call's return, so the key is laundered and the read vanishes.
**Confirmed with one variable changed** — same helper, same read, differing only in how the path
arrives:

| call site | argument | readers derived |
|---|---|---|
| `ntfy_responder.py:340` | `load_list_prior(SEEN_HASHES_FILE)` — constant | **2** |
| `staging_watcher.py:220` | `load_list_prior(STATE_FILE)` — constant | **3** |
| `launch_liveness.py:287` | `load_list_prior(resolved, ...)` — resolver return | **0** |

The blinding was introduced by the 2026-09-16 "there is one book" repair (`shared_tree_live_record`)
— **again, a correct repair making a carrier leave the class the census enumerates**, which is the
exact property the docstring warns is "getting STRONGER WITH ADOPTION".

`eroded_dispositions` is explicit that this leg **cannot be excused by `declassified`** ("the first
three are not repairs and no field excuses them"). The only honest remedy is to make the derivation
see the read. That is deliberately NOT bundled with §1–§3.

## 5. PRE-REGISTRATION — extending attribution to return values

Written **before** the change, so it can refute me.

- **P1.** Teaching the fixpoint that a local bound from a call returning a key-derived value carries
  that key will recover `.launch_records.json`'s readers and clear the `eroded_dispositions` leg.
- **P2.** It will **not** stop at that path. I expect **other** paths to gain writers/readers, and
  some to become new `hit`s — each then owing an authored disposition row, so
  `test_every_live_hit_is_dispositioned` goes **RED with new names**. That red is the mechanism
  working, not a regression, and the row count should rise above 54.
- **P3.** I do **not** predict the count. If P2 produces zero new hits I will say so plainly: that
  would mean the resolver shape is rare and this was one carrier, not a class.

**The failure mode I am watching for**, because it is this project's named one: an attribution rule
loose enough to make the census green by attributing paths to functions that do not touch them. A
recovered read must be traceable to a real call chain, never inferred from a name.

## 6. What the gate could not do about any of it

Neither §1 nor §2 was reachable by the gate that introduced it.
`tests_for('background/self_clearing_alarm_census.py')` returns **exactly one file**,
`test_self_clearing_alarm_census.py`. The eight-assertion file — which tests a function in that very
module and **existed at `98a9a090c`** — is not selected. The merge ran its gate, got 481 passed, and
the controls that would have named the lost `return` were unreachable from the module they guard.
This is the already-filed selection-by-stem finding with a named, dated instance and a cost.

**The symptom then bit this turn's own landing**, which is worth recording because it is the
mechanism completing its cycle: the first land attempt was **refused** — changing the census module
selected `test_self_clearing_alarm_census.py`, red for the two live-tree causes in §3 and §4, which
this turn had not yet repaired. A commit is refused for reds it did not cause; here they were at
least in scope, but nothing about the selection made that so.

## 7. Also repaired: a fixture pinned to a constant's magnitude

`PUBLISH_CADENCE_SECONDS` was re-measured 1500 → 5400 by its own documented method (median over the
last 200 markers, rounded DOWN; window 2026-09-02→09-17, n=189 usable gaps). The drift is monotone
across slices, not one bad day, and **the direction is the quieter one for the second time** — so
the cadence log records it as a finding about the machine that moving the number registers rather
than answers.

That change went red in a **different** test: `test_a_killed_run_is_not_certified_as_inside_the_
cadence` asserted `over_cadence` for a literal 4503.7s, which was above the cadence when written and
is below 5400. The leg had quietly become a second *below*-cadence case and tested nothing it was
written to test. Both legs are now expressed in terms of the constant, and the below-cadence leg's
precondition is asserted rather than assumed. **Same class as §2** — a control keyed to today's
answer rather than to its property.
