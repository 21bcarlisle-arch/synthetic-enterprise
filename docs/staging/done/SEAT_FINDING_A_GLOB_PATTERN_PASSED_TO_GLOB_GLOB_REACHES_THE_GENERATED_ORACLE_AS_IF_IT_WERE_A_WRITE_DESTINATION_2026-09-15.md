**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — split out of `the-tree-keyed-oracle-hard-joins-a-path-from-the-declared-prefix-so-a-deeper-destination-is-emitted-as-a-file-that-does-not-exist`)

*Filed LATENT; **RECORDED 2026-09-15**, same day — §6 is the result and no work is owed. §5 names
the one thing still open and it is a different mechanism again.*

# A glob PATTERN handed to `glob.glob()` reaches the tree-keyed generated oracle as if it were a destination, and ordered reconstruction reads it perfectly

**Filed 2026-09-15, delivery seat.** Found by the repair it is split from: with the hard-join
fabrications removed, `docs/reports/run_output_*.json` is what is left standing in
`generated_artefacts()` that is not a file. Filed separately because it has a different cause and
a different fix, and a reader seeing the join repaired must not conclude this went with it.

---

## 1. The mechanism

`tools/file_scope_generated_paths.generated_artefacts()` now reconstructs each `/`-chain in an
assignment in source order and emits it when a declared tree stands at its head. Two sites spell a
chain that is a **search pattern**, not a destination:

```python
# tools/couple_value_based_pricing.py:499
dated = [p for p in glob.glob(str(PROJECT / "docs" / "reports" / "run_output_*.json"))
         if "2026" in Path(p).name]
# tools/r1_inference_ceiling.py:182
runs = [p for p in glob.glob(str(PROJECT / "docs" / "reports" / "run_output_*.json"))
        if "latest" not in p]
```

The chain is `docs` / `reports` / `run_output_*.json`. It reconstructs *correctly* — that is the
point. The defect is not in the reading; it is that the tree-keyed oracle has **no write-site
evidence requirement at all**. It is keyed to "a module names an artefact-suffixed path under a
declared tree in an assignment", and a `glob` pattern satisfies that exactly as a destination does.

This is the same asymmetry `written_artefacts`'s docstring is at pains to state — *"writing is the
property, naming is not"* — and the tree-keyed oracle is the half that does not hold it. It is held
there instead by the declaration: a path under `site/data/` is generated ground whoever names it.
That substitution is sound for destinations and silent for patterns.

## 2. The count

Two sites, **one** member: `docs/reports/run_output_*.json`. Both sites spell the same pattern.

Measured after the ordered-reconstruction repair: `generated_artefacts()` holds 216 members, 49 of
which are not on disk. Of those 49, **exactly one contains a glob metacharacter**. The other 48 are
overwhelmingly gitignored state files (`docs/observability/.rate_limits.json` and its siblings) that
legitimately do not exist in a fresh worktree — "not on disk" stays a noisy proxy and is not the
finding.

## 3. What it costs, and what it does not

**Inert today, and inert for a structural reason rather than by luck.** `origin_reconcile
._split_generated` tests exact membership against paths git reports. Git never reports a path
containing `*` — no such file can be created on any tree git tracks here — so this member can never
match and no lane's work is reverted by it. It is dead weight that makes the oracle read wider than
it is.

**The live cost is the reader, not the consumer.** `generated_artefacts()` is the thing a person
greps when asking "does the system know about this path", and a member that can never match is a
member that answers yes to a question it cannot act on. That reading is what hid the hard-join
defect for eight weeks: the oracle *contained a path that looked right*.

**It cannot move the commit gate.** `offends()` decides by prefix and every member is under one, so
membership is subsumed — `test_the_gate_half_is_SUBSUMED_by_the_prefix_test` holds this.

## 4. The fix, and why it is not in that commit

Two candidates and they are not equivalent, which is the reason this is a finding and not a
one-liner:

1. **Refuse a segment carrying a glob metacharacter** (`*`, `?`, `[`) in `_chain_segments`. Cheap,
   local, and refuses on the shape rather than on the caller. It would also refuse a legitimate
   destination whose filename genuinely contains one of those characters — measured: **zero** such
   paths are tracked in this repo today.
2. **Require the chain to be a write destination**, i.e. fold the write-site key into the tree-keyed
   oracle. That is the *correct* predicate and it is a much larger change: the tree-keyed oracle
   exists precisely because it reaches artefacts the write-site scan cannot resolve — 39 destinations
   in this tree are a `/` join on a name, and the whole-string spelling reaches eleven more. Making
   writing necessary here would lose most of what this oracle is for.

**(1) is the recommendation** and (2) is explicitly declined with its reason, so a later reader does
not re-derive it. But (1) makes the oracle stricter by one member, and this project has just learned
(same day, the finding this is split from) that a stricter oracle's *predicted* membership diff can
be wrong in both directions. It gets its own before/after measurement rather than a paragraph in
someone else's.

**Prediction filed before that work, so it can refute me:** the metacharacter refusal removes
exactly one member (`docs/reports/run_output_*.json`), adds none, leaves the on-disk member count at
167, and leaves `gate_violations()` empty. If it removes more than one, a real destination is being
spelled with a metacharacter somewhere and (1) is the wrong fix.

## 5. The other path still in neither oracle, and why it is a third thing again

`docs/observability/scale_probe_10k/prediction_register.json` is AO12's tracked output and reaches
neither oracle. `tools/scale_probe_10k.py` binds the directory in one expression and joins the
filename in another, so **no per-assignment matcher of any shape can see it** — not the membership
test that was replaced, not the ordered reconstruction that replaced it. It needs cross-expression
name resolution in the tree-keyed oracle, which is the thing `_scope_path_names` already does for
the write-keyed half. Recorded here so the two remaining gaps are counted in one place rather than
each being rediscovered as "the oracle is missing a path".

## 6. ACTIONED — and §4's prediction holds exactly

**Delivery seat, 2026-09-15, same day.** Recommendation (1) is implemented: `GLOB_METACHARACTERS`
(`*`, `?`, `[`) and a single subtraction in `generated_artefacts()`, placed AFTER both the
`/`-chain branch and the whole-string branch so one rule covers both doors — a refusal honoured by
one of two routes into the same set is no refusal at all, which this module's record already says
twice.

**§4 said "in `_chain_segments`" and that placement was wrong**, which is a small correction worth
making rather than absorbing: `_chain_segments` sees only the `/`-chain spelling, so a pattern
written as one whole string (`ALSO = "docs/reports/run_output_?.json"`) would have walked straight
past it. The whole-string branch is the door ten of this oracle's members already came through. One
subtraction after both branches is the mechanism that cannot be half-applied.

`]` is deliberately not a metacharacter here: it is only special after a `[`, so refusing on it
alone would refuse a real name for nothing.

| §4 predicted | measured |
|---|---|
| removes exactly one member | 216 → 215, one: `docs/reports/run_output_*.json` |
| adds none | none |
| on-disk member count stays 167 | 167 |
| `gate_violations()` stays empty | empty |

Unlike the prediction in the finding this was split from, this one was right in every leg — and the
reason is worth naming rather than taking as a good sign. It was a prediction about a **filter over a
set I had already measured**, not about what a new matcher would find. The one that failed was the
second kind. A prereg's value is not evenly distributed across the questions it asks.

`test_MUTATION_a_GLOB_PATTERN_is_not_a_destination` holds it, with both spellings and a real
destination in one fixture; deleting the filter reddens it, verified by doing that.

**Recommendation (2) stays declined, with its reason on the page**: requiring a write site here is
the correct predicate and would lose most of this oracle's reach. Nothing in §5 is closed by this.
