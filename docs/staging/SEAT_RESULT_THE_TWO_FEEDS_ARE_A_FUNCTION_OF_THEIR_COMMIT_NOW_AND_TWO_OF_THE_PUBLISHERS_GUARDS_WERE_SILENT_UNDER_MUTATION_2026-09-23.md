**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `controls_that_cannot_fail` (primary)

# The two feeds are a function of their commit now, and two of the publisher's guards were silent under mutation

**Claim:** `the-publisher-stamps-a-commit-it-did-not-read-so-two-candidate-feeds-can-never-have-a-standpoint`
**Landed:** `7e9c2c935` (6 paths) and the consumer leg in the commit after it.
**Direction it answers:** the final section of
`docs/staging/records/SEAT_RESULT_A_DISPLACED_CLOCK_SEPARATES_THE_FEEDS_THAT_ARE_A_FUNCTION_OF_THEIR_COMMIT_2026-09-23.md`
— *"it is a producer defect, not a comparator one ... it wants its own item"*.

## The premise, re-measured before starting

Both commits the item cites — `d181b062d`, `6b4bfdd15` — were already ancestors of `origin/main`,
as the draw said. **The premise was not spent.** Those two commits landed the HONEST STAMP and the
two legs that accept it; what they left behind is exactly the state the item describes, and the
committed feeds said so in their own bytes:

    capabilities_door.json  published_from.inputs_are_the_committed_bytes: false
      "read off the working tree, not out of this commit: site/data/customers.json,
       site/data/dashboard.json, site/data/evidence.json, site/data/maturity_map.json"
    evidence.json           published_from.inputs_are_the_committed_bytes: false
      "read off the working tree, not out of this commit:
       docs/observability/test_execution_log.jsonl"

So `COVERED_AT_THEIR_OWN_COMMIT` was empty for a measured reason, and `check_at_its_own_commit` —
the only thing in this repository that can catch a hand-edit made to a published feed AFTER
publication — was switched off in production.

## What was done

The producer moved. `tools/publish_from_a_clean_tree` runs both generators in ONE clean checkout of
HEAD, where every input they read IS that commit's bytes, and writes a feed into the tree only if
the feed's own provenance stamp names that commit and vouches for its inputs.

Printed at real inputs before a line of it was wired, which is what this costs:

    clone + checkout                    1.8s
    generate_evidence_data              0.6s   inputs_are_the_committed_bytes: true
    generate_capabilities_door          2.8s   inputs_are_the_committed_bytes: true

Then measured before promoting, not after: each published feed regenerated in **two independent
clones** standing at the commit it records (`98a02bd18`), `_verdict` returning `AGREES` both times.
Against HEAD's committed bytes after landing, `check_at_its_own_commit` returns
`AGREES_AT_ITS_OWN_COMMIT` for both. **The relation is no longer empty.**

## The two guards that could not fail, and neither was an equivalence

Six mutations, restored after each. Four killed immediately. Two survived, and the flattering
reading — "they are equivalences" — was wrong for both:

| Mutation | Survived because | The case it does not cover |
|---|---|---|
| drop the exit-code leg | a dead generator normally leaves the commit's own feed behind, and the stamp leg refuses THAT for naming an earlier commit | a run that writes its JSON and then dies on a later step (`generate_evidence_data` writes the JSON, then decides about the HTML page) leaves bytes that DO vouch for this commit, from a broken run |
| drop the `produced is None` leg | both feeds covered today are committed, so nothing reached it | a NEW feed's first publication with a failing generator reaches `json.loads(None)`, and the TypeError takes every feed after it down with it |

Both are now held by named legs, and both mutations are killed. Recorded in the module beside the
code rather than left for the next reader to re-derive.

## The gate refused the first landing and it was right

Taking the two generators out of the publish path's imports made them orphans to every import
graph in the tree — *"this commit adds work that nothing runs"*, for two modules that run every
cycle. They are reached as `python -m tools.<name>` inside the clone, a route only a PATH STRING
makes visible (`capability_index` records it as a `(by path)` caller). `GENERATOR_SOURCES` spells
it and doubles as the pre-flight that names a typo'd generator before a clone is paid for.

Freezing them into the ratchet floor would have been a lie with a signature on it, and the freeze
door was right there.

## What it costs, on the surface and not in a footnote

**A feed that is a function of its commit is a feed about COMMITTED state.** `capabilities_door`
reads `evidence.json`, `customers.json` and `dashboard.json`, all of which the same publish cycle
regenerates; produced in the clean tree it reads the copies HEAD holds, so its figures lag this
cycle's uncommitted siblings by one publish cycle (~30 minutes). That is the whole trade. Reading
the uncommitted siblings is what made the stamp false and is not an option that also reproduces.

## Landed in two commits on purpose

`test_a_promoted_feed_still_reproduces_at_the_commit_it_records` grades the bytes HEAD carries, and
HEAD does not carry a clean-tree publication until the first commit is in. Promoting in the FIRST
commit and adding the leg in the SECOND is the only order in which both gates are green at their
own gate time — promoting later would have left `promotable` non-empty and reddened every lane in
the tree for a gate cycle. The ordering is written in the comment beside the set, so a reader who
finds the leg missing knows it is owed rather than assuming the set is unguarded.

## What I did not touch

`tools/refresh_to_head.py` is dirty in the shared tree and carries +5 `F401`, which reds
`test_static_quality_ratchet` for every lane reading the working tree. Its mtime (05:54) PREDATES
the last commit to its path (06:07), which is the stale-copy shape — **but it is not one**. The
diff supplies `--staged-too`, `STAGED_DISAGREES`, `_index_bytes` and `_clear_index_entry`, none of
which HEAD has: it is a concurrent fork, and `refresh_to_head` would destroy it. Left alone.
`surgical_land` gates the tree the commit would create, which carries HEAD's copy, so it was never
this landing's problem — recorded here because the next lane to hit that red will otherwise walk
the stale-copy door.

## Still owed

* The five generators outside `CANDIDATES_AT_THEIR_OWN_COMMIT` that publish from the dirty tree are
  untouched. Nothing here widens the candidate set; the door to widening it is now cheap, which is
  the point.
* `COVERED_DERIVED_ARTEFACTS` is still empty and still for the reason its own comment gives —
  `churn_belief_size_response.json` is STALE against its own code, filed as
  `SEAT_FINDING_THE_PUBLISHED_CHURN_KNEE_IS_GBP_3000_AND_THE_CODES_KNEE_IS_GBP_0_1_2026-09-23.md`.
  That is a different defect and this item does not reach it.
