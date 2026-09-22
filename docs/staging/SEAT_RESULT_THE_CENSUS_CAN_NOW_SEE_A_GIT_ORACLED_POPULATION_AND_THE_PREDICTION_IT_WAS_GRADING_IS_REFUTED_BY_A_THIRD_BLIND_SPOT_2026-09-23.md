**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the instrument

# The widening works and found a standing member nothing could see; the count it predicted is refuted, and the cause is a leg nobody was looking at

**Grades the pre-registration in**
`docs/staging/done/SEAT_FINDING_THE_WHOLE_TREE_SUBJECT_CENSUS_IS_BLIND_TO_A_GIT_ORACLED_POPULATION_AND_TO_THE_TEST_CORPUS_2026-09-22.md`.
The prediction was fixed before this measurement and is reproduced verbatim below, beside its answer.

## The prediction, and the answer

> **Pre-registered, 2026-09-22.** Widen the predicate to accept a git-derived population and to
> include `tests` for corpus-wide ratchets, and re-run `--strict-dataflow`. I predict it returns
> **more than five** — the five below plus at least two others… If it returns fewer than five, the
> widening is wrong and not the census.

**Measured, 2026-09-23: `--strict-dataflow` returns 1.** By the pre-registration's own terms that is
**REFUTED**, and the sentence it lands on — "the widening is wrong and not the census" — is the one
this document has to argue with, because the evidence says the widening is right and the
prediction's *diagnosis* was incomplete.

| | before | after |
|---|---|---|
| loose (legs 1+2+3) | 99 | **113** |
| strict (one-hop dataflow) | **0** | **1** |
| transitive (any depth) | 0 | **4** |
| matching but already on `CONTROL_TESTS` | 26 | 28 |

## What the widening actually caught, and it is a real one

    tests/tools/test_the_pages_artifact_is_the_manifest_not_the_docs_tree.py   [docs, site]

Its population is `subprocess.run(("git", "ls-files"), …)` over the whole tree; its bounds are
`len(refs) >= 9` and `len(published_md) >= 20`. Whole-tree subject, integer-literal ratchets, and no
selector but its own filename stem — the class exactly. **It was not a new instance. It was a
standing one the instrument could not see**, and it surfaced the moment leg 1 learned to read a git
oracle. `test_the_strict_census_stays_discharged` refused it at this commit, which is the mechanism
doing precisely what it was built to do. It is discharged onto `CENSUSED_WHOLE_DIRECTORY_SUBJECTS`
here, priced at 8 tests / 36.3s — the most expensive entry on that list by a factor of three, stated
rather than glossed.

That single catch is the confirmation half. The refutation half is the other five.

## Why the five did not come back, attributed leg by leg

All five are now on `CONTROL_TESTS` via their own batch, so leg 3 removes them from `unreachable()`
correctly — they are *fixed*, not missing. Running the predicate on them directly, before leg 3:

| member | leg 1 (population) | leg 2 (integer-literal bound) | in class? |
|---|---|---|---|
| `test_a_commons_artefact_can_tell_when_its_source_was_revised` | ✅ **now passes** (git) | ✅ | loose, transitive |
| `test_no_committed_discharge_cites_an_unlanded_falsifier` | ✅ **now passes** (git) | ✅ | loose |
| `test_no_committed_store_claims_an_unlanded_falsifier` | ✅ **now passes** (git wrapper) | ❌ **0 literal bounds** | no |
| `test_no_tree_scan_passes_on_an_empty_population` | ✅ **now passes** (tests corpus) | ❌ **0 literal bounds** | no |
| `test_a_coverage_claim_declares_what_it_reduces_over` | ❌ population is **IMPORTED** | ✅ | no |

**Leg 1 — the thing the prediction was about — now passes for four of the five.** Both widenings do
what the finding said they would: the git-oracle leg admits three, the `tests`-corpus split admits
the fourth. The finding's mechanism is confirmed on every member it named.

**What stops three of them is leg 2, which nobody was looking at.**

## The third blind spot, which is the finding this produces

Leg 2 requires the bound be an **integer literal**. Two of the five compare against a *named* floor:

```python
_MIN_CITED_PATHS = 120
...
assert len(cited) >= _MIN_CITED_PATHS
```

That is the same claim about a growing population as `>= 120` written inline — **and it is the more
honest spelling**, because the constant has a name, a home and a place to carry its provenance. The
census counts the inline version and is blind to the named one. So the instrument systematically
rewards the less honest code, which is this project's "key a control to the property, not to today's
answer" failure pointing the wrong way down its own rule.

The third residual is different in kind: `test_a_coverage_claim_declares_what_it_reduces_over` has no
population call **in its own source at all** — it imports `OUTSTANDING` from
`tools.reduction_dimension`. The predicate is AST-visible and module-local, so an imported population
is structurally invisible to it. That is named in `classify_source`'s docstring rather than fixed.

**Neither is repaired here, and the reason is the same one the finding gave for not repairing itself
inside the commit that discharged its five.** Widening leg 2 in the same change that widened leg 1
would have made this measurement unattributable — two things moved, no attribution. The leg-1
widening is what was pre-registered; it is what landed; it is what is graded above.

## What is NOT claimed

The strict count is 1, and the honest reading of 1 is "this predicate, with this leg 2, found one" —
not "there is one". Three of the five known members of the real class score zero on it. **The strict
pool is still not a measurement of the class**, and `test_the_strict_census_stays_discharged`'s 0 was
never the evidence of absence it was read as. Widening leg 2 is the next thing that would move this
number, and its size is unpredicted — deliberately, since the last pre-registration here was wrong
about magnitude while right about mechanism.

## Filed as a consequence

- **Leg 2's integer-literal requirement is a blind spot of the same class as the two just closed**,
  and it is live: two known members sit behind it. A named floor constant is a ratchet.
- The stale half of the comment above `GIT_ORACLED_AND_TEST_CORPUS_SUBJECTS` — "they do not scan a
  whole directory" — is corrected in place, beside the original, rather than rewritten.
