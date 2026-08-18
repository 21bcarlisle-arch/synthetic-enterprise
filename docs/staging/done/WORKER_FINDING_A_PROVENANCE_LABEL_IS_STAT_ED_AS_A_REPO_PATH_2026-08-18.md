# WORKER FINDING — a provenance label is stat-ed as a repo path, and the Proof door's citation gate has been red at HEAD

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-18, SITE2_two_sided_wall_exhibit worker tick (commit `2673e013e`), while
establishing whether four `tests/tools` reds were mine or pre-existing.
**Rank:** backlog. Blocks nothing today; it is a live wedge for any commit whose gate
selection reaches this test file.
**Class:** harness / control false-positive. Queued per SELF-INTERRUPT DISCIPLINE, not fixed
on sight — it is not this atom's file scope and the repair moves a published control.

## Observed-with-evidence

Three tests in `tests/tools/test_site1_proof_citations_resolve.py` fail:

```
test_every_published_citation_resolves_to_a_real_artefact
test_the_gate_does_not_false_positive_on_a_live_path
test_a_url_citation_is_never_stat_ed_as_a_path
```

each with the same payload:

```
the Proof door publishes 2 citation(s) pointing at nothing:
['predicted_from_this_book', 'predicted_from_this_book']
```

**Proven pre-existing, not introduced.** Run against a clean detached worktree at HEAD
(`git worktree add --detach`), all three fail identically there. They are red at HEAD and
this tick merely discovered them — the same shape as the count-match gate that is red at
HEAD while a working tree reads green.

## The finding, which is not "a citation is broken"

`predicted_from_this_book` is **not a path and was never meant to be one.** It is a
provenance LABEL — the value of a `source` field inside a `_measured_on` metadata block
emitted by `tools/couple_w2_11_d5.py` (line ~10498), saying *how* a figure was derived.
Its own test suite asserts that value verbatim in three places, so the producer is behaving
exactly as specified.

The collision is that `source` is an **overloaded key**:

| producer | `source` means |
|---|---|
| the Proof door's citations | a repo-relative artefact PATH a reader can walk to |
| `couple_w2_11_d5`'s measured-on blocks | a derivation METHOD, in prose |

`generate_proof_data.CITATION_KEYS` is `('source', 'doctrine', 'outcome_source')`, and the
walker in the test descends the whole published payload, so it reaches the coupled
instrument's metadata and treats its method label as a citation. Measured directly:

```
citation_path('predicted_from_this_book') -> ('predicted_from_this_book', '')   # a "path"
citation_path('https://example.com/x')    -> (None, None)                        # carved out
```

So the checker **already has a carve-out for one class of non-path string (URLs) and is one
class short.** The third failing test is literally named
`test_a_url_citation_is_never_stat_ed_as_a_path` — the same concern, one category away.

## Why this matters beyond three red tests

The gate's own docstring states its purpose: telling a reader the evidence sits at a path
where nothing sits "is the same lie as a dead anchor". That gate is currently crying wolf on
a figure whose provenance is honestly recorded. A control that fires on correct data is the
failure mode that trains a reader — and a future promoter — to skip it, and this one has been
firing long enough to be red at HEAD.

It also means the REAL half is unguarded: while these three sit red, a genuinely archived
citation (the rot class the gate was built for, which recurs at every archive sweep) would
land inside the same red and be indistinguishable from the noise.

## Recommendation, not a question

Give `citation_path` a **provenance-label carve-out of the same shape as the URL one**, so a
bare token carrying no path separator and no file extension resolves to `(None, None)`
rather than to itself. Prefer that over exempting the `couple_w2_11_d5` producer or renaming
its field: the overload will recur at the next producer that writes a `source`, so fixing the
class is R10 and fixing the instance is not.

Three checks for whoever builds it:

1. **The carve-out must not blind the real gate.** The rot class this control exists for is
   `docs/staging/X.md` moving to `docs/staging/done/X.md` — those strings carry separators
   AND an extension, so they must still be stat-ed. R15 both ways: a real archived citation
   still FIRES, the provenance label does not.
2. **The anti-vacuity floors are already there and must stay meaningful** — the test asserts
   at least 10 citations parse as paths. A carve-out drawn too wide drops that count and the
   floor is what catches it, so run it and read the number rather than trusting the pass.
3. **Confirm the producer is left alone.** `tests/tools/test_couple_w2_11_d5.py` asserts the
   label verbatim in three places; a repair that renames the field reds those instead, moving
   the failure rather than closing it.

## Null control

After the fix, the three named tests pass AND a deliberately archived citation planted in the
payload still fails the gate. If both go green, the carve-out ate the control.

## Not claimed

Nothing here says the Proof door publishes a wrong figure — the provenance label is accurate
and the door renders it as intended. This is a checker defect, not a published-evidence
defect. It says nothing about SITE1_expert_doors' level or MAJOR-7's other half.
